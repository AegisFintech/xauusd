import pandas as pd

from xauusd.core import synthetic_bars
from xauusd.engine import ExecutionConfig
from xauusd.research import StrategySpec, build_features
from xauusd.validation import (StrategyValidator, ValidationConfig, bootstrap_trade_paths,
                               chronological_split, parameter_neighbors, walk_forward_splits)


def test_chronological_splits_are_ordered_and_disjoint():
    frame = build_features(synthetic_bars(500, seed=21))
    parts = chronological_split(frame, ValidationConfig())
    assert parts["train"].index.max() < parts["validation"].index.min()
    assert parts["validation"].index.max() < parts["test"].index.min()
    assert sum(map(len, parts.values())) == len(frame)


def test_walk_forward_never_trains_on_future():
    frame = build_features(synthetic_bars(500, seed=22))
    folds = walk_forward_splits(frame, 4)
    assert all(train.index.max() < test.index.min() for train, test in folds)
    assert all(folds[i][1].index.max() < folds[i + 1][1].index.min() for i in range(len(folds) - 1))


def test_parameter_neighbors_change_one_value():
    spec = StrategySpec("mean_reversion", {"entry_z": 1.5, "exit_z": .25})
    candidates = parameter_neighbors(spec)
    assert len(candidates) == 4
    assert all(sum(a != b for a, b in zip(spec.parameters.values(), c.parameters.values())) == 1 for c in candidates)


def test_bootstrap_is_seeded_and_reports_loss_probability():
    pnl = pd.Series([1.0, -0.5, 2.0, -0.25])
    first = bootstrap_trade_paths(pnl, 100, 9)
    assert first == bootstrap_trade_paths(pnl, 100, 9)
    assert 0 <= first["loss_probability"] <= 1


def test_validator_writes_report_and_does_not_promote_weak_strategy(tmp_path):
    execution = ExecutionConfig(spread=.2, slippage=.03, commission_per_lot_side=3.5)
    config = ValidationConfig(walk_forward_folds=2, bootstrap_samples=20, minimum_trades=1)
    spec = StrategySpec("momentum", {"fast": 8, "slow": 34, "threshold_atr": .1})
    report = StrategyValidator(execution, config).validate(synthetic_bars(500, seed=23), spec, tmp_path)
    assert (tmp_path / "momentum.json").exists()
    assert set(report["splits"]) == {"train", "validation", "test"}
    assert report["passed"] == all(report["gates"].values())
