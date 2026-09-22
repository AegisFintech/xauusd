"""Deterministic local-data sources for the demo automation canary."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from typing import Callable

import pandas as pd

from .data import HistoricalDataStore
from .demo_execution import NormalizedDecision
from .demo_runner import MarketData
from .research import StrategySpec, build_features, generate_signal


CONFIRMED_BREAKOUT_SPEC = StrategySpec(
    "confirmed_breakout",
    {"lookback": 30, "range_ratio": 1.5, "min_strength": 0.15, "direction": "both"},
)

# A consumer that samples once per minute against a per-minute bar cadence
# inevitably skips bars. A transition landing on a skipped bar stays actionable
# for this many bars, then is dropped rather than traded late.
DEFAULT_MAX_BACKLOG_BARS = 2


def _normalized_m1_bars(store: HistoricalDataStore) -> pd.DataFrame:
    if store.config.timeframe != "M1":
        raise ValueError("canary source requires an M1 HistoricalDataStore")
    bars = store.read()
    if not isinstance(bars.index, pd.DatetimeIndex) or bars.index.tz is None:
        raise ValueError("canary source requires UTC-indexed bars")
    if bars.index.tz.utcoffset(datetime.now()) != timezone.utc.utcoffset(datetime.now()):
        raise ValueError("canary source requires UTC-indexed bars")
    return store.normalize(bars)


class LocalHistoricalMarketDataSource:
    """Expose the final persisted, normalized M1 bar as a market observation."""

    def __init__(self, store: HistoricalDataStore):
        self.store = store

    def read(self) -> MarketData:
        bars = _normalized_m1_bars(self.store)
        if bars.empty:
            raise ValueError("canary source requires at least one bar")
        final_bar = bars.iloc[-1]
        return MarketData(float(final_bar.close), bars.index[-1].to_pydatetime())


@dataclass(frozen=True)
class ConfirmedBreakoutCanaryConfig:
    quantity: float
    strategy: StrategySpec = CONFIRMED_BREAKOUT_SPEC
    max_backlog_bars: int = DEFAULT_MAX_BACKLOG_BARS

    def validate(self) -> None:
        if (not isinstance(self.quantity, (int, float)) or isinstance(self.quantity, bool) or
                not math.isfinite(self.quantity) or self.quantity <= 0):
            raise ValueError("quantity must be finite and positive")
        if self.strategy != CONFIRMED_BREAKOUT_SPEC:
            raise ValueError("canary strategy must use the confirmed breakout specification")
        if (not isinstance(self.max_backlog_bars, int) or isinstance(self.max_backlog_bars, bool) or
                self.max_backlog_bars < 1):
            raise ValueError("max_backlog_bars must be a positive integer")


class ConfirmedBreakoutCanarySource:
    """Emit each new confirmed-breakout transition from closed local M1 bars once."""

    def __init__(self, store: HistoricalDataStore, quantity: float,
                 signal_generator: Callable[[pd.DataFrame, StrategySpec], pd.Series] = generate_signal):
        self.store = store
        self.config = ConfirmedBreakoutCanaryConfig(quantity)
        self.config.validate()
        self.signal_generator = signal_generator
        self.last_observed_bar_time: datetime | None = None

    def read(self, market_data: MarketData) -> NormalizedDecision | None:
        # Persisted historical bars are closed bars; the runner independently rejects stale observations.
        bars = _normalized_m1_bars(self.store)
        if bars.empty:
            return None
        features = build_features(bars)
        if features.empty:
            return None
        signals = self.signal_generator(features, self.config.strategy)
        if signals.empty:
            return None
        values = signals.astype(int)
        if not set(values.unique()) <= {-1, 0, 1}:
            raise ValueError("signal generator must return -1, 0, or 1")
        pending = self._pending_transition(values)
        self.last_observed_bar_time = values.index[-1].to_pydatetime()
        if pending is None:
            return None
        transition_time, signal = pending
        side = "BUY" if signal == 1 else "SELL"
        return NormalizedDecision(
            self._decision_id(transition_time, side), self.store.config.symbol, side,
            float(self.config.quantity), transition_time,
        )

    def _pending_transition(self, values: pd.Series) -> tuple[datetime, int] | None:
        """Most recent transition among the bars not yet observed, or None.

        Inspecting only the newest bar loses any transition that lands on a bar
        the consumer skipped: the following bar reads as "no change", so the
        signal never surfaces again. Scanning the unobserved window recovers it,
        bounded by max_backlog_bars so a signal too old to act on is dropped
        rather than traded late. A cold start deliberately considers only the
        newest bar, so a restart cannot resurrect an old breakout as a fresh
        entry.
        """
        previous = values.shift(1).fillna(0).astype(int)
        transitions = values[(values != 0) & (values != previous)]
        if transitions.empty:
            return None
        if self.last_observed_bar_time is None:
            if transitions.index[-1] != values.index[-1]:
                return None
        else:
            window = values[values.index > self.last_observed_bar_time]
            if window.empty:
                return None
            oldest_actionable = window.iloc[-self.config.max_backlog_bars:].index[0]
            transitions = transitions[transitions.index >= oldest_actionable]
            if transitions.empty:
                return None
        return transitions.index[-1].to_pydatetime(), int(transitions.iloc[-1])

    def _decision_id(self, transition_time: datetime, side: str) -> str:
        payload = {
            "strategy": asdict(self.config.strategy),
            "transition_bar_time": transition_time.astimezone(timezone.utc).isoformat(),
            "side": side,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
