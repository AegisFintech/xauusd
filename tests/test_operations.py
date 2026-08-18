import json
import sqlite3

from xauusd.operations import OperationsManager


def test_health_detects_database_and_missing_backup(tmp_path,monkeypatch):
 database=tmp_path/"registry.db"
 with sqlite3.connect(database) as db: db.execute("CREATE TABLE test(id INTEGER)")
 manager=OperationsManager(database,tmp_path/"backups",tmp_path/"reports")
 monkeypatch.chdir(tmp_path); health=manager.health()
 assert health["database"]["integrity"]=="ok" and not health["healthy"]
 assert "backup missing or older than 30 hours" in health["alerts"]


def test_backup_uses_sqlite_snapshot_and_manifest(tmp_path,monkeypatch):
 monkeypatch.chdir(tmp_path); database=tmp_path/"data"/"experiments"/"registry.sqlite3"; database.parent.mkdir(parents=True)
 with sqlite3.connect(database) as db: db.execute("CREATE TABLE test(value TEXT)"); db.execute("INSERT INTO test VALUES('safe')")
 (tmp_path/"data"/"tournaments").mkdir(); (tmp_path/"data"/"tournaments"/"active.json").write_text("{}")
 manager=OperationsManager(database,tmp_path/"backups",tmp_path/"reports"); result=manager.backup()
 snapshot=tmp_path/result["directory"]/"registry.sqlite3"
 with sqlite3.connect(snapshot) as db: assert db.execute("SELECT value FROM test").fetchone()[0]=="safe"
 latest=json.loads((tmp_path/"backups"/"latest.json").read_text())
 assert latest["run_id"]==result["run_id"] and snapshot.exists()
