from datetime import datetime, timedelta, timezone
import json

import pytest

from xauusd.agent_loop import agent_transcript_store_from_env
from xauusd.local_state import SQLiteAgentTranscriptStore, SQLitePaperTradingStore
from xauusd.paper_trading import (ACCEPTED, KILL_SWITCH, PaperDecision, PaperRiskConfig, PaperTrading,
                                  paper_from_env, restart_policy)

NOW = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)


def decision(identifier="d1", side="BUY", quantity=1.0, price=4000.0, age=0):
    return PaperDecision(identifier, "XAUUSD", side, quantity, price, NOW - timedelta(seconds=age))


def test_sqlite_paper_store_persists_state_and_decision_idempotency(tmp_path):
    path = str(tmp_path / "paper.db")
    store = SQLitePaperTradingStore(db_path=path)
    trading = PaperTrading(store, PaperRiskConfig(max_market_data_age_seconds=120))
    trading.start("test")
    first = trading.evaluate(decision("a1"), NOW)
    assert first["accepted"] and first["reason"] == ACCEPTED

    reopened = PaperTrading(SQLitePaperTradingStore(db_path=path), PaperRiskConfig(max_market_data_age_seconds=120))
    duplicate = reopened.evaluate(decision("a1"), NOW + timedelta(seconds=10))
    # Idempotent across a restart, and still identifiable as a replay.
    assert duplicate["accepted"] is first["accepted"]
    assert duplicate["position"] == first["position"]
    assert duplicate["replayed"] is True
    assert reopened.state()["position"] == pytest.approx(1.0)
    assert len(reopened.state()["ledger"]) == 1
    assert reopened.state()["stopped"] is False


def test_sqlite_paper_store_kill_switch_persists_and_fails_closed(tmp_path):
    path = str(tmp_path / "paper.db")
    store = SQLitePaperTradingStore(db_path=path)
    trading = PaperTrading(store); trading.start("test")
    trading.evaluate(decision("a1"), NOW)

    reopened = PaperTrading(SQLitePaperTradingStore(db_path=path))
    reopened.stop("operator halt")
    assert reopened.evaluate(decision("a2"), NOW)["reason"] == KILL_SWITCH
    assert reopened.state()["stopped"] is True
    assert reopened.state()["kill_switch_reason"] == "operator halt"


def test_sqlite_paper_store_corrupt_state_fails_closed(tmp_path):
    import sqlite3
    path = str(tmp_path / "paper.db")
    store = SQLitePaperTradingStore(db_path=path)
    store.state()  # materialize the default state row
    connection = sqlite3.connect(path)
    connection.execute("UPDATE paper_trading_state SET state_json='{not valid json' WHERE state_key='primary'")
    connection.commit()
    connection.close()

    trading = PaperTrading(SQLitePaperTradingStore(db_path=path))
    assert trading.state()["kill_switch_reason"] == "corrupt_state"
    assert trading.evaluate(decision(), NOW)["reason"] == KILL_SWITCH


def test_sqlite_paper_store_rejects_valid_json_with_missing_keys(tmp_path):
    """A row that parses but cannot be evaluated is corruption, not an account.

    Before this was enforced, such a row was trusted: every gate raised KeyError
    instead of returning a reason, the monitor raised instead of marking a stop,
    and restart_policy read the absent evidence as a fresh account and cleared
    the kill switch.
    """
    import sqlite3
    path = str(tmp_path / "paper.db")
    SQLitePaperTradingStore(db_path=path).state()
    connection = sqlite3.connect(path)
    connection.execute("UPDATE paper_trading_state SET state_json=? WHERE state_key='primary'",
                       (json.dumps({"stopped": False, "kill_switch_reason": "missing_state"}),))
    connection.commit()
    connection.close()

    trading = PaperTrading(SQLitePaperTradingStore(db_path=path))
    state = trading.state()
    assert state["kill_switch_reason"] == "corrupt_state"
    assert state["stopped"] is True
    assert trading.evaluate(decision(), NOW)["reason"] == KILL_SWITCH
    # An unreadable state must never be classified as resumable.
    assert restart_policy(state) == "refuse"
    assert trading.maybe_resume("agent restart")["resumed"] is False


@pytest.mark.parametrize("state_json", [
    json.dumps({"stopped": "false", "cash": 1.0, "position": 0.0, "average_entry_price": 0.0,
                "mark_price": 1.0, "high_water_equity": 1.0, "day": None, "day_start_equity": 1.0,
                "trades_today": 0, "ledger": [], "kill_switch_reason": "missing_state"}),
    json.dumps({"stopped": True, "cash": "lots", "position": 0.0, "average_entry_price": 0.0,
                "mark_price": 1.0, "high_water_equity": 1.0, "day": None, "day_start_equity": 1.0,
                "trades_today": 0, "ledger": [], "kill_switch_reason": "missing_state"}),
    json.dumps({"stopped": True, "cash": 1.0, "position": 0.0, "average_entry_price": 0.0,
                "mark_price": 1.0, "high_water_equity": 1.0, "day": None, "day_start_equity": 1.0,
                "trades_today": 0, "ledger": {}, "kill_switch_reason": "missing_state"}),
    json.dumps([1, 2, 3]),
    json.dumps({"stopped": True, "cash": 1e999, "position": 0.0, "average_entry_price": 0.0,
                "mark_price": 1.0, "high_water_equity": 1.0, "day": None, "day_start_equity": 1.0,
                "trades_today": 0, "ledger": [], "kill_switch_reason": "missing_state"}),
])
def test_sqlite_paper_store_rejects_mistyped_fields(tmp_path, state_json):
    import sqlite3
    path = str(tmp_path / "paper.db")
    SQLitePaperTradingStore(db_path=path).state()
    connection = sqlite3.connect(path)
    connection.execute("UPDATE paper_trading_state SET state_json=? WHERE state_key='primary'", (state_json,))
    connection.commit()
    connection.close()

    trading = PaperTrading(SQLitePaperTradingStore(db_path=path))
    assert trading.state()["kill_switch_reason"] == "corrupt_state"
    assert trading.state()["stopped"] is True
    # summary() must stay renderable: a corruption report is useless if the
    # health endpoint raises instead of reporting it.
    assert trading.summary()["kill_switch_reason"] == "corrupt_state"


def test_sqlite_paper_store_keeps_a_valid_state_untouched(tmp_path):
    """Validation must not reject a real account, including a running one."""
    import sqlite3
    path = str(tmp_path / "paper.db")
    trading = PaperTrading(SQLitePaperTradingStore(db_path=path))
    trading.start("operator")
    trading.evaluate(decision("fill-1"), NOW)
    before = trading.state()
    assert before["stopped"] is False

    reopened = PaperTrading(SQLitePaperTradingStore(db_path=path))
    after = reopened.state()
    assert after["stopped"] is False
    assert after["kill_switch_reason"] == "operator"
    assert after["position"] == pytest.approx(1.0)
    assert len(after["ledger"]) == 1
    assert after["kill_switch_reason"] != "corrupt_state"


def test_sqlite_transcript_store_round_trips_steps_and_runs(tmp_path):
    path = str(tmp_path / "transcript.db")
    store = SQLiteAgentTranscriptStore(db_path=path)
    store.start_run("run-1")
    id1 = store.append("run-1", 1, "tick_start", {"price": 4000.0})
    id2 = store.append("run-1", 1, "tick_end", {"summary": "ok"})
    store.finish_run("run-1", "stopped")

    reopened = SQLiteAgentTranscriptStore(db_path=path)
    assert reopened.run_status("run-1") == "stopped"
    steps = reopened.steps("run-1")
    assert [step["id"] for step in steps] == [id1, id2]
    assert steps[0]["phase"] == "tick_start"
    assert steps[0]["content"] == {"price": 4000.0}
    desc = reopened.steps("run-1", desc=True)
    assert [step["id"] for step in desc] == [id2, id1]
    after = reopened.steps("run-1", after_id=id1)
    assert [step["id"] for step in after] == [id2]
    assert reopened.runs(limit=5)[0]["ticks"] == 1


def test_agent_transcript_backend_selection_defaults_to_local(tmp_path, monkeypatch):
    monkeypatch.delenv("XAUUSD_STATE_BACKEND", raising=False)
    monkeypatch.setenv("STATE_DB_PATH", str(tmp_path / "state.db"))
    store = agent_transcript_store_from_env()
    from xauusd.local_state import SQLiteAgentTranscriptStore
    assert isinstance(store, SQLiteAgentTranscriptStore)


def test_invalid_backend_raises(monkeypatch):
    monkeypatch.setenv("XAUUSD_STATE_BACKEND", "bogus")
    with pytest.raises(ValueError, match="XAUUSD_STATE_BACKEND"):
        paper_from_env()


def test_paper_from_env_defaults_to_local_sqlite_store(tmp_path, monkeypatch):
    monkeypatch.delenv("XAUUSD_STATE_BACKEND", raising=False)
    monkeypatch.setenv("STATE_DB_PATH", str(tmp_path / "paper.db"))
    trading = paper_from_env()
    from xauusd.local_state import SQLitePaperTradingStore
    assert isinstance(trading.store, SQLitePaperTradingStore)
    assert trading.state()["cash"] == pytest.approx(100_000.0)


def test_sqlite_paper_store_integrity_check_reports_ok(tmp_path):
    path = str(tmp_path / "paper.db")
    store = SQLitePaperTradingStore(db_path=path)
    store.state()
    assert store.integrity_check() == "ok"


def test_sqlite_integrity_check_detects_corruption(tmp_path):
    path = tmp_path / "paper.db"
    store = SQLitePaperTradingStore(db_path=str(path))
    store.state()
    data = bytearray(path.read_bytes())
    data[100:116] = b"\x00" * 16  # page-1 header block -> malformed database image
    path.write_bytes(bytes(data))
    for sidecar in (tmp_path / "paper.db-wal", tmp_path / "paper.db-shm"):
        if sidecar.exists():
            sidecar.unlink()  # simulate abrupt loss of the WAL sidecars
    reopened = SQLitePaperTradingStore.__new__(SQLitePaperTradingStore)
    reopened.db_path = str(path)
    assert reopened.integrity_check() != "ok"


def test_sqlite_transcript_reconciles_running_orphans(tmp_path):
    path = str(tmp_path / "transcript.db")
    store = SQLiteAgentTranscriptStore(db_path=path)
    store.start_run("run-old")
    store.start_run("run-current")

    closed = store.reconcile_running_runs(excluding="run-current")

    assert closed == 1
    assert store.run_status("run-old") == "stopped"
    assert store.run_status("run-current") == "running"
    store.finish_run("run-current", "stopped")
    assert store.reconcile_running_runs() == 0

def test_transcript_prune_bounds_growth_but_keeps_recent_runs(tmp_path):
    """The transcript had no DELETE anywhere and gained a row per heartbeat.

    14,350 rows and 5.4 MB accumulated in two days, 1.9 MB of it pure per-tick
    noise. Retention keeps recent runs whole and trims the oldest steps.
    """
    store = SQLiteAgentTranscriptStore(str(tmp_path / "state.db"))
    for index in range(6):
        run = f"agent_{index}"
        store.start_run(run)
        for tick in range(10):
            store.append(run, tick, "tick_start", {"tick": tick})
        store.finish_run(run, "stopped")

    before = len(store.steps(limit=1000))
    assert before == 60

    removed = store.prune(keep_runs=2, keep_steps=1000)

    assert removed["runs_removed"] == 40
    assert len(store.steps(limit=1000)) == 20
    # The run history itself is never deleted, so `runs()` still reports all six.
    assert len(store.runs(limit=10)) == 6
    kept = {row["run_id"] for row in store.steps(limit=1000)}
    assert kept == {"agent_4", "agent_5"}


def test_transcript_prune_trims_the_oldest_steps_within_kept_runs(tmp_path):
    store = SQLiteAgentTranscriptStore(str(tmp_path / "state.db"))
    store.start_run("agent_only")
    for tick in range(50):
        store.append("agent_only", tick, "tick_start", {"tick": tick})

    removed = store.prune(keep_runs=5, keep_steps=10)

    assert removed["steps_removed"] == 40
    remaining = store.steps(limit=100)
    assert len(remaining) == 10
    # The newest steps are the ones kept.
    assert [row["content"]["tick"] for row in remaining] == list(range(40, 50))


def test_transcript_prune_is_a_no_op_below_the_threshold(tmp_path):
    store = SQLiteAgentTranscriptStore(str(tmp_path / "state.db"))
    store.start_run("agent_small")
    store.append("agent_small", 1, "tick_start", {"tick": 1})

    assert store.prune(keep_runs=5, keep_steps=100)["steps_removed"] == 0
    assert len(store.steps(limit=10)) == 1


def test_transcript_prune_protects_rows_a_view_is_still_paging(tmp_path):
    """Pruning must not delete content a connected reader has not displayed yet.

    The live view pages by an `after`/`before` cursor. If a process start prunes
    the rows between the cursor and the newest, the view silently skips them.
    """
    store = SQLiteAgentTranscriptStore(str(tmp_path / "state.db"))
    for index in range(6):
        run = f"agent_{index}"
        store.start_run(run)
        for tick in range(10):
            store.append(run, tick, "tick_start", {"tick": tick})
        store.finish_run(run, "stopped")

    # The view has served up to id 25 and is asking for older steps.
    cursor = 25
    unconstrained = store.prune(keep_runs=2, keep_steps=1000)
    assert unconstrained["runs_removed"] == 40

    store2 = SQLiteAgentTranscriptStore(str(tmp_path / "state2.db"))
    for index in range(6):
        run = f"agent_{index}"
        store2.start_run(run)
        for tick in range(10):
            store2.append(run, tick, "tick_start", {"tick": tick})
        store2.finish_run(run, "stopped")

    protected = store2.prune(keep_runs=2, keep_steps=1000, preserve_below_id=cursor)
    # Rows at or below the cursor survive; only the ones the view has already
    # rendered are reclaimed. Old runs span ids 1-40, so ids 26-40 go.
    assert protected["runs_removed"] == 15
    assert store2.steps(after_id=0, limit=200)[0]["id"] == 1
    surviving = [row["id"] for row in store2.steps(after_id=0, limit=200)]
    assert all(row_id <= cursor or row_id > 40 for row_id in surviving)
