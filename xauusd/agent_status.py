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
        last = f"last {error.get('code') or 'unknown'} at {error.get('path') or '$'}"
        if "open_drafts" in memory:
            reasons = ", ".join(memory.get("repair_reasons") or []) or "unresolved"
            alerts.append(f"memory drafts need repair: {memory['open_drafts']} unresolved rejected write(s), "
                          f"{memory.get('consecutive_failures', 0)} consecutive rejections ({reasons}; {last})")
        else:  # heartbeat written by the previous release
            alerts.append(f"memory writes failing: {memory.get('consecutive_failures', 0)} consecutive rejected "
                          f"writes ({last}); stored notes unchanged")
    capabilities = heartbeat.get("capabilities") or {}
    if capabilities.get("status") == "failed":
        alerts.append(f"Bits shell capability discovery failed ({capabilities.get('error_code') or 'unknown error'}); "
                      "tool availability is unknown")
    elif capabilities.get("status") == "partial":
        sections = ", ".join(f"{error.get('section')} ({error.get('error_code')})"
                             for error in capabilities.get("errors") or []) or "unknown sections"
        alerts.append("Bits shell capability discovery incomplete: " + sections)
    for error in capabilities.get("configuration_errors") or []:
        alerts.append(f"Bits shell configuration: {error.get('variable', 'BITS_SHELL_EXTRA_PATH')} entry "
                      f"{error.get('entry')} ignored ({error.get('reason')})")
    if capabilities.get("required_missing"):
        alerts.append("Bits shell is missing required executables: " + ", ".join(capabilities["required_missing"]))
    if capabilities.get("observed_missing"):
        alerts.append("Bits shell jobs hit missing executables: " + ", ".join(capabilities["observed_missing"])
                      + " (see capabilities fallbacks)")
    return alerts


def read_status(path: str | Path | None = None) -> dict[str, Any] | None:
    target = Path(path) if path is not None else agent_status_path()
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else None
    except (OSError, ValueError):
        return None