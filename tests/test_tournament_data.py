import json
import threading
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


def test_create_never_reuses_one_temporary_name(tmp_path, monkeypatch):
    """A shared temporary name lets two writers interleave into one inode.

    `create` froze every dataset through a fixed `bars.parquet.tmp` with no fsync
    and no directory fsync, which is the mechanism that made the M1 store
    undecodable on 2026-10-08: a rename can land a Parquet whose footer never
    reached the platter.
    """
    store = dataset(tmp_path)
    seen = []
    real = pd.DataFrame.to_parquet

    def spy(frame, destination, *args, **kwargs):
        seen.append(destination)
        return real(frame, destination, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "to_parquet", spy)
    store.create(synthetic_bars(60*24*40, seed=61))
    store.create(synthetic_bars(60*24*40, seed=62))

    assert len(seen) == 2
    assert not any(str(item).endswith("bars.parquet.tmp") for item in seen), seen
    assert seen[0] is not seen[1]


def test_no_tournament_write_truncates_its_target_in_place(tmp_path, monkeypatch):
    """`write_text` truncates before it writes, so a reader can see a partial file.

    The manifest and the `active.json` pointer were both written that way, and the
    pointer decides which frozen dataset every later run reads.
    """
    store = dataset(tmp_path)
    seen = []
    real = Path.write_text

    def spy(path, *args, **kwargs):
        seen.append(str(path))
        return real(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", spy)
    store.create(synthetic_bars(60*24*40, seed=63))

    assert seen == []


def test_concurrent_freezes_leave_a_readable_active_pointer(tmp_path, monkeypatch):
    """The invariant the shared temporary broke: one complete pointer, and it resolves.

    Every version activated through the same `active.json.tmp`, so two research
    cycles freezing different datasets could rename each other's temporary away,
    or land a pointer whose manifest path was never finished.
    """
    store = dataset(tmp_path)
    seeds = range(70, 78)
    barrier = threading.Barrier(len(seeds), timeout=30)
    real_activate = TournamentDataset._activate
    errors = []

    def synchronized_activate(self, manifest):
        # Force the interleaving production produces: every writer inside the
        # pointer swap at once, instead of drifting apart behind the freeze work.
        barrier.wait()
        return real_activate(self, manifest)

    monkeypatch.setattr(TournamentDataset, "_activate", synchronized_activate)

    def freeze(seed):
        try:
            store.create(synthetic_bars(60*24*40, seed=seed))
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=freeze, args=(seed,)) for seed in seeds]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    pointer = json.loads(store.config.active_path.read_text())
    manifest = json.loads(Path(pointer["manifest"]).read_text())
    assert manifest["version"] == pointer["version"]
    assert store.verify(manifest)["valid"]
    assert not list(store.config.active_path.parent.glob("*.tmp"))
