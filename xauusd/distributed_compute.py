from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from .experiment_registry import ExperimentRegistry, canonical_json
from .tournament_data import TournamentDataset
from .tournament_runner import TournamentRunner, _finite
from .adaptive_search import AdaptiveSearch
from .codex_workflow import CodexImprovementWorkflow
from .portfolio_research import PortfolioResearch
from .search_space import replenish_catalog
from .strategy_proposals import ProposalEngine


PROTOCOL_VERSION="distributed-v1"


def _atomic_json(path: Path,payload: dict) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(_finite(payload),indent=2,allow_nan=False))
    temporary.replace(path)


def job_payload(experiment: dict,dataset: dict,code_commit: str) -> dict:
    return {"protocol":PROTOCOL_VERSION,"created_at":datetime.now(timezone.utc).isoformat(),
            "code_commit":code_commit,"dataset":{"version":dataset["version"],
            "fingerprint":dataset["fingerprint"],"engine_version":dataset["engine_version"],
            "cost_model_version":dataset["cost_model_version"]},"experiment":experiment}


def compute_job(job_path: Path,output_directory: Path,dataset: TournamentDataset | None=None) -> dict:
    job=json.loads(job_path.read_text()); expected=job["dataset"]
    dataset=dataset or TournamentDataset(); actual=dataset.active()
    for key in ("version","fingerprint","engine_version","cost_model_version"):
        if actual[key]!=expected[key]: raise ValueError(f"dataset {key} mismatch")
    experiment=job["experiment"]
    if experiment["fingerprint"] != hashlib.sha256(canonical_json({
        "strategy_family":experiment["strategy_family"],"formula":experiment["formula"],
        "parameters":experiment["parameters"],"dataset_version":experiment["dataset_version"],
        "dataset_fingerprint":experiment["dataset_fingerprint"],"engine_version":experiment["engine_version"],
        "cost_model_version":experiment["cost_model_version"]}).encode()).hexdigest():
        raise ValueError("experiment fingerprint mismatch")
    runner=TournamentRunner(registry=ExperimentRegistry(output_directory/"unused.sqlite3"),dataset=dataset,
                            output_root=output_directory)
    strategy,execution=runner.reconstruct(experiment)
    development=runner._backtest("train",strategy,execution)
    validation_result=None
    validation={"passed":False,"stage":"development",
                "gates":{"minimum_trades":runner._development_passed(development["metrics"])}}
    if runner._development_passed(development["metrics"]):
        from .research import build_features,generate_signal
        from .engine import EventDrivenBacktester
        features=build_features(dataset.read("validation"))
        validation_result=EventDrivenBacktester(execution).run(features,generate_signal(features,strategy))
        validation={"stage":"validation",**runner._validation(validation_result["metrics"],validation_result,
                    features,strategy,execution)}
    result=validation_result or development
    output_directory.mkdir(parents=True,exist_ok=True)
    result["trades"].to_csv(output_directory/"trades.csv.gz",index=False,compression="gzip")
    result["equity"].to_frame().to_parquet(output_directory/"equity.parquet")
    metrics={"development":_finite(development["metrics"]),
             "validation":_finite(validation_result["metrics"]) if validation_result else None,"holdout":None}
    bundle={"protocol":PROTOCOL_VERSION,"experiment_id":experiment["id"],
            "experiment_fingerprint":experiment["fingerprint"],"dataset":expected,
            "code_commit":job["code_commit"],"worker_id":os.getenv("HOSTNAME","remote"),
            "finished_at":datetime.now(timezone.utc).isoformat(),"metrics":metrics,"validation":validation,
            "strategy":asdict(strategy),"execution":asdict(execution),
            "files":{"trades":"trades.csv.gz","equity":"equity.parquet"}}
    bundle["result_digest"]=hashlib.sha256(canonical_json(bundle).encode()).hexdigest()
    _atomic_json(output_directory/"result.json",bundle)
    try: (output_directory/"unused.sqlite3").unlink()
    except FileNotFoundError: pass
    return bundle


class RemoteComputeBridge:
    """Master-only SSH bridge. The remote host never opens the master SQLite database."""
    def __init__(self,registry: ExperimentRegistry | None=None,dataset: TournamentDataset | None=None,
                 root: Path=Path("reports/tournament/distributed")):
        self.registry=registry or ExperimentRegistry(); self.dataset=dataset or TournamentDataset(); self.root=root
        self.host=os.environ["COMPUTE_HOST"]; self.user=os.getenv("COMPUTE_USER","root")
        self.port=os.getenv("COMPUTE_PORT","22"); self.key=os.getenv("COMPUTE_SSH_KEY","/root/.ssh/xauusd_compute")
        self.remote_root=os.getenv("COMPUTE_ROOT","/opt/xauusd")
        self.workers=max(1,int(os.getenv("COMPUTE_WORKERS","12")))
        self.control_path=os.getenv("COMPUTE_SSH_CONTROL_PATH","/tmp/xauusd-ssh-%r@%h:%p")

    def _ssh_options(self) -> list[str]:
        return ["-i",self.key,"-p",self.port,"-o","BatchMode=yes","-o","ConnectTimeout=15",
                "-o","ServerAliveInterval=15","-o","ServerAliveCountMax=4","-o","ControlMaster=auto",
                "-o","ControlPersist=300","-o",f"ControlPath={self.control_path}"]

    @staticmethod
    def _retry(command: list[str],timeout: int=7200,attempts: int=4):
        last=None
        for attempt in range(attempts):
            try: return subprocess.run(command,check=True,text=True,timeout=timeout)
            except subprocess.CalledProcessError as error:
                last=error
                if attempt+1<attempts: time.sleep(2**attempt)
        raise last

    def _ssh(self,*remote: str,check=True,capture=False):
        command=["ssh",*self._ssh_options(),f"{self.user}@{self.host}",*remote]
        if check and not capture: return self._retry(command)
        return subprocess.run(command,check=check,text=True,capture_output=capture,timeout=7200)

    def _scp(self,source: str,target: str,recursive=False):
        command=["scp","-i",self.key,"-P",self.port,"-q","-o","ControlMaster=auto",
                 "-o","ControlPersist=300","-o",f"ControlPath={self.control_path}"]
        if recursive: command.append("-r")
        command.extend([source,target]); self._retry(command)

    def _upload_job(self,source: Path,remote: str) -> None:
        command=["ssh",*self._ssh_options(),f"{self.user}@{self.host}",f"cat > {remote}"]
        last=None
        for attempt in range(4):
            try:
                subprocess.run(command,input=source.read_bytes(),check=True,timeout=60)
                return
            except subprocess.CalledProcessError as error:
                last=error; time.sleep(2**attempt)
        raise last

    def _download_result(self,remote: str,local: Path) -> None:
        archive=local.parent/f".{local.name}.tar.gz"
        command=["ssh",*self._ssh_options(),f"{self.user}@{self.host}",f"tar -C {remote} -czf - ."]
        with archive.open("wb") as output:
            subprocess.run(command,stdout=output,check=True,timeout=300)
        local.mkdir(parents=True,exist_ok=True)
        with tarfile.open(archive,"r:gz") as bundle:
            for member in bundle.getmembers():
                if member.islnk() or member.issym() or ".." in Path(member.name).parts:
                    raise ValueError("unsafe remote result archive")
            bundle.extractall(local,filter="data")
        archive.unlink()

    def status(self,**extra) -> dict:
        path=self.root/"status.json"; previous={}
        try: previous=json.loads(path.read_text())
        except (OSError,json.JSONDecodeError): pass
        payload={**previous,"protocol":PROTOCOL_VERSION,"updated_at":datetime.now(timezone.utc).isoformat(),**extra}
        _atomic_json(path,payload); return payload

    def fetch_artifact(self,remote_directory: str,name: str,destination: Path) -> Path:
        if name not in {"equity.parquet","trades.csv.gz"}: raise ValueError("unsupported artifact")
        if not remote_directory.startswith("/tmp/xauusd-result-"): raise ValueError("invalid remote artifact path")
        destination.parent.mkdir(parents=True,exist_ok=True)
        temporary=destination.with_suffix(destination.suffix+".tmp")
        command=["ssh",*self._ssh_options(),f"{self.user}@{self.host}",f"cat {remote_directory}/{name}"]
        with temporary.open("wb") as output: subprocess.run(command,stdout=output,check=True,timeout=300)
        temporary.replace(destination); return destination

    def process_claimed(self,experiment: dict,code_commit: str) -> dict:
        eid=experiment["id"]; worker=experiment["worker_id"]
        local=self.root/"results"/str(eid); job=self.root/"jobs"/f"{eid}.json"
        _atomic_json(job,job_payload(experiment,self.dataset.active(),code_commit))
        remote_job=f"/tmp/xauusd-job-{eid}.json"; remote_result=f"/tmp/xauusd-result-{eid}"
        try:
            self._upload_job(job,remote_job)
            execution=self._ssh(f"cd {self.remote_root} && .venv/bin/python -m xauusd.cli compute-job {remote_job} {remote_result}",capture=True)
            if execution.returncode: raise subprocess.CalledProcessError(execution.returncode,execution.args,execution.stdout,execution.stderr)
            bundle=json.loads(execution.stdout)
            digest=bundle.pop("result_digest"); actual=hashlib.sha256(canonical_json(bundle).encode()).hexdigest()
            if digest!=actual or bundle["experiment_fingerprint"]!=experiment["fingerprint"]:
                raise ValueError("remote result verification failed")
            strategy,execution=TournamentRunner.reconstruct(experiment)
            validation=bundle["validation"]; validation["remote_compute"]={
                "worker_id":bundle["worker_id"],"protocol":bundle["protocol"],"code_commit":bundle["code_commit"]}
            promoted,holdout,finalist=TournamentRunner(self.registry,self.dataset)._promote(
                experiment,strategy,execution,validation,local)
            validation["finalist"]=finalist; metrics=bundle["metrics"]
            if holdout: metrics["holdout"]=_finite(holdout["metrics"])
            local.mkdir(parents=True,exist_ok=True); _atomic_json(local/"result.json",{**bundle,"result_digest":digest})
            artifacts={"directory":str(local),"summary":str(local/"result.json"),"remote_host":self.host,
                       "remote_directory":remote_result,"storage":"remote","fetch_policy":"on_demand"}
            return self.registry.complete(eid,worker,metrics,validation,artifacts,promoted)
        except Exception as error:
            self.registry.requeue(eid,worker,f"remote retry: {type(error).__name__}: {error}")
            raise
        finally:
            self._ssh(f"rm -f {remote_job}",check=False)

    def maintain_control_plane(self) -> dict:
        completed=self.registry.count("completed"); queued=self.registry.count("queued")
        adaptive_path=Path("reports/tournament/adaptive.json")
        try: previous=json.loads(adaptive_path.read_text()) if adaptive_path.exists() else {}
        except (OSError,json.JSONDecodeError): previous={}
        last=int(previous.get("last_completed_trigger",100 if previous else 0) or 0)
        adaptive=None
        if completed >= (last+250 if previous else 100) and queued<500:
            adaptive=AdaptiveSearch(self.registry,adaptive_path).generate(
                self.dataset.active(),25,int(previous.get("generation",1 if previous else 0) or 0)+1,completed)
        portfolio=None; portfolio_path=Path("reports/tournament/portfolio/latest.json")
        if completed>=150 and not portfolio_path.exists():
            portfolio=PortfolioResearch(self.registry,self.dataset).run()
        catalog=None
        if queued<100:
            catalog=replenish_catalog(self.registry,self.dataset.active(),500)
            if catalog["exhausted"]:
                catalog["novelty"]=ProposalEngine(self.registry).generate(self.dataset.active(),500)
                if catalog["novelty"]["exhausted"]:
                    latest=Path("reports/tournament/codex/latest.json")
                    if not latest.exists():
                        catalog["codex"]=CodexImprovementWorkflow(self.registry).run(self.dataset.active())
        return {"adaptive":adaptive,"portfolio":portfolio,"catalog":catalog}

    def run_forever(self,idle_seconds: float=10) -> None:
        worker_prefix=f"remote-master-{os.getpid()}"
        recovered_replaced=self.registry.recover_worker_prefix("remote-master-",worker_prefix)
        self.registry.recover_stale(datetime.now(timezone.utc)-timedelta(minutes=120))
        self._ssh("true")
        try: code_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
        except (OSError,subprocess.CalledProcessError): code_commit="unknown"
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            active={}; completed_total=0; failed_total=0; started=time.monotonic()
            while True:
                try:
                    recovered=self.registry.recover_stale(datetime.now(timezone.utc)-timedelta(minutes=120))
                    control=self.maintain_control_plane()
                    while len(active)<self.workers:
                        experiment=self.registry.claim_next(f"{worker_prefix}-{len(active)+1}")
                        if experiment is None: break
                        future=pool.submit(self.process_claimed,experiment,code_commit)
                        active[future]=experiment
                    for future in [f for f in active if f.done()]:
                        experiment=active.pop(future)
                        try: future.result(); completed_total+=1
                        except Exception: failed_total+=1
                    summary=self.registry.summary(); elapsed=max(1,time.monotonic()-started)
                    self.status(state="running" if active else "idle",host=self.host,workers=self.workers,
                                active=len(active),active_experiment_ids=[x["id"] for x in active.values()],
                                completed_session=completed_total,failed_session=failed_total,
                                throughput_per_hour=round(completed_total*3600/elapsed,2),recovered_stale=recovered,
                                queue=summary["by_status"].get("queued",0),control=control,last_error=None)
                    time.sleep(1 if active else idle_seconds)
                except KeyboardInterrupt:
                    self.status(state="stopped",active=len(active)); return
                except Exception as error:
                    self.status(state="error",active=len(active),last_error=f"{type(error).__name__}: {error}")
                    time.sleep(idle_seconds)
