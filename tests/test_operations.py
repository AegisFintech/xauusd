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


def test_compaction_compresses_trade_ledgers_and_updates_registry(tmp_path):
 database=tmp_path/"registry.db"; ledger=tmp_path/"trades.csv"; ledger.write_text("pnl\n"+("1.25\n"*1000))
 artifacts=json.dumps({"trades":str(ledger)})
 with sqlite3.connect(database) as db:
  db.execute("CREATE TABLE experiments(id INTEGER,artifacts_json TEXT)"); db.execute("INSERT INTO experiments VALUES(1,?)",(artifacts,))
 result=OperationsManager(database,tmp_path/"b",tmp_path/"r").compact_artifacts()
 with sqlite3.connect(database) as db: updated=json.loads(db.execute("SELECT artifacts_json FROM experiments").fetchone()[0])
 assert result["compressed"]==1 and result["bytes_saved"]>0
 assert not ledger.exists() and updated["trades"].endswith(".gz")


def test_remote_artifact_plan_is_deterministic_and_protects_candidates(tmp_path):
 database=tmp_path/"registry.db"; output=tmp_path/"plan.json"
 with sqlite3.connect(database) as db:
  db.execute("CREATE TABLE experiments(id INTEGER,fingerprint TEXT,status TEXT,promoted INTEGER,validation_json TEXT,artifacts_json TEXT)")
  for i,validation in ((1,{"passed":False,"gates":{"a":False,"b":False}}),(2,{"passed":True,"gates":{"a":True}})):
   db.execute("INSERT INTO experiments VALUES(?,?,?,?,?,?)",(i,"f"*64,"completed",0,json.dumps(validation),json.dumps({"remote_directory":f"/opt/xauusd/var/results/xauusd-result-{i}"})))
 result=OperationsManager(database,tmp_path/"b",tmp_path/"r").remote_artifacts_plan(output,audit_percent=0)
 plan=json.loads(output.read_text())
 assert result["candidate_count"]==1 and result["protected_count"]==1
 assert plan["candidates"][0]["experiment_id"]==1 and plan["protected"][0]["reason"]=="validation_passed"
 OperationsManager(database,tmp_path/"b",tmp_path/"r").remote_artifacts_plan(output,0)
 repeated=json.loads(output.read_text())
 assert repeated["candidates"]==plan["candidates"] and repeated["protected"]==plan["protected"]
