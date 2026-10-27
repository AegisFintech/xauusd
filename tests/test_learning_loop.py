from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import threading
import pytest
from tests.test_lab import setup
from xauusd.paper_trading import PaperDecision

NOW=datetime(2026,10,27,2,tzinfo=timezone.utc)


def test_mid_price_attribution_reconciles_gross_costs_and_net():
    from xauusd.experiment_learning import initialize,observe_fill,assessment
    state={'cash':1000.,'position':0.,'mark_price':100.,'average_entry_price':0.,'ledger':[]}
    row={};initialize(row,state,NOW)
    observe_fill(row,state,PaperDecision('open','XAUUSD','BUY',1.,100.3,NOW),{'bid':99.9,'ask':100.1},NOW)
    state.update(position=1.,average_entry_price=100.3)
    d=PaperDecision('close','XAUUSD','SELL',1.,101.7,NOW)
    quote={'bid':101.9,'ask':102.1}
    observe_fill(row,state,d,quote,NOW);observe_fill(row,state,d,quote,NOW)
    a=assessment(row,NOW)
    assert a['closed_fills']==1 and a['accepted_fills']==2
    assert a['matched_gross_mid']==pytest.approx(2.)
    assert a['matched_cost']==pytest.approx(.6)
    assert a['matched_net']==pytest.approx(1.4)
    assert a['spread_cost']+a['slippage_commission_cost']==pytest.approx(.6)
    assert a['qualification'] is False


def test_legacy_open_position_has_no_invented_entry_attribution():
    from xauusd.experiment_learning import observe_fill,assessment
    before={'cash':900.,'position':1.,'mark_price':100.,'average_entry_price':100.,'ledger':[]}
    row={};observe_fill(row,before,PaperDecision('exit','XAUUSD','SELL',1.,99.7,NOW),{'bid':99.9,'ask':100.1},NOW)
    a=assessment(row,NOW)
    assert a['unmatched_closes']==1 and a['matched_gross_mid']==0 and a['net_realized']==pytest.approx(-.3)


def test_due_review_is_evidence_linked_and_never_trades(tmp_path):
    from xauusd.agent_experiments import start
    from xauusd.experiment_learning import initialize,assessment,record_review
    store,paper=setup(tmp_path);before=deepcopy(paper.state())
    eid=start(store,{'name':'baseline','expression':'0'})['id']
    rows=store.meta('experiments');initialize(rows[0],rows[0]['account']['state'],NOW);store.meta('experiments',rows)
    due=assessment(rows[0],NOW+timedelta(days=8))
    assert due['review_due'] and not due['sample_sufficient']
    args={'id':eid,'evidence_digest':due['evidence_digest'],'decision':'continue','reason':'Need more prospective closes'}
    assert record_review(store,{**args,'evidence_digest':'wrong'},NOW)['error_code']=='stale_experiment_review'
    assert record_review(store,args,NOW+timedelta(days=8))['ok']
    row=store.meta('experiments')[0]
    assert len(row['learning']['reviews'])==1 and not assessment(row,NOW+timedelta(days=8))['review_due']
    assert paper.state()==before and row['account']==rows[0]['account']


def test_tick_collects_prospective_costs_without_mutating_main_account(tmp_path):
    import pandas as pd
    from xauusd.agent_experiments import start,tick,review
    store,paper=setup(tmp_path);before=deepcopy(paper.state());start(store,{'name':'long','expression':'1'})
    bars=pd.DataFrame({k:[100.] for k in ('open','high','low','close','volume')},index=[pd.Timestamp(NOW)-pd.Timedelta(minutes=1)])
    quote={'source':'ctrader_demo','symbol':'XAUUSD','bid':99.9,'ask':100.1,'observed_at':NOW.isoformat(),'received_at':NOW.isoformat()}
    tick(store,paper.config,bars,NOW,quote)
    a=review(store)['accounts'][0]['learning']
    assert a['accepted_fills']==1 and a['spread_cost']==pytest.approx(.01)
    assert paper.state()==before


def test_scorecard_does_not_credit_operator_or_legacy_as_autonomous(tmp_path):
    from xauusd.learning_audit import scorecard
    store,_=setup(tmp_path)
    store.meta('research_outcomes',[{'id':'old'},{'id':'manual','origin':'operator','recorded_by':'autonomous'},
        {'id':'own','origin':'autonomous','recorded_by':'autonomous','recorded_at':NOW.isoformat()}])
    d=scorecard(store)
    assert d['research']['autonomous_findings']==1 and d['research']['legacy_origin_unknown']==1
    assert d['research']['operator_findings']==1 and not d['trading']['profitability_proven']


def test_cycle_failure_is_recorded_without_exception_text(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    store,_=setup(tmp_path)
    class Client:
        def run_turn(self,*args):raise ValueError('sensitive exception text')
    a=AgentAdvisor(store,Client(),tmp_path,origin='autonomous')
    with pytest.raises(ValueError):a.run(tmp_path/'cycle',{},threading.Event())
    cycles=store.meta('learning_cycles')
    assert cycles[-1]['state']=='failed' and cycles[-1]['origin']=='autonomous'
    assert 'sensitive exception text' not in json.dumps(cycles)


def test_completed_result_origin_is_preserved_in_finding(tmp_path):
    from xauusd.agent_outcomes import record
    store,_=setup(tmp_path)
    store.meta('agent_calls',[{'id':'source','name':'analysis','state':'completed','origin':'operator','cycle_id':'old','result':{'ok':True,'output':'measured fixture'}}])
    result=record(store,{'hypothesis':'fixture','verdict':'reject','conclusion':'fixture','call_id':'source'},recorded_by={'origin':'autonomous','cycle_id':'new'})
    assert result['ok']
    finding=store.meta('research_outcomes')[0]
    assert finding['origin']=='operator' and finding['recorded_by']=='autonomous' and finding['recorded_cycle_id']=='new'


def test_paired_runner_rejects_multiple_changes_and_preserves_same_data():
    from xauusd.research_runner import compare
    rows=[{'timestamp':(NOW+timedelta(minutes=i)).isoformat(),'open':100.+i,'close':100.+i+.2} for i in range(80)]
    config={'baseline':{'lookback':3,'hold':4,'mode':'momentum'},'challenger':{'lookback':3,'hold':4,'mode':'reversal'},'reason':'Fixed directional inversion diagnostic, not strategy tuning'}
    before=deepcopy(rows);r=compare(rows,config)
    assert rows==before and r['promotion_allowed'] is False and r['changed_fields']==['mode']
    b,c=r['reports']['baseline'],r['reports']['challenger']
    assert b['trades']==c['trades'] and b['gross']==pytest.approx(-c['gross'])
    assert r['delta']['stress_net']==pytest.approx(c['stress_net']-b['stress_net'])
    assert b['costs_per_roundtrip']==c['costs_per_roundtrip']
    config['challenger']['hold']=5
    with pytest.raises(ValueError,match='one_preregistered_change'):compare(rows,config)


def test_due_paper_review_has_a_real_scheduler_stage(tmp_path):
    from xauusd.agent_experiments import start
    from xauusd.experiment_learning import initialize
    from xauusd.research_execution import directive
    store,_=setup(tmp_path);start(store,{'name':'old','expression':'0'})
    rows=store.meta('experiments');initialize(rows[0],rows[0]['account']['state'],NOW-timedelta(days=30));store.meta('experiments',rows)
    d=directive(store)
    assert d['stage']=='review_paper_experiment' and d['target']['id']==rows[0]['id']


def test_unattended_compute_finding_and_closure_survive_advisor_restart(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    from xauusd.learning_audit import scorecard
    from tests.test_agent_advisor import turn
    from tests.test_research_program import plan
    store,_=setup(tmp_path)
    class Tools:
        def catalog(self):return []
        def execute(self,name,args):
            assert name=='analysis'
            return {'ok':True,'output':'{"net_profit":-1}','returncode':0}
    class Client:
        step=0
        def run_turn(self,workspace,context,emit,stop):
            n=self.step;self.step+=1
            def call(name,args):return {'id':f'step-{n}','name':name,'arguments_json':json.dumps(args)}
            if n==0:return turn([call('research_plan',plan())],True)
            pid=store.meta('research_plans')[0]['id']
            if n==1:return turn([call('analysis',{'command':'fixture diagnostic','plan_id':pid,'variant_id':'v1'})],True)
            if n==2:
                source=next(r for r in store.meta('agent_calls') if r['name']=='analysis')
                return turn([call('research_record',{'hypothesis':'fixture','verdict':'reject','conclusion':'Fixture loss after costs',
                    'call_id':source['id'],'experiment':{'family':'rate_news','dataset_version':'v1','code_sha256':'a'*64,
                    'parameters':{},'costs':{'spread':.3},'metrics':{'net_profit':-1},'failure_reason':'costs','parent_id':None}})],True)
            return turn([call('research_plan_close',{'id':pid,'state':'completed','reason':'Fixture evidence recorded'})])
    client=Client()
    AgentAdvisor(store,client,tmp_path,Tools(),max_turns=2,origin='autonomous').run(tmp_path/'one',{},threading.Event())
    AgentAdvisor(store,client,tmp_path,Tools(),max_turns=2,origin='autonomous').run(tmp_path/'two',{},threading.Event())
    d=scorecard(store)
    assert d['research']['autonomous_findings']==1
    assert d['research']['autonomous_cycles']==2 and d['research']['autonomous_cycles_with_findings']==1
    assert store.meta('research_plans')[0]['state']=='completed'
