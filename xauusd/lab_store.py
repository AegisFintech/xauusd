"""Bounded lab state on the same selected backend as paper and transcript."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from functools import wraps
import threading
from typing import Callable

from .bits_jobs import BitsStore, SecretFilter


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def serialized(function):
    @wraps(function)
    def locked(first, *args, **kwargs):
        store = getattr(first, "store", first)
        with store.execution_lock:
            return function(first, *args, **kwargs)
    return locked


class LabStore:
    def __init__(self, transcript):
        self.transcript = transcript
        self.state = BitsStore(transcript)
        self.filter = SecretFilter()
        self.execution_lock = threading.RLock()

    def update(self, key: str, transform: Callable, default=None, observation=None):
        with self.state.transaction() as tx:
            tx.lock("lab:" + key)
            before = tx.get("lab:" + key, default)
            value = transform(before)
            if observation is not None:
                from .lab_statistics import transition
                kind, row = observation
                previous = next((r for r in before or [] if r['id'] == row['id']), None)
                transition(tx, kind, previous, row)
            tx.put("lab:" + key, value)
            return value

    def meta(self, key: str, value=...):
        if value is ...:
            return self.state.get("lab:" + key)
        self.state.put("lab:" + key, value)
        return value

    def event(self, kind: str, summary: str, detail: dict | None = None):
        import json
        safe = self.filter.clean(detail or {})
        if kind in ('instructions','input','assistant','commentary','tool','coding','tool_call','tool_result','compaction','session'):
            from .agent_conversation import ConversationStore
            record = ConversationStore(self).append(kind, {'summary': summary, 'detail': safe},
                safe.get('session_id', ''), safe.get('turn_id', ''))
            safe = {"conversation_id": record['id'], "digest": record['digest'],
                    "preview": json.dumps(safe, ensure_ascii=False, allow_nan=False)[:2000],
                    "session_id": record['session_id'], "turn_id": record['turn_id']}
        if len(json.dumps(safe, allow_nan=False)) > 8000:
            safe = {"output_omitted": True, "reason": "event_size_limit"}
        def add(current):
            current = current or {"next_id": 1, "events": []}
            row = {"id": current["next_id"], "time": timestamp(), "kind": kind[:80],
                   "summary": self.filter.clean(summary)[:1500], "detail": safe}
            return {"next_id": row["id"] + 1, "events": (current["events"] + [row])[-300:]}
        return self.update("events", add)["events"][-1]

    def events(self, after: int = 0, limit: int = 100):
        data = self.meta("events") or {"events": []}
        return [row for row in data["events"] if row["id"] > after][:min(1000, max(1, limit))]

    def job(self, row: dict):
        row = self.filter.clean(row)
        def save(current):
            current = current or []
            result = [dict(item, **row) if item["id"] == row["id"] else item for item in current]
            if not any(item["id"] == row["id"] for item in current):
                result.insert(0, row)
            # Never evict unfinished work.
            return [r for i, r in enumerate(result) if i < 30 or r["state"] == "running"]
        self.update("jobs", save, [], observation=("sessions", row))

    def jobs(self):
        return self.meta("jobs") or []

    def recover_jobs(self) -> int:
        count = 0
        for job in self.jobs():
            if job["state"] == "running":
                self.job({"id": job["id"], "state": "interrupted", "finished_at": timestamp(),
                          "error_code": "research_interrupted_no_replay"})
                if job.get("workspace"):
                    from pathlib import Path
                    from .atomic import atomic_write_json
                    root = Path("data/lab/workspaces").absolute()
                    path = Path(job["workspace"]).absolute()
                    if path.is_relative_to(root) and path.is_dir() and not any(p.is_symlink() for p in (path, *path.parents)):
                        atomic_write_json(path / "completion.json", {"status": "interrupted", "completed_at": timestamp()})
                count += 1
        return count

    @serialized
    def candidate(self, row: dict):
        def save(current):
            current = current or []
            result = [dict(item, **row) if item["id"] == row["id"] else item for item in current]
            if not any(item["id"] == row["id"] for item in current):
                result.insert(0, row)
            return [r for i, r in enumerate(result) if i < 100 or r.get("state") in ("active", "probation", "qualified")]
        self.update("candidates", save, [], observation=("qualification", row))

    def candidates(self):
        return self.meta("candidates") or []

    def active(self):
        active = self.meta("active")
        return next((r for r in self.candidates() if r["id"] == active and r.get("state") == "active"), None)

    def memory(self, value=...):
        if value is ...:
            return self.meta("memory") or {"conclusion": "No completed research yet.", "next": "Establish baseline."}
        safe = self.filter.clean({key: str(value.get(key, ""))[:4000] for key in ("conclusion", "next")})
        return self.meta("memory", safe)

    def prune_monitor_history(self, now: datetime) -> int:
        """Expire old price-mark results, never actual trade idempotency keys.

        Monitor observations older than seven days cannot pass the shared
        freshness gate. Their replay rows confer no broker/trade authority.
        SQLite reuses freed pages; no blocking VACUUM is run on the live store.
        """
        from .database_retention import prune_monitor_records
        return prune_monitor_records(self,now)

    @serialized
    def prune_research_evidence(self, lab_root="data/lab") -> dict:
        """Daily bounded cleanup of inactive research evidence only.

        Compact summaries and namespace deletion commit together. Real paper
        accounts and order/trade idempotency namespaces are never queried here.
        """
        import math
        import re
        from .retention import prune_lab_dataset_archives

        def number(value):
            return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None

        removed = 0
        errors = []
        preserved_versions = set()
        valid_references = True
        with self.state.transaction() as tx:
            tx.lock("lab:candidates")
            rows = tx.get("lab:candidates", [])
            if not isinstance(rows, list) or any(not isinstance(row, dict) or not isinstance(row.get("id"), str) for row in rows):
                return {"removed_shadows": 0, "deleted_dataset_bytes": 0, "errors": ["candidate_metadata_invalid"]}
            candidates = {row["id"]: row for row in rows}
            active_id = tx.get("lab:active")
            protected = {row["id"] for row in rows if row.get("state") in ("active", "probation", "qualified")}
            if isinstance(active_id, str):
                protected.add(active_id)
                if active_id not in candidates: valid_references = False
            current = tx.get("lab:dataset")
            history = tx.get("lab:dataset_history", [])
            if current is not None and not isinstance(current, dict): valid_references = False
            if not isinstance(history, list) or any(not isinstance(item, dict) for item in history):
                valid_references = False
                history = []
            if valid_references:
                manifests = history[-12:] + ([current] if current else [])
                versions = [item.get("version") for item in manifests]
                if any(not isinstance(version, str) or not re.fullmatch("[a-f0-9]{64}", version) for version in versions):
                    valid_references = False
                else:
                    preserved_versions.update(versions)
                    if len(history) > 12: tx.put("lab:dataset_history", history[-12:])
            for row in rows:
                if row["id"] in protected:
                    version = row.get("dataset_version")
                    if isinstance(version, str) and re.fullmatch("[a-f0-9]{64}", version):
                        preserved_versions.add(version)
                    else: valid_references = False
            summaries = tx.get("lab:research_evidence_history", [])
            if not isinstance(summaries, list): summaries = []
            keys = tx.db.execute("SELECT state_key FROM bits_state WHERE state_key LIKE 'lab:shadow:%' ORDER BY state_key LIMIT 1000").fetchall()
            for record in keys:
                key = record["state_key"]
                candidate_id = key[len("lab:shadow:"):]
                row = candidates.get(candidate_id)
                if candidate_id in protected: continue
                if row is not None and row.get("state") not in ("retired", "rejected", "rejected_forward"):
                    continue
                shadow = tx.get(key)
                if not isinstance(shadow, dict):
                    errors.append("shadow_state_invalid"); continue
                pnl = shadow.get("closed_pnl", [])
                if not isinstance(pnl, list) or any(number(value) is None for value in pnl):
                    errors.append("shadow_metrics_invalid"); continue
                values = [float(value) for value in pnl]
                net_profit = sum(values)
                if not math.isfinite(net_profit):
                    errors.append("shadow_metrics_invalid"); continue
                summary = {"id": candidate_id, "state": row.get("state") if row else "evicted",
                           "dataset_version": row.get("dataset_version") if row else None,
                           "recorded_at": timestamp(),
                           "metrics": {"trades": len(values), "net_profit": net_profit,
                                       "expectancy": net_profit / len(values) if values else None,
                                       "max_drawdown": number(shadow.get("maximum_drawdown"))}}
                forward = row.get("forward") if row else None
                if isinstance(forward, dict) and isinstance(forward.get("metrics"), dict):
                    summary["metrics"].update({k: number(v) for k, v in forward["metrics"].items()
                                               if k in ("trades", "net_profit", "expectancy", "profit_factor", "max_drawdown")})
                summaries = [r for r in summaries if isinstance(r, dict) and r.get("id") != candidate_id] + [summary]
                summaries = summaries[-100:]
                tx.put("lab:research_evidence_history", summaries)
                tx.delete(key)
                removed += 1
        dataset_result = (prune_lab_dataset_archives(lab_root, preserved_versions) if valid_references else
                          {"deleted_dataset_bytes": 0, "deleted_datasets": 0, "errors": ["dataset_reference_invalid"]})
        return {**dataset_result, "removed_shadows": removed,
                "errors": sorted(set(errors + dataset_result["errors"]))}

    def equity(self, row: dict | None = None):
        if row is None:
            return self.meta("equity") or []
        def add(current):
            current = current or []
            # At most one mark per minute, 7 days of minute observations.
            if current and current[-1]["time"][:16] == row["time"][:16]:
                return current[:-1] + [row]
            return (current + [row])[-10080:]
        return self.update("equity", add, [])
