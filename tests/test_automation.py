from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

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


def _pipeline_config(tmp_path, **overrides):
    from xauusd.automation import AutomationConfig
    base = dict(lookback_days=10, validate_top=5, minimum_freshness_hours=10_000,
                reports_dir=tmp_path / "automation", registry_path=tmp_path / "champion.json",
                status_path=tmp_path / "status.json", attempts_path=tmp_path / "attempts.jsonl")
    base.update(overrides)
    return AutomationConfig(**base)


def _seed_store(tmp_path, periods=6000):
    """A store whose newest bar is fresh and which contains a real, cost-aware edge.

    A pure random walk has no profitable strategy under the gates, and the pipeline
    now refuses to promote a loser, so the fixture needs an exploitable
    oscillation rather than noise.
    """
    from xauusd.data import DataConfig, HistoricalDataStore
    end = pd.Timestamp.now(tz="UTC").floor("min")
    index = pd.date_range(end - pd.Timedelta(minutes=periods - 1), periods=periods, freq="min", tz="UTC")
    rng = np.random.default_rng(11)
    steps = np.arange(periods)
    close = 2000 + 8 * np.sin(steps / 45.0) + 3 * np.sin(steps / 13.0) + rng.normal(0, 0.6, periods)
    bars = pd.DataFrame({"open": close, "high": close + 0.4, "low": close - 0.4, "close": close,
                         "volume": rng.integers(50, 500, periods)}, index=index)
    store = HistoricalDataStore(DataConfig(processed_dir=tmp_path / "processed",
                                           raw_dir=tmp_path / "raw"))
    store.write(bars)
    return store


def _permissive_validation():
    from xauusd.validation import ValidationConfig
    return ValidationConfig(walk_forward_folds=2, bootstrap_samples=20, minimum_trades=5,
                            minimum_positive_folds=0.0, minimum_stable_neighbors=0.0,
                            maximum_drawdown=-1.0)


def test_pipeline_validates_on_bars_that_did_not_choose_the_candidate(tmp_path, monkeypatch):
    """Ranking, validation and selection must use three disjoint partitions.

    The pipeline ranked every candidate on the whole lookback and then validated
    the top N on a split carved out of that same lookback, so the held-out
    "test" segment was inside the data that chose the candidate.
    """
    _seed_store(tmp_path)
    monkeypatch.setattr("xauusd.automation.HistoricalDataStore", lambda: _seed_store(tmp_path))
    from xauusd.automation import DailyResearchPipeline

    manifest = DailyResearchPipeline(_pipeline_config(tmp_path), validation=_permissive_validation()).run()

    partitions = manifest["data"]["partitions"]
    assert set(partitions) == {"train", "validation", "test"}
    # Strictly ordered, non-overlapping, and the validation window is a minority of
    # the data so it cannot be the data that chose the candidate.
    assert partitions["train"]["end"] < partitions["validation"]["start"]
    assert partitions["validation"]["end"] < partitions["test"]["start"]
    assert partitions["validation"]["rows"] < partitions["train"]["rows"]
    # The run id is content-addressed, so a data revision cannot reuse it.
    assert manifest["data"]["fingerprint"]
    assert manifest["run_id"].endswith(manifest["data"]["fingerprint"])


def test_pipeline_refuses_to_run_when_no_candidate_passes(tmp_path, monkeypatch):
    """An all-fail run must not promote `candidates[0]` anyway."""
    _seed_store(tmp_path)
    monkeypatch.setattr("xauusd.automation.HistoricalDataStore", lambda: _seed_store(tmp_path))
    from xauusd.automation import DailyResearchPipeline

    pipeline = DailyResearchPipeline(_pipeline_config(tmp_path))
    # Force every candidate to fail validation.
    monkeypatch.setattr(type(pipeline.validation), "minimum_trades", 10 ** 9)

    with pytest.raises(RuntimeError, match="no candidate passed validation"):
        pipeline.run()
    assert not (tmp_path / "champion.json").exists()


def test_champion_record_is_bound_to_the_dataset_that_authorised_it(tmp_path):
    """A bare score with no provenance could be compared against anything."""
    from xauusd.automation import ChampionRegistry

    registry = ChampionRegistry(tmp_path / "champion.json")
    first = registry.consider({"strategy": "a", "score": 5.0, "passed": True},
                              dataset_fingerprint="fp-1")
    assert first["promoted"] is True
    champion = registry.read()
    assert champion["schema"] == "xauusd.champion/2"
    assert champion["dataset_fingerprint"] == "fp-1"
    assert champion["promoted_at"]

    # A better score on the same bars does promote.
    better = registry.consider({"strategy": "b", "score": 6.0, "passed": True},
                               dataset_fingerprint="fp-1")
    assert better["promoted"] is True
    # A worse score on the same bars does not.
    worse = registry.consider({"strategy": "c", "score": 1.0, "passed": True},
                              dataset_fingerprint="fp-1")
    assert worse["promoted"] is False
    assert registry.read()["strategy"] == "b"

    # A different dataset stands on its own: the old score is not comparable, so
    # a passing candidate is promoted rather than measured against a stale number.
    changed = registry.consider({"strategy": "d", "score": 0.1, "passed": True},
                                dataset_fingerprint="fp-2")
    assert changed["promoted"] is True
    assert "dataset changed" in changed["reason"]


def test_champion_is_not_replaced_when_either_side_lacks_a_dataset_binding(tmp_path):
    from xauusd.automation import ChampionRegistry

    registry = ChampionRegistry(tmp_path / "champion.json")
    registry.consider({"strategy": "a", "score": 5.0, "passed": True}, dataset_fingerprint="fp-1")

    unbound = registry.consider({"strategy": "b", "score": 99.0, "passed": True})
    assert unbound["promoted"] is False
    assert "not bound to a dataset" in unbound["reason"]
    assert registry.read()["strategy"] == "a"


def test_champion_never_promotes_a_candidate_with_no_score(tmp_path):
    from xauusd.automation import ChampionRegistry

    registry = ChampionRegistry(tmp_path / "champion.json")
    result = registry.consider({"strategy": "a", "score": None, "passed": True},
                               dataset_fingerprint="fp-1")
    assert result["promoted"] is False
    assert result["eligible"] is False
    assert registry.read() is None
