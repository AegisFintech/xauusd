import json
import gzip
import hashlib

from xauusd.operations import OperationsManager
from xauusd.experiment_registry import ExperimentRegistry,ExperimentSpec
from tests.memory_registry import MemoryRegistry


def test_health_detects_database_and_missing_backup(tmp_path,monkeypatch):
 manager=OperationsManager(MemoryRegistry(),tmp_path/"backups",tmp_path/"reports")
 monkeypatch.chdir(tmp_path); health=manager.health()
 assert health["database"]["integrity"]=="ok" and not health["healthy"]
 assert "backup missing or older than 30 hours" in health["alerts"]


def test_health_uses_configured_cockroach_registry(tmp_path,monkeypatch):
 class Result:
  def fetchone(self): return {"one":1}
 class Connection:
  def __enter__(self): return self
  def __exit__(self,*args): pass
  def execute(self,query):
   assert query=="SELECT 1"
   return Result()
 class Registry:
  def connect(self): return Connection()
 manager=OperationsManager(Registry(),tmp_path/"backups",tmp_path/"reports")
 monkeypatch.chdir(tmp_path); health=manager.health(Registry())
 assert health["database"]=={"available":True,"integrity":"ok","backend":"cockroachdb"}


def test_backup_uses_cockroach_logical_snapshot_and_manifest(tmp_path,monkeypatch):
 monkeypatch.chdir(tmp_path); registry=MemoryRegistry()
 registry.register(ExperimentSpec("momentum","f",{},"v","d","e","c"))
 (tmp_path/"data"/"tournaments").mkdir(parents=True); (tmp_path/"data"/"tournaments"/"active.json").write_text("{}")
 manager=OperationsManager(registry,tmp_path/"backups",tmp_path/"reports"); result=manager.backup()
 snapshot=tmp_path/result["directory"]/"registry.json.gz"
 payload=json.loads(gzip.decompress(snapshot.read_bytes()))
 assert payload["experiments"][0]["strategy_family"]=="momentum"
 latest=json.loads((tmp_path/"backups"/"latest.json").read_text())
 assert latest["run_id"]==result["run_id"] and snapshot.exists()
 assert result["auxiliary_files"][0]["backup"]=="active.json"
 assert OperationsManager.verify_backup(tmp_path/result["directory"])["valid"]


def test_backup_preserves_scaling_checkpoints_with_integrity_manifest(tmp_path,monkeypatch):
 monkeypatch.chdir(tmp_path); registry=MemoryRegistry()
 checkpoints=tmp_path/"reports"/"tournament"/"scaling-checkpoints"; checkpoints.mkdir(parents=True)
 (checkpoints/"50000.json").write_text('{"checkpoint":50000}')
 (checkpoints/"latest.json").write_text('{"checkpoint":"latest"}')
 manager=OperationsManager(registry,tmp_path/"backups",tmp_path/"reports"/"tournament")
 result=manager.backup(); backup=tmp_path/result["directory"]
 assert (backup/"scaling-checkpoints"/"50000.json").read_text()=='{"checkpoint":50000}'
 inventory=result["scaling_checkpoints"]
 assert [item["backup"] for item in inventory]==["scaling-checkpoints/50000.json","scaling-checkpoints/latest.json"]
 for item in inventory:
  archived=backup/item["backup"]
  assert item["bytes"]==archived.stat().st_size
  assert item["sha256"]==__import__("hashlib").sha256(archived.read_bytes()).hexdigest()
 assert OperationsManager.verify_backup(backup)["valid"]


def test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(tmp_path):
 backup=tmp_path/"backup"; checkpoints=backup/"scaling-checkpoints"; checkpoints.mkdir(parents=True)
 registry=backup/"registry.json.gz"; registry.write_bytes(gzip.compress(b'{"experiments":[],"experiment_events":[],"champion_history":[]}'))
 checkpoint=checkpoints/"50000.json"; checkpoint.write_text("original")
 manifest={"run_id":"fixture","registry_bytes":registry.stat().st_size,"registry_sha256":hashlib.sha256(registry.read_bytes()).hexdigest(),
  "scaling_checkpoints":[{"backup":"scaling-checkpoints/50000.json","bytes":8,"sha256":"wrong"},
                         {"backup":"../outside.json","bytes":0,"sha256":"wrong"}]}
 (backup/"manifest.json").write_text(json.dumps(manifest))
 result=OperationsManager.verify_backup(backup)
 assert not result["valid"] and result["registry_integrity"]=="ok"
 assert "checkpoint integrity mismatch: scaling-checkpoints/50000.json" in result["errors"]
 assert "unsafe checkpoint path: ../outside.json" in result["errors"]


def test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(tmp_path):
 backup=tmp_path/"backup"; backup.mkdir()
 registry=backup/"registry.json.gz"; registry.write_bytes(gzip.compress(b'{"experiments":[],"experiment_events":[],"champion_history":[]}'))
 report=backup/"worker-status.json"; report.write_text("status")
 manifest={"run_id":"fixture","registry_bytes":registry.stat().st_size,"registry_sha256":hashlib.sha256(registry.read_bytes()).hexdigest(),
  "auxiliary_files":[{"backup":"worker-status.json","bytes":6,"sha256":"wrong"},
                     {"backup":"../outside.json","bytes":0,"sha256":"wrong"}]}
 (backup/"manifest.json").write_text(json.dumps(manifest))
 result=OperationsManager.verify_backup(backup)
 assert not result["valid"] and result["auxiliary_files"]==2
 assert "auxiliary file integrity mismatch: worker-status.json" in result["errors"]
 assert "unsafe auxiliary path: ../outside.json" in result["errors"]


def test_compaction_compresses_trade_ledgers_and_updates_registry(tmp_path):
 registry=MemoryRegistry(); ledger=tmp_path/"trades.csv"; ledger.write_text("pnl\n"+("1.25\n"*1000))
 registry.register(ExperimentSpec("momentum","f",{},"v","d","e","c")); claimed=registry.claim_next("w")
 registry.complete(claimed["id"],"w",{},artifacts={"trades":str(ledger)})
 result=OperationsManager(registry,tmp_path/"b",tmp_path/"r").compact_artifacts()
 updated=registry.get(claimed["id"])["artifacts"]
 assert result["compressed"]==1 and result["bytes_saved"]>0
 assert not ledger.exists() and updated["trades"].endswith(".gz")


def test_remote_artifact_plan_is_deterministic_and_protects_candidates(tmp_path):
 registry=MemoryRegistry(); output=tmp_path/"plan.json"
 for i,validation in ((1,{"passed":False,"gates":{"a":False,"b":False}}),(2,{"passed":True,"gates":{"a":True}})):
  registry.register(ExperimentSpec("momentum",f"f{i}",{},"v","d","e","c")); claimed=registry.claim_next("w")
  registry.complete(claimed["id"],"w",{},validation,{"remote_directory":f"/opt/xauusd/var/results/xauusd-result-{i}"})
 manager=OperationsManager(registry,tmp_path/"b",tmp_path/"r")
 result=manager.remote_artifacts_plan(output,audit_percent=0)
 plan=json.loads(output.read_text())
 assert result["candidate_count"]==1 and result["protected_count"]==1
 assert plan["candidates"][0]["experiment_id"]==1 and plan["protected"][0]["reason"]=="validation_passed"
 manager.remote_artifacts_plan(output,0)
 repeated=json.loads(output.read_text())
 assert repeated["candidates"]==plan["candidates"] and repeated["protected"]==plan["protected"]


def test_remote_artifact_apply_is_resumable_and_reconciles(tmp_path):
 registry=MemoryRegistry(); remote=tmp_path/"results"/"xauusd-result-1"; remote.mkdir(parents=True)
 (remote/"result.json").write_text("{}"); (remote/"trades.csv.gz").write_bytes(b"trade"); (remote/"equity.parquet").write_bytes(b"equity")
 validation={"passed":False,"gates":{"a":False,"b":False}}
 registry.register(ExperimentSpec("momentum","f",{},"v","d","e","c")); claimed=registry.claim_next("w")
 registry.complete(claimed["id"],"w",{},validation,{"remote_directory":str(remote)})
 manager=OperationsManager(registry,tmp_path/"b",tmp_path/"r"); plan_path=tmp_path/"plan.json"
 manager.remote_artifacts_plan(plan_path,0); plan=json.loads(plan_path.read_text()); journal=tmp_path/"journal.jsonl"
 result=manager.apply_remote_artifacts_plan(plan_path,plan["plan_digest"],journal,allowed_root=str(tmp_path/"results"))
 assert result["removed_files"]==2 and (remote/"result.json").exists() and not (remote/"equity.parquet").exists()
 assert manager.apply_remote_artifacts_plan(plan_path,plan["plan_digest"],journal,allowed_root=str(tmp_path/"results"))["previously_completed"]==1
 reconciled=manager.reconcile_remote_artifacts(plan_path,plan["plan_digest"],journal)
 assert reconciled["updated"]==1
 artifacts=registry.get(1)["artifacts"]; event=registry.events(1)[-1]["event"]
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


def test_scaling_checkpoint_uses_registry_and_measured_stage_evidence(tmp_path):
 registry=MemoryRegistry()
 for number in range(2):
  spec=ExperimentSpec("momentum",f"formula-{number}",{"window":number+1},"v","d","e","c")
  registry.register(spec); claimed=registry.claim_next(f"w-{number}")
  if number==0: registry.complete(claimed["id"],f"w-{number}",{"validation":{"net_profit":1}})
  else: registry.fail(claimed["id"],f"w-{number}","failed")
 status=tmp_path/"status.json"
 status.write_text(json.dumps({"workers":16,"throughput_per_hour":1000,"history":[{"cpu_percent":95}],
   "duration":{"median_seconds":4,"p95_seconds":7},"stage_duration":{
    "dispatching":{"median_seconds":.3},"computing":{"median_seconds":3.4},"importing":{"median_seconds":.1}},
   "telemetry":{"memory":{"percent":20},"disk":{"percent":30},"network":{"rx_bytes_per_second":10}}}))
 report=OperationsManager(MemoryRegistry()).scaling_checkpoint(registry,status,target=100)
 assert report["registry"]["completed"]==1 and report["failure_rate"]==.5
 assert report["duplicate_fingerprints"]==0 and report["measured_bottleneck"]=="secondary_compute"
 assert report["checkpoints"]["50000"]["status"]=="pending"
 assert report["projected_hours_to_target"]==.099 and report["workers"]==16


def test_checkpoint_capture_is_atomic_and_first_observation_is_immutable(tmp_path,monkeypatch):
 manager=OperationsManager(MemoryRegistry()); output=tmp_path/"checkpoints"; reports=[
  {"registry":{"completed":60_000},"checkpoints":{}},
  {"registry":{"completed":110_000},"checkpoints":{}},
  {"registry":{"completed":120_000},"checkpoints":{}},
 ]
 monkeypatch.setattr(manager,"scaling_checkpoint",lambda *args,**kwargs:reports.pop(0))
 first=manager.capture_scaling_checkpoints(output_root=output)
 assert first["created"]==[str(output/"50000.json")]
 captured=json.loads((output/"50000.json").read_text())
 assert captured["checkpoint_capture"]=={"threshold":50_000,"first_observed_completed":60_000,
  "exact_threshold_capture":False,"note":"Immutable first observation at or after threshold crossing."}
 assert captured["acceptance"]["status"]=="baseline" and captured["acceptance"]["passed"] is None
 second=manager.capture_scaling_checkpoints(output_root=output)
 assert second["created"]==[str(output/"100000.json")] and second["existing"]==[str(output/"50000.json")]
 original=(output/"50000.json").read_text(); manager.capture_scaling_checkpoints(output_root=output)
 assert (output/"50000.json").read_text()==original
 assert json.loads((output/"latest.json").read_text())["registry"]["completed"]==120_000


def test_scaling_acceptance_compares_reliability_resources_and_performance():
 baseline={"throughput_per_hour":1000,"duration":{"p95_seconds":8},"memory":{"percent":20},"disk":{"percent":30}}
 report={"throughput_per_hour":850,"duration":{"p95_seconds":10},"memory":{"percent":25},"disk":{"percent":35},
         "failure_rate":.0005,"retried_scenario_rate":.002,"duplicate_fingerprints":0,"workers":16}
 accepted=OperationsManager.evaluate_scaling_checkpoint(report,baseline)
 assert accepted["status"]=="passed" and accepted["passed"]
 report["throughput_per_hour"]=799
 rejected=OperationsManager.evaluate_scaling_checkpoint(report,baseline)
 assert rejected["status"]=="failed" and not rejected["checks"]["throughput_retention"]["passed"]


def test_scaling_acceptance_fails_closed_when_measurements_are_missing():
 baseline={"throughput_per_hour":1000,"duration":{"p95_seconds":8},"memory":{"percent":20},"disk":{"percent":30}}
 report={"failure_rate":0,"retried_scenario_rate":0,"duplicate_fingerprints":0,"workers":16}
 result=OperationsManager.evaluate_scaling_checkpoint(report,baseline)
 assert not result["passed"] and not result["checks"]["measurement_completeness"]["passed"]


def test_capacity_plan_rounds_up_with_efficiency_and_optional_cost():
 report={"target":500_000,"registry":{"completed":100_000},"workers":16,"throughput_per_hour":4_000}
 plan=OperationsManager.capacity_plan(report,target_hours=24,efficiency=.8,host_hour_cost=1.25)
 assert plan["required_throughput_per_hour"]==400_000/24
 assert plan["effective_throughput_per_host"]==3_200
 assert plan["required_total_hosts"]==6 and plan["additional_hosts"]==5
 assert plan["projected_completion_hours"]<=24 and plan["projected_compute_cost"]==180
 assert plan["authorization"]=="planning_only"


def test_capacity_plan_fails_closed_without_measurement_and_validates_inputs():
 import pytest
 plan=OperationsManager.capacity_plan({"target":500_000,"registry":{"completed":10}})
 assert plan["status"]=="insufficient_evidence" and plan["required_total_hosts"] is None
 assert plan["cost_status"]=="not_yet_verified"
 with pytest.raises(ValueError): OperationsManager.capacity_plan({},target_hours=0)
 with pytest.raises(ValueError): OperationsManager.capacity_plan({},efficiency=1.1)
