import json
from tests.test_lab import setup
from xauusd.agent_advisor import AgentAdvisor
from xauusd.research_effectiveness import diagnostics
from xauusd.research_workflow import result_summary


def invoke(advisor,root,i,name,args):
    return advisor.execute({'id':str(i),'name':name,'arguments_json':json.dumps(args)},root)


def test_large_result_retains_final_page_across_restart(tmp_path):
    store,_=setup(tmp_path)
    payload={'ok':True,'output':'a'*19000+'END_OF_EVIDENCE'}
    class Tools:
        def execute(self,name,args):return payload
    a=AgentAdvisor(store,None,tmp_path,Tools())
    row=invoke(a,tmp_path,1,'market_observe',{})
    a=AgentAdvisor(store,None,tmp_path,Tools())
    page=invoke(a,tmp_path,2,'evidence_read',{'call_id':row['id'],'offset':18500,'limit':4000})['result']
    assert 'END_OF_EVIDENCE' in page['content'] and page['next_offset'] is None
    assert store.meta('agent_calls')[0]['result']==payload


def test_large_experiment_review_is_success_and_has_decision_summary(tmp_path):
    store,_=setup(tmp_path)
    store.meta('experiments',[{'id':str(i),'name':'x','summary':{'equity':1000+i,'position':0,'recent_fills':['x'*5000]},'last_verdict':None} for i in range(4)])
    a=AgentAdvisor(store,None,tmp_path)
    row=invoke(a,tmp_path,1,'experiment_review',{})
    assert row['result']['ok'] is True
    summary=result_summary(store,row['id'])
    assert summary['decision_fields']['capacity']==4
    assert summary['decision_fields']['accounts'][3]['metrics']['equity']==1003
    assert len(json.dumps(summary))<5000


def test_recent_retrieval_regression_is_detected_despite_old_calls(tmp_path):
    store,_=setup(tmp_path)
    store.meta('agent_calls',[{'id':str(i),'name':'analysis' if i<80 else 'evidence_read','state':'completed','finished_at':f'{i:04}', 'result':{'ok':True}} for i in range(100)])
    assert 'retrieval_overhead' in [r['id'] for r in diagnostics(store)['bottlenecks']]


def test_timeout_repair_directive_is_durable_and_ignores_paper_capacity(tmp_path):
    from xauusd.research_execution import directive
    store,paper=setup(tmp_path)
    before=paper.state()
    store.meta('experiments',[{'id':str(i)} for i in range(4)])
    store.meta('research_inference',{'samples':[{'ok':False,'seconds':600} for _ in range(10)]})
    d=directive(store)
    assert d['stage']=='repair' and d['target']['id']=='inference_failures'
    assert d['paper_capacity_blocks_research'] is False
    assert store.meta('research_execution')==d and paper.state()==before


def test_stagnant_review_cannot_repeat_forever(tmp_path):
    store,_=setup(tmp_path);a=AgentAdvisor(store,None,tmp_path)
    state=a.state();state.update(stagnation_cycles=119,evidence_digest='same');store.meta('agent',state)
    invoke(a,tmp_path,1,'experiment_review',{});invoke(a,tmp_path,2,'experiment_review',{})
    assert invoke(a,tmp_path,3,'experiment_review',{})['result']['error_code']=='unchanged_research_read_limit'


def test_recurring_verified_bottleneck_reopens_repair_without_erasing_history(tmp_path):
    from xauusd.research_effectiveness import review
    store,_=setup(tmp_path)
    store.meta('improvements',[{'id':'observed:retrieval_overhead','state':'verified','release_id':'old','problem':'old','change':'old'}])
    store.meta('agent_calls',[{'id':str(i),'name':'evidence_read','state':'completed','finished_at':str(i),'result':{'ok':True}} for i in range(20)])
    review(store)
    row=store.meta('improvements')[0]
    assert row['state']=='planned' and row['recurrence'] is True
    assert row['previous_verified_release_id']=='old'


def test_timeout_emits_safe_elapsed_diagnostics(tmp_path):
    import sys
    import pytest
    from xauusd.lab_codex import CodexResearchClient
    client=CodexResearchClient(sys.executable)
    client.timeout=0
    client.command=lambda workspace,prompt:[sys.executable,'-c','import time;time.sleep(5)']
    events=[]
    with pytest.raises(ValueError,match='codex_timeout'):
        client._run(tmp_path,{},lambda kind,summary,detail:events.append((kind,detail)))
    diagnostic=next(d for k,d in events if k=='error')
    assert diagnostic['error_code']=='codex_timeout' and diagnostic['elapsed_seconds']>=0
    assert diagnostic['received_bytes']==0 and 'command' not in diagnostic


def test_pagination_does_not_recursively_page_other_pages(tmp_path):
    store,_=setup(tmp_path)
    class Tools:
        def execute(self,name,args):return {'ok':True,'output':'x'*19000}
    a=AgentAdvisor(store,None,tmp_path,Tools())
    original=invoke(a,tmp_path,1,'market_observe',{})
    page=invoke(a,tmp_path,2,'evidence_read',{'call_id':original['id']})
    nested=invoke(a,tmp_path,3,'evidence_read',{'call_id':page['id']})['result']
    assert nested['error_code']=='nested_evidence_page'
    assert nested['canonical_call_id']==original['id']


def test_tc02_upload_compression_and_transport_diagnostics_never_retry(tmp_path,monkeypatch):
    from xauusd.agent_tools import AgentTools
    import xauusd.agent_tools as module
    store,_=setup(tmp_path);sent=[]
    (tmp_path/'train.csv').write_bytes(b'1,2,3\n'*10000)
    def transport(argv,**kwargs):
        sent.append(argv)
        return {'returncode':255,'timed_out':True}
    monkeypatch.setattr(module,'bounded_process',transport)
    result=AgentTools(store,tmp_path).execute('tc02_run',{'command':'true','upload':['train.csv']})
    assert len(sent)==1 and 'Compression=yes' in sent[0]
    assert result['error_code']=='remote_outcome_uncertain_no_retry'
    assert result['transport']['upload_bytes']==60000 and result['transport']['timed_out']


def test_advisor_prompt_prioritizes_result_completion_over_generic_discovery(tmp_path):
    import sys
    from xauusd.lab_codex import CodexResearchClient
    client=CodexResearchClient(sys.executable)
    client._run=lambda *a:a[6]
    prompt=client.run_turn(tmp_path,{},lambda *a:None)
    assert 'ONE concrete next action' in prompt
    assert 'return research_record' in prompt
    assert 'Inspect project/ and the actual tool results' not in prompt


def test_blocked_historical_plan_cannot_preempt_current_completed_result(tmp_path):
    from xauusd.research_execution import directive
    store,_=setup(tmp_path)
    store.meta('research_plans',[{'id':'old','family':'old','state':'blocked','reason':'missing hash','variants':{'v':{'state':'completed','ok':True,'call_id':'old:c'}},'finding_ids':[]},
                                 {'id':'new','family':'new','state':'running','variants':{'v':{'state':'completed','ok':True,'call_id':'new:c'}},'finding_ids':[]}])
    assert directive(store)['target']['call_id']=='new:c'


def test_current_stage_metrics_are_in_the_actual_prompt(tmp_path):
    import sys
    from xauusd.lab_codex import CodexResearchClient
    client=CodexResearchClient(sys.executable);client._run=lambda *a:a[6]
    prompt=client.run_turn(tmp_path,{'research_execution':{'stage':'interpret_result','result':{'metrics':{'rows':1000}}}},lambda *a:None)
    assert '"rows": 1000' in prompt and '"interpret_result"' in prompt


def test_non_success_prompt_does_not_request_fabricated_finding(tmp_path):
    import sys
    from xauusd.lab_codex import CodexResearchClient
    client=CodexResearchClient(sys.executable);client._run=lambda *a:a[6]
    stage={'stage':'inspect_non_success_result','target':{'plan_id':'fixture-plan','call_id':'fixture-call'},
           'result':{'execution_status':'REPORTED_FAILURE'}}
    prompt=client.run_turn(tmp_path,{'research_execution':stage},lambda *a:None)
    assert 'For this non-success result, never call research_record' in prompt
    assert 'research_plan_close with id, state=blocked' in prompt
    assert 'fixture-plan' in prompt and 'fixture-call' in prompt
    assert 'preserve uncertainty and never replay' in prompt
