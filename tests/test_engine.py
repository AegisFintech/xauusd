import pandas as pd
import pytest

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
    trade = EventDrivenBacktester(config).run(frame, signal)["trades"].iloc[0]
    assert trade.gross_pnl == pytest.approx(-30)
    assert trade.commission == 7
    assert trade.net_pnl == pytest.approx(-37)


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
