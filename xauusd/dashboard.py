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
<title>XAUUSD Research</title><script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script><style>
body{margin:0;background:#0b1020;color:#e8edf7;font:14px system-ui}.wrap{max-width:1200px;margin:auto;padding:24px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}.card{background:#151d32;padding:16px;border-radius:10px}
table{width:100%;border-collapse:collapse;margin-top:20px;background:#151d32}th,td{text-align:left;padding:10px;border-bottom:1px solid #2b3653}
.pass{color:#58d68d}.fail{color:#ff6b6b}button{background:#315efb;color:white;border:0;padding:6px 10px;border-radius:5px;cursor:pointer}#chart,#history{height:430px}
</style></head><body><div class='wrap'><h1>XAUUSD Research Operations</h1><p>Research-only · no execution connectivity</p>
<div class='cards' id='cards'></div><table><thead><tr><th>Strategy</th><th>Net P&amp;L</th><th>PF</th><th>Drawdown</th><th>Gate</th><th></th></tr></thead><tbody id='rows'></tbody></table><div id='chart'></div><div id='history'></div>
<script>async function load(){const s=await fetch('/api/status').then(r=>r.json()),l=await fetch('/api/leaderboard').then(r=>r.json());
cards.innerHTML=`<div class=card>Tournament<br><b>${s.tournament?.version??'not frozen'}</b><br><small>${s.tournament?.rows?.toLocaleString()??'-'} bars</small></div><div class=card>Experiments<br><b>${s.experiments.total.toLocaleString()} / ${s.experiments.catalog_size.toLocaleString()}</b><br><small>${s.experiments.by_status.queued??0} queued · ${s.experiments.by_status.completed??0} completed</small></div><div class=card>Live data<br><b>${s.data.available?s.data.rows.toLocaleString():'missing'} bars</b></div><div class=card>Freshness<br><b>${s.data.age_hours?.toFixed(1)??'-'} hours</b></div><div class=card>Latest run<br><b>${s.latest_run??'none'}</b></div><div class=card>Champion<br><b>${s.champion?.strategy??'none'}</b></div><div class=card>Automation<br><b>${s.scheduler.status??'unknown'}</b><br><small>Next: ${s.scheduler.next_run??'-'}</small></div>`;
rows.innerHTML=l.map(x=>`<tr><td>${x.strategy}</td><td>${x.net_profit.toFixed(2)}</td><td>${x.profit_factor.toFixed(3)}</td><td>${(x.max_drawdown*100).toFixed(2)}%</td><td class=${x.passed?'pass':'fail'}>${x.passed?'PASS':'FAIL'}</td><td><button onclick="chart('${x.strategy}')">Chart</button></td></tr>`).join('');if(l.length)chart(l[0].strategy)}
async function chart(name){const f=await fetch('/api/equity/'+name).then(r=>r.json());Plotly.react('chart',f.data,f.layout)}
async function history(){const f=await fetch('/api/history/chart').then(r=>r.json());Plotly.react('history',f.data,f.layout)}load();history()</script></div></body></html>"""
