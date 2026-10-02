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


def gapped_bars():
    """Three contiguous sessions separated by weekend gaps."""
    first = pd.date_range("2026-01-05 22:00", periods=40, freq="min", tz="UTC")
    second = pd.date_range("2026-01-08 01:00", periods=40, freq="min", tz="UTC")
    third = pd.date_range("2026-01-09 01:00", periods=20, freq="min", tz="UTC")
    index = first.append(second).append(third)
    flat = np.full(len(index), 3000.0)
    return pd.DataFrame({"open": flat, "high": flat + 0.1, "low": flat - 0.1, "close": flat,
                         "volume": np.ones(len(index))}, index=index)


HOLD = dict(max_holding_bars=None, stop_distance=None, target_distance=None)


def holding_signal(index, first=5, last=80):
    signal = pd.Series(0, index=index)
    signal.iloc[first:last] = 1
    return signal


def test_overnight_financing_is_charged_once_per_crossed_session_gap():
    """A multi-day hold was modelled with zero carry.

    `max_holding_bars` reaches 240 in the search grid, so multi-day gold holds
    were priced with no financing at all while a 1-5 point stop was in force.
    """
    frame = gapped_bars()
    signal = holding_signal(frame.index)
    free = EventDrivenBacktester(ExecutionConfig(annual_financing_rate=0.0, **HOLD)).run(frame, signal)["metrics"]
    charged = EventDrivenBacktester(ExecutionConfig(annual_financing_rate=0.05, **HOLD)).run(frame, signal)["metrics"]

    assert free["overnight_financing"] == 0.0
    # Two weekend gaps are crossed, at 0.05/365.25 per gap on 3000 x 1 oz.
    assert charged["overnight_financing"] == pytest.approx(2 * 0.05 / 365.25 * 3000.0)
    # The carry is a real cost, not a presentational one.
    assert charged["net_profit"] < free["net_profit"]


def test_overnight_financing_is_not_charged_to_a_flat_account():
    frame = gapped_bars()
    flat = EventDrivenBacktester(ExecutionConfig(annual_financing_rate=0.05, **HOLD)).run(
        frame, pd.Series(0, index=frame.index))["metrics"]
    assert flat["overnight_financing"] == 0.0


def test_metrics_never_serialise_nan_or_infinity():
    """A no-loss strategy used to produce profit_factor inf.

    json.dumps(..., allow_nan=False) raises on inf, so the strongest strategy in
    the space could not be recorded at all, and `inf >= 1.0` passed the
    profit-factor gate in the strategy's favour.
    """
    import json

    index = pd.date_range("2026-01-05 00:00", periods=200, freq="min", tz="UTC")
    rising = np.concatenate([np.linspace(3000, 3100, 40), np.full(160, 3100.0)])
    frame = pd.DataFrame({"open": rising, "high": rising + 0.05, "low": rising - 0.05,
                          "close": rising, "volume": np.ones(200)}, index=index)
    signal = pd.Series(0, index=index)
    signal.iloc[5] = 1
    signal.iloc[20] = 0
    metrics = EventDrivenBacktester(ExecutionConfig()).run(frame, signal)["metrics"]

    assert metrics["trades"] == 1
    assert metrics["net_profit"] > 0
    # Undefined, not infinite: a single winner has no loss side to divide by.
    assert metrics["profit_factor"] is None
    json.dumps(metrics, allow_nan=False)  # must not raise


def test_a_flat_strategy_reports_undefined_metrics_rather_than_zero():
    """Zero is a real value; a metric that cannot be computed must say so.

    Reporting sharpe 0.0 for zero return variance made a completely flat
    strategy look like a well-defined mediocre one.
    """
    import json

    index = pd.date_range("2026-01-05 00:00", periods=50, freq="min", tz="UTC")
    flat = np.full(50, 3000.0)
    frame = pd.DataFrame({"open": flat, "high": flat + 0.1, "low": flat - 0.1, "close": flat,
                          "volume": np.ones(50)}, index=index)
    metrics = EventDrivenBacktester(ExecutionConfig()).run(frame, pd.Series(0, index=index))["metrics"]

    assert metrics["trades"] == 0
    assert metrics["sharpe"] is None
    assert metrics["win_rate"] is None
    assert metrics["exposure"] is None
    assert metrics["overnight_financing"] == 0.0
    json.dumps(metrics, allow_nan=False)


def test_optimistic_intrabar_priority_is_refused():
    """`target` resolves an ambiguous bar in the strategy's favour.

    The search grid and the tournament gates never set it, so production stayed
    conservative, but it was an unguarded footgun for any config that could
    reach a champion.
    """
    with pytest.raises(ValueError, match="intrabar_priority"):
        ExecutionConfig(intrabar_priority="target")


def test_financing_rate_must_be_finite_and_non_negative():
    for bad in (-0.01, float("inf"), float("nan")):
        with pytest.raises(ValueError, match="annual_financing_rate"):
            ExecutionConfig(annual_financing_rate=bad)
