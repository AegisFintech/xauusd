from datetime import datetime,timezone,timedelta
import json
from tests.test_lab import setup

NOW=datetime(2026,10,24,12,tzinfo=timezone.utc)
OLD=(NOW-timedelta(days=8)).isoformat()
RECENT=(NOW-timedelta(days=1)).isoformat()


def test_seven_day_rotation_preserves_learning_active_work_and_trade_keys(tmp_path):
    from xauusd.database_retention import rotate
    store,paper=setup(tmp_path)
    store.meta('research_lessons',[{'id':'learn','last_conclusion':'Never repeat this failed hypothesis'}])
    store.meta('research_outcomes',[{'id':'finding','call_id':'protected','evidence':{'ok':True}}])
    store.meta('agent_calls',[{'id':'old','state':'completed','finished_at':OLD},
        {'id':'protected','state':'completed','finished_at':OLD},
        {'id':'uncertain','state':'unknown','started_at':OLD},
        {'id':'live','state':'running','started_at':OLD}])
    store.meta('events',{'next_id':4,'events':[{'id':1,'time':OLD},{'id':2,'time':RECENT},{'id':3,'time':'bad'}]})
    with store.state.db() as db:
        db.execute('insert into paper_trading_decisions values(?,?,?)',('monitor:old','{}',OLD))
        db.execute('insert into paper_trading_decisions values(?,?,?)',('trade:old','{}',OLD))
    before=paper.state()
    report=rotate(store.transcript,now=NOW)
    assert report['state']=='ok'
    assert [r['id'] for r in store.meta('agent_calls')]==['protected','uncertain','live']
    assert [r['id'] for r in store.meta('events')['events']]==[2,3]
    assert store.meta('events')['next_id']==4
    assert store.meta('research_lessons')[0]['id']=='learn'
    assert paper.state()==before
    with store.state.db() as db:
        assert [r['decision_id'] for r in db.execute('select decision_id from paper_trading_decisions')]==['trade:old']


def test_terminal_job_output_expires_but_identity_and_references_survive(tmp_path):
    from xauusd.database_retention import rotate
    from tests.test_bits_jobs import action
    store,_=setup(tmp_path)
    jobs=[]
    for name,status in [('old','succeeded'),('pinned','succeeded'),('unknown','unknown')]:
        row,_=store.state.claim(name,action('printf test'))
        store.state.finish({**row,'status':status,'created_at':OLD,'finished_at':OLD,'stdout':'raw output '*100})
        jobs.append(row)
    store.meta('memory',{'conclusion':'Evidence '+jobs[1]['job_id'],'next':'Keep learning'})
    rotate(store.transcript,now=NOW)
    expired=store.state.job(jobs[0]['job_id'])
    assert expired['stdout']=='' and expired['output_expired'] is True
    assert store.state.job(jobs[1]['job_id'])['stdout']
    assert store.state.job(jobs[2]['job_id'])['stdout']
    original,created=store.state.claim('old',action('printf test'))
    assert created is False and original['job_id']==jobs[0]['job_id']


def test_undated_legacy_job_gets_a_grace_period_not_an_invented_age(tmp_path):
    from xauusd.database_retention import rotate
    from tests.test_bits_jobs import action
    store,_=setup(tmp_path);row,_=store.state.claim('legacy',action('true'))
    store.state.finish({**row,'status':'succeeded','stdout':'keep until dated'})
    with store.state.db() as db:
        value=store.state.job(row['job_id'])
        for key in ('created_at','finished_at'):value.pop(key,None)
        db.execute('update bits_jobs set result_json=? where job_id=?',(json.dumps(value),row['job_id']))
    rotate(store.transcript,now=NOW)
    assert store.state.job(row['job_id'])['stdout']
    rotate(store.transcript,now=NOW+timedelta(days=8))
    assert store.state.job(row['job_id'])['output_expired']


def test_old_trade_using_monitor_prefix_and_unknown_jobs_never_expire(tmp_path):
    from xauusd.database_retention import rotate
    store,_=setup(tmp_path)
    with store.state.db() as db:
        db.execute('insert into paper_trading_decisions values(?,?,?)',('monitor:trade',json.dumps({'accepted':True,'decision_id':'monitor:trade'}),OLD))
    rotate(store.transcript,now=NOW)
    with store.state.db() as db:
        assert db.execute('select count(*) from paper_trading_decisions').fetchone()[0]==1


def test_old_run_logs_expire_but_active_runs_survive(tmp_path):
    from xauusd.database_retention import rotate
    store,_=setup(tmp_path)
    with store.state.db() as db:
        for name,status in [('past','stopped'),('active','running')]:
            db.execute('insert into agent_runs values(?,?,?,?)',(name,status,OLD,OLD if status=='stopped' else None))
            db.execute('insert into agent_transcript(run_id,tick,phase,content_json,occurred_at) values(?,?,?,?,?)',(name,1,'log','{}',OLD))
    rotate(store.transcript,now=NOW)
    with store.state.db() as db:
        assert [r['run_id'] for r in db.execute('select run_id from agent_runs')]==['active']
        assert list(db.execute('select run_id from agent_transcript'))==[]


def test_legacy_row_count_pruning_preserves_unknown_jobs(tmp_path):
    from tests.test_bits_jobs import action
    store,_=setup(tmp_path)
    job,_=store.state.claim('uncertain',action('true'));store.state.finish({**job,'status':'unknown'})
    assert store.state.prune(keep=0)==0
    assert store.state.job(job['job_id'])['status']=='unknown'


def test_offline_compaction_reclaims_pages_without_changing_account_or_learning(tmp_path,monkeypatch):
    from types import SimpleNamespace
    from xauusd.database_retention import compact_local
    store,paper=setup(tmp_path);before=paper.state()
    store.meta('research_lessons',[{'id':'keep','conclusion':'A learned result'}])
    with store.state.db() as db:
        db.execute('create table temporary_bulk (value text)')
        db.execute('insert into temporary_bulk values(?)',('x'*2_000_000,))
        db.execute('delete from temporary_bulk')
    monkeypatch.setattr('xauusd.database_retention.subprocess.run',lambda *a,**kw:SimpleNamespace(returncode=3,stdout='inactive\n'))
    report=compact_local(store.transcript)
    assert report['after_bytes']<report['before_bytes']
    assert paper.state()==before
    assert store.meta('research_lessons')[0]['id']=='keep'
    with store.state.db() as db:
        assert db.execute('pragma auto_vacuum').fetchone()[0]==2
        assert db.execute('pragma quick_check').fetchone()[0]=='ok'


def test_compaction_refuses_a_running_database_service(tmp_path,monkeypatch):
    import pytest
    from types import SimpleNamespace
    from xauusd.database_retention import compact_local
    store,_=setup(tmp_path)
    monkeypatch.setattr('xauusd.database_retention.subprocess.run',lambda *a,**kw:SimpleNamespace(returncode=0,stdout='active\n'))
    with pytest.raises(ValueError,match='stop_database_services'):
        compact_local(store.transcript)


def test_compaction_also_refuses_deactivating_or_unverified_units(tmp_path,monkeypatch):
    import pytest
    from types import SimpleNamespace
    from xauusd.database_retention import compact_local
    store,_=setup(tmp_path)
    for state in ('deactivating','unknown',''):
        monkeypatch.setattr('xauusd.database_retention.subprocess.run',lambda *a,**kw:SimpleNamespace(returncode=3,stdout=state))
        with pytest.raises(ValueError,match='stop_database_services'):
            compact_local(store.transcript)
