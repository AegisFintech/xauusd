import json
import pandas as pd
import pytest
from tests.test_lab import setup
from tests.test_research_program import plan
from xauusd import research_program as rp


def test_training_export_preserves_utc_index_and_reports_gaps(tmp_path):
    from xauusd.research_workflow import prepare_training
    frame=pd.DataFrame({'open':[1.,2.,3.],'high':[2.,3.,4.],'low':[.5,1.,2.],
                        'close':[1.5,2.5,3.5],'volume':[1.,1.,1.]},
                       index=pd.to_datetime(['2026-01-01T00:00Z','2026-01-01T00:01Z','2026-01-01T00:03Z']))
    report=prepare_training(tmp_path,frame,'v1')
    csv=pd.read_csv(tmp_path/'train.csv')
    assert csv.timestamp.tolist()==[t.isoformat() for t in frame.index]
    assert report['irregular_intervals']==1 and report['rows']==3
    assert report['timestamps_verified'] and report['scope']=='training_only'
    with pytest.raises(ValueError): prepare_training(tmp_path,frame.reset_index(drop=True),'v1')


@pytest.mark.parametrize('gap',[pd.Timedelta(minutes=2),pd.Timedelta(days=2)])
def test_return_features_exclude_entire_gap_straddling_horizon(gap):
    from xauusd.core import synthetic_bars
    from xauusd.research import build_features
    bars=synthetic_bars(200,seed=12)
    stamps=bars.index.to_list()
    bars.index=pd.DatetimeIndex(stamps[:100]+[s+gap for s in stamps[100:]])
    result=build_features(bars)
    assert not any(t in result.index for t in bars.index[100:115])
    assert bars.index[115] in result.index
    pd.testing.assert_frame_equal(build_features(bars.iloc[:150]),result.loc[:bars.index[149]])


def test_only_two_plans_may_execute_and_success_must_be_interpreted(tmp_path):
    store,_=setup(tmp_path);rp.ensure(store)
    ids=[]
    for i in range(3):
        args=plan();args['family']=str(i);ids.append(rp.create_plan(store,args)['id'])
    for i in range(2):
        assert rp.reserve(store,'analysis',{'plan_id':ids[i],'variant_id':'v','command':'true'},str(i))['ok']
    assert rp.reserve(store,'analysis',{'plan_id':ids[2],'variant_id':'v','command':'true'},'2')['error_code']=='active_experiment_limit'
    rp.finish_call(store,{'id':'0','plan_id':ids[0],'variant_id':'v','state':'completed','result':{'ok':True,'output':'{"trades":10}'}})
    assert rp.reserve(store,'analysis',{'plan_id':ids[1],'variant_id':'v2','command':'true'},'x')['error_code']=='record_completed_result_first'


def test_plan_keeps_evidence_and_code_provenance_after_call_log_rotation(tmp_path):
    from xauusd.research_workflow import resolve_call, result_summary
    from xauusd.agent_advisor import AgentAdvisor
    store,_=setup(tmp_path);rp.ensure(store)
    identifier=rp.create_plan(store,plan())['id']
    class Tools:
        def execute(self,*args):return {'ok':True,'output':'{"trades":12,"base_net":-2,"stress_net":-4}'}
    advisor=AgentAdvisor(store,None,tmp_path,Tools())
    (tmp_path/'study.py').write_text('print(1)')
    row=advisor.execute({'id':'run','name':'analysis','arguments_json':json.dumps({'command':'python study.py','plan_id':identifier,'variant_id':'v'})},tmp_path)
    store.meta('agent_calls',[])
    restored=resolve_call(store,row['id'])
    assert restored['result']==row['result']
    assert restored['provenance']['files']['study.py']
    summary=result_summary(store,row['id'])
    assert summary['metrics']['trades']==12 and summary['classification']=='unvalidated_evidence_summary'
    assert summary['provenance']==restored['provenance']


def test_blockers_are_classified_and_repair_has_priority(tmp_path):
    from xauusd.research_workflow import workflow_status
    store,_=setup(tmp_path);rp.ensure(store)
    a=rp.create_plan(store,plan())['id']
    rp.close_plan(store,{'id':a,'state':'blocked','reason':'KeyError timestamp: train export missing timestamps'})
    status=workflow_status(store)
    assert status['blockers'][0]['category']=='data_schema'
    assert status['next_action']=='repair_shared_blocker'
    assert status['counts']['blocked']==1


def test_improvement_has_one_working_slot_and_protected_fix_is_escalated(tmp_path):
    from xauusd.agent_outcomes import improvement
    from xauusd.research_workflow import workflow_status
    store,_=setup(tmp_path)
    def args(i):return {'id':i,'problem':'defect','change':'fix','acceptance':'regression passes','state':'working'}
    assert improvement(store,args('a'))['ok']
    assert improvement(store,args('b'))['error_code']=='active_improvement_limit'
    store.meta('improvements',[{**args('a'),'state':'blocked'}])
    assert workflow_status(store)['escalations'][0]['id']=='a'


def test_old_workspace_exact_evidence_can_be_recorded_after_log_rotation(tmp_path):
    from xauusd.agent_outcomes import record
    store,_=setup(tmp_path);rp.ensure(store)
    identifier=rp.create_plan(store,plan())['id']
    rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':'v','command':'true'},'old:call')
    rp.finish_call(store,{'id':'old:call','name':'analysis','plan_id':identifier,'variant_id':'v',
                         'state':'completed','result':{'ok':True,'output':'{"trades":2}'}})
    store.meta('agent_calls',[])
    args={'hypothesis':'question','verdict':'investigate','conclusion':'training evidence only','call_id':'old:call',
          'experiment':{'family':'rate_news','dataset_version':'v1','code_sha256':'a'*64,'parameters':{},
                        'costs':{},'metrics':{'trades':2},'failure_reason':'unvalidated','parent_id':None}}
    assert record(store,args)['ok']
    assert not record(store,{**args,'call_id':'new:old:call'})['ok']


def test_result_summary_keeps_metrics_in_compacted_context(tmp_path):
    from xauusd.agent_advisor import compact_context
    value={'tool_results':[{'id':'old:call','name':'analysis','state':'completed',
        'result':{'ok':True,'output':'x'*5000},'evidence_summary':{'metrics':{'trades':12},'complete_evidence':False}}]}
    compact=compact_context(value)
    assert compact['tool_results'][0]['result']['evidence_summary']['metrics']['trades']==12


def test_dashboard_prioritizes_outcomes_over_chat():
    from xauusd.lab_dashboard import PAGE
    assert "views.research.prepend(panel('Research outcomes & blockers','research-completion'))" in PAGE
    assert "function renderCompletion" in PAGE


def test_operator_release_measurements_yield_to_next_autonomous_release(tmp_path):
    from xauusd.research_effectiveness import release_id
    from xauusd.agent_outcomes import improvement
    store,_=setup(tmp_path)
    store.meta('engineering',{'state':'verified','release_id':'old'})
    store.meta('research_operator_release',{'state':'verified','release_id':'operator','engineering_base':'old'})
    assert release_id(store)=='operator'
    args={'id':'fix','problem':'defect','change':'fix','acceptance':'tested','state':'planned'}
    assert improvement(store,args)['ok']
    assert not improvement(store,{**args,'state':'verified'})['ok']
    store.meta('engineering',{'state':'verified','release_id':'new'})
    assert release_id(store)=='new'
    assert improvement(store,{**args,'state':'verified'})['ok']


def test_completed_plan_legacy_evidence_is_backfilled_only_by_exact_id(tmp_path):
    store,_=setup(tmp_path);rp.ensure(store)
    identifier=rp.create_plan(store,plan())['id']
    rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':'v','command':'true'},'old:call')
    rows=store.meta('research_plans');rows[0]['variants']['v'].update(state='completed',ok=True)
    store.meta('research_plans',rows)
    store.meta('agent_calls',[{'id':'old:call','name':'analysis','state':'completed','plan_id':identifier,
                              'variant_id':'v','result':{'ok':True,'output':'{"trades":2}'}}])
    rp.begin_cycle(store)
    store.meta('agent_calls',[])
    from xauusd.research_workflow import resolve_call
    assert resolve_call(store,'old:call')['result']['ok']
    assert resolve_call(store,'other:old:call') is None


def test_failed_terminal_variant_is_not_a_finding_and_gets_recovery_guidance(tmp_path):
    from xauusd.research_effectiveness import diagnostics
    from xauusd.research_execution import directive
    from xauusd.research_workflow import workflow_status
    store,_=setup(tmp_path);rp.ensure(store)
    identifier=rp.create_plan(store,plan())['id']
    rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':'v','command':'true'},'failed:call')
    rp.finish_call(store,{'id':'failed:call','name':'analysis','plan_id':identifier,'variant_id':'v',
                         'state':'completed','result':{'ok':False,'error_code':'fixture_failure'}})
    before=store.meta('research_plans')
    warnings=[row['id'] for row in diagnostics(store)['bottlenecks']]
    assert 'unrecorded_results' not in warnings
    assert 'non_success_results' in warnings
    status=workflow_status(store)
    assert status['awaiting_findings']==[]
    assert status['awaiting_non_success_results']==[{'plan_id':identifier,'call_id':'failed:call','state':'running'}]
    guidance=directive(store)
    assert guidance['stage']=='inspect_non_success_result'
    assert guidance['target']['call_id']=='failed:call'
    assert guidance['result']['ok'] is True
    assert guidance['result']['execution_status']=='REPORTED_FAILURE'
    assert rp.context(store)['recommendation']['action']=='inspect_non_success_result'
    assert store.meta('research_plans')==before



def test_successful_result_has_priority_over_non_success(tmp_path):
    from xauusd.research_execution import directive
    store,_=setup(tmp_path);rp.ensure(store)
    first=rp.create_plan(store,plan())['id']
    args=plan();args['family']='other';second=rp.create_plan(store,args)['id']
    for identifier,call,ok in [(first,'failed:call',False),(second,'success:call',True)]:
        assert rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':'v','command':'true'},call)['ok']
        rp.finish_call(store,{'id':call,'name':'analysis','plan_id':identifier,'variant_id':'v',
                             'state':'completed','result':{'ok':ok,'output':'{"net":-4}' if ok else ''}})
    guidance=directive(store)
    assert guidance['stage']=='interpret_result' and guidance['target']['call_id']=='success:call'
    assert guidance['result']['execution_status']=='SUCCEEDED'
    assert guidance['result']['metrics']['net']==-4


def test_unresolved_variant_is_not_misclassified_or_closed(tmp_path):
    from xauusd.research_workflow import workflow_status, result_summary
    store,_=setup(tmp_path);rp.ensure(store)
    identifier=rp.create_plan(store,plan())['id']
    rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':'v','command':'true'},'unknown:call')
    rp.finish_call(store,{'id':'unknown:call','name':'analysis','plan_id':identifier,'variant_id':'v',
                         'state':'unknown','result':{'ok':True}})
    status=workflow_status(store)
    assert status['awaiting_findings']==[] and status['awaiting_non_success_results']==[]
    summary=result_summary(store,'unknown:call')
    assert summary['execution_status']=='UNKNOWN' and summary['execution_ok'] is False
    assert rp.close_plan(store,{'id':identifier,'state':'blocked','reason':'unknown'})['error_code']=='plan_has_unresolved_variants'
    assert rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':'v','command':'true'},'retry')['error_code']=='plan_variant_already_reserved'


def test_missing_success_flag_stays_unknown(tmp_path):
    from xauusd.research_execution import directive
    store,_=setup(tmp_path);rp.ensure(store)
    identifier=rp.create_plan(store,plan())['id']
    rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':'v','command':'true'},'ambiguous:call')
    rp.finish_call(store,{'id':'ambiguous:call','name':'analysis','plan_id':identifier,'variant_id':'v',
                         'state':'completed','result':{'returncode':0}})
    guidance=directive(store)
    assert guidance['stage']=='inspect_non_success_result'
    assert guidance['result']['execution_status']=='UNKNOWN'
    assert not store.meta('research_plans')[0]['finding_ids']



def test_legacy_missing_outcome_and_evidence_stay_unknown(tmp_path):
    from xauusd.research_execution import directive
    store,_=setup(tmp_path);rp.ensure(store)
    identifier=rp.create_plan(store,plan())['id']
    rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':'v','command':'true'},'missing:call')
    rp.finish_call(store,{'id':'missing:call','name':'analysis','plan_id':identifier,'variant_id':'v',
                         'state':'completed','result':{'ok':False}})
    plans=store.meta('research_plans');variant=plans[0]['variants']['v']
    del variant['ok'];del variant['evidence'];store.meta('research_plans',plans)
    guidance=directive(store)
    assert guidance['stage']=='inspect_non_success_result'
    assert guidance['result']=={'ok':False,'error_code':'evidence_not_retained'}
    assert store.meta('research_plans')[0]['state']=='running'


def test_non_success_waits_when_peer_variant_is_unresolved(tmp_path):
    from xauusd.research_effectiveness import diagnostics
    from xauusd.research_workflow import workflow_status
    store,_=setup(tmp_path);rp.ensure(store)
    identifier=rp.create_plan(store,plan())['id']
    for variant in ('failed','unknown'):
        assert rp.reserve(store,'analysis',{'plan_id':identifier,'variant_id':variant,'command':'true'},variant)['ok']
    rp.finish_call(store,{'id':'failed','name':'analysis','plan_id':identifier,'variant_id':'failed',
                         'state':'completed','result':{'ok':False}})
    rp.finish_call(store,{'id':'unknown','name':'analysis','plan_id':identifier,'variant_id':'unknown',
                         'state':'unknown','result':{'ok':False}})
    assert workflow_status(store)['awaiting_non_success_results']==[]
    assert 'non_success_results' not in [row['id'] for row in diagnostics(store)['bottlenecks']]
    assert rp.close_plan(store,{'id':identifier,'state':'blocked','reason':'unresolved'})['error_code']=='plan_has_unresolved_variants'
