from datetime import datetime,timezone

from tests.test_lab import setup


def test_utc_daily_roll_preserves_memory_account_and_validation_budget(tmp_path):
    from xauusd.agent_daily import roll_daily_goal
    store,paper=setup(tmp_path)
    store.meta('agent',{'session_id':'ongoing','turn':10,'goal':{'achieved':True},'agenda':[{'title':'Continue evidence'}]})
    store.memory({'conclusion':'Learned method','next':'Continue'})
    store.meta('attempts',17);before=paper.state()
    first=roll_daily_goal(store,datetime(2026,10,21,23,59,tzinfo=timezone.utc))
    store.meta('agent',{**store.meta('agent'),'goal':{'achieved':True}})
    second=roll_daily_goal(store,datetime(2026,10,22,tzinfo=timezone.utc))
    assert first['day']=='2026-10-21' and second['day']=='2026-10-22'
    assert second['started_at']=='2026-10-22T00:00:00+00:00'
    assert store.meta('agent')['goal']['achieved'] is False
    assert store.meta('agent')['session_id']=='ongoing'
    assert store.memory()['conclusion']=='Learned method'
    assert store.meta('attempts')==17 and paper.state()==before
    count=len(store.events())
    roll_daily_goal(store,datetime(2026,10,22,5,tzinfo=timezone.utc))
    assert len(store.events())==count


def test_daily_snapshot_hides_yesterday_progress_and_jobs(tmp_path,monkeypatch):
    from xauusd import lab_api
    from tests.test_lab_strategy import bars
    store,paper=setup(tmp_path)
    paper.store.set_kill_switch(True,'operator')
    day=datetime.now(timezone.utc).date().isoformat()
    store.meta('agent',{'session_id':'s','started_at':'2026-01-01T00:00:00+00:00'})
    store.job({'id':'old','state':'completed','session_id':'s','started_at':'2020-01-01T12:00:00+00:00'})
    store.job({'id':'today','state':'completed','session_id':'s','started_at':day+'T01:00:00+00:00'})
    monkeypatch.setattr(lab_api,'_data',lambda:bars(500))
    result=lab_api.snapshot(store.transcript,paper)
    assert result['daily']['day']==day and result['daily']['timezone']=='UTC'
    assert [j['id'] for j in result['current_jobs']]==['today']
    assert result['performance']['daily_return_pct']==0


def test_dashboard_uses_utc_even_when_browser_timezone_is_china():
    import os,subprocess
    from xauusd.lab_dashboard import PAGE
    script=PAGE.split('<script>',1)[1].split('</script>',1)[0]
    script=script[:script.index("$('timeframes').addEventListener")]
    code=script+"\nconsole.log(stamp('2026-10-21T23:30:00Z'));"
    result=subprocess.run(['node','-e',code],env={**os.environ,'TZ':'Asia/Shanghai'},capture_output=True,text=True,timeout=10)
    assert result.returncode==0,result.stderr
    assert '21/10/2026' in result.stdout and '23:30:00 UTC' in result.stdout
