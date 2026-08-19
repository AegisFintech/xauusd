from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sqlite3
from typing import Any, Literal

from .research import StrategySpec


ExperimentStatus = Literal["queued", "running", "completed", "failed", "cancelled"]
TERMINAL_STATUSES = {"completed", "failed", "cancelled"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class ExperimentSpec:
    strategy_family: str
    formula: str
    parameters: dict[str, Any]
    dataset_version: str
    dataset_fingerprint: str
    engine_version: str
    cost_model_version: str
    code_commit: str | None = None

    def identity(self) -> dict:
        return {key: value for key, value in asdict(self).items() if key != "code_commit"}

    @property
    def fingerprint(self) -> str:
        return hashlib.sha256(canonical_json(self.identity()).encode()).hexdigest()


class ExperimentRegistry:
    def __init__(self, path: Path = Path("data/experiments/registry.sqlite3"), initialize: bool = True):
        self.path = path
        if initialize:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    def initialize(self) -> None:
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT NOT NULL UNIQUE,
                strategy_family TEXT NOT NULL,
                formula TEXT NOT NULL,
                parameters_json TEXT NOT NULL,
                dataset_version TEXT NOT NULL,
                dataset_fingerprint TEXT NOT NULL,
                engine_version TEXT NOT NULL,
                cost_model_version TEXT NOT NULL,
                code_commit TEXT,
                status TEXT NOT NULL CHECK(status IN ('queued','running','completed','failed','cancelled')),
                priority INTEGER NOT NULL DEFAULT 0,
                worker_id TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                heartbeat_at TEXT,
                metrics_json TEXT,
                validation_json TEXT,
                artifacts_json TEXT,
                error TEXT,
                promoted INTEGER NOT NULL DEFAULT 0 CHECK(promoted IN (0,1))
            );
            CREATE INDEX IF NOT EXISTS idx_experiments_queue ON experiments(status, priority DESC, id);
            CREATE INDEX IF NOT EXISTS idx_experiments_family ON experiments(strategy_family, status);
            CREATE TABLE IF NOT EXISTS experiment_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER NOT NULL REFERENCES experiments(id),
                occurred_at TEXT NOT NULL,
                event TEXT NOT NULL,
                payload_json TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_events_experiment ON experiment_events(experiment_id, id);
            CREATE TABLE IF NOT EXISTS champion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_version TEXT NOT NULL,
                experiment_id INTEGER NOT NULL REFERENCES experiments(id),
                previous_experiment_id INTEGER REFERENCES experiments(id),
                promoted_at TEXT NOT NULL,
                validation_score REAL NOT NULL,
                holdout_score REAL NOT NULL,
                holdout_metrics_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_champion_dataset ON champion_history(dataset_version,id);
            """)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def register(self, spec: ExperimentSpec, priority: int = 0) -> tuple[dict, bool]:
        now = self._now()
        with self.connect() as db:
            cursor = db.execute("""INSERT OR IGNORE INTO experiments
                (fingerprint,strategy_family,formula,parameters_json,dataset_version,dataset_fingerprint,
                 engine_version,cost_model_version,code_commit,status,priority,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,'queued',?,?)""",
                (spec.fingerprint, spec.strategy_family, spec.formula, canonical_json(spec.parameters),
                 spec.dataset_version, spec.dataset_fingerprint, spec.engine_version,
                 spec.cost_model_version, spec.code_commit, priority, now))
            created = cursor.rowcount == 1
            row = db.execute("SELECT * FROM experiments WHERE fingerprint=?", (spec.fingerprint,)).fetchone()
            if created:
                self._event(db, row["id"], "registered", {"priority": priority})
            return self._decode(row), created

    def claim_next(self, worker_id: str) -> dict | None:
        now = self._now()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id FROM experiments WHERE status='queued' ORDER BY priority DESC,id LIMIT 1").fetchone()
            if row is None:
                return None
            db.execute("UPDATE experiments SET status='running',worker_id=?,started_at=?,heartbeat_at=? WHERE id=? AND status='queued'",
                       (worker_id, now, now, row["id"]))
            claimed = db.execute("SELECT * FROM experiments WHERE id=?", (row["id"],)).fetchone()
            self._event(db, row["id"], "claimed", {"worker_id": worker_id})
            return self._decode(claimed)

    def heartbeat(self, experiment_id: int, worker_id: str) -> None:
        with self.connect() as db:
            cursor = db.execute("UPDATE experiments SET heartbeat_at=? WHERE id=? AND status='running' AND worker_id=?",
                                (self._now(), experiment_id, worker_id))
            if cursor.rowcount != 1:
                raise ValueError("experiment is not owned by this worker")

    def complete(self, experiment_id: int, worker_id: str, metrics: dict,
                 validation: dict | None = None, artifacts: dict | None = None, promoted: bool = False) -> dict:
        return self._finish(experiment_id, worker_id, "completed", metrics, validation, artifacts, None, promoted)

    def fail(self, experiment_id: int, worker_id: str, error: str, artifacts: dict | None = None) -> dict:
        return self._finish(experiment_id, worker_id, "failed", None, None, artifacts, error, False)

    def requeue(self,experiment_id: int,worker_id: str,error: str) -> dict:
        with self.connect() as db:
            cursor=db.execute("""UPDATE experiments SET status='queued',worker_id=NULL,started_at=NULL,
                heartbeat_at=NULL,error=? WHERE id=? AND status='running' AND worker_id=?""",
                (error,experiment_id,worker_id))
            if cursor.rowcount!=1: raise ValueError("experiment is not owned by this worker or is no longer running")
            self._event(db,experiment_id,"requeued_remote_error",{"worker_id":worker_id,"error":error})
            return self.get(experiment_id,db)

    def _finish(self, experiment_id: int, worker_id: str, status: ExperimentStatus, metrics, validation,
                artifacts, error, promoted: bool) -> dict:
        now = self._now()
        with self.connect() as db:
            cursor = db.execute("""UPDATE experiments SET status=?,finished_at=?,heartbeat_at=?,metrics_json=?,
                validation_json=?,artifacts_json=?,error=?,promoted=?
                WHERE id=? AND status='running' AND worker_id=?""",
                (status, now, now, canonical_json(metrics) if metrics is not None else None,
                 canonical_json(validation) if validation is not None else None,
                 canonical_json(artifacts) if artifacts is not None else None, error, int(promoted),
                 experiment_id, worker_id))
            if cursor.rowcount != 1:
                raise ValueError("experiment is not owned by this worker or is no longer running")
            self._event(db, experiment_id, status, {"error": error, "promoted": promoted})
            return self.get(experiment_id, db)

    def recover_stale(self, stale_before: datetime) -> int:
        threshold = stale_before.astimezone(timezone.utc).isoformat()
        now = self._now()
        with self.connect() as db:
            rows = db.execute("SELECT id,worker_id FROM experiments WHERE status='running' AND heartbeat_at<?", (threshold,)).fetchall()
            for row in rows:
                db.execute("UPDATE experiments SET status='queued',worker_id=NULL,started_at=NULL,heartbeat_at=NULL,error=? WHERE id=?",
                           (f"recovered stale worker {row['worker_id']} at {now}", row["id"]))
                self._event(db, row["id"], "requeued_stale", {"previous_worker": row["worker_id"]})
            return len(rows)

    def recover_other_workers(self, active_worker_id: str) -> int:
        """Recover claims left by a previous instance of the single system worker."""
        now=self._now()
        with self.connect() as db:
            rows=db.execute("SELECT id,worker_id FROM experiments WHERE status='running' AND worker_id<>?",
                            (active_worker_id,)).fetchall()
            for row in rows:
                db.execute("UPDATE experiments SET status='queued',worker_id=NULL,started_at=NULL,heartbeat_at=NULL,error=? WHERE id=?",
                           (f"recovered replaced worker {row['worker_id']} at {now}",row["id"]))
                self._event(db,row["id"],"requeued_replaced_worker",{"previous_worker":row["worker_id"]})
            return len(rows)

    def recover_worker_prefix(self,prefix: str,active_prefix: str | None=None) -> int:
        """Requeue leases from replaced instances of a named worker pool."""
        now=self._now(); pattern=f"{prefix}%"
        with self.connect() as db:
            if active_prefix:
                rows=db.execute("SELECT id,worker_id FROM experiments WHERE status='running' AND worker_id LIKE ? AND worker_id NOT LIKE ?",
                                (pattern,f"{active_prefix}%")).fetchall()
            else:
                rows=db.execute("SELECT id,worker_id FROM experiments WHERE status='running' AND worker_id LIKE ?",(pattern,)).fetchall()
            for row in rows:
                db.execute("UPDATE experiments SET status='queued',worker_id=NULL,started_at=NULL,heartbeat_at=NULL,error=? WHERE id=?",
                           (f"recovered replaced pool worker {row['worker_id']} at {now}",row["id"]))
                self._event(db,row["id"],"requeued_replaced_pool_worker",{"previous_worker":row["worker_id"]})
            return len(rows)

    def get(self, experiment_id: int, db: sqlite3.Connection | None = None) -> dict:
        if db is not None:
            row = db.execute("SELECT * FROM experiments WHERE id=?", (experiment_id,)).fetchone()
        else:
            with self.connect() as connection:
                row = connection.execute("SELECT * FROM experiments WHERE id=?", (experiment_id,)).fetchone()
        if row is None:
            raise KeyError(experiment_id)
        return self._decode(row)

    def list(self, status: ExperimentStatus | None = None, limit: int = 100, offset: int = 0) -> list[dict]:
        query = "SELECT * FROM experiments"; params: list[Any] = []
        if status:
            query += " WHERE status=?"; params.append(status)
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"; params.extend((limit, offset))
        with self.connect() as db:
            return [self._decode(row) for row in db.execute(query, params).fetchall()]

    def summary(self) -> dict:
        with self.connect() as db:
            counts = {row["status"]: row["count"] for row in db.execute(
                "SELECT status,COUNT(*) count FROM experiments GROUP BY status")}
            families = db.execute("SELECT COUNT(DISTINCT strategy_family) count FROM experiments").fetchone()["count"]
            promoted = db.execute("SELECT COUNT(*) count FROM experiments WHERE promoted=1").fetchone()["count"]
            return {"total": sum(counts.values()), "by_status": counts, "strategy_families": families, "promoted": promoted}

    def count(self, status: ExperimentStatus | None = None, dataset_version: str | None = None) -> int:
        clauses=[]; params=[]
        if status: clauses.append("status=?"); params.append(status)
        if dataset_version: clauses.append("dataset_version=?"); params.append(dataset_version)
        query="SELECT COUNT(*) count FROM experiments"+(" WHERE "+" AND ".join(clauses) if clauses else "")
        with self.connect() as db:
            return int(db.execute(query,params).fetchone()["count"])

    def leaderboard(self, limit: int = 25) -> list[dict]:
        with self.connect() as db:
            rows=db.execute("""SELECT * FROM experiments WHERE status='completed' AND validation_json IS NOT NULL
                ORDER BY json_extract(validation_json,'$.score') DESC LIMIT ?""",(limit,)).fetchall()
            return [self._decode(row) for row in rows]

    def champion(self, dataset_version: str) -> dict | None:
        with self.connect() as db:
            row=db.execute("SELECT * FROM champion_history WHERE dataset_version=? ORDER BY id DESC LIMIT 1",
                           (dataset_version,)).fetchone()
            return self._decode_champion(row) if row else None

    def champion_history(self, dataset_version: str, limit: int = 100) -> list[dict]:
        with self.connect() as db:
            return [self._decode_champion(row) for row in db.execute(
                "SELECT * FROM champion_history WHERE dataset_version=? ORDER BY id DESC LIMIT ?",
                (dataset_version,limit)).fetchall()]

    def promote_champion(self, dataset_version: str, experiment_id: int, validation_score: float,
                         holdout_score: float, holdout_metrics: dict) -> dict:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            previous=db.execute("SELECT experiment_id,holdout_score FROM champion_history WHERE dataset_version=? ORDER BY id DESC LIMIT 1",
                                (dataset_version,)).fetchone()
            if previous and float(previous["holdout_score"]) >= holdout_score:
                raise ValueError("challenger does not beat champion holdout score")
            db.execute("UPDATE experiments SET promoted=0 WHERE dataset_version=? AND promoted=1",(dataset_version,))
            db.execute("UPDATE experiments SET promoted=1 WHERE id=?",(experiment_id,))
            cursor=db.execute("""INSERT INTO champion_history
                (dataset_version,experiment_id,previous_experiment_id,promoted_at,validation_score,holdout_score,holdout_metrics_json)
                VALUES(?,?,?,?,?,?,?)""",(dataset_version,experiment_id,previous["experiment_id"] if previous else None,
                self._now(),validation_score,holdout_score,canonical_json(holdout_metrics)))
            self._event(db,experiment_id,"champion_promoted",{"previous_experiment_id":previous["experiment_id"] if previous else None,
                                                               "holdout_score":holdout_score})
            row=db.execute("SELECT * FROM champion_history WHERE id=?",(cursor.lastrowid,)).fetchone()
            return self._decode_champion(row)

    def events(self, experiment_id: int) -> list[dict]:
        with self.connect() as db:
            return [{"id": row["id"], "occurred_at": row["occurred_at"], "event": row["event"],
                     "payload": json.loads(row["payload_json"]) if row["payload_json"] else None}
                    for row in db.execute("SELECT * FROM experiment_events WHERE experiment_id=? ORDER BY id", (experiment_id,))]

    def _event(self, db: sqlite3.Connection, experiment_id: int, event: str, payload: dict | None = None) -> None:
        db.execute("INSERT INTO experiment_events(experiment_id,occurred_at,event,payload_json) VALUES(?,?,?,?)",
                   (experiment_id, self._now(), event, canonical_json(payload) if payload is not None else None))

    @staticmethod
    def _decode(row: sqlite3.Row) -> dict:
        result = dict(row)
        for key in ("parameters_json", "metrics_json", "validation_json", "artifacts_json"):
            result[key.removesuffix("_json")] = json.loads(result.pop(key)) if result[key] else None
        result["promoted"] = bool(result["promoted"])
        return result

    @staticmethod
    def _decode_champion(row: sqlite3.Row) -> dict:
        result=dict(row); result["holdout_metrics"]=json.loads(result.pop("holdout_metrics_json")); return result


def from_strategy(spec: StrategySpec, dataset_manifest: dict, code_commit: str | None = None) -> ExperimentSpec:
    formula = {
        "mean_reversion": "hold(zscore_20 < -entry_z, zscore_20 > entry_z, exit=abs(zscore_20)<exit_z)",
        "momentum": "sign((ema_8-ema_34)/atr_14, threshold_atr)",
        "breakout": "hold(close>channel_high_30, close<channel_low_30, exit=ema_20_cross)",
        "micro_trend": "sign((ema_5-ema_20)/atr_14, min_strength)",
        "volatility_expansion": "direction if range_ratio>=threshold and body_fraction>=threshold else flat",
        "session_momentum": "sign(return_15) within UTC session",
        "regime_switch": "trend signal when strength>=threshold else zscore reversion",
        "autocorrelation_regime": "follow returns in positive rolling autocorrelation; fade in negative autocorrelation",
        "multi_horizon_momentum": "trade only when fast and slow ATR-normalized returns agree",
        "quantile_reversion": "fade causal rolling return-tail quantiles and exit near the median",
        "volatility_adjusted_trend": "sign(return_period / rolling_return_volatility, threshold)",
    }.get(spec.name, spec.name)
    return ExperimentSpec(spec.name, formula, dict(spec.parameters), dataset_manifest["version"],
                          dataset_manifest["fingerprint"], dataset_manifest["engine_version"],
                          dataset_manifest["cost_model_version"], code_commit)
