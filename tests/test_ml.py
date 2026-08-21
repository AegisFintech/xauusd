import pandas as pd
import pytest

from xauusd.core import synthetic_bars
from xauusd.engine import ExecutionConfig
from xauusd.ml import (
    classification_diagnostics, feature_drift, FEATURE_COLUMNS, GradientBoostingResearch,
    MLConfig, supervised_frame,
)
from xauusd.ml_campaign import EnsembleConfig, WalkForwardMLCampaign


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
    assert first["passed"] is False and first["model_card"]["promotion_eligible"] is False
    assert first["model_card"]["fallback"] == "no_trade"
    assert "train_prevalence_baseline" in first["test"] and "feature_drift" in first["test"]


def test_calibration_and_drift_diagnostics_are_deterministic():
    labels=pd.Series([0,0,1,1]); probability=[.1,.2,.8,.9]
    diagnostics=classification_diagnostics(labels,probability,4)
    assert diagnostics["brier_score"] < .05
    assert diagnostics["expected_calibration_error"] == pytest.approx(.15)
    reference=pd.DataFrame({"stable":range(100),"shifted":range(100)})
    observed=pd.DataFrame({"stable":range(100),"shifted":range(100,200)})
    drift=feature_drift(reference,observed,.2)
    assert "shifted" in drift["breached_features"] and "stable" not in drift["breached_features"]


def test_walk_forward_campaign_is_research_only_and_baselined(tmp_path):
    bars=synthetic_bars(800,seed=44)
    campaign=WalkForwardMLCampaign(MLConfig(max_iter=10),EnsembleConfig(
        backends=("hist_gradient_boosting",),regimes=2,folds=2),
        ExecutionConfig(spread=0,slippage=0,commission_per_lot_side=0))
    report=campaign.run(bars,tmp_path)
    assert report["passed"] is False and report["model_card"]["promotion_eligible"] is False
    assert all("train_prevalence_baseline" in fold and "feature_drift" in fold for fold in report["folds"])
