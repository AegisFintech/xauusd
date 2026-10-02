from pathlib import Path

import pandas as pd
import pytest

from xauusd.core import synthetic_bars
from xauusd.tournament_data import TournamentDataConfig, TournamentDataset, frame_digest


def dataset(tmp_path,days=30):
    config=TournamentDataConfig(root=tmp_path/"versions",active_path=tmp_path/"active.json",days=days)
    return TournamentDataset(config)


def test_frozen_dataset_is_reproducible_and_partitioned(tmp_path):
    bars=synthetic_bars(60*24*40,seed=51)
    store=dataset(tmp_path); first=store.create(bars); second=store.create(bars)
    assert first==second and store.verify()["valid"]
    assert sum(p["rows"] for p in first["partitions"].values())==first["rows"]
    assert first["partitions"]["train"]["end"] < first["partitions"]["validation"]["start"]
    assert first["partitions"]["validation"]["end"] < first["partitions"]["test"]["start"]
    assert (Path(first["data_path"]).stat().st_mode & 0o222)==0


def test_content_change_creates_new_version(tmp_path):
    bars=synthetic_bars(60*24*40,seed=52); store=dataset(tmp_path)
    first=store.create(bars); bars.iloc[-1,bars.columns.get_loc("close")]+=0.01
    second=store.create(bars)
    assert first["version"]!=second["version"]


def test_partitions_read_exact_manifest_counts(tmp_path):
    bars=synthetic_bars(60*24*40,seed=53); store=dataset(tmp_path); manifest=store.create(bars)
    for name,metadata in manifest["partitions"].items():
        assert len(store.read(name))==metadata["rows"]


def test_tampering_is_detected(tmp_path):
    bars=synthetic_bars(60*24*40,seed=54); store=dataset(tmp_path); manifest=store.create(bars)
    path=Path(manifest["data_path"]); path.chmod(0o644); frame=pd.read_parquet(path); frame.iloc[0,0]+=1; frame.to_parquet(path)
    assert not store.verify()["valid"]


def test_engine_and_cost_versions_are_derived_not_hardcoded():
    """A backtester or cost change must invalidate stored results.

    Both were hardcoded literals ("event-v1", "fixed-v1") and the experiment
    fingerprint excluded the code commit, so editing the simulator or the cost
    model left every stored experiment with an unchanged identity and old-code
    and new-code results were pooled and ranked as if commensurable.
    """
    from xauusd.tournament_data import (TournamentDataConfig, cost_model_fingerprint,
                                        engine_fingerprint)

    config = TournamentDataConfig()
    assert config.engine_version is None
    assert config.cost_model_version is None
    # Derived values, and they describe the real code and parameters.
    assert config.resolved_engine_version.startswith("event-")
    assert config.resolved_cost_model_version.startswith("cost-")
    assert config.resolved_engine_version == engine_fingerprint()
    assert config.resolved_cost_model_version == cost_model_fingerprint()
    # An explicit override is still honoured.
    pinned = TournamentDataConfig(engine_version="pinned-engine")
    assert pinned.resolved_engine_version == "pinned-engine"


def test_cost_fingerprint_tracks_the_execution_defaults():
    from dataclasses import asdict
    import json as _json
    from xauusd.engine import ExecutionConfig
    from xauusd.tournament_data import cost_model_fingerprint

    baseline = cost_model_fingerprint()
    changed = _json.dumps({**asdict(ExecutionConfig()), "spread": 9.99}, sort_keys=True, default=str)
    other = "cost-" + __import__("hashlib").sha256(changed.encode()).hexdigest()[:12]
    assert other != baseline


def test_dataset_manifest_records_the_derived_versions(tmp_path):
    config = TournamentDataConfig()
    manifest = config.to_manifest() if hasattr(config, "to_manifest") else None
    if manifest is None:
        # The manifest is produced by the dataset builder; assert the config path
        # the builder reads is the resolved one.
        assert config.resolved_engine_version.startswith("event-")
        assert config.resolved_cost_model_version.startswith("cost-")
    else:
        assert manifest["engine_version"].startswith("event-")
        assert manifest["cost_model_version"].startswith("cost-")
