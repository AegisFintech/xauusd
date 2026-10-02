"""Deterministic, database-backed paper trading.  This module has no broker capability."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
import math
import os
from typing import Any, Callable, Protocol
from zoneinfo import ZoneInfo

from .experiment_registry import PostgresConnection, canonical_json


KILL_SWITCH = "KILL_SWITCH"
INVALID_DECISION = "INVALID_DECISION"
UNSUPPORTED_SYMBOL = "UNSUPPORTED_SYMBOL"
STALE_MARKET_DATA = "STALE_MARKET_DATA"
MARKET_CLOSED = "MARKET_CLOSED"
MAX_TRADES_PER_DAY = "MAX_TRADES_PER_DAY"
MAX_POSITION = "MAX_POSITION"
DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"
MAX_DRAWDOWN = "MAX_DRAWDOWN"
ACCEPTED = "ACCEPTED"
# Reported by the propose_trade tool when the store returned a persisted outcome
# for a decision id it had already processed. Not a gate reason: no gate refused,
# the proposal was simply not a new one.
DUPLICATE_DECISION = "DUPLICATE_DECISION"

# Restart policy shared by every persistent kill switch (paper and cTrader demo execution).
# This is an allowlist: an unattended restart may only start a fresh account that nothing has
# ever stopped. Every other persisted reason (``operator`` or any custom ``paper stop --reason``,
# corrupt state, missing credentials, recovery or reconciliation failure, risk limits, broker
# failures, and reasons added in future) stays stopped until an explicit start (AGENTS.md).
KILL_SWITCH_AUTO_RESUME = frozenset({"missing_state"})


def restart_policy(state: dict[str, Any]) -> str:
    """Classify a persisted kill switch for an unattended restart.

    ``"running"``: not stopped, so resuming is a no-op. ``"resume"``: a fresh, never-stopped
    account that may start. ``"refuse"``: any other stop, including a state without an explicit
    boolean ``stopped`` flag, must be preserved until an operator starts it explicitly.
    """
    stopped = state.get("stopped")
    if stopped is False:
        return "running"
    if stopped is True and state.get("kill_switch_reason") in KILL_SWITCH_AUTO_RESUME:
        return "resume"
    return "refuse"


# XAUUSD spot trades from Sunday 18:00 to Friday 17:00 New York time, with a daily break at the
# 17:00 New York close. Anchoring the session to New York keeps it correct across US daylight
# saving time: the break is 21:00-22:00 UTC from March to November and 22:00-23:00 UTC in winter.
# zoneinfo uses the system tz database or the ``tzdata`` package (already a pandas dependency).
NEW_YORK = ZoneInfo("America/New_York")
NEW_YORK_CLOSE_HOUR = 17
NEW_YORK_REOPEN_HOUR = 18


def market_is_open(now: datetime) -> bool:
    """XAUUSD spot session: Sunday 18:00 to Friday 17:00 New York time, break 17:00-18:00 New York.

    In UTC that is Sunday 22:00 to Friday 21:00 with a 21:00-22:00 break during US daylight time,
    and one hour later (Sunday 23:00, Friday 22:00, break 22:00-23:00) during US standard time.
    Exchange holidays are not modelled; the freshness gates refuse trading when bars stop arriving.
    """
    local = now.astimezone(NEW_YORK)
    weekday = local.weekday()  # Monday=0 ... Sunday=6, in New York time
    if weekday == 5:  # Saturday
        return False
    if weekday == 6:  # Sunday opens at 18:00 New York
        return local.hour >= NEW_YORK_REOPEN_HOUR
    if weekday == 4:  # Friday closes at 17:00 New York
        return local.hour < NEW_YORK_CLOSE_HOUR
    return local.hour != NEW_YORK_CLOSE_HOUR  # Monday-Thursday: closed for the daily break


# Persisted bars are M1 and stamped with their *open* time, so the newest bar in
# the store is not a complete observation until one interval later.
BAR_INTERVAL_SECONDS = 60.0

# Three closed M1 bars. Tighter than one bar interval is unsatisfiable (see
# market_data_age_seconds); three bars absorbs a late download without letting a
# gate pass on a feed that has genuinely stopped advancing.
DEFAULT_MAX_MARKET_DATA_AGE_SECONDS = 180.0


def market_data_age_seconds(bar_time: datetime, now: datetime,
                            bar_seconds: float = BAR_INTERVAL_SECONDS) -> float:
    """Age of a persisted bar measured from when that bar *closed*.

    Every freshness gate must use this instead of subtracting the bar timestamp
    from the clock: a closed M1 bar stamped 01:09 is only knowable at 01:10, so
    measuring from the open time makes the newest bar intrinsically older than
    any per-minute threshold and the gate can never pass. The result is clamped
    at zero for a bar still forming, whose close time is up to one interval ahead.

    That clamp is only honest for a bar at most one interval into the future. A
    bar further ahead than that is not a forming bar, it is a bad observation:
    it would report age zero forever, pass every freshness gate, and supply the
    fill price. Callers must pair this with :func:`observation_is_future` rather
    than relying on a large age to reject it.
    """
    closed_at = bar_time.astimezone(timezone.utc) + timedelta(seconds=bar_seconds)
    return max(0.0, (now.astimezone(timezone.utc) - closed_at).total_seconds())


def observation_is_future(bar_time: datetime, now: datetime,
                          bar_seconds: float = BAR_INTERVAL_SECONDS) -> bool:
    """True when a bar closes more than one interval after ``now``.

    Rejects a future-dated observation instead of letting the zero clamp above
    mark it perpetually fresh.
    """
    closed_at = bar_time.astimezone(timezone.utc) + timedelta(seconds=bar_seconds)
    return closed_at > now.astimezone(timezone.utc) + timedelta(seconds=bar_seconds)


def _positive_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = float(raw)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return value


@dataclass(frozen=True)
class PaperRiskConfig:
    daily_loss_limit: float = 500.0
    max_drawdown: float = 0.10
    max_position: float = 1.0
    max_trades_per_day: int = 20
    max_market_data_age_seconds: float = DEFAULT_MAX_MARKET_DATA_AGE_SECONDS

    def validate(self) -> None:
        values = asdict(self)
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0
               for value in values.values()):
            raise ValueError("paper risk config values must be finite positive numbers")
        if self.max_drawdown > 1:
            raise ValueError("max_drawdown must be between zero and one")
        if not float(self.max_trades_per_day).is_integer():
            raise ValueError("max_trades_per_day must be a whole number")

    @classmethod
    def from_env(cls) -> "PaperRiskConfig":
        config = cls(
            daily_loss_limit=_positive_env_float("PAPER_DAILY_LOSS_LIMIT", 500.0),
            max_drawdown=_positive_env_float("PAPER_MAX_DRAWDOWN", 0.10),
            max_position=_positive_env_float("PAPER_MAX_POSITION", 1),
            max_trades_per_day=int(_positive_env_float("PAPER_MAX_TRADES_PER_DAY", 20)),
            max_market_data_age_seconds=_positive_env_float(
                "PAPER_MAX_MARKET_DATA_AGE_SECONDS", DEFAULT_MAX_MARKET_DATA_AGE_SECONDS),
        )
        config.validate()
        return config


@dataclass(frozen=True)
class PaperDecision:
    decision_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    market_data_at: datetime


def _default_state(initial_cash: float = 100_000.0) -> dict[str, Any]:
    return {"stopped": True, "kill_switch_reason": "missing_state", "cash": initial_cash,
            "position": 0.0, "average_entry_price": 0.0, "mark_price": 0.0,
            "high_water_equity": initial_cash, "day": None, "day_start_equity": initial_cash,
            "trades_today": 0, "ledger": []}


# Every key the gates index directly. A state missing any of them cannot be
# evaluated, so it is corruption rather than a partial account.
REQUIRED_STATE_KEYS = frozenset({
    "stopped", "kill_switch_reason", "cash", "position", "average_entry_price", "mark_price",
    "high_water_equity", "day", "day_start_equity", "trades_today", "ledger",
})

# Numeric fields that must stay finite. A NaN or inf here silently turns every
# comparison in _gate into a pass or a trip depending on its direction.
NUMERIC_STATE_KEYS = ("cash", "position", "average_entry_price", "mark_price",
                      "high_water_equity", "day_start_equity", "trades_today")


def _corrupt_state(initial_cash: float) -> dict[str, Any]:
    state = _default_state(initial_cash)
    state["kill_switch_reason"] = "corrupt_state"
    return state


def validated_paper_state(state: Any, initial_cash: float) -> dict[str, Any]:
    """Validate persisted paper state, falling back to a stopped corrupt account.

    Accepts either a raw JSON string (a database row) or an already-decoded value
    (the in-memory store). Corruption is anything that cannot be evaluated safely:
    unparseable JSON, a non-object, a missing required key, a non-boolean
    ``stopped``, a non-list ``ledger``, or a non-finite numeric field.

    Returning a *stopped* default is what makes this fail closed for every
    consumer at once: the fill gate refuses with KILL_SWITCH, :func:`restart_policy`
    refuses the unattended resume, and ``paper status`` names the reason. Without
    this, a valid-JSON but incomplete row is trusted, every gate raises, and the
    kill switch is never consulted again.
    """
    if isinstance(state, (str, bytes, bytearray)):
        try:
            state = json.loads(state)
        except (ValueError, TypeError):
            return _corrupt_state(initial_cash)
    if not isinstance(state, dict) or not REQUIRED_STATE_KEYS <= state.keys():
        return _corrupt_state(initial_cash)
    if not isinstance(state["stopped"], bool) or not isinstance(state["ledger"], list):
        return _corrupt_state(initial_cash)
    if not all(isinstance(state[key], (int, float)) and not isinstance(state[key], bool)
               and math.isfinite(state[key]) for key in NUMERIC_STATE_KEYS):
        return _corrupt_state(initial_cash)
    if state["day"] is not None and not isinstance(state["day"], str):
        return _corrupt_state(initial_cash)
    return state


class PaperTradingStore(Protocol):
    def initialize(self) -> None: ...
    def run(self, decision_id: str, transition: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]: ...
    def set_kill_switch(self, stopped: bool, reason: str) -> None: ...
    def state(self) -> dict[str, Any]: ...


class CockroachPaperTradingStore:
    """CockroachDB is the authoritative state and idempotency store in production."""
    def __init__(self, database_url: str | None = None, initial_cash: float = 100_000.0):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is required for CockroachDB paper trading state")
        if not math.isfinite(initial_cash) or initial_cash <= 0:
            raise ValueError("initial_cash must be finite and positive")
        self.initial_cash = initial_cash
        self.initialize()

    def connect(self):
        return PostgresConnection(self.database_url)

    def initialize(self) -> None:
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS paper_trading_state (
                state_key TEXT PRIMARY KEY, state_json TEXT NOT NULL, updated_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS paper_trading_decisions (
                decision_id TEXT PRIMARY KEY, result_json TEXT NOT NULL, created_at TEXT NOT NULL)""")

    def _locked_state(self, db: Any) -> dict[str, Any]:
        row = db.execute("SELECT state_json FROM paper_trading_state WHERE state_key='primary' FOR UPDATE").fetchone()
        if row is None:
            state = _default_state(self.initial_cash)
            db.execute("INSERT INTO paper_trading_state(state_key,state_json,updated_at) VALUES('primary',?,?)",
                       (canonical_json(state), _now().isoformat()))
            return state
        state = validated_paper_state(row["state_json"], self.initial_cash)
        if state["kill_switch_reason"] == "corrupt_state":
            self._save(db, state)
        return state

    @staticmethod
    def _save(db: Any, state: dict[str, Any]) -> None:
        db.execute("UPDATE paper_trading_state SET state_json=?,updated_at=? WHERE state_key='primary'",
                   (canonical_json(state), _now().isoformat()))

    def run(self, decision_id: str, transition: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
        with self.connect() as db:
            duplicate = db.execute("SELECT result_json FROM paper_trading_decisions WHERE decision_id=?", (decision_id,)).fetchone()
            if duplicate is not None:
                result = json.loads(duplicate["result_json"])
                # See SQLitePaperTradingStore.run: a replay is never a fresh fill.
                result["replayed"] = True
                return result
            state = self._locked_state(db)
            result = transition(state)
            self._save(db, state)
            db.execute("INSERT INTO paper_trading_decisions(decision_id,result_json,created_at) VALUES(?,?,?)",
                       (decision_id, canonical_json(result), _now().isoformat()))
            return result

    def set_kill_switch(self, stopped: bool, reason: str) -> None:
        with self.connect() as db:
            state = self._locked_state(db)
            state["stopped"] = stopped
            state["kill_switch_reason"] = reason
            self._save(db, state)

    def state(self) -> dict[str, Any]:
        with self.connect() as db:
            return self._locked_state(db)


class InMemoryPaperTradingStore:
    """Test double only; production must use :class:`CockroachPaperTradingStore`."""
    def __init__(self, initial_cash: float = 100_000.0):
        self.initial_cash = initial_cash
        self._state: dict[str, Any] | None = None
        self._results: dict[str, dict[str, Any]] = {}

    def initialize(self) -> None:
        return None

    def run(self, decision_id: str, transition: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
        if decision_id in self._results:
            replayed = json.loads(canonical_json(self._results[decision_id]))
            replayed["replayed"] = True
            return replayed
        state = self._load()
        result = transition(state)
        self._state = state
        self._results[decision_id] = result
        return json.loads(canonical_json(result))

    def set_kill_switch(self, stopped: bool, reason: str) -> None:
        state = self._load(); state["stopped"] = stopped; state["kill_switch_reason"] = reason; self._state = state

    def state(self) -> dict[str, Any]:
        return json.loads(canonical_json(self._load()))

    def corrupt_state_for_test(self) -> None:
        self._state = {"invalid": object()}  # serialization failure is treated as corrupt state below

    def _load(self) -> dict[str, Any]:
        if self._state is None:
            self._state = _default_state(self.initial_cash)
        state = validated_paper_state(self._state, self.initial_cash)
        if state is not self._state:
            self._state = state
        return state


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PaperTrading:
    """Applies risk gates and fills accepted decisions into a simulated local ledger."""
    def __init__(self, store: PaperTradingStore, config: PaperRiskConfig | None = None):
        self.store = store
        self.config = config or PaperRiskConfig()
        self.config.validate()
        self.store.initialize()

    def start(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("start reason is required")
        self.store.set_kill_switch(False, reason)

    def stop(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("stop reason is required")
        self.store.set_kill_switch(True, reason)

    def maybe_resume(self, reason: str) -> dict[str, Any]:
        """Resume after an unattended restart only when :func:`restart_policy` allows it.

        A paper lifecycle that is already running resumes as a no-op, and a fresh
        ``missing_state`` account starts. Every other persisted stop (operator stops
        with any reason, corruption, missing credentials, recovery or reconciliation
        failure, risk limits, and broker failures) is preserved across restarts until
        an explicit :meth:`start`.
        """
        if not reason.strip():
            raise ValueError("start reason is required")
        state = self.store.state()
        prior = state.get("kill_switch_reason")
        decision = restart_policy(state)
        if decision == "running":
            return {"resumed": True, "already_running": True, "reason": prior, "kill_switch_reason": prior}
        if decision == "refuse":
            return {"resumed": False, "already_running": False, "reason": prior, "kill_switch_reason": prior,
                    "blocked": True}
        self.store.set_kill_switch(False, reason)
        return {"resumed": True, "already_running": False, "reason": reason, "kill_switch_reason": reason}

    def integrity_check(self) -> str:
        """Quick integrity check for the persisted store; non-local stores report 'ok'."""
        method = getattr(self.store, "integrity_check", None)
        return method() if callable(method) else "ok"

    def state(self) -> dict[str, Any]:
        return self.store.state()

    def summary(self) -> dict[str, Any]:
        """Computed, display-only paper results for the live view."""
        state = self.store.state()
        equity = self._equity(state)
        day_start = float(state.get("day_start_equity") or equity)
        high_water = float(state.get("high_water_equity") or equity)
        position = float(state.get("position", 0.0))
        realized = sum(float(fill.get("realized_pnl") or 0.0) for fill in state.get("ledger", []))
        fills = [dict(fill) for fill in state.get("ledger", [])[-6:]][::-1]
        return {
            "stopped": state.get("stopped") is True,
            "kill_switch_reason": state.get("kill_switch_reason"),
            "cash": float(state.get("cash", 0.0)),
            "position": position,
            "side": "long" if position > 1e-9 else "short" if position < -1e-9 else "flat",
            "average_entry_price": float(state.get("average_entry_price") or 0.0),
            "mark_price": float(state.get("mark_price") or 0.0),
            "equity": equity,
            "day": state.get("day"),
            "day_start_equity": day_start,
            "day_pl": equity - day_start,
            "realized_pl": realized,
            "drawdown_pct": round((high_water - equity) / high_water * 100, 3) if high_water > 0 else 0.0,
            "high_water_equity": high_water,
            "trades_today": int(state.get("trades_today", 0)),
            "market_open": market_is_open(_now()),
            "recent_fills": fills,
        }

    def monitor(self, price: float, observed_at: datetime, now: datetime | None = None) -> dict[str, Any]:
        """Mark fresh observations and persist risk stops without an AI or order call."""
        now = now or _now()
        if not math.isfinite(price) or price <= 0:
            return {"status": "invalid_price"}
        if not market_is_open(now):
            return {"status": "market_closed"}
        if observation_is_future(observed_at, now):
            return {"status": "invalid_observation"}
        if market_data_age_seconds(observed_at, now) > self.config.max_market_data_age_seconds:
            return {"status": "stale_data"}
        def transition(state):
            self._mark(state, price, now)
            equity = self._equity(state)
            breached = (state["day_start_equity"] - equity >= self.config.daily_loss_limit or
                        (state["high_water_equity"] - equity) / state["high_water_equity"] >= self.config.max_drawdown)
            if breached and state["stopped"] is False:
                state["stopped"] = True
                state["kill_switch_reason"] = "risk_limit"
            return {"status": "stopped" if state["stopped"] is True else "ok", "equity": equity,
                    "position": state["position"], "mark_price": price}
        # The monitor is stateful but never places an order. One mark per observation.
        key = "monitor:" + observed_at.isoformat() + ":" + str(price)
        return self.store.run(key, transition)

    def evaluate(self, decision: PaperDecision, now: datetime | None = None) -> dict[str, Any]:
        now = (now or _now()).astimezone(timezone.utc)
        if not decision.decision_id.strip():
            return {"accepted": False, "reason": INVALID_DECISION, "decision_id": decision.decision_id}

        def transition(state: dict[str, Any]) -> dict[str, Any]:
            reason = self._gate(state, decision, now)
            if reason:
                return self._result(False, reason, decision.decision_id, state)
            self._fill(state, decision, now)
            return self._result(True, ACCEPTED, decision.decision_id, state)

        return self.store.run(decision.decision_id, transition)

    def _gate(self, state: dict[str, Any], decision: PaperDecision, now: datetime) -> str | None:
        # ``is True`` rather than truthiness: restart_policy reads this field by
        # identity, so a non-boolean must never mean "running" here. The state
        # validator rejects non-booleans outright; this keeps the two readers
        # consistent if one is ever relaxed.
        if state["stopped"] is not False:
            return KILL_SWITCH
        if (decision.symbol != "XAUUSD" or decision.side not in {"BUY", "SELL"} or
                not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0
                        for value in (decision.quantity, decision.price)) or
                not isinstance(decision.market_data_at, datetime) or decision.market_data_at.tzinfo is None):
            return INVALID_DECISION if decision.symbol == "XAUUSD" else UNSUPPORTED_SYMBOL
        if not market_is_open(now):
            return MARKET_CLOSED
        if observation_is_future(decision.market_data_at, now):
            return STALE_MARKET_DATA
        if market_data_age_seconds(decision.market_data_at, now) > self.config.max_market_data_age_seconds:
            return STALE_MARKET_DATA
        self._mark(state, decision.price, now)
        signed_quantity = decision.quantity if decision.side == "BUY" else -decision.quantity
        if state["trades_today"] >= self.config.max_trades_per_day:
            return MAX_TRADES_PER_DAY
        if abs(state["position"] + signed_quantity) > self.config.max_position:
            return MAX_POSITION
        equity = self._equity(state)
        if state["day_start_equity"] - equity >= self.config.daily_loss_limit:
            return DAILY_LOSS_LIMIT
        if (state["high_water_equity"] - equity) / state["high_water_equity"] >= self.config.max_drawdown:
            return MAX_DRAWDOWN
        return None

    def _mark(self, state: dict[str, Any], price: float, now: datetime) -> None:
        # Order matters. The previous day's close is read from the mark that is
        # still in state, *before* this observation is applied, so a move that
        # straddles the day boundary is measured against yesterday's close
        # instead of being absorbed by the reset.
        day = now.date().isoformat()
        previous_equity = self._equity(state)
        state["mark_price"] = price
        equity = self._equity(state)
        if state["day"] != day:
            state["day"] = day
            state["day_start_equity"] = previous_equity
            state["trades_today"] = 0
        state["high_water_equity"] = max(state["high_water_equity"], equity)

    @staticmethod
    def _equity(state: dict[str, Any]) -> float:
        return state["cash"] + state["position"] * state["mark_price"]

    def _fill(self, state: dict[str, Any], decision: PaperDecision, now: datetime) -> None:
        signed = decision.quantity if decision.side == "BUY" else -decision.quantity
        previous = state["position"]
        average = state["average_entry_price"]
        current = previous + signed
        realized = 0.0
        if previous and previous * signed < 0:
            closed = min(abs(previous), abs(signed))
            realized = closed * (decision.price - average) * (1 if previous > 0 else -1)
        if current == 0:
            next_average = 0.0
        elif previous == 0 or previous * current < 0:
            next_average = decision.price
        elif previous * signed > 0:
            next_average = (abs(previous) * average + abs(signed) * decision.price) / abs(current)
        else:
            next_average = average
        state["cash"] -= signed * decision.price
        state["position"] = current
        state["average_entry_price"] = next_average
        state["trades_today"] += 1
        state["ledger"].append({"decision_id": decision.decision_id, "side": decision.side,
                                "quantity": decision.quantity, "price": decision.price,
                                "realized_pnl": realized, "filled_at": now.isoformat()})
        self._mark(state, decision.price, now)

    def _result(self, accepted: bool, reason: str, decision_id: str, state: dict[str, Any]) -> dict[str, Any]:
        return {"accepted": accepted, "reason": reason, "decision_id": decision_id,
                "position": state["position"], "equity": self._equity(state),
                "trades_today": state["trades_today"]}


def state_backend() -> str:
    backend = (os.getenv("XAUUSD_STATE_BACKEND") or "local").lower()
    if backend not in {"local", "cockroach"}:
        raise ValueError("XAUUSD_STATE_BACKEND must be 'local' or 'cockroach'")
    return backend


def paper_from_env() -> PaperTrading:
    """Single paper-trading entry point shared by the CLI and the live view."""
    initial_cash = _positive_env_float("PAPER_INITIAL_CASH", 100_000.0)
    if state_backend() == "cockroach":
        store: PaperTradingStore = CockroachPaperTradingStore(initial_cash=initial_cash)
    else:
        from .local_state import SQLitePaperTradingStore
        store = SQLitePaperTradingStore(initial_cash=initial_cash)
    return PaperTrading(store, PaperRiskConfig.from_env())
