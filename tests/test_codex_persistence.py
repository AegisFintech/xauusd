from pathlib import Path
from xauusd.lab_codex import CodexResearchClient

def test_resumes_exact_thread_and_enables_native_compaction(tmp_path):
    client=CodexResearchClient('/usr/bin/codex')
    client.thread_id='12345678-1234-1234-1234-123456789abc'
    command=client.command(tmp_path,'continue')
    assert '--ephemeral' not in command
    assert command[-3:]==['resume',client.thread_id,'continue']
    assert 'model_auto_compact_token_limit=80000' in command

def test_thread_id_persisted_before_next_turn():
    client=CodexResearchClient('/usr/bin/codex'); saved=[]
    client.save_thread=saved.append
    client._event(b'{"type":"thread.started","thread_id":"12345678-1234-1234-1234-123456789abc"}',lambda *a:None)
    assert saved==['12345678-1234-1234-1234-123456789abc']


def test_harness_pins_luna_on_new_and_resumed_calls(tmp_path):
    client=CodexResearchClient('/usr/bin/codex')
    for thread in (None,'12345678-1234-1234-1234-123456789abc'):
        client.thread_id=thread
        command=client.command(tmp_path,'continue')
        assert command[command.index('--model')+1]=='gpt-6-luna'


def test_session_telemetry_tracks_native_compaction_incrementally(tmp_path):
    import json
    from xauusd.lab_codex import session_telemetry
    thread='12345678-1234-1234-1234-123456789abc'
    path=tmp_path/('rollout-'+thread+'.jsonl')
    rows=[{'type':'compacted','timestamp':'2026-10-23T01:00:00Z','payload':{'message':'private content'}},
          {'type':'event_msg','timestamp':'2026-10-23T01:01:00Z','payload':{'type':'token_count','info':{'last_token_usage':{'input_tokens':800,'cached_input_tokens':600,'output_tokens':20},'total_token_usage':{'input_tokens':1600}}}}]
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    first=session_telemetry(tmp_path,thread,{})
    assert first['compactions']==1 and first['last_token_usage']['input_tokens']==800
    assert 'private content' not in json.dumps(first)
    assert session_telemetry(tmp_path,thread,first)['compactions']==1
    with path.open('a') as f: f.write(json.dumps({'type':'compacted','timestamp':'2026-10-23T01:02:00Z'})+'\n')
    assert session_telemetry(tmp_path,thread,first)['compactions']==2
    # An incomplete last line must be retried rather than skipped forever.
    with path.open('a') as f:f.write('{"type":"compacted"')
    partial=session_telemetry(tmp_path,thread,first)
    with path.open('a') as f:f.write(',"timestamp":"2026-10-23T01:03:00Z"}\n')
    assert session_telemetry(tmp_path,thread,partial)['compactions']==3
