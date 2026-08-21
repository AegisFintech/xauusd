import pandas as pd
import pytest
import numpy as np

from xauusd.engine import EventDrivenBacktester, ExecutionConfig


def bars(rows):
    index = pd.date_range("2025-01-01", periods=len(rows), freq="min", tz="UTC")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=index)


def no_costs(**kwargs):
    return ExecutionConfig(spread=0, slippage=0, commission_per_lot_side=0, **kwargs)


def test_signal_executes_at_next_open_without_lookahead():
    frame = bars([(100, 100, 100, 100), (110, 112, 109, 111), (111, 111, 111, 111)])
    signal = pd.Series([1, 0, 0], index=frame.index)
    result = EventDrivenBacktester(no_costs(stop_distance=None, target_distance=None)).run(frame, signal)
    trade = result["trades"].iloc[0]
    assert trade.entry_price == 110
    assert trade.exit_price == 111
    assert trade.net_pnl == 1


def test_spread_slippage_and_commission_are_charged_both_sides():
    frame = bars([(100, 100, 100, 100), (100, 100, 100, 100), (100, 100, 100, 100)])
    signal = pd.Series([1, 0, 0], index=frame.index)
    config = ExecutionConfig(quantity_oz=100, spread=.20, slippage=.05, commission_per_lot_side=3.5,
                             stop_distance=None, target_distance=None)
    result = EventDrivenBacktester(config).run(frame, signal)
    trade = result["trades"].iloc[0]
    assert trade.gross_pnl == pytest.approx(-30)
    assert trade.commission == 7
    assert trade.net_pnl == pytest.approx(-37)
    metrics = result["metrics"]
    assert metrics["gross_profit"] == pytest.approx(0)
    assert metrics["implicit_execution_cost"] == pytest.approx(30)
    assert metrics["commission_cost"] == pytest.approx(7)
    assert metrics["total_cost"] == pytest.approx(37)
    assert metrics["turnover"] == pytest.approx(20_000)
    assert metrics["expected_shortfall"] == pytest.approx(-37)
    assert metrics["profit_concentration"] == 0


def test_compact_attribution_metrics_reconcile_and_measure_concentration():
    frame = bars([(100, 100, 100, 100), (100, 102, 99, 101), (101, 102, 100, 102),
                  (102, 103, 101, 103), (103, 103, 103, 103)])
    signal = pd.Series([1, 0, 1, 0, 0], index=frame.index)
    result = EventDrivenBacktester(no_costs(stop_distance=None, target_distance=None)).run(frame, signal)
    metrics = result["metrics"]
    assert metrics["gross_profit"] == pytest.approx(metrics["net_profit"] + metrics["total_cost"])
    assert metrics["turnover"] > 0
    assert 0 <= metrics["profit_concentration"] <= 1


def test_stop_wins_ambiguous_intrabar_path():
    frame = bars([(100, 100, 100, 100), (100, 103, 97, 100), (100, 100, 100, 100)])
    signal = pd.Series([1, 1, 0], index=frame.index)
    config = no_costs(stop_distance=2, target_distance=2, intrabar_priority="stop")
    trade = EventDrivenBacktester(config).run(frame, signal)["trades"].iloc[0]
    assert trade.exit_reason == "stop"
    assert trade.net_pnl == -2


def test_time_exit():
    frame = bars([(100, 100, 100, 100), (100, 101, 99, 100), (100, 101, 99, 101)])
    signal = pd.Series([1, 1, 1], index=frame.index)
    config = no_costs(stop_distance=None, target_distance=None, max_holding_bars=2)
    trade = EventDrivenBacktester(config).run(frame, signal)["trades"].iloc[0]
    assert trade.exit_reason == "time"
    assert trade.bars_held == 2


def test_array_loop_is_deterministic_on_randomized_path():
 rng=np.random.default_rng(91); rows=5000; close=2000+np.cumsum(rng.normal(0,.8,rows))
 frame=pd.DataFrame({"open":close+rng.normal(0,.1,rows),"high":close+rng.uniform(.1,2,rows),
                     "low":close-rng.uniform(.1,2,rows),"close":close},
                    index=pd.date_range("2025-01-01",periods=rows,freq="min",tz="UTC"))
 signal=pd.Series(rng.integers(-1,2,rows),index=frame.index)
 config=ExecutionConfig(quantity_oz=3,spread=.23,slippage=.04,commission_per_lot_side=3.7,
                        stop_distance=1.7,target_distance=2.4,max_holding_bars=17)
 first=EventDrivenBacktester(config).run(frame,signal); second=EventDrivenBacktester(config).run(frame,signal)
 pd.testing.assert_frame_equal(first["trades"],second["trades"],check_exact=True)
 pd.testing.assert_series_equal(first["equity"],second["equity"],check_exact=True)
 assert first["metrics"]==second["metrics"]
