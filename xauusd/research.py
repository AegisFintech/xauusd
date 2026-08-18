from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .engine import EventDrivenBacktester, ExecutionConfig


@dataclass(frozen=True)
class StrategySpec:
    name: str
    parameters: dict[str, float | int | str]


DEFAULT_STRATEGIES = (
    StrategySpec("mean_reversion", {"entry_z": 1.5, "exit_z": 0.25}),
    StrategySpec("momentum", {"fast": 8, "slow": 34, "threshold_atr": 0.10}),
    StrategySpec("breakout", {"lookback": 30}),
    StrategySpec("micro_trend", {"fast": 5, "slow": 20, "min_strength": 0.15}),
    StrategySpec("volatility_expansion", {"range_ratio": 1.5, "body_fraction": 0.55}),
    StrategySpec("session_momentum", {"start_hour": 7, "end_hour": 17}),
    StrategySpec("regime_switch", {"trend_threshold": 0.35, "entry_z": 1.25}),
)


def build_features(bars: pd.DataFrame) -> pd.DataFrame:
    """Build causal M1 price/volume features without backward filling."""
    x = bars.sort_index().copy()
    close = x.close.astype(float)
    high, low, open_ = x.high.astype(float), x.low.astype(float), x.open.astype(float)
    previous_close = close.shift(1)
    true_range = pd.concat((high - low, (high - previous_close).abs(), (low - previous_close).abs()), axis=1).max(axis=1)
    x["return_1"] = close.pct_change()
    x["return_5"] = close.pct_change(5)
    x["return_15"] = close.pct_change(15)
    x["atr_14"] = true_range.rolling(14, min_periods=14).mean()
    x["range_ratio"] = (high - low) / true_range.rolling(30, min_periods=30).mean().replace(0, np.nan)
    x["body_fraction"] = (close - open_).abs() / (high - low).replace(0, np.nan)
    x["direction"] = np.sign(close - open_)
    for window in (5, 8, 20, 34, 50):
        x[f"ema_{window}"] = close.ewm(span=window, adjust=False, min_periods=window).mean()
    mean = close.rolling(20, min_periods=20).mean()
    std = close.rolling(20, min_periods=20).std()
    x["zscore_20"] = (close - mean) / std.replace(0, np.nan)
    x["channel_high_30"] = high.rolling(30, min_periods=30).max().shift(1)
    x["channel_low_30"] = low.rolling(30, min_periods=30).min().shift(1)
    x["trend_strength"] = (x.ema_8 - x.ema_34).abs() / x.atr_14.replace(0, np.nan)
    x["hour_utc"] = x.index.hour
    return x.replace([np.inf, -np.inf], np.nan).dropna()


def _hold_until_exit(entry_long: pd.Series, entry_short: pd.Series, exit_mask: pd.Series) -> pd.Series:
    state = 0
    values = []
    for long_entry, short_entry, exit_now in zip(entry_long, entry_short, exit_mask):
        if exit_now:
            state = 0
        if long_entry:
            state = 1
        elif short_entry:
            state = -1
        values.append(state)
    return pd.Series(values, index=entry_long.index, dtype=int)


def generate_signal(features: pd.DataFrame, spec: StrategySpec) -> pd.Series:
    p, f = spec.parameters, features
    def ema(window): return f.close.ewm(span=int(window),adjust=False,min_periods=int(window)).mean()
    def directional(signal):
        mode=p.get("direction","both")
        return signal.clip(lower=0) if mode=="long" else signal.clip(upper=0) if mode=="short" else signal
    if spec.name == "mean_reversion":
        window=int(p.get("window",20)); mean=f.close.rolling(window).mean(); std=f.close.rolling(window).std(); z=(f.close-mean)/std
        return directional(_hold_until_exit(z < -float(p["entry_z"]), z > float(p["entry_z"]),z.abs() < float(p["exit_z"])))
    if spec.name == "momentum":
        edge = (ema(p["fast"]) - ema(p["slow"])) / f.atr_14
        threshold = float(p["threshold_atr"])
        return directional(pd.Series(np.where(edge > threshold, 1, np.where(edge < -threshold, -1, 0)), index=f.index))
    if spec.name == "breakout":
        lookback=int(p["lookback"]); high=f.high.rolling(lookback).max().shift(1); low=f.low.rolling(lookback).min().shift(1); mid=ema(p.get("exit_ema",20))
        return directional(_hold_until_exit(f.close > high, f.close < low,(f.close < mid) & (f.close > mid.shift(1))))
    if spec.name == "micro_trend":
        strength = (ema(p["fast"]) - ema(p["slow"])) / f.atr_14
        minimum = float(p["min_strength"])
        return directional(pd.Series(np.where(strength > minimum, 1, np.where(strength < -minimum, -1, 0)), index=f.index))
    if spec.name == "volatility_expansion":
        active = (f.range_ratio >= float(p["range_ratio"])) & (f.body_fraction >= float(p["body_fraction"]))
        return directional((f.direction.where(active, 0)).astype(int))
    if spec.name == "session_momentum":
        active = (f.hour_utc >= int(p["start_hour"])) & (f.hour_utc < int(p["end_hour"]))
        period=int(p.get("return_period",15)); returns=f.close.pct_change(period)
        return directional(pd.Series(np.where(active, np.sign(returns), 0), index=f.index, dtype=int))
    if spec.name == "regime_switch":
        trending = f.trend_strength >= float(p["trend_threshold"])
        trend_signal = np.sign(f.ema_8 - f.ema_34)
        revert_signal = np.where(f.zscore_20 < -float(p["entry_z"]), 1,
                                 np.where(f.zscore_20 > float(p["entry_z"]), -1, 0))
        return pd.Series(np.where(trending, trend_signal, revert_signal), index=f.index, dtype=int)
    raise ValueError(f"unknown strategy: {spec.name}")


class ResearchCampaign:
    def __init__(self, execution: ExecutionConfig | None = None):
        self.execution = execution or ExecutionConfig()

    def run(self, bars: pd.DataFrame, specs=DEFAULT_STRATEGIES, output_dir: Path = Path("reports/research")) -> list[dict]:
        features = build_features(bars)
        if features.empty:
            raise ValueError("not enough bars to build research features")
        output_dir.mkdir(parents=True, exist_ok=True)
        leaderboard = []
        for spec in specs:
            result = EventDrivenBacktester(self.execution).run(features, generate_signal(features, spec))
            metrics = result["metrics"]
            score = metrics["sharpe"] + 0.25 * min(metrics["profit_factor"], 3) + 5 * metrics["max_drawdown"]
            summary = {"strategy": spec.name, "parameters": spec.parameters, "score": float(score), **metrics}
            leaderboard.append(summary)
            result["trades"].to_csv(output_dir / f"{spec.name}_trades.csv", index=False)
            result["equity"].to_frame().to_parquet(output_dir / f"{spec.name}_equity.parquet")
        leaderboard.sort(key=lambda row: row["score"], reverse=True)
        manifest = {"start": features.index.min().isoformat(), "end": features.index.max().isoformat(),
                    "bars": len(features), "execution": asdict(self.execution), "strategies": leaderboard}
        (output_dir / "leaderboard.json").write_text(json.dumps(manifest, indent=2, allow_nan=False))
        return leaderboard
