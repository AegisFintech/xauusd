"""FastAPI live view of the autonomous agent's visible thinking process."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from .agent_loop import AgentTranscriptStore, CockroachAgentTranscriptStore
from .paper_trading import PaperTrading, paper_from_env

DEFAULT_VIEW_HOST = "127.0.0.1"
DEFAULT_VIEW_PORT = 8100

_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>xauusd agent - live thinking</title>
<style>
 body{background:#0d1017;color:#d7dde6;font:13px/1.45 ui-monospace,Menlo,monospace;margin:0;padding:16px}
 h1{font-size:15px;color:#8ab4f8;margin:0 0 4px}
 #meta{color:#7f8ea3;margin-bottom:8px;min-height:15px}
 #runs{color:#7f8ea3;margin-bottom:12px;font-size:12px}
 .step{margin:6px 0;padding:8px 10px;border-left:3px solid #2a3444;background:#141a24;border-radius:0 4px 4px 0;white-space:pre-wrap;word-break:break-word}
 .step.tick_start,.step.tick_end{border-color:#8ab4f8}
 .step.tick_error,.step.planner_error{border-color:#e3746e;background:#241a1f}
 .step.assistant{border-color:#f2c14e;background:#201c12}
 .step.tool_call{border-color:#4dab6d}
 .step.tool_result{border-color:#5b87b8}
 .step b{display:block;color:#8ab4f8;margin-bottom:3px;font-weight:700}
 .step .human{margin:0;white-space:pre-wrap}
 .step details{margin-top:3px}
 .step summary{color:#7f8ea3;cursor:pointer;font-size:12px}
 .step pre{margin:4px 0 0;color:#9aa8bd;white-space:pre-wrap}
 #more{text-align:center;color:#7f8ea3;padding:10px}
 #end{text-align:center;color:#57637a;padding:10px;font-size:12px}
 .k{color:#7f8ea3}
 #paper{margin-bottom:12px;padding:8px 10px;border:1px solid #2a3444;background:#12151c;border-radius:4px;font-size:12px}
 #paper .pl{white-space:pre-wrap}
 #paper .fills{margin-top:4px;color:#7f8ea3;font-size:11px;white-space:pre-wrap}
 #paper .badge.on{color:#4dab6d}.badge{color:#7f8ea3}.badge.stopped{color:#e3746e}
 .pos{color:#4dab6d}.neg{color:#e3746e}
 #paper b{color:#8ab4f8}
</style></head><body>
<h1>xauusd autonomous agent &mdash; live thinking <span style="font-weight:400">(newest first)</span></h1>
<div id="meta">connecting&hellip;</div>
<div id="paper">paper &mdash; checking&hellip;</div>
<div id="runs"></div>
<div id="log"></div>
<div id="more">load older decisions&hellip;</div>
<div id="end" style="display:none">end of history</div>
<script>
 let cur=null, topId=0, bottomId=0, loading=false, ended=false;
 const rendered=new Set();
 const $=id=>document.getElementById(id);
 const esc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 async function j(u){const r=await fetch(u);if(!r.ok)throw Error(r.status);return r.json();}
 function fmtTime(iso){if(!iso)return '?';const d=new Date(iso);return isNaN(d)?String(iso):d.toISOString().slice(11,19)+' UTC';}
 function fmtBar(iso){const m=/T(\\d\\d):(\\d\\d)/.exec(String(iso||''));return m?m[1]+':'+m[2]+' UTC':String(iso);}
 function stepNode(s){
  if(rendered.has(s.id))return null;rendered.add(s.id);
  const d=document.createElement('div');d.className='step '+s.phase;
  const b=document.createElement('b');
  b.textContent=s.phase.replace('_',' ').toUpperCase()+'  ·  tick '+s.tick+'  ·  '+fmtTime(s.occurred_at);
  d.appendChild(b);
  const hu=document.createElement('div');hu.className='human';hu.textContent=humanize(s);d.appendChild(hu);
  const det=document.createElement('details');
  const sm=document.createElement('summary');sm.textContent='raw json';det.appendChild(sm);
  const pre=document.createElement('pre');pre.textContent=JSON.stringify(s.content,null,2);det.appendChild(pre);
  d.appendChild(det);return d;
 }
 function addNode(n,atTop){if(!n)return;if(atTop&&$('log').firstChild)$('log').insertBefore(n,$('log').firstChild);else $('log').appendChild(n);}
 function pairs(o){
  const out=[];
  for(const k of Object.keys(o||{})){
   const v=o[k];
   if(v===undefined||v===null||v===''||(Array.isArray(v)&&v.length===0)||(typeof v==='object'&&Object.keys(v).length===0))continue;
   out.push(typeof v==='object'?k+'='+JSON.stringify(v):k+': '+v);
  }
  return out.join('  ·  ');
 }
 function priceFmt(p){const n=Number(p);return Number.isFinite(n)?n.toFixed(2):String(p);}
 function humanize(s){
  const c=s.content||{};
  switch(s.phase){
   case 'tick_start':
    return (c.bar_time_utc?'bar '+fmtBar(c.bar_time_utc):'market watch')+(c.price!=null?'  ·  price '+priceFmt(c.price):'');
   case 'tick_end':
    if(c.error_type)return 'error - '+(c.summary||c.error_type);
    return (c.summary?'summary: '+(c.summary||''):'done')+(c.steps!=null?'  ·  '+c.steps+' steps':'');
   case 'assistant':
    return humanizeAssistant(c);
   case 'tool_call':
    return 'executing '+c.tool+(c.input&&Object.keys(c.input).length?'  ('+pairs(c.input)+')':'');
   case 'tool_result':
    return pairs(c)||JSON.stringify(c);
   case 'planner_error':
    return c.summary||JSON.stringify(c);
   default:
    return JSON.stringify(c);
  }
 }
 function firstSentence(s){if(!s)return '';const t=String(s).trim();const i=t.search(/[.!?]/);return i>0?t.slice(0,i+1):t;}
 function humanizeAssistant(c){
  if(!c||typeof c!=='object')return JSON.stringify(c);
  if(typeof c.content==='string'){
   try{const p=JSON.parse(c.content);if(p&&typeof p==='object'&&p.action)return humanizeAssistant(p);}catch(e){}
   return String(c.content).slice(0,400);
  }
  const reason=firstSentence(c.reason);
  if(c.action==='final')return 'decision  -  '+(c.summary||'')+(reason?'  ('+reason+')':'');
  if(c.action==='tool'){
   let line='decided to run '+c.tool;
   if(c.input&&Object.keys(c.input).length)line+='  ·  '+pairs(c.input);
   if(reason)line+='  -  '+reason;
   return line;
  }
  return JSON.stringify(c);
 }
 function markEnded(){ended=true;$('more').style.display='none';$('end').style.display='block';}
 async function loadTop(){
  const st=await j('/api/steps?run_id='+encodeURIComponent(cur)+'&limit=100');
  for(const s of st.steps)addNode(stepNode(s),false);
  if(st.steps.length){topId=st.steps[0].id;bottomId=st.steps[st.steps.length-1].id;}
  if(st.count<100)markEnded();
  updateMeta();
 }
 async function loadOlder(){
  if(loading||ended||!cur||!bottomId)return;loading=true;
  try{
   const st=await j('/api/steps?run_id='+encodeURIComponent(cur)+'&before='+bottomId+'&limit=100');
   for(const s of st.steps)addNode(stepNode(s),false);
   if(st.steps.length){bottomId=st.steps[st.steps.length-1].id;updateMeta();}
   if(st.count<100)markEnded();
  }catch(e){/* retry next scroll */}
  finally{loading=false;}
 }
 function watchSentinel(){
  if(!('IntersectionObserver' in window))return;
  new IntersectionObserver(en=>{if(en[0].isIntersecting)loadOlder();},{rootMargin:'300px'}).observe($('more'));
 }
 async function pull(){
  try{
   const st=await j('/api/status');
   if(st.latest_run_id!==cur){
    cur=st.latest_run_id;topId=0;bottomId=0;loading=false;ended=false;rendered.clear();
    $('log').innerHTML='';
    $('more').style.display='block';$('end').style.display='none';
    if(cur)await loadTop();
   }
   updateMeta(st.latest_run_status);
   if(cur){
    const nw=await j('/api/steps?run_id='+encodeURIComponent(cur)+'&after='+topId+'&limit=100');
    if(nw.steps.length){
     const nodes=[];
     for(const s of nw.steps){const n=stepNode(s);if(n)nodes.push(n);}
     for(let i=nodes.length-1;i>=0;i--)if(nodes[i])addNode(nodes[i],true);
     if(nodes.length){topId=Math.max(topId,nw.steps[nw.steps.length-1].id);updateMeta();}
    }
   }
   await refreshRuns();
   await refreshPaper();
  }catch(e){/* transient; next poll retries */}
 }
 function updateMeta(status){
  const detail=(cur?cur:'no run yet')+(status?'  ·  '+status:'');
  $('meta').textContent=detail+'  ·  '+rendered.size+' steps';
 }
 function fmtMoney(v){const n=Number(v);if(!Number.isFinite(n))return String(v);return n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});}
 function fmtPnl(v){const n=Number(v);if(!Number.isFinite(n))return String(v);return (n>=0?'+':'')+n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});}
 function durationText(a,b){if(!a||!b)return '';const ms=Math.max(0,new Date(b)-new Date(a));const m=Math.floor(ms/60000);return m<1?'<1 min':(m>=60?(Math.floor(m/60)+'h '+(m%60)+'m'):m+' min');}
 function renderRun(r){
  let s='<span class="k">'+esc(r.run_id)+'</span> ('+esc(r.status);
  if(r.finished_at)s+='  ·  '+esc(fmtTime(r.finished_at));
  if(r.ticks)s+='  ·  '+r.ticks+' '+(r.ticks===1?'tick':'ticks');
  const dur=durationText(r.created_at,r.finished_at);
  if(dur)s+='  ·  '+dur;
  return s+')';
 }
 async function refreshRuns(){
  const r=await j('/api/runs?limit=6');
  const line='recent runs: '+r.runs.map(renderRun).join('  ·  ');
  if(line!==refreshRuns.last){refreshRuns.last=line;$('runs').innerHTML=line;}
 }
 function paperHeadline(s, risk){
  const pnl=s.day_pl>=0?'pos':'neg';
  let line='<span class="badge '+(s.stopped?'stopped':'on')+'">'+(s.stopped?'STOPPED':'running')+'</span>'
   +'  ·  equity <b>$'+fmtMoney(s.equity)+'</b>'
   +'  ·  '+posText(s)
   +'  ·  '+s.trades_today+'/'+risk.max_trades_per_day+' trades today'
   +'  ·  day P&L <span class="'+pnl+'">$'+fmtPnl(s.day_pl)+'</span>'
   +'  ·  realized <span class="'+(s.realized_pl>=0?'pos':'neg')+'">$'+fmtPnl(s.realized_pl)+'</span>'
   +'  ·  drawdown '+(s.drawdown_pct?s.drawdown_pct.toFixed(2):'0.00')+'%';
  return '<div class="pl">'+line+'</div>';
 }
 function posText(s){
  if(Math.abs(s.position)<1e-9)return 'flat';
  return '<b>'+esc(s.side)+'</b> '+s.position.toFixed(2)+' @ $'+fmtMoney(s.average_entry_price);
 }
 function renderFill(f){return '<b>'+esc(f.side)+'</b> '+f.quantity+' @ $'+fmtMoney(f.price)+(f.realized_pnl?'  ·  <span class="'+(f.realized_pnl>=0?'pos':'neg')+'">realized $'+fmtPnl(f.realized_pnl)+'</span>':'');}
 async function refreshPaper(){
  const p=await j('/api/paper');
  const sig=JSON.stringify(p);
  if(sig===refreshPaper.last)return;refreshPaper.last=sig;
  const s=p.paper.summary, risk=p.paper.risk;
  let html=paperHeadline(s,risk);
  if(s.recent_fills.length)html+='<div class="fills">fills: '+s.recent_fills.map(renderFill).join('  ·  ')+'</div>';
  $('paper').innerHTML=html;
 }
 setInterval(pull,1000);watchSentinel();pull();
 setTimeout(()=>{if(!cur)$('meta').textContent='no run yet  -  agent has not started';},4000);
</script></body></html>
"""


def create_app(store: AgentTranscriptStore | None = None,
               paper: PaperTrading | None = None) -> FastAPI:
    transcript: AgentTranscriptStore
    if store is None:
        transcript = CockroachAgentTranscriptStore()
    else:
        transcript = store
    transcript.initialize()
    paper_trading: PaperTrading | None = paper

    def paper_or_default() -> PaperTrading:
        nonlocal paper_trading
        if paper_trading is None:
            paper_trading = paper_from_env()
        return paper_trading

    app = FastAPI(title="xauusd agent view", docs_url=None, redoc_url=None, openapi_url=None)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return _PAGE

    @app.get("/api/status")
    def status() -> dict[str, Any]:
        runs = transcript.runs(limit=1)
        return {"latest_run_id": runs[0]["run_id"] if runs else None,
                "latest_run_status": runs[0]["status"] if runs else None}

    @app.get("/api/runs")
    def runs(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
        return {"runs": transcript.runs(limit)}

    @app.get("/api/steps")
    def steps(run_id: str | None = Query(default=None), after: int | None = Query(default=None, ge=0),
              before: int | None = Query(default=None, ge=1),
              limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
        desc = before is not None or after is None
        rows = transcript.steps(run_id, after_id=after or 0, before_id=before, desc=desc, limit=limit)
        run_status = transcript.run_status(run_id) if run_id else None
        return {"run_id": run_id, "run_status": run_status, "order": "desc" if desc else "asc",
                "after": after, "before": before, "count": len(rows), "steps": rows}

    @app.get("/api/paper")
    def paper_endpoint() -> dict[str, Any]:
        pt = paper_or_default()
        return {"paper": {"summary": pt.summary(), "risk": {
            key: getattr(pt.config, key) for key in ("daily_loss_limit", "max_drawdown", "max_position",
                                                     "max_trades_per_day", "max_market_data_age_seconds")}}}

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app