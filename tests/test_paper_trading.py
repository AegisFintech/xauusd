import pytest
from datetime import datetime, timedelta, timezone

from xauusd.paper_trading import (ACCEPTED, DAILY_LOSS_LIMIT, KILL_SWITCH, MAX_POSITION,
                                  STALE_MARKET_DATA, InMemoryPaperTradingStore, PaperDecision,
                                  PaperRiskConfig, PaperTrading)


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
    assert trading.evaluate(decision("stale", age=6), NOW)["reason"] == STALE_MARKET_DATA
    assert trading.evaluate(decision("fill"), NOW)["reason"] == ACCEPTED
    assert trading.evaluate(decision("large", quantity=0.1), NOW)["reason"] == MAX_POSITION
    assert trading.evaluate(decision("loss", side="SELL", price=3980), NOW)["reason"] == DAILY_LOSS_LIMIT


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
