import json
import sqlite3

import pytest

from xauusd.local_state import SQLitePaperTradingStore
from xauusd.state_backup import backup_local_state, restore_local_state
from xauusd.paper_trading import PaperDecision, PaperRiskConfig, PaperTrading
from datetime import datetime, timedelta, timezone


def decision(identifier="d1", side="BUY", quantity=1.0, price=4000.0):
    now = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)
    return PaperDecision(identifier, "XAUUSD", side, quantity, price, now)


def seeded_db(tmp_path):
    path = str(tmp_path / "state.db")
    store = SQLitePaperTradingStore(db_path=path)
    trading = PaperTrading(store, PaperRiskConfig(max_market_data_age_seconds=120))
    trading.start("test")
    trading.evaluate(decision("before-backup"), datetime(2026, 9, 17, 12, tzinfo=timezone.utc))
    return path


def test_backup_restore_round_trip_preserves_state(tmp_path):
    source = seeded_db(tmp_path)
    backup_root = tmp_path / "backups"

    manifest = backup_local_state(source_db=source, dest_root=backup_root)

    assert (backup_root / manifest["run_id"] / "state.db.gz").is_file()
    assert manifest["integrity"] == "ok"
    assert manifest["sha256"]

    restored_target = tmp_path / "restored.db"
    result = restore_local_state(backup_root / manifest["run_id"], target_db=restored_target)

    assert result["restored"] is True
    assert result["sha256_ok"] is True
    reopened = PaperTrading(SQLitePaperTradingStore(db_path=str(restored_target)),
                            PaperRiskConfig(max_market_data_age_seconds=120))
    assert reopened.state()["stopped"] is False
    assert reopened.state()["kill_switch_reason"] == "test"
    assert len(reopened.state()["ledger"]) == 1


def test_backup_refuses_corrupt_source(tmp_path):
    source = tmp_path / "bad.db"
    source.write_bytes(b"this is not a sqlite database" * 8)
    with pytest.raises(ValueError, match="quick_check"):
        backup_local_state(source_db=source, dest_root=tmp_path / "backups")


def test_restore_refuses_sha256_tampering(tmp_path):
    source = seeded_db(tmp_path)
    backup_root = tmp_path / "backups"
    manifest = backup_local_state(source_db=source, dest_root=backup_root)
    import gzip
    archive = backup_root / manifest["run_id"] / "state.db.gz"
    raw = gzip.decompress(archive.read_bytes())
    with gzip.open(archive, "wb") as handle:
        handle.write(raw + b"\x00")
    with pytest.raises(ValueError, match="sha256"):
        restore_local_state(backup_root / manifest["run_id"], target_db=tmp_path / "out.db")


def test_restore_refuses_garbage_archive(tmp_path):
    manifest_dir = tmp_path / "bundle"
    manifest_dir.mkdir()
    bogus = manifest_dir / "state.db.gz"
    import gzip
    with gzip.open(bogus, "wb") as handle:
        handle.write(b"not a database at all")
    (manifest_dir / "manifest.json").write_text(json.dumps({"archive": "state.db.gz", "sha256": None}))
    with pytest.raises(ValueError, match="quick_check"):
        restore_local_state(manifest_dir, target_db=tmp_path / "out.db")


def test_backup_keeps_validating_wal_writes(tmp_path):
    source = seeded_db(tmp_path)
    backup_root = tmp_path / "backups"
    manifest = backup_local_state(source_db=source, dest_root=backup_root)
    latest = json.loads((backup_root / "latest.json").read_text())
    assert latest["run_id"] == manifest["run_id"]
    assert latest["integrity"] == "ok"