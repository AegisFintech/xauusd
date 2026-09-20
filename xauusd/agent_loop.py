"""Continuous single-agent XAUUSD paper trading loop with a live, visible thinking process."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from threading import Event
import time
from typing import Any, Callable, Protocol
from uuid import uuid4

from .autonomous_harness import (
    OpenAICompatiblePlanner,
    ToolExecutionError,
    ToolRegistry,
    ToolSpec,
    _now,
    _validate_json,
    canonical_json,
)
from .canary_strategy import ConfirmedBreakoutCanarySource, LocalHistoricalMarketDataSource
from .demo_execution import NormalizedDecision, PaperToCTraderDemoCoordinator
from .experiment_registry import PostgresConnection
from .firecrawl_research import FirecrawlResearchClient, firecrawl_fetch_tool
from .paper_trading import PaperTrading
from .paper_trading import market_is_open

DEFAULT_AGENT_GOAL = (
    "Trade XAUUSD profitably on the safe local paper lifecycle. You see current and recent M1 "
    "bars, the paper account state, and your decision history. You may read market data and "
    "paper state, run the deterministic breakout signal, fetch allow-listed news research, and "
    "propose trades. Proposals are always proposals: the deterministic risk gates approve or "
    "refuse them and only the gate outcome is real. Never claim an order was placed. Finish "
    "every tick with a summary of what you decided and why."
)

MAX_TRANSCRIPT_CONTENT_CHARS = 4000


@dataclass(frozen=True)
class AgentConfig:
    goal: str = DEFAULT_AGENT_GOAL
    poll_seconds: float = 60.0
    max_steps_per_tick: int = 4
    symbol: str = "XAUUSD"
    max_market_data_age_seconds: float = 60.0
    data_refresh_enabled: bool = False
    data_refresh_threshold_seconds: float = 60.0
    data_refresh_min_interval_seconds: float = 300.0
    data_refresh_timeout_seconds: float = 120.0
    transcript_content_limit: int = MAX_TRANSCRIPT_CONTENT_CHARS

    def validate(self) -> None:
        if not self.goal.strip() or self.poll_seconds <= 0 or self.max_steps_per_tick < 1:
            raise ValueError("goal, positive poll seconds, and positive steps per tick are required")
        if not self.symbol.strip():
            raise ValueError("symbol is required")
        if self.max_market_data_age_seconds <= 0 or self.transcript_content_limit < 1:
            raise ValueError("market data age and transcript content limit must be positive")
        for name, value in (("data_refresh_threshold_seconds", self.data_refresh_threshold_seconds),
                            ("data_refresh_min_interval_seconds", self.data_refresh_min_interval_seconds),
                            ("data_refresh_timeout_seconds", self.data_refresh_timeout_seconds)):
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be positive")

    @classmethod
    def from_env(cls) -> "AgentConfig":
        max_age = _positive_float("AGENT_MAX_MARKET_DATA_AGE_SECONDS", 60.0)
        return cls(
            goal=os.getenv("AGENT_GOAL", DEFAULT_AGENT_GOAL),
            poll_seconds=_positive_float("AGENT_POLL_SECONDS", 60.0),
            max_steps_per_tick=int(os.getenv("AGENT_MAX_STEPS_PER_TICK", "4")),
            symbol=os.getenv("AGENT_SYMBOL", "XAUUSD"),
            max_market_data_age_seconds=max_age,
            data_refresh_enabled=os.getenv("AGENT_DATA_REFRESH_ENABLED") == "true",
            data_refresh_threshold_seconds=_positive_float("AGENT_DATA_REFRESH_MAX_AGE_SECONDS", max_age),
            data_refresh_min_interval_seconds=_positive_float("AGENT_DATA_REFRESH_MIN_INTERVAL_SECONDS", 300.0),
            data_refresh_timeout_seconds=_positive_float("AGENT_DATA_REFRESH_TIMEOUT_SECONDS", 120.0),
        )


def _positive_float(name: str, default: float) -> float:
    value = float(os.getenv(name, str(default)))
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


class AgentTranscriptStore(Protocol):
    def initialize(self) -> None: ...
    def start_run(self, run_id: str) -> None: ...
    def finish_run(self, run_id: str, status: str) -> None: ...
    def reconcile_running_runs(self, excluding: str | None = None) -> int: ...
    def append(self, run_id: str, tick: int, phase: str, content: dict[str, Any]) -> int: ...
    def steps(self, run_id: str | None = None, after_id: int = 0, before_id: int | None = None,
              desc: bool = False, limit: int = 100) -> list[dict[str, Any]]: ...
    def runs(self, limit: int = 20) -> list[dict[str, Any]]: ...
    def run_status(self, run_id: str) -> str | None: ...


class CockroachAgentTranscriptStore:
    """Production transcript store; the database is authoritative agent state."""

    def __init__(self, database_url: str | None = None, initialize: bool = True):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is required for the agent transcript")
        if initialize:
            self.initialize()

    def connect(self):
        return PostgresConnection(self.database_url)

    def initialize(self) -> None:
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS agent_runs (run_id TEXT PRIMARY KEY, status TEXT NOT NULL CHECK(status IN ('running','completed','stopped','failed')), created_at TEXT NOT NULL, finished_at TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS agent_transcript (id BIGSERIAL PRIMARY KEY, run_id TEXT NOT NULL REFERENCES agent_runs(run_id), tick BIGINT NOT NULL, phase TEXT NOT NULL, content_json TEXT NOT NULL, occurred_at TEXT NOT NULL)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_agent_transcript_run ON agent_transcript(run_id,id)")

    def start_run(self, run_id: str) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO agent_runs(run_id,status,created_at) VALUES(?,?,?)", (run_id, "running", _now()))

    def finish_run(self, run_id: str, status: str) -> None:
        with self.connect() as db:
            db.execute("UPDATE agent_runs SET status=?,finished_at=? WHERE run_id=? AND status='running'", (status, _now(), run_id))

    def append(self, run_id: str, tick: int, phase: str, content: dict[str, Any]) -> int:
        with self.connect() as db:
            cursor = db.execute("INSERT INTO agent_transcript(run_id,tick,phase,content_json,occurred_at) VALUES(?,?,?,?,?) RETURNING id",
                                (run_id, tick, phase, canonical_json(content), _now()))
            return int(cursor.fetchone()["id"])

    def steps(self, run_id: str | None = None, after_id: int = 0, before_id: int | None = None,
              desc: bool = False, limit: int = 100) -> list[dict[str, Any]]:
        if desc:
            params: list[Any] = []
            where = []
            if before_id is not None:
                where.append("id < ?")
                params.append(before_id)
            order = "ORDER BY id DESC"
        else:
            params = [after_id]
            where = ["id > ?"]
            order = "ORDER BY id ASC"
        if run_id:
            where.append("run_id = ?")
            params.append(run_id)
        params.append(limit)
        sql = f"SELECT id,run_id,tick,phase,content_json,occurred_at FROM agent_transcript WHERE {' AND '.join(where) or '1=1'} {order} LIMIT ?"
        with self.connect() as db:
            rows = db.execute(sql, tuple(params)).fetchall()
        return [self._row(row) for row in rows]

    def runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute("SELECT run_id,status,created_at,finished_at FROM agent_runs ORDER BY created_at DESC LIMIT ?",
                              (limit,)).fetchall()
            counts = {row["run_id"]: int(row["total"]) for row in db.execute(
                "SELECT run_id, COUNT(*) AS total FROM agent_transcript WHERE phase='tick_start' GROUP BY run_id")}
        return [{"run_id": row["run_id"], "status": row["status"], "created_at": row["created_at"],
                 "finished_at": row["finished_at"], "ticks": counts.get(row["run_id"], 0)} for row in rows]

    def run_status(self, run_id: str) -> str | None:
        with self.connect() as db:
            row = db.execute("SELECT status FROM agent_runs WHERE run_id=?", (run_id,)).fetchone()
        return row["status"] if row else None

    def reconcile_running_runs(self, excluding: str | None = None) -> int:
        parameters: list[Any] = ["stopped", _now()]
        where = ["status='running'"]
        if excluding:
            where.append("run_id != ?")
            parameters.append(excluding)
        with self.connect() as db:
            cursor = db.execute(f"UPDATE agent_runs SET status=?,finished_at=? WHERE {' AND '.join(where)}",
                                tuple(parameters))
        return int(cursor.rowcount or 0)

    @staticmethod
    def _row(row: Any) -> dict[str, Any]:
        return {"id": int(row["id"]), "run_id": row["run_id"], "tick": int(row["tick"]), "phase": row["phase"],
                "content": json.loads(row["content_json"]), "occurred_at": row["occurred_at"]}


class InMemoryAgentTranscriptStore:
    """Test double only; production state lives in the configured backend store."""

    def __init__(self):
        self._next_id = 1
        self._runs: dict[str, dict[str, Any]] = {}
        self._steps: list[dict[str, Any]] = []

    def initialize(self) -> None: pass
    def start_run(self, run_id): self._runs[run_id] = {"status": "running"}
    def finish_run(self, run_id, status):
        if run_id in self._runs and self._runs[run_id]["status"] == "running":
            self._runs[run_id]["status"] = status
    def append(self, run_id, tick, phase, content):
        step = {"id": self._next_id, "run_id": run_id, "tick": tick, "phase": phase,
                "content": content, "occurred_at": _now()}
        self._next_id += 1
        self._steps.append(step)
        return step["id"]
    def steps(self, run_id=None, after_id=0, before_id=None, desc=False, limit=100):
        matches = [step for step in self._steps if run_id is None or step["run_id"] == run_id]
        if desc:
            if before_id is not None:
                matches = [step for step in matches if step["id"] < before_id]
            matches.sort(key=lambda step: -step["id"])
        else:
            matches = [step for step in matches if step["id"] > after_id]
            matches.sort(key=lambda step: step["id"])
        return matches[:limit]
    def runs(self, limit=20):
        from collections import Counter
        ticks = Counter(step["run_id"] for step in self._steps if step["phase"] == "tick_start")
        return [{"run_id": rid, "status": run["status"], "ticks": int(ticks.get(rid, 0))}
                for rid, run in self._runs.items()][:limit]
    def run_status(self, run_id): return self._runs.get(run_id, {}).get("status")
    def reconcile_running_runs(self, excluding=None):
        closed = 0
        for rid, run in self._runs.items():
            if rid == excluding or run.get("status") != "running":
                continue
            run["status"] = "stopped"
            run["finished_at"] = _now()
            closed += 1
        return closed


def agent_transcript_store_from_env(initialize: bool = True) -> AgentTranscriptStore:
    """Transcript store for the configured backend (local SQLite by default)."""
    backend = (os.getenv("XAUUSD_STATE_BACKEND") or "local").lower()
    if backend == "cockroach":
        return CockroachAgentTranscriptStore(initialize=initialize)
    if backend == "local":
        from .local_state import SQLiteAgentTranscriptStore
        return SQLiteAgentTranscriptStore(initialize=initialize)
    raise ValueError("XAUUSD_STATE_BACKEND must be 'local' or 'cockroach'")


def _decision_id(provider: str, symbol: str, side: str, quantity: float, market_data_at: datetime) -> str:
    payload = {"provider": provider, "symbol": symbol, "side": side, "quantity": float(quantity),
               "market_data_at": market_data_at.astimezone(timezone.utc).isoformat()}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _assistant_step(action: dict[str, Any], raw: str, limit: int) -> dict[str, Any]:
    """Display-friendly assistant step: parsed action plus the model's plain-English reason."""
    content = {"action": action["action"], "reply": raw[:limit]}
    if action["action"] == "final":
        content["summary"] = action["summary"]
    else:
        content["tool"] = action["tool"]
        content["input"] = _redact_for_transcript(action["input"], limit)
    reason = action.get("reason")
    if reason:
        content["reason"] = reason[:400]
    return content


def _redact_for_transcript(result: dict[str, Any], limit: int) -> dict[str, Any]:
    """Transcript-friendly view: keep structures, bound untrusted string lengths."""
    if isinstance(result, dict):
        return {key: _redact_for_transcript(value, limit) for key, value in result.items()}
    if isinstance(result, list):
        return [_redact_for_transcript(value, limit) for value in result]
    if isinstance(result, str) and len(result) > limit:
        return result[:limit] + f"...<truncated {len(result) - limit} chars>"
    return result


def read_market_tool(source: LocalHistoricalMarketDataSource, config: AgentConfig) -> ToolSpec:
    def handler(value: dict[str, Any]) -> dict[str, Any]:
        market = source.read()
        age_seconds = (datetime.now(timezone.utc) - market.observed_at.astimezone(timezone.utc)).total_seconds()
        recent_closes: list[float] = []
        try:
            normalized = source.store.normalize(source.store.read())
            recent_closes = [float(close) for close in normalized["close"].tail(5)]
        except Exception:
            recent_closes = []
        return {"symbol": config.symbol, "price": float(market.price),
                "bar_time_utc": market.observed_at.astimezone(timezone.utc).isoformat(),
                "age_seconds": round(age_seconds, 1), "fresh": age_seconds <= config.max_market_data_age_seconds,
                "market_open": market_is_open(datetime.now(timezone.utc)),
                "recent_closes": recent_closes}

    input_schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
    output_schema = {"type": "object", "properties": {
        "symbol": {"type": "string"}, "price": {"type": "number"}, "bar_time_utc": {"type": "string"},
        "age_seconds": {"type": "number"}, "fresh": {"type": "boolean"}, "market_open": {"type": "boolean"},
        "recent_closes": {"type": "array", "items": {"type": "number"}},
    }, "required": ["symbol", "price", "bar_time_utc", "age_seconds", "fresh", "market_open", "recent_closes"], "additionalProperties": False}
    return ToolSpec("read_market", "Read the latest market observation and freshness from the local M1 data.", input_schema, output_schema, handler)


def paper_state_tool(paper_trading: PaperTrading) -> ToolSpec:
    def handler(value: dict[str, Any]) -> dict[str, Any]:
        state = paper_trading.state()
        return {"stopped": bool(state.get("stopped")), "position": float(state.get("position", 0.0)),
                "cash": float(state.get("cash", 0.0)), "average_entry_price": float(state.get("average_entry_price", 0.0)),
                "mark_price": float(state.get("mark_price", 0.0)), "day_start_equity": float(state.get("day_start_equity", 0.0)),
                "high_water_equity": float(state.get("high_water_equity", 0.0)),
                "trades_today": int(state.get("trades_today", 0)),
                "recent_ledger": [{"decision_id": entry.get("decision_id"), "side": entry.get("side"),
                                   "quantity": float(entry.get("quantity", 0)), "price": float(entry.get("price", 0))
                                   if entry.get("price") is not None else None,
                                   "net_debit": float(entry.get("net_debit", 0)) if entry.get("net_debit") is not None else None}
                                  for entry in state.get("ledger", [])[-5:]]}

    input_schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
    output_schema = {"type": "object", "properties": {
        "stopped": {"type": "boolean"}, "position": {"type": "number"}, "cash": {"type": "number"},
        "average_entry_price": {"type": "number"}, "mark_price": {"type": "number"},
        "day_start_equity": {"type": "number"}, "high_water_equity": {"type": "number"}, "trades_today": {"type": "integer"},
        "recent_ledger": {"type": "array", "items": {"type": "object"}},
    }, "required": ["stopped", "position", "cash", "average_entry_price", "mark_price", "day_start_equity",
                    "high_water_equity", "trades_today", "recent_ledger"], "additionalProperties": False}
    return ToolSpec("paper_state", "Read the current paper account state and recent fills.", input_schema, output_schema, handler)


def canary_signal_tool(canary: ConfirmedBreakoutCanarySource) -> ToolSpec:
    def handler(value: dict[str, Any]) -> dict[str, Any]:
        decision = canary.read(_mock_market_for_read(canary))
        if decision is None:
            return {"signal": "NONE", "quantity": 0.0}
        return {"signal": decision.side, "quantity": float(decision.quantity)}

    input_schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
    output_schema = {"type": "object", "properties": {
        "signal": {"type": "string", "enum": ["NONE", "BUY", "SELL"]}, "quantity": {"type": "number"},
    }, "required": ["signal", "quantity"], "additionalProperties": False}
    return ToolSpec("canary_signal", "Run the deterministic confirmed-breakout signal on closed M1 bars.", input_schema, output_schema, handler)


def _mock_market_for_read(canary: ConfirmedBreakoutCanarySource):
    from .demo_runner import MarketData
    bars = canary.store.read()
    if bars is None or bars.empty:
        return MarketData(0.0, datetime.now(timezone.utc))
    last_time = bars.index[-1]
    return MarketData(float(bars["close"].iloc[-1]), last_time)


def propose_trade_tool(coordinator: PaperToCTraderDemoCoordinator, paper_trading: PaperTrading,
                       source: LocalHistoricalMarketDataSource, config: AgentConfig,
                       now_provider: Callable[[], datetime] | None = None) -> ToolSpec:
    def handler(value: dict[str, Any]) -> dict[str, Any]:
        market = source.read()
        decision = NormalizedDecision(
            _decision_id("agent", config.symbol, value["side"], value["quantity"], market.observed_at),
            config.symbol, value["side"], float(value["quantity"]), market.observed_at,
        )
        now = now_provider() if now_provider is not None else datetime.now(timezone.utc)
        outcome = coordinator.execute(decision, float(market.price), now)
        paper = outcome.get("paper", {})
        return {"accepted": bool(outcome.get("accepted", False)), "decision_id": decision.decision_id,
                "reason": paper.get("reason"), "paper_accept": bool(paper.get("accepted", False)),
                "paper_reason": paper.get("reason"), "paper_only": bool(outcome.get("paper_only", False)),
                "proposal_reason": value.get("reason", "")}

    input_schema = {"type": "object", "properties": {
        "side": {"type": "string", "enum": ["BUY", "SELL"]}, "quantity": {"type": "number"}, "reason": {"type": "string"},
    }, "required": ["side", "quantity", "reason"], "additionalProperties": False}
    output_schema = {"type": "object", "properties": {
        "accepted": {"type": "boolean"}, "decision_id": {"type": "string"}, "reason": {"type": "string"},
        "paper_accept": {"type": "boolean"}, "paper_reason": {"type": "string"}, "paper_only": {"type": "boolean"},
        "proposal_reason": {"type": "string"},
    }, "required": ["accepted", "decision_id", "reason", "paper_accept", "paper_reason", "paper_only", "proposal_reason"],
        "additionalProperties": False}
    return ToolSpec("propose_trade", "Propose a paper trade. The deterministic risk gates approve or refuse; their outcome is authoritative.",
                    input_schema, output_schema, handler)


def build_agent_registry(source: LocalHistoricalMarketDataSource, paper_trading: PaperTrading,
                         coordinator: PaperToCTraderDemoCoordinator, config: AgentConfig,
                         canary: ConfirmedBreakoutCanarySource | None = None,
                         firecrawl_client: FirecrawlResearchClient | None = None) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(read_market_tool(source, config))
    registry.register(paper_state_tool(paper_trading))
    registry.register(propose_trade_tool(coordinator, paper_trading, source, config))
    if canary is not None:
        registry.register(canary_signal_tool(canary))
    if firecrawl_client is not None:
        registry.register(firecrawl_fetch_tool(firecrawl_client))
    return registry


class ContinuousAgentRunner:
    """Drives one planner per tick; every action and outcome becomes a visible transcript step."""

    def __init__(self, planner: OpenAICompatiblePlanner, registry: ToolRegistry,
                 transcript: AgentTranscriptStore, source: LocalHistoricalMarketDataSource,
                 paper_trading: PaperTrading, coordinator: PaperToCTraderDemoCoordinator | None = None,
                 config: AgentConfig | None = None,
                 refresh_source: Callable[[], dict[str, Any]] | None = None,
                 status_path: str | None = None,
                 now_provider: Callable[[], datetime] | None = None):
        self.planner, self.registry, self.transcript = planner, registry, transcript
        self.source, self.paper_trading = source, paper_trading
        self.coordinator = coordinator or PaperToCTraderDemoCoordinator(paper_trading, paper_only=True)
        self.config = config or AgentConfig()
        self.refresh_source = refresh_source
        self._last_refresh_at: float | None = None
        self.config.validate()
        self.run_id = f"agent_{uuid4().hex[:12]}"
        self._tick = 0
        self._stop = Event()
        self.status_path = status_path
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))
        self._started_at = datetime.now(timezone.utc)
        self.consecutive_errors = 0
        self.transcript.initialize()
        self.transcript.start_run(self.run_id)
        self._closed_orphans = self.transcript.reconcile_running_runs(self.run_id)
        self._write_status("starting")

    def _now(self) -> datetime:
        return self._now_provider()

    def _write_status(self, status: str, **extra: Any) -> None:
        """Persist one heartbeat when a status path is configured (atomic)."""
        if not self.status_path:
            return
        from .agent_status import write_status
        paper = self.paper_trading.state()
        payload = {"run_id": self.run_id, "pid": os.getpid(), "status": status,
                   "last_tick_status": status, "started_at": self._started_at.isoformat(),
                   "last_tick_at": datetime.now(timezone.utc).isoformat(),
                   "tick": self._tick, "market_open": market_is_open(self._now()),
                   "consecutive_errors": self.consecutive_errors,
                   "stalled": self.consecutive_errors >= 5,
                   "closed_orphans": self._closed_orphans,
                   "paper_stopped": bool(paper.get("stopped")),
                   "kill_switch_reason": paper.get("kill_switch_reason")}
        payload.update(extra)
        write_status(payload, self.status_path)

    @staticmethod
    def _age(market) -> float:
        return (datetime.now(timezone.utc) - market.observed_at.astimezone(timezone.utc)).total_seconds()

    def _refresh_if_stale(self, tick: int, age: float) -> bool:
        """Blocking, bounded, opt-in refresh that never interrupts the tick loop."""
        if self.refresh_source is None or not self.config.data_refresh_enabled:
            return False
        if age <= self.config.data_refresh_threshold_seconds:
            return False
        now = time.monotonic()
        if self._last_refresh_at is not None and now - self._last_refresh_at < self.config.data_refresh_min_interval_seconds:
            self.transcript.append(self.run_id, tick, "data_refresh", {
                "ok": False, "skipped": "cooldown", "age_seconds": round(age, 1)})
            return False
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.refresh_source)
        try:
            result = future.result(timeout=self.config.data_refresh_timeout_seconds)
        except FutureTimeoutError:
            result = {"ok": False, "error_type": "timeout"}
        except Exception as exc:
            result = {"ok": False, "error_type": type(exc).__name__}
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
        self._last_refresh_at = time.monotonic()
        refreshed = bool(result.get("ok"))
        step = dict(result)
        step.setdefault("age_seconds", round(age, 1))
        self.transcript.append(self.run_id, tick, "data_refresh", step)
        return refreshed

    def run_tick(self) -> dict[str, Any]:
        self._tick += 1
        tick = self._tick
        now_utc = self._now()
        market = self.source.read()
        if not market_is_open(now_utc):
            # Deterministic gate: never spend a planner call, tokens, or a data
            # refresh while the XAUUSD session is closed (weekends, 21:00-22:00 UTC).
            self.consecutive_errors = 0
            self.transcript.append(self.run_id, tick, "tick_start", {
                "price": float(market.price),
                "bar_time_utc": market.observed_at.astimezone(timezone.utc).isoformat(),
                "age_seconds": round(self._age(market), 1),
                "fresh": self._age(market) <= self.config.max_market_data_age_seconds,
                "market_open": False})
            self.transcript.append(self.run_id, tick, "tick_end",
                                   {"summary": "XAUUSD market is closed", "steps": 0})
            outcome = {"tick": tick, "status": "market_closed", "summary": "XAUUSD market is closed", "steps": 0}
            self._write_status("market_closed")
            return outcome
        if self._refresh_if_stale(tick, self._age(market)):
            market = self.source.read()
        self.transcript.append(self.run_id, tick, "tick_start", {
            "price": float(market.price),
            "bar_time_utc": market.observed_at.astimezone(timezone.utc).isoformat(),
            "age_seconds": round(self._age(market), 1),
            "fresh": self._age(market) <= self.config.max_market_data_age_seconds,
            "market_open": True})
        evidence = [{"source": "market_snapshot", "market": self._market_view(market)},
                    {"source": "paper_state", "state": self.paper_trading.state()}]
        for step in range(self.config.max_steps_per_tick + 1):
            try:
                raw, action = self.planner.plan_with_raw(self.config.goal, self.registry, evidence)
            except Exception as exc:
                self.consecutive_errors += 1
                self.transcript.append(self.run_id, tick, "tick_end",
                                       {"summary": "planner error", "steps": step + 1, "error_type": type(exc).__name__})
                self._write_status("planner_error", error_type=type(exc).__name__)
                return {"tick": tick, "status": "planner_error", "summary": "planner error", "steps": step + 1}
            self.transcript.append(self.run_id, tick, "assistant", _assistant_step(action, raw, self.config.transcript_content_limit))
            if action["action"] == "final":
                self.consecutive_errors = 0
                self.transcript.append(self.run_id, tick, "tick_end",
                                       {"summary": action["summary"], "steps": step + 1})
                self._write_status("completed")
                return {"tick": tick, "status": "completed", "summary": action["summary"], "steps": step + 1}
            if step >= self.config.max_steps_per_tick:
                self.consecutive_errors = 0
                self.transcript.append(self.run_id, tick, "tick_end", {"summary": "tick step limit", "steps": step + 1})
                self._write_status("step_limit")
                return {"tick": tick, "status": "step_limit", "summary": "tick step limit", "steps": step + 1}
            tool = self.registry.get(action["tool"])
            tool_input = action["input"]
            self.transcript.append(self.run_id, tick, "tool_call", {"tool": tool.name, "input": tool_input, "step": step + 1})
            result = self._execute_tool(tick, tool, tool_input)
            self.transcript.append(self.run_id, tick, "tool_result", _redact_for_transcript(result, self.config.transcript_content_limit))
            evidence.append({"tool": tool.name, "input": tool_input, "result": result})
        raise AssertionError("bounded agent tick must return or fail")

    def _market_view(self, market) -> dict[str, Any]:
        try:
            normalized = self.source.store.normalize(self.source.store.read())
            closes = [float(close) for close in normalized["close"].tail(5)]
        except Exception:
            closes = []
        view = {"symbol": self.config.symbol, "price": float(market.price),
                "bar_time_utc": market.observed_at.astimezone(timezone.utc).isoformat(), "recent_closes": closes}
        age = self._age(market)
        view["age_seconds"] = round(age, 1)
        view["fresh"] = age <= self.config.max_market_data_age_seconds
        view["market_open"] = market_is_open(self._now())
        return view

    def _execute_tool(self, tick: int, tool: ToolSpec, tool_input: dict[str, Any]) -> dict[str, Any]:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(tool.handler, tool_input)
        try:
            result = future.result(timeout=tool.timeout_seconds)
        except FutureTimeoutError:
            return {"status": "failed", "error_type": "timeout"}
        except Exception as exc:
            return {"status": "failed", "error_type": type(exc).__name__}
        finally:
            # A timed-out tool cannot block the agent tick.
            executor.shutdown(wait=False, cancel_futures=True)
        try:
            _validate_json(result, tool.output_schema)
        except ValueError as exc:
            return {"status": "invalid_output", "error_type": type(exc).__name__}
        result["status"] = "completed"
        return result

    def run_forever(self, stop: Event | None = None, on_tick: Callable[[dict[str, Any]], None] | None = None) -> None:
        if stop is not None:
            self._stop = stop
        while not self._stop.is_set():
            try:
                result = self.run_tick()
                if on_tick is not None:
                    on_tick(result)
            except Exception as exc:
                self.consecutive_errors += 1
                self.transcript.append(self.run_id, self._tick, "tick_error", {"error_type": type(exc).__name__})
                self._write_status("tick_error", error_type=type(exc).__name__)
            self._stop.wait(self.config.poll_seconds)

    def stop(self) -> None:
        self._stop.set()
        self.transcript.finish_run(self.run_id, "stopped")
        self._write_status("stopped")

    def status(self) -> dict[str, Any]:
        return {"run_id": self.run_id, "status": self.transcript.run_status(self.run_id) or "running",
                "tick": self._tick, "poll_seconds": self.config.poll_seconds}