"""Explicit operator reset of a stopped local paper session, after backup."""
from datetime import datetime, timezone
from pathlib import Path

from .bits_jobs import AgentLock, BitsStore
from .experiment_registry import canonical_json
from .local_state import SQLitePaperTradingStore, SQLiteAgentTranscriptStore
from .paper_trading import _default_state
from .state_backup import backup_local_state


def reset_paper_session(paper, transcript, backup_root="backups/local-state"):
    if not isinstance(paper.store, SQLitePaperTradingStore) or not isinstance(transcript, SQLiteAgentTranscriptStore):
        raise ValueError("session reset supports local SQLite paper accounts only")
    if Path(paper.store.db_path).resolve() != Path(transcript.db_path).resolve():
        raise ValueError("paper and transcript must share the same database")
    if not paper.state().get("stopped"):
        raise ValueError("paper stop is required before reset")
    lock = AgentLock(transcript)
    try:
        store = BitsStore(transcript)
        backup = backup_local_state(paper.store.db_path, backup_root)
        state = _default_state(paper.store.initial_cash)
        state["kill_switch_reason"] = "operator"
        reset = {"recorded_at": datetime.now(timezone.utc).isoformat(), "initial_cash": paper.store.initial_cash,
                 "reason": "operator_requested_fresh_start"}
        connection = transcript.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            for table in ("bits_jobs", "bits_state", "agent_transcript", "agent_runs", "paper_trading_decisions", "paper_trading_state"):
                connection.execute("DELETE FROM " + table)
            connection.execute("DELETE FROM sqlite_sequence WHERE name='agent_transcript'")
            connection.execute("INSERT INTO paper_trading_state(state_key,state_json,updated_at) VALUES('primary',?,?)",
                               (canonical_json(state), reset["recorded_at"]))
            connection.execute("INSERT INTO bits_state(state_key,value_json) VALUES('session_reset',?)", (canonical_json(reset),))
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()
        return {"status": "reset", "paper_stopped": True, "initial_cash": paper.store.initial_cash,
                "backup": backup["directory"], "reset": reset}
    finally:
        lock.close()
