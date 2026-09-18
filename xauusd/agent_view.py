"""FastAPI live view of the autonomous agent's visible thinking process."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

from .agent_loop import AgentTranscriptStore, CockroachAgentTranscriptStore

DEFAULT_VIEW_HOST = "127.0.0.1"
DEFAULT_VIEW_PORT = 8100

_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>xauusd agent - live thinking</title>
<style>
 body{background:#0d1017;color:#d7dde6;font:13px/1.45 ui-monospace,Menlo,monospace;margin:0;padding:16px}
 h1{font-size:15px;color:#8ab4f8;margin:0 0 4px}
 #meta{color:#7f8ea3;margin-bottom:8px}
 #runs{color:#7f8ea3;margin-bottom:12px;font-size:12px}
 .step{margin:6px 0;padding:8px 10px;border-left:3px solid #2a3444;background:#141a24;border-radius:0 4px 4px 0;white-space:pre-wrap;word-break:break-word}
 .step.tick_start,.step.tick_end{border-color:#8ab4f8}
 .step.tick_error,.step.planner_error{border-color:#e3746e;background:#241a1f}
 .step.assistant{border-color:#f2c14e;background:#201c12}
 .step.tool_call{border-color:#4dab6d}
 .step.tool_result{border-color:#5b87b8}
 .step b{display:block;color:#8ab4f8;margin-bottom:3px}
 .step .human{margin:0;white-space:pre-wrap}
 .step details{margin-top:3px}
 .step summary{color:#7f8ea3;cursor:pointer;font-size:12px}
 .step pre{margin:4px 0 0;color:#9aa8bd;white-space:pre-wrap}
 #more{text-align:center;color:#7f8ea3;padding:10px}
 #end{text-align:center;color:#57637a;padding:10px;font-size:12px}
 .k{color:#7f8ea3}
</style></head><body>
<h1>xauusd autonomous agent &mdash; live thinking <span style="font-weight:400">(newest first)</span></h1>
<div id="meta">connecting&hellip;</div>
<div id="runs"></div>
<div id="log"></div>
<div id="more">load older decisions&hellip;</div>
<div id="end" style="display:none">end of history</div>
<script>
 let cur=null, topId=0, bottomId=0, loading=false, ended=false;
 const log=()=>document.getElementById('log');
 const esc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 async function j(u){const r=await fetch(u);if(!r.ok)throw Error(r.status);return r.json();}
 async function loadTop(){
  const st=await j('/api/steps?run_id='+encodeURIComponent(cur)+'&limit=100');
  for(const s of st.steps)append(s,false);
  if(st.steps.length)bottomId=st.steps[st.steps.length-1].id;
  if(st.count<100)markEnded();
 }
 function stepNode(s){
  const d=document.createElement('div');d.className='step '+s.phase;
  const b=document.createElement('b');b.textContent=s.phase.replace('_',' ').toUpperCase()+'  #'+s.id+'  tick '+s.tick;
  d.appendChild(b);
  const hu=document.createElement('div');hu.className='human';hu.textContent=humanize(s);d.appendChild(hu);
  const det=document.createElement('details');
  const sm=document.createElement('summary');sm.textContent='raw json';det.appendChild(sm);
  const pre=document.createElement('pre');pre.textContent=JSON.stringify(s.content,null,2);det.appendChild(pre);
  d.appendChild(det);return d;
 }
 function append(s,atTop){const n=stepNode(s);if(atTop)log().insertBefore(n,log().firstChild);else log().appendChild(n);}
 function humanize(s){
  const c=s.content||{};
  switch(s.phase){
   case 'tick_start':
    return 'bar '+(c.bar_time_utc||'?')+(c.price!=null?'  &middot;  price '+priceFmt(c.price):'');
   case 'tick_end':
    return (c.error_type?c.error_type+(c.message?' '+c.message:''):'summary: '+(c.summary||''))+(c.steps!=null?'  &middot;  watched '+c.steps+' steps':'');
   case 'assistant':
    if(c.action==='tool')return 'decided to call tool  '+c.tool+(c.input&&Object.keys(c.input).length?'(params: '+pairs(c.input)+')':'');
    if(c.action==='final')return 'decision  &mdash;  '+(c.summary||'');
    if(c.content)return String(c.content);
    return JSON.stringify(c);
   case 'tool_call':
    return 'calling tool  '+c.tool+'  (step '+c.step+')'+(c.input&&Object.keys(c.input).length?'  &middot;  '+pairs(c.input):'');
   case 'tool_result':
    return pairs(c)||friendlyTool(c)||JSON.stringify(c);
   case 'planner_error':
    return c.summary||JSON.stringify(c);
   default:
    return JSON.stringify(c);
  }
 }
 function friendlyTool(c){
  const skip=['status','completed'];
  if(c.signal&&c.signal!=='NONE')return 'signal '+c.signal+(c.quantity!=null?' qty '+c.quantity:'');
  return '';
 }
 function pairs(o){
  const out=[];
  for(const k of Object.keys(o||{})){
   const v=o[k];
   if(v===undefined||v===null||v===''||(Array.isArray(v)&&v.length===0)||(typeof v==='object'&&Object.keys(v).length===0))continue;
   if(typeof v==='object')out.push(k+'='+JSON.stringify(v));else out.push(k+'='+v);
  }
  return out.join('  &middot;  ');
 }
 function priceFmt(p){const n=Number(p);return Number.isFinite(n)?n.toFixed(2):p;}
 function markEnded(){ended=true;document.getElementById('more').style.display='none';document.getElementById('end').style.display='block';}
 async function loadOlder(){
  if(loading||ended||!cur)return;loading=true;
  try{
   const st=await j('/api/steps?run_id='+encodeURIComponent(cur)+'&before='+bottomId+'&limit=100');
   for(const s of st.steps)append(s,false);
   if(st.steps.length){bottomId=st.steps[st.steps.length-1].id;updateMeta();}
   if(st.count<100)markEnded();
  }catch(e){/* retry next scroll */}
  finally{loading=false;}
 }
 let obs;
 function watchSentinel(){
  if(!('IntersectionObserver' in window))return;
  obs=new IntersectionObserver(en=>{if(en[0].isIntersecting)loadOlder();},{rootMargin:'300px'});
  obs.observe(document.getElementById('more'));
 }
 async function pull(){
  const st=await j('/api/status');
  if(st.latest_run_id!==cur){
   cur=st.latest_run_id;topId=0;bottomId=0;loading=false;ended=false;
   log().innerHTML='';
   document.getElementById('more').style.display='block';document.getElementById('end').style.display='none';
   if(cur){await refreshRuns();topId=0;await loadTop();}
  }
  updateMeta(st.latest_run_status);
  referenceRuns(st.latest_run_id);
  if(cur){
   const nw=await j('/api/steps?run_id='+encodeURIComponent(cur)+'&after='+topId+'&limit=100');
   if(nw.steps.length){
    const nodes=nw.steps.map(stepNode);
    for(let i=nodes.length-1;i>=0;i--)log().insertBefore(nodes[i],log().firstChild);
    topId=nw.steps[nw.steps.length-1].id;updateMeta();
   }
  }
 }
 function updateMeta(status){document.getElementById('meta').textContent=(cur?cur+' &middot; ':'')+(status||'')+' &middot; '+log().childElementCount+' decisions visible';}
 async function refreshRuns(){const r=await j('/api/runs?limit=6');renderRuns(r.runs);}
 async function referenceRuns(latest){if(!document.getElementById('runs').childElementCount)await refreshRuns();}
 function renderRuns(runs){document.getElementById('runs').innerHTML='recent runs: '+runs.map(r=>'<span class="k">'+esc(r.run_id)+'</span> ('+esc(r.status)+(r.finished_at?', fin '+esc(r.finished_at):'')+')').join(' &middot; ');}
 setInterval(pull,1000);watchSentinel();pull();setTimeout(()=>{if(!cur)document.getElementById('meta').textContent='no run yet &mdash; agent has not started';},4000);
</script></body></html>
"""


def create_app(store: AgentTranscriptStore | None = None) -> FastAPI:
    transcript: AgentTranscriptStore
    if store is None:
        transcript = CockroachAgentTranscriptStore()
    else:
        transcript = store
    transcript.initialize()

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

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app