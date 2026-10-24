from tests.test_lab import setup


def test_release_success_does_not_imply_measured_improvement(tmp_path):
    from xauusd.research_effectiveness import start_measurement,review
    store,_=setup(tmp_path)
    store.meta('engineering',{'state':'verified','release_id':'old'})
    store.meta('agent_calls',[{'id':str(i),'name':'evidence_read','state':'completed','result':{'ok':True}} for i in range(12)])
    assert start_measurement(store,'retrieval','evidence_read_share')['ok']
    assert review(store)['measurements'][0]['state']=='awaiting_verified_release'
    store.meta('engineering',{'state':'verified','release_id':'new'})
    assert review(store)['measurements'][0]['state']=='awaiting_linked_verified_improvement'
    store.meta('improvements',[{'id':'retrieval','state':'verified','release_id':'new'}])
    assert review(store)['measurements'][0]['state']=='collecting_samples'
    store.meta('agent_calls',[{'id':'new'+str(i),'name':'analysis','state':'completed','result':{'ok':True},'release_id':'new'} for i in range(10)])
    measured=review(store)['measurements'][0]
    assert measured['state']=='improved' and measured['relative_change']==1
    assert measured['interpretation'].startswith('observational')


def test_missing_baseline_cannot_be_claimed_and_inference_history_is_bounded(tmp_path):
    from xauusd.research_effectiveness import inference,start_measurement,review
    store,_=setup(tmp_path)
    store.meta('engineering',{'state':'verified','release_id':'old'})
    assert start_measurement(store,'latency','inference_seconds')['ok']
    store.meta('engineering',{'state':'verified','release_id':'new'})
    store.meta('improvements',[{'id':'latency','state':'verified','release_id':'new'}])
    for i in range(125):inference(store,2.,True,100)
    assert len(store.meta('research_inference')['samples'])==120
    assert store.meta('research_inference')['count']==125
    assert review(store)['measurements'][0]['state']=='insufficient_baseline'


def test_measured_bottleneck_seeds_one_backlog_item_and_preserves_baseline(tmp_path):
    from xauusd.research_effectiveness import review
    store,_=setup(tmp_path)
    store.meta('agent_calls',[{'id':str(i),'name':'evidence_read','state':'completed','result':{'ok':True}} for i in range(15)])
    review(store);review(store)
    assert len(store.meta('improvements'))==1
    assert store.meta('improvements')[0]['state']=='planned'
    assert store.meta('improvement_measurements')[0]['baseline']['samples']==15


def test_observed_regression_cannot_be_labeled_improved(tmp_path):
    from xauusd.research_effectiveness import start_measurement,review
    store,_=setup(tmp_path)
    store.meta('engineering',{'state':'verified','release_id':'old'})
    store.meta('agent_calls',[{'id':str(i),'name':'analysis','state':'completed','duration_seconds':1,'result':{'ok':True}} for i in range(10)])
    start_measurement(store,'latency','tool_seconds')
    store.meta('engineering',{'state':'verified','release_id':'new'})
    store.meta('agent_calls',[{'id':str(i),'name':'analysis','state':'completed','duration_seconds':2,'release_id':'new','result':{'ok':True}} for i in range(10)])
    store.meta('improvements',[{'id':'latency','state':'verified','release_id':'new'}])
    assert review(store)['measurements'][0]['state']=='regressed'


def test_recent_metric_window_does_not_bias_toward_retained_old_unknowns(tmp_path):
    from xauusd.research_effectiveness import metric
    store,_=setup(tmp_path)
    recent=[{'id':str(i),'name':'analysis','state':'completed','finished_at':'2026-10-24T00:00:00Z','result':{'ok':True}} for i in range(20)]
    old=[{'id':'old'+str(i),'name':'tc02_run','state':'unknown','started_at':'2026-10-20T00:00:00Z'} for i in range(12)]
    store.meta('agent_calls',recent+old)
    assert metric(store,'tool_failure_rate')['value']==0
