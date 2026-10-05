"""FastAPI live view of the autonomous agent's visible thinking process."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from .agent_loop import AgentTranscriptStore
from .paper_trading import PaperTrading, paper_from_env, state_backend

DEFAULT_VIEW_HOST = "127.0.0.1"
DEFAULT_VIEW_PORT = 8100

# Ticks that never reached the planner are silent: the heartbeat stays fresh and
# the feed keeps downloading, so liveness checks alone cannot see a stuck loop.
# At the default 60s poll this fires after roughly ten unproductive minutes.
STALE_TICK_ALERT_THRESHOLD = 10
# The Bits risk monitor runs every five seconds. Three missed cycles plus slack is
# enough to conclude it is dead rather than slow.
MONITOR_STALE_SECONDS = 45
# Largest `/api/steps` response body. A captured shell job can contribute up to
# its max_output_bytes (1 MiB) in a single step, so a row limit alone does not
# bound the response.
STEPS_BYTE_BUDGET = 2_000_000


def _read_json_file(path: str) -> dict[str, Any] | None:
    """Read a small status file, or None when it is absent or unreadable.

    A status file that cannot be read is a normal condition (the service may not
    be deployed), not an error to surface on the page.
    """
    try:
        target = Path(path)
        if not target.is_file():
            return None
        payload = json.loads(target.read_text())
        return payload if isinstance(payload, dict) else None
    except (OSError, ValueError):
        return None


def read_status_file() -> dict[str, Any] | None:
    from .agent_status import read_status
    return read_status()


def _engine_display_text(phase: str, c: dict[str, Any]) -> str:
    """One line describing a deterministic engine event.

    Engine events are decided by code, not by a model, so the wording states the
    gate verdict plainly rather than summarising intent.
    """
    side = c.get("side")
    direction = {"BUY": "long", "SELL": "short"}.get(side, "flat")
    if phase == "engine_signal":
        if not side:
            return "Engine: no qualifying signal on this bar."
        return f"Engine signal: {direction} {c.get('quantity', '')}".strip() + "."
    if phase == "engine_decision":
        reason = str(c.get("gate_reason", "")).replace("_", " ").lower()
        accepted = c.get("accepted") is True
        return (f"Engine proposal accepted: {direction} {c.get('quantity', '')}".strip() + "."
                if accepted else f"Engine proposal refused: {reason or 'a risk gate'}.")
    if phase == "engine_fill":
        return (f"Engine filled {direction} {c.get('quantity', '')} at ${c.get('price', 0):,.2f}."
                .replace("  ", " "))
    return str(c.get("summary") or "Engine halted.")


def step_display(step: dict[str, Any]) -> dict[str, str]:
    """Presentation only: never turns an assessment into a confirmed execution."""
    c = step.get("content") or {}
    phase = step.get("phase", "event")
    titles = {"assistant": "Decision", "tool_call": "Tool call", "tool_result": "Tool result",
              "tick_start": "Market check", "tick_end": "Review complete", "data_refresh": "Market data",
              "bits_submit": "Analyzing", "tick_error": "Needs attention", "planner_error": "Needs attention",
              "session_start": "Fresh start", "agent_message": "Thinking",
              "engine_signal": "Engine signal", "engine_decision": "Engine decision",
              "engine_fill": "Engine fill", "engine_halt": "Engine halted",
              "interrogation": "Self-review"}
    title = titles.get(phase, "System update")
    text = "An update was recorded. Expand details to inspect it."
    if phase == "assistant":
        reply = c
        for key in ("reply", "content"):
            try:
                parsed = json.loads(c.get(key, ""))
                if isinstance(parsed, dict): reply = parsed; break
            except (ValueError, TypeError): pass
        text = reply.get("summary") or c.get("summary") or reply.get("reason") or c.get("reason")
        if not text:
            text = c.get("content") if reply is c and not c.get("action") else "Preparing the next action."
        if reply.get("status") == "blocked": title = "Waiting for help"
        elif reply.get("status") == "waiting": title = "Waiting"
        elif reply.get("actions") or reply.get("action") == "tool": title = "Next action"
    elif phase == "tool_call":
        text = c.get("description") or ("Running a shell command on the trading server." if c.get("tool") == "shell"
                                       else "Running " + str(c.get("tool", "a tool")).replace("_", " ") + ".")
    elif phase == "tool_result":
        status = c.get("status")
        if c.get("filled") is True:
            text = "Paper trade filled." if c.get("paper_only") else "Demo trade confirmed."
        elif c.get("filled") is False:
            text = "Trade was not placed: " + str(c.get("gate_reason", "risk gate refusal")).replace("_", " ").lower() + "."
        elif status in {"succeeded", "completed"}:
            text = "Command completed successfully." if "exit_code" in c else "Tool completed successfully."
        elif status == "running": text = "Command is still running."
        elif status == "timed_out": text = "Command exceeded its time limit. Its effects need to be checked before retrying."
        elif status in {"cancelled", "unknown"}: text = "Command was interrupted. Its effects need to be checked before retrying."
        else: text = "Tool did not complete successfully. Expand details for the error."
        if c.get("total_bytes"):
            text += f" Returned {c['total_bytes']:,} bytes of output."
        if c.get("truncated"): text += " Captured output was shortened."
    elif phase == "bits_submit":
        text = "Sent the latest market information, account state, and relevant history to Bits for analysis."
    elif phase == "agent_message":
        # The real agent turn, from the workflow's message stream. The last
        # assistant turn is the most informative, so it leads.
        messages = c.get("messages") or []
        turns = [m for m in messages if isinstance(m, dict) and m.get("content")]
        if not turns:
            text = "The workflow published no message stream for this cycle."
        else:
            last = [m for m in turns if m.get("role") == "assistant"] or turns
            preview = str(last[-1].get("content", "")).strip().replace("\n", " ")
            text = f"{len(turns)} turn(s). Latest: {preview[:280]}"
    elif phase == "interrogation":
        pairs = c.get("pairs") or []
        if not pairs:
            text = c.get("summary") or "The agent reviewed its own reasoning."
        else:
            first = pairs[0] if isinstance(pairs[0], dict) else {}
            text = f"{len(pairs)} self-question(s). First: {str(first.get('question', ''))[:200]}"
    elif phase in {"engine_signal", "engine_decision", "engine_fill", "engine_halt"}:
        text = _engine_display_text(phase, c)
    elif phase == "data_refresh":
        if c.get("ok"): text = f"Market data updated with {c.get('downloaded_rows', 0):,} downloaded bars."
        elif c.get("skipped"): text = "Waiting before the next market-data refresh."
        else: text = "Market data could not be refreshed. Trading requires a fresh feed."
    elif phase == "tick_start":
        text = f"Gold is ${c['price']:,.2f}." if isinstance(c.get("price"), (int, float)) else "Checking the market."
        if c.get("market_open") is False: text += " The market is closed; no new trade will be placed."
        elif c.get("fresh") is False: text += " The data is stale; waiting for an update."
        elif c.get("fresh") is True: text += " Market data is fresh."
    elif phase in {"tick_end", "tick_error", "planner_error", "session_start"}:
        text = c.get("summary") or "This check could not complete. The next check will retry safely."
    return {"title": title, "text": str(text or "The agent recorded a decision; expand details to inspect it.")}

_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>xauusd agent - live thinking</title>
<style>
 body{background:#0d1017;color:#d7dde6;font:13px/1.45 ui-monospace,Menlo,monospace;margin:0;padding:16px}
h1{font-size:15px;color:#8ab4f8;margin:0 0 4px}
  #meta{color:#7f8ea3;margin-bottom:8px;min-height:15px}
  #health{margin:0 0 8px;padding:6px 10px;border:1px solid #2a3444;border-radius:4px;font-size:12px;color:#7f8ea3}
  #health.ok{color:#4dab6d;border-color:#274a33}
  #health.problem{color:#e3746e;border-color:#5c2a28}
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
 .step summary{color:#7f8ea3;cursor:pointer;font-size:12px;list-style:none}
 .step summary::-webkit-details-marker{display:none}
 .step summary::before{content:'>';display:inline-block;margin-right:8px;transition:transform .15s}
 .step details[open]>summary::before{transform:rotate(90deg)}
 .step h3{font-size:12px;color:#8ab4f8;margin:12px 0 3px}
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
<div id="health">checking&hellip;</div>
<div id="paper">paper &mdash; checking&hellip;</div>
<div id="session" style="color:#8ab4f8;margin-bottom:8px"></div>
<details><summary>Run history</summary><div id="runs"></div></details>
<div id="log"></div>
<div id="more">load older decisions&hellip;</div>
<div id="end" style="display:none">end of history</div>
<script>
 let cur=null, topId=0, bottomId=0, loading=false, ended=false;
 const rendered=new Set();
 const $=id=>document.getElementById(id);
 const esc=t=>String(t).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 async function j(u){const r=await fetch(u);if(!r.ok)throw Error(r.status);return r.json();}
 // Display timezone only. Persisted timestamps, bar indices, and the market-hours
 // gate all stay UTC; GMT+8 is a fixed offset here, never the browser's own zone.
 const DISPLAY_OFFSET_MINUTES=480;
 function parseWhen(iso){
  const s=String(iso||'');if(!s)return null;
  const d=new Date(/(Z|[+-]\\d\\d:?\\d\\d)$/.test(s)?s:s+'Z');  // a naive stamp is UTC
  return isNaN(d)?null:d;
 }
 function shiftDisplay(d){return new Date(d.getTime()+DISPLAY_OFFSET_MINUTES*60000);}
 function fmtTime(iso){if(!iso)return '?';const d=parseWhen(iso);return d?shiftDisplay(d).toISOString().slice(11,19)+' +08:00':String(iso);}
 function fmtBar(iso){const d=parseWhen(iso);return d?shiftDisplay(d).toISOString().slice(11,16)+' +08:00':String(iso);}
 function stepNode(s){
  if(rendered.has(s.id))return null;rendered.add(s.id);
  const d=document.createElement('div');d.className='step '+s.phase;
  const b=document.createElement('b');
  b.textContent=(s.display?s.display.title:s.phase.replaceAll('_',' '))+'  ·  '+fmtTime(s.occurred_at);
  d.appendChild(b);
  const hu=document.createElement('div');hu.className='human';hu.textContent=s.display?s.display.text:'Activity recorded. Expand details to inspect it.';d.appendChild(hu);
  const det=document.createElement('details');
  const sm=document.createElement('summary');sm.textContent='Details';det.appendChild(sm);
  const c=s.content||{};
  function section(label,text){if(text===undefined||text===null||text==='')return;
   const h=document.createElement('h3');h.textContent=label;det.appendChild(h);
   const p=document.createElement('pre');p.textContent=String(text);det.appendChild(p);}
  if(c.input&&c.input.command){section('Command',c.input.command);section('Working directory',c.input.cwd);}
  section('Output',c.stdout);section('Errors',c.stderr);
  const raw=document.createElement('details');const rs=document.createElement('summary');rs.textContent='Technical data (raw json)';raw.appendChild(rs);
  const pre=document.createElement('pre');pre.textContent=JSON.stringify(c,null,2);raw.appendChild(pre);det.appendChild(raw);
  d.appendChild(det);return d;
 }
 function addNode(n,atTop){if(!n)return;if(atTop&&$('log').firstChild)$('log').insertBefore(n,$('log').firstChild);else $('log').appendChild(n);}
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
   $('session').textContent=st.session_reset?'Fresh session · started '+fmtTime(st.session_reset.recorded_at)+
    ' · starting paper balance $'+fmtMoney(st.session_reset.initial_cash):'';
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
    await refreshHealth();
   }catch(e){/* transient; next poll retries */}
 }
 function updateMeta(status){
  const detail=cur?('Agent '+(status||'running')):'Waiting for the agent to start';
  $('meta').textContent=detail+'  ·  '+rendered.size+' activity updates';
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
  async function refreshHealth(){
   try{const h=await j('/api/health');const el=$('health');
    const du=h.data_update||{};const gap=du.age_seconds!=null?' · feed gap '+Math.round(du.age_seconds)+'s':'';
    const bar=du.end?(' · last bar '+fmtBar(du.end)):'';
    el.textContent=(h.alerts&&h.alerts.length)?'ATTENTION: '+h.alerts.join('  ·  '):'healthy'+bar+gap;
    const beat=(h.agent||{}).heartbeat||{};
    const states={bits_waiting:'Bits is analyzing',shell_running:'A command is running',waiting:'Waiting for the next review',
     completed:'Review complete',market_closed:'Market closed',stopped:'Agent stopped',starting:'Starting up'};
    if(cur)$('meta').textContent=(states[beat.status]||'Monitoring the market')+
     (beat.next_review_at?' · next review '+fmtTime(beat.next_review_at):'')+' · '+rendered.size+' activity updates';
    el.className=h.status==='ok'?'ok':'problem';}catch(e){}
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
  let html='<div class="k">'+(p.mode==='demo'?'CTRADER DEMO':'PAPER TRADING · simulated orders')+'</div>'+paperHeadline(s,risk);
  if(s.recent_fills.length)html+='<div class="fills">fills: '+s.recent_fills.map(renderFill).join('  ·  ')+'</div>';
  $('paper').innerHTML=html;
 }
 setInterval(pull,1000);watchSentinel();pull();
 setTimeout(()=>{if(!cur)$('meta').textContent='no run yet  -  agent has not started';},4000);
</script></body></html>
"""


def create_app(store: AgentTranscriptStore | None = None,
               paper: PaperTrading | None = None) -> FastAPI:
    from .agent_loop import agent_transcript_store_from_env
    transcript: AgentTranscriptStore
    if store is None:
        transcript = agent_transcript_store_from_env()
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
        reset = None
        if hasattr(transcript, "connect"):
            from .bits_jobs import BitsStore
            reset = BitsStore(transcript).get("session_reset")
        return {"latest_run_id": runs[0]["run_id"] if runs else None,
                "latest_run_status": runs[0]["status"] if runs else None, "session_reset": reset}

    @app.get("/api/runs")
    def runs(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, Any]:
        return {"runs": transcript.runs(limit)}

    @app.get("/api/steps")
    def steps(run_id: str | None = Query(default=None), after: int | None = Query(default=None, ge=0),
              before: int | None = Query(default=None, ge=1),
              limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
        desc = before is not None or after is None
        # A byte budget as well as a row limit. `limit` alone is not a bound on
        # response size: a shell-job step can carry a captured stdout of up to the
        # job's max_output_bytes, so a single request could serialise tens of
        # megabytes and the page then runs JSON.stringify over all of it.
        rows = transcript.steps(run_id, after_id=after or 0, before_id=before, desc=desc, limit=limit)
        served: list[dict[str, Any]] = []
        used = 0
        truncated = False
        for row in rows:
            # Measure the serialised size, not len(str(content)): the budget is a
            # response-body bound and a Python repr is neither the bytes sent nor
            # proportional to them.
            size = len(json.dumps(row.get("content"), default=str))
            if served and used + size > STEPS_BYTE_BUDGET:
                truncated = True
                break
            used += size
            served.append({**row, "display": step_display(row)})
        run_status = transcript.run_status(run_id) if run_id else None
        return {"run_id": run_id, "run_status": run_status, "order": "desc" if desc else "asc",
                "after": after, "before": before, "count": len(served), "steps": served,
                "truncated": truncated, "bytes": used, "byte_budget": STEPS_BYTE_BUDGET}

    @app.get("/harness", response_class=HTMLResponse)
    def harness_page() -> str:
        """The nof1-style live harness page.

        A second page rather than a replacement: the original compact view is
        still the right tool for reading a specific cycle, and this one is for
        watching the harness work. Read-only by construction, so an operator
        command can never be issued from a browser.
        """
        from .harness_page import _HARNESS_PAGE
        return _HARNESS_PAGE

    @app.get("/api/harness")
    def harness() -> dict[str, Any]:
        """Everything the page shows at a glance, in one call.

        The 1 Hz sweep made five sequential requests per second for the whole
        page. This is one request for the same facts: the engine, the current
        cycle phase, the memory and notes, and the live feed. It is the polled
        companion to the event stream, so a page still works without SSE.
        """
        from .bits_jobs import BitsStore
        try:
            store = BitsStore(transcript)
            cycle = store.get("cycle") or {}
            notes = (store.get("working_notes") or {}).get("notes", {})
            progress = store.get("research_progress", {})
        except Exception:
            # A non-SQLite transcript store (the in-memory double, or a backend
            # without bits_state) must not take the page down; the panel simply
            # shows less.
            cycle, notes, progress = {}, {}, {}
        heartbeat = read_status_file()
        return {
            "engine": _read_json_file(os.getenv("ENGINE_STATUS_PATH", "reports/engine_status.json")),
            "data_feed": _read_json_file(os.getenv("DATA_FEED_STATUS_PATH",
                                                   "reports/data_feed_status.json")),
            "cycle": {"phase": cycle.get("phase", "idle"), "steps": cycle.get("steps", 0),
                      "submitted_at": cycle.get("submitted_at"),
                      "next_at": cycle.get("next_at"),
                      "instance": cycle.get("instance"),
                      "job_id": cycle.get("job_id")},
            "working_notes": notes,
            "research_progress": progress,
            "heartbeat": {k: (heartbeat or {}).get(k) for k in
                          ("status", "last_tick_status", "tick", "recorded_at", "next_review_at",
                           "kill_switch_reason", "monitor", "monitor_error")},
        }

    @app.get("/api/stream")
    async def stream(request: Request, after: int = Query(default=0, ge=0)) -> StreamingResponse:
        """Server-sent events for transcript rows, newest-first like the page.

        Polling replaced this: while a model round trip is in flight (22.8s
        median) the transcript receives nothing, so the page looked frozen for a
        minute at a time with no indication anything was happening. Each new row is
        pushed the moment it is committed, because the agent and this view share
        the same SQLite database in WAL mode.

        A heartbeat comment is sent on every idle tick so proxies keep the
        connection open and the client can show "connected, nothing new".
        """
        import asyncio

        async def events():
            cursor = after
            last_keepalive = 0.0
            while not await request.is_disconnected():
                rows = await asyncio.to_thread(transcript.steps, None, cursor, None, True, 100)
                for row in rows:
                    cursor = max(cursor, int(row["id"]))
                    payload = {**row, "display": step_display(row)}
                    yield f"event: step\nid: {row['id']}\ndata: {json.dumps(payload, default=str)}\n\n"
                if not rows:
                    now = time.monotonic()
                    if now - last_keepalive >= 10:
                        last_keepalive = now
                        yield ": keepalive\n\n"
                await asyncio.sleep(1)

        return StreamingResponse(events(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.get("/api/job")
    def job_output(job_id: str = Query(...), stream: str = Query(default="stdout", pattern="^(stdout|stderr)$"),
                   offset: int = Query(default=0, ge=0), limit: int = Query(default=8000, ge=1, le=65536)) -> dict[str, Any]:
        """A page of one shell job's captured output.

        The transcript caps each stored result, so most of a large capture was
        unreachable from the UI and only retrievable by the agent through the CLI.
        """
        from .bits_jobs import BitsStore
        try:
            record = BitsStore(transcript).job(job_id)
        except Exception as exc:
            return {"status": "unavailable", "error_type": type(exc).__name__}
        text = record.get(stream) or ""
        if offset > len(text):
            return {"status": "rejected", "error": {"code": "offset_out_of_range",
                                                    "stored_characters": len(text)}}
        end = min(len(text), offset + limit)
        return {"job_id": job_id, "status": record.get("status"), "stream": stream,
                "offset": offset, "text": text[offset:end],
                "next_offset": end if end < len(text) else None,
                "stored_characters": len(text), "truncated": record.get("truncated")}

    @app.get("/api/paper")
    def paper_endpoint() -> dict[str, Any]:
        pt = paper_or_default()
        return {"mode": "paper" if os.getenv("CTRADER_PAPER_ONLY") == "true" else "demo",
                "paper": {"summary": pt.summary(), "risk": {
            key: getattr(pt.config, key) for key in ("daily_loss_limit", "max_drawdown", "max_position",
                                                     "max_trades_per_day", "max_market_data_age_seconds")}}}

    @app.get("/api/data-update")
    def data_update_status() -> dict[str, Any]:
        path = Path(os.getenv("CTRADER_DATA_UPDATE_STATUS_PATH", "reports/data_update_status.json"))
        try:
            payload = dict(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return {"exists": False, "state": None, "recorded_at": None, "error_code": None}
        return {"exists": True, **payload}

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        from .agent_status import bits_alerts, read_status
        alerts: list[str] = []
        # The health endpoint is the designated observability surface. A state
        # store outage must report `degraded`, not raise: an unhandled exception
        # here returned HTTP 500, which reads as "the agent is fine, the view is
        # broken" rather than "we cannot see the account at all".
        try:
            pt = paper_or_default()
            paper_state = pt.state()
            market_open = pt.summary().get("market_open")
        except Exception as exc:
            return {"status": "degraded",
                    "alerts": [f"state store unavailable ({type(exc).__name__})"],
                    "agent": {}, "paper": {}, "data_update": {}, "database": {}}
        heartbeat = read_status()
        heartbeat_age = _age_seconds((heartbeat or {}).get("recorded_at"))
        runs = transcript.runs(limit=1)
        latest = runs[0] if runs else None
        if heartbeat is None:
            alerts.append("agent heartbeat missing")
        elif heartbeat.get("stalled"):
            alerts.append(f"agent stalled ({heartbeat.get('consecutive_errors', 0)} consecutive errors)")
        elif heartbeat.get("status") in {"planner_error", "tick_error"}:
            code = heartbeat.get("error_code")
            alerts.append(f"agent last tick {heartbeat.get('status')}" + (f" ({code})" if code else ""))
        if (heartbeat or {}).get("status") in {"bits_blocked", "recovery_failed"}:
            alerts.append("Bits agent requires attention")
        progress = (heartbeat or {}).get("research_progress") or {}
        if progress.get("needs_attention"):
            alerts.append(f"Research progress needs review: {progress.get('cycles_without_new_notes')} cycles without updated research notes")
        alerts.extend(bits_alerts(heartbeat))
        monitor = (heartbeat or {}).get("monitor") or {}
        if monitor.get("status") in {"unavailable", "stale_data"}:
            alerts.append("position monitor " + monitor["status"])
        # The monitor's status *string* alone was not enough: a monitor that died
        # after one healthy cycle kept reporting {status: ok} forever with a frozen
        # timestamp, and no risk_limit stop was ever persisted. Age is the check.
        monitor_age = _age_seconds(monitor.get("recorded_at"))
        if monitor and (monitor_age is None or monitor_age > MONITOR_STALE_SECONDS):
            alerts.append(f"position monitor stale ({int(monitor_age or 0)}s)")
        if (heartbeat or {}).get("monitor_error"):
            alerts.append(f"position monitor error ({heartbeat['monitor_error']})")
        if (heartbeat or {}).get("monitor_thread_alive") is False:
            alerts.append("position monitor thread is not running")
        stale_ticks = int((heartbeat or {}).get("consecutive_stale_ticks") or 0)
        if stale_ticks >= STALE_TICK_ALERT_THRESHOLD:
            alerts.append(f"agent unproductive: {stale_ticks} consecutive stale-data ticks")
        if heartbeat_age is not None and heartbeat_age > 600:
            alerts.append(f"agent heartbeat stale ({int(heartbeat_age)}s)")
        if paper_state.get("stopped"):
            alerts.append(f"paper trading stopped: {paper_state.get('kill_switch_reason')}")
        data = data_update_status()
        if data.get("state") in {"auth_error", "failed"}:
            alerts.append(f"data update {data.get('state')}")
        integrity = "checks not available"
        if state_backend() == "local":
            try:
                integrity = pt.integrity_check()
                if integrity != "ok":
                    alerts.append(f"state database integrity: {integrity}")
            except Exception as exc:
                integrity = f"error ({type(exc).__name__})"
                alerts.append("state database integrity check failed")
        # Storage size in the health payload. These tables previously grew with no
        # bound and no reader anywhere reported their size, so growth was invisible
        # until the database became a problem.
        try:
            from .bits_jobs import BitsStore
            storage = BitsStore(transcript).storage()
        except Exception as exc:
            storage = {"error_type": type(exc).__name__}
        # Feed state, informational only: it is deliberately not an alert, because
        # the feed is not deployed yet. It is surfaced so a feed that is deployed
        # and failing cannot be invisible, which is how a Restart=always loop
        # against an unimplemented feed went unnoticed.
        data_feed = _feed_health()
        return {"status": "ok" if not alerts else "degraded", "alerts": alerts,
                "agent": {"heartbeat": heartbeat, "heartbeat_age_seconds": heartbeat_age,
                          "latest_run_id": latest["run_id"] if latest else None,
                          "latest_run_status": latest["status"] if latest else None},
                "paper": {"stopped": paper_state.get("stopped"),
                          "kill_switch_reason": paper_state.get("kill_switch_reason"),
                          "market_open": market_open},
                "monitor": {"status": monitor.get("status"), "age_seconds": monitor_age,
                            "error": (heartbeat or {}).get("monitor_error"),
                            "thread_alive": (heartbeat or {}).get("monitor_thread_alive")},
                "data_update": {**data, "age_seconds": _age_seconds(data.get("recorded_at"))},
                "data_feed": data_feed,
                "storage": storage,
                "database": {"backend": state_backend(), "integrity": integrity}}

    return app


def _feed_health() -> dict[str, Any]:
    """Whatever the live feed last recorded, or that it has never run.

    Never raises: health is the one endpoint that must answer when something else
    is broken. A missing file is reported as ``not_deployed`` rather than guessed
    at, so an absent feed is distinguishable from a feed that failed to start.
    """
    try:
        from .live_feed import LiveFeedConfig
        path = Path(LiveFeedConfig.from_env().status_path)
    except Exception as exc:  # noqa: BLE001 - health must not depend on config loading
        return {"state": "unknown", "error_type": type(exc).__name__}
    if not path.is_file():
        return {"state": "not_deployed"}
    try:
        status = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        return {"state": "unreadable", "error_type": type(exc).__name__}
    return {**status, "age_seconds": _age_seconds(status.get("recorded_at"))}


def _age_seconds(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        moment = datetime.fromisoformat(iso)
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - moment.astimezone(timezone.utc)).total_seconds()
    except ValueError:
        return None
