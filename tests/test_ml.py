import pandas as pd

from xauusd.core import synthetic_bars
from xauusd.engine import ExecutionConfig
from xauusd.ml import FEATURE_COLUMNS, GradientBoostingResearch, MLConfig, supervised_frame


def test_supervised_features_are_causal_and_labels_use_future():
    bars = synthetic_bars(400, seed=41)
    x, y, future_return = supervised_frame(bars, MLConfig(prediction_horizon=5))
    timestamp = x.index[100]
    expected = bars.close.shift(-5).loc[timestamp] / bars.close.loc[timestamp] - 1
    assert future_return.loc[timestamp] == expected
    assert y.loc[timestamp] == int(expected > 0)
    assert tuple(x.columns) == FEATURE_COLUMNS


def test_appending_future_does_not_change_existing_ml_features():
    bars = synthetic_bars(500, seed=42)
    early_x, _, _ = supervised_frame(bars.iloc[:350], MLConfig())
    full_x, _, _ = supervised_frame(bars, MLConfig())
    pd.testing.assert_frame_equal(early_x, full_x.loc[early_x.index])


def test_gradient_boosting_report_is_reproducible(tmp_path):
    bars = synthetic_bars(1000, seed=43)
    execution = ExecutionConfig(spread=0, slippage=0, commission_per_lot_side=0)
    research = GradientBoostingResearch(MLConfig(max_iter=20), execution)
    first = research.run(bars, tmp_path)
    second = research.run(bars, tmp_path)
    assert first == second
    assert first["train"]["end"] < first["validation"]["start"]
    assert first["validation"]["end"] < first["test"]["start"]
