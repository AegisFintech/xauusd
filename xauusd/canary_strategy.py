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

    def validate(self) -> None:
        if (not isinstance(self.quantity, (int, float)) or isinstance(self.quantity, bool) or
                not math.isfinite(self.quantity) or self.quantity <= 0):
            raise ValueError("quantity must be finite and positive")
        if self.strategy != CONFIRMED_BREAKOUT_SPEC:
            raise ValueError("canary strategy must use the confirmed breakout specification")


class ConfirmedBreakoutCanarySource:
    """Emit only new confirmed-breakout transitions from closed local M1 bars."""

    def __init__(self, store: HistoricalDataStore, quantity: float,
                 signal_generator: Callable[[pd.DataFrame, StrategySpec], pd.Series] = generate_signal):
        self.store = store
        self.config = ConfirmedBreakoutCanaryConfig(quantity)
        self.config.validate()
        self.signal_generator = signal_generator
        self.last_emitted_bar_time: datetime | None = None

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
        signal = int(signals.iloc[-1])
        previous_signal = int(signals.iloc[-2]) if len(signals) > 1 else 0
        if signal not in {-1, 0, 1} or previous_signal not in {-1, 0, 1}:
            raise ValueError("signal generator must return -1, 0, or 1")
        final_time = features.index[-1].to_pydatetime()
        if (signal == 0 or signal == previous_signal or
                final_time == self.last_emitted_bar_time):
            return None
        self.last_emitted_bar_time = final_time
        side = "BUY" if signal == 1 else "SELL"
        return NormalizedDecision(
            self._decision_id(final_time, side), self.store.config.symbol, side,
            float(self.config.quantity), final_time,
        )

    def _decision_id(self, final_time: datetime, side: str) -> str:
        payload = {
            "strategy": asdict(self.config.strategy),
            "final_bar_time": final_time.astimezone(timezone.utc).isoformat(),
            "side": side,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
