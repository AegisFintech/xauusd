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


def test_remote_artifact_apply_is_resumable_and_reconciles(tmp_path):
 database=tmp_path/"registry.db"; remote=tmp_path/"results"/"xauusd-result-1"; remote.mkdir(parents=True)
 (remote/"result.json").write_text("{}"); (remote/"trades.csv.gz").write_bytes(b"trade"); (remote/"equity.parquet").write_bytes(b"equity")
 validation={"passed":False,"gates":{"a":False,"b":False}}
 with sqlite3.connect(database) as db:
  db.execute("CREATE TABLE experiments(id INTEGER,fingerprint TEXT,status TEXT,promoted INTEGER,validation_json TEXT,artifacts_json TEXT)")
  db.execute("CREATE TABLE experiment_events(experiment_id INTEGER,occurred_at TEXT,event TEXT,payload_json TEXT)")
  db.execute("INSERT INTO experiments VALUES(1,?,'completed',0,?,?)",("f"*64,json.dumps(validation),json.dumps({"remote_directory":str(remote)})))
 manager=OperationsManager(database,tmp_path/"b",tmp_path/"r"); plan_path=tmp_path/"plan.json"
 manager.remote_artifacts_plan(plan_path,0); plan=json.loads(plan_path.read_text()); journal=tmp_path/"journal.jsonl"
 result=manager.apply_remote_artifacts_plan(plan_path,plan["plan_digest"],journal,allowed_root=str(tmp_path/"results"))
 assert result["removed_files"]==2 and (remote/"result.json").exists() and not (remote/"equity.parquet").exists()
 assert manager.apply_remote_artifacts_plan(plan_path,plan["plan_digest"],journal,allowed_root=str(tmp_path/"results"))["previously_completed"]==1
 reconciled=manager.reconcile_remote_artifacts(plan_path,plan["plan_digest"],journal)
 assert reconciled["updated"]==1
 with sqlite3.connect(database) as db:
  artifacts=json.loads(db.execute("SELECT artifacts_json FROM experiments").fetchone()[0]); event=db.execute("SELECT event FROM experiment_events").fetchone()[0]
 assert not artifacts["detail_retention"]["detailed"] and event=="remote_artifacts_compacted"


def test_artifact_retention_inventory_reports_policy_and_file_mismatches(tmp_path):
 root=tmp_path/"results"; compact=root/"xauusd-result-1"; detailed=root/"xauusd-result-2"; missing=root/"xauusd-result-3"
 for directory in (compact,detailed,missing): directory.mkdir(parents=True)
 (compact/"result.json").write_text(json.dumps({"artifact_retention":{"detailed":False,"reason":"compact"}}))
 (detailed/"result.json").write_text(json.dumps({"artifact_retention":{"detailed":True,"reason":"audit"}}))
 (detailed/"trades.csv.gz").write_bytes(b"trades"); (detailed/"equity.parquet").write_bytes(b"equity")
 (missing/"result.json").write_text(json.dumps({"artifact_retention":{"detailed":True,"reason":"legacy"}}))
 report=OperationsManager.artifact_retention_inventory(root)
 assert report["directories"]==3 and report["result_bundles"]==3 and report["invalid_result_json"]==0
 assert report["groups"]["compact"]["average_bytes_per_scenario"]>0
 assert report["groups"]["audit"]["detailed_scenarios"]==1 and report["groups"]["audit"]["missing_declared_detail"]==0
 assert report["groups"]["legacy"]["missing_declared_detail"]==1
