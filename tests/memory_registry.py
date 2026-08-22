from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json


class MemoryRegistry:
    """Small behavioral registry double; production always uses CockroachDB."""

    def __init__(self):
        self.rows = []
        self.event_rows = []
        self.champions = []

    def connect(self):
        return MemoryConnection(self)

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    def register(self, spec, priority=0):
        existing = next((row for row in self.rows if row["fingerprint"] == spec.fingerprint), None)
        if existing:
            return deepcopy(existing), False
        row = {"id": len(self.rows) + 1, "fingerprint": spec.fingerprint,
               "strategy_family": spec.strategy_family, "formula": spec.formula,
               "parameters": deepcopy(spec.parameters), "dataset_version": spec.dataset_version,
               "dataset_fingerprint": spec.dataset_fingerprint, "engine_version": spec.engine_version,
               "cost_model_version": spec.cost_model_version, "code_commit": spec.code_commit,
               "status": "queued", "priority": priority, "worker_id": None,
               "created_at": self._now(), "started_at": None, "finished_at": None,
               "heartbeat_at": None, "metrics": None, "validation": None, "artifacts": None,
               "error": None, "promoted": False, "retry_count": 0, "failure_code": None}
        self.rows.append(row)
        self._event(row["id"], "registered", {"priority": priority})
        return deepcopy(row), True

    def claim_next(self, worker_id):
        queued = sorted((row for row in self.rows if row["status"] == "queued"),
                        key=lambda row: (-row["priority"], row["id"]))
        if not queued:
            return None
        row = queued[0]; now = self._now()
        row.update(status="running", worker_id=worker_id, started_at=now, heartbeat_at=now)
        self._event(row["id"], "claimed", {"worker_id": worker_id})
        return deepcopy(row)

    def heartbeat(self, experiment_id, worker_id):
        row = self._owned(experiment_id, worker_id)
        row["heartbeat_at"] = self._now()

    def complete(self, experiment_id, worker_id, metrics, validation=None, artifacts=None, promoted=False):
        return self._finish(experiment_id, worker_id, "completed", metrics, validation, artifacts, None, promoted)

    def fail(self, experiment_id, worker_id, error, artifacts=None):
        return self._finish(experiment_id, worker_id, "failed", None, None, artifacts, error, False)

    def _finish(self, experiment_id, worker_id, status, metrics, validation, artifacts, error, promoted):
        row = self._owned(experiment_id, worker_id); now = self._now()
        row.update(status=status, finished_at=now, heartbeat_at=now, metrics=deepcopy(metrics),
                   validation=deepcopy(validation), artifacts=deepcopy(artifacts), error=error,
                   promoted=bool(promoted))
        self._event(experiment_id, status, {"error": error, "promoted": promoted})
        return deepcopy(row)

    def requeue(self, experiment_id, worker_id, error, failure_code="REMOTE_ERROR", max_retries=None):
        row = self._owned(experiment_id, worker_id); row["retry_count"] += 1
        terminal = max_retries is not None and row["retry_count"] >= max_retries
        row.update(status="failed" if terminal else "queued", worker_id=None, started_at=None,
                   heartbeat_at=None, finished_at=self._now() if terminal else None,
                   error=error, failure_code=failure_code)
        self._event(experiment_id, "failed_retry_limit" if terminal else "requeued_remote_error", {})
        return deepcopy(row)

    def recover_stale(self, stale_before):
        threshold = stale_before.astimezone(timezone.utc).isoformat()
        return self._recover(lambda row: row["status"] == "running" and row["heartbeat_at"] < threshold,
                             "requeued_stale")

    def recover_other_workers(self, active_worker_id):
        return self._recover(lambda row: row["status"] == "running" and row["worker_id"] != active_worker_id,
                             "requeued_replaced_worker")

    def recover_worker_prefix(self, prefix, active_prefix=None):
        return self._recover(lambda row: row["status"] == "running" and row["worker_id"].startswith(prefix)
                             and not (active_prefix and row["worker_id"].startswith(active_prefix)),
                             "requeued_replaced_pool_worker")

    def _recover(self, predicate, event):
        rows = [row for row in self.rows if predicate(row)]
        for row in rows:
            previous = row["worker_id"]
            row.update(status="queued", worker_id=None, started_at=None, heartbeat_at=None,
                       error=f"recovered worker {previous}")
            self._event(row["id"], event, {"previous_worker": previous})
        return len(rows)

    def get(self, experiment_id, db=None):
        row = next((row for row in self.rows if row["id"] == experiment_id), None)
        if row is None:
            raise KeyError(experiment_id)
        return deepcopy(row)

    def list(self, status=None, limit=100, offset=0):
        rows = [row for row in self.rows if status is None or row["status"] == status]
        return deepcopy(sorted(rows, key=lambda row: row["id"], reverse=True)[offset:offset + limit])

    def summary(self):
        counts = {}
        for row in self.rows:
            counts[row["status"]] = counts.get(row["status"], 0) + 1
        return {"total": len(self.rows), "by_status": counts,
                "strategy_families": len({row["strategy_family"] for row in self.rows}),
                "promoted": sum(row["promoted"] for row in self.rows)}

    def count(self, status=None, dataset_version=None):
        return sum((status is None or row["status"] == status) and
                   (dataset_version is None or row["dataset_version"] == dataset_version) for row in self.rows)

    def leaderboard(self, limit=25):
        rows = [row for row in self.rows if row["status"] == "completed" and row["validation"]]
        return deepcopy(sorted(rows, key=lambda row: row["validation"].get("score", float("-inf")), reverse=True)[:limit])

    def champion(self, dataset_version):
        rows = [row for row in self.champions if row["dataset_version"] == dataset_version]
        return deepcopy(rows[-1]) if rows else None

    def champion_history(self, dataset_version, limit=100):
        rows = [row for row in self.champions if row["dataset_version"] == dataset_version]
        return deepcopy(list(reversed(rows))[:limit])

    def promote_champion(self, dataset_version, experiment_id, validation_score, holdout_score, holdout_metrics):
        previous = self.champion(dataset_version)
        if previous and previous["holdout_score"] >= holdout_score:
            raise ValueError("challenger does not beat champion holdout score")
        for row in self.rows:
            if row["dataset_version"] == dataset_version:
                row["promoted"] = row["id"] == experiment_id
        item = {"id": len(self.champions) + 1, "dataset_version": dataset_version,
                "experiment_id": experiment_id,
                "previous_experiment_id": previous["experiment_id"] if previous else None,
                "promoted_at": self._now(), "validation_score": validation_score,
                "holdout_score": holdout_score, "holdout_metrics": deepcopy(holdout_metrics)}
        self.champions.append(item); self._event(experiment_id, "champion_promoted", {})
        return deepcopy(item)

    def events(self, experiment_id):
        return deepcopy([row for row in self.event_rows if row["experiment_id"] == experiment_id])

    def _owned(self, experiment_id, worker_id):
        row = next((row for row in self.rows if row["id"] == experiment_id and
                    row["status"] == "running" and row["worker_id"] == worker_id), None)
        if row is None:
            raise ValueError("experiment is not owned by this worker or is no longer running")
        return row

    def _event(self, experiment_id, event, payload):
        self.event_rows.append({"id": len(self.event_rows) + 1, "experiment_id": experiment_id,
                                "occurred_at": self._now(), "event": event, "payload": deepcopy(payload)})


class MemoryCursor:
    def __init__(self, rows=None, rowcount=0):
        self.rows = rows or []
        self.rowcount = rowcount

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


class MemoryConnection:
    def __init__(self, registry):
        self.registry = registry

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    @staticmethod
    def _encoded(row):
        result = deepcopy(row)
        for name in ("parameters", "metrics", "validation", "artifacts"):
            result[name + "_json"] = json.dumps(result.pop(name)) if result.get(name) is not None else None
        result["promoted"] = int(result["promoted"])
        return result

    def execute(self, query, params=()):
        normalized = " ".join(query.split())
        if normalized == "SELECT 1":
            return MemoryCursor([{"one": 1}])
        if normalized.startswith("SELECT COUNT(*) total"):
            rows = self.registry.rows
            result = {"total": len(rows), "completed": 0, "failed": 0, "queued": 0, "running": 0,
                      "retried": sum(row["retry_count"] > 0 for row in rows),
                      "retries": sum(row["retry_count"] for row in rows),
                      "distinct_fingerprints": len({row["fingerprint"] for row in rows})}
            for status in ("completed", "failed", "queued", "running"):
                result[status] = sum(row["status"] == status for row in rows)
            return MemoryCursor([result])
        if normalized.startswith("SELECT * FROM experiments ORDER BY id"):
            return MemoryCursor([self._encoded(row) for row in self.registry.rows])
        if normalized.startswith("SELECT * FROM experiment_events ORDER BY id"):
            rows = [{**row, "payload_json": json.dumps(row["payload"])} for row in self.registry.event_rows]
            return MemoryCursor(rows)
        if normalized.startswith("SELECT * FROM champion_history ORDER BY id"):
            rows = [{**row, "holdout_metrics_json": json.dumps(row["holdout_metrics"])}
                    for row in self.registry.champions]
            return MemoryCursor(rows)
        if normalized.startswith("SELECT id,artifacts_json FROM experiments"):
            rows = [{"id": row["id"], "artifacts_json": json.dumps(row["artifacts"])}
                    for row in self.registry.rows if row["artifacts"] is not None]
            return MemoryCursor(rows)
        if normalized.startswith("SELECT id,fingerprint,status,promoted,validation_json,artifacts_json"):
            rows = [{"id": row["id"], "fingerprint": row["fingerprint"], "status": row["status"],
                     "promoted": int(row["promoted"]), "validation_json": json.dumps(row["validation"]),
                     "artifacts_json": json.dumps(row["artifacts"])} for row in self.registry.rows
                    if row["status"] == "completed" and row["artifacts"] is not None]
            return MemoryCursor(rows)
        if normalized.startswith("SELECT artifacts_json FROM experiments WHERE id="):
            eid = params[0]
            row = next((row for row in self.registry.rows if row["id"] == eid and row["status"] == "completed"), None)
            return MemoryCursor([{"artifacts_json": json.dumps(row["artifacts"])}] if row else [])
        if normalized.startswith("UPDATE experiments SET artifacts_json="):
            encoded, eid = params
            row = next(row for row in self.registry.rows if row["id"] == eid)
            row["artifacts"] = json.loads(encoded)
            return MemoryCursor(rowcount=1)
        if normalized.startswith("INSERT INTO experiment_events"):
            eid, occurred_at, event, payload = params
            self.registry.event_rows.append({"id": len(self.registry.event_rows) + 1,
                "experiment_id": eid, "occurred_at": occurred_at, "event": event,
                "payload": json.loads(payload) if payload else None})
            return MemoryCursor(rowcount=1)
        raise AssertionError(f"unsupported memory query: {normalized}")
