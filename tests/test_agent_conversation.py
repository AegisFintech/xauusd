import json
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.test_lab import setup


def test_full_access_launcher_preserves_session_and_compaction(tmp_path):
    from xauusd.lab_codex import CodexResearchClient
    client=CodexResearchClient('/usr/bin/codex');client.thread_id='existing-thread'
    command=client.command(tmp_path,'continue')
    assert '--yolo' in command
    assert not any('permissions.lab' in a or 'default_permissions' in a or a=='--sandbox' for a in command)
    assert command[-3:]==['resume','existing-thread','continue']
    assert 'model_auto_compact_token_limit=80000' in command


def test_large_exchange_is_retrievable_but_activity_stays_small(tmp_path,monkeypatch):
    from xauusd.agent_conversation import ConversationStore
    store,_=setup(tmp_path)
    payload='line of evidence\n'*2000+'THE-END'
    event=store.event('tool_result','Completed',{'output':payload,'session_id':'s','turn_id':'t'})
    assert len(json.dumps(event))<4000
    records=ConversationStore(store);record=records.entries()['entries'][0]
    assert record['id']==event['detail']['conversation_id']
    text='';offset=0
    while True:
        page=records.page(record['id'],offset,3000);text+=page['text']
        assert len(page['text'])<=3000
        if page['next_offset'] is None:break
        offset=page['next_offset']
    assert json.loads(text)['detail']['output']==payload
    assert page['session_id']=='s' and page['turn_id']=='t'


def test_filters_before_capture_and_deduplicates_instruction_content(tmp_path,monkeypatch):
    from xauusd.agent_conversation import ConversationStore
    store,_=setup(tmp_path);records=ConversationStore(store)
    monkeypatch.setenv('TEST_SECRET','sensitive-test-value-123456789')
    a=records.append('instructions',{'detail':{'text':'same instructions','turn_id':'a'}},turn_id='a')
    b=records.append('instructions',{'detail':{'text':'same instructions','turn_id':'b'}},turn_id='b')
    assert a['digest']==b['digest']
    c=records.append('input',{'text':'sensitive-test-value-123456789'})
    assert 'sensitive-test-value' not in records.page(c['id'])['text']
    with store.state.db() as db:
        assert db.execute('SELECT COUNT(*) n FROM agent_conversation_bodies').fetchone()['n']==2


def test_retention_limits_and_equal_timestamp_paging(tmp_path,monkeypatch):
    from xauusd import agent_conversation as module
    store,_=setup(tmp_path);records=module.ConversationStore(store)
    now=datetime.now(timezone.utc)
    old=records.append('input',{'text':'expired'},now=now-timedelta(days=8))
    assert not records.page(old['id'])['ok']
    ids={records.append('tool',{'text':str(i)},now=now)['id'] for i in range(4)}
    first=records.entries(limit=2);second=records.entries(first['next_before'],2)
    assert {r['id'] for r in first['entries']+second['entries']}==ids
    monkeypatch.setattr(module,'MAX_ENTRIES',2);records.prune(now)
    assert len(records.entries()['entries'])==2
    monkeypatch.setattr(module,'MAX_BYTES',1);records.prune(now)
    assert records.entries()['entries']==[]
    with store.state.db() as db:
        assert db.execute('SELECT COUNT(*) n FROM agent_conversation_bodies').fetchone()['n']==0


def test_read_only_paged_routes_and_inert_ui(tmp_path):
    from xauusd.agent_conversation import ConversationStore
    from xauusd.lab_dashboard import attach_routes,PAGE
    store,paper=setup(tmp_path);row=ConversationStore(store).append('input',{'text':'<img onerror=alert(1)>'+'x'*10000})
    app=FastAPI();attach_routes(app,store.transcript,lambda:paper);client=TestClient(app)
    assert client.get('/api/lab/conversation').json()['entries'][0]['id']==row['id']
    page=client.get('/api/lab/conversation/'+row['id']+'?limit=2000').json()
    assert len(page['text'])==2000 and page['next_offset']==2000
    assert client.get('/api/lab/conversation/'+row['id']+'?limit=12001').status_code==422
    download=client.get('/api/lab/conversation/'+row['id']+'/download')
    assert download.status_code==200 and len(download.text)>10000
    assert download.headers['content-disposition'].startswith('attachment;')
    assert client.post('/api/lab/conversation/'+row['id']).status_code==405
    assert 'text.textContent=page.text' in PAGE and 'Next page' in PAGE


def test_native_output_is_complete_and_private_reasoning_is_ignored(tmp_path):
    from xauusd.lab_codex import CodexResearchClient
    client=CodexResearchClient('/usr/bin/codex');events=[]
    client._event(json.dumps({'item':{'type':'command_execution','aggregated_output':'x'*9000,'exit_code':0}}).encode(),lambda *a:events.append(a))
    assert len(events[0][2]['output'])==9000
    client._event(json.dumps({'item':{'type':'reasoning','text':'PRIVATE'}}).encode(),lambda *a:events.append(a))
    assert len(events)==1


def test_real_child_boundary_records_exact_application_input_and_validated_reply(tmp_path):
    from xauusd.lab_codex import CodexResearchClient
    from tests.test_agent_advisor import turn
    from xauusd.agent_conversation import ConversationStore
    import sys
    store,_=setup(tmp_path);client=CodexResearchClient('/usr/bin/codex')
    response=turn();workspace=tmp_path/'workspace';workspace.mkdir()
    child="from pathlib import Path;Path('proposal.json').write_text("+repr(json.dumps(response))+")"
    client.command=lambda workspace,prompt:[sys.executable,'-c',child]
    brief={'evidence':'training only','input_marker':'RETAIN-THIS-EXACT-CONTEXT'}
    assert client.run_turn(workspace,brief,store.event)==response
    records=ConversationStore(store);entries=records.entries()['entries']
    kinds={e['kind']:e for e in entries}
    captured=json.loads(records.download(kinds['input']['id']))['detail']
    assert captured['brief']==brief and captured['permissions']=='yolo'
    assert captured['prompt'].startswith('Current workspace: ')
    instructions=json.loads(records.download(kinds['instructions']['id']))['detail']['text']
    assert instructions==(workspace/'AGENTS.md').read_text()
    assert json.loads(records.download(kinds['assistant']['id']))['detail']['response']==response
    assert len({e['turn_id'] for e in entries})==1 and entries[0]['turn_id']


def test_capture_limit_is_explicit_and_remains_valid_json(tmp_path,monkeypatch):
    from xauusd import agent_conversation as module
    store,_=setup(tmp_path);records=module.ConversationStore(store)
    monkeypatch.setattr(module,'MAX_CAPTURE_CHARS',8000)
    row=records.append('tool',{'text':'\\'*10000})
    text=records.download(row['id']);payload=json.loads(text)
    assert payload['capture_truncated'] is True and payload['original_characters']>8000
    assert len(text)<=8000
