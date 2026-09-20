from datetime import datetime, timedelta, timezone

import pytest

from xauusd.agent_loop import agent_transcript_store_from_env
from xauusd.local_state import SQLiteAgentTranscriptStore, SQLitePaperTradingStore
from xauusd.paper_trading import ACCEPTED, KILL_SWITCH, PaperDecision, PaperRiskConfig, PaperTrading, paper_from_env

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
    assert duplicate == first
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