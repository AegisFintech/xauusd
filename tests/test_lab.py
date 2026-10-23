import json
from datetime import datetime, timezone, timedelta

import pytest

from xauusd.local_state import SQLiteAgentTranscriptStore, SQLitePaperTradingStore
from xauusd.paper_trading import PaperTrading, PaperRiskConfig


def setup(tmp_path):
    from xauusd.lab_store import LabStore
    transcript=SQLiteAgentTranscriptStore(str(tmp_path/'state.db'))
    return LabStore(transcript), PaperTrading(SQLitePaperTradingStore(str(tmp_path/'state.db')),PaperRiskConfig())


def test_durable_job_recovery_never_replays(tmp_path):
    store,paper=setup(tmp_path)
    store.job({'id':'job1','state':'running','started_at':'2026-01-01T00:00:00+00:00'})
    assert store.recover_jobs()==1
    assert store.jobs()[0]['state']=='interrupted'
    assert store.recover_jobs()==0


def test_event_and_memory_storage_is_bounded(tmp_path):
    store,paper=setup(tmp_path)
    for i in range(510): store.event('research','Inspecting evidence',{'number':i})
    assert len(store.events(0,1000))<=300
    assert store.events(0,10)[-1]['id'] < store.events(0,1000)[-1]['id']
    store.memory({'conclusion':'x'*10000,'next':'y'*10000})
    assert len(json.dumps(store.memory()))<9000


def test_promotion_refuses_claimed_success_without_forward_evidence(tmp_path):
    from xauusd.lab import promote
    store,paper=setup(tmp_path)
    candidate={'id':'fake','name':'fake','expression':'1','state':'probation','report':{'passed':True}}
    store.candidate(candidate)
    assert promote(store,candidate,paper)['promoted'] is False
    assert store.active() is None
    assert paper.state()['stopped'] is True


def test_paper_execution_revalidates_evidence_and_never_clears_stop(tmp_path):
    from xauusd.lab import paper_tick
    from tests.test_lab_strategy import bars
    store,paper=setup(tmp_path)
    store.meta('active','fake')
    store.candidate({'id':'fake','expression':'1','state':'active','report':{'passed':True}})
    frame=bars(500); now=frame.index[-1].to_pydatetime()+timedelta(minutes=1)
    result=paper_tick(store,paper,frame,now)
    assert result['state'] in ('invalid_evidence','paper_stopped')
    assert paper.state()['position']==0 and paper.state()['stopped'] is True


def test_codex_contract_rejects_unknown_fields_and_overlarge_requests():
    from xauusd.lab_codex import validate_proposal
    with pytest.raises(ValueError): validate_proposal({'summary':'x','candidates':[],'disable_risk':True})
    with pytest.raises(ValueError): validate_proposal({'summary':'x'*10000,'candidates':[],'data_requests':[],'memory':{'conclusion':'x','next':'x'}})


def test_codex_environment_does_not_inherit_broker_credentials(tmp_path,monkeypatch):
    from xauusd.lab_codex import child_environment
    monkeypatch.setenv('CTRADER_ACCESS_TOKEN','secret-value')
    monkeypatch.setenv('DD_API_KEY','secret-value')
    env=child_environment(tmp_path)
    assert 'CTRADER_ACCESS_TOKEN' not in env and 'DD_API_KEY' not in env
    assert env['PATH'] and env['CODEX_HOME']


def qualified_candidate(now, expression='1'):
    from dataclasses import asdict
    from xauusd.lab_strategy import identity, execution_config, evidence_digest
    gates={k:True for k in ('minimum_trades','positive_expectancy','net_profit','profit_factor','drawdown','bootstrap_positive')}
    metrics={'trades':100,'net_profit':50.,'expectancy':.5,'profit_factor':2.,'max_drawdown':-.01}
    execution=asdict(execution_config(.1))
    row={'expression':expression,'name':'test','id':identity({'expression':expression}),
         'state':'qualified','dataset_version':'v1','created_at':(now-timedelta(days=8)).isoformat(),
         'forward_end':(now-timedelta(days=1)).isoformat(),
         'execution':execution,
         'report':{'candidate_id':identity({'expression':expression}),'dataset_version':'v1',
                   'passed':True,'positive_fold_fraction':1.,'gates':{**gates,'positive_folds':True},'metrics':metrics,
                   'bootstrap':{'p05_net_pnl':1.},'execution':execution,'holdout_consumed':False},
         'forward':{'passed':True,'gates':{**gates,'flat_at_end':True,'shadow_not_stopped':True,'observation_coverage':True},
                    'metrics':metrics,'bootstrap':{'p05_net_pnl':1.},'execution':execution,
                    'prospective':True,'quote_based':True,'days':7,
                    'coverage':{'expected_minutes':6000,'observed_minutes':6000,'fraction':1.,'passed':True,
                                'first_boundary_covered':True,'last_boundary_covered':True,'exposed_gap':False},
                    'start':(now-timedelta(days=8)+timedelta(minutes=1)).isoformat(),'end':(now-timedelta(days=1)).isoformat()}}
    from xauusd.lab import _expected_forward_minutes
    minutes=_expected_forward_minutes(row['created_at'],row['forward_end'])
    row['forward']['coverage'].update(expected_minutes=len(minutes),observed_minutes=len(minutes),
                                      first_observed_at=minutes[0].isoformat(),last_observed_at=minutes[-1].isoformat())
    row['forward']['start']=minutes[0].isoformat()
    row['evidence_digest']=evidence_digest(row)
    return row


def quote(now,bid=100.,ask=100.3):
    return {'bid':bid,'ask':ask,'symbol':'XAUUSD','source':'ctrader_demo',
            'observed_at':now.isoformat(),'received_at':now.isoformat()}


def test_qualified_promotion_and_trade_uses_real_side_price_costs_and_idempotency(tmp_path):
    from xauusd.lab import promote,paper_tick
    from tests.test_lab_strategy import bars
    store,paper=setup(tmp_path);paper.start('test')
    frame=bars(500);now=frame.index[-1].to_pydatetime()+timedelta(minutes=1)
    row=qualified_candidate(now);store.candidate(row)
    assert promote(store,row,paper)['promoted'] is True
    assert paper_tick(store,paper,frame,now,quote=quote(now))['filled'] is True
    assert paper.state()['average_entry_price']==pytest.approx(100.385)
    assert paper.state()['position']==pytest.approx(.1)
    assert paper_tick(store,paper,frame,now,quote=quote(now))['state']=='duplicate_bar'
    assert len(paper.state()['ledger'])==1


def test_modified_program_and_stale_quotes_cannot_trade(tmp_path):
    from xauusd.lab import promote,paper_tick
    from tests.test_lab_strategy import bars
    store,paper=setup(tmp_path);paper.start('test')
    frame=bars(500);now=frame.index[-1].to_pydatetime()+timedelta(minutes=1)
    row=qualified_candidate(now);store.candidate(row);promote(store,row,paper)
    old=quote(now-timedelta(seconds=20))
    assert paper_tick(store,paper,frame,now,quote=old)['state']=='quote_unavailable'
    row['expression']='-1';row['state']='active';store.candidate(row)
    assert paper_tick(store,paper,frame,now,quote=quote(now))['state']=='invalid_evidence'
    assert not paper.state()['ledger']


def test_forward_window_is_scored_once_then_rejected(tmp_path,monkeypatch):
    from xauusd.lab import ResearchHarness
    import xauusd.lab as lab
    store,paper=setup(tmp_path)
    now=datetime(2026,1,10,tzinfo=timezone.utc)
    row=qualified_candidate(now);row.update(state='probation',forward_end=(now-timedelta(days=1)).isoformat())
    row.pop('forward');store.candidate(row)
    harness=ResearchHarness(store.transcript,paper,None,None,now_provider=lambda:now)
    actual=lab.gates_for;calls=[]
    def count(*args,**kwargs): calls.append(1);return actual(*args,**kwargs)
    monkeypatch.setattr(lab,'gates_for',count)
    harness.probation(None);harness.probation(None)
    assert calls==[1]
    assert store.candidates()[0]['state']=='rejected_forward'


def test_shadow_and_paper_share_target_prices_and_flatten_reversals():
    from xauusd.lab_execution import ShadowStore,target_decision
    from tests.test_lab_strategy import bars
    frame=bars(500);now=frame.index[-1].to_pydatetime()+timedelta(minutes=1)
    account=PaperTrading(ShadowStore(),PaperRiskConfig())
    row={'id':'s','expression':'1'}
    enter=target_decision(row,frame,account.state(),now,quote(now),.1)
    assert enter.price==pytest.approx(100.385)
    account.evaluate(enter,now)
    row['expression']='-1'
    exit=target_decision(row,frame,account.state(),now,quote(now),.1)
    assert exit.side=='SELL' and exit.quantity==pytest.approx(.1)
    assert exit.price==pytest.approx(99.915)


def test_read_only_lab_api_reports_actual_data_and_events(tmp_path,monkeypatch):
    from xauusd import lab_api
    from tests.test_lab_strategy import bars
    store,paper=setup(tmp_path);store.event('research','Known activity',{'value':5})
    monkeypatch.setattr(lab_api,'_data',lambda:bars(500))
    result=lab_api.snapshot(store.transcript,paper)
    assert result['data']['rows']==500 and result['limits']['paper_only'] is True
    assert result['activity'][0]['summary']=='Known activity'
    assert lab_api.events(store.transcript,0,10)['events'][0]['detail']=={'value':5}


def test_permission_profile_restricts_tools_to_training_workspace(tmp_path):
    from xauusd.lab_codex import permission_arguments
    args=' '.join(permission_arguments(tmp_path))
    assert 'default_permissions="lab"' in args
    assert '":root"="deny"' in args and str(tmp_path) in args
    assert 'features.network_proxy=true' in args and 'web_search="disabled"' in args


@pytest.mark.parametrize('change',[{'positive_fold_fraction':None},{'positive_fold_fraction':.1},{'dataset_version':'other'}])
def test_evidence_relations_are_checked_beyond_digest(tmp_path,change):
    from xauusd.lab import _qualified
    from xauusd.lab_strategy import evidence_digest
    now=datetime(2026,1,10,tzinfo=timezone.utc)
    row=qualified_candidate(now);row['report'].update(change)
    row['evidence_digest']=evidence_digest(row)
    assert _qualified(row) is False


def test_shadow_risk_monitor_sees_intraminute_loss_and_keeps_stop(tmp_path):
    from xauusd.lab import ResearchHarness
    from tests.test_lab_strategy import bars
    store,_=setup(tmp_path)
    paper=PaperTrading(SQLitePaperTradingStore(str(tmp_path/'state.db')),PaperRiskConfig(daily_loss_limit=1.))
    frame=bars(500);now=frame.index[-1].to_pydatetime()+timedelta(minutes=1)
    row=qualified_candidate(now);row.update(state='probation',created_at=(now-timedelta(days=1)).isoformat(),forward_end=(now+timedelta(days=6)).isoformat())
    store.candidate(row)
    harness=ResearchHarness(store.transcript,paper,None,None)
    harness.shadow_tick(frame,now,quote(now))
    harness.shadow_tick(frame,now+timedelta(seconds=5),quote(now+timedelta(seconds=5),80.,80.3))
    harness.shadow_tick(frame,now+timedelta(seconds=10),quote(now+timedelta(seconds=10)))
    shadow=store.meta('shadow:'+row['id'])
    assert shadow['account']['state']['stopped'] is True
    assert shadow['account']['state']['kill_switch_reason']=='risk_limit'


def test_promotion_waits_for_inflight_paper_fill(tmp_path,monkeypatch):
    import threading
    from xauusd.lab import promote,paper_tick
    from tests.test_lab_strategy import bars
    store,paper=setup(tmp_path);paper.start('test')
    frame=bars(500);now=frame.index[-1].to_pydatetime()+timedelta(minutes=1)
    old=qualified_candidate(now);store.candidate(old);promote(store,old,paper)
    new=qualified_candidate(now,'-1');store.candidate(new)
    entered=threading.Event();release=threading.Event();done=threading.Event();result={}
    actual=paper.evaluate
    def delayed(*args,**kwargs): entered.set();assert release.wait(3);return actual(*args,**kwargs)
    monkeypatch.setattr(paper,'evaluate',delayed)
    first=threading.Thread(target=lambda:paper_tick(store,paper,frame,now,quote=quote(now)))
    def promotion():result.update(promote(store,new,paper));done.set()
    second=threading.Thread(target=promotion)
    first.start();assert entered.wait(3);second.start()
    try: assert not done.wait(.05)
    finally: release.set();first.join(3);second.join(3)
    assert result['promoted'] is False
    assert store.active()['id']==old['id']


def test_dataset_advances_only_to_a_wholly_new_cohort(tmp_path):
    from types import SimpleNamespace
    import io
    import pandas as pd
    from tests.test_lab_strategy import bars
    from xauusd.atomic import atomic_write_bytes
    from xauusd.lab import ResearchHarness
    from xauusd.lab_strategy import freeze_dataset
    store,paper=setup(tmp_path)
    original=bars(1000);manifest=freeze_dataset(original)
    fresh=bars(101000).iloc[1000:]
    root=tmp_path/'lab';root.mkdir()
    buf=io.BytesIO();original.to_parquet(buf);atomic_write_bytes(root/'dataset.parquet',buf.getvalue())
    store.meta('dataset',manifest);store.meta('attempts',20)
    class Client:
        executable='codex'
        def run(self,workspace,brief,emit,stop):
            self.brief=brief
            return {'summary':'Continuing independent research.','candidates':[],'data_requests':[],
                    'memory':{'conclusion':'New cohort','next':'Test causal hypotheses'}}
    client=Client();now=fresh.index[-1].to_pydatetime()+timedelta(minutes=1)
    harness=ResearchHarness(store.transcript,paper,SimpleNamespace(read=lambda:pd.concat([original,fresh])),client,
                            root=root,now_provider=lambda:now)
    assert harness.research_once()['state']=='completed'
    new=store.meta('dataset')
    assert pd.Timestamp(new['start'])>pd.Timestamp(manifest['end'])
    assert store.meta('attempts')==0
    assert new['version']!=manifest['version'] and new['holdout_consumed'] is False
    assert client.brief['constraints']['attempts_remaining']==20


def test_monitor_history_pruning_preserves_trade_idempotency_and_paper_state(tmp_path):
    store,paper=setup(tmp_path)
    before=paper.state()
    now=datetime(2026,1,10,tzinfo=timezone.utc)
    with store.state.db() as db:
        for key,created in [('monitor:old','2020-01-01T00:00:00+00:00'),('lab:trade-old','2020-01-01T00:00:00+00:00'),('monitor:new',now.isoformat())]:
            db.execute('INSERT INTO paper_trading_decisions VALUES(?,?,?)',(key,'{}',created))
    assert store.prune_monitor_history(now)==1
    with store.state.db() as db:
        ids={r['decision_id'] for r in db.execute('SELECT decision_id FROM paper_trading_decisions').fetchall()}
    assert ids=={'lab:trade-old','monitor:new'}
    assert paper.state()==before


def test_forward_coverage_rejects_short_observation_despite_fixed_deadline():
    from xauusd.lab import forward_coverage
    end=datetime(2026,1,9,20,tzinfo=timezone.utc);start=end-timedelta(days=7)
    marks=[{'time':(end-timedelta(minutes=i)).isoformat(),'equity':100000.} for i in range(1,11)]
    coverage=forward_coverage(start.isoformat(),end.isoformat(),{'equity':marks})
    assert coverage['passed'] is False
    assert coverage['fraction'] < .01


def test_forward_coverage_uses_new_york_market_minutes_and_accepts_complete_week():
    import pandas as pd
    from xauusd.lab import forward_coverage
    from xauusd.paper_trading import market_is_open
    start=datetime(2026,1,2,20,tzinfo=timezone.utc);end=start+timedelta(days=7)
    expected=[t for t in pd.date_range(start+timedelta(minutes=2),end,inclusive='left',freq='min') if market_is_open(t.to_pydatetime())]
    marks=[{'time':t.isoformat(),'equity':100000.} for t in expected]
    coverage=forward_coverage(start.isoformat(),end.isoformat(),{'equity':marks})
    assert coverage['passed'] is True and coverage['fraction']==1
    assert coverage['expected_minutes']==len(expected)<7*1440
    assert forward_coverage(start.isoformat(),end.isoformat(),{'equity':marks,'exposed_observation_gap':True})['passed'] is False


def test_shadow_exposed_open_market_gap_invalidates_forward_evidence(tmp_path):
    import pandas as pd
    from xauusd.lab import ResearchHarness
    from tests.test_lab_strategy import bars
    store,paper=setup(tmp_path);frame=bars(500)
    now=frame.index[-1].to_pydatetime()+timedelta(minutes=1)
    row=qualified_candidate(now);row.update(state='probation',created_at=(now-timedelta(days=1)).isoformat(),forward_end=(now+timedelta(days=6)).isoformat())
    store.candidate(row);harness=ResearchHarness(store.transcript,paper,None,None)
    harness.shadow_tick(frame,now,quote(now))
    later=now+timedelta(minutes=4)
    tail=frame.tail(4).copy();tail.index=pd.date_range(frame.index[-1]+timedelta(minutes=1),periods=4,freq='min')
    harness.shadow_tick(pd.concat([frame,tail]),later,quote(later))
    assert store.meta('shadow:'+row['id'])['exposed_observation_gap'] is True


def test_probation_after_outage_rejects_profitable_but_stale_observations(tmp_path):
    from xauusd.lab import ResearchHarness
    from xauusd.lab_execution import ShadowStore
    store,paper=setup(tmp_path);now=datetime(2026,1,10,tzinfo=timezone.utc)
    row=qualified_candidate(now);row['state']='probation';row.pop('forward');store.candidate(row)
    created=datetime.fromisoformat(row['created_at'])
    marks=[{'time':(created+timedelta(minutes=i)).isoformat(),'equity':100050.} for i in range(2,12)]
    store.meta('shadow:'+row['id'],{'start':marks[0]['time'],'equity':marks,'closed_pnl':[1.,-.1]*50,
                                    'maximum_drawdown':-.001,'account':ShadowStore().payload})
    harness=ResearchHarness(store.transcript,paper,None,None,now_provider=lambda:now)
    harness.probation(None)
    result=store.candidates()[0]
    assert result['state']=='rejected_forward'
    assert result['forward']['gates']['minimum_trades'] is True
    assert result['forward']['gates']['observation_coverage'] is False


def test_qualification_requires_coverage_even_with_recomputed_digest():
    from xauusd.lab import _qualified
    from xauusd.lab_strategy import evidence_digest
    row=qualified_candidate(datetime(2026,1,10,tzinfo=timezone.utc))
    row['forward'].pop('coverage');row['evidence_digest']=evidence_digest(row)
    assert _qualified(row) is False


def test_shadow_weekend_closure_is_not_an_exposed_observation_gap(tmp_path):
    import pandas as pd
    from xauusd.lab import ResearchHarness
    from tests.test_lab_strategy import bars
    store,paper=setup(tmp_path);frame=bars(500)
    friday=datetime(2026,1,9,21,59,tzinfo=timezone.utc)
    frame.index=pd.date_range(end=friday-timedelta(minutes=1),periods=len(frame),freq='min')
    row=qualified_candidate(friday);row.update(state='probation',created_at=(friday-timedelta(days=1)).isoformat(),forward_end=(friday+timedelta(days=6)).isoformat())
    store.candidate(row);harness=ResearchHarness(store.transcript,paper,None,None)
    harness.shadow_tick(frame,friday,quote(friday))
    sunday=datetime(2026,1,11,23,1,tzinfo=timezone.utc)
    latest=frame.tail(1).copy();latest.index=pd.DatetimeIndex([sunday-timedelta(minutes=1)])
    harness.shadow_tick(pd.concat([frame,latest]),sunday,quote(sunday))
    assert store.meta('shadow:'+row['id']).get('exposed_observation_gap',False) is False


def test_qualification_checks_observed_boundaries_and_expected_count():
    from xauusd.lab import _qualified
    from xauusd.lab_strategy import evidence_digest
    now=datetime(2026,1,10,tzinfo=timezone.utc)
    row=qualified_candidate(now)
    row['forward']['start']=(datetime.fromisoformat(row['forward_end'])-timedelta(minutes=10)).isoformat()
    row['evidence_digest']=evidence_digest(row)
    assert _qualified(row) is False
    row=qualified_candidate(now)
    row['forward']['coverage'].update(expected_minutes=1,observed_minutes=1)
    row['evidence_digest']=evidence_digest(row)
    assert _qualified(row) is False
