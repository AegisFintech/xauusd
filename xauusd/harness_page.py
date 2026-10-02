"""The nof1-style live harness page.

Design intent
-------------
The operator needs to watch the harness *work*: what the deterministic engine
decided, what the model is thinking right now, and what it is asking itself.
The previous page showed one collapsed sentence per transcript row, polled five
endpoints once a second, and rendered nothing at all for the memory, the notes,
the current cycle phase, or the engine.

What this page adds:

* an event stream, so a row appears the moment it is committed instead of on the
  next poll, and so the page can say "connected, thinking" during a model round
  trip that produces no rows (22.8s median, 39.3s p90);
* a persistent **thinking** panel that renders the agent's real message stream;
* an **engine** panel: strategy, state, last decision, gate verdict, fill;
* a **self-review** panel that renders the interrogation Q&A as a dialogue;
* a **memory** panel: the working notes by category, including the candidates
  list, so the operator can see the search space rather than only rejections;
* **cycle phase** and elapsed timers, so a parked cycle is legible.

Deliberately absent: any control that can start, stop, halt or resume anything.
Every command on this page is read-only. Operator commands remain CLI-only and
explicitly operator-only (AGENTS.md), and a page reachable by a browser is not
the place to put them.
"""

_HARNESS_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>xauusd harness - live</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
 :root{
  --bg:#0b0e14; --panel:#121722; --panel2:#161d2b; --line:#222c3d;
  --fg:#dbe2ec; --dim:#7f8da0; --accent:#7aa2f7; --green:#7ee787;
  --amber:#e3b341; --red:#f7768e; --violet:#bb9af7;
 }
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--fg);
      font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
 header{display:flex;gap:16px;align-items:center;flex-wrap:wrap;
        padding:10px 16px;border-bottom:1px solid var(--line);background:var(--panel);
        position:sticky;top:0;z-index:5}
 h1{font-size:14px;margin:0;color:var(--accent);letter-spacing:.5px}
 .pill{padding:2px 9px;border-radius:99px;border:1px solid var(--line);background:var(--panel2);
      color:var(--dim);font-size:11px;white-space:nowrap}
 .pill.on{color:var(--green);border-color:#1f4030}
 .pill.warn{color:var(--amber);border-color:#4a3a12}
 .pill.bad{color:var(--red);border-color:#4a1f2a}
 .grid{display:grid;gap:12px;padding:12px;
       grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
 .wide{grid-column:1/-1}
 .card{background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
 .card h2{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--dim);
          margin:0;padding:9px 12px;border-bottom:1px solid var(--line);background:var(--panel2)}
 .body{padding:10px 12px;max-height:340px;overflow:auto}
 .body.tall{max-height:60vh}
 .row{display:flex;gap:10px;justify-content:space-between;padding:2px 0;
      border-bottom:1px dotted #1b2331}
 .row:last-child{border-bottom:0}
 .k{color:var(--dim)} .v{text-align:right;word-break:break-word}
 .ok{color:var(--green)} .no{color:var(--red)} .warn{color:var(--amber)} .vi{color:var(--violet)}
 .log{padding:6px 12px}
 .ev{border-bottom:1px solid #1b2331;padding:6px 0}
 .ev .hd{display:flex;gap:8px;align-items:baseline}
 .t{color:var(--dim);font-size:11px}
 .ttl{font-weight:600}
 .msg{color:#b6c2d2;margin-top:2px;white-space:pre-wrap;word-break:break-word}
 .bubble{border:1px solid var(--line);border-radius:6px;padding:7px 9px;margin:6px 0;
         background:var(--panel2)}
 .bubble.q{border-left:3px solid var(--violet)}
 .bubble.a{border-left:3px solid var(--accent);background:#141b28}
 .bubble .who{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--dim)}
 .qa{margin:2px 0;color:var(--dim);font-size:11px}
 details{margin-top:5px} summary{cursor:pointer;color:var(--dim);font-size:11px}
 pre{margin:5px 0 0;padding:7px;background:#0d1117;border:1px solid var(--line);border-radius:5px;
     max-height:220px;overflow:auto;white-space:pre-wrap;word-break:break-word;font-size:11px}
 .spin{display:inline-block;width:8px;height:8px;border:2px solid var(--accent);
       border-right-color:transparent;border-radius:50%;animation:sp .7s linear infinite;vertical-align:-1px}
 @keyframes sp{to{transform:rotate(360deg)}}
 .muted{color:var(--dim)}
 .tag{font-size:10px;padding:1px 5px;border-radius:3px;background:#1b2331;color:var(--dim)}
 .empty{color:var(--dim);font-style:italic}
 .notes-c h3{font-size:11px;margin:8px 0 3px;color:var(--accent)}
 .notes-c ul{margin:0;padding-left:16px} .notes-c li{margin:2px 0}
 .notes-c .src{color:var(--dim);font-size:10px}
</style></head><body>
<header>
  <h1>XAUUSD HARNESS</h1>
  <span class="pill" id="conn">connecting</span>
  <span class="pill" id="phase">phase -</span>
  <span class="pill" id="paper">paper -</span>
  <span class="pill" id="feed">feed -</span>
  <span class="pill" id="clock">-</span>
  <span class="pill">read-only</span>
</header>

<div class="grid">
  <div class="card wide">
    <h2>Live log</h2>
    <div class="log body tall" id="log"><div class="empty">waiting for activity</div></div>
  </div>

  <div class="card">
    <h2>Thinking</h2>
    <div class="body tall" id="thinking"><div class="empty">no agent message stream yet</div></div>
  </div>

  <div class="card">
    <h2>Deterministic engine</h2>
    <div class="body" id="engine"><div class="empty">no engine status</div></div>
  </div>

  <div class="card">
    <h2>Self-review <span class="muted">(agent questions itself)</span></h2>
    <div class="body tall" id="review"><div class="empty">no self-review yet</div></div>
  </div>

  <div class="card">
    <h2>Account and market</h2>
    <div class="body" id="account"><div class="empty">-</div></div>
  </div>

  <div class="card wide">
    <h2>Research memory <span class="muted">(search space, not just rejections)</span></h2>
    <div class="body tall notes-c" id="notes"><div class="empty">no notes recorded</div></div>
  </div>
</div>

<script>
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const num=(v,d=2)=>typeof v==='number'&&isFinite(v)?v.toFixed(d):'-';
function row(k,v,cls){return `<div class="row"><span class="k">${esc(k)}</span><span class="v ${cls||''}">${v}</span></div>`}
function pill(id,txt,cls){const e=$(id);e.textContent=txt;e.className='pill '+(cls||'')}

// ---- elapsed timers: the page must never look frozen -------------------
let lastRowAt=Date.now(), thinkingSince=null, submittedAt=null, nextAt=null;
function tickClock(){
  const idle=Math.round((Date.now()-lastRowAt)/1000);
  pill('clock', idle<3 ? 'live' : 'idle '+idle+'s', idle<3?'on':'warn');
  const th=$('thinking');
  if(thinkingSince){
    const s=Math.round((Date.now()-thinkingSince)/1000);
    let head=th.querySelector('.elapsed');
    if(head) head.textContent='thinking '+s+'s';
  }
  if(submittedAt&&nextAt){
    const wait=Math.round((nextAt-Date.now())/1000);
    pill('phase', (nextAt>Date.now()? 'next review in '+wait+'s':'review due'), 'warn');
  }
}
setInterval(tickClock,1000);

// ---- event stream -------------------------------------------------------
const log=$('log');
function addStep(row){
  if(log.querySelector('.empty')) log.innerHTML='';
  const c=row.content||{}, d=row.display||{};
  const when=(row.occurred_at||'').replace('T',' ').replace('+00:00','').slice(11,19);
  const d2=document.createElement('div'); d2.className='ev';
  let html=`<div class="hd"><span class="t">${when}</span>`+
           `<span class="ttl">${esc(d.title||row.phase)}</span>`+
           `<span class="tag">${esc(row.phase)}</span></div>`+
           `<div class="msg">${esc(d.text||'')}</div>`;
  if(row.phase==='agent_message') html+=thinkingPanel(c);
  if(row.phase==='interrogation') html+=interrogationPanel(c);
  if(row.phase==='tool_call'&&c.input) html+=`<details><summary>command</summary><pre>${esc(c.input.command)}</pre></details>`;
  if(row.phase==='tool_result') html+=outputPanel(c);
  if(c.cycle_id&&c.instance) submittedAt=Date.now();
  d2.innerHTML=html; log.insertBefore(d2,log.firstChild);
  while(log.children.length>400) log.removeChild(log.lastChild);
  lastRowAt=Date.now();
}
function thinkingPanel(c){
  const turns=c.messages||[];
  if(!turns.length) return '<div class="muted">no message stream</div>';
  return turns.slice(-8).map(m=>
    `<div class="bubble ${m.role==='assistant'?'a':''}"><div class="who">${esc(m.role)}</div>`+
    `<div>${esc(m.content)}</div></div>`).join('')+
    '<div class="elapsed muted">thinking</div>';
}
function interrogationPanel(c){
  const pairs=c.pairs||[];
  if(!pairs.length) return '';
  return pairs.map(p=>
    `<div class="bubble q"><div class="who">asks itself</div><div>${esc(p.question)}</div></div>`+
    `<div class="bubble a"><div class="who">answers</div><div>${esc(p.answer)}</div>`+
    ((p.evidence||[]).length?`<div class="qa">evidence: ${esc((p.evidence||[]).join(', '))}</div>`:'')+
    `</div>`).join('');
}
function outputPanel(c){
  const out=c.stdout||'', err=c.stderr||'';
  let h='';
  if(out) h+=`<details><summary>stdout (${(c.total_bytes||0).toLocaleString()} bytes${c.truncated?', truncated':''})</summary><pre>${esc(out)}</pre></details>`;
  if(err) h+=`<details><summary>stderr</summary><pre>${esc(err)}</pre></details>`;
  if(c.job_id) h+=`<details><summary>full output</summary><div class="muted">use /api/job?job_id=${esc(c.job_id)}</div></details>`;
  return h;
}
function connect(){
  const es=new EventSource('/api/stream');
  es.addEventListener('open',()=>pill('conn','stream connected','on'));
  es.addEventListener('step',e=>{ try{addStep(JSON.parse(e.data))}catch(err){} });
  es.addEventListener('error',()=>pill('conn','stream lost','bad'));
  es.addEventListener('message',e=>{ try{addStep(JSON.parse(e.data))}catch(err){} });
}
connect();

// ---- polled companion state -------------------------------------------
function renderHarness(h){
  const e=h.engine||{}, c=h.cycle||{}, hb=h.heartbeat||{}, f=h.data_feed||{};
  pill('phase', 'phase '+(c.phase||'-'));
  if(hb.kill_switch_reason) pill('paper','paper '+hb.kill_switch_reason,'bad');
  else pill('paper','paper '+(hb.status||'-'),'on');
  if(f.state) pill('feed','feed '+(f.session||f.state), f.state==='ok'?'on':'warn');
  else pill('feed','feed not running','warn');
  if(c.next_at){ nextAt=new Date(c.next_at).getTime(); }
  else nextAt=null;
  if(c.phase==='workflow'||c.phase==='submitting'){ if(!submittedAt) submittedAt=Date.now(); }
  else if(c.phase==='idle'){ submittedAt=null; }

  $('engine').innerHTML = e.state ? [
      row('state', esc(e.state), e.state==='halted'?'warn':'ok'),
      row('strategy', esc(e.strategy||'-')),
      row('quantity', num(e.quantity)),
      row('poll seconds', num(e.poll_seconds)),
      row('ticks', e.tick),
      row('decisions', e.decisions),
      row('consecutive errors', e.consecutive_errors, e.consecutive_errors?'warn':''),
      row('halted because', esc(e.halted_reason||'-'), e.halted_reason?'warn':''),
      e.last_decision?row('last signal', esc(e.last_decision.signal)+' '+
          (e.last_decision.side||'')+' '+num(e.last_decision.quantity),
          e.last_decision.accepted?'ok':'no')+row('gate', esc(e.last_decision.gate_reason||'-'),
          e.last_decision.accepted?'ok':'no'):'',
      e.last_decision?row('at', esc((e.last_decision.bar_utc||'').replace('T',' ').replace('+00:00',''))):'',
    ].join('') : '<div class="empty">engine not deployed</div>';

  $('account').innerHTML = [
      row('bar age (s)', num(f.age_seconds,0), (f.age_seconds>180)?'no':'ok'),
      row('last bar', esc((f.last_bar_utc||'-').replace('T',' ').replace('+00:00',''))),
      row('session', esc(f.session||'-')),
      row('agent tick', hb.tick), row('agent status', esc(hb.last_tick_status||'-')),
      row('monitor', esc((hb.monitor||{}).status||'-'),
          (hb.monitor||{}).status==='ok'?'ok':'warn'),
      row('monitor error', esc(hb.monitor_error||'-'), hb.monitor_error?'no':''),
      row('research progress', esc((h.research_progress||{}).cycles_without_new_notes??'-')+' cycles unchanged',
          (h.research_progress||{}).needs_attention?'warn':''),
    ].join('');

  const n=h.working_notes||{};
  const keys=Object.keys(n);
  if(!keys.length){ $('notes').innerHTML='<div class="empty">no notes recorded</div>'; return; }
  $('notes').innerHTML=keys.map(k=>{
    const items=n[k]||[]; if(!items.length) return '';
    return `<div class="notes-c"><h3>${esc(k)} (${items.length})</h3><ul>`+
      items.map(i=>`<li>${esc(i.text||i)}`+
        ((i.sources&&i.sources.length)?` <span class="src">[${esc(i.sources.join(' '))}]</span>`:'')+
        `</li>`).join('')+`</ul></div>`;
  }).join('')||'<div class="empty">no notes recorded</div>';
}
async function refresh(){
  try{
    const h=await (await fetch('/api/harness')).json(); renderHarness(h);
    pill('conn', $('conn').textContent==='stream lost'?'stream lost':'stream connected','on');
  }catch(e){}
  try{
    const p=await (await fetch('/api/paper')).json();
    const s=p.summary||p.paper||p;
    if(s&&s.position!==undefined) $('account').insertAdjacentHTML('afterbegin',
      row('position', num(s.position,3)+' ('+(s.side||'')+')', Number(s.position)?'ok':'')+
      row('equity', '$'+num(s.equity===undefined?s.cash:s.equity)));
  }catch(e){}
}
refresh(); setInterval(refresh,3000);
</script></body></html>"""
