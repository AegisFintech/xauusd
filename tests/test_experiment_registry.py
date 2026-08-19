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


def test_leaderboard_orders_validation_score(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db")
 for value,score in ((1,2.0),(2,1.0)):
  row,_=registry.register(spec(x=value)); claimed=registry.claim_next("w")
  registry.complete(claimed["id"],"w",{"validation":{"net_profit":value}}, {"passed":True,"score":score})
 assert [row["validation"]["score"] for row in registry.leaderboard()]==[2.0,1.0]


def test_replaced_worker_is_recovered_immediately(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db"); row,_=registry.register(spec()); registry.claim_next("old")
 assert registry.recover_other_workers("new")==1 and registry.get(row["id"])["status"]=="queued"


def test_remote_error_can_requeue_owned_experiment(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db"); row,_=registry.register(spec()); claimed=registry.claim_next("remote")
 result=registry.requeue(claimed["id"],"remote","connection lost")
 assert result["status"]=="queued" and result["worker_id"] is None
 assert registry.events(row["id"])[-1]["event"]=="requeued_remote_error"


def test_champion_history_is_atomic_and_requires_improvement(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db")
 rows=[]
 for value in (1,2): rows.append(registry.register(spec(x=value))[0])
 first=registry.promote_champion("dataset-v1",rows[0]["id"],1,2,{"net_profit":10})
 second=registry.promote_champion("dataset-v1",rows[1]["id"],2,3,{"net_profit":20})
 assert second["previous_experiment_id"]==first["experiment_id"]
 assert [x["experiment_id"] for x in registry.champion_history("dataset-v1")]==[rows[1]["id"],rows[0]["id"]]
 with pytest.raises(ValueError): registry.promote_champion("dataset-v1",rows[0]["id"],4,2.5,{})
