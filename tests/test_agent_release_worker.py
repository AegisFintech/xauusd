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


def test_research_advisories_do_not_disable_safe_software_releases():
    from xauusd.agent_release_worker import release_healthy
    health={'status':'degraded','alerts':['research needs a new hypothesis'],
            'release_readiness':{'status':'ok','alerts':[]},
            'agent':{'heartbeat':{'run_id':'new','planner':'codex','state':'running'},'heartbeat_age_seconds':2},
            'monitor':{'status':'ok','thread_alive':True}}
    assert release_healthy(health,'old')
    health['release_readiness']={'status':'degraded','alerts':['position monitor stale']}
    assert not release_healthy(health,'old')
    health['release_readiness']={'status':'ok','alerts':[]}
    health['monitor']['thread_alive']=False
    assert not release_healthy(health,'old')
