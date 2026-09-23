from uuid import uuid4
import json
import pytest
from xauusd.bits import BitsError
from xauusd.bits_jobs import BitsStore, SecretFilter
from xauusd.bits_memory import BitsMemory, NOTE_FIELDS, result_for_prompt
from xauusd.local_state import SQLiteAgentTranscriptStore


@pytest.fixture
def memory(tmp_path):
    return BitsMemory(BitsStore(SQLiteAgentTranscriptStore(str(tmp_path/'state.db'))),
                      SecretFilter(str(tmp_path/'no-env')))


def reply(i):
    return dict(reply_to=str(i), summary='Hypothesis only: price 4321.25 at 09:30 UTC; needs validation.',
                status='completed',actions=[])


def test_memory_retains_recent_exchanges_and_source_linked_digest(memory):
    for i in range(15): memory.remember('cycle',reply(i))
    context=memory.context()
    assert len(context['recent'])==6
    assert context['recent'][-1]['source']=='14'
    assert context['digest'][-1]['source']=='8'
    assert '4321.25' in context['digest'][-1]['assessment']
    memory.remember('cycle',reply(14))
    assert len(memory.context()['recent'])==6
    assert BitsMemory(memory.store).context()['recent']==context['recent']


def test_history_size_and_excerpts_are_explicit(memory):
    for i in range(100):
        r=reply(i);r['summary']='observation '*3000
        memory.remember('cycle',r)
    assert len(json.dumps(memory.context()))<15000
    assert 'excerpt' in memory.context()['recent'][0]['assessment']
    result=dict(job_id='job',stdout='x'*50000,stderr='y'*3000,status='succeeded',exit_code=0)
    view=result_for_prompt(result)
    assert view['context_excerpt'] and view['source']=='bits-job job'
    assert len(view['stdout'])<3300 and len(view['stderr'])<900
    assert len(result['stdout'])==50000


def test_notes_preserve_structured_claims_and_reject_oversize(memory,monkeypatch):
    notes={key:[] for key in NOTE_FIELDS}
    notes['hypotheses']=[{'text':'Unverified breakout near 4321.25; review after 10:00 UTC.','sources':['job-1']}]
    memory.write_notes(notes)
    assert memory.context()['working_notes']['notes']==notes
    notes['findings']=[{'text':'a'*5000,'sources':[]}]
    with pytest.raises(BitsError):memory.write_notes(notes)
    value=uuid4().hex;monkeypatch.setenv('TEST_SECRET',value)
    notes['findings']=[{'text':value,'sources':[]}]
    with pytest.raises(BitsError):memory.write_notes(notes)
    assert value not in json.dumps(memory.context())
