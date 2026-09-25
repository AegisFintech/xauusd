"""R1: rejected memory writes keep durable draft identities until explicitly resolved."""
import json
import os
import sqlite3
import threading
from uuid import uuid4

import pytest

from xauusd.bits_jobs import BitsStore, SecretFilter, StateTransaction
from xauusd.bits_memory import (DRAFT_ALERT_AGE_SECONDS, MAX_CLOSED_DRAFTS, MAX_OPEN_DRAFTS, BitsMemory,
                                NotesRejected, NOTE_CATEGORIES, notes_schema)
from xauusd.local_state import SQLiteAgentTranscriptStore


@pytest.fixture
def memory(tmp_path):
    return BitsMemory(BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db'))),
                      SecretFilter(str(tmp_path / 'no-env')))


def notes(*findings):
    value = {category: [] for category in NOTE_CATEGORIES}
    value['findings'] = [{'text': text, 'sources': sources} for text, sources in findings]
    return value


VALID_A = notes(('Valid finding A.', ['job-a']))
# Draft B: new evidence, but sources is a bare string instead of a list.
DRAFT_B = notes(('Weekly reproduction: 34 versus 30 signals.', '53e4380f3e2e4b01b772a46da08601b5'))
FIXED_B = notes(('Weekly reproduction: 34 versus 30 signals.', ['53e4380f3e2e4b01b772a46da08601b5']))


def reject(memory, payload, **kwargs):
    with pytest.raises(NotesRejected) as caught:
        memory.write_notes(payload, **kwargs)
    return caught.value


def open_drafts(memory):
    return (memory.store.get('pending_drafts') or {'open': []})['open']


def test_unchanged_write_reproduction_keeps_draft_b_and_its_alert(memory):
    memory.write_notes(VALID_A)
    draft_id = reject(memory, DRAFT_B).pending['draft_ids'][0]
    result = memory.write_notes(VALID_A)
    assert result['status'] == 'unchanged' and result['open_drafts'] == [draft_id]
    assert 'did not clear' in result['notice']
    (draft,) = open_drafts(memory)
    assert draft['id'] == draft_id and draft['payload'] == DRAFT_B
    assert draft['evidence'] == ['53e4380f3e2e4b01b772a46da08601b5']
    status = memory.status()
    assert status['needs_repair'] and status['repair_reasons'] == ['later_write_did_not_resolve']
    assert status['state'] == 'drafts_pending' and memory.repair_task()['open_drafts'][0]['id'] == draft_id


def test_unrelated_write_keeps_draft_b_and_reports_its_stale_base(memory):
    memory.write_notes(VALID_A)
    draft_id = reject(memory, DRAFT_B).pending['draft_ids'][0]
    saved = memory.write_notes(notes(('Unrelated finding C.', ['job-c'])))
    assert saved['status'] == 'saved' and saved['version'] == 2 and saved['open_drafts'] == [draft_id]
    assert set(memory.status()['repair_reasons']) == {'later_write_did_not_resolve', 'notes_changed_since_draft'}
    context = memory.context()['pending_notes']
    assert context['drafts'][0]['id'] == draft_id and context['payload'] == DRAFT_B
    assert context['drafts'][0]['unresolved_evidence'] == ['53e4380f3e2e4b01b772a46da08601b5']


def test_explicit_corrected_resolution_clears_only_the_named_draft(memory):
    memory.write_notes(VALID_A)
    first = reject(memory, DRAFT_B).pending['draft_ids'][0]
    other_payload = notes(('EMA fold one differs by $2.80/oz.', 7))
    second = reject(memory, other_payload).pending['draft_ids'][0]
    assert first != second and len(open_drafts(memory)) == 2
    merged = notes(('Valid finding A.', ['job-a']), ('Weekly reproduction: 34 versus 30 signals.',
                                                     ['53e4380f3e2e4b01b772a46da08601b5']))
    result = memory.write_notes(merged, resolves=[first], base_version=1)
    assert result['resolved'] == [{'draft_id': first, 'dropped_evidence': []}]
    assert [draft['id'] for draft in open_drafts(memory)] == [second] and result['open_drafts'] == [second]
    closed = memory.store.get('pending_drafts')['closed'][-1]
    assert closed['id'] == first and closed['resolution'] == 'resolved' and closed['notes_version'] == 2


def test_multiple_failed_drafts_are_bounded_with_explicit_eviction(memory):
    ids = [reject(memory, notes((f'draft {index}', f'job-{index}'))).pending for index in range(MAX_OPEN_DRAFTS + 1)]
    assert all(pending['created'] for pending in ids)
    assert ids[-1]['evicted'] == [ids[0]['draft_ids'][0]]
    state = memory.store.get('pending_drafts')
    assert len(state['open']) == MAX_OPEN_DRAFTS and state['evicted_total'] == 1
    evicted = state['closed'][-1]
    assert evicted['resolution'] == 'evicted_overflow' and evicted['evidence'] == ['job-0']
    assert 'payload' not in evicted and evicted['last_error']['code'] == 'invalid_type'
    for index in range(MAX_CLOSED_DRAFTS + 5):
        reject(memory, notes((f'more {index}', f'job-more-{index}')))
    state = memory.store.get('pending_drafts')
    assert len(state['open']) == MAX_OPEN_DRAFTS and len(state['closed']) == MAX_CLOSED_DRAFTS
    schema = notes_schema()['drafts']
    assert schema['limits']['max_open'] == MAX_OPEN_DRAFTS and 'evicted_overflow' in schema['overflow']


def test_identical_retries_update_one_draft_and_usage_errors_open_none(memory):
    first = reject(memory, DRAFT_B).pending
    again = reject(memory, DRAFT_B).pending
    assert again['draft_ids'] == first['draft_ids'] and again['attempts'] == 2 and not again['created']
    with pytest.raises(NotesRejected) as caught:
        memory.submit(None)
    assert caught.value.pending['draft_ids'] == [] and caught.value.pending['draft_reason'] == 'no_payload'
    assert caught.value.pending['consecutive_rejections'] == 3 and len(open_drafts(memory)) == 1


def test_interrupted_resolution_rolls_back_notes_and_drafts_together(memory, monkeypatch):
    memory.write_notes(VALID_A)
    draft_id = reject(memory, DRAFT_B).pending['draft_ids'][0]
    before_notes, before_drafts = memory.store.get('working_notes'), memory.store.get('pending_drafts')
    original = StateTransaction.put
    def interrupted(self, key, value):
        if key == 'pending_drafts':  # after the notes row was replaced inside the same transaction
            raise sqlite3.OperationalError('disk I/O error')
        return original(self, key, value)
    monkeypatch.setattr(StateTransaction, 'put', interrupted)
    with pytest.raises(sqlite3.OperationalError):
        memory.write_notes(FIXED_B, resolves=[draft_id], base_version=1)
    monkeypatch.setattr(StateTransaction, 'put', original)
    assert memory.store.get('working_notes') == before_notes
    assert memory.store.get('pending_drafts') == before_drafts and open_drafts(memory)[0]['id'] == draft_id


def test_stale_base_versions_are_rejected_and_recorded(memory):
    memory.write_notes(VALID_A)
    memory.write_notes(notes(('Second revision.', ['job-2'])))
    stale = reject(memory, notes(('Built from revision 1.', ['job-3'])), base_version=1)
    detail = stale.issues[0]
    assert (detail['code'], detail['path'], detail['current_version']) == ('stale_base', '--base-version', 2)
    assert stale.pending['created'] and memory.store.get('working_notes')['version'] == 2
    assert 'notes_changed_since_draft' in memory.status()['repair_reasons']
    draft_id = stale.pending['draft_ids'][0]
    # Resolving without asserting the current base stays stale because the draft was written against revision 1.
    assert reject(memory, notes(('Merged.', ['job-3'])), resolves=[draft_id]).code == 'stale_base'
    merged = memory.write_notes(notes(('Second revision.', ['job-2']), ('Merged.', ['job-3'])),
                                resolves=[draft_id], base_version=2)
    assert merged['version'] == 3 and merged['resolved'][0]['draft_id'] == draft_id
    assert reject(memory, VALID_A, base_version=-1).code == 'invalid_base_version'


def test_concurrent_writers_with_the_same_base_cannot_both_win(tmp_path):
    path = str(tmp_path / 'state.db')
    BitsMemory(BitsStore(SQLiteAgentTranscriptStore(path)), SecretFilter(str(tmp_path / 'no-env'))).write_notes(VALID_A)
    barrier, outcomes = threading.Barrier(2), []

    def writer(label):
        memory = BitsMemory(BitsStore(SQLiteAgentTranscriptStore(path)), SecretFilter(str(tmp_path / 'no-env')))
        barrier.wait()
        try:
            outcomes.append(('saved', memory.write_notes(notes((f'writer {label}', [f'job-{label}'])), base_version=1)['version']))
        except NotesRejected as rejection:
            outcomes.append((rejection.code, rejection.pending['draft_ids']))
    threads = [threading.Thread(target=writer, args=(label,)) for label in 'xy']
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert sorted(outcome[0] for outcome in outcomes) == ['saved', 'stale_base']
    loser = next(outcome for outcome in outcomes if outcome[0] == 'stale_base')
    memory = BitsMemory(BitsStore(SQLiteAgentTranscriptStore(path)), SecretFilter(str(tmp_path / 'no-env')))
    assert memory.store.get('working_notes')['version'] == 2
    assert [draft['id'] for draft in open_drafts(memory)] == loser[1]  # the losing findings stay recoverable


def test_replacing_a_draft_keeps_unresolved_evidence_and_resolution_reports_drops(memory):
    memory.write_notes(VALID_A)
    draft_id = reject(memory, notes(('first attempt', ['job-old', 'transcript:14425']), ('bad', 3))).pending['draft_ids'][0]
    retry = reject(memory, notes(('second attempt', 'job-new')), resolves=[draft_id])
    assert retry.pending['draft_ids'] == [draft_id] and not retry.pending['created']
    (draft,) = open_drafts(memory)
    assert draft['attempts'] == 2 and draft['payload'] == notes(('second attempt', 'job-new'))
    assert draft['evidence'] == ['job-old', 'transcript:14425', 'job-new']
    result = memory.write_notes(notes(('second attempt', ['job-new']), ('first attempt', ['job-old'])),
                                resolves=[draft_id], base_version=1)
    assert result['resolved'] == [{'draft_id': draft_id, 'dropped_evidence': ['transcript:14425']}]
    assert memory.store.get('pending_drafts')['closed'][-1]['dropped_evidence'] == ['transcript:14425']


def test_supersede_needs_identity_and_reason_and_closes_only_that_draft(memory, monkeypatch):
    first = reject(memory, DRAFT_B).pending['draft_ids'][0]
    second = reject(memory, notes(('other', 5))).pending['draft_ids'][0]
    for draft_id, reason, code in (('draft_x', 'why', 'invalid_draft_id'), (first, ' ', 'missing_reason'),
                                   (first, 'x' * 301, 'reason_too_long'), ('draft_' + 'a' * 12, 'why', 'unknown_draft')):
        with pytest.raises(NotesRejected) as caught:
            memory.supersede(draft_id, reason)
        assert caught.value.code == code
    token = 'k' + uuid4().hex
    monkeypatch.setenv('EXAMPLE_ACCESS_TOKEN', token)
    with pytest.raises(NotesRejected) as caught:
        memory.supersede(first, 'contains ' + token)
    assert caught.value.code == 'sensitive_content' and token not in json.dumps(caught.value.report())
    result = memory.supersede(first, 'Superseded by the frozen-snapshot reproduction.')
    assert result['status'] == 'superseded' and result['open_drafts'] == [second]
    assert result['dropped_evidence'] == ['53e4380f3e2e4b01b772a46da08601b5']
    with pytest.raises(NotesRejected) as caught:
        memory.supersede(first, 'again')
    assert caught.value.code == 'draft_not_open'
    assert token not in json.dumps(memory.store.get('pending_drafts'))


def test_draft_references_are_validated_and_closed_drafts_are_not_reopened(memory):
    memory.write_notes(VALID_A)
    draft_id = reject(memory, DRAFT_B).pending['draft_ids'][0]
    assert reject(memory, FIXED_B, resolves=['not-a-draft']).code == 'invalid_draft_id'
    unknown = reject(memory, FIXED_B, resolves=['draft_' + 'b' * 12])
    assert unknown.code == 'unknown_draft'
    memory.write_notes(FIXED_B, resolves=[draft_id] + unknown.pending['draft_ids'], base_version=1)
    repeat = reject(memory, FIXED_B, resolves=[draft_id], base_version=2)
    assert repeat.code == 'draft_not_open' and repeat.issues[0]['resolution'] == 'resolved'
    # Retrying an already-saved payload records nothing new to recover.
    assert repeat.pending['draft_reason'] == 'identical_to_stored_notes' and open_drafts(memory) == []


def test_legacy_single_pending_record_is_migrated_to_one_draft(memory):
    legacy_payload = {'notes': DRAFT_B}
    memory.store.put('pending_notes', {'schema': 'xauusd.notes/1', 'attempts': 2, 'needs_repair': True,
                                       'latest': {'recorded_at': '2026-09-25T09:00:00+00:00',
                                                  'error': {'code': 'invalid_type', 'path': '$.notes.findings[0].sources',
                                                            'message': 'sources must be an array'}},
                                       'payload': legacy_payload, 'payload_kind': 'json', 'payload_characters': 200,
                                       'payload_recorded_at': '2026-09-25T09:00:00+00:00'})
    status = memory.status()
    assert status['open_drafts'] == 1 and 'migrated_legacy_draft' in status['repair_reasons']
    draft_id = status['draft_ids'][0]
    assert memory.status()['draft_ids'] == [draft_id]  # stable identity before migration is persisted
    saved = memory.write_notes(VALID_A)
    assert saved['open_drafts'] == [draft_id] and memory.store.get('pending_notes') is None
    migrated = open_drafts(memory)[0]
    assert migrated['payload'] == legacy_payload and migrated['base'] is None
    assert migrated['evidence'] == ['53e4380f3e2e4b01b772a46da08601b5']
    assert reject(memory, FIXED_B, resolves=[draft_id]).code == 'stale_base'  # unknown base needs an explicit one
    assert memory.write_notes(FIXED_B, resolves=[draft_id], base_version=1)['resolved'][0]['draft_id'] == draft_id


def test_old_drafts_raise_a_repair_reason(memory):
    draft_id = reject(memory, DRAFT_B).pending['draft_ids'][0]
    state = memory.store.get('pending_drafts')
    state['open'][0]['created_at'] = '2026-01-01T00:00:00+00:00'
    state['consecutive_rejections'] = 0
    memory.store.put('pending_drafts', state)
    assert memory.status()['repair_reasons'] == ['unresolved_over_30_minutes']
    assert DRAFT_ALERT_AGE_SECONDS == 1800 and memory.status()['draft_ids'] == [draft_id]


class RecordingPostgres:
    """psycopg-like connection: one implicit transaction per block, committed or rolled back on exit."""
    log = []

    def __init__(self, path):
        self.sqlite = sqlite3.connect(path, timeout=30)  # DML opens an implicit transaction, as psycopg does
        self.sqlite.row_factory = sqlite3.Row
        self.statements = []

    def execute(self, sql, params=()):
        assert not sql.lstrip().upper().startswith(('BEGIN', 'COMMIT', 'ROLLBACK')), 'manual transaction control'
        self.statements.append(sql)
        return self.sqlite.execute(sql.replace(' FOR UPDATE', ''), params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        (self.sqlite.rollback if exc_type else self.sqlite.commit)()
        RecordingPostgres.log.append(('rollback' if exc_type else 'commit', list(self.statements)))
        return False

    def close(self):
        self.sqlite.close()


class PostgresLikeTranscript:
    def __init__(self, path):
        self.path = path

    def connect(self):
        return RecordingPostgres(self.path)


def test_postgres_path_locks_and_commits_or_rolls_back_one_transaction(tmp_path, monkeypatch):
    memory = BitsMemory(BitsStore(PostgresLikeTranscript(str(tmp_path / 'pg.db'))), SecretFilter(str(tmp_path / 'no-env')))
    RecordingPostgres.log.clear()
    memory.write_notes(VALID_A)
    outcome, statements = RecordingPostgres.log[-1]
    lock = 'SELECT value_json FROM bits_state WHERE state_key=? FOR UPDATE'
    assert outcome == 'commit' and lock in statements
    assert statements.index(lock) < min(i for i, sql in enumerate(statements) if sql.startswith('INSERT INTO bits_state(state_key,value_json) VALUES(?,?) ON CONFLICT(state_key) DO UPDATE'))
    draft_id = reject(memory, DRAFT_B).pending['draft_ids'][0]
    before = memory.store.get('working_notes'), memory.store.get('pending_drafts')
    original = StateTransaction.put
    def interrupted(self, key, value):
        if key == 'pending_drafts':
            raise RuntimeError('connection lost')
        return original(self, key, value)
    monkeypatch.setattr(StateTransaction, 'put', interrupted)
    RecordingPostgres.log.clear()
    with pytest.raises(RuntimeError):
        memory.write_notes(FIXED_B, resolves=[draft_id], base_version=1)
    monkeypatch.setattr(StateTransaction, 'put', original)
    assert [entry[0] for entry in RecordingPostgres.log] == ['rollback']
    assert (memory.store.get('working_notes'), memory.store.get('pending_drafts')) == before


@pytest.mark.skipif(not os.getenv('XAUUSD_TEST_DATABASE_URL'),
                    reason='set XAUUSD_TEST_DATABASE_URL to a disposable Postgres/Cockroach database')
def test_real_database_transaction_contract():
    """Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store: it rewrites memory keys."""
    pytest.importorskip('psycopg')
    from xauusd.agent_loop import CockroachAgentTranscriptStore
    store = BitsStore(CockroachAgentTranscriptStore(os.environ['XAUUSD_TEST_DATABASE_URL']))
    for key in ('working_notes', 'pending_drafts', 'pending_notes', 'memory_lock'):
        store.delete(key)
    memory = BitsMemory(store, SecretFilter('/nonexistent/.env'))
    memory.write_notes(VALID_A)
    draft_id = reject(memory, DRAFT_B).pending['draft_ids'][0]
    assert memory.write_notes(VALID_A)['open_drafts'] == [draft_id]
    barrier, outcomes = threading.Barrier(2), []

    def writer(label):
        barrier.wait()
        try:
            BitsMemory(store, SecretFilter('/nonexistent/.env')).write_notes(
                notes((f'writer {label}', [f'job-{label}'])), base_version=1)
            outcomes.append('saved')
        except NotesRejected as rejection:
            outcomes.append(rejection.code)
        except Exception as exc:  # a serialization failure is also a refusal to let both win
            outcomes.append(type(exc).__name__)
    threads = [threading.Thread(target=writer, args=(label,)) for label in 'xy']
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert outcomes.count('saved') == 1 and store.get('working_notes')['version'] == 2
    for key in ('working_notes', 'pending_drafts', 'memory_lock'):
        store.delete(key)
