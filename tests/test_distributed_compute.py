import hashlib,json

from xauusd.core import synthetic_bars
from xauusd.distributed_compute import PROTOCOL_VERSION,compute_job,job_payload
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
