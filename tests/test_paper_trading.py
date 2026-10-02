import pytest
from datetime import datetime, timedelta, timezone

from xauusd.paper_trading import (ACCEPTED, BAR_INTERVAL_SECONDS, DAILY_LOSS_LIMIT,
                                  DEFAULT_MAX_MARKET_DATA_AGE_SECONDS, KILL_SWITCH, MARKET_CLOSED,
                                  MAX_POSITION, STALE_MARKET_DATA, InMemoryPaperTradingStore,
                                  PaperDecision, PaperRiskConfig, PaperTrading, market_data_age_seconds,
                                  market_is_open, observation_is_future, restart_policy)


NOW = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)


def decision(identifier="d1", side="BUY", quantity=1.0, price=4000.0, age=0, at=None):
    return PaperDecision(identifier, "XAUUSD", side, quantity, price,
                         (at or NOW) - timedelta(seconds=age))


def test_missing_state_defaults_to_stopped_and_requires_explicit_start():
    trading = PaperTrading(InMemoryPaperTradingStore())
    assert trading.evaluate(decision("blocked"), NOW)["reason"] == KILL_SWITCH
    trading.start("operator approved paper session")
    assert trading.evaluate(decision("authorized"), NOW)["reason"] == ACCEPTED


def test_duplicate_decision_returns_persisted_outcome_without_second_fill():
    trading = PaperTrading(InMemoryPaperTradingStore()); trading.start("test")
    first = trading.evaluate(decision(), NOW)
    duplicate = trading.evaluate(decision(), NOW + timedelta(seconds=10))
    # Same verdict, same recorded outcome, but explicitly flagged as a replay so a
    # consumer cannot mistake it for a fresh fill.
    assert {k: v for k, v in duplicate.items() if k != "replayed"} == first
    assert duplicate["replayed"] is True
    assert "replayed" not in first
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


def test_observation_is_future_only_tolerates_one_bar_of_forming():
    # A bar up to one interval ahead is still forming and legitimately has a
    # close time in the future.
    assert observation_is_future(NOW, NOW) is False
    assert observation_is_future(NOW - timedelta(seconds=30), NOW) is False
    # Beyond that it is a bad observation, not a forming one. The zero clamp in
    # market_data_age_seconds would report it as age zero forever.
    assert observation_is_future(NOW + timedelta(seconds=61), NOW) is True
    assert observation_is_future(NOW + timedelta(days=10), NOW) is True


def test_gate_refuses_a_future_dated_bar_instead_of_trusting_the_clamp():
    """A far-future bar used to pass every freshness gate and supply the fill.

    market_data_age_seconds clamps to zero, so a bar dated ten days ahead
    reported age 0, satisfied any max_market_data_age_seconds, and provided the
    fill price. The clamp is only honest for a forming bar.
    """
    config = PaperRiskConfig(daily_loss_limit=10, max_position=1, max_market_data_age_seconds=5)
    trading = PaperTrading(InMemoryPaperTradingStore(), config); trading.start("test")

    future = PaperDecision("future-bar", "XAUUSD", "BUY", 0.5, 4000.0,
                           NOW + timedelta(days=10))
    assert trading.evaluate(future, NOW)["reason"] == STALE_MARKET_DATA
    assert trading.state()["ledger"] == []
    assert trading.monitor(4000.0, NOW + timedelta(days=10), NOW)["status"] == "invalid_observation"


def test_monitor_still_marks_a_forming_bar_and_rejects_a_future_one():
    trading = PaperTrading(InMemoryPaperTradingStore()); trading.start("test")
    assert trading.monitor(4000.0, NOW, NOW)["status"] == "ok"
    assert trading.monitor(4000.0, NOW + timedelta(hours=2), NOW)["status"] == "invalid_observation"


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


def utc(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def test_market_is_open_follows_the_new_york_close_in_us_standard_time():
    # From 2026-11-01 to 2027-03-14 New York is UTC-5, so the 17:00 New York close and
    # break move to 22:00-23:00 UTC; a fixed 21:00-22:00 UTC window would be wrong both ways.
    cases = [
        (utc(2027, 1, 13, 21, 30), True),   # Wednesday 16:30 New York: still trading
        (utc(2027, 1, 13, 22, 0), False),   # Wednesday 17:00 New York: daily break
        (utc(2027, 1, 13, 22, 59), False),  # Wednesday 17:59 New York: daily break
        (utc(2027, 1, 13, 23, 0), True),    # Wednesday 18:00 New York: reopened
        (utc(2027, 1, 15, 21, 59), True),   # Friday 16:59 New York: before the weekly close
        (utc(2027, 1, 15, 22, 0), False),   # Friday 17:00 New York: weekly close
        (utc(2027, 1, 16, 2, 0), False),    # Friday 21:00 New York, already Saturday in UTC
        (utc(2027, 1, 17, 22, 30), False),  # Sunday 17:30 New York: before the weekly open
        (utc(2027, 1, 17, 23, 0), True),    # Sunday 18:00 New York: weekly open
        (utc(2027, 1, 18, 3, 0), True),     # Sunday 22:00 New York, already Monday in UTC
    ]
    for moment, expected in cases:
        assert market_is_open(moment) is expected, f"{moment}: expected {expected}"


def test_market_is_open_across_both_us_daylight_saving_transitions():
    cases = [
        (utc(2026, 10, 30, 20, 59), True),   # last daylight-time Friday: open until 21:00 UTC
        (utc(2026, 10, 30, 21, 0), False),
        (utc(2026, 11, 1, 22, 0), False),    # clocks fell back: Sunday open moves to 23:00 UTC
        (utc(2026, 11, 1, 23, 0), True),
        (utc(2027, 3, 12, 21, 30), True),    # last standard-time Friday: open until 22:00 UTC
        (utc(2027, 3, 12, 22, 0), False),
        (utc(2027, 3, 14, 21, 59), False),   # clocks sprang forward: Sunday open back at 22:00 UTC
        (utc(2027, 3, 14, 22, 0), True),
        (utc(2027, 3, 17, 21, 30), False),   # the break is 21:00-22:00 UTC again
    ]
    for moment, expected in cases:
        assert market_is_open(moment) is expected, f"{moment}: expected {expected}"


def test_gate_accepts_the_winter_hour_after_21_utc_and_refuses_the_real_break():
    trading = PaperTrading(InMemoryPaperTradingStore()); trading.start("test")
    trading_hour = utc(2027, 1, 13, 21, 30)   # 16:30 New York
    break_hour = utc(2027, 1, 13, 22, 30)     # 17:30 New York
    fresh = lambda identifier, moment: PaperDecision(identifier, "XAUUSD", "BUY", 0.1, 4000.0, moment)
    assert trading.evaluate(fresh("winter-open", trading_hour), trading_hour)["reason"] == ACCEPTED
    assert trading.evaluate(fresh("winter-break", break_hour), break_hour)["reason"] == MARKET_CLOSED


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


def test_daily_loss_limit_is_not_reset_by_the_first_move_after_midnight():
    """The first observation of a new day must not set its own loss baseline.

    ``_mark`` used to set ``day_start_equity`` to the equity it had *already*
    re-marked. The first observation of a new day therefore anchored that day at
    its own post-move equity, so whatever move that observation carried was
    forgiven: an adverse gap at the boundary, or the whole Friday-to-Sunday
    reopen, reset the counter instead of counting against the new day. The
    baseline is now the previous mark, taken before this observation is applied.
    The day still rolls at UTC midnight.
    """
    config = PaperRiskConfig(daily_loss_limit=100, max_position=2, max_drawdown=0.5,
                             max_market_data_age_seconds=180)
    trading = PaperTrading(InMemoryPaperTradingStore(), config); trading.start("test")

    # Open a long on day 1 at 4000 and leave the last day-1 mark at the entry,
    # so equity is unchanged. One unit of XAUUSD: $1 of price is $1 of equity.
    assert trading.evaluate(decision("open", quantity=1.0, price=4000.0), NOW)["reason"] == ACCEPTED
    assert trading.state()["day"] == NOW.date().isoformat()
    assert trading.state()["day_start_equity"] == pytest.approx(100_000.0)

    # The very first observation of day 2 carries a $150 adverse move.
    after_midnight = NOW.replace(hour=0, minute=1, day=NOW.day + 1)
    probe = decision("post-boundary", quantity=0.01, price=3850.0, at=after_midnight)
    assert trading.evaluate(probe, after_midnight)["reason"] == DAILY_LOSS_LIMIT
    state = trading.state()
    assert state["day"] == after_midnight.date().isoformat()
    # The day is dated after the move, but the baseline is the pre-move mark.
    assert state["day_start_equity"] == pytest.approx(100_000.0)
    assert trading.summary()["day_pl"] == pytest.approx(-150.0)
    # trades_today still resets on the date change; only the P&L baseline survives it.
    assert state["trades_today"] == 0


def test_daily_loss_limit_counts_the_weekend_reopen_gap():
    """The same mechanism, with a weekend-sized move: the reopen gap is counted.

    Friday 21:00 UTC close and Sunday 22:00 UTC reopen, one unit long from 4000.
    """
    config = PaperRiskConfig(daily_loss_limit=100, max_position=2, max_drawdown=0.5,
                             max_market_data_age_seconds=180)
    trading = PaperTrading(InMemoryPaperTradingStore(), config); trading.start("test")
    friday = datetime(2026, 9, 18, 20, tzinfo=timezone.utc)
    assert trading.evaluate(decision("open", quantity=1.0, price=4000.0, at=friday), friday)["reason"] == ACCEPTED

    sunday = datetime(2026, 9, 20, 22, 5, tzinfo=timezone.utc)  # first reopen tick
    assert market_is_open(sunday) is True
    assert market_is_open(friday) is True
    probe = decision("reopen-gap", quantity=0.01, price=3700.0, at=sunday)
    assert trading.evaluate(probe, sunday)["reason"] == DAILY_LOSS_LIMIT
    state = trading.state()
    assert state["day_start_equity"] == pytest.approx(100_000.0)
    assert trading.summary()["day_pl"] == pytest.approx(-300.0)


def test_daily_loss_baseline_is_not_the_high_water_mark():
    """The daily baseline is the day's opening mark, never the high-water mark.

    Marking up raises high_water_equity. Falling back from that peak must still
    measure the day loss against the day's open, otherwise a single intraday
    spike silently forgives every point after it. ``day_pl`` in the summary is
    the direct observable: measured from the peak it would read -120 here.
    """
    config = PaperRiskConfig(daily_loss_limit=25, max_position=2, max_drawdown=0.5,
                             max_market_data_age_seconds=180)
    trading = PaperTrading(InMemoryPaperTradingStore(), config); trading.start("test")
    trading.evaluate(decision("open", quantity=1.0, price=4000.0), NOW)

    up = NOW + timedelta(minutes=1)
    assert trading.monitor(4100.0, up, up)["status"] == "ok"
    state = trading.state()
    assert state["high_water_equity"] == pytest.approx(100_100.0)
    assert state["day_start_equity"] == pytest.approx(100_000.0)

    down = NOW + timedelta(minutes=2)
    assert trading.monitor(3980.0, down, down)["status"] == "ok"
    state = trading.state()
    assert state["day_start_equity"] == pytest.approx(100_000.0)
    assert state["high_water_equity"] == pytest.approx(100_100.0)
    # 96,000 cash + 1 unit x 3,980 mark = 99,980, so the day is down 20, not 120.
    assert trading.summary()["day_pl"] == pytest.approx(-20.0)

    # Past the limit the monitor persists the risk stop, as it always has.
    further = NOW + timedelta(minutes=3)
    assert trading.monitor(3970.0, further, further)["status"] == "stopped"
    assert trading.state()["kill_switch_reason"] == "risk_limit"


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


@pytest.mark.parametrize("reason", [
    "maintenance",                    # custom `paper stop --reason`
    "agent_continuous_paper_loop",    # even the agent's own start reason, once used to stop
    "broker_execution_failed",        # coordinator after a rejected or unknown broker outcome
    "max_consecutive_failures",       # demo automation loop
    "startup_reconciliation_failed",  # demo automation start-up
    "transport_failure",
    "risk_limit", "recovery_failed", "missing_credentials", "unknown_account_type",
])
def test_maybe_resume_preserves_every_persisted_stop_except_fresh_state(reason):
    store = InMemoryPaperTradingStore()
    trading = PaperTrading(store); trading.start("agent_continuous_paper_loop")
    trading.stop(reason)
    result = trading.maybe_resume("agent_continuous_paper_loop")
    assert result["resumed"] is False
    assert result["blocked"] is True
    assert result["kill_switch_reason"] == reason
    assert trading.state()["stopped"] is True
    assert trading.state()["kill_switch_reason"] == reason
    trading.start("operator investigated")  # the explicit override still works
    assert trading.state()["stopped"] is False


def test_restart_policy_is_an_allowlist_that_fails_closed():
    assert restart_policy({"stopped": False, "kill_switch_reason": "operator_resume"}) == "running"
    assert restart_policy({"stopped": True, "kill_switch_reason": "missing_state"}) == "resume"
    assert restart_policy({"stopped": True, "kill_switch_reason": "a_reason_added_later"}) == "refuse"
    assert restart_policy({"stopped": True, "kill_switch_reason": None}) == "refuse"
    # Without an explicit boolean the state cannot prove it is running or fresh.
    assert restart_policy({"kill_switch_reason": "missing_state"}) == "refuse"
    assert restart_policy({"stopped": None, "kill_switch_reason": "missing_state"}) == "refuse"
