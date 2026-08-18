from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from xauusd.automation import (AutomationConfig, ChampionRegistry, RunLock, atomic_json,
                               automated_attempt, render_html, weekly_comparison)


def test_registry_only_promotes_passing_better_candidate(tmp_path):
    registry=ChampionRegistry(tmp_path/"champion.json")
    assert not registry.consider({"strategy":"bad","score":10,"passed":False})["promoted"]
    assert registry.read() is None
    assert registry.consider({"strategy":"first","score":1,"passed":True})["promoted"]
    assert not registry.consider({"strategy":"worse","score":0,"passed":True})["promoted"]
    assert registry.read()["strategy"]=="first"


def test_atomic_json_replaces_complete_document(tmp_path):
    path=tmp_path/"x.json"; atomic_json(path,{"value":1}); atomic_json(path,{"value":2})
    assert path.read_text().strip().endswith("}") and '2' in path.read_text()
    assert not path.with_suffix(".json.tmp").exists()


def test_html_report_contains_candidates():
    manifest={"run_id":"run-1","data":{"start":"a","end":"b","rows":10},
              "candidates":[{"strategy":"mean_reversion","score":-1.,"net_profit":-2.,"profit_factor":.8,"passed":False}]}
    html=render_html(manifest)
    assert "mean_reversion" in html and "FAIL" in html and "<table>" in html


def test_weekly_comparison_collects_archived_runs(tmp_path):
    for number in (1,2):
        directory=tmp_path/f"run-{number}"; directory.mkdir()
        atomic_json(directory/"manifest.json",{"run_id":f"run-{number}","candidates":[
            {"strategy":"momentum","score":-number,"net_profit":-10*number,"passed":False}]})
    report=weekly_comparison(tmp_path)
    assert report["runs"]==2 and len(report["strategies"]["momentum"])==2


def test_run_lock_rejects_overlap(tmp_path):
    with RunLock(tmp_path/"run.lock"):
        try:
            with RunLock(tmp_path/"run.lock"):
                assert False
        except RuntimeError as exc:
            assert "already active" in str(exc)


def test_automated_attempt_records_failure(tmp_path,monkeypatch):
    config=AutomationConfig(reports_dir=tmp_path,status_path=tmp_path/"status.json",attempts_path=tmp_path/"attempts.jsonl")
    def fail(*args,**kwargs): raise RuntimeError("expected failure")
    monkeypatch.setattr("xauusd.automation.DailyResearchPipeline.run",fail)
    attempt=automated_attempt(config)
    assert attempt["status"]=="failed" and "expected failure" in attempt["error"]
    assert config.status_path.exists() and config.attempts_path.exists()
