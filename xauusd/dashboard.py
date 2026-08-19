from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import os
import secrets
import shutil
import threading
import time
import asyncio
import subprocess

import pandas as pd
import plotly.graph_objects as go
from .experiment_registry import ExperimentRegistry
from .search_space import catalog_size
from .operations import OperationsManager
from .shadow_trading import ShadowTradingReadiness
from .distributed_compute import RemoteComputeBridge
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials


REPORTS = Path(os.getenv("XAUUSD_REPORTS_DIR", "reports")).resolve()
DATA_FILE = Path(os.getenv("XAUUSD_DATA_FILE", "data/processed/XAUUSD_M1.parquet")).resolve()
security = HTTPBasic(auto_error=False)
app = FastAPI(title="XAUUSD Research Dashboard", version="0.7.0")
log = logging.getLogger("xauusd.dashboard")
_monitor_lock=threading.Lock()
_monitor_sample: dict | None=None
_portfolio_chart_cache: dict={}


def _read_proc(path: str) -> str:
    try: return Path(path).read_text()
    except (FileNotFoundError,PermissionError,OSError): return ""


def _bytes(value: int | float) -> dict:
    return {"bytes":int(value),"gb":round(value/1024**3,2)}


def _service_process(service: str) -> dict:
    pids=[line for line in _read_proc(f"/sys/fs/cgroup/system.slice/{service}.service/cgroup.procs").splitlines() if line]
    if not pids: return {"service":service,"running":False}
    pid=int(pids[0]); status={}
    for line in _read_proc(f"/proc/{pid}/status").splitlines():
        if ":" in line:
            key,value=line.split(":",1); status[key]=value.strip()
    stat=_read_proc(f"/proc/{pid}/stat").split(); uptime=float(_read_proc("/proc/uptime").split()[0] or 0)
    ticks=os.sysconf("SC_CLK_TCK"); process_seconds=(float(stat[13])+float(stat[14]))/ticks if len(stat)>21 else 0
    elapsed=max(.001,uptime-float(stat[21])/ticks) if len(stat)>21 else .001
    memory_kb=int(status.get("VmRSS","0 kB").split()[0])
    return {"service":service,"running":True,"pid":pid,"memory":_bytes(memory_kb*1024),
            "cpu_percent":round(100*process_seconds/elapsed,2),"uptime_seconds":round(elapsed),
            "threads":int(status.get("Threads",0))}


def system_metrics() -> dict:
    global _monitor_sample
    now=time.monotonic(); memory={}
    for line in _read_proc("/proc/meminfo").splitlines():
        key,value=line.split(":",1); memory[key]=int(value.strip().split()[0])*1024
    total=memory.get("MemTotal",0); available=memory.get("MemAvailable",0); used=max(0,total-available)
    disk=shutil.disk_usage(Path.cwd()); load=tuple(map(float,_read_proc("/proc/loadavg").split()[:3] or (0,0,0)))
    network={}
    for line in _read_proc("/proc/net/dev").splitlines()[2:]:
        interface,raw=line.split(":",1); values=raw.split(); name=interface.strip()
        if name!="lo": network[name]={"rx_bytes":int(values[0]),"tx_bytes":int(values[8])}
    with _monitor_lock:
        previous=_monitor_sample; _monitor_sample={"time":now,"network":network}
    elapsed=now-previous["time"] if previous else 0
    rx=sum(row["rx_bytes"] for row in network.values()); tx=sum(row["tx_bytes"] for row in network.values())
    old_rx=sum(row["rx_bytes"] for row in previous["network"].values()) if previous else rx
    old_tx=sum(row["tx_bytes"] for row in previous["network"].values()) if previous else tx
    cpu_count=os.cpu_count() or 1
    return {"cpu":{"cores":cpu_count,"load_1m":load[0],"load_5m":load[1],"load_15m":load[2],
                   "load_percent":round(100*load[0]/cpu_count,1)},
            "memory":{"total":_bytes(total),"used":_bytes(used),"available":_bytes(available),
                      "percent":round(100*used/total,1) if total else 0},
            "disk":{"path":str(Path.cwd()),"total":_bytes(disk.total),"used":_bytes(disk.used),
                    "free":_bytes(disk.free),"percent":round(100*disk.used/disk.total,1)},
            "network":{"interfaces":network,"rx":_bytes(rx),"tx":_bytes(tx),
                       "rx_bytes_per_second":round(max(0,rx-old_rx)/elapsed) if elapsed else 0,
                       "tx_bytes_per_second":round(max(0,tx-old_tx)/elapsed) if elapsed else 0},
            "services":[_service_process("xauusd-tournament"),_service_process("xauusd-dashboard")]}


@app.middleware("http")
async def request_log(request: Request, call_next):
    started = time.monotonic()
    response = await call_next(request)
    log.info(json.dumps({"event": "http_request", "method": request.method, "path": request.url.path,
                         "status": response.status_code, "duration_ms": round((time.monotonic()-started)*1000, 2)}))
    return response


def authenticate(credentials: HTTPBasicCredentials | None = Depends(security)) -> str:
    expected_user = os.getenv("DASHBOARD_USERNAME")
    expected_password = os.getenv("DASHBOARD_PASSWORD")
    if not expected_user and not expected_password:
        return "local"
    valid = bool(credentials and expected_user and expected_password)
    if valid:
        valid = secrets.compare_digest(credentials.username.encode(), expected_user.encode())
        valid &= secrets.compare_digest(credentials.password.encode(), expected_password.encode())
    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required",
                            headers={"WWW-Authenticate": "Basic"})
    return credentials.username


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


def latest_manifest() -> dict | None:
    pointer = read_json(REPORTS / "automation" / "latest.json")
    if not pointer:
        return None
    path = Path(pointer["path"])
    if not path.is_absolute():
        path = Path.cwd() / path
    return read_json(path / "manifest.json")


def data_status() -> dict:
    if not DATA_FILE.exists():
        return {"available": False, "path": str(DATA_FILE)}
    frame = pd.read_parquet(DATA_FILE, columns=["close"])
    end = frame.index.max()
    now = pd.Timestamp.now("UTC")
    age = (now - end).total_seconds() / 3600
    return {"available": True, "path": str(DATA_FILE), "rows": len(frame),
            "start": frame.index.min().isoformat(), "end": end.isoformat(),
            "age_hours": age, "fresh": age <= 48}


def scheduler_status() -> dict:
    state = read_json(REPORTS / "automation" / "status.json", {"status": "never_run"})
    timer = read_json(REPORTS / "automation" / "timer.json", {})
    return {**state, **timer}


def tournament_status() -> dict | None:
    pointer = read_json(Path("data/tournaments/active.json"))
    return read_json(Path(pointer["manifest"])) if pointer else None


def tournament_champion() -> dict | None:
    tournament = tournament_status()
    if not tournament:
        return None
    return read_json(REPORTS / "tournament" / tournament["version"] / "champion.json")


def tournament_worker_status() -> dict:
    state = read_json(REPORTS / "tournament" / "worker-status.json", {"state": "not_started"})
    updated = state.get("updated_at")
    if updated:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(updated)).total_seconds()
        state["heartbeat_age_seconds"] = max(0, age)
        state["healthy"] = state.get("state") in {"running", "idle"} and age < 120
    else:
        state["healthy"] = False
    return state


def proposal_status() -> dict | None:
    return read_json(REPORTS/"tournament"/"proposals.json")


def codex_status() -> dict:
    return read_json(REPORTS/"tournament"/"codex"/"latest.json",{"status":"never_run","auto_merge":False})


def adaptive_status() -> dict | None:
    return read_json(REPORTS/"tournament"/"adaptive.json")


def distributed_status() -> dict:
    return read_json(REPORTS/"tournament"/"distributed"/"status.json",{"state":"not_started","active":0})


def portfolio_status() -> dict | None:
    return read_json(REPORTS/"tournament"/"portfolio"/"latest.json")


def weekly_report_status() -> dict | None:
    return read_json(REPORTS/"tournament"/"weekly"/"latest.json")


def registry() -> ExperimentRegistry | None:
    path=Path(os.getenv("XAUUSD_EXPERIMENT_DB", "data/experiments/registry.sqlite3"))
    return ExperimentRegistry(path,initialize=False) if path.exists() else None


def recent_logs(lines: int=30) -> list[str]:
    try:
        result=subprocess.run(["journalctl","-u","xauusd-tournament.service","-n",str(lines),"--no-pager","-o","short-iso"],
                              capture_output=True,text=True,timeout=3)
        return result.stdout.splitlines()[-lines:]
    except (OSError,subprocess.SubprocessError): return []


def live_snapshot(include_static: bool=True) -> dict:
    database=registry(); summary=database.summary() if database else {"total":0,"by_status":{},"strategy_families":0,"promoted":0}
    result={"sent_at":datetime.now(timezone.utc).isoformat(),"tournament_worker":tournament_worker_status(),
            "experiments":{**summary,"catalog_size":catalog_size()},"system":system_metrics(),
            "operations":OperationsManager().health(),"adaptive":adaptive_status(),"distributed":distributed_status()}
    if include_static:
        result.update({"champion":tournament_champion() or read_json(REPORTS/"champion.json"),
                       "proposals":proposal_status(),"codex":codex_status(),
                       "portfolio":portfolio_status(),"logs":recent_logs()})
    return result


@app.get("/health")
def health():
    return {"status": "ok", "mode": "research-only"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/api/status")
def api_status(_: str = Depends(authenticate)):
    data = data_status()
    manifest = latest_manifest()
    return {"status": "ok" if data.get("fresh") else "degraded", "mode": "research-only",
            "data": data, "latest_run": manifest["run_id"] if manifest else None,
            "champion": tournament_champion() or read_json(REPORTS / "champion.json"), "scheduler": scheduler_status(),
            "tournament_worker": tournament_worker_status(),
            "proposals":proposal_status(),
            "codex":codex_status(),
            "adaptive":adaptive_status(),
            "distributed":distributed_status(),
            "system":system_metrics(),
            "portfolio":portfolio_status(),
            "weekly":weekly_report_status(),
            "shadow":ShadowTradingReadiness().readiness(),
            "operations":OperationsManager().health(),
            "tournament": tournament_status(), "experiments": {**(registry().summary() if registry() else
            {"total":0,"by_status":{},"strategy_families":0,"promoted":0}),"catalog_size":catalog_size()}}


@app.get("/api/live")
async def live(request: Request, _: str = Depends(authenticate)):
    async def events():
        last_signature=None; sequence=0
        while not await request.is_disconnected():
            snapshot=await asyncio.to_thread(live_snapshot,sequence==0)
            signature=(snapshot["experiments"].get("by_status",{}).get("completed",0),
                       snapshot["experiments"].get("by_status",{}).get("running",0),
                       snapshot["tournament_worker"].get("last_experiment_id"))
            snapshot["experiment_changed"]=signature!=last_signature
            last_signature=signature; sequence+=1
            yield f"event: snapshot\ndata: {json.dumps(snapshot,allow_nan=False)}\n\n"
            await asyncio.sleep(5)
    return StreamingResponse(events(),media_type="text/event-stream",headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})


@app.get("/api/operations/logs")
def operation_logs(lines: int=Query(30,ge=1,le=200),_: str=Depends(authenticate)):
    return {"lines":recent_logs(lines)}


@app.get("/api/leaderboard")
def leaderboard(_: str = Depends(authenticate)):
    manifest = latest_manifest()
    if manifest:
        return manifest["candidates"]
    legacy = read_json(REPORTS / "leaderboard.json", [])
    return legacy


@app.get("/api/runs")
def runs(limit: int = Query(20, ge=1, le=100), _: str = Depends(authenticate)):
    items = []
    for path in sorted((REPORTS / "automation").glob("*/manifest.json"), reverse=True)[:limit]:
        manifest = read_json(path)
        items.append({"run_id": manifest["run_id"], "created_at": manifest["created_at"],
                      "data": manifest["data"], "promotion": manifest["promotion"],
                      "best": manifest["candidates"][0] if manifest["candidates"] else None})
    return items


@app.get("/api/history")
def history(limit: int = Query(100, ge=1, le=500), _: str = Depends(authenticate)):
    items = []
    for path in sorted((REPORTS / "automation").glob("*/manifest.json"))[-limit:]:
        manifest = read_json(path)
        for candidate in manifest["candidates"]:
            items.append({"run_id": manifest["run_id"], "created_at": manifest["created_at"],
                          "strategy": candidate["strategy"], "score": candidate["score"],
                          "net_profit": candidate["net_profit"], "profit_factor": candidate["profit_factor"],
                          "max_drawdown": candidate["max_drawdown"], "passed": candidate["passed"]})
    return items


@app.get("/api/history/chart")
def history_chart(_: str = Depends(authenticate)):
    items = history(500, _)
    figure = go.Figure()
    strategies = sorted({item["strategy"] for item in items})
    for strategy in strategies:
        rows = [item for item in items if item["strategy"] == strategy]
        figure.add_trace(go.Scatter(x=[row["created_at"] for row in rows], y=[row["net_profit"] for row in rows],
                                    name=strategy, mode="lines+markers"))
    figure.update_layout(template="plotly_dark", title="Historical Net P&L by Automated Run",
                         xaxis_title="Run", yaxis_title="Net P&L")
    return json.loads(figure.to_json())


@app.get("/api/experiments")
def experiments(status_filter: str | None = Query(None, alias="status"), limit: int = Query(100, ge=1, le=500),
                _: str = Depends(authenticate)):
    allowed = {None,"queued","running","completed","failed","cancelled"}
    if status_filter not in allowed:
        raise HTTPException(400,"invalid experiment status")
    database=registry()
    return database.list(status_filter,limit) if database else []


@app.get("/api/experiments/{experiment_id}")
def experiment_detail(experiment_id: int, _: str = Depends(authenticate)):
    try:
        database=registry()
        if database is None: raise KeyError(experiment_id)
        item=database.get(experiment_id)
    except KeyError:
        raise HTTPException(404,"experiment not found")
    item["events"]=database.events(experiment_id)
    return item


@app.get("/api/tournament/leaderboard")
def tournament_leaderboard(limit: int = Query(25, ge=1, le=100), _: str = Depends(authenticate)):
    database=registry()
    return database.leaderboard(limit) if database else []


@app.get("/api/tournament/champions")
def tournament_champions(limit: int = Query(100, ge=1, le=500), _: str = Depends(authenticate)):
    database=registry(); tournament=tournament_status()
    return database.champion_history(tournament["version"],limit) if database and tournament else []


@app.get("/api/tournament/equity/{experiment_id}")
def tournament_equity(experiment_id: int, _: str = Depends(authenticate)):
    database=registry()
    try:
        item=database.get(experiment_id) if database else None
    except KeyError:
        item=None
    if not item or not item.get("artifacts"):
        raise HTTPException(404,"experiment artifact not found")
    allowed=(REPORTS/"tournament").resolve()
    artifacts=item["artifacts"]
    if artifacts.get("storage")=="remote":
        path=(REPORTS/"tournament"/"distributed"/"cache"/str(experiment_id)/"equity.parquet").resolve()
        if not path.is_file():
            try: RemoteComputeBridge(registry=database).fetch_artifact(artifacts["remote_directory"],"equity.parquet",path)
            except (OSError,ValueError,subprocess.SubprocessError): raise HTTPException(503,"remote equity artifact unavailable")
    else:
        path=Path(artifacts.get("equity","")).resolve()
    if allowed not in path.parents or not path.is_file():
        raise HTTPException(404,"equity artifact not found")
    series=pd.read_parquet(path).iloc[:,0]
    if len(series)>3000: series=series.iloc[::max(1,len(series)//3000)]
    drawdown=series/series.cummax()-1
    figure=go.Figure()
    figure.add_trace(go.Scatter(x=series.index,y=series.values,name="Equity"))
    figure.add_trace(go.Scatter(x=drawdown.index,y=drawdown.values,name="Drawdown",yaxis="y2"))
    figure.update_layout(template="plotly_dark",title=f"Experiment #{experiment_id}",hovermode="x unified",
                         yaxis2={"overlaying":"y","side":"right","tickformat":".1%"})
    return json.loads(figure.to_json())


@app.get("/api/tournament/portfolio/equity")
def portfolio_equity(_: str = Depends(authenticate)):
    report=portfolio_status()
    if not report or not Path(report.get("equity","")).is_file(): raise HTTPException(404,"portfolio not available")
    path=Path(report["equity"]); stamp=path.stat().st_mtime_ns
    if _portfolio_chart_cache.get("stamp")==stamp: return _portfolio_chart_cache["figure"]
    series=pd.read_parquet(path).iloc[:,0]
    if len(series)>3000: series=series.iloc[::max(1,len(series)//3000)]
    figure=go.Figure(go.Scatter(x=series.index,y=series.values,name="Portfolio equity"))
    figure.update_layout(template="plotly_dark",title="Validation ensemble",hovermode="x unified")
    result=json.loads(figure.to_json()); _portfolio_chart_cache.update(stamp=stamp,figure=result); return result


@app.get("/api/runs/{run_id}")
def run_detail(run_id: str, _: str = Depends(authenticate)):
    if not run_id.replace("-", "").isalnum():
        raise HTTPException(400, "invalid run id")
    manifest = read_json(REPORTS / "automation" / run_id / "manifest.json")
    if manifest is None:
        raise HTTPException(404, "run not found")
    return manifest


@app.get("/api/equity/{strategy}")
def equity(strategy: str, run_id: str | None = None, _: str = Depends(authenticate)):
    if not strategy.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(400, "invalid strategy")
    if run_id is None:
        manifest = latest_manifest()
        if not manifest:
            raise HTTPException(404, "no research run")
        run_id = manifest["run_id"]
    path = REPORTS / "automation" / run_id / "research" / f"{strategy}_equity.parquet"
    if not path.exists():
        raise HTTPException(404, "equity artifact not found")
    series = pd.read_parquet(path).iloc[:, 0]
    if len(series) > 3000:
        series = series.iloc[::max(1, len(series) // 3000)]
    drawdown = series / series.cummax() - 1
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=series.index, y=series.values, name="Equity"))
    figure.add_trace(go.Scatter(x=drawdown.index, y=drawdown.values, name="Drawdown", yaxis="y2"))
    figure.update_layout(template="plotly_dark", yaxis2={"overlaying": "y", "side": "right", "tickformat": ".1%"})
    return json.loads(figure.to_json())


@app.get("/api/export/{run_id}/{artifact:path}")
def export(run_id: str, artifact: str, _: str = Depends(authenticate)):
    base = (REPORTS / "automation" / run_id).resolve()
    target = (base / artifact).resolve()
    if base not in target.parents or not target.is_file():
        raise HTTPException(404, "artifact not found")
    return FileResponse(target, filename=target.name)


@app.get("/", response_class=HTMLResponse)
def home(_: str = Depends(authenticate)):
    return HTMLResponse(DASHBOARD_HTML)


DASHBOARD_HTML = """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>
<title>XAUUSD Tournament</title><script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script><style>
body{margin:0;background:#09101f;color:#e8edf7;font:14px system-ui}.wrap{max-width:1400px;margin:auto;padding:22px}.top{display:flex;justify-content:space-between;align-items:center}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.card,.panel{background:#151d32;padding:16px;border-radius:10px}.card b{font-size:20px}.muted,small{color:#9ca9c3}
.progress{height:8px;background:#293550;border-radius:5px;margin-top:8px}.progress i{display:block;height:100%;background:#3b82f6;border-radius:5px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}.panel{overflow:auto}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px;border-bottom:1px solid #2b3653;white-space:nowrap}
tr{cursor:pointer}tr:hover{background:#202b47}.pass{color:#58d68d}.fail{color:#ff6b6b}.running{color:#60a5fa}button,select{background:#253454;color:white;border:1px solid #3b4c70;padding:7px 10px;border-radius:6px}#tchart,#scatter{height:390px}.cores{display:grid;grid-template-columns:repeat(8,1fr);gap:6px}.core{background:#202b47;padding:6px;border-radius:5px;text-align:center}.computeCharts{display:grid;grid-template-columns:1fr 1fr;gap:12px}.computeChart{height:260px}
@media(max-width:900px){.grid{grid-template-columns:1fr}.wrap{padding:12px}}
</style></head><body><div class='wrap'><div class=top><div><h1>Strategy Tournament</h1><p class=muted>Frozen XAUUSD M1 research · live competition · no order execution</p></div><div><span id=updated></span></div></div>
<div class=cards id=cards></div><div class=grid><section class=panel><h2>Selected experiment</h2><div id=detail class=muted>Select an experiment from the tables below to inspect parameters, gates and event history.</div><div id=tchart></div></section><section class=panel><h2>Risk / return field</h2><div id=scatter></div></section></div><section class=panel style='margin-top:16px'><h2>Regime &amp; portfolio competition</h2><div id=portfolioSummary class=muted>Waiting for sufficient diverse results.</div><div id=portfolioChart style='height:380px'></div><table><thead><tr><th>Experiment</th><th>Family</th><th>Best regime</th><th>Regime P&amp;L</th></tr></thead><tbody id=regimes></tbody></table></section><section class=panel style='margin-top:16px'><h2>Server resources</h2><div class=cards id=systemCards></div><table><thead><tr><th>Service</th><th>PID</th><th>CPU</th><th>Memory</th><th>Threads</th><th>Uptime</th></tr></thead><tbody id=processes></tbody></table></section><section class=panel style='margin-top:16px'><h2>Operations &amp; recovery</h2><div id=ops></div><pre id=logs style='max-height:260px;overflow:auto;color:#9ca9c3;white-space:pre-wrap'></pre></section><section class=panel style='margin-top:16px'><h2>Weekly research report</h2><div id=weekly class=muted>Waiting for first report.</div></section><div class=grid><section class=panel><h2>Live experiments</h2><label>Status <select id=filter onchange=loadExperiments()><option value=''>All</option><option>running</option><option>completed</option><option>failed</option><option>queued</option></select></label><table><thead><tr><th>ID</th><th>Family</th><th>Status</th><th>Score</th><th>Validation P&amp;L</th><th>PF</th><th>Drawdown</th></tr></thead><tbody id=experiments></tbody></table></section><section class=panel><h2>Best challengers</h2><table><thead><tr><th>Rank</th><th>ID</th><th>Family</th><th>Score</th><th>Gate</th></tr></thead><tbody id=leaders></tbody><tfoot><tr><td colspan=5 id=championHistory class=muted></td></tr></tfoot></table></section></div>
<section class=panel style='margin-top:16px'><h2>Mainland compute server <span id=computeHealth></span></h2><div class=cards id=computeCards></div><h3>16-core activity</h3><div class=cores id=remoteCores></div><div class=computeCharts><div id=throughputChart class=computeChart></div><div id=queueChart class=computeChart></div></div><table><thead><tr><th>Worker</th><th>Experiment</th><th>Family</th><th>Stage</th><th>Elapsed</th></tr></thead><tbody id=remoteWorkers></tbody></table></section>
<script>
const n=(v,d=2)=>v==null?'—':Number(v).toFixed(d), esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function json(url){const r=await fetch(url);if(!r.ok)throw Error(await r.text());return r.json()}
let state={},followLogs=true,portfolioLoaded=false;logs.addEventListener('scroll',()=>{followLogs=logs.scrollHeight-logs.scrollTop-logs.clientHeight<24});async function load(){state=await json('/api/status');render(state,true)}
async function render(s,changed=false){const c=s.experiments.by_status,done=(c.completed??0)+(c.failed??0),pct=s.experiments.catalog_size?100*done/s.experiments.catalog_size:0;
const nextAdaptive=s.adaptive?Number(s.adaptive.last_completed_trigger??0)+250:100,d=s.distributed??{};
cards.innerHTML=`<div class=card>Compute bridge<br><b class=${d.state==='running'?'pass':'running'}>${esc(d.state)}</b><br><small>${d.active??0} / ${d.workers??0} remote workers · ${n(d.throughput_per_hour,1)}/hour</small></div><div class=card>Running now<br><b class=running>${c.running??0}</b><br><small>Remote queue ${(d.queue??c.queued??0).toLocaleString()}</small></div><div class=card>Tested<br><b>${done.toLocaleString()} / ${s.experiments.catalog_size.toLocaleString()}</b><div class=progress><i style='width:${Math.min(100,pct)}%'></i></div><small>${n(pct,1)}% fixed catalog</small></div><div class=card>Remote session<br><b>${d.completed_session??0} done</b><br><small>${d.failed_session??0} failed · host ${esc(d.host??'waiting')}</small></div><div class=card>Adaptive generation<br><b>#${s.adaptive?.generation??0} · ${s.adaptive?.created??0} new</b><br><small>${s.adaptive?esc(s.adaptive.parents+' parents · next at '+nextAdaptive+' completed'):'waiting for 100 results'}</small></div><div class=card>Novel proposals<br><b>${s.proposals?.created??0}</b><br><small>${esc(s.proposals?.generator_version??'waiting for catalog exhaustion')}</small></div><div class=card>Codex lab<br><b>${esc(s.codex.status)}</b><br><small>Auto-merge: ${s.codex.auto_merge?'ON':'OFF'}</small></div><div class=card>Champion<br><b>${esc(s.champion?.strategy??'none yet')}</b><br><small>Score ${n(s.champion?.score)}</small></div><div class=card>Promotions<br><b>${s.experiments.promoted}</b><br><small>Robust gates only</small></div>`;
const sys=s.system,bps=v=>v<1024?v+' B/s':v<1048576?n(v/1024,1)+' KB/s':n(v/1048576,1)+' MB/s',duration=v=>v<3600?n(v/60,0)+'m':v<86400?n(v/3600,1)+'h':n(v/86400,1)+'d';
const rt=d.telemetry??{},connected=rt.connected===true,age=rt.contact_at?(Date.now()-Date.parse(rt.contact_at))/1000:999,health=connected&&age<30&&d.failed_session===0?'CONNECTED':connected&&age<60?'DEGRADED':'DISCONNECTED';computeHealth.innerHTML=`<b class=${health==='CONNECTED'?'pass':health==='DEGRADED'?'running':'fail'}>${health}</b>`;
const gb=v=>n((v??0)/1073741824,1),eta=d.eta_seconds?duration(d.eta_seconds):'calculating';computeCards.innerHTML=`<div class=card>Processing speed<br><b>${n(d.throughput_per_hour,1)}/hour</b><br><small>Median ${n(d.duration?.median_seconds,1)}s · P95 ${n(d.duration?.p95_seconds,1)}s</small></div><div class=card>Queue ETA<br><b>${eta}</b><br><small>${d.queue??0} waiting · ${d.active??0}/${d.workers??0} active</small></div><div class=card>Remote CPU<br><b>${n(rt.cpu?.total_percent,1)}%</b><br><small>Load ${(rt.cpu?.load??[]).map(x=>n(x,1)).join(' / ')||'—'}</small></div><div class=card>Remote memory<br><b>${n(rt.memory?.percent,1)}%</b><br><small>${gb(rt.memory?.used)} / ${gb(rt.memory?.total)} GB</small></div><div class=card>Remote disk<br><b>${n(rt.disk?.percent,1)}%</b><br><small>${gb(rt.disk?.free)} GB free</small></div><div class=card>SOCKS tunnel<br><b class=${rt.tunnel?.active?'pass':'fail'}>${rt.tunnel?.active?'ACTIVE':'DOWN'}</b><br><small>SSH ${n(rt.ssh_latency_ms,0)}ms · contact ${n(age,0)}s ago</small></div><div class=card>Remote network<br><b>↓ ${bps(rt.network?.rx_bytes_per_second??0)}</b><br><small>↑ ${bps(rt.network?.tx_bytes_per_second??0)}</small></div>`;
remoteCores.innerHTML=(rt.cpu?.per_core??[]).map((x,i)=>`<div class=core>C${i+1}<br><b class=${x>90?'fail':x>65?'running':'pass'}>${n(x,0)}%</b><div class=progress><i style='width:${x}%'></i></div></div>`).join('');remoteWorkers.innerHTML=(d.worker_details??[]).sort((a,b)=>Number(a.worker)-Number(b.worker)).map(x=>`<tr onclick=inspect(${x.experiment_id})><td>${esc(x.worker)}</td><td>#${x.experiment_id}</td><td>${esc(x.family)}</td><td class=running>${esc(x.stage)}</td><td>${duration(x.elapsed_seconds)}</td></tr>`).join('');
const hist=d.history??[],hx=hist.map(x=>x.time);Plotly.react('throughputChart',[{x:hx,y:hist.map(x=>x.throughput_per_hour),mode:'lines',name:'Experiments/hour',line:{color:'#58d68d'}}],{template:'plotly_dark',margin:{t:35,l:45,r:15,b:35},title:'Processing speed',uirevision:'compute'});Plotly.react('queueChart',[{x:hx,y:hist.map(x=>x.queue),mode:'lines',name:'Queue',line:{color:'#60a5fa'}},{x:hx,y:hist.map(x=>x.cpu_percent),mode:'lines',name:'CPU %',yaxis:'y2',line:{color:'#f59e0b'}}],{template:'plotly_dark',margin:{t:35,l:45,r:45,b:35},title:'Queue burn-down / CPU',yaxis2:{overlaying:'y',side:'right',range:[0,100]},uirevision:'compute'});
systemCards.innerHTML=`<div class=card>CPU load<br><b>${n(sys.cpu.load_percent,1)}%</b><div class=progress><i style='width:${Math.min(100,sys.cpu.load_percent)}%'></i></div><small>${sys.cpu.cores} cores · ${n(sys.cpu.load_1m)} / ${n(sys.cpu.load_5m)} / ${n(sys.cpu.load_15m)}</small></div><div class=card>Memory<br><b>${n(sys.memory.percent,1)}%</b><div class=progress><i style='width:${sys.memory.percent}%'></i></div><small>${n(sys.memory.used.gb)} / ${n(sys.memory.total.gb)} GB</small></div><div class=card>Disk usage<br><b>${n(sys.disk.percent,1)}%</b><div class=progress><i style='width:${sys.disk.percent}%'></i></div><small>${n(sys.disk.used.gb)} / ${n(sys.disk.total.gb)} GB · ${n(sys.disk.free.gb)} GB free</small></div><div class=card>Network live<br><b>↓ ${bps(sys.network.rx_bytes_per_second)}</b><br><small>↑ ${bps(sys.network.tx_bytes_per_second)} · total ↓ ${n(sys.network.rx.gb)} GB ↑ ${n(sys.network.tx.gb)} GB</small></div>`;
processes.innerHTML=sys.services.map(x=>`<tr><td>${esc(x.service)}</td><td>${x.pid??'—'}</td><td>${x.running?n(x.cpu_percent)+'%':'stopped'}</td><td>${x.memory?n(x.memory.gb)+' GB':'—'}</td><td>${x.threads??'—'}</td><td>${x.uptime_seconds?duration(x.uptime_seconds):'—'}</td></tr>`).join('');
const o=s.operations;ops.innerHTML=`<b class=${o.healthy?'pass':'fail'}>${o.healthy?'HEALTHY':'ATTENTION'}</b> · DB integrity: ${esc(o.database.integrity)} · disk free ${n(o.disk_free_percent)}% · backup ${o.backup_age_hours==null?'missing':n(o.backup_age_hours,1)+'h ago'}${o.alerts.length?'<br><span class=fail>'+o.alerts.map(esc).join(' · ')+'</span>':''}`;if(s.logs){logs.textContent=s.logs.join('\\n');if(followLogs)logs.scrollTop=logs.scrollHeight}
const w=s.weekly;if(w){weekly.innerHTML=`<b>Last 7 days</b> · ${w.completed_this_week} completed · ${n(100*w.positive_validation_fraction,1)}% positive validation · throughput Δ ${w.throughput_change} · best score ${n(w.current_best_score)} · all-time ${w.all_time_completed.toLocaleString()}<br><small>Multiple-testing context: ${n(100*w.multiple_testing.familywise_false_positive_probability,1)}% nominal familywise false-positive probability across ${w.multiple_testing.experiments.toLocaleString()} trials. Robust gates remain mandatory.</small>`}
const p=s.portfolio;if(p){portfolioSummary.innerHTML=`<b class=${p.passed?'pass':'fail'}>${p.passed?'PASS':'FAIL'}</b> · ${p.experiment_ids.length} diverse strategies · P&amp;L ${n(p.metrics.net_profit)} · Sharpe ${n(p.metrics.sharpe)} · Drawdown ${n(100*p.metrics.max_drawdown)}% · exposure ${n(100*p.average_exposure)}%`;regimes.innerHTML=p.strategies.map(x=>{const best=[...x.regimes].sort((a,b)=>b.net_profit-a.net_profit)[0];return `<tr onclick=inspect(${x.experiment_id})><td>#${x.experiment_id}</td><td>${esc(x.family)}</td><td>${esc(best?.regime??'—')}</td><td>${n(best?.net_profit)}</td></tr>`}).join('');if(!portfolioLoaded){portfolioLoaded=true;json('/api/tournament/portfolio/equity').then(f=>Plotly.react('portfolioChart',f.data,f.layout))}}
updated.textContent='LIVE · '+new Date().toLocaleTimeString();if(changed)await Promise.all([loadExperiments(),loadLeaders()])}
async function loadExperiments(){const status=filter.value,rows=await json('/api/experiments?limit=100'+(status?'&status='+status:''));experiments.innerHTML=rows.map(x=>{const m=x.metrics?.validation,v=x.validation;return `<tr onclick=inspect(${x.id})><td>#${x.id}</td><td>${esc(x.strategy_family)}</td><td class=${x.status}>${x.status}</td><td>${n(v?.score)}</td><td>${n(m?.net_profit)}</td><td>${n(m?.profit_factor)}</td><td>${m? n(100*m.max_drawdown,2)+'%':'—'}</td></tr>`}).join('')}
async function loadLeaders(){const [rows,hist]=await Promise.all([json('/api/tournament/leaderboard?limit=30'),json('/api/tournament/champions?limit=10')]);leaders.innerHTML=rows.map((x,i)=>`<tr onclick=inspect(${x.id})><td>${i+1}</td><td>#${x.id}</td><td>${esc(x.strategy_family)}</td><td>${n(x.validation?.score)}</td><td class=${x.validation?.passed?'pass':'fail'}>${x.validation?.passed?'PASS':'FAIL'}</td></tr>`).join('');championHistory.textContent=hist.length?'Champion history: '+hist.map(x=>'#'+x.experiment_id+' ('+n(x.holdout_score)+')').join(' → '):'No holdout-qualified champion yet';const pts=rows.filter(x=>x.metrics?.validation);Plotly.react('scatter',[{x:pts.map(x=>100*x.metrics.validation.max_drawdown),y:pts.map(x=>x.metrics.validation.net_profit),text:pts.map(x=>'#'+x.id+' '+x.strategy_family),mode:'markers',marker:{color:pts.map(x=>x.validation.score),colorscale:'Viridis',showscale:true}}],{template:'plotly_dark',margin:{t:20},xaxis:{title:'Max drawdown %'},yaxis:{title:'Validation net P&L'},hovermode:'closest'})}
async function inspect(id){const x=await json('/api/experiments/'+id),g=x.validation?.gates??{},wf=x.validation?.walk_forward,bs=x.validation?.bootstrap,fin=x.validation?.finalist;detail.innerHTML=`<h3>#${x.id} ${esc(x.strategy_family)} <span class=${x.status}>${x.status}</span></h3><p><b>Parameters</b><br><code>${esc(JSON.stringify(x.parameters))}</code></p><p><b>Gates</b><br>${Object.entries(g).map(([k,v])=>`<span class=${v?'pass':'fail'}>${v?'✓':'✗'} ${esc(k)}</span>`).join(' · ')||'Pending'}</p><p><b>Robustness</b><br>Positive walk-forward folds: ${wf?n(100*wf.positive_fold_fraction,0)+'%':'not reached'} · Bootstrap loss probability: ${bs?n(100*bs.loss_probability,1)+'%':'not reached'} · Bootstrap P05 P&amp;L: ${bs?n(bs.p05_net_pnl):'—'}</p><p><b>Finalist holdout</b><br>${fin?.eligible?'Evaluated · '+(fin.passed?'PASS':'FAIL')+' · score '+n(fin.score):esc(fin?.reason??'not eligible')}</p><p><b>Timeline</b><br>${x.events.map(e=>esc(e.occurred_at.slice(11,19))+' '+esc(e.event)).join(' → ')}</p>`;if(x.artifacts?.equity){const f=await json('/api/tournament/equity/'+id);Plotly.react('tchart',f.data,f.layout)}else Plotly.purge('tchart')}
load().then(()=>{const stream=new EventSource('/api/live');stream.addEventListener('snapshot',event=>{const incoming=JSON.parse(event.data);state={...state,...incoming};render(state,incoming.experiment_changed)});stream.onerror=()=>{updated.textContent='Reconnecting live stream…'}});
</script></div></body></html>"""
