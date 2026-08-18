import pandas as pd
import pytest

from xauusd.core import synthetic_bars
from xauusd.portfolio_research import classify_regimes,equity_metrics
from xauusd.research import build_features


def test_regime_labels_are_causal_and_complete():
 bars=synthetic_bars(1500,seed=121); earlier=build_features(bars.iloc[:1200]); full=build_features(bars)
 left=classify_regimes(earlier); right=classify_regimes(full.loc[earlier.index])
 pd.testing.assert_series_equal(left,right)
 assert not left.isna().any() and all(label.count("|")==2 for label in left)


def test_equity_metrics_measure_portfolio_drawdown():
 index=pd.date_range("2026-01-01",periods=4,freq="min",tz="UTC")
 metrics=equity_metrics(pd.Series([100.,110.,99.,120.],index=index))
 assert metrics["net_profit"]==20 and metrics["max_drawdown"]==pytest.approx(-0.1)
