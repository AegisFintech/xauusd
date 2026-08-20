import hashlib,json

from xauusd.core import synthetic_bars
from xauusd.distributed_compute import PROTOCOL_VERSION,RemoteComputeBridge,compute_job,job_payload,failure_code,retain_detailed_artifacts
from xauusd.experiment_registry import ExperimentRegistry,ExperimentSpec,canonical_json
from xauusd.tournament_data import TournamentDataConfig,TournamentDataset
from xauusd.search_space import catalog_size


def setup(tmp_path):
 dataset=TournamentDataset(TournamentDataConfig(root=tmp_path/"data",active_path=tmp_path/"active.json",days=30))
 manifest=dataset.create(synthetic_bars(60*24*40,seed=4))
 registry=ExperimentRegistry(tmp_path/"registry.sqlite3")
 spec=ExperimentSpec("momentum","formula",{"strategy":{"fast":8,"slow":34,"threshold_atr":.1}},
                     manifest["version"],manifest["fingerprint"],manifest["engine_version"],manifest["cost_model_version"])
 row,_=registry.register(spec); claimed=registry.claim_next("remote")
 return dataset,claimed


def test_compute_job_is_fingerprinted_and_never_reads_holdout(tmp_path,monkeypatch):
 dataset,experiment=setup(tmp_path); job=job_payload(experiment,dataset.active(),"commit")
 path=tmp_path/"job.json"; path.write_text(json.dumps(job)); reads=[]; original=dataset.read
 def guarded(partition):
  reads.append(partition); assert partition!="test"; return original(partition)
 monkeypatch.setattr(dataset,"read",guarded)
 result=compute_job(path,tmp_path/"result",dataset)
 assert result["protocol"]==PROTOCOL_VERSION and set(reads)<={"train","validation"}
 digest=result.pop("result_digest")
 assert digest==hashlib.sha256(canonical_json(result).encode()).hexdigest()
 assert result["artifact_retention"]["reason"] in {"validation_candidate","deterministic_audit_sample","compact_development_reject"}
 assert (tmp_path/"result"/"trades.csv.gz").exists()==result["artifact_retention"]["detailed"]


def test_compute_job_rejects_wrong_dataset(tmp_path):
 dataset,experiment=setup(tmp_path); job=job_payload(experiment,dataset.active(),"commit")
 job["dataset"]["fingerprint"]="wrong"; path=tmp_path/"job.json"; path.write_text(json.dumps(job))
 try: compute_job(path,tmp_path/"result",dataset)
 except ValueError as error: assert "fingerprint mismatch" in str(error)
 else: raise AssertionError("mismatch accepted")


def test_remote_artifact_fetch_restricts_path_and_name(tmp_path,monkeypatch):
 monkeypatch.setenv("COMPUTE_HOST","example"); bridge=RemoteComputeBridge(root=tmp_path)
 for path,name in (("/etc","equity.parquet"),("/tmp/xauusd-result-1","secret")):
  try: bridge.fetch_artifact(path,name,tmp_path/"out")
  except ValueError: pass
  else: raise AssertionError("unsafe artifact accepted")


def test_remote_result_root_is_persistent_and_below_compute_root(tmp_path,monkeypatch):
 monkeypatch.setenv("COMPUTE_HOST","example")
 bridge=RemoteComputeBridge(root=tmp_path)
 assert bridge.remote_result_root=="/opt/xauusd/var/results"
 monkeypatch.setenv("COMPUTE_RESULT_ROOT","/tmp/results")
 try: RemoteComputeBridge(root=tmp_path)
 except ValueError: pass
 else: raise AssertionError("unsafe result root accepted")


def test_result_root_is_not_created_per_scenario(tmp_path):
 source=__import__('inspect').getsource(RemoteComputeBridge.process_claimed)
 assert "mkdir -p" not in source


def test_remote_telemetry_has_bpytop_capacity_fields(tmp_path,monkeypatch):
 monkeypatch.setenv("COMPUTE_HOST","example"); bridge=RemoteComputeBridge(root=tmp_path)
 class Result:
  returncode=0
  stdout='{"cpu":{"total_percent":50,"per_core":[40,60],"cores":2,"load":[1,2,3]},"memory":{"percent":25},"disk":{"percent":10},"network":{},"tunnel":{"active":true}}'
 monkeypatch.setattr(bridge,"_ssh",lambda *a,**k:Result())
 sample=bridge.sample_remote()
 assert sample["connected"] and sample["cpu"]["per_core"]==[40,60] and sample["ssh_latency_ms"]>=0


def test_control_plane_refills_at_ten_percent(tmp_path,monkeypatch):
 dataset,experiment=setup(tmp_path); registry=ExperimentRegistry(tmp_path/"registry.sqlite3")
 monkeypatch.setenv("COMPUTE_HOST","example")
 bridge=RemoteComputeBridge(registry,dataset,tmp_path/"reports")
 calls=[]
 monkeypatch.setattr("xauusd.distributed_compute.replenish_catalog",
  lambda registry,dataset,target_new:{"exhausted":False,"created":target_new})
 monkeypatch.setattr("xauusd.distributed_compute.PortfolioResearch.run",lambda self:None)
 result=bridge.maintain_control_plane()
 assert result["low_queue_threshold"]==int(catalog_size()*.10)
 assert result["catalog"]["created"]==result["low_queue_threshold"]


def test_remote_failure_codes_are_structured():
 assert failure_code(OSError("No space left on device"))=="RESOURCE_EXHAUSTED"
 assert failure_code(TimeoutError("timed out"))=="TIMEOUT"
 assert failure_code(ValueError("remote result verification failed"))=="PROTOCOL_MISMATCH"


def test_readiness_uses_most_constrained_mount(tmp_path,monkeypatch):
 monkeypatch.setenv("COMPUTE_HOST","example"); bridge=RemoteComputeBridge(root=tmp_path)
 bridge.telemetry={"mounts":{"root":{"percent":40},"tmp":{"percent":91}}}
 assert bridge.readiness()["state"]=="RESOURCE_EXHAUSTED" and not bridge.readiness()["ready"]
 bridge.telemetry={"mounts":{"root":{"percent":40},"tmp":{"percent":81}}}
 assert bridge.readiness()["state"]=="DEGRADED" and bridge.readiness()["ready"]


def test_coordinator_drain_flag_is_reversible(tmp_path,monkeypatch):
 monkeypatch.setenv("COMPUTE_HOST","example")
 monkeypatch.setenv("COMPUTE_DRAIN_PATH",str(tmp_path/"DRAIN"))
 bridge=RemoteComputeBridge(root=tmp_path)
 assert not bridge.drain_status()["draining"]
 assert bridge.drain()["draining"] and bridge.drain_path.exists()
 assert bridge.drain_status()["requested_at"]
 assert not bridge.resume()["draining"] and not bridge.drain_path.exists()


def test_artifact_retention_keeps_candidates_and_deterministic_audits(monkeypatch):
 experiment={"fingerprint":"00000000"+"a"*56}
 assert retain_detailed_artifacts(experiment,{"stage":"validation"})==(True,"validation_candidate")
 monkeypatch.setenv("COMPUTE_ARTIFACT_AUDIT_PERCENT","1")
 assert retain_detailed_artifacts(experiment,{"stage":"development"})==(True,"deterministic_audit_sample")
 experiment["fingerprint"]="ffffffff"+"a"*56
 assert retain_detailed_artifacts(experiment,{"stage":"development"})==(False,"compact_development_reject")
