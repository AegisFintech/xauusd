from types import SimpleNamespace


def test_worker_requires_new_healthy_heartbeat_before_acceptance():
    from xauusd.agent_release_worker import release_healthy
    health={'status':'ok','alerts':[], 'agent':{'heartbeat':{'run_id':'new','planner':'codex','state':'running'},'heartbeat_age_seconds':2},
            'monitor':{'status':'ok','thread_alive':True}}
    assert release_healthy(health,'old')
    assert not release_healthy(health,'new')
    health['alerts']=['stale data']
    assert not release_healthy(health,'old')


def test_failed_worker_schedule_rolls_back_without_retry(monkeypatch):
    from xauusd.agent_release_worker import schedule_verification
    class Store:
        def meta(self,key):return {'state':'pending_health'}
        def event(self,*args):pass
    calls=[]
    manager=SimpleNamespace(verify_pending=lambda healthy:calls.append(healthy))
    monkeypatch.setattr('xauusd.agent_release_worker.subprocess.run',lambda *a,**kw:SimpleNamespace(returncode=1))
    assert schedule_verification(Store(),manager)['ok'] is False
    assert calls==[False]
