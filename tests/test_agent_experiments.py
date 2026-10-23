import pytest
from tests.test_lab import setup

def test_experimental_account_is_separate_and_bounded(tmp_path):
 from xauusd.agent_experiments import start
 store,paper=setup(tmp_path); before=paper.state().copy()
 result=start(store,{'name':'momentum','expression':'where(close>lag(close,1),1,-1)'})
 assert result['ok']
 assert store.meta('experiments')[0]['account']['state']['cash']==1000
 assert paper.state()==before
 assert start(store,{'name':'bad','expression':'__import__("os")'})['ok'] is False

def test_experimental_tick_fills_once_and_refuses_stale_quotes(tmp_path):
 from datetime import datetime,timezone
 import pandas as pd
 from xauusd.agent_experiments import start,tick
 store,paper=setup(tmp_path)
 start(store,{'name':'long','expression':'1'})
 now=datetime(2026,10,22,1,0,tzinfo=timezone.utc)
 bars=pd.DataFrame({'open':[4000.],'high':[4001.],'low':[3999.],'close':[4000.],'volume':[10.]},index=pd.to_datetime(['2026-10-22T00:59:00Z']))
 quote={'source':'ctrader_demo','symbol':'XAUUSD','bid':4000.,'ask':4000.2,'observed_at':now.isoformat(),'received_at':now.isoformat()}
 tick(store,paper.config,bars,now,{**quote,'observed_at':'2026-10-21T00:00:00Z'})
 assert store.meta('experiments')[0]['account']['state']['position']==0
 tick(store,paper.config,bars,now,quote)
 row=store.meta('experiments')[0]
 assert row['account']['state']['position']==.1
 tick(store,paper.config,bars,now,quote)
 assert len(store.meta('experiments')[0]['account']['state']['ledger'])==1
 assert paper.state()['position']==0


def test_retire_flat_frees_capacity_and_keeps_review(tmp_path):
 from xauusd.agent_experiments import start,retire,review
 store,paper=setup(tmp_path)
 ids=[start(store,{'name':str(i),'expression':'1'})['id'] for i in range(4)]
 assert not start(store,{'name':'full','expression':'1'})['ok']
 assert retire(store,{'id':ids[0],'reason':'replace sparse hypothesis'})['ok']
 assert review(store)['active']==3
 assert store.meta('experiment_archive')[0]['id']==ids[0]
 assert start(store,{'name':'replacement','expression':'-1'})['ok']
 assert paper.state()['position']==0

def test_retirement_does_not_hide_open_exposure(tmp_path):
 from xauusd.agent_experiments import start,retire
 store,_=setup(tmp_path)
 eid=start(store,{'name':'open','expression':'1'})['id']
 rows=store.meta('experiments');rows[0]['account']['state']['position']=.1;store.meta('experiments',rows)
 result=retire(store,{'id':eid,'reason':'reject'})
 assert result['state']=='retiring'
 assert len(store.meta('experiments'))==1
 assert not store.meta('experiment_archive')

def test_retiring_uses_gates_and_archives_only_after_flat(tmp_path):
 from datetime import datetime,timezone,timedelta
 import pandas as pd
 from xauusd.agent_experiments import start,tick,retire
 store,paper=setup(tmp_path)
 eid=start(store,{'name':'long','expression':'1'})['id']
 now=datetime(2026,10,22,1,0,tzinfo=timezone.utc)
 def feed(t):
  bars=pd.DataFrame({k:[4000.] for k in ('open','high','low','close','volume')},index=[pd.Timestamp(t)-pd.Timedelta(minutes=1)])
  quote={'source':'ctrader_demo','symbol':'XAUUSD','bid':4000.,'ask':4000.2,'observed_at':t.isoformat(),'received_at':t.isoformat()}
  tick(store,paper.config,bars,t,quote)
 feed(now)
 retire(store,{'id':eid,'reason':'replace'})
 rows=store.meta('experiments');rows[0]['account']['state'].update(stopped=True,kill_switch_reason='operator');store.meta('experiments',rows)
 feed(now+timedelta(minutes=1))
 assert len(store.meta('experiments'))==1
 assert store.meta('experiments')[0]['account']['state']['position']==.1
 assert not store.meta('experiment_archive')
