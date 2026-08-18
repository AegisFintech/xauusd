from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import subprocess
import uuid

from .experiment_registry import ExperimentRegistry


FORBIDDEN_PATHS=(".env","data/","reports/","deploy/","xauusd/data.py")


@dataclass(frozen=True)
class CodexWorkflowConfig:
    repository: Path=Path(".")
    worktree_root: Path=Path("/tmp/xauusd-codex-worktrees")
    report_root: Path=Path("reports/tournament/codex")
    timeout_seconds: int=3600


class CodexImprovementWorkflow:
    """Create review-only Codex candidates in disposable detached worktrees."""
    def __init__(self,registry: ExperimentRegistry | None=None,config: CodexWorkflowConfig | None=None):
        self.registry=registry or ExperimentRegistry(); self.config=config or CodexWorkflowConfig()

    def research_brief(self,dataset: dict) -> dict:
        leaders=self.registry.leaderboard(20)
        families={}
        for row in self.registry.list("completed",limit=500):
            metrics=(row.get("metrics") or {}).get("validation") or {}
            bucket=families.setdefault(row["strategy_family"],{"experiments":0,"best_score":None,"best_net_profit":None})
            bucket["experiments"]+=1
            score=(row.get("validation") or {}).get("score")
            if score is not None: bucket["best_score"]=score if bucket["best_score"] is None else max(bucket["best_score"],score)
            profit=metrics.get("net_profit")
            if profit is not None: bucket["best_net_profit"]=profit if bucket["best_net_profit"] is None else max(bucket["best_net_profit"],profit)
        return {"dataset":{"version":dataset["version"],"symbol":dataset["symbol"],"timeframe":dataset["timeframe"],
                           "rows":dataset["rows"],"partitions":dataset["partitions"]},
                "constraints":{"research_only":True,"no_credentials":True,"no_broker_execution":True,
                               "do_not_read_test_partition":True,"causal_signals_only":True},
                "families":families,
                "leaders":[{"experiment_id":x["id"],"family":x["strategy_family"],"parameters":x["parameters"],
                            "validation":x["validation"],"metrics":(x.get("metrics") or {}).get("validation")} for x in leaders]}

    def prepare(self,dataset: dict) -> dict:
        run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:8]
        report_dir=self.config.report_root/run_id; report_dir.mkdir(parents=True)
        worktree=self.config.worktree_root/run_id; worktree.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(["git","worktree","add","--detach",str(worktree),"HEAD"],cwd=self.config.repository,
                       check=True,capture_output=True,text=True)
        brief=self.research_brief(dataset)
        (report_dir/"research-brief.json").write_text(json.dumps(brief,indent=2,allow_nan=False))
        prompt=("Improve this historical XAUUSD research engine by adding one genuinely new causal strategy family. "
                "Read RESEARCH_BRIEF.json. Modify only xauusd/research.py and tests. Do not access .env, data, reports, "
                "broker/network APIs, the frozen test partition, deployment files, or execution connectivity. Add tests "
                "for causality, bounded signals, and formula sensitivity. Run the focused tests. Do not commit, merge, "
                "push, or modify the primary worktree. End with a concise review summary.")
        (worktree/"RESEARCH_BRIEF.json").write_text(json.dumps(brief,indent=2,allow_nan=False))
        state={"run_id":run_id,"status":"prepared","created_at":datetime.now(timezone.utc).isoformat(),
               "worktree":str(worktree),"report_dir":str(report_dir),"prompt":prompt,"auto_merge":False}
        self._write_state(report_dir,state); self._latest(state)
        return state

    def run(self,dataset: dict) -> dict:
        state=self.prepare(dataset); report_dir=Path(state["report_dir"]); worktree=Path(state["worktree"])
        output=worktree/"CODEX_OUTPUT.txt"
        command=["codex","exec","--ephemeral","--sandbox","workspace-write","--cd",str(worktree),
                 "--output-last-message",str(output),state["prompt"]]
        state.update(status="running",started_at=datetime.now(timezone.utc).isoformat(),command=command[:-1]+["<bounded-prompt>"])
        self._write_state(report_dir,state); self._latest(state)
        try:
            allowed=("PATH","CODEX_HOME","LANG","LC_ALL","TERM","SSL_CERT_FILE","SSL_CERT_DIR")
            clean_env={key:os.environ[key] for key in allowed if key in os.environ}
            clean_env.update({"HOME":str(worktree/".isolated-home"),"NO_COLOR":"1"})
            (worktree/".isolated-home").mkdir()
            process=subprocess.run(command,cwd=worktree,text=True,capture_output=True,
                                   timeout=self.config.timeout_seconds,env=clean_env)
            (report_dir/"codex-stdout.log").write_text(process.stdout); (report_dir/"codex-stderr.log").write_text(process.stderr)
            if output.exists(): (report_dir/"codex-output.txt").write_text(output.read_text())
            subprocess.run(["git","clean","-fd","--","CODEX_OUTPUT.txt",".isolated-home"],cwd=worktree,capture_output=True)
            changed=subprocess.run(["git","diff","--name-only"],cwd=worktree,text=True,capture_output=True,check=True).stdout.splitlines()
            forbidden=[path for path in changed if any(path==item or path.startswith(item) for item in FORBIDDEN_PATHS)]
            tests=subprocess.run([str(Path.cwd()/".venv/bin/python"),"-m","pytest","-q","tests/test_research.py"],
                                 cwd=worktree,text=True,capture_output=True,timeout=600)
            patch=subprocess.run(["git","diff","--binary"],cwd=worktree,text=True,capture_output=True,check=True).stdout
            (report_dir/"candidate.patch").write_text(patch); (report_dir/"validation.log").write_text(tests.stdout+tests.stderr)
            accepted=process.returncode==0 and tests.returncode==0 and not forbidden and bool(changed)
            state.update(status="review_ready" if accepted else "rejected",finished_at=datetime.now(timezone.utc).isoformat(),
                         codex_exit_code=process.returncode,test_exit_code=tests.returncode,changed_files=changed,
                         forbidden_changes=forbidden,patch=str(report_dir/"candidate.patch"),auto_merge=False)
        except Exception as error:
            state.update(status="failed",finished_at=datetime.now(timezone.utc).isoformat(),error=f"{type(error).__name__}: {error}")
        self._write_state(report_dir,state); self._latest(state)
        return state

    def cleanup(self,state: dict) -> None:
        worktree=Path(state["worktree"])
        if worktree.exists():
            subprocess.run(["git","worktree","remove","--force",str(worktree)],cwd=self.config.repository,check=True)

    @staticmethod
    def _write_state(directory: Path,state: dict) -> None:
        (directory/"state.json").write_text(json.dumps(state,indent=2))

    def _latest(self,state: dict) -> None:
        path=self.config.report_root/"latest.json"; path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_suffix(".json.tmp"); temporary.write_text(json.dumps(state,indent=2)); temporary.replace(path)
