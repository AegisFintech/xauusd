"""Atomic on-disk heartbeat for the continuous agent.

The agent writes no console/journald logs (AGENTS.md); this file is the durable,
restart-loud observability signal the live view and operator checks read.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AGENT_STATUS_FILE = "reports/agent_status.json"


def agent_status_path() -> Path:
    return Path(os.getenv("AGENT_STATUS_FILE", AGENT_STATUS_FILE))


def write_status(payload: dict[str, Any], path: str | Path | None = None) -> None:
    """Persist one heartbeat atomically (temp file + fsync + rename)."""
    target = Path(path) if path is not None else agent_status_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    body = dict(payload)
    body.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())
    temporary = target.with_name(target.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(body, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(target)


def bits_alerts(heartbeat: dict[str, Any] | None) -> list[str]:
    """Operator alerts derived from Bits heartbeat fields.

    Pure so it is testable without the web stack; a healthy heartbeat alone does
    not mean research is progressing, so these name the specific blocker.
    """
    heartbeat = heartbeat or {}
    alerts: list[str] = []
    memory = heartbeat.get("memory") or {}
    if memory.get("needs_repair"):
        error = memory.get("last_error") or {}
        alerts.append(f"memory writes failing: {memory.get('consecutive_failures', 0)} consecutive rejected writes "
                      f"(last {error.get('code') or 'unknown'} at {error.get('path') or '$'}); stored notes unchanged")
    return alerts


def read_status(path: str | Path | None = None) -> dict[str, Any] | None:
    target = Path(path) if path is not None else agent_status_path()
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except (OSError, ValueError):
        return None