from datetime import datetime,timedelta,timezone

def test_runner_costs_gaps_and_undefined_metrics():
 from xauusd.research_runner import run
 t=datetime(2026,10,20,tzinfo=timezone.utc)
 rows=[{'timestamp':(t+timedelta(minutes=i)).isoformat(),'open':4000+i,'close':4000+i} for i in range(50)]
 r=run(rows,5,3,'momentum')
 assert r['trades']>0 and r['stress_net']<r['base_net']<r['gross']
 assert len(r['thirds'])==3
 rows[20]['timestamp']=(t+timedelta(minutes=19)).isoformat()
 import pytest
 with pytest.raises(ValueError):run(rows,5,3,'momentum')
 assert run([],5,3,'momentum')['win_rate'] is None
