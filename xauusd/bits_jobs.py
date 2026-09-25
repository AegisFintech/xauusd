"""Durable arbitrary-shell execution; the database records intent before spawn."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import sqlite3
import subprocess
import fcntl
from threading import Event, Thread
import time
from uuid import uuid4

from .bits import BitsError, validate_shell_action
from .bits_capabilities import SHELL, shell_environment
from .experiment_registry import canonical_json


class AgentAlreadyRunning(BitsError):
    pass


class AgentLock:
    """Single process per container; the lock is runtime coordination, not state."""
    def __init__(self, transcript):
        database_path = getattr(transcript, "db_path", "state/xauusd_local.db")
        path = Path(database_path).with_suffix(".bits.lock")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = path.open("a")
        try:
            fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.handle.close()
            raise AgentAlreadyRunning("another Bits agent owns this container state",
                                      "agent_already_running") from None

    def close(self):
        self.handle.close()


class SecretFilter:
    """Suppress whole values, not partial/redacted credentials. Not a shell sandbox."""
    def __init__(self, env_file=".env"):
        self.env_file = env_file

    def unsafe(self, text):
        from dotenv import dotenv_values
        values = dict(os.environ)
        if Path(self.env_file).is_file():
            values.update(dotenv_values(self.env_file))
        for key, value in values.items():
            if value and len(value) >= 8 and re.search(r"KEY|TOKEN|SECRET|PASSWORD|PASS$|DATABASE_URL|OPENAI_BASE_URL", key, re.I):
                if value in text or (len(value) >= 16 and value[:16] in text):
                    return True
        return bool(re.search(r"(?im)(?:authorization\s*[:=]|bearer\s+\S+|(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|client_secret)\s*[\"']?\s*[:=]\s*[\"']?\S+|postgres(?:ql)?://[^\s]+:[^\s]+@)", text))

    def clean(self, value):
        if isinstance(value, str):
            return "[output withheld: sensitive content]" if self.unsafe(value) else value
        if isinstance(value, list):
            return [self.clean(v) for v in value]
        if isinstance(value, dict):
            return {k: self.clean(v) for k, v in value.items()}
        return value


class StateTransaction:
    """bits_state access bound to one open connection/transaction."""
    UPSERT = ("INSERT INTO bits_state(state_key,value_json) VALUES(?,?) "
              "ON CONFLICT(state_key) DO UPDATE SET value_json=excluded.value_json")

    def __init__(self, db):
        self.db = db

    def get(self, key, default=None):
        row = self.db.execute("SELECT value_json FROM bits_state WHERE state_key=?", (key,)).fetchone()
        return json.loads(row["value_json"]) if row else default

    def put(self, key, value):
        self.db.execute(self.UPSERT, (key, canonical_json(value)))

    def delete(self, key):
        self.db.execute("DELETE FROM bits_state WHERE state_key=?", (key,))


class BitsStore:
    """Uses the same connection selected for the application's transcript store."""
    def __init__(self, transcript):
        self.transcript = transcript
        with self.db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS bits_jobs (action_key TEXT PRIMARY KEY, job_id TEXT NOT NULL, request_json TEXT NOT NULL, result_json TEXT NOT NULL, status TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS bits_state (state_key TEXT PRIMARY KEY, value_json TEXT NOT NULL)")

    @contextmanager
    def db(self):
        connection = self.transcript.connect()
        try:
            with connection as db:
                yield db
        finally:
            if hasattr(connection, "close"):
                connection.close()

    def get(self, key, default=None):
        with self.db() as db:
            row = db.execute("SELECT value_json FROM bits_state WHERE state_key=?", (key,)).fetchone()
        return json.loads(row["value_json"]) if row else default

    def put(self, key, value):
        with self.db() as db:
            db.execute(StateTransaction.UPSERT, (key, canonical_json(value)))

    def delete(self, key):
        with self.db() as db:
            db.execute("DELETE FROM bits_state WHERE state_key=?", (key,))

    @contextmanager
    def transaction(self):
        """Read-modify-write several state keys atomically.

        SQLite connections run in autocommit mode, so the transaction is explicit;
        a psycopg connection block is already one transaction.
        """
        with self.db() as db:
            explicit = isinstance(db, sqlite3.Connection)
            if explicit:
                db.execute("BEGIN IMMEDIATE")
            try:
                yield StateTransaction(db)
                if explicit:
                    db.execute("COMMIT")
            except BaseException:
                if explicit:
                    db.execute("ROLLBACK")
                raise

    def claim(self, cycle, action):
        key = hashlib.sha256((cycle + ":" + action["id"]).encode()).hexdigest()
        payload = canonical_json(action)
        job_id = uuid4().hex
        result = {"action_id": action["id"], "job_id": job_id, "status": "running",
                  "exit_code": None, "stdout": "", "stderr": "", "truncated": False,
                  "total_bytes": 0}
        with self.db() as db:
            cur = db.execute("INSERT INTO bits_jobs(action_key,job_id,request_json,result_json,status) VALUES(?,?,?,?,?) ON CONFLICT(action_key) DO NOTHING",
                             (key, job_id, payload, canonical_json(result), "running"))
            created = cur.rowcount == 1
            row = db.execute("SELECT request_json,result_json FROM bits_jobs WHERE action_key=?", (key,)).fetchone()
        if row["request_json"] != payload:
            raise BitsError("action ID reused with different command", "action_id_conflict")
        return json.loads(row["result_json"]), created

    def finish(self, result):
        with self.db() as db:
            db.execute("UPDATE bits_jobs SET result_json=?,status=? WHERE job_id=?",
                       (canonical_json(result), result["status"], result["job_id"]))

    def job(self, job_id):
        with self.db() as db:
            row = db.execute("SELECT result_json FROM bits_jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            raise BitsError("unknown shell job", "unknown_job")
        return json.loads(row["result_json"])

    def recover(self):
        with self.db() as db:
            rows = db.execute("SELECT result_json FROM bits_jobs WHERE status='running'").fetchall()
        for row in rows:
            result = json.loads(row["result_json"])
            result.update(status="unknown", stderr="process interrupted; reconcile effects before any retry")
            self.finish(result)
        return len(rows)


class ShellJobs:
    def __init__(self, store, secrets=None):
        self.store = store
        self.secrets = secrets or SecretFilter()
        self.workers = {}
        self.cancelled = Event()

    def start(self, cycle, action):
        if self.cancelled.is_set():
            raise BitsError("shell executor is stopping", "executor_stopping")
        validate_shell_action(action)
        if self.secrets.unsafe(canonical_json(action)):
            raise BitsError("command contains sensitive content", "sensitive_command")
        result, created = self.store.claim(cycle, action)
        if created:
            self.workers = {key: thread for key, thread in self.workers.items() if thread.is_alive()}
            worker = Thread(target=self._run, args=(action["args"], result), daemon=True)
            self.workers[result["job_id"]] = worker
            worker.start()
        return result

    def _run(self, args, result):
        proc = None
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        total = 0
        limit = args["max_output_bytes"]
        deadline = time.monotonic() + args["timeout_sec"]
        state = "failed"
        try:
            # One definition of the job environment; the capability manifest uses it too.
            env = shell_environment(env_file=self.secrets.env_file)
            proc = subprocess.Popen([SHELL, "-c", args["command"]], cwd=args["cwd"], env=env,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, start_new_session=True)
            with selectors.DefaultSelector() as sel:
                for name in buffers:
                    stream = getattr(proc, name)
                    os.set_blocking(stream.fileno(), False)
                    sel.register(stream, selectors.EVENT_READ, name)
                state = "running"
                while sel.get_map():
                    if self.cancelled.is_set() or time.monotonic() >= deadline:
                        state = "cancelled" if self.cancelled.is_set() else "timed_out"
                        break
                    for key, _ in sel.select(0.1):
                        chunk = os.read(key.fileobj.fileno(), 65536)
                        if not chunk:
                            sel.unregister(key.fileobj)
                            continue
                        total += len(chunk)
                        # Retain a little lookahead so a secret spanning the output boundary
                        # is detected before the requested output truncation.
                        remaining = limit + 4096 - sum(map(len, buffers.values()))
                        if remaining > 0:
                            buffers[key.data].extend(chunk[:remaining])
                if state == "running":
                    while proc.poll() is None and not self.cancelled.is_set() and time.monotonic() < deadline:
                        self.cancelled.wait(.1)
                    if self.cancelled.is_set(): state = "cancelled"
                    elif proc.poll() is None: state = "timed_out"
                    else: state = "succeeded" if proc.returncode == 0 else "failed"
        except Exception as exc:
            buffers["stderr"] = bytearray(type(exc).__name__.encode())
        finally:
            if proc:
                # Kill the process group even if the shell exited with background children.
                try: os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                proc.wait()
                proc.stdout.close()
                proc.stderr.close()
            remaining = limit
            for name, value in buffers.items():
                text = value.decode("utf-8", errors="replace")
                if self.secrets.unsafe(text):
                    result[name] = "[output withheld: sensitive content]"
                else:
                    result[name] = bytes(value[:remaining]).decode("utf-8", errors="replace")
                remaining = max(0, remaining - len(value))
            result.update(status=state, exit_code=proc.returncode if proc else None,
                          truncated=total > limit, total_bytes=total)
            self.store.finish(result)

    def stop(self):
        self.cancelled.set()
        for worker in self.workers.values():
            worker.join(timeout=2)
