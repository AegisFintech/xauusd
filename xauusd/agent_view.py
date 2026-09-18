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
 #meta{color:#7f8ea3;margin-bottom:12px}
 .step{margin:6px 0;padding:8px 10px;border-left:3px solid #2a3444;background:#141a24;border-radius:0 4px 4px 0;white-space:pre-wrap;word-break:break-word}
 .step.tick_start,.step.tick_end{border-color:#8ab4f8;color:#c7d5ee}
 .step.tick_error,.step.planner_error{border-color:#e3746e;background:#241a1f}
 .step.assistant{border-color:#f2c14e;background:#201c12}
 .step.tool_call{border-color:#4dab6d}
 .step.tool_result{border-color:#5b87b8}
 .step b{display:block;color:#8ab4f8;margin-bottom:2px}
 .k{color:#7f8ea3}
</style></head><body>
<h1>xauusd autonomous agent &mdash; live thinking</h1>
<div id="meta">connecting&hellip;</div>
<div id="log"></div>
<script>
 const seen=new Set(); let latestRun=null; let after=0;
 async function j(u){const r=await fetch(u);if(!r.ok)throw Error(r.status);return r.json();}
 async function poll(){
  try{
   if(!latestRun){const rs=await j('/api/status');latestRun=rs.latest_run_id;
     const runs=await j('/api/runs?limit=6');renderRuns(runs.runs);}
   if(latestRun){const st=await j('/api/steps?run_id='+encodeURIComponent(latestRun)+'&after='+after+'&limit=200');
     for(const s of st.steps){if(seen.has(s.id))continue;seen.add(s.id);after=Math.max(after,s.id);render(s);}
     const info=document.getElementById('meta');
     info.textContent='run '+latestRun+' &middot; '+st.run_status+' &middot; '+st.count+' steps';
     scroll();}
  }catch(e){/* retry */}
 }
 function renderRuns(runs){const el=document.createElement('div');el.style.color='#7f8ea3';
  el.innerHTML='recent runs: '+runs.map(r=>htmlEsc(r.run_id)+' ('+r.status+')').join(' &middot; ');
  document.getElementById('log').prepend(el);}
 function render(s){
  const d=document.createElement('div');d.className='step '+s.phase;
  const b=document.createElement('b');b.textContent=s.phase.toUpperCase()+' #'+s.id+' tick '+s.tick;
  d.appendChild(b);
  const body=document.createElement('span');
  body.textContent=pretty(s.content);
  d.appendChild(body);document.getElementById('log').appendChild(d);
 }
 function pretty(o){try{return JSON.stringify(o,null,1);}catch(_){return String(o);}}
 function htmlEsc(t){return t.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
 function scroll(){const g=document.getElementById('log');if(g.children.length>200){g.firstChild.remove();}}
 setInterval(poll,1000);poll();setTimeout(()=>{const m=document.getElementById('meta');m.textContent='live&middot;no run yet&mdash;agent has not started';},4000);
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
    def steps(run_id: str | None = Query(default=None), after: int = Query(default=0, ge=0),
              limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
        rows = transcript.steps(run_id, after, limit)
        run_status = transcript.run_status(run_id) if run_id else None
        return {"run_id": run_id, "run_status": run_status, "after": after, "count": len(rows), "steps": rows}

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app