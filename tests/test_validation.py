import pandas as pd
import pytest

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
    assert first["method"] == "circular_moving_block" and first["block_length"] == 4
    assert first["units"] == "account_currency"
    assert first["p95_drawdown_loss_currency"] == -first["p05_drawdown_currency"]
    assert first["p95_max_drawdown"] == first["p05_drawdown_currency"]


def test_block_bootstrap_preserves_clustered_sequence_effect():
    clustered = pd.Series([2.] * 10 + [-2.] * 10)
    iid = bootstrap_trade_paths(clustered, 1000, 11, block_length=1)
    blocked = bootstrap_trade_paths(clustered, 1000, 11, block_length=5)
    assert blocked["p95_drawdown_loss_currency"] > iid["p95_drawdown_loss_currency"]


def test_bootstrap_rejects_invalid_configuration():
    import pytest
    with pytest.raises(ValueError):
        bootstrap_trade_paths(pd.Series([1.]), block_length=0)


def test_validator_writes_report_and_does_not_promote_weak_strategy(tmp_path):
    execution = ExecutionConfig(spread=.2, slippage=.03, commission_per_lot_side=3.5)
    config = ValidationConfig(walk_forward_folds=2, bootstrap_samples=20, minimum_trades=1)
    spec = StrategySpec("momentum", {"fast": 8, "slow": 34, "threshold_atr": .1})
    report = StrategyValidator(execution, config).validate(synthetic_bars(500, seed=23), spec, tmp_path)
    assert (tmp_path / "momentum.json").exists()
    assert set(report["splits"]) == {"train", "validation", "test"}
    assert report["passed"] == all(report["gates"].values())


def test_validator_fails_a_strategy_that_loses_money(tmp_path):
    """The negative path was never asserted, which is why several real defects survived.

    The only prior assertion was `passed == all(gates.values())`, a tautology. A
    gate that could never fail, a threshold comparison that inverts, or a metric
    that is None on a losing strategy would all still satisfy it. A strategy with
    an absurdly high entry threshold trades nothing and must not pass.
    """
    execution = ExecutionConfig(spread=.2, slippage=.03, commission_per_lot_side=3.5)
    config = ValidationConfig(walk_forward_folds=2, bootstrap_samples=20, minimum_trades=1)
    # A threshold no bar can clear: no trades, so no expectancy and no profit factor.
    inert = StrategySpec("momentum", {"fast": 8, "slow": 34, "threshold_atr": 1e9})
    report = StrategyValidator(execution, config).validate(synthetic_bars(500, seed=23), inert, tmp_path)

    assert report["passed"] is False
    assert report["gates"]["minimum_trades"] is False
    assert report["gates"]["positive_expectancy"] is False
    assert report["gates"]["profit_factor"] is False
    # Every failure must name itself, so a report is auditable.
    assert [name for name, ok in report["gates"].items() if not ok]


def test_validator_embargo_purges_the_training_tail(tmp_path):
    """A 30-bar rolling feature reaches across the split boundary.

    The last `embargo_bars` rows of a training window encode the first rows of
    the window that follows it, so they are purged before any fold is scored.
    """
    frame = build_features(synthetic_bars(500, seed=22))
    plain = walk_forward_splits(frame, 4, embargo=0)
    purged = walk_forward_splits(frame, 4, embargo=32)

    assert all(len(purged[i][0]) == len(plain[i][0]) - 32 for i in range(4))
    for (train, test), (purged_train, purged_test) in zip(plain, purged):
        # Ordering still holds, and the evaluation window is untouched.
        assert purged_train.index.max() < purged_test.index.min()
        assert test.equals(purged_test)
    assert purged[0][0].index.max() < plain[0][0].index.max()


def test_walk_forward_refuses_an_embargo_larger_than_a_fold_block():
    """An empty training window must fail loudly, not look like a negative result."""
    frame = build_features(synthetic_bars(120, seed=5))
    with pytest.raises(ValueError, match="embargo"):
        walk_forward_splits(frame, 4, embargo=32)
    # A proportionate embargo is accepted and still orders the windows correctly.
    folds = walk_forward_splits(frame, 4, embargo=8)
    for train, test in folds:
        assert len(train) > 0 and len(test) > 0
        assert train.index.max() < test.index.min()


def test_validator_applies_the_embargo_to_its_own_folds(tmp_path):
    """The embargo must reach the report, not just the helper.

    `walk_forward_splits` was callable with an embargo while `validate()` did not
    pass one, so every fold the gates actually scored still ran on a training
    window whose tail reached into the evaluation window.
    """
    bars = synthetic_bars(2000, seed=31)
    execution = ExecutionConfig()

    plain = StrategyValidator(execution, ValidationConfig(
        walk_forward_folds=2, bootstrap_samples=10, minimum_trades=1, embargo_bars=0,
    )).validate(bars, StrategySpec("momentum", {"fast": 8, "slow": 34, "threshold_atr": .1}),
                tmp_path / "plain")
    purged = StrategyValidator(execution, ValidationConfig(
        walk_forward_folds=2, bootstrap_samples=10, minimum_trades=1, embargo_bars=32,
    )).validate(bars, StrategySpec("momentum", {"fast": 8, "slow": 34, "threshold_atr": .1}),
                tmp_path / "purged")

    for left, right in zip(plain["walk_forward"], purged["walk_forward"]):
        # Identical evaluation windows, strictly shorter training windows.
        assert left["test_start"] == right["test_start"]
        assert pd.Timestamp(right["train_end"]) < pd.Timestamp(left["train_end"])
