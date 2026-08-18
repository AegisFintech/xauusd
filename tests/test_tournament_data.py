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
