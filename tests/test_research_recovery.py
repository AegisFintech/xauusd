import json
from tests.test_lab import setup
from xauusd.agent_advisor import AgentAdvisor


def seed(store):
    store.meta('agent_calls',[{'id':'old:job','name':'tc02_run','state':'unknown',
        'fingerprint':'original','remote_job_id':'a'*32,'result':{'ok':False}}])


def call(advisor,root,i,name='action_reconcile',args=None):
    return advisor.execute({'id':str(i),'name':name,'arguments_json':json.dumps(args or {'call_id':'old:job'})},root)


def test_missing_checks_are_bounded_across_restart_and_direct_status(tmp_path):
    store,_=setup(tmp_path)
    class Tools:
        count=0
        def execute(self,name,args):
            self.count+=1
            return {'ok':True,'state':'not_found','job_id':'a'*32}
    tools=Tools(); advisor=AgentAdvisor(store,None,tmp_path,tools);seed(store)
    call(advisor,tmp_path,1);call(advisor,tmp_path,2)
    advisor=AgentAdvisor(store,None,tmp_path,tools)
    assert call(advisor,tmp_path,3)['result']['error_code']=='investigation_parked'
    assert call(advisor,tmp_path,4,'tc02_job_status',{'job_id':'a'*32})['result']['error_code']=='investigation_parked'
    assert tools.count==2
    original=next(r for r in store.meta('agent_calls') if r['id']=='old:job')
    assert original['state']=='unknown' and original['result']=={'ok':False}


def test_only_dependent_plan_is_parked_and_slot_is_freed(tmp_path):
    store,_=setup(tmp_path);seed(store)
    row=store.meta('agent_calls')[0];row['investigation']={'missing_checks':2};store.meta('agent_calls',[row])
    store.meta('research_plans',[{'id':'dependent','state':'running','variants':{'v':{'call_id':'old:job','state':'unknown'}},'finding_ids':[]},
                                {'id':'independent','state':'running','variants':{'v':{'call_id':'fresh','state':'running'}},'finding_ids':[]}])
    AgentAdvisor(store,None,tmp_path)
    plans=store.meta('research_plans')
    assert plans[0]['state']=='blocked' and plans[0]['variants']['v']['state']=='unknown'
    assert plans[1]['state']=='running'


def test_new_matching_evidence_resolves_parked_action_without_dispatch(tmp_path):
    store,_=setup(tmp_path);seed(store)
    rows=store.meta('agent_calls');rows[0]['investigation']={'missing_checks':2}
    rows.append({'id':'status:new','name':'tc02_job_status','state':'completed','result':{'ok':True,'state':'completed','job_id':'a'*32,'returncode':0}})
    store.meta('agent_calls',rows)
    advisor=AgentAdvisor(store,None,tmp_path)
    assert call(advisor,tmp_path,1,args={'call_id':'old:job','evidence_call_id':'invalid'})['result']['error_code']=='investigation_parked'
    assert call(advisor,tmp_path,2,args={'call_id':'old:job','evidence_call_id':'status:new'})['result']['state']=='completed'
    assert next(r for r in store.meta('agent_calls') if r['id']=='old:job')['state']=='completed'


def test_stagnant_identical_reads_are_bounded_until_evidence_changes(tmp_path):
    store,_=setup(tmp_path)
    class Tools:
        count=0
        def execute(self,name,args):self.count+=1;return {'ok':True}
    tools=Tools();advisor=AgentAdvisor(store,None,tmp_path,tools)
    state=advisor.state();state.update(stagnation_cycles=107,evidence_digest='old');store.meta('agent',state)
    call(advisor,tmp_path,1,'tc02_inspect',{'resource':1});call(advisor,tmp_path,2,'tc02_inspect',{'resource':1})
    assert call(advisor,tmp_path,3,'tc02_inspect',{'resource':1})['result']['error_code']=='unchanged_research_read_limit'
    state['evidence_digest']='new';store.meta('agent',state)
    assert call(advisor,tmp_path,4,'tc02_inspect',{'resource':1})['state']=='completed'
    assert tools.count==3


def test_parked_unknowns_do_not_consume_global_slots_or_allow_replay(tmp_path):
    store,_=setup(tmp_path)
    class Tools:
        def execute(self,name,args):return {'ok':True}
    advisor=AgentAdvisor(store,None,tmp_path,Tools())
    store.meta('agent_calls',[{'id':str(i),'name':'tc02_run','state':'unknown','fingerprint':'original',
        'investigation':{'state':'outcome_unavailable','missing_checks':2}} for i in range(20)])
    assert call(advisor,tmp_path,1,'source_register',{'domain':'example.com'})['state']=='completed'
    # Original execution fingerprint remains protected even after parking.
    payload={'name':'tc02_run','arguments':{'command':'old'}}
    import hashlib
    rows=store.meta('agent_calls');next(r for r in rows if r['state']=='unknown')['fingerprint']=hashlib.sha256(json.dumps(payload,sort_keys=True,allow_nan=False).encode()).hexdigest();store.meta('agent_calls',rows)
    result=call(advisor,tmp_path,2,'tc02_run',{'command':'old'})
    assert result['replayed'] and result['state']=='unknown'


def test_independent_experiment_finishes_with_twenty_parked_unknowns(tmp_path,monkeypatch):
    import tests.test_research_program as integration
    original=integration.setup
    def populated(path):
        store,paper=original(path)
        store.meta('agent_calls',[{'id':'old:'+str(i),'name':'tc02_run','state':'unknown','fingerprint':'old:'+str(i),
            'investigation':{'state':'outcome_unavailable','missing_checks':2}} for i in range(20)])
        return store,paper
    monkeypatch.setattr(integration,'setup',populated)
    integration.test_full_advisor_discovery_plan_compute_findings_loop_survives_cycle_boundary(tmp_path)


def test_legacy_recorded_missing_checks_are_adopted_without_query(tmp_path):
    import hashlib
    store,_=setup(tmp_path);seed(store)
    rows=store.meta('agent_calls')
    fingerprint=hashlib.sha256(json.dumps({'name':'action_reconcile','arguments':{'call_id':'old:job'}},sort_keys=True,allow_nan=False).encode()).hexdigest()
    rows.extend({'id':'lookup:'+str(i),'name':'action_reconcile','state':'completed','fingerprint':fingerprint,'result':{'state':'not_found'}} for i in range(2))
    store.meta('agent_calls',rows)
    advisor=AgentAdvisor(store,None,tmp_path)
    assert call(advisor,tmp_path,1)['result']['error_code']=='investigation_parked'
