from tests.test_lab import setup


def test_counters_survive_detail_eviction_and_ignore_duplicate_updates(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    from xauusd.lab_statistics import snapshot
    store,_=setup(tmp_path); advisor=AgentAdvisor(store,None,tmp_path)
    for i in range(105):
        row={'id':str(i),'name':'tc02_run','state':'running','started_at':'2026-10-24T00:00:00+00:00'}
        advisor._calls(row)
        row={**row,'state':'completed','finished_at':'2026-10-24T00:00:02+00:00',
             'result':{'ok':True,'cpu_seconds':.2,'wall_seconds':2}}
        advisor._calls(row);advisor._calls(row)
    stats=snapshot(store)
    assert len(store.meta('agent_calls'))==100
    assert stats['totals']['tools.tc02_run.started']==105
    assert stats['totals']['tools.tc02_run.completed']==105
    assert abs(stats['totals']['tc02.cpu_seconds']-21)<.001
    assert stats['totals']['tc02.wall_seconds']==210
    assert stats['scope']=='since_counter_installation'


def test_counter_update_rolls_back_with_owning_state_transaction(tmp_path):
    import pytest
    from xauusd.lab_statistics import transition, snapshot
    store,_=setup(tmp_path)
    with pytest.raises(RuntimeError):
        with store.state.transaction() as tx:
            transition(tx,'sessions',None,{'state':'running'})
            raise RuntimeError('rollback')
    assert snapshot(store)['totals']=={}
