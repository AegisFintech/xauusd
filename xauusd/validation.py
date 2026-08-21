from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .engine import EventDrivenBacktester, ExecutionConfig
from .research import StrategySpec, build_features, generate_signal


@dataclass(frozen=True)
class ValidationConfig:
    train_fraction: float = 0.60
    validation_fraction: float = 0.20
    walk_forward_folds: int = 4
    minimum_trades: int = 100
    maximum_drawdown: float = -0.20
    minimum_profit_factor: float = 1.0
    minimum_positive_folds: float = 0.60
    minimum_stable_neighbors: float = 0.50
    bootstrap_samples: int = 500
    bootstrap_seed: int = 17
    bootstrap_block_length: int = 5

    def __post_init__(self) -> None:
        if not 0 < self.train_fraction < 1 or not 0 < self.validation_fraction < 1:
            raise ValueError("split fractions must be between zero and one")
        if self.train_fraction + self.validation_fraction >= 1:
            raise ValueError("train and validation fractions must leave a test set")
        if self.walk_forward_folds < 2 or self.bootstrap_samples < 1 or self.bootstrap_block_length < 1:
            raise ValueError("at least two folds and one bootstrap sample are required")


def chronological_split(frame: pd.DataFrame, config: ValidationConfig) -> dict[str, pd.DataFrame]:
    n = len(frame)
    train_end = int(n * config.train_fraction)
    validation_end = train_end + int(n * config.validation_fraction)
    if train_end < 2 or validation_end >= n:
        raise ValueError("not enough rows for chronological train/validation/test split")
    return {"train": frame.iloc[:train_end], "validation": frame.iloc[train_end:validation_end], "test": frame.iloc[validation_end:]}


def walk_forward_splits(frame: pd.DataFrame, folds: int) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """Anchored training windows followed by non-overlapping test windows."""
    block = len(frame) // (folds + 1)
    if block < 2:
        raise ValueError("not enough rows for requested walk-forward folds")
    result = []
    for fold in range(folds):
        train_end = block * (fold + 1)
        test_end = block * (fold + 2) if fold < folds - 1 else len(frame)
        result.append((frame.iloc[:train_end], frame.iloc[train_end:test_end]))
    return result


def parameter_neighbors(spec: StrategySpec) -> list[StrategySpec]:
    """Create one-at-a-time ±20% numeric perturbations around a baseline."""
    neighbors = []
    for key, value in spec.parameters.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value == 0:
            continue
        for multiplier in (0.8, 1.2):
            parameters = dict(spec.parameters)
            adjusted = value * multiplier
            parameters[key] = max(1, int(round(adjusted))) if isinstance(value, int) else float(adjusted)
            if parameters != spec.parameters:
                neighbors.append(StrategySpec(spec.name, parameters))
    return neighbors


def bootstrap_trade_paths(pnl: pd.Series, samples: int = 500, seed: int = 17,
                          block_length: int = 5) -> dict:
    """Moving-block bootstrap preserving short-run trade P&L dependence."""
    if samples < 1 or block_length < 1:
        raise ValueError("samples and block length must be positive")
    if pnl.empty:
        return {"method": "circular_moving_block", "samples": samples, "seed": seed,
                "block_length": block_length, "units": "account_currency",
                "loss_probability": 1.0, "median_net_pnl": 0.0, "p05_net_pnl": 0.0,
                "p05_drawdown_currency": 0.0, "p95_drawdown_loss_currency": 0.0,
                "p95_max_drawdown": 0.0}
    values = pnl.to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    totals, drawdowns = [], []
    effective_block = min(block_length, len(values))
    blocks_per_path = int(np.ceil(len(values) / effective_block))
    offsets = np.arange(effective_block)
    for _ in range(samples):
        starts = rng.integers(0, len(values), size=blocks_per_path)
        indices = ((starts[:, None] + offsets) % len(values)).reshape(-1)[:len(values)]
        path = values[indices].cumsum()
        totals.append(path[-1])
        drawdowns.append(float((path - np.maximum.accumulate(np.r_[0.0, path])[-len(path):]).min()))
    p05_drawdown = float(np.quantile(drawdowns, .05))
    return {"method": "circular_moving_block", "samples": samples, "seed": seed,
            "block_length": effective_block, "units": "account_currency",
            "loss_probability": float(np.mean(np.asarray(totals) <= 0)),
            "median_net_pnl": float(np.median(totals)), "p05_net_pnl": float(np.quantile(totals, .05)),
            "p05_drawdown_currency": p05_drawdown,
            "p95_drawdown_loss_currency": -p05_drawdown,
            "p95_max_drawdown": p05_drawdown}


class StrategyValidator:
    def __init__(self, execution: ExecutionConfig | None = None, config: ValidationConfig | None = None):
        self.execution = execution or ExecutionConfig()
        self.config = config or ValidationConfig()

    def _run(self, frame: pd.DataFrame, spec: StrategySpec) -> dict:
        return EventDrivenBacktester(self.execution).run(frame, generate_signal(frame, spec))

    def validate(self, bars: pd.DataFrame, spec: StrategySpec, output_dir: Path = Path("reports/validation")) -> dict:
        features = build_features(bars)
        splits = chronological_split(features, self.config)
        split_results = {name: self._run(part, spec) for name, part in splits.items()}
        folds = []
        for number, (train, test) in enumerate(walk_forward_splits(features, self.config.walk_forward_folds), 1):
            result = self._run(test, spec)
            folds.append({"fold": number, "train_start": train.index.min().isoformat(),
                          "train_end": train.index.max().isoformat(), "test_start": test.index.min().isoformat(),
                          "test_end": test.index.max().isoformat(), **result["metrics"]})
        neighbors = []
        for candidate in parameter_neighbors(spec):
            metrics = self._run(splits["validation"], candidate)["metrics"]
            neighbors.append({"parameters": candidate.parameters, **metrics})
        test_result = split_results["test"]
        bootstrap = bootstrap_trade_paths(test_result["trades"].net_pnl if not test_result["trades"].empty else pd.Series(dtype=float),
                                          self.config.bootstrap_samples, self.config.bootstrap_seed,
                                          self.config.bootstrap_block_length)
        positive_folds = float(np.mean([fold["net_profit"] > 0 for fold in folds]))
        stable_neighbors = float(np.mean([row["net_profit"] > 0 for row in neighbors])) if neighbors else 0.0
        test = test_result["metrics"]
        gates = {
            "minimum_trades": test["trades"] >= self.config.minimum_trades,
            "maximum_drawdown": test["max_drawdown"] >= self.config.maximum_drawdown,
            "positive_expectancy": test["expectancy"] > 0,
            "profit_factor": test["profit_factor"] >= self.config.minimum_profit_factor,
            "walk_forward_consistency": positive_folds >= self.config.minimum_positive_folds,
            "parameter_stability": stable_neighbors >= self.config.minimum_stable_neighbors,
            "bootstrap_p05_positive": bootstrap["p05_net_pnl"] > 0,
        }
        report = {
            "strategy": spec.name, "parameters": spec.parameters, "config": asdict(self.config),
            "execution": asdict(self.execution),
            "splits": {name: {"start": splits[name].index.min().isoformat(), "end": splits[name].index.max().isoformat(),
                              **result["metrics"]} for name, result in split_results.items()},
            "walk_forward": folds, "positive_fold_fraction": positive_folds,
            "sensitivity": neighbors, "stable_neighbor_fraction": stable_neighbors,
            "bootstrap": bootstrap, "gates": gates, "passed": all(gates.values()),
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / f"{spec.name}.json").write_text(json.dumps(report, indent=2, allow_nan=False))
        return report
