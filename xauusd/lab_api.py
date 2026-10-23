"""Read-only dashboard projections, bounded by rows and bytes."""
from datetime import datetime, timezone
from dataclasses import asdict
from pathlib import Path
import shutil
import threading
import time

import pandas as pd

from .lab_store import LabStore

_cache = {}
_lock = threading.Lock()


def _data():
    from .data import HistoricalDataStore
    store = HistoricalDataStore()
    stat = store.path.stat()
    key = (str(store.path.resolve()), stat.st_mtime_ns, stat.st_size)
    with _lock:
        if _cache.get("key") != key:
            _cache.update(key=key, bars=store.read())
        return _cache["bars"]


def retained_statistics(store) -> dict:
    """Counts only bounded retained evidence; never infer remote execution success."""
    from collections import Counter
    def rows(key):
        return store.meta(key) or []
    def states(items, field='state'):
        return dict(Counter(row.get(field, 'unknown') for row in items))
    calls = rows('agent_calls')
    remote = [row for row in calls if row.get('name') == 'tc02_run']
    return {
        'scope': 'retained_records',
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'research': {'total': len(rows('research_outcomes')),
                     'verdicts': states(rows('research_outcomes'), 'verdict')},
        'sessions': {'total': len(store.jobs()), 'states': states(store.jobs())},
        'qualification': {'total': len(store.candidates()), 'states': states(store.candidates())},
        'experiments': {'current': len(rows('experiments')), 'retired': len(rows('experiment_archive'))},
        'improvements': {'total': len(rows('improvements')), 'states': states(rows('improvements'))},
        'tools': dict(Counter(row.get('name', 'unknown') for row in calls)),
        'tc02': {'requests': len(remote), 'states': states(remote),
                 'successful_results': sum(row.get('state') == 'completed' and
                     isinstance(row.get('result'), dict) and row['result'].get('ok') is True for row in remote),
                 'inspections': sum(row.get('name') == 'tc02_inspect' for row in calls),
                 'cpu_hours': None, 'utilization_pct': None, 'lifetime_backtests': None},
    }


def snapshot(transcript, paper) -> dict:
    from .agent_daily import utc_day
    daily=utc_day()
    try:
        store = LabStore(transcript)
        status = store.meta("status") or {"state": "not_started", "phase": "awaiting_first_cycle", "provider": "codex"}
        candidates = store.candidates()
        active, jobs, equity, activity = store.active(), store.jobs(), store.equity(), store.events(0, 300)
        dataset = store.meta("dataset")
        attempts = store.meta("attempts") or 0
        memory = store.memory()
        storage = store.meta("storage") or {}
        agent = store.meta("agent") or {}
        engineering = store.meta("engineering") or {}
    except (AttributeError, TypeError):
        # The legacy in-memory transcript has no connection; it remains useful
        # for old view tests and does not imply a persistent lab exists.
        status = {"state": "not_started", "provider": "codex"}
        candidates, active, jobs, equity, activity, dataset, attempts, memory, storage = [], None, [], [], [], None, 0, {}, {}
        agent, engineering = {}, {}
    account = paper.summary()
    baseline = account.get("day_start_equity")
    daily_pnl=account.get("day_pl",0) if account.get("day")==daily['day'] else 0
    measured = (daily_pnl / baseline * 100) if isinstance(baseline, (int, float)) and baseline > 0 else None
    performance = {"daily_return_pct": measured,"day_pl":daily_pnl,"day":daily['day'],"timezone":"UTC",
                   "target_achieved": measured is not None and measured >= 100}
    def current_job(job):
        if job.get('state')=='running': return True
        if job.get('started_at','') < daily['started_at']: return False
        if not agent.get("session_id"):
            return False
        if job.get("session_id"):
            return job["session_id"] == agent["session_id"]
        return bool(agent.get("started_at") and job.get("started_at", "") >= agent["started_at"])
    current_jobs = [job for job in jobs if current_job(job)]
    archived_jobs = [job for job in jobs if not current_job(job)]
    try:
        bars = _data()
        now = datetime.now(timezone.utc)
        from .paper_trading import market_data_age_seconds, market_is_open, observation_is_future
        bar = bars.index[-1].to_pydatetime()
        age = market_data_age_seconds(bar, now)
        data = {"rows": len(bars), "start": bars.index[0].isoformat(), "end": bars.index[-1].isoformat(),
                "columns": list(bars.columns), "volume_type": "tick count", "market_open": market_is_open(now),
                "age_seconds": age, "fresh": not observation_is_future(bar, now) and age <= paper.config.max_market_data_age_seconds,
                "quality": "Closed M1 OHLCV plus bounded live bid/ask observations; historical tick paths unavailable",
                "needs": ["longer bid/ask observation history", "broker-measured slippage and commissions", "point-in-time economic releases"]}
        from .quotes import read_quote
        from .lab_execution import quote_valid
        quote = read_quote()
        data.update(quote=quote, quote_fresh=quote_valid(quote, now))
    except Exception:
        data = {"state": "unavailable", "fresh": False, "error_code": "market_data_unavailable"}
    usage = shutil.disk_usage(Path("."))
    storage = {"used_bytes": usage.used, "free_bytes": usage.free, "total_bytes": usage.total,
               "policy": storage.get("policy", {"events": 300, "jobs": 30, "equity_minutes": 10080,
                                                   "workspace_days": 7}),
               "deleted_bytes": storage.get("deleted_bytes", 0), "state": storage.get("state", "not_run")}
    retained_status = store.meta("storage") if 'store' in locals() and hasattr(transcript, "connect") else {}
    retained_status = retained_status or {}
    storage.update(errors=retained_status.get("errors", []),
                   bytes_reclaimable=retained_status.get("bytes_reclaimable", 0),
                   recorded_at=retained_status.get("recorded_at"))
    if status.get("heartbeat_at"):
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(status["heartbeat_at"])).total_seconds()
            status = dict(status, stale=age > 45, heartbeat_age_seconds=age)
        except (ValueError, TypeError):
            status = dict(status, stale=True)
    alerts = []
    if storage["errors"] or storage["state"] == "partial":
        alerts.append("Artifact retention needs attention; some generated files were retained.")
    if usage.free < max(2_000_000_000, usage.total * .05):
        alerts.append("Disk space is low; research storage needs attention.")
    if status.get("stale"):
        alerts.append("Codex harness heartbeat is stale.")
    if data.get("market_open") and not data.get("fresh"):
        alerts.append("Market bars are stale; trading is blocked.")
    if data.get("market_open") and not data.get("quote_fresh"):
        alerts.append("Fresh two-sided quotes unavailable; paper orders wait.")
    if jobs and jobs[0].get("state") in ("failed", "interrupted"):
        alerts.append("Latest research job needs attention: " + str(jobs[0].get("error_code", "job_failed")))
    if agent.get("phase")=="error":
        alerts.append("Autonomous research is failing: " + str(agent.get("last_error","research_cycle_failed")))
    if agent.get("stagnation_cycles",0)>=3:
        alerts.append("Research has no changed experimental evidence in three sessions; review the evolving plan.")
    if engineering.get("state") in ("recovery_required","installing"):
        alerts.append("Engineering release recovery needs attention.")
    return {"statistics": retained_statistics(store) if hasattr(transcript, "connect") else {}, "status": status, "alerts": alerts, "account": account, "active": active, "candidates": candidates[:40],
            "jobs": jobs[:30], "equity": [r for r in equity if r.get('time','')>=daily['started_at']][-2000:], "activity": activity[-100:], "data": data,
            "storage": storage, "dataset": dataset, "memory": memory,
            "experiments": (store.meta("experiments") or []) if hasattr(transcript,"connect") else [],
            "outcomes": (store.meta("research_outcomes") or []) if hasattr(transcript,"connect") else [],
            "improvements": (store.meta("improvements") or []) if hasattr(transcript,"connect") else [],
            "experiment_archive": (store.meta("experiment_archive") or []) if hasattr(transcript,"connect") else [],
            "codex_thread_id": store.meta("codex_thread_id") if hasattr(transcript,"connect") else None,
            "codex_usage": {k:v for k,v in (store.meta("codex_usage") or {}).items() if k not in ("cursor","file_inode")} if hasattr(transcript,"connect") else {},
            "agent": agent, "engineering": engineering, "performance": performance,"daily":daily,
            "current_jobs": current_jobs, "archived_jobs": archived_jobs,
            "limits": {"paper_only": True, "automatic_promotion": True, "research_attempts": attempts,
                       "maximum_attempts_per_frozen_dataset": 20, "minimum_forward_days": 7,
                       "minimum_forward_trades": 30, "return_target_is_aspirational": True,
                       "risk": asdict(paper.config)}}


def chart(timeframe="M1", limit=300):
    rules = {"M1": "1min", "M5": "5min", "M15": "15min", "H1": "1h", "H4": "4h", "D1": "1D"}
    if timeframe not in rules or type(limit) is not int or not 10 <= limit <= 1000:
        raise ValueError("invalid_chart_request")
    try:
        bars = _data()
        now = pd.Timestamp.now(tz="UTC")
        closed = bars.loc[:now - pd.Timedelta(minutes=1)]
        interval = pd.Timedelta(rules[timeframe])
        view = closed.resample(rules[timeframe]).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna()
        view = view.loc[view.index + interval <= now].tail(limit)
        return {"timeframe": timeframe, "bars": [{"time": t.isoformat(), **row} for t, row in view.to_dict("index").items()],
                "count": len(view), "source": "cTrader demo closed bars"}
    except Exception:
        return {"timeframe": timeframe, "bars": [], "error_code": "chart_unavailable"}


def events(transcript, after=0, limit=100):
    try:
        store = LabStore(transcript)
        rows = store.events(after, limit)
        latest = (store.meta("events") or {}).get("next_id", 1) - 1
    except (AttributeError, TypeError):
        rows, latest = [], 0
    return {"events": rows, "latest_id": latest}
