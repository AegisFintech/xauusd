import hashlib,json

from xauusd.core import synthetic_bars
from xauusd.distributed_compute import PROTOCOL_VERSION,RemoteComputeBridge,compute_job,job_payload
from xauusd.experiment_registry import ExperimentRegistry,ExperimentSpec,canonical_json
from xauusd.tournament_data import TournamentDataConfig,TournamentDataset


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
 assert (tmp_path/"result"/"trades.csv.gz").exists()


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


def test_remote_telemetry_has_bpytop_capacity_fields(tmp_path,monkeypatch):
 monkeypatch.setenv("COMPUTE_HOST","example"); bridge=RemoteComputeBridge(root=tmp_path)
 class Result:
  returncode=0
  stdout='{"cpu":{"total_percent":50,"per_core":[40,60],"cores":2,"load":[1,2,3]},"memory":{"percent":25},"disk":{"percent":10},"network":{},"tunnel":{"active":true}}'
 monkeypatch.setattr(bridge,"_ssh",lambda *a,**k:Result())
 sample=bridge.sample_remote()
 assert sample["connected"] and sample["cpu"]["per_core"]==[40,60] and sample["ssh_latency_ms"]>=0
