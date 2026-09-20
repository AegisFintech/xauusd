"""Crash-safe backup and restore for the local SQLite state database.

Mirrors the OperationsManager backup discipline (manifest + sha256, atomic
replaces) but targets the local paper/transcript database. Recovery is a
manual operator action: nothing here ever overwrites a live store without an
explicit restore command.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .local_state import state_db_path

DEFAULT_BACKUP_ROOT = "backups/local-state"

MANIFEST_NAME = "manifest.json"
ARCHIVE_NAME = "state.db.gz"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _quick_check(db_path: str | Path) -> str:
    connection = sqlite3.connect(str(db_path), isolation_level=None)
    try:
        try:
            rows = connection.execute("PRAGMA quick_check").fetchall()
        except sqlite3.DatabaseError as exc:
            raise ValueError(f"quick_check failed: {exc}") from exc
    finally:
        connection.close()
    problems = [str(row[0]) for row in rows if str(row[0]) != "ok"]
    return "ok" if not problems else " ; ".join(problems)


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True))
    temporary.replace(path)


def backup_local_state(source_db: str | Path | None = None,
                       dest_root: str | Path = DEFAULT_BACKUP_ROOT) -> dict[str, Any]:
    """Snapshot the live SQLite database and verify it before returning."""
    source_db = Path(source_db or state_db_path())
    if not source_db.is_file():
        raise FileNotFoundError(f"source state database not found: {source_db}")
    destination_root = Path(dest_root)
    run_id = _now().strftime("%Y%m%dT%H%M%SZ")
    directory = destination_root / run_id
    directory.mkdir(parents=True, exist_ok=True)
    integrity = _quick_check(source_db)
    if integrity != "ok":
        raise ValueError(f"backup failed quick_check: {integrity}")
    staging = directory / "state.db"
    source = sqlite3.connect(str(source_db), isolation_level=None)
    try:
        target = sqlite3.connect(str(staging), isolation_level=None)
        try:
            source.backup(target)
        finally:
            target.close()
    finally:
        source.close()
    integrity = _quick_check(staging)
    if integrity != "ok":
        staging.unlink()
        raise ValueError(f"backup failed quick_check: {integrity}")
    raw = staging.read_bytes()
    archive_path = directory / ARCHIVE_NAME
    with gzip.open(archive_path, "wb", compresslevel=6) as handle:
        handle.write(raw)
    staging.unlink()
    manifest = {
        "run_id": run_id, "created_at": _now().isoformat(), "source_db": str(source_db),
        "directory": str(directory), "archive": ARCHIVE_NAME,
        "archive_bytes": archive_path.stat().st_size, "sha256": hashlib.sha256(raw).hexdigest(),
        "integrity": integrity, "format": "sqlite-gzip-json-v1",
    }
    _atomic_write_json(directory / MANIFEST_NAME, manifest)
    _atomic_write_json(destination_root / "latest.json", manifest)
    return manifest


def restore_local_state(backup_ref: str | Path, target_db: str | Path | None = None) -> dict[str, Any]:
    """Restore an archive or a backup directory into the configured state database."""
    reference = Path(backup_ref)
    gz_path: Path
    manifest: dict[str, Any]
    if reference.is_dir():
        manifest = json.loads((reference / MANIFEST_NAME).read_text(encoding="utf-8"))
        gz_path = reference / manifest["archive"]
    elif reference.name == ARCHIVE_NAME:
        gz_path = reference
        manifest = {}
    else:
        raise ValueError("backup_ref must be a backup directory or a state.db.gz archive")
    if not gz_path.is_file():
        raise FileNotFoundError(f"backup archive not found: {gz_path}")
    raw = gzip.decompress(gz_path.read_bytes())
    expected = manifest.get("sha256")
    actual = hashlib.sha256(raw).hexdigest()
    if expected and actual != expected:
        raise ValueError("backup sha256 mismatch; restore refused")
    target = Path(target_db or state_db_path()).resolve()
    staged = target.with_suffix(target.suffix + ".restore.tmp")
    staged.write_bytes(raw)
    integrity = _quick_check(staged)
    if integrity != "ok":
        staged.unlink()
        raise ValueError(f"restored database failed quick_check: {integrity}")
    for sidecar in (Path(str(target) + "-wal"), Path(str(target) + "-shm")):
        try:
            if sidecar.exists():
                sidecar.unlink()
        except OSError:
            pass
    staged.replace(target)
    return {"restored": True, "target_db": str(target), "run_id": manifest.get("run_id"),
            "sha256_ok": expected is None or actual == expected, "integrity": integrity,
            "archive": str(gz_path)}