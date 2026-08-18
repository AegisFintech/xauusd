from datetime import datetime, timedelta, timezone

import pytest

from xauusd.experiment_registry import ExperimentRegistry, ExperimentSpec


def spec(**parameters):
    return ExperimentSpec("mean_reversion", "zscore(entry_z,exit_z)", parameters or {"entry_z":1.5},
                          "dataset-v1", "abc123", "engine-v1", "cost-v1", "commit1")


def test_fingerprint_is_canonical_and_ignores_commit():
    a=spec(a=1,b=2); b=ExperimentSpec(a.strategy_family,a.formula,{"b":2,"a":1},a.dataset_version,
                                      a.dataset_fingerprint,a.engine_version,a.cost_model_version,"other")
    assert a.fingerprint==b.fingerprint


def test_registration_rejects_duplicate_identity(tmp_path):
    registry=ExperimentRegistry(tmp_path/"registry.db")
    first,created=registry.register(spec(entry_z=1.5)); second,created_again=registry.register(spec(entry_z=1.5))
    assert created and not created_again and first["id"]==second["id"]
    assert registry.summary()["total"]==1


def test_worker_lifecycle_and_events(tmp_path):
    registry=ExperimentRegistry(tmp_path/"registry.db"); registry.register(spec(),priority=5)
    claimed=registry.claim_next("worker-1"); registry.heartbeat(claimed["id"],"worker-1")
    result=registry.complete(claimed["id"],"worker-1",{"net_profit":12.},
                             {"passed":True},{"ledger":"trades.csv"},promoted=True)
    assert result["status"]=="completed" and result["metrics"]["net_profit"]==12
    assert result["promoted"] and [e["event"] for e in registry.events(result["id"])]==["registered","claimed","completed"]
    with pytest.raises(ValueError): registry.complete(result["id"],"worker-1",{})


def test_claim_is_priority_ordered_and_failure_is_recorded(tmp_path):
    registry=ExperimentRegistry(tmp_path/"registry.db")
    registry.register(spec(x=1),priority=1); registry.register(spec(x=2),priority=10)
    claimed=registry.claim_next("w"); assert claimed["parameters"]=={"x":2}
    failed=registry.fail(claimed["id"],"w","boom"); assert failed["status"]=="failed" and failed["error"]=="boom"


def test_stale_work_is_requeued(tmp_path):
    registry=ExperimentRegistry(tmp_path/"registry.db"); registered,_=registry.register(spec()); registry.claim_next("dead")
    with registry.connect() as db:
        db.execute("UPDATE experiments SET heartbeat_at=? WHERE id=?", ((datetime.now(timezone.utc)-timedelta(hours=2)).isoformat(),registered["id"]))
    assert registry.recover_stale(datetime.now(timezone.utc)-timedelta(hours=1))==1
    assert registry.get(registered["id"])["status"]=="queued"
