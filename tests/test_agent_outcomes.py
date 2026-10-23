from tests.test_lab import setup

def test_inspection_and_failed_remote_work_are_not_progress(tmp_path):
 from xauusd.agent_outcomes import progress_signature
 store,_=setup(tmp_path)
 baseline=progress_signature(store)
 store.meta('agent_calls',[{'id':'a','name':'tc02_inspect','state':'completed','result':{'ok':True}}])
 assert progress_signature(store)==baseline

def test_outcome_requires_existing_successful_evidence_and_deduplicates(tmp_path):
 from xauusd.agent_outcomes import record
 store,_=setup(tmp_path)
 args={'hypothesis':'costs erase edge','verdict':'reject','conclusion':'negative after costs','call_id':'a'}
 assert not record(store,args)['ok']
 store.meta('agent_calls',[{'id':'a','name':'tc02_run','state':'completed','result':{'ok':True,'returncode':0,'output':'measured'}}])
 assert record(store,args)['ok']
 assert record(store,args)['replayed']
 assert len(store.meta('research_outcomes'))==1

def test_improvement_cannot_claim_old_release_as_new_work(tmp_path):
 from xauusd.agent_outcomes import improvement
 store,_=setup(tmp_path)
 store.meta('engineering',{'state':'verified','release_id':'old'})
 args={'id':'fix','problem':'blocked retrieval','change':'repair cursor','acceptance':'recover original job','state':'planned'}
 assert improvement(store,args)['ok']
 assert not improvement(store,{**args,'state':'verified'})['ok']
 store.meta('engineering',{'state':'verified','release_id':'new'})
 assert improvement(store,{**args,'state':'verified'})['ok']
