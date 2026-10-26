"""Codex research supervisor and independently paced, gated paper execution.

No broker adapter is constructed here. Automatic promotion deploys a verified
strategy program, never a model assertion and never a change to risk policy.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import math
from functools import lru_cache
from pathlib import Path
import threading
import time
from uuid import uuid4

import pandas as pd

from .atomic import atomic_write_bytes, atomic_write_json
from .lab_store import LabStore, timestamp, serialized
from .lab_strategy import (EMBARGO, MAX_ATTEMPTS, MIN_FORWARD_TRADES, assess, evidence_digest,
                           execution_config, freeze_dataset, gates_for, identity, partition,
                           signals, evaluate)
from .paper_trading import market_is_open, market_data_age_seconds, observation_is_future
from .lab_execution import quote_valid, target_decision, ShadowStore


def _open_minutes(start, end):
    """Observation opportunities under the shared New York market session."""
    return [t for t in pd.date_range(start, end, inclusive="left", freq="min")
            if market_is_open(t.to_pydatetime())]


@lru_cache(maxsize=128)
def _expected_forward_minutes(created_at, end):
    first = pd.Timestamp(created_at).floor("min") + pd.Timedelta(minutes=2)
    return tuple(_open_minutes(first, pd.Timestamp(end)))


def forward_coverage(created_at, end, shadow):
    # The first eligible bar opens after creation and closes one minute later.
    expected = _expected_forward_minutes(created_at, end)
    observed = {pd.Timestamp(mark["time"]).floor("min") for mark in shadow.get("equity", [])}
    covered = [i for i, minute in enumerate(expected) if minute in observed]
    fraction = len(covered) / len(expected) if expected else 0.
    first_ok = bool(covered) and covered[0] <= 2
    last_ok = bool(covered) and len(expected) - 1 - covered[-1] <= 2
    exposed_gap = shadow.get("exposed_observation_gap", False) is not False
    return {"expected_minutes": len(expected), "observed_minutes": len(covered),
            "fraction": fraction, "first_boundary_covered": first_ok,
            "last_boundary_covered": last_ok, "exposed_gap": exposed_gap,
            "first_observed_at": expected[covered[0]].isoformat() if covered else None,
            "last_observed_at": expected[covered[-1]].isoformat() if covered else None,
            "passed": fraction >= .99 and first_ok and last_ok and not exposed_gap}


def _qualified(row: dict) -> bool:
    """Recheck the facts instead of trusting a passed flag from any producer."""
    report, forward = row.get("report") or {}, row.get("forward") or {}
    for evidence in (report, forward):
        gates = evidence.get("gates") or {}
        required_gates = {"minimum_trades", "positive_expectancy", "net_profit", "profit_factor", "drawdown", "bootstrap_positive"}
        if evidence is report:
            required_gates.add("positive_folds")
        if not required_gates.issubset(gates):
            return False
        if evidence.get("passed") is not True or not gates or any(v is not True for v in gates.values()):
            return False
        metrics = evidence.get("metrics") or {}
        required = ("trades", "net_profit", "expectancy", "profit_factor", "max_drawdown")
        if any(type(metrics.get(k)) not in (int, float) or not math.isfinite(metrics[k]) for k in required):
            return False
        if metrics["net_profit"] <= 0 or metrics["expectancy"] <= 0 or metrics["profit_factor"] < 1.15 or metrics["max_drawdown"] < -.10:
            return False
        p05 = (evidence.get("bootstrap") or {}).get("p05_net_pnl")
        if type(p05) not in (int, float) or not math.isfinite(p05) or p05 <= 0:
            return False
    if report["metrics"]["trades"] < 100 or forward["metrics"]["trades"] < MIN_FORWARD_TRADES:
        return False
    if report.get("holdout_consumed") is not False or forward.get("prospective") is not True or forward.get("quote_based") is not True:
        return False
    coverage = forward.get("coverage") or {}
    expected, observed = coverage.get("expected_minutes"), coverage.get("observed_minutes")
    if (forward.get("gates", {}).get("observation_coverage") is not True or
            coverage.get("passed") is not True or type(expected) is not int or expected <= 0 or
            type(observed) is not int or not 0 <= observed <= expected or observed / expected < .99 or
            coverage.get("fraction") != observed / expected or
            coverage.get("first_boundary_covered") is not True or
            coverage.get("last_boundary_covered") is not True or coverage.get("exposed_gap") is not False):
        return False
    fraction = report.get("positive_fold_fraction")
    if type(fraction) not in (int, float) or not math.isfinite(fraction) or fraction < .75:
        return False
    if forward.get("days") != 7 or report.get("candidate_id") != row.get("id") or report.get("dataset_version") != row.get("dataset_version"):
        return False
    try:
        minutes = _expected_forward_minutes(row["created_at"], row["forward_end"])
        first_observed = pd.Timestamp(coverage["first_observed_at"])
        last_observed = pd.Timestamp(coverage["last_observed_at"])
        if (expected != len(minutes) or first_observed not in minutes[:3] or
                last_observed not in minutes[-3:] or
                pd.Timestamp(forward["start"]).floor("min") != first_observed):
            return False
        if forward["end"] != row["forward_end"] or pd.Timestamp(row["forward_end"]) - pd.Timestamp(row["created_at"]) != pd.Timedelta(days=7):
            return False
        if pd.Timestamp(forward["start"]) <= pd.Timestamp(row["created_at"]):
            return False
        if identity(row) != row["id"]:
            return False
        if report["execution"] != forward["execution"] or report["execution"] != row["execution"]:
            return False
        return row.get("evidence_digest") == evidence_digest(row)
    except (KeyError, TypeError, ValueError):
        return False


@serialized
def promote(store: LabStore, candidate: dict, paper) -> dict:
    # Only persisted, completed evaluator evidence is eligible.
    row = next((r for r in store.candidates() if r["id"] == candidate["id"]), None)
    if row is None or not _qualified(row):
        return {"promoted": False, "reason": "invalid_evidence"}
    state = paper.state()
    if state["stopped"] or abs(state["position"]) > 1e-9:
        return {"promoted": False, "reason": "paper_stopped_or_exposed"}
    # One transaction binds the active pointer to the exact verified candidate.
    with store.state.transaction() as tx:
        tx.lock("lab:candidates")
        rows = tx.get("lab:candidates", [])
        fresh = next((r for r in rows if r["id"] == row["id"]), None)
        if fresh is None or not _qualified(fresh):
            return {"promoted": False, "reason": "evidence_changed"}
        for entry in rows:
            if entry.get("state") == "active":
                entry["state"] = "retired"
        fresh.update(state="active", promoted_at=timestamp())
        tx.put("lab:candidates", rows)
        tx.put("lab:active", fresh["id"])
    store.event("promotion", "Validated strategy automatically deployed to paper trading.",
                {"candidate_id": row["id"], "name": row["name"], "evidence_digest": row["evidence_digest"]})
    return {"promoted": True, "candidate_id": row["id"]}


@serialized
def paper_tick(store: LabStore, paper, bars: pd.DataFrame, now: datetime, quantity: float = .1, quote=None) -> dict:
    state = paper.state()
    if state["stopped"]:
        return {"state": "paper_stopped"}
    row = store.active()
    if row is None:
        return {"state": "researching", "reason": "no_qualified_candidate"}
    if not _qualified(row) or row["execution"] != __import__('dataclasses').asdict(execution_config(quantity)):
        return {"state": "invalid_evidence"}
    if not market_is_open(now):
        return {"state": "market_closed"}
    if bars.empty:
        return {"state": "stale_data"}
    bar = bars.index[-1].to_pydatetime()
    if observation_is_future(bar, now) or market_data_age_seconds(bar, now) > paper.config.max_market_data_age_seconds:
        return {"state": "stale_data"}
    # Forming bars never enter deployed strategy calculations.
    closed = bars.loc[bars.index <= pd.Timestamp(now) - pd.Timedelta(minutes=1)]
    if closed.empty or closed.index[-1].to_pydatetime() != bar:
        return {"state": "forming_bar"}
    position = float(state["position"])
    if abs(position) > 1e-9 and store.meta("position_owner") != row["id"]:
        return {"state": "unowned_exposure"}
    # Freeze one intent per bar before reading mutable position again. A repeated
    # tick or restart cannot execute the second half of a reversal on this bar.
    bar_id = row["id"] + ":" + bar.isoformat()
    prior = store.meta("execution_intent")
    if prior and prior.get("bar_id") == bar_id:
        return {"state": "duplicate_bar"}
    if quote is None:
        from .quotes import read_quote
        quote = read_quote()
    if not quote_valid(quote, now):
        return {"state": "quote_unavailable"}
    decision = target_decision(row, closed, state, now, quote, quantity)
    if decision is None:
        return {"state": "holding" if position else "waiting"}
    side, delta, decision_id = decision.side, decision.quantity, decision.decision_id
    store.meta("execution_intent", {"bar_id": bar_id, "decision_id": decision_id,
                                     "side": side, "quantity": abs(delta), "recorded_at": now.isoformat()})
    store.meta("position_owner", row["id"])
    result = paper.evaluate(decision, now)
    filled = result.get("accepted") is True and result.get("replayed") is not True
    store.event("trade" if filled else "gate", "Paper fill recorded." if filled else "Paper proposal refused by risk gate.",
                {"candidate_id": row["id"], "side": side, "quantity": abs(delta), "filled": filled,
                 "gate_reason": result.get("reason"), "decision_id": decision_id,
                 "price": decision.price, "bid": quote["bid"], "ask": quote["ask"], "paper_only": True})
    return {"state": "filled" if filled else "refused", "gate_reason": result.get("reason"), "filled": filled}


class ResearchHarness:
    def __init__(self, transcript, paper, market_store, client, root=Path("data/lab"),
                 now_provider=None, research_seconds=300, quantity=.1):
        if research_seconds < 60 or not math.isfinite(quantity) or quantity <= 0:
            raise ValueError("invalid_harness_config")
        self.store = LabStore(transcript)
        self.paper, self.market_store, self.client = paper, market_store, client
        self.root = Path(root)
        self.now = now_provider or (lambda: datetime.now(timezone.utc))
        self.research_seconds, self.quantity = research_seconds, quantity
        self.stop = threading.Event()
        self.run_id = "agent_codex_" + uuid4().hex[:12]
        self.tick = 0
        self.last_probation = 0.0
        self.monitor_result = {"status": "starting"}
        self.monitor_failures = 0
        self.frame_key = None
        self.recent_frame = None

    def _status(self, phase, **extra):
        status = self.store.meta("status") or {}
        status.update({"state": "running", "phase": phase, "provider": "codex", "run_id": self.run_id,
                       "heartbeat_at": self.now().isoformat(), **extra})
        self.store.meta("status", status)
        from .agent_status import write_status
        state = self.paper.state()
        write_status({"state": "running", "run_id": self.run_id, "planner": "codex", "tick": self.tick,
                      "last_tick_status": phase, "phase": phase, "paper_stopped": state["stopped"],
                      "paper_stop_reason": state["kill_switch_reason"], "integrity": "ok",
                      "monitor": {**self.monitor_result, "recorded_at": self.now().isoformat(),
                                  "consecutive_errors": self.monitor_failures},
                      "monitor_thread_alive": self.monitor_failures < 3,
                      "monitor_error": "monitor_cycle_failed" if self.monitor_failures else None,
                      "lab": status})

    def research_once(self) -> dict:
        self.tick += 1
        frame = self.market_store.read()
        cutoff = pd.Timestamp(self.now()) - pd.Timedelta(minutes=1)
        frame = frame.loc[:cutoff]
        manifest = self.store.meta("dataset")
        dataset_path = self.root / "dataset.parquet"
        if manifest:
            independent = frame.loc[frame.index > pd.Timestamp(manifest["end"])]
            if len(independent) >= 100000:
                # A new cohort must be wholly later than the previous dataset,
                # including its protected holdout. Never recycle a failed split.
                atomic_write_bytes(self.root / "datasets" / (manifest["version"] + ".parquet"), dataset_path.read_bytes())
                history = self.store.meta("dataset_history") or []
                self.store.meta("dataset_history", (history + [manifest])[-12:])
                manifest = None
                self.store.meta("attempts", 0)
                frame = independent
        if not manifest:
            # Freeze once, not on every tick. This is intentionally not rolled
            # forward after a failed experiment or the twentieth attempt.
            frozen = frame.tail(100000)
            manifest = freeze_dataset(frozen)
            buffer = io.BytesIO()
            frozen.to_parquet(buffer)
            atomic_write_bytes(dataset_path, buffer.getvalue())
            self.store.meta("dataset", manifest)
        frozen = pd.read_parquet(dataset_path)
        check = hashlib.sha256(pd.util.hash_pandas_object(frozen, index=True).values.tobytes()).hexdigest()
        if check != manifest["version"]:
            raise ValueError("frozen_dataset_changed")
        rows = [r for r in self.store.candidates() if r.get("dataset_version") == manifest["version"]]
        count = self.store.meta("attempts") or 0
        discovery_only = count >= MAX_ATTEMPTS
        train, _ = partition(frozen, manifest)
        job_id = uuid4().hex
        workspace = self.root / "workspaces" / job_id
        workspace.mkdir(parents=True)
        from .lab_tools import seed_tools
        seed_tools(workspace, self.root / "tools")
        buffer = io.BytesIO()
        train.to_parquet(buffer)
        atomic_write_bytes(workspace / "train.parquet", buffer.getvalue())
        from .research_workflow import prepare_training
        training_schema = prepare_training(workspace, train, manifest["version"])
        self.store.meta("training_schema", training_schema)
        atomic_write_bytes(workspace / "research_runner.py", Path(__file__).with_name("research_runner.py").read_bytes())
        started = self.now().isoformat()
        brief = {"task": "Own an evolving research and engineering agenda toward the 100% daily net-return aspiration, supported by evidence.", "dataset": manifest,
                 "training_schema": training_schema, "train": {"rows": len(train), "start": train.index[0].isoformat(), "end": train.index[-1].isoformat()},
                 "recent_training_bars": [{"time": t.isoformat(), **r} for t, r in train.tail(120).to_dict("index").items()],
                 "memory": self.store.memory(), "prior_candidates": [
                     {k: r.get(k) for k in ("id", "name", "expression", "hypothesis", "state")}
                     for r in rows[:30]],
                 "execution": __import__('dataclasses').asdict(execution_config(self.quantity)),
                 "data_sources": (self.store.meta("sources") or [])[-5:],
                 "constraints": {"paper_only": True, "protected_holdout_unavailable": True,
                                 "no_size_or_risk_changes": True, "attempts_remaining": max(0, MAX_ATTEMPTS - count),
                                 "discovery_only": discovery_only,
                                 "discovery_task": "When the frozen validation budget is exhausted, return zero candidates; improve data/tools and plan a future disjoint dataset. Research continues."}}
        # Only an actual chronological validation consumes the protected budget.
        # Engineering, source discovery and tool work remain open-ended.
        advisor = None
        if hasattr(self.client, "run_turn"):
            from .agent_advisor import AgentAdvisor
            from .agent_tools import AgentTools
            from .agent_engineering import EngineeringManager
            advisor = AgentAdvisor(self.store, self.client, Path.cwd(),
                                   AgentTools(self.store, workspace, Path.cwd()),
                                   EngineeringManager(Path.cwd(), self.store))
            brief.update(account=self.paper.summary(),
                         risk_limits=__import__('dataclasses').asdict(self.paper.config),
                         objective={"aspirational_daily_net_return_pct":100,"capital_planning_ceiling":2000000,
                                    "instruction":"Measure feasibility under actual costs, liquidity, capacity and unchanged risk limits. Report incompatibilities honestly; never increase risk to meet the aspiration."},
                         data_status=self.store.meta("status"),
                         unresolved_actions=[{k:r.get(k) for k in ("id","name","state","result","remote_job_id")}
                                             for r in (self.store.meta("agent_calls") or []) if r["state"]=="unknown"])
        self.store.job({"id": job_id, "state": "running", "started_at": started,
                        "summary": "Codex autonomous research and engineering", "workspace": str(workspace),
                        "session_id": advisor.state()["session_id"] if advisor else None})
        self.store.event("research", "Codex is choosing its next research, data, compute, or engineering action.", {"job_id": job_id})
        completed = "failed"
        try:
            proposal = (advisor.run(workspace, brief, self.stop) if advisor else
                        self.client.run(workspace, brief, self.store.event, self.stop))
            from .lab_tools import promote_tools
            tools = promote_tools(workspace, self.root / "tools", executable=self.client.executable)
            if tools.get("promoted"):
                self.store.meta("tools", tools)
                self.store.event("coding", "Tested research tools published for future Codex jobs.", tools)
            self.store.memory(proposal["memory"])
            self.store.event("conclusion", proposal["summary"], {"job_id": job_id})
            accepted = []
            # Rank on TRAIN ONLY before any validation reads.
            for candidate in ([] if discovery_only else proposal["candidates"]):
                cid = identity(candidate)
                if any(r["id"] == cid for r in self.store.candidates()):
                    self.store.event("research", "Repeated strategy expression skipped.", {"candidate_id": cid})
                    continue
                try:
                    score = evaluate(candidate["expression"], train, self.quantity)["metrics"]["net_profit"]
                    accepted.append((score, candidate))
                except ValueError:
                    self.store.event("validation", "Candidate rejected: invalid causal strategy program.", {"candidate_id": cid})
            # Only the best training candidate consumes a validation attempt.
            for _, candidate in sorted(accepted, key=lambda pair: pair[0], reverse=True)[:1]:
                self.store.meta("attempts", count + 1)
                report = assess(candidate, frozen, manifest, self.quantity)
                created = self.now()
                row = {**candidate, "id": identity(candidate), "created_at": created.isoformat(),
                       "dataset_version": manifest["version"], "execution": report["execution"],
                       "state": "probation" if report["passed"] else "rejected", "report": report,
                       "metrics": report["metrics"], "gates": report["gates"], "job_id": job_id,
                       "forward_end": (created + timedelta(days=7)).isoformat()}
                self.store.candidate(row)
                self.store.event("validation", "Candidate entered prospective observation." if report["passed"] else
                                 "Candidate failed cost-aware chronological validation.",
                                 {"candidate_id": row["id"], "gates": report["gates"], "metrics": report["metrics"]})
            self._sources(proposal["data_requests"])
            completed = "completed"
            if advisor:
                agent_state=advisor.state();agent_state.update(consecutive_errors=0,last_error=None)
                self.store.meta("agent",agent_state)
            self.store.job({"id": job_id, "state": completed, "finished_at": timestamp(), "summary": proposal["summary"]})
            return {"state": completed, "job_id": job_id}
        except Exception as exc:
            code = str(exc) if str(exc) in ("codex_timeout", "codex_failed", "codex_interrupted", "codex_output_limit") else "research_job_failed"
            if advisor:
                agent_state=advisor.state()
                agent_state.update(phase="error",last_error=code,consecutive_errors=agent_state.get("consecutive_errors",0)+1)
                self.store.meta("agent",agent_state)
            self.store.job({"id": job_id, "state": "failed", "finished_at": timestamp(), "error_code": code})
            self.store.event("error", "Research job failed; no strategy was deployed.", {"job_id": job_id, "error_code": code})
            return {"state": "failed", "error_code": code}
        finally:
            atomic_write_json(workspace / "completion.json", {"status": completed, "completed_at": timestamp()})
            # Keep compact evidence in the state store, not a training copy for
            # every job. Research scripts remain for a short retention window.
            for training_name in ("train.parquet", "train.csv"):
                train_path = workspace / training_name
                if train_path.is_file() and not train_path.is_symlink():
                    train_path.unlink()
            if advisor and advisor.engineering:
                from .agent_release_worker import schedule_verification
                schedule_verification(self.store, advisor.engineering)

    def _sources(self, requests):
        from .lab_sources import fetch_source
        for request in requests:
            try:
                source = fetch_source(request["url"])
                self.store.update("sources", lambda rows: ((rows or []) + [source])[-20:], [])
                self.store.event("data", "Retrieved requested research source.", {"url": source["url"], "digest": source["digest"]})
            except Exception:
                self.store.event("data", "Requested source unavailable or outside configured research domains.",
                                 {"error_code": "source_not_retrieved"})

    @serialized
    def probation(self, frame):
        from dataclasses import asdict
        for row in self.store.candidates():
            if row.get("state") == "qualified":
                promote(self.store, row, self.paper)
                continue
            if row.get("state") != "probation" or self.now() < datetime.fromisoformat(row["forward_end"]):
                continue
            shadow = self.store.meta("shadow:" + row["id"]) or {}
            pnl = pd.Series(shadow.get("closed_pnl", []), dtype=float)
            equity = pd.Series([r["equity"] for r in shadow.get("equity", [])], dtype=float)
            state = (shadow.get("account") or {}).get("state") or {}
            wins, losses = pnl[pnl > 0].sum(), -pnl[pnl < 0].sum()
            metrics = {"trades": len(pnl), "net_profit": float(equity.iloc[-1] - 100000) if len(equity) else 0.,
                       "expectancy": float(pnl.mean()) if len(pnl) else None,
                       "profit_factor": float(wins/losses) if losses > 0 else None,
                       "max_drawdown": shadow.get("maximum_drawdown") if len(equity) else None}
            checks = gates_for(metrics, pnl, MIN_FORWARD_TRADES)
            # Frozen seven-day window, scored once. No optional stopping and no
            # price reconstruction from a candle path after the fact.
            coverage = forward_coverage(row["created_at"], row["forward_end"], shadow)
            checks["gates"]["observation_coverage"] = coverage["passed"]
            checks["gates"]["flat_at_end"] = abs(state.get("position", 1)) < 1e-9
            checks["gates"]["shadow_not_stopped"] = state.get("stopped") is False
            row["forward"] = {**checks, "metrics": metrics, "passed": all(checks["gates"].values()),
                              "prospective": True, "quote_based": True, "coverage": coverage, "start": shadow.get("start", row["created_at"]),
                              "end": row["forward_end"], "days": 7,
                              "execution": asdict(execution_config(self.quantity))}
            row["state"] = "qualified" if row["forward"]["passed"] else "rejected_forward"
            row["forward_finalized_at"] = self.now().isoformat()
            row["evidence_digest"] = evidence_digest(row)
            self.store.candidate(row)
            if row["forward"]["passed"]:
                promote(self.store, row, self.paper)

    @serialized
    def shadow_tick(self, frame, now, quote):
        """Observe prospective fills at actual fresh quotes through the same gates."""
        from .paper_trading import PaperTrading
        if not quote_valid(quote, now) or not market_is_open(now):
            return
        for row in self.store.candidates():
            if row.get("state") != "probation" or now >= datetime.fromisoformat(row["forward_end"]):
                continue
            closed = frame.loc[frame.index <= pd.Timestamp(now) - pd.Timedelta(minutes=1)]
            if closed.empty or closed.index[-1] <= pd.Timestamp(row["created_at"]):
                continue
            observed_at = closed.index[-1].to_pydatetime()
            if observation_is_future(observed_at, now) or market_data_age_seconds(observed_at, now) > self.paper.config.max_market_data_age_seconds:
                continue
            key = "shadow:" + row["id"]
            shadow = self.store.meta(key) or {"start": now.isoformat(), "closed_pnl": [], "equity": []}
            bar = closed.index[-1].isoformat()
            account_store = ShadowStore(shadow.get("account"))
            account = PaperTrading(account_store, self.paper.config)
            before = float(account.state()["position"])
            previous_observation = shadow.get("last_observed_at")
            if before and previous_observation:
                first_missing = pd.Timestamp(previous_observation).floor("min") + pd.Timedelta(minutes=1)
                opportunities = _open_minutes(first_missing, pd.Timestamp(now).floor("min") + pd.Timedelta(minutes=1))
                if len(opportunities) > 2:
                    shadow["exposed_observation_gap"] = True
            shadow["last_observed_at"] = now.isoformat()
            mid = (float(quote["bid"]) + float(quote["ask"]))/2
            account.monitor(mid, closed.index[-1].to_pydatetime(), now)
            decision = (target_decision(row, closed, account.state(), now, quote, self.quantity)
                        if shadow.get("last_bar") != bar else None)
            if decision:
                outcome = account.evaluate(decision, now)
                if outcome.get("accepted") and before and abs(account.state()["position"]) < abs(before):
                    shadow["closed_pnl"].append(float(account.state()["ledger"][-1]["realized_pnl"]))
            account.monitor(mid, closed.index[-1].to_pydatetime(), now)
            shadow.update(account=account_store.payload, last_bar=bar)
            equity = account.summary()["equity"]
            high = account.state()["high_water_equity"]
            shadow["maximum_drawdown"] = min(shadow.get("maximum_drawdown", 0), equity/high-1)
            marks = shadow["equity"]
            if marks and marks[-1]["time"][:16] == now.isoformat()[:16]:
                marks = marks[:-1]
            shadow["equity"] = (marks + [{"time": now.isoformat(), "equity": equity}])[-12000:]
            self.store.meta(key, shadow)

    def _research_loop(self):
        last_retention = 0.0
        while not self.stop.is_set():
            try:
                self.probation(None)
                self.research_once()
                if time.monotonic() - last_retention > 86400:
                    from .retention import apply_retention
                    self.store.meta("storage", apply_retention())
                    self.store.meta("monitor_retention", {"removed": self.store.prune_monitor_history(self.now()),
                                                           "recorded_at": timestamp()})
                    self.store.meta("research_evidence_retention", self.store.prune_research_evidence(self.root))
                    last_retention = time.monotonic()
            except Exception:
                agent_state=self.store.meta("agent")
                if agent_state:
                    agent_state.update(phase="error",last_error="research_cycle_failed",
                                       consecutive_errors=agent_state.get("consecutive_errors",0)+1)
                    self.store.meta("agent",agent_state)
                self.store.event("error", "Research cycle unavailable.", {"error_code": "research_cycle_failed"})
            self.stop.wait(self.research_seconds)

    def run(self):
        from .bits_jobs import AgentLock
        from .agent_status import write_status
        lock = AgentLock(self.store.transcript)
        try:
            # Construct/verify the planner before even considering resume.
            try:
                self.client.verify()
            except Exception:
                self.paper.stop("missing_credentials")
                write_status({"state": "stopped", "reason": "missing_credentials", "planner": "codex"})
                return
            legacy = self.store.state.get("cycle", {}) or {}
            with self.store.state.db() as db:
                running_jobs = db.execute("SELECT COUNT(*) c FROM bits_jobs WHERE status IN ('running','unknown')").fetchone()["c"]
            if running_jobs or legacy.get("phase") in ("submitting", "blocked", "job", "workflow"):
                self.paper.stop("recovery_failed")
                write_status({"state": "stopped", "reason": "legacy_recovery_required", "planner": "codex"})
                return
            if self.paper.integrity_check() != "ok":
                self.paper.stop("recovery_failed")
                write_status({"state": "stopped", "reason": "integrity_check_failed"})
                return
            resume = self.paper.maybe_resume("codex_harness")
            if not resume["resumed"]:
                write_status({"state": "stopped", "reason": "resume_refused", **resume})
                return
            interrupted = self.store.recover_jobs()
            if interrupted:
                self.store.event("recovery", "Interrupted research jobs recorded; no uncertain jobs were replayed.", {"count": interrupted})
            self.store.transcript.reconcile_running_runs(excluding=self.run_id)
            self.store.transcript.start_run(self.run_id)
            if hasattr(self.store.transcript, "prune"):
                self.store.transcript.prune(keep_runs=5, keep_steps=20000)
            self.store.event("system", "Codex harness started. Automatic deployment is paper-only; risk gates remain authoritative.", {})
            thread = threading.Thread(target=self._research_loop, name="codex-research", daemon=True)
            thread.start()
            failures = 0
            while not self.stop.is_set():
                try:
                    now = self.now()
                    from .agent_daily import roll_daily_goal
                    roll_daily_goal(self.store,now)
                    path = getattr(self.market_store, "path", None)
                    key = path.stat().st_mtime_ns if path else None
                    if self.recent_frame is None or self.frame_key != key or path is None:
                        self.recent_frame = self.market_store.read().tail(8192)
                        self.frame_key = key
                    frame = self.recent_frame
                    # Monitor the freshest closed bar; future observations fail
                    # closed at the shared gate rather than being clamped away.
                    bar = frame.index[-1].to_pydatetime()
                    from .quotes import read_quote
                    quote = read_quote()
                    mark = (quote["bid"]+quote["ask"])/2 if quote_valid(quote, now) else float(frame.close.iloc[-1])
                    self.monitor_result = self.paper.monitor(mark, bar, now)
                    outcome = paper_tick(self.store, self.paper, frame, now, self.quantity, quote)
                    self.shadow_tick(frame, now, quote)
                    from .agent_experiments import tick as experiment_tick
                    experiment_tick(self.store,self.paper.config,frame,now,quote,self.quantity)
                    summary = self.paper.summary()
                    self.store.equity({"time": now.isoformat(), "equity": summary["equity"]})
                    self._status(outcome["state"], summary="Codex owns an evolving agenda, executes tools, and improves research and application code.")
                    failures = 0
                    self.monitor_failures = 0
                except Exception:
                    failures += 1
                    self.monitor_failures = failures
                    self.monitor_result = {"status": "failed", "consecutive_errors": failures}
                    self.store.event("error", "Independent paper monitor cycle failed.", {"error_code": "monitor_cycle_failed", "consecutive_errors": failures})
                    if failures >= 3:
                        self.paper.stop("recovery_failed")
                        self._status("monitor_failed", error_code="monitor_cycle_failed")
                        break
                    self._status("monitor_error", error_code="monitor_cycle_failed")
                self.stop.wait(5)
            self.stop.set()
            thread.join(timeout=15)
            self.store.transcript.finish_run(self.run_id, "stopped")
            self.store.meta("status", {"state": "stopped", "provider": "codex", "heartbeat_at": timestamp()})
            write_status({"state": "stopped", "run_id": self.run_id, "planner": "codex"})
        except Exception:
            self.paper.stop("recovery_failed")
            write_status({"state": "stopped", "reason": "recovery_failed", "planner": "codex"})
        finally:
            self.stop.set()
            lock.close()
