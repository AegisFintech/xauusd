"""Minimal local SQLite state stores for paper trading and the agent transcript.

Selected when XAUUSD_STATE_BACKEND=local (the default) so the running agent needs
no external database. The schema mirrors the Cockroach stores so switching backends
only changes the connection layer.
"""
from __future__ import annotations

import json
import math
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .experiment_registry import canonical_json
from .paper_trading import _default_state

DEFAULT_STATE_DB_PATH = "state/xauusd_local.db"


def state_db_path(db_path: str | None = None) -> str:
    return db_path or os.getenv("STATE_DB_PATH") or DEFAULT_STATE_DB_PATH


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, timeout=30.0, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA busy_timeout=30000")
    return connection


class SQLitePaperTradingStore:
    """Local SQLite replacement for the CockroachDB paper trading store."""

    def __init__(self, db_path: str | None = None, initial_cash: float = 100_000.0):
        if not (isinstance(initial_cash, (int, float)) and not isinstance(initial_cash, bool)
                and math.isfinite(initial_cash) and initial_cash > 0):
            raise ValueError("initial_cash must be finite and positive")
        self.db_path = state_db_path(db_path)
        self.initial_cash = initial_cash
        self.initialize()

    def initialize(self) -> None:
        with _connect(self.db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS paper_trading_state (
                state_key TEXT PRIMARY KEY, state_json TEXT NOT NULL, updated_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS paper_trading_decisions (
                decision_id TEXT PRIMARY KEY, result_json TEXT NOT NULL, created_at TEXT NOT NULL)""")

    def _locked_state(self, db: sqlite3.Connection) -> dict[str, Any]:
        row = db.execute("SELECT state_json FROM paper_trading_state WHERE state_key='primary'").fetchone()
        if row is None:
            state = _default_state(self.initial_cash)
            db.execute("INSERT INTO paper_trading_state(state_key,state_json,updated_at) VALUES('primary',?,?)",
                       (canonical_json(state), _now().isoformat()))
            return state
        try:
            state = json.loads(row["state_json"])
            if not isinstance(state, dict):
                raise ValueError("state is not an object")
            return state
        except (ValueError, TypeError, json.JSONDecodeError):
            state = _default_state(self.initial_cash)
            state["kill_switch_reason"] = "corrupt_state"
            self._save(db, state)
            return state

    @staticmethod
    def _save(db: sqlite3.Connection, state: dict[str, Any]) -> None:
        db.execute("UPDATE paper_trading_state SET state_json=?,updated_at=? WHERE state_key='primary'",
                   (canonical_json(state), _now().isoformat()))

    def run(self, decision_id: str, transition: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
        db = _connect(self.db_path)
        try:
            db.execute("BEGIN IMMEDIATE")
            duplicate = db.execute("SELECT result_json FROM paper_trading_decisions WHERE decision_id=?",
                                   (decision_id,)).fetchone()
            if duplicate is not None:
                result = json.loads(duplicate["result_json"])
                db.execute("COMMIT")
                return result
            state = self._locked_state(db)
            result = transition(state)
            self._save(db, state)
            db.execute("INSERT INTO paper_trading_decisions(decision_id,result_json,created_at) VALUES(?,?,?)",
                       (decision_id, canonical_json(result), _now().isoformat()))
            db.execute("COMMIT")
            return result
        except BaseException:
            db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def set_kill_switch(self, stopped: bool, reason: str) -> None:
        db = _connect(self.db_path)
        try:
            db.execute("BEGIN IMMEDIATE")
            state = self._locked_state(db)
            state["stopped"] = stopped
            state["kill_switch_reason"] = reason
            self._save(db, state)
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def state(self) -> dict[str, Any]:
        db = _connect(self.db_path)
        try:
            return self._locked_state(db)
        finally:
            db.close()

    def integrity_check(self) -> str:
        try:
            with _connect(self.db_path) as db:
                rows = db.execute("PRAGMA quick_check").fetchall()
        except sqlite3.Error as exc:
            return f"database error: {exc}"
        problems = [str(row[0]) for row in rows if str(row[0]) != "ok"]
        return "ok" if not problems else " ; ".join(problems)


class SQLiteAgentTranscriptStore:
    """Local SQLite replacement for the CockroachDB agent transcript store."""

    def __init__(self, db_path: str | None = None, initialize: bool = True):
        self.db_path = state_db_path(db_path)
        if initialize:
            self.initialize()

    def connect(self) -> sqlite3.Connection:
        return _connect(self.db_path)

    def initialize(self) -> None:
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS agent_runs (run_id TEXT PRIMARY KEY, status TEXT NOT NULL "
                       "CHECK(status IN ('running','completed','stopped','failed')), created_at TEXT NOT NULL, finished_at TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS agent_transcript (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                       "run_id TEXT NOT NULL REFERENCES agent_runs(run_id), tick INTEGER NOT NULL, phase TEXT NOT NULL, "
                       "content_json TEXT NOT NULL, occurred_at TEXT NOT NULL)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_agent_transcript_run ON agent_transcript(run_id,id)")

    def start_run(self, run_id: str) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO agent_runs(run_id,status,created_at) VALUES(?,?,?)", (run_id, "running", _now().isoformat()))

    def finish_run(self, run_id: str, status: str) -> None:
        with self.connect() as db:
            db.execute("UPDATE agent_runs SET status=?,finished_at=? WHERE run_id=? AND status='running'",
                       (status, _now().isoformat(), run_id))

    def append(self, run_id: str, tick: int, phase: str, content: dict[str, Any]) -> int:
        with self.connect() as db:
            cursor = db.execute("INSERT INTO agent_transcript(run_id,tick,phase,content_json,occurred_at) "
                                "VALUES(?,?,?,?,?) RETURNING id",
                                (run_id, tick, phase, canonical_json(content), _now().isoformat()))
            return int(cursor.fetchone()["id"])

    def steps(self, run_id: str | None = None, after_id: int = 0, before_id: int | None = None,
              desc: bool = False, limit: int = 100) -> list[dict[str, Any]]:
        if desc:
            params: list[Any] = []
            where = []
            if before_id is not None:
                where.append("id < ?")
                params.append(before_id)
            order = "ORDER BY id DESC"
        else:
            params = [after_id]
            where = ["id > ?"]
            order = "ORDER BY id ASC"
        if run_id:
            where.append("run_id = ?")
            params.append(run_id)
        params.append(limit)
        sql = f"SELECT id,run_id,tick,phase,content_json,occurred_at FROM agent_transcript WHERE {' AND '.join(where) or '1=1'} {order} LIMIT ?"
        with self.connect() as db:
            rows = db.execute(sql, tuple(params)).fetchall()
        return [self._row(row) for row in rows]

    def runs(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute("SELECT run_id,status,created_at,finished_at FROM agent_runs ORDER BY created_at DESC LIMIT ?",
                              (limit,)).fetchall()
            counts = {row["run_id"]: int(row["total"]) for row in db.execute(
                "SELECT run_id, COUNT(*) AS total FROM agent_transcript WHERE phase='tick_start' GROUP BY run_id")}
        return [{"run_id": row["run_id"], "status": row["status"], "created_at": row["created_at"],
                 "finished_at": row["finished_at"], "ticks": counts.get(row["run_id"], 0)} for row in rows]

    def run_status(self, run_id: str) -> str | None:
        with self.connect() as db:
            row = db.execute("SELECT status FROM agent_runs WHERE run_id=?", (run_id,)).fetchone()
        return row["status"] if row else None

    def reconcile_running_runs(self, excluding: str | None = None) -> int:
        """Close interrupted runs left 'running' by a killed process."""
        parameters: list[Any] = ["stopped", _now().isoformat()]
        where = ["status='running'"]
        if excluding:
            where.append("run_id != ?")
            parameters.append(excluding)
        with self.connect() as db:
            cursor = db.execute(f"UPDATE agent_runs SET status=?,finished_at=? WHERE {' AND '.join(where)}",
                                tuple(parameters))
        return int(cursor.rowcount or 0)

    def integrity_check(self) -> str:
        with self.connect() as db:
            rows = db.execute("PRAGMA quick_check").fetchall()
        problems = [str(row[0]) for row in rows if str(row[0]) != "ok"]
        return "ok" if not problems else " ; ".join(problems)

    @staticmethod
    def _row(row: sqlite3.Row) -> dict[str, Any]:
        return {"id": int(row["id"]), "run_id": row["run_id"], "tick": int(row["tick"]), "phase": row["phase"],
                "content": json.loads(row["content_json"]), "occurred_at": row["occurred_at"]}