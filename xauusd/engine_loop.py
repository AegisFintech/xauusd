"""Deterministic paper-trading engine: the trade decision path, with no LLM on it.

Why this exists
---------------
A Datadog Bits round trip measured 22.8s median (39.3s p90) in the live run, so an
LLM can drive at most ~158 cycles per hour no matter how the review floor is
tuned. That is roughly one decision every 23 seconds, which is not a trading
loop. Over 6,666 ticks the supervised agent proposed **zero** trades: every
decision was spent on research.

So execution is split:

* this engine decides, in code, on the market feed;
* the LLM supervises, questions itself, and can halt the engine.

The engine has no privilege the agent did not have. It proposes a
``NormalizedDecision`` and hands it to the same
:meth:`PaperTrading.evaluate` gate the agent uses, so the symbol check, sizing,
daily-loss, drawdown, exposure, duplicate, freshness, market-hours and kill-switch
gates all apply unchanged. A deterministic loop that could skip a risk gate would
be strictly more dangerous than the LLM loop, not less.

Every decision is written to the transcript so the live view can show what the
engine saw, what it proposed, and which gate accepted or refused it.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Protocol
import hashlib
import json
import math
import os
import threading
import time
from uuid import uuid4

from .demo_execution import NormalizedDecision, PaperToCTraderDemoCoordinator
from .paper_trading import PaperTrading

ENGINE_PHASES = ("halted", "waiting", "evaluating", "filled", "refused")
# The engine is the supervisor's only stop control, so it is explicit and durable.
HALT_STATE_KEY = "engine_halt"


class EngineStore(Protocol):
    """The narrow slice of the durable store the engine needs."""

    def get(self, key: str, default: Any = None) -> Any: ...
    def put(self, key: str, value: Any) -> None: ...
    def delete(self, key: str) -> None: ...


class TranscriptSink(Protocol):
    def append(self, run_id: str, tick: int, phase: str, content: dict[str, Any]) -> int: ...
    def start_run(self, run_id: str) -> None: ...
    def finish_run(self, run_id: str, status: str) -> None: ...
    def reconcile_running_runs(self, excluding: str | None = None) -> int: ...


class MarketSource(Protocol):
    def read(self) -> Any: ...


@dataclass(frozen=True)
class EngineConfig:
    """Engine pacing and sizing. Every field is bounded and validated."""

    quantity: float = 0.1
    # One evaluation per closed bar. Faster than this re-reads the same bar and
    # produces duplicate decisions the idempotency store then has to reject.
    poll_seconds: float = 5.0
    # Refuse to act on a bar older than this. Matches the paper freshness gate.
    max_bar_age_seconds: float = 180.0
    # A halt written by the supervisor, and by the engine itself on an internal
    # failure. Separate from the paper kill switch: the engine may be paused
    # while paper trading is still permitted for the agent.
    auto_halt_after_consecutive_errors: int = 3
    strategy: str = "confirmed_breakout"
    status_path: str = "reports/engine_status.json"
    run_id: str = ""

    def validate(self) -> None:
        if not isinstance(self.quantity, (int, float)) or isinstance(self.quantity, bool) \
                or not math.isfinite(self.quantity) or self.quantity <= 0:
            raise ValueError("engine quantity must be finite and positive")
        if not math.isfinite(self.poll_seconds) or self.poll_seconds <= 0:
            raise ValueError("engine poll_seconds must be finite and positive")
        if not math.isfinite(self.max_bar_age_seconds) or self.max_bar_age_seconds <= 0:
            raise ValueError("engine max_bar_age_seconds must be finite and positive")
        if not isinstance(self.auto_halt_after_consecutive_errors, int) \
                or isinstance(self.auto_halt_after_consecutive_errors, bool) \
                or self.auto_halt_after_consecutive_errors < 1:
            raise ValueError("auto_halt_after_consecutive_errors must be a positive integer")
        if not self.strategy.strip():
            raise ValueError("engine strategy must be named")

    @classmethod
    def from_env(cls) -> "EngineConfig":
        return cls(
            quantity=_float_env("ENGINE_QUANTITY", 0.1),
            poll_seconds=_float_env("ENGINE_POLL_SECONDS", 5.0),
            max_bar_age_seconds=_float_env("ENGINE_MAX_BAR_AGE_SECONDS", 180.0),
            auto_halt_after_consecutive_errors=int(_float_env("ENGINE_HALT_AFTER_ERRORS", 3)),
            strategy=os.getenv("ENGINE_STRATEGY", "confirmed_breakout"),
            status_path=os.getenv("ENGINE_STATUS_PATH", "reports/engine_status.json"),
            run_id=os.getenv("ENGINE_RUN_ID", ""),
        )


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


def engine_decision_id(strategy: str, side: str, quantity: float, bar_time: datetime) -> str:
    """Durable identity for one engine decision.

    Derived from the bar, not from a counter, so a restart re-proposes the same
    decision for the same bar and the paper store's idempotency check refuses it
    instead of double-filling.
    """
    payload = {"strategy": strategy, "side": side, "quantity": float(quantity),
               "bar": bar_time.astimezone(timezone.utc).isoformat()}
    return "engine:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass
class EngineDecision:
    """One bar's outcome, as recorded for the live view."""

    bar_utc: str
    price: float
    signal: str
    side: str | None
    quantity: float
    accepted: bool
    gate_reason: str
    decision_id: str | None
    decided_at: str

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


class PaperTradingEngine:
    """Evaluate a deterministic strategy on the feed and pass it through the gates."""

    def __init__(self, paper: PaperTrading, coordinator: PaperToCTraderDemoCoordinator,
                 source: Any, signal_source: Any, store: EngineStore,
                 transcript: TranscriptSink, config: EngineConfig | None = None,
                 now_provider: Callable[[], datetime] | None = None):
        self.paper = paper
        self.coordinator = coordinator
        self.source = source
        self.signals = signal_source
        self.store = store
        self.transcript = transcript
        self.config = config or EngineConfig()
        self.config.validate()
        self._now = now_provider or (lambda: datetime.now(timezone.utc))
        self._stop = threading.Event()
        self.run_id = self.config.run_id or f"engine_{uuid4().hex[:12]}"
        self.tick = 0
        self.consecutive_errors = 0
        self.decisions: list[EngineDecision] = []
        self.halted_reason: str | None = None

    # -- operator / supervisor control ------------------------------------
    def halt(self, reason: str) -> dict[str, Any]:
        """Stop the engine. Operator-only at the CLI, and callable by the supervisor.

        This is deliberately *not* the paper kill switch. Halting the engine means
        no deterministic proposals; paper trading stays available so the agent can
        still act, and the reason is durable so a restart stays halted.
        """
        if not reason.strip():
            raise ValueError("engine halt requires a reason")
        self.halted_reason = reason
        self.store.put(HALT_STATE_KEY, {"reason": reason, "halted_at": self._now().isoformat()})
        self._record("engine_halt", {"summary": f"Engine halted: {reason}", "reason": reason})
        self._write_status("halted")
        return {"halted": True, "reason": reason}

    def resume(self, reason: str) -> dict[str, Any]:
        """Clear a halt. Never clears a paper or demo execution kill switch."""
        if not reason.strip():
            raise ValueError("engine resume requires a reason")
        self.halted_reason = None
        self.consecutive_errors = 0
        self.store.delete(HALT_STATE_KEY)
        self._record("engine_halt", {"summary": f"Engine resumed: {reason}", "reason": reason,
                                     "resumed": True})
        self._write_status("resumed")
        return {"halted": False, "reason": reason}

    @property
    def halted(self) -> bool:
        """Whether a durable halt is in force, re-read from the store every tick.

        The store is the source of truth, not this instance's field. Caching the
        reason meant a halt was latched in memory: `engine resume` cleared the
        key, and the running service kept reporting halted until someone
        restarted it, so the documented supervisor control path did nothing at
        all. A local store read once per closed bar is not worth a control that
        silently fails.
        """
        stored = self.store.get(HALT_STATE_KEY)
        reason = None
        if isinstance(stored, dict) and stored.get("reason"):
            reason = str(stored["reason"])
        if reason != self.halted_reason:
            self.halted_reason = reason
            if reason is None:
                self.consecutive_errors = 0
                self._write_status("resumed")
        return self.halted_reason is not None

    def stop(self) -> None:
        self._stop.set()

    # -- the decision path ------------------------------------------------
    def evaluate_once(self) -> dict[str, Any]:
        """One bar, one evaluation, one recorded outcome. No LLM involved."""
        self.tick += 1
        if self.halted:
            self._write_status("halted")
            return {"tick": self.tick, "status": "halted", "reason": self.halted_reason}
        try:
            outcome = self._decide()
        except Exception as exc:
            self.consecutive_errors += 1
            # An internal failure must not become a silent no-op. The engine is the
            # trade path, so repeated failure halts it and says so.
            self._record("tick_error", {"error_type": type(exc).__name__,
                                        "error_code": "engine_evaluation_failed"})
            if self.consecutive_errors >= self.config.auto_halt_after_consecutive_errors:
                self.halt(f"engine evaluation failed {self.consecutive_errors} times: "
                          f"{type(exc).__name__}")
            self._write_status("error")
            return {"tick": self.tick, "status": "error", "error_type": type(exc).__name__}
        self.consecutive_errors = 0
        return outcome

    def _decide(self) -> dict[str, Any]:
        now = self._now()
        # Market hours first, exactly as the agent's run_tick does. On a weekend the
        # bar is days old, so checking freshness first would report "stale data"
        # for two days when the real cause is that the market is shut.
        from .paper_trading import market_is_open
        if not market_is_open(now):
            self._record("engine_signal", {"bar_utc": None, "signal": "NONE", "quantity": 0.0,
                                           "market_open": False,
                                           "note": "market closed; no evaluation attempted"})
            self._write_status("market_closed")
            return {"tick": self.tick, "status": "market_closed"}
        market = self.source.read()
        price = float(market.price)
        bar_time = market.observed_at
        # The engine reads the same closed-bar rule as the gate, before it
        # proposes. A stale bar must not become a proposal at all.
        from .paper_trading import market_data_age_seconds, observation_is_future
        age = market_data_age_seconds(bar_time, now)
        future = observation_is_future(bar_time, now)
        limit = min(self.config.max_bar_age_seconds, self._stale_limit())
        fresh = (not future) and age <= limit
        if not fresh:
            self._record("engine_signal", {"bar_utc": bar_time.isoformat(), "price": price,
                                           "age_seconds": round(age, 1), "fresh": False,
                                           "future_dated": future, "signal": "NONE",
                                           "quantity": 0.0, "note": "bar is not fresh enough to act on"})
            self._write_status("stale_data", age_seconds=round(age, 1))
            return {"tick": self.tick, "status": "stale_data", "age_seconds": round(age, 1)}

        proposal = self._signal(bar_time)
        side = proposal.side if proposal else None
        self._record("engine_signal", {"bar_utc": bar_time.isoformat(), "price": price,
                                       "age_seconds": round(age, 1), "fresh": True,
                                       "signal": side or "NONE",
                                       "quantity": float(proposal.quantity) if proposal else 0.0,
                                       "decision_id": proposal.decision_id if proposal else None})
        if proposal is None:
            self._write_status("waiting")
            return {"tick": self.tick, "status": "no_signal", "bar_utc": bar_time.isoformat()}

        outcome = self.coordinator.execute(proposal, price, now)
        paper = outcome.get("paper", {})
        accepted = bool(paper.get("accepted", False))
        replayed = bool(paper.get("replayed") or outcome.get("replayed"))
        gate_reason = "DUPLICATE_DECISION" if replayed else str(paper.get("reason") or "")
        decision = EngineDecision(
            bar_utc=bar_time.isoformat(), price=price, signal="TRADE", side=proposal.side,
            quantity=float(proposal.quantity), accepted=accepted and not replayed,
            gate_reason=gate_reason or ("ACCEPTED" if accepted else ""),
            decision_id=proposal.decision_id, decided_at=now.isoformat())
        self.decisions.append(decision)
        self.decisions[:] = self.decisions[-200:]
        self._record("engine_fill" if decision.accepted else "engine_decision",
                     {**decision.to_json(), "paper_only": bool(outcome.get("paper_only")),
                      "position": paper.get("position")})
        self._write_status("filled" if decision.accepted else "refused")
        return {"tick": self.tick, "status": "filled" if decision.accepted else "refused",
                "decision": decision.to_json()}

    def _stale_limit(self) -> float:
        return float(self.paper.config.max_market_data_age_seconds)

    def _signal(self, bar_time: datetime) -> NormalizedDecision | None:
        """Ask the deterministic strategy for a direction, and size it here.

        The strategy supplies direction only. Sizing belongs to the engine because
        it is the risk-relevant knob and must be configured in exactly one place:
        a signal source carrying its own quantity made ``EngineConfig.quantity``
        dead, and the size that reached the gate came from whichever component was
        constructed first.

        The proposal is passed through unchanged. It is deliberately *not* clamped
        to the risk config's max_position: a silent clamp turns a visible
        MAX_POSITION refusal into a hidden partial fill, so the strategy's real
        size and the gate's verdict both stay visible in the record.
        """
        from .demo_runner import MarketData
        # The signal source is stateful by design: it emits each transition once,
        # so the same transition cannot be traded twice across ticks.
        decision = self.signals.read(MarketData(float(self.source.read().price), bar_time))
        if decision is None:
            return None
        quantity = float(self.config.quantity)
        if not math.isfinite(quantity) or quantity <= 0:
            return None
        return NormalizedDecision(
            engine_decision_id(self.config.strategy, decision.side, quantity, bar_time),
            decision.symbol, decision.side, quantity, decision.market_data_at)

    # -- loop and observability -------------------------------------------
    def run_forever(self, iterations: int | None = None) -> dict[str, Any]:
        self.transcript.start_run(self.run_id)
        self.transcript.reconcile_running_runs(self.run_id)
        self._write_status("starting")
        try:
            count = 0
            while not self._stop.is_set():
                self.evaluate_once()
                count += 1
                if iterations is not None and count >= iterations:
                    break
                # wait, not sleep: a halt or SIGTERM takes effect immediately.
                self._stop.wait(self.config.poll_seconds)
        finally:
            self._write_status("stopped")
            self.transcript.finish_run(self.run_id, "stopped")
        return self.status()

    def status(self) -> dict[str, Any]:
        now = self._now()
        last = self.decisions[-1] if self.decisions else None
        paper = self.paper.state()
        return {
            "run_id": self.run_id, "tick": self.tick,
            "state": "halted" if self.halted else "running",
            "halted_reason": self.halted_reason,
            "strategy": self.config.strategy, "quantity": self.config.quantity,
            "poll_seconds": self.config.poll_seconds,
            "decisions": len(self.decisions), "consecutive_errors": self.consecutive_errors,
            "last_decision": last.to_json() if last else None,
            "paper": {"stopped": paper.get("stopped"),
                      "kill_switch_reason": paper.get("kill_switch_reason"),
                      "position": paper.get("position"),
                      "trades_today": paper.get("trades_today")},
            "recorded_at": now.isoformat(),
        }

    def _write_status(self, phase: str, **extra: Any) -> None:
        payload = {"phase": phase, **self.status(), **extra}
        try:
            from .atomic import atomic_write_json
            from pathlib import Path
            atomic_write_json(Path(self.config.status_path), payload)
        except OSError:
            # Observability must never stop the trade path.
            pass

    def _record(self, phase: str, content: dict[str, Any]) -> None:
        try:
            self.transcript.append(self.run_id, self.tick, phase, content)
        except Exception:
            pass
