import json
import subprocess

from xauusd.codex_workflow import CodexImprovementWorkflow,CodexWorkflowConfig
from xauusd.experiment_registry import ExperimentRegistry,ExperimentSpec


DATASET={"version":"v1","fingerprint":"abc","engine_version":"e1","cost_model_version":"c1",
         "symbol":"XAUUSD","timeframe":"M1","rows":100,"partitions":{"train":{},"validation":{},"test":{}}}


def repository(tmp_path):
 repo=tmp_path/"repo"; repo.mkdir(); subprocess.run(["git","init","-q"],cwd=repo,check=True)
 subprocess.run(["git","config","user.email","test@example.com"],cwd=repo,check=True)
 subprocess.run(["git","config","user.name","Test"],cwd=repo,check=True)
 (repo/"README.md").write_text("test"); subprocess.run(["git","add","."],cwd=repo,check=True)
 subprocess.run(["git","commit","-qm","initial"],cwd=repo,check=True); return repo


def test_research_brief_is_redacted_and_aggregated(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db"); row,_=registry.register(ExperimentSpec("momentum","f",{},"v1","abc","e1","c1"))
 claimed=registry.claim_next("w"); registry.complete(claimed["id"],"w",{"validation":{"net_profit":1}},{"score":2,"passed":True})
 brief=CodexImprovementWorkflow(registry).research_brief(DATASET)
 encoded=json.dumps(brief)
 assert brief["constraints"]["no_credentials"] and "password" not in encoded.lower() and brief["leaders"][0]["experiment_id"]==row["id"]


def test_prepare_creates_detached_review_only_worktree(tmp_path):
 repo=repository(tmp_path); registry=ExperimentRegistry(tmp_path/"registry.db")
 config=CodexWorkflowConfig(repo,tmp_path/"worktrees",tmp_path/"reports")
 workflow=CodexImprovementWorkflow(registry,config); state=workflow.prepare(DATASET)
 assert state["status"]=="prepared" and state["auto_merge"] is False
 assert (tmp_path/"worktrees"/state["run_id"]/"RESEARCH_BRIEF.json").exists()
 assert not (repo/"RESEARCH_BRIEF.json").exists()
 workflow.cleanup(state)


def test_prompt_has_explicit_safety_boundaries(tmp_path):
 repo=repository(tmp_path); workflow=CodexImprovementWorkflow(ExperimentRegistry(tmp_path/"r.db"),
  CodexWorkflowConfig(repo,tmp_path/"w",tmp_path/"out")); state=workflow.prepare(DATASET)
 prompt=state["prompt"]
 assert ".env" in prompt and "Do not commit" in prompt and "test partition" in prompt
 workflow.cleanup(state)


def test_codex_child_environment_uses_allowlist(tmp_path,monkeypatch):
 repo=repository(tmp_path); workflow=CodexImprovementWorkflow(ExperimentRegistry(tmp_path/"r.db"),
  CodexWorkflowConfig(repo,tmp_path/"w",tmp_path/"out")); captured={}
 monkeypatch.setenv("CTRADER_PASSWORD","must-not-leak")
 original_run=subprocess.run
 def fake_run(command,**kwargs):
  if command[0]=="codex":
   captured.update(kwargs["env"]); return subprocess.CompletedProcess(command,1,"","fake")
  return original_run(command,**kwargs)
 monkeypatch.setattr("xauusd.codex_workflow.subprocess.run",fake_run)
 state=workflow.run(DATASET)
 assert state["status"]=="rejected" and "CTRADER_PASSWORD" not in captured
 workflow.cleanup(state)
