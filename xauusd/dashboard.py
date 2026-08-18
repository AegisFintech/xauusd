from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import os
import secrets
import time

import pandas as pd
import plotly.graph_objects as go
from .experiment_registry import ExperimentRegistry
from .search_space import catalog_size
from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials


REPORTS = Path(os.getenv("XAUUSD_REPORTS_DIR", "reports")).resolve()
DATA_FILE = Path(os.getenv("XAUUSD_DATA_FILE", "data/processed/XAUUSD_M1.parquet")).resolve()
security = HTTPBasic(auto_error=False)
app = FastAPI(title="XAUUSD Research Dashboard", version="0.7.0")
log = logging.getLogger("xauusd.dashboard")


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


def registry() -> ExperimentRegistry | None:
    path=Path(os.getenv("XAUUSD_EXPERIMENT_DB", "data/experiments/registry.sqlite3"))
    return ExperimentRegistry(path,initialize=False) if path.exists() else None


@app.get("/health")
def health():
    return {"status": "ok", "mode": "research-only"}


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
            "tournament": tournament_status(), "experiments": {**(registry().summary() if registry() else
            {"total":0,"by_status":{},"strategy_families":0,"promoted":0}),"catalog_size":catalog_size()}}


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
    path=Path(item["artifacts"]["equity"]).resolve()
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
tr{cursor:pointer}tr:hover{background:#202b47}.pass{color:#58d68d}.fail{color:#ff6b6b}.running{color:#60a5fa}button,select{background:#253454;color:white;border:1px solid #3b4c70;padding:7px 10px;border-radius:6px}#tchart,#scatter{height:390px}
@media(max-width:900px){.grid{grid-template-columns:1fr}.wrap{padding:12px}}
</style></head><body><div class='wrap'><div class=top><div><h1>Strategy Tournament</h1><p class=muted>Frozen XAUUSD M1 research · live competition · no order execution</p></div><div><span id=updated></span> <button onclick=load()>Refresh</button></div></div>
<div class=cards id=cards></div><div class=grid><section class=panel><h2>Live experiments</h2><label>Status <select id=filter onchange=loadExperiments()><option value=''>All</option><option>running</option><option>completed</option><option>failed</option><option>queued</option></select></label><table><thead><tr><th>ID</th><th>Family</th><th>Status</th><th>Score</th><th>Validation P&amp;L</th><th>PF</th><th>Drawdown</th></tr></thead><tbody id=experiments></tbody></table></section>
<section class=panel><h2>Best challengers</h2><table><thead><tr><th>Rank</th><th>ID</th><th>Family</th><th>Score</th><th>Gate</th></tr></thead><tbody id=leaders></tbody><tfoot><tr><td colspan=5 id=championHistory class=muted></td></tr></tfoot></table></section></div>
<div class=grid><section class=panel><h2>Selected experiment</h2><div id=detail class=muted>Select an experiment row to inspect parameters, gates and event history.</div><div id=tchart></div></section><section class=panel><h2>Risk / return field</h2><div id=scatter></div></section></div>
<script>
const n=(v,d=2)=>v==null?'—':Number(v).toFixed(d), esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function json(url){const r=await fetch(url);if(!r.ok)throw Error(await r.text());return r.json()}
async function load(){const s=await json('/api/status'),c=s.experiments.by_status,done=(c.completed??0)+(c.failed??0),pct=s.experiments.catalog_size?100*done/s.experiments.catalog_size:0;
cards.innerHTML=`<div class=card>Worker<br><b class=${s.tournament_worker.healthy?'pass':'fail'}>${esc(s.tournament_worker.state)}</b><br><small>${n(s.tournament_worker.heartbeat_age_seconds,0)}s heartbeat</small></div><div class=card>Running now<br><b class=running>${c.running??0}</b><br><small>Last #${s.tournament_worker.last_experiment_id??'—'}</small></div><div class=card>Tested<br><b>${done.toLocaleString()} / ${s.experiments.catalog_size.toLocaleString()}</b><div class=progress><i style='width:${Math.min(100,pct)}%'></i></div><small>${n(pct,1)}% fixed catalog</small></div><div class=card>Queue<br><b>${(c.queued??0).toLocaleString()}</b><br><small>${s.tournament_worker.catalog?.remaining_unregistered?.toLocaleString()??'auto'} unregistered</small></div><div class=card>Adaptive search<br><b>${s.adaptive?.created??0}</b><br><small>${esc(s.adaptive?s.adaptive.parents+' diverse parents':'waiting for 100 results')}</small></div><div class=card>Novel proposals<br><b>${s.proposals?.created??0}</b><br><small>${esc(s.proposals?.generator_version??'waiting for catalog exhaustion')}</small></div><div class=card>Codex lab<br><b>${esc(s.codex.status)}</b><br><small>Auto-merge: ${s.codex.auto_merge?'ON':'OFF'}</small></div><div class=card>Champion<br><b>${esc(s.champion?.strategy??'none yet')}</b><br><small>Score ${n(s.champion?.score)}</small></div><div class=card>Promotions<br><b>${s.experiments.promoted}</b><br><small>Robust gates only</small></div>`;
updated.textContent='Updated '+new Date().toLocaleTimeString();await Promise.all([loadExperiments(),loadLeaders()])}
async function loadExperiments(){const status=filter.value,rows=await json('/api/experiments?limit=100'+(status?'&status='+status:''));experiments.innerHTML=rows.map(x=>{const m=x.metrics?.validation,v=x.validation;return `<tr onclick=inspect(${x.id})><td>#${x.id}</td><td>${esc(x.strategy_family)}</td><td class=${x.status}>${x.status}</td><td>${n(v?.score)}</td><td>${n(m?.net_profit)}</td><td>${n(m?.profit_factor)}</td><td>${m? n(100*m.max_drawdown,2)+'%':'—'}</td></tr>`}).join('')}
async function loadLeaders(){const [rows,hist]=await Promise.all([json('/api/tournament/leaderboard?limit=30'),json('/api/tournament/champions?limit=10')]);leaders.innerHTML=rows.map((x,i)=>`<tr onclick=inspect(${x.id})><td>${i+1}</td><td>#${x.id}</td><td>${esc(x.strategy_family)}</td><td>${n(x.validation?.score)}</td><td class=${x.validation?.passed?'pass':'fail'}>${x.validation?.passed?'PASS':'FAIL'}</td></tr>`).join('');championHistory.textContent=hist.length?'Champion history: '+hist.map(x=>'#'+x.experiment_id+' ('+n(x.holdout_score)+')').join(' → '):'No holdout-qualified champion yet';const pts=rows.filter(x=>x.metrics?.validation);Plotly.react('scatter',[{x:pts.map(x=>100*x.metrics.validation.max_drawdown),y:pts.map(x=>x.metrics.validation.net_profit),text:pts.map(x=>'#'+x.id+' '+x.strategy_family),mode:'markers',marker:{color:pts.map(x=>x.validation.score),colorscale:'Viridis',showscale:true}}],{template:'plotly_dark',margin:{t:20},xaxis:{title:'Max drawdown %'},yaxis:{title:'Validation net P&L'},hovermode:'closest'})}
async function inspect(id){const x=await json('/api/experiments/'+id),g=x.validation?.gates??{},wf=x.validation?.walk_forward,bs=x.validation?.bootstrap,fin=x.validation?.finalist;detail.innerHTML=`<h3>#${x.id} ${esc(x.strategy_family)} <span class=${x.status}>${x.status}</span></h3><p><b>Parameters</b><br><code>${esc(JSON.stringify(x.parameters))}</code></p><p><b>Gates</b><br>${Object.entries(g).map(([k,v])=>`<span class=${v?'pass':'fail'}>${v?'✓':'✗'} ${esc(k)}</span>`).join(' · ')||'Pending'}</p><p><b>Robustness</b><br>Positive walk-forward folds: ${wf?n(100*wf.positive_fold_fraction,0)+'%':'not reached'} · Bootstrap loss probability: ${bs?n(100*bs.loss_probability,1)+'%':'not reached'} · Bootstrap P05 P&amp;L: ${bs?n(bs.p05_net_pnl):'—'}</p><p><b>Finalist holdout</b><br>${fin?.eligible?'Evaluated · '+(fin.passed?'PASS':'FAIL')+' · score '+n(fin.score):esc(fin?.reason??'not eligible')}</p><p><b>Timeline</b><br>${x.events.map(e=>esc(e.occurred_at.slice(11,19))+' '+esc(e.event)).join(' → ')}</p>`;if(x.artifacts?.equity){const f=await json('/api/tournament/equity/'+id);Plotly.react('tchart',f.data,f.layout)}else Plotly.purge('tchart')}
load();setInterval(load,15000);
</script></div></body></html>"""
