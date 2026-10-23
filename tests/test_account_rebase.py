from tests.test_lab import setup

def test_account_only_reset_preserves_research_and_stop(tmp_path):
 from xauusd.account_rebase import rebase
 store,paper=setup(tmp_path);store.memory({'conclusion':'evidence','next':'test'})
 paper.store.set_kill_switch(True,'operator')
 rebase(paper,1000)
 assert paper.state()['cash']==1000
 assert paper.state()['high_water_equity']==1000
 assert paper.state()['stopped'] is True
 assert paper.state()['kill_switch_reason']=='operator'
 assert store.memory()['conclusion']=='evidence'
