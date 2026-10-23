from pathlib import Path
import pytest
from xauusd.agent_tools import AgentTools, bounded_process

class Store:
    def __init__(self): self.values={}
    def meta(self,key,value=...):
        if value is ...: return self.values.get(key)
        self.values[key]=value

def test_domain_configuration(tmp_path):
    tools=AgentTools(Store(),tmp_path)
    assert tools.execute('source_domain',{'domain':'example.com'})['ok']
    for domain in ['localhost','127.0.0.1','https://example.com','a..com']:
        assert not tools.execute('source_domain',{'domain':domain})['ok']

def test_upload_refuses_escape_and_credentials(tmp_path):
    tools=AgentTools(Store(),tmp_path)
    for path in ['../secret','.env','/etc/passwd','auth.json']:
        assert not tools.execute('tc02_run',{'command':'true','upload':[path]})['ok']

def test_unknown_tool(tmp_path):
    assert AgentTools(Store(),tmp_path).execute('nope',{})['error_code']=='unknown_tool'

def test_process_timeout_and_output_bound():
    result=bounded_process(['/bin/sh','-c','sleep 3'],timeout=.1)
    assert result['timed_out']
    result=bounded_process(['/bin/sh','-c','yes x | head -c 300000'],timeout=5)
    assert len(result['output'].encode()) <= 262144
    assert result['output_truncated']

def test_symlink_upload(tmp_path):
    (tmp_path/'a.py').symlink_to('/etc/passwd')
    assert not AgentTools(Store(),tmp_path).execute('tc02_run',{'command':'true','upload':['a.py']})['ok']

def test_timeout_rejected_without_transport(tmp_path):
    tools=AgentTools(Store(),tmp_path)
    assert tools.execute('tc02_run',{'command':'true','timeout':1201})['error_code']=='invalid_timeout'

def test_source_fetch_does_not_change_default_configuration(tmp_path,monkeypatch):
    import xauusd.lab_sources as sources
    import socket
    monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**k:[(2,1,6,'',('93.184.216.34',443))])
    calls=[]
    monkeypatch.setattr(sources,'fetch_source',lambda url,**kw:calls.append(kw) or {'trusted':False})
    tools=AgentTools(Store(),tmp_path)
    assert not tools.execute('source_fetch',{'url':'https://example.com/a'})['ok']
    tools.execute('source_domain',{'domain':'example.com'})
    assert tools.execute('source_fetch',{'url':'https://example.com/a'})['ok']
    assert 'example.com' in calls[0]['domains']

def test_remote_retrieval_is_local_and_content_addressed(tmp_path,monkeypatch):
    import base64,json
    import xauusd.agent_tools as module
    monkeypatch.setattr(module,'bounded_process',lambda *a,**k:{'returncode':0,'timed_out':False,
        'output':json.dumps({'returncode':0,'output':'ok','files':{'result.txt':base64.b64encode(b'evidence').decode()}})})
    result=AgentTools(Store(),tmp_path).execute('tc02_run',{'command':'research','retrieve':['result.txt']})
    assert result['ok']
    assert (tmp_path/'remote-results/result.txt').read_bytes()==b'evidence'
    assert result['retrieved']['result.txt']['bytes']==8

def test_remote_uncertain_transport_is_not_retried(tmp_path,monkeypatch):
    import xauusd.agent_tools as module
    calls=[]
    monkeypatch.setattr(module,'bounded_process',lambda *a,**k:calls.append(a) or {'returncode':255,'timed_out':False})
    result=AgentTools(Store(),tmp_path).execute('tc02_run',{'command':'research'})
    assert not result['ok']
    assert result['error_code']=='remote_outcome_uncertain_no_retry'
    assert len(calls)==1

def test_uncertain_result_is_explicit(tmp_path,monkeypatch):
    import xauusd.agent_tools as module
    monkeypatch.setattr(module,'bounded_process',lambda *a,**k:{'returncode':255,'timed_out':False})
    assert AgentTools(Store(),tmp_path).execute('tc02_run',{'command':'true'})['uncertain'] is True

def test_fetch_rejects_private_dns(tmp_path,monkeypatch):
    import socket
    monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**k:[(2,1,6,'',('169.254.169.254',443))])
    tools=AgentTools(Store(),tmp_path);tools.execute('source_domain',{'domain':'metadata.example.com'})
    result=tools.execute('source_fetch',{'url':'https://metadata.example.com/'})
    assert result['error_code']=='source_address_not_public'

def test_remote_wrapper_requires_filesystem_isolation():
    from xauusd.agent_tools import REMOTE
    assert "shutil.which('bwrap')" in REMOTE
    assert "remote_sandbox_unavailable" in REMOTE
    assert "'--unshare-all'" in REMOTE
    assert "'--bind',str(w),'/work'" in REMOTE
    assert "'--ro-bind','/root'" not in REMOTE

def test_successful_shell_cannot_leave_background_writer(tmp_path):
    import time
    marker=tmp_path/'late.txt'
    result=bounded_process(['/bin/bash','-c',f'(sleep .4; echo orphan > {marker}) &'],timeout=2)
    assert result['returncode']==0
    time.sleep(.6)
    assert not marker.exists()

def test_dependency_install_requires_pins(tmp_path):
    tools=AgentTools(Store(),tmp_path)
    for requirement in ['numpy','numpy>=2','git+https://example.com/a','numpy==2; echo bad']:
        assert tools.execute('dependency_install',{'packages':[requirement]})['error_code']=='dependency_pin_required'

def test_dependency_install_targets_scratch_only(tmp_path,monkeypatch):
    import xauusd.agent_tools as module
    calls=[]
    monkeypatch.setattr(module,'bounded_process',lambda argv,**kw:calls.append((argv,kw)) or {'returncode':0,'output':'','timed_out':False})
    result=AgentTools(Store(),tmp_path).execute('dependency_install',{'packages':['numpy==2.2.0'],'timeout':60})
    assert result['ok']
    import shlex
    command=shlex.split(calls[0][0][-1])
    assert '--target' in command and str(tmp_path/'dependencies') in command
    assert '--only-binary' in command and ':all:' in command
    assert 'https://pypi.org/simple' in command
    assert 'TMPDIR' not in calls[0][1]['env']
    assert result['pythonpath']==str(tmp_path/'dependencies')

def test_market_observe_excludes_frozen_and_forming_bars(tmp_path,monkeypatch):
    import pandas as pd
    from datetime import datetime,timezone,timedelta
    import xauusd.data as data
    import xauusd.quotes as quotes
    now=datetime.now(timezone.utc).replace(second=0,microsecond=0)
    index=pd.date_range(now-timedelta(minutes=3),periods=4,freq='min')
    frame=pd.DataFrame({key:[1.,2.,3.,4.] for key in ['open','high','low','close','volume']},index=index)
    monkeypatch.setattr(data.HistoricalDataStore,'read',lambda s:frame)
    stamp=datetime.now(timezone.utc).isoformat()
    monkeypatch.setattr(quotes,'read_quote',lambda:{'source':'ctrader_demo','symbol':'XAUUSD','bid':4000.,'ask':4000.2,'spread':.2,'observed_at':stamp,'received_at':stamp})
    store=Store();store.meta('dataset',{'end':index[1].isoformat()})
    result=AgentTools(store,tmp_path).execute('market_observe',{})
    assert result['ok'] and result['quote_fresh']
    assert len(result['bars'])==1
    assert result['bars'][0]['timestamp']==index[2].isoformat()

def test_market_observe_without_frozen_boundary_reveals_no_history(tmp_path):
    result=AgentTools(Store(),tmp_path).execute('market_observe',{})
    assert result['bars']==[]
    assert result['note']=='dataset_boundary_unavailable_no_history_exposed'

def test_process_workspace_limit_stops_writer(tmp_path):
    result=bounded_process(['/bin/bash','-c','head -c 8192 /dev/zero > big; sleep 3'],
                           timeout=5,cwd=tmp_path,workspace_limit=1024)
    assert result['error_code']=='workspace_limit'
    assert result['returncode']!=0

def test_process_workspace_symlink_is_rejected(tmp_path):
    (tmp_path/'escape').symlink_to('/etc/passwd')
    result=bounded_process(['/bin/bash','-c','sleep 3'],timeout=5,cwd=tmp_path)
    assert result['error_code']=='workspace_symlink'

def test_remote_job_identity_is_action_derived(tmp_path,monkeypatch):
    import xauusd.agent_tools as module
    import hashlib,json
    captured=[]
    monkeypatch.setattr(module,'bounded_process',lambda *a,**kw:captured.append(json.loads(kw['input_data'])) or {'returncode':255,'timed_out':False})
    tools=AgentTools(Store(),tmp_path); tools.action_id='durable-action-123'
    result=tools.execute('tc02_run',{'command':'true'})
    expected=hashlib.sha256(tools.action_id.encode()).hexdigest()[:32]
    assert captured[0]['job_id']==expected
    assert result['job_id']==expected and result['uncertain']

def test_remote_status_rejects_bad_identifier_without_transport(tmp_path):
    result=AgentTools(Store(),tmp_path).execute('tc02_job_status',{'job_id':'../oops'})
    assert result['error_code']=='invalid_remote_job_id'
