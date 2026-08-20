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
import base64
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from .experiment_registry import ExperimentRegistry, canonical_json
from .tournament_data import TournamentDataset
from .tournament_runner import TournamentRunner, _finite
from .adaptive_search import AdaptiveSearch
from .codex_workflow import CodexImprovementWorkflow
from .portfolio_research import PortfolioResearch
from .search_space import catalog_size,replenish_catalog
from .strategy_proposals import ProposalEngine


PROTOCOL_VERSION="distributed-v1"
REMOTE_TELEMETRY_SCRIPT=r'''import json,os,shutil,time
def cpu():
 rows=[]
 for line in open('/proc/stat'):
  if not line.startswith('cpu'): break
  p=line.split(); values=list(map(int,p[1:])); rows.append((sum(values),values[3]+(values[4] if len(values)>4 else 0)))
 return rows
def net():
 rx=tx=0
 for line in open('/proc/net/dev').read().splitlines()[2:]:
  p=line.replace(':',' ').split(); rx+=int(p[1]); tx+=int(p[9])
 return rx,tx
c1=cpu(); n1=net(); started=time.monotonic(); time.sleep(.25); seconds=time.monotonic()-started; c2=cpu(); n2=net()
usage=[]
for a,b in zip(c1,c2):
 total=b[0]-a[0]; idle=b[1]-a[1]; usage.append(round(100*(total-idle)/total,1) if total else 0)
mem={}
for line in open('/proc/meminfo'):
 k,v,*_=line.replace(':','').split(); mem[k]=int(v)*1024
def disk(path):
 d=shutil.disk_usage(path); return {'path':path,'total':d.total,'used':d.used,'free':d.free,'percent':round(100*d.used/d.total,1)}
root_disk=disk('/'); tmp_disk=disk('/tmp')
load=os.getloadavg(); tunnel=os.system('systemctl is-active --quiet sg-tunnel.service')==0
print(json.dumps({'sampled_at':time.time(),'cpu':{'total_percent':usage[0],'per_core':usage[1:],'cores':len(usage)-1,'load':load},
'memory':{'total':mem['MemTotal'],'available':mem['MemAvailable'],'used':mem['MemTotal']-mem['MemAvailable'],'percent':round(100*(mem['MemTotal']-mem['MemAvailable'])/mem['MemTotal'],1),'swap_total':mem['SwapTotal'],'swap_used':mem['SwapTotal']-mem['SwapFree']},
'disk':root_disk,'mounts':{'root':root_disk,'tmp':tmp_disk},
'network':{'rx_bytes':n2[0],'tx_bytes':n2[1],'rx_bytes_per_second':round((n2[0]-n1[0])/seconds),'tx_bytes_per_second':round((n2[1]-n1[1])/seconds)},
'tunnel':{'active':tunnel},'uptime_seconds':float(open('/proc/uptime').read().split()[0])}))'''


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
        self.remote_result_root=os.getenv("COMPUTE_RESULT_ROOT",f"{self.remote_root}/var/results")
        if not self.remote_result_root.startswith(f"{self.remote_root}/"):
            raise ValueError("COMPUTE_RESULT_ROOT must be below COMPUTE_ROOT")
        self.workers=max(1,int(os.getenv("COMPUTE_WORKERS","16")))
        self.control_path=os.getenv("COMPUTE_SSH_CONTROL_PATH","/tmp/xauusd-ssh-%r@%h:%p")
        self.worker_states={}; self.state_lock=threading.Lock(); self.durations=deque(maxlen=500)
        self.telemetry={}; self.telemetry_at=0.; self.history=deque(maxlen=360)

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

    def sample_remote(self) -> dict:
        started=time.monotonic(); encoded=base64.b64encode(REMOTE_TELEMETRY_SCRIPT.encode()).decode()
        result=self._ssh(f"python3 -c \"import base64;exec(base64.b64decode('{encoded}'))\"",capture=True)
        if result.returncode: raise subprocess.CalledProcessError(result.returncode,result.args)
        sample=json.loads(result.stdout); sample["ssh_latency_ms"]=round((time.monotonic()-started)*1000,1)
        sample["connected"]=True; sample["contact_at"]=datetime.now(timezone.utc).isoformat()
        return sample

    def _stage(self,worker: str,experiment: dict,stage: str) -> None:
        with self.state_lock:
            previous=self.worker_states.get(worker,{})
            self.worker_states[worker]={"worker":worker.rsplit("-",1)[-1],"experiment_id":experiment["id"],
                "family":experiment["strategy_family"],"stage":stage,"started_at":previous.get("started_at",datetime.now(timezone.utc).isoformat()),
                "started_monotonic":previous.get("started_monotonic",time.monotonic())}

    def fetch_artifact(self,remote_directory: str,name: str,destination: Path) -> Path:
        if name not in {"equity.parquet","trades.csv.gz"}: raise ValueError("unsupported artifact")
        allowed=(f"{self.remote_result_root}/xauusd-result-","/tmp/xauusd-result-")
        if not remote_directory.startswith(allowed): raise ValueError("invalid remote artifact path")
        destination.parent.mkdir(parents=True,exist_ok=True)
        temporary=destination.with_suffix(destination.suffix+".tmp")
        command=["ssh",*self._ssh_options(),f"{self.user}@{self.host}",f"cat {remote_directory}/{name}"]
        with temporary.open("wb") as output: subprocess.run(command,stdout=output,check=True,timeout=300)
        temporary.replace(destination); return destination

    def process_claimed(self,experiment: dict,code_commit: str) -> dict:
        eid=experiment["id"]; worker=experiment["worker_id"]
        local=self.root/"results"/str(eid); job=self.root/"jobs"/f"{eid}.json"
        _atomic_json(job,job_payload(experiment,self.dataset.active(),code_commit))
        remote_job=f"/tmp/xauusd-job-{eid}.json"
        remote_result=f"{self.remote_result_root}/xauusd-result-{eid}"
        try:
            self._stage(worker,experiment,"dispatching")
            self._ssh(f"mkdir -p {self.remote_result_root}")
            self._upload_job(job,remote_job)
            self._stage(worker,experiment,"computing")
            execution=self._ssh(f"cd {self.remote_root} && .venv/bin/python -m xauusd.cli compute-job {remote_job} {remote_result}",capture=True)
            if execution.returncode: raise subprocess.CalledProcessError(execution.returncode,execution.args,execution.stdout,execution.stderr)
            bundle=json.loads(execution.stdout)
            self._stage(worker,experiment,"importing")
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
            completed=self.registry.complete(eid,worker,metrics,validation,artifacts,promoted)
            with self.state_lock:
                state=self.worker_states.pop(worker,{}); self.durations.append(time.monotonic()-state.get("started_monotonic",time.monotonic()))
            return completed
        except Exception as error:
            self.registry.requeue(eid,worker,f"remote retry: {type(error).__name__}: {error}")
            raise
        finally:
            self._ssh(f"rm -f {remote_job}",check=False)

    def maintain_control_plane(self) -> dict:
        completed=self.registry.count("completed"); queued=self.registry.count("queued")
        low_queue_threshold=max(100,int(catalog_size()*.10))
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
        if queued<low_queue_threshold:
            catalog=replenish_catalog(self.registry,self.dataset.active(),low_queue_threshold-queued)
            catalog["low_queue_threshold"]=low_queue_threshold
            if catalog["exhausted"]:
                catalog["novelty"]=ProposalEngine(self.registry).generate(
                    self.dataset.active(),low_queue_threshold-queued)
                if catalog["novelty"]["exhausted"]:
                    latest=Path("reports/tournament/codex/latest.json")
                    latest_state={}
                    try: latest_state=json.loads(latest.read_text()) if latest.exists() else {}
                    except (OSError,json.JSONDecodeError): pass
                    terminal=latest_state.get("status") in {"review_ready","rejected","failed"}
                    finished=latest_state.get("finished_at")
                    old_enough=not finished or datetime.fromisoformat(finished).astimezone(timezone.utc) <= datetime.now(timezone.utc)-timedelta(days=1)
                    if not latest.exists() or (terminal and old_enough):
                        catalog["codex"]=CodexImprovementWorkflow(self.registry).run(self.dataset.active())
        return {"adaptive":adaptive,"portfolio":portfolio,"catalog":catalog,
                "low_queue_threshold":low_queue_threshold,"low_queue_percent":10}

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
                    if time.monotonic()-self.telemetry_at>=10:
                        try: self.telemetry=self.sample_remote(); self.telemetry_at=time.monotonic()
                        except Exception as error:
                            self.telemetry={**self.telemetry,"connected":False,"telemetry_error":f"{type(error).__name__}: {error}"}
                    with self.state_lock:
                        workers=[]
                        for state in self.worker_states.values():
                            workers.append({k:v for k,v in state.items() if k!="started_monotonic"}|
                                           {"elapsed_seconds":round(time.monotonic()-state["started_monotonic"],1)})
                        durations=sorted(self.durations)
                    rate=completed_total*3600/elapsed; eta=summary["by_status"].get("queued",0)/rate*3600 if rate else None
                    duration_stats={"median_seconds":durations[len(durations)//2] if durations else None,
                                    "p95_seconds":durations[min(len(durations)-1,int(len(durations)*.95))] if durations else None}
                    self.history.append({"time":datetime.now(timezone.utc).isoformat(),"throughput_per_hour":round(rate,2),
                                         "queue":summary["by_status"].get("queued",0),"cpu_percent":self.telemetry.get("cpu",{}).get("total_percent")})
                    self.status(state="running" if active else "idle",host=self.host,workers=self.workers,
                                active=len(active),active_experiment_ids=[x["id"] for x in active.values()],
                                completed_session=completed_total,failed_session=failed_total,
                                throughput_per_hour=round(rate,2),eta_seconds=round(eta) if eta else None,
                                duration=duration_stats,worker_details=workers,telemetry=self.telemetry,history=list(self.history),
                                recovered_stale=recovered,queue=summary["by_status"].get("queued",0),control=control,last_error=None)
                    time.sleep(1 if active else idle_seconds)
                except KeyboardInterrupt:
                    self.status(state="stopped",active=len(active)); return
                except Exception as error:
                    self.status(state="error",active=len(active),last_error=f"{type(error).__name__}: {error}")
                    time.sleep(idle_seconds)
