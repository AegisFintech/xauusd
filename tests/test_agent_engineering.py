from pathlib import Path
import pytest
from xauusd.atomic import atomic_write_text
from xauusd.agent_engineering import EngineeringManager

class Store:
    def __init__(self): self.values={}; self.events=[]
    def meta(self,key,value=...):
        if value is ...: return self.values.get(key)
        self.values[key]=value; return value
    def event(self,*args): self.events.append(args)

@pytest.fixture
def setup(tmp_path):
    root=tmp_path/'repo'; root.mkdir()
    for name,text in {'AGENTS.md':'rules','pyproject.toml':'[project]\nname="example"\nversion="0.0.1"\n','xauusd/__init__.py':'','xauusd/lab_dashboard.py':'PAGE="old"\n','xauusd/paper_trading.py':'PROTECTED=True\n','tests/test_original.py':'def test_original(): assert True\n'}.items():
        atomic_write_text(root/name,text)
    manager=EngineeringManager(root,Store()); work=tmp_path/'work'; work.mkdir()
    manager.snapshot(work)
    return manager,root,work

def test_snapshot_never_copies_secrets_state_or_links(tmp_path):
    root=tmp_path/'root'; root.mkdir(); atomic_write_text(root/'.env','DO_NOT_COPY=1')
    atomic_write_text(root/'data/state','private'); atomic_write_text(root/'xauusd/app.py','ok=1')
    (root/'xauusd/leak.py').symlink_to(root/'.env')
    manager=EngineeringManager(root,Store()); result=manager.snapshot(tmp_path/'work')
    assert not result['ok']; assert result['error_code']=='unsafe_path'
    assert not (tmp_path/'work/project/.env').exists()

@pytest.mark.parametrize('name',['AGENTS.md','xauusd/paper_trading.py','tests/test_original.py','pyproject.toml'])
def test_protected_changes_refused(setup,name):
    manager,root,work=setup; atomic_write_text(work/'project'/name,'changed')
    assert manager.check(work)['error_code']=='protected_change'

def test_new_tests_and_application_changes_allowed(setup):
    manager,root,work=setup; atomic_write_text(work/'project/xauusd/lab_dashboard.py','PAGE="new"\n')
    atomic_write_text(work/'project/tests/test_added.py','def test_added(): assert True\n')
    result=manager.check(work); assert result['ok']; assert len(result['changes'])==2

def test_stale_live_change_rejected(setup):
    manager,root,work=setup; atomic_write_text(root/'xauusd/lab_dashboard.py','PAGE="outside"\n')
    assert manager.check(work)['error_code']=='live_base_changed'

def test_failed_tests_never_install(setup,monkeypatch):
    manager,root,work=setup; atomic_write_text(work/'project/xauusd/lab_dashboard.py','PAGE="new"\n')
    monkeypatch.setattr(manager,'_test',lambda project: {'ok':False,'error_code':'tests_failed'})
    assert manager.deploy(work)['error_code']=='tests_failed'
    assert (root/'xauusd/lab_dashboard.py').read_text()=='PAGE="old"\n'

def test_pending_release_rollback_and_verification(setup,monkeypatch):
    manager,root,work=setup; atomic_write_text(work/'project/xauusd/lab_dashboard.py','PAGE="new"\n')
    monkeypatch.setattr(manager,'_test',lambda project: {'ok':True,'exit_code':0})
    result=manager.deploy(work); assert result['ok'] and result['restart_required']
    assert manager.store.meta('engineering_pending')['id']==result['release_id']
    assert manager.verify_pending(healthy=False)['state']=='rolled_back'
    assert (root/'xauusd/lab_dashboard.py').read_text()=='PAGE="old"\n'
    assert manager.store.meta('engineering_pending') is None

def test_success_keeps_new_release(setup,monkeypatch):
    manager,root,work=setup; atomic_write_text(work/'project/xauusd/lab_dashboard.py','PAGE="new"\n')
    monkeypatch.setattr(manager,'_test',lambda project: {'ok':True})
    assert manager.deploy(work)['ok']
    assert manager.verify_pending(healthy=True)['state']=='verified'
    assert (root/'xauusd/lab_dashboard.py').read_text()=='PAGE="new"\n'

def test_test_mutation_rejected(setup,monkeypatch):
    manager,root,work=setup; atomic_write_text(work/'project/xauusd/lab_dashboard.py','PAGE="new"\n')
    def mutate(project):
        atomic_write_text(project/'xauusd/lab_dashboard.py','PAGE="untested"\n'); return {'ok':True}
    monkeypatch.setattr(manager,'_test',mutate)
    assert manager.deploy(work)['error_code']=='sources_changed_during_tests'

def test_rollback_does_not_clobber_intervening_operator_edit(setup,monkeypatch):
    manager,root,work=setup; atomic_write_text(work/'project/xauusd/lab_dashboard.py','PAGE="new"\n')
    monkeypatch.setattr(manager,'_test',lambda project: {'ok':True}); manager.deploy(work)
    atomic_write_text(root/'xauusd/lab_dashboard.py','PAGE="operator"\n')
    result=manager.verify_pending(healthy=False)
    assert result['error_code']=='rollback_conflict'
    assert (root/'xauusd/lab_dashboard.py').read_text()=='PAGE="operator"\n'

def test_added_conftest_cannot_skip_original_tests(setup):
    manager,root,work=setup
    atomic_write_text(work/'project/tests/conftest.py','def pytest_collection_modifyitems(items): items.clear()\n')
    assert manager.check(work)['error_code']=='protected_change'

def test_changed_files_rechecked_before_health_success(setup,monkeypatch):
    manager,root,work=setup; atomic_write_text(work/'project/xauusd/lab_dashboard.py','PAGE="new"\n')
    monkeypatch.setattr(manager,'_test',lambda project:{'ok':True}); manager.deploy(work)
    atomic_write_text(root/'xauusd/lab_dashboard.py','PAGE="outside"\n')
    assert manager.verify_pending(healthy=True)['error_code']=='rollback_conflict'

def test_interrupted_partial_install_rolls_back(setup,monkeypatch):
    manager,root,work=setup; atomic_write_text(work/'project/xauusd/lab_dashboard.py','PAGE="new"\n')
    monkeypatch.setattr(manager,'_test',lambda project:{'ok':True}); manager.deploy(work)
    pending=manager.store.meta('engineering_pending'); pending['state']='installing'
    manager.store.meta('engineering_pending',pending)
    assert manager.recover_pending()['state']=='rolled_back'
    assert (root/'xauusd/lab_dashboard.py').read_text()=='PAGE="old"\n'

def test_dependencies_may_change_but_build_configuration_cannot(setup):
    manager,root,work=setup
    content=(work/'project/pyproject.toml').read_text()
    atomic_write_text(work/'project/pyproject.toml', content+'dependencies=["numpy>=1.26"]\n')
    assert manager.check(work)['error_code']=='dependency_environment_unavailable'
    atomic_write_text(work/'project/pyproject.toml', content+'[build-system]\nrequires=["evil"]\n')
    assert manager.check(work)['error_code']=='protected_change'

def test_sandbox_tests_return_bounded_feedback_and_clean_environment(setup,monkeypatch):
    import xauusd.agent_engineering as module
    manager,root,work=setup; seen={}
    class Process:
        pid=99999999; returncode=1
        def __init__(self,command,**kwargs):
            seen.update(command=command,kwargs=kwargs)
            kwargs['stdout'].write(b'AssertionError: expected two observations\n')
        def poll(self): return 1
        def wait(self): return 1
    monkeypatch.setattr(module.subprocess,'Popen',Process)
    monkeypatch.setenv('CTRADER_ACCESS_TOKEN','sensitive-value-never-forward')
    result=manager._test(work/'project')
    assert not result['ok'] and 'expected two observations' in result['output']
    assert seen['kwargs']['env']['AGENT_PLANNER']=='openai'
    assert 'CTRADER_ACCESS_TOKEN' not in seen['kwargs']['env']
    assert seen['command'][0]=='bwrap'
    assert '--unshare-all' in seen['command']
    assert '--share-net' not in seen['command']

@pytest.mark.parametrize('early_exit',[False,True])
def test_real_pytest_requires_trusted_completion(setup,early_exit,monkeypatch):
    import shutil
    import sys
    import subprocess
    import xauusd.agent_engineering as module
    original_popen = subprocess.Popen
    # Exercise the real completion wrapper and actual os._exit in a Python
    # child. Transport isolation is independently checked above and by the full
    # suite running inside bwrap; nesting private proc mounts is unsupported.
    def python_transport(command, **kwargs):
        return original_popen(command[command.index('--') + 1:], **kwargs)
    monkeypatch.setattr(module.subprocess, 'Popen', python_transport)
    manager,root,work=setup
    (root/'.venv').symlink_to(Path(sys.prefix),target_is_directory=True)
    if early_exit:
        atomic_write_text(work/'project/tests/test_added.py','import os\nos._exit(0)\n')
    result=manager._test(work/'project')
    assert result['ok'] is not early_exit, result
    if early_exit: assert result['error_code']=='tests_completion_missing'

def test_gate_dependency_closure_is_immutable(setup):
    manager,root,work=setup
    atomic_write_text(root/'xauusd/paper_trading.py','from .account_codec import load_state\n')
    atomic_write_text(root/'xauusd/account_codec.py','def load_state(): return {}\n')
    manager=EngineeringManager(root,Store()); second=work.parent/'second'
    assert manager.snapshot(second)['ok']
    atomic_write_text(second/'project/xauusd/account_codec.py','def load_state(): return {"stopped":False}\n')
    assert manager.check(second)['error_code']=='protected_change'

def test_invalid_added_test_returns_repairable_feedback(setup):
    manager,root,work=setup
    atomic_write_text(work/'project/tests/test_added.py','def broken(\n')
    result=manager._test(work/'project')
    assert result['error_code']=='tests_collection_invalid'

def test_snapshot_expiry_deletes_backend_rows(setup):
    import sqlite3
    from xauusd.local_state import SQLiteAgentTranscriptStore
    from xauusd.lab_store import LabStore
    _,root,work=setup
    database=work.parent/'state.sqlite'
    store=LabStore(SQLiteAgentTranscriptStore(database))
    manager=EngineeringManager(root,store)
    for index in range(9): assert manager.snapshot(work.parent/('snapshot'+str(index)))['ok']
    with sqlite3.connect(database) as connection:
        count=connection.execute("SELECT count(*) FROM bits_state WHERE state_key LIKE 'lab:engineering_snapshot:%'").fetchone()[0]
    assert count==8
