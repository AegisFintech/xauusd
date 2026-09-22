import pytest
from datetime import datetime, timedelta, timezone

from xauusd.paper_trading import (ACCEPTED, BAR_INTERVAL_SECONDS, DAILY_LOSS_LIMIT,
                                  DEFAULT_MAX_MARKET_DATA_AGE_SECONDS, KILL_SWITCH, MARKET_CLOSED,
                                  MAX_POSITION, STALE_MARKET_DATA, InMemoryPaperTradingStore,
                                  PaperDecision, PaperRiskConfig, PaperTrading, market_data_age_seconds,
                                  market_is_open)


NOW = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)


def decision(identifier="d1", side="BUY", quantity=1.0, price=4000.0, age=0):
    return PaperDecision(identifier, "XAUUSD", side, quantity, price, NOW - timedelta(seconds=age))


def test_missing_state_defaults_to_stopped_and_requires_explicit_start():
    trading = PaperTrading(InMemoryPaperTradingStore())
    assert trading.evaluate(decision("blocked"), NOW)["reason"] == KILL_SWITCH
    trading.start("operator approved paper session")
    assert trading.evaluate(decision("authorized"), NOW)["reason"] == ACCEPTED


def test_duplicate_decision_returns_persisted_outcome_without_second_fill():
    trading = PaperTrading(InMemoryPaperTradingStore()); trading.start("test")
    first = trading.evaluate(decision(), NOW)
    duplicate = trading.evaluate(decision(), NOW + timedelta(seconds=10))
    assert first == duplicate
    assert len(trading.state()["ledger"]) == 1


def test_position_freshness_and_daily_loss_gates_are_deterministic():
    config = PaperRiskConfig(daily_loss_limit=10, max_position=1, max_market_data_age_seconds=5)
    trading = PaperTrading(InMemoryPaperTradingStore(), config); trading.start("test")
    # age counts from the bar's open stamp, so 66s means it closed 6s ago: past the 5s gate.
    assert trading.evaluate(decision("stale", age=66), NOW)["reason"] == STALE_MARKET_DATA
    assert trading.evaluate(decision("fill"), NOW)["reason"] == ACCEPTED
    assert trading.evaluate(decision("large", quantity=0.1), NOW)["reason"] == MAX_POSITION
    assert trading.evaluate(decision("loss", side="SELL", price=3980), NOW)["reason"] == DAILY_LOSS_LIMIT


def test_market_data_age_counts_from_bar_close_not_bar_open():
    assert market_data_age_seconds(NOW - timedelta(seconds=90), NOW) == 30
    assert market_data_age_seconds(NOW - timedelta(seconds=60), NOW) == 0


def test_market_data_age_clamps_a_still_forming_bar_to_zero():
    assert market_data_age_seconds(NOW, NOW) == 0
    assert market_data_age_seconds(NOW + timedelta(seconds=30), NOW) == 0


def test_default_gate_accepts_the_newest_closed_m1_bar():
    # Regression: persisted bars are stamped at their open time, so the newest
    # closed M1 bar is always 60-120s old. The previous 60s default could never
    # accept one, and every proposal was refused as STALE_MARKET_DATA.
    trading = PaperTrading(InMemoryPaperTradingStore()); trading.start("test")

    assert DEFAULT_MAX_MARKET_DATA_AGE_SECONDS > BAR_INTERVAL_SECONDS
    assert trading.evaluate(decision("closed_110s_ago", age=110), NOW)["reason"] == ACCEPTED
    assert trading.evaluate(decision("feed_died", age=600), NOW)["reason"] == STALE_MARKET_DATA


def test_simulated_ledger_realizes_profit_when_position_is_closed():
    trading = PaperTrading(InMemoryPaperTradingStore()); trading.start("test")
    trading.evaluate(decision("buy", price=4000), NOW)
    result = trading.evaluate(decision("sell", side="SELL", price=4010), NOW)
    assert result["accepted"] and result["position"] == 0
    assert trading.state()["ledger"][-1]["realized_pnl"] == 10


def test_summary_includes_equity_pnl_drawdown_and_recent_fills():
    trading = PaperTrading(InMemoryPaperTradingStore(), PaperRiskConfig(max_market_data_age_seconds=120))
    assert trading.summary()["stopped"] is True
    assert trading.summary()["side"] == "flat"
    trading.start("test")
    trading.evaluate(decision("buy", price=4000), NOW)
    summary = trading.summary()
    assert summary["stopped"] is False
    assert summary["position"] == pytest.approx(1.0)
    assert summary["side"] == "long"
    assert summary["equity"] == pytest.approx(100_000.0)
    assert summary["day_pl"] == pytest.approx(0.0)
    assert len(summary["recent_fills"]) == 1
    assert summary["recent_fills"][0]["decision_id"] == "buy"


def test_corrupt_memory_state_fails_closed():
    store = InMemoryPaperTradingStore(); trading = PaperTrading(store); trading.start("test")
    store.corrupt_state_for_test()
    assert trading.evaluate(decision(), NOW)["reason"] == KILL_SWITCH
    assert trading.state()["kill_switch_reason"] == "corrupt_state"


def xtime(day, hour, minute=0):
    return datetime(2026, 9, day, hour, minute, tzinfo=timezone.utc)


def test_market_is_open_session_matrix():
    cases = [
        (xtime(14, 0), True),     # Monday 00:00 open
        (xtime(17, 12, 0), True),  # Wednesday midday open
        (xtime(17, 21, 30), False),  # Wednesday evening break 21-22 UTC
        (xtime(17, 22, 5), True),   # Wednesday reopening after break
        (xtime(18, 20, 59), True),  # Friday before close
        (xtime(18, 21, 0), False),  # Friday close 21:00 UTC
        (xtime(19, 12, 0), False),  # Saturday closed
        (xtime(20, 21, 59), False),  # Sunday before open
        (xtime(20, 22, 0), True),   # Sunday open 22:00 UTC
    ]
    for moment, expected in cases:
        assert market_is_open(moment) is expected, f"{moment}: expected {expected}"


def test_gate_returns_market_closed_outside_trading_hours():
    trading = PaperTrading(InMemoryPaperTradingStore()); trading.start("test")
    saturday = xtime(19, 12, 0)
    result = trading.evaluate(decision("weekend", age=0), saturday)
    assert result["accepted"] is False
    assert result["reason"] == MARKET_CLOSED


def test_market_closed_precedes_stale_data():
    trading = PaperTrading(InMemoryPaperTradingStore()); trading.start("test")
    saturday = xtime(19, 12, 0)
    assert trading.evaluate(decision("weekend-stale", age=7200), saturday)["reason"] == MARKET_CLOSED


def test_summary_reports_market_open():
    trading = PaperTrading(InMemoryPaperTradingStore())
    summary = trading.summary()
    assert "market_open" in summary
    assert summary["market_open"] == market_is_open(datetime.now(timezone.utc))


def test_maybe_resume_fresh_missing_state_auto_starts():
    trading = PaperTrading(InMemoryPaperTradingStore())
    result = trading.maybe_resume("agent_continuous_paper_loop")
    assert result["resumed"] is True
    assert result["already_running"] is False
    assert result["kill_switch_reason"] == "agent_continuous_paper_loop"
    assert trading.state()["stopped"] is False


def test_maybe_resume_already_running_is_noop():
    store = InMemoryPaperTradingStore()
    trading = PaperTrading(store); trading.start("agent_continuous_paper_loop")
    result = trading.maybe_resume("agent_continuous_paper_loop")
    assert result["resumed"] is True
    assert result["already_running"] is True
    assert trading.state()["kill_switch_reason"] == "agent_continuous_paper_loop"


def test_maybe_resume_refuses_operator_stop_across_restart():
    original = InMemoryPaperTradingStore()
    trading = PaperTrading(original); trading.start("agent_continuous_paper_loop")
    trading.stop("operator")
    reopened = InMemoryPaperTradingStore()
    reopened._state = original._state  # simulate reopening the persisted state
    result = PaperTrading(reopened).maybe_resume("agent_continuous_paper_loop")
    assert result["resumed"] is False
    assert result["blocked"] is True
    assert result["kill_switch_reason"] == "operator"
    assert reopened.state()["stopped"] is True


def test_maybe_resume_refuses_corrupt_state():
    store = InMemoryPaperTradingStore()
    trading = PaperTrading(store); trading.start("test")
    store.corrupt_state_for_test()
    result = trading.maybe_resume("agent_continuous_paper_loop")
    assert result["resumed"] is False
    assert result["kill_switch_reason"] == "corrupt_state"


def test_maybe_resume_continues_after_benign_stop_reason():
    store = InMemoryPaperTradingStore()
    trading = PaperTrading(store); trading.start("agent_continuous_paper_loop")
    trading.stop("agent_continuous_paper_loop")
    result = trading.maybe_resume("agent_continuous_paper_loop")
    assert result["resumed"] is True
    assert trading.state()["stopped"] is False
