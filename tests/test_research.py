import numpy as np
import pandas as pd

from xauusd.core import synthetic_bars
from xauusd.engine import ExecutionConfig
from xauusd.research import DEFAULT_STRATEGIES, ResearchCampaign, build_features, generate_signal


def test_features_do_not_change_when_future_bars_are_appended():
    bars = synthetic_bars(300, seed=11)
    earlier = build_features(bars.iloc[:200])
    full = build_features(bars)
    pd.testing.assert_frame_equal(earlier, full.loc[earlier.index])


def test_all_baseline_signals_are_aligned_and_bounded():
    features = build_features(synthetic_bars(500, seed=5))
    for spec in DEFAULT_STRATEGIES:
        signal = generate_signal(features, spec)
        assert signal.index.equals(features.index)
        assert not signal.isna().any()
        assert set(np.unique(signal)).issubset({-1, 0, 1})


def test_breakout_channel_excludes_current_bar():
    bars = synthetic_bars(100, seed=3)
    features = build_features(bars)
    timestamp = features.index[-1]
    expected = bars.high.loc[:timestamp].iloc[-31:-1].max()
    assert features.loc[timestamp, "channel_high_30"] == expected


def test_campaign_writes_reproducible_manifest(tmp_path):
    specs = DEFAULT_STRATEGIES[:2]
    execution = ExecutionConfig(spread=0, slippage=0, commission_per_lot_side=0)
    first = ResearchCampaign(execution).run(synthetic_bars(300, seed=19), specs, tmp_path)
    second = ResearchCampaign(execution).run(synthetic_bars(300, seed=19), specs, tmp_path)
    assert first == second
    assert (tmp_path / "leaderboard.json").exists()
    assert {row["strategy"] for row in first} == {spec.name for spec in specs}
