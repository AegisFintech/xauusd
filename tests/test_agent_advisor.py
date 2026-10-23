import json
import threading

import pytest

from tests.test_lab import setup


def turn(calls=None, continuing=False):
    return {'summary':'Measured an outcome', 'assessment':'Need better source coverage',
            'agenda':[{'id':'sources','title':'Measure data coverage','status':'running'}],
            'next_action':'Inspect results', 'tool_calls':calls or [], 'continue':continuing,
            'candidates':[], 'data_requests':[], 'memory':{'conclusion':'Evidence','next':'Measure'}}


def test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    store,_=setup(tmp_path)
    class Tools:
        def catalog(self): return [{'name':'tc02_inspect'}]
        def execute(self,name,arguments): return {'ok':True,'cpus':16}
    class Client:
        def run_turn(self,workspace,brief,emit,stop):
            if not brief['tool_results']:
                return turn([{'id':'inspect1','name':'tc02_inspect','arguments_json':'{}'}],True)
            assert brief['tool_results'][0]['result']['cpus']==16
            return turn()
    advisor=AgentAdvisor(store,Client(),tmp_path,Tools())
    result=advisor.run(tmp_path/'work',{'memory':store.memory()},threading.Event())
    assert result['summary']=='Measured an outcome'
    assert store.meta('agent')['turn']==2
    assert store.meta('agent')['goal']['aspirational_daily_return_pct']==100
    assert store.meta('agent_calls')[0]['state']=='completed'


def test_unknown_side_effect_is_not_replayed_under_new_id(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    store,_=setup(tmp_path)
    class Tools:
        count=0
        def catalog(self): return [{'name':'tc02_run'}]
        def execute(self,name,arguments):
            self.count+=1
            raise RuntimeError('uncertain transport')
    tools=Tools(); advisor=AgentAdvisor(store,None,tmp_path,tools)
    first=advisor.execute({'id':'one','name':'tc02_run','arguments_json':'{"command":"work"}'},tmp_path)
    second=advisor.execute({'id':'two','name':'tc02_run','arguments_json':'{"command":"work"}'},tmp_path)
    assert tools.count==1
    assert first['state']=='unknown' and second['state']=='unknown'
    assert second['replayed'] is True


def test_advisor_contract_rejects_extra_actions_and_nonobject_arguments():
    from xauusd.agent_advisor import validate_turn
    with pytest.raises(ValueError): validate_turn({**turn(), 'disable_controls':True})
    with pytest.raises(ValueError): validate_turn(turn([{'id':'x','name':'shell','arguments_json':'[]'}]))


def test_running_calls_become_unknown_without_execution(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    store,_=setup(tmp_path);store.meta('agent_calls',[{'id':'a','state':'running','fingerprint':'abc'}])
    advisor=AgentAdvisor(store,None,tmp_path,None)
    assert store.meta('agent_calls')[0]['state']=='unknown'
    assert advisor.state()['goal']['achieved'] is False


def test_pre_job_research_failure_is_loud_and_preserves_trading_state(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    from xauusd.lab import ResearchHarness
    store,paper=setup(tmp_path);AgentAdvisor(store,None,tmp_path)
    before=paper.state()
    harness=ResearchHarness(store.transcript,paper,None,None)
    def fail():
        harness.stop.set()
        raise ValueError('frozen data changed')
    harness.research_once=fail
    harness._research_loop()
    assert store.meta('agent')['last_error']=='research_cycle_failed'
    assert store.meta('agent')['consecutive_errors']==1
    assert paper.state()==before


def test_unknown_remote_action_can_be_reconciled_without_resubmission(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    store,_=setup(tmp_path)
    class Tools:
        def execute(self,name,arguments):
            assert name=='tc02_job_status'
            assert arguments=={'job_id':'a'*32}
            return {'ok':True,'state':'completed','returncode':0}
    advisor=AgentAdvisor(store,None,tmp_path,Tools())
    store.meta('agent_calls',[{'id':'work:old','name':'tc02_run','state':'unknown','fingerprint':'old','remote_job_id':'a'*32}])
    result=advisor.execute({'id':'check','name':'action_reconcile','arguments_json':'{"call_id":"work:old"}'},tmp_path)
    assert result['result']['state']=='completed'
    original=next(r for r in store.meta('agent_calls') if r['id']=='work:old')
    assert original['state']=='completed' and original['reconciled'] is True


def test_new_session_does_not_reinstate_archived_brief_memory(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    store,_=setup(tmp_path)
    old={'conclusion':'Old preset checklist','next':'Repeat old workflow'}
    store.memory(old)
    class Client:
        def run_turn(self,workspace,brief,emit,stop):
            assert brief['memory']!=old
            assert 'New open-ended' in brief['memory']['conclusion']
            return turn()
    AgentAdvisor(store,Client(),tmp_path).run(tmp_path/'work',{'memory':old},threading.Event())
    assert store.meta('agent_prior_memory')==old


def test_final_structured_turn_is_not_repeated_as_public_commentary():
    from xauusd.lab_codex import CodexResearchClient
    client=CodexResearchClient(executable='codex');events=[]
    message=json.dumps({'item':{'type':'agent_message','text':json.dumps(turn(),sort_keys=True)}}).encode()
    client._event(message,lambda *args:events.append(args))
    assert events==[]
    client._event(json.dumps({'item':{'type':'agent_message','text':'Inspecting source quality.'}}).encode(),lambda *args:events.append(args))
    assert events[0][0]=='commentary'


def test_compact_context_preserves_account_controls_and_retrievable_evidence(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor, compact_context
    store,_=setup(tmp_path)
    advisor=AgentAdvisor(store,None,tmp_path)
    result={'ok':True,'output':'large output '*3000}
    store.meta('agent_calls',[{'id':'work:one','name':'analysis','state':'completed','result':result}])
    context={'account':{'equity':1000,'stopped':True},'risk_limits':{'daily_loss':10},
             'constraints':{'protected_holdout_unavailable':True},
             'agent':{'turn':1,'capabilities':['x'*20000],'latest_tool_results':[result]},
             'tool_results':[store.meta('agent_calls')[0]],'recent_training_bars':[{'close':2}]*120,
             'research_outcomes':[{'id':'finding','evidence':result,'call_id':'work:one'}]}
    small=compact_context(context)
    assert len(json.dumps(small))<6000
    assert small['account']==context['account'] and small['risk_limits']==context['risk_limits']
    assert small['constraints']==context['constraints']
    assert small['tool_results'][0]['evidence_ref']=='work:one'
    call={'id':'read','name':'evidence_read','arguments_json':json.dumps({'call_id':'work:one','offset':0,'limit':1000})}
    evidence=advisor.execute(call,tmp_path/'work')['result']
    assert evidence['ok'] and evidence['total_chars']>1000 and evidence['next_offset']==1000
    assert evidence['content']==json.dumps(result,allow_nan=False,sort_keys=True)[:1000]
