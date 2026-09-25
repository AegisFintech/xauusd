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


# --- xauusd.notes/1: published schema, structured rejections, pending recovery ---
import hashlib
from xauusd.bits_memory import (NOTES_BUDGET, NOTES_SCHEMA, NotesRejected, check_notes, notes_schema,
                                parse_notes_input, validate_notes)
from xauusd.experiment_registry import canonical_json


def entry(text, *sources):
    return {'text': text, 'sources': list(sources)}


def sample_notes(**overrides):
    notes = {key: [] for key in NOTE_FIELDS}
    notes['findings'] = [entry('Weekly rule: 34 signals, latest 0, threshold 237.25 (report units).',
                               'c5ea68176942459881c9409618ac2936')]
    notes['next_steps'] = [entry('Reproduce with a frozen input snapshot.', 'transcript:14441')]
    notes.update(overrides)
    return notes


def rejection(payload, secrets=None):
    with pytest.raises(NotesRejected) as caught:
        check_notes(payload, secrets or SecretFilter('/nonexistent/.env'))
    return caught.value


def codes(error):
    return [(item['code'], item['path']) for item in error.issues]


def observed_wrapper_payload():
    """Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single notes key."""
    notes = {key: [] for key in NOTE_FIELDS}
    notes['findings'] = [entry(f'Finding {i}: EMA fold {i} differs by one turnover event and $2.80/oz.',
                               '91be334e3abb4a4fa0996a960c2a2297') for i in range(8)]
    notes['hypotheses'] = [entry('Weekly exhaustion reversal may be concentrated in few trades.',
                                 '53e4380f3e2e4b01b772a46da08601b5')]
    notes['rejected_approaches'] = [entry('EMA crossover: inconsistent across folds after costs.', 'job-1')]
    notes['open_questions'] = [entry('Why 34 versus 30 historical signals?', 'transcript:14425')]
    notes['next_steps'] = [entry('Freeze the input snapshot and rerun the producer script.', 'transcript:14433')]
    shortfall = 2571 - len(canonical_json(notes))
    notes['next_steps'][0]['text'] += ' ' + 'x' * (shortfall - 1)
    assert len(canonical_json(notes)) == 2571
    return {'notes': notes}


def test_observed_notes_wrapper_is_an_explicit_compatibility_form(memory):
    payload = observed_wrapper_payload()
    # The previous validator required exactly the five categories at top level, so this
    # 2,571-character payload failed only because of its shape, never its size.
    assert set(payload) != NOTE_FIELDS and len(canonical_json(payload['notes'])) < NOTES_BUDGET
    saved = memory.write_notes(payload)
    assert saved['status'] == 'saved' and saved['input_form'] == 'notes_wrapper'
    assert saved['characters'] == 2571 and saved['version'] == 1
    stored = memory.store.get('working_notes')
    assert stored['notes'] == payload['notes'] and stored['schema'] == NOTES_SCHEMA
    raw = canonical_json(stored['notes'])
    assert stored['digest'] == saved['digest'] == 'sha256:' + hashlib.sha256(raw.encode()).hexdigest()


def test_raw_wrapped_and_versioned_forms_share_one_revision(memory):
    notes = sample_notes()
    first = memory.write_notes(notes)
    assert (first['status'], first['version'], first['input_form']) == ('saved', 1, 'canonical')
    assert memory.write_notes({'notes': notes})['status'] == 'unchanged'
    again = memory.write_notes({'schema': NOTES_SCHEMA, 'notes': notes})
    assert (again['status'], again['version'], again['digest']) == ('unchanged', 1, first['digest'])
    changed = memory.write_notes(sample_notes(open_questions=[entry('Is the threshold 182.98 or 237.25?', 'job-2')]))
    assert changed['version'] == 2 and changed['digest'] != first['digest']
    assert memory.store.get('working_notes')['version'] == 2


def test_mixed_and_unknown_shapes_are_rejected_with_actionable_paths():
    notes = sample_notes()
    error = rejection({'notes': notes, 'findings': []})
    assert codes(error)[0] == ('ambiguous_shape', '$') and error.issues[0]['categories'] == ['findings']
    assert codes(rejection({'notes': notes, 'updated_at': '2026-09-25T01:02:00+00:00'})) == [('unexpected_field', '$.updated_at')]
    unsupported = rejection({'schema': 'xauusd.notes/2', 'notes': notes})
    assert codes(unsupported) == [('unsupported_schema', '$.schema')]
    assert unsupported.issues[0]['expected'] == NOTES_SCHEMA and unsupported.issues[0]['actual'] == 'xauusd.notes/2'
    assert codes(rejection({'schema': NOTES_SCHEMA, **notes})) == [('unexpected_field', '$.schema')]
    assert rejection([notes]).issues[0]['actual'] == 'array'


def test_malformed_fields_are_all_reported_with_paths_and_types():
    notes = sample_notes()
    del notes['open_questions']
    notes['extra'] = []
    notes['findings'] = [{'text': '', 'sources': ['job', 7]}, 'bare string', {'text': 'ok', 'sources': 'job', 'x': 1}]
    notes['hypotheses'] = [entry('h', 'job')] * 13
    notes['next_steps'] = {'text': 'not a list'}
    error = rejection(notes)
    found = codes(error)
    for expected in [('unexpected_field', '$.extra'), ('missing_field', '$.open_questions'),
                     ('empty_value', '$.findings[0].text'), ('invalid_type', '$.findings[0].sources[1]'),
                     ('invalid_type', '$.findings[1]'), ('unexpected_field', '$.findings[2].x'),
                     ('invalid_type', '$.findings[2].sources'), ('too_many_entries', '$.hypotheses'),
                     ('invalid_type', '$.next_steps')]:
        assert expected in found
    too_many = next(item for item in error.issues if item['code'] == 'too_many_entries')
    assert (too_many['actual_entries'], too_many['maximum_entries']) == (13, 12)
    assert all(item['retryable'] and item['retry'] == 'after_correction' for item in error.issues)
    assert error.report()['error_count'] == len(found)


def test_oversize_notes_report_sizes_and_preserve_previous_notes(memory):
    memory.write_notes(sample_notes())
    before = memory.store.get('working_notes')
    big = sample_notes(findings=[entry('a' * 700, 'job') for _ in range(7)])
    with pytest.raises(NotesRejected) as caught:
        memory.write_notes(big)
    detail = caught.value.issues[0]
    assert detail['code'] == 'notes_too_large' and detail['maximum_characters'] == NOTES_BUDGET
    assert detail['actual_characters'] == len(canonical_json(big)) > NOTES_BUDGET
    assert detail['category_characters']['findings'] > 4900
    assert memory.store.get('working_notes') == before
    pending = memory.store.get('pending_notes')
    assert pending['attempts'] == 1 and pending['payload'] == big and pending['latest']['retained']


def test_secret_notes_are_rejected_never_echoed_or_retained(memory, monkeypatch):
    value = 'k' + uuid4().hex  # an identifier-shaped key, so only the secret filter can redact it
    monkeypatch.setenv('EXAMPLE_API_TOKEN', value)
    with pytest.raises(NotesRejected) as caught:
        memory.write_notes(sample_notes(findings=[entry('leaked ' + value, 'job')]))
    assert caught.value.issues[0]['code'] == 'sensitive_content'
    assert value not in json.dumps(caught.value.report())
    pending = memory.store.get('pending_notes')
    assert pending['latest']['not_retained_reason'] == 'sensitive_content' and 'payload' not in pending
    assert value not in json.dumps(memory.context()) and value not in json.dumps(memory.pending())
    keyed = rejection({**sample_notes(), value: []}, memory.secrets)
    assert value not in json.dumps(keyed.report()) and keyed.issues[0]['path'] == '$[<unexpected key>]'


def test_storage_failure_rolls_back_the_whole_write(memory, monkeypatch):
    from xauusd.bits_jobs import StateTransaction
    memory.write_notes(sample_notes())
    before = memory.store.get('working_notes')
    def broken(self, key):
        raise RuntimeError('disk full')
    monkeypatch.setattr(StateTransaction, 'delete', broken)
    with pytest.raises(RuntimeError):
        memory.write_notes(sample_notes(hypotheses=[entry('new', 'job')]))
    assert memory.store.get('working_notes') == before


def test_pending_notes_stay_recoverable_and_repeated_failures_create_repair_task(memory):
    draft = sample_notes()
    draft['findings'][0]['sources'] = 'c5ea68176942459881c9409618ac2936'
    for attempt in (1, 2):
        with pytest.raises(NotesRejected) as caught:
            memory.write_notes(draft)
        assert caught.value.pending['attempts'] == attempt and caught.value.pending['notes_unchanged']
    status = memory.status()
    assert status['state'] == 'failing' and status['needs_repair'] and status['consecutive_failures'] == 2
    assert status['last_error'] == {'code': 'invalid_type', 'path': '$.findings[0].sources',
                                    'message': 'sources must be an array'}
    task = memory.repair_task()
    assert task['kind'] == 'memory_write' and 'installed' in task['instruction']
    assert all(' -m xauusd.cli bits-memory ' in command for command in task['commands'].values())
    context = memory.context()
    assert context['pending_notes']['payload'] == draft and context['memory_status']['needs_repair']
    # The evidence reference survives in the retained payload until a corrected write succeeds.
    fixed = json.loads(json.dumps(draft))
    fixed['findings'][0]['sources'] = [fixed['findings'][0]['sources']]
    assert memory.write_notes(fixed)['status'] == 'saved'
    assert memory.store.get('pending_notes') is None and memory.repair_task() is None
    assert memory.status()['state'] == 'ok' and memory.status()['notes_version'] == 1


def test_unparseable_input_reports_position_and_is_kept_as_text(memory):
    text = '{"findings": [{"text": "EMA fold one differs", "sources": ["job"]}], "hypotheses": ['
    with pytest.raises(NotesRejected) as caught:
        memory.submit(text)
    detail = caught.value.issues[0]
    assert detail['code'] == 'invalid_json' and detail['line'] == 1 and detail['column'] > 1
    pending = memory.store.get('pending_notes')
    assert pending['payload_kind'] == 'text' and pending['payload'] == text
    for raw, code in (('{"a": NaN}', 'non_finite_number'), ('{"a": 1, "a": 2}', 'duplicate_field'),
                      ('x' * 70000, 'input_too_large'), (None, 'missing_input')):
        with pytest.raises(NotesRejected) as caught:
            parse_notes_input(raw)
        assert caught.value.code == code


def test_validation_only_and_published_schema():
    result = validate_notes({'notes': sample_notes()}, SecretFilter('/nonexistent/.env'))
    assert result['status'] == 'valid' and result['input_form'] == 'notes_wrapper'
    assert result['entries']['findings'] == 1 and result['maximum_characters'] == NOTES_BUDGET
    schema = notes_schema()
    assert schema['schema'] == NOTES_SCHEMA and schema['limits']['max_entries_per_category'] == 12
    assert set(schema['accepted_forms']) == {'canonical', 'versioned', 'compatibility'}
    for command in schema['commands'].values():
        assert ' -m xauusd.cli bits-' in command and not command.startswith('bits-')
    assert 'no standalone bits-memory executable' in schema['note']


def test_policy_publishes_complete_commands_limits_and_source_rules(memory):
    policy = memory.context()['policy']
    assert ' -m xauusd.cli bits-memory validate --input-file - ' in policy
    assert ' -m xauusd.cli bits-job JOB_ID ' in policy and 'no standalone bits-memory' in policy
    assert 'at most 12' in policy and '4000 characters' in policy and 'sources name evidence' in policy
