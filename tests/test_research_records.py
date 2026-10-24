from tests.test_lab import setup
from xauusd.agent_outcomes import record


def payload(call='a'):
    return {'hypothesis':'reversal','verdict':'reject','conclusion':'costs erase edge','call_id':call,
            'experiment':{'family':'reversal','dataset_version':'v1','code_sha256':'a'*64,
                          'parameters':{'lookback':5},'costs':{'per_trade':1.08},
                          'metrics':{'trades':10,'profit_factor':None,'net_profit':-2.},
                          'failure_reason':'cost_stress','parent_id':None}}


def test_structured_findings_deduplicate_equivalent_experiments(tmp_path):
    store,_=setup(tmp_path)
    store.meta('agent_calls',[{'id':v,'name':'analysis','state':'completed','result':{'ok':True}} for v in ('a','b')])
    first=record(store,payload())
    assert first['ok']
    second=record(store,payload('b'))
    assert second['replayed'] and second['equivalent_experiment']
    assert len(store.meta('research_outcomes'))==1
    assert store.meta('research_outcomes')[0]['experiment']['metrics']['profit_factor'] is None


def test_invalid_metrics_or_missing_parent_do_not_replace_findings(tmp_path):
    store,_=setup(tmp_path)
    store.meta('agent_calls',[{'id':'a','name':'analysis','state':'completed','result':{'ok':True}}])
    assert record(store,payload())['ok']
    store.meta('agent_calls',[{'id':'b','name':'analysis','state':'completed','result':{'ok':True}}])
    for value in (float('inf'),float('nan'),True,'profitable'):
        args=payload('b');args['experiment']['metrics']['net_profit']=value
        assert not record(store,args)['ok']
    args=payload('b');args['experiment']['parent_id']='absent'
    assert not record(store,args)['ok']
    assert len(store.meta('research_outcomes'))==1
