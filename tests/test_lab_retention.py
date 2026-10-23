from pathlib import Path

from xauusd.lab_store import LabStore
from xauusd.local_state import SQLiteAgentTranscriptStore


def store_at(tmp_path):
    return LabStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))


def test_shadow_retention_keeps_live_state_and_compacts_final_metrics(tmp_path):
    store = store_at(tmp_path)
    for candidate_id, state in [('a', 'active'), ('p', 'probation'), ('q', 'qualified'), ('r', 'retired'), ('f', 'rejected_forward')]:
        store.candidate({'id': candidate_id, 'state': state})
        store.meta('shadow:' + candidate_id, {'closed_pnl': [3.0, -1.0], 'maximum_drawdown': -0.01})
    store.meta('shadow:evicted', {'closed_pnl': [2.0]})
    store.meta('active', 'missing_row_active')
    store.meta('shadow:missing_row_active', {'closed_pnl': []})
    store.state.put('paper:decision:untouched', {'filled': True})
    result = store.prune_research_evidence(tmp_path / 'data/lab')
    assert result['removed_shadows'] == 3
    for candidate_id in ('a', 'p', 'q', 'missing_row_active'):
        assert store.meta('shadow:' + candidate_id) is not None
    for candidate_id in ('r', 'f', 'evicted'):
        assert store.meta('shadow:' + candidate_id) is None
    summaries = store.meta('research_evidence_history')
    assert {r['id'] for r in summaries} == {'r', 'f', 'evicted'}
    assert next(r for r in summaries if r['id'] == 'r')['metrics']['net_profit'] == 2.0
    assert store.state.get('paper:decision:untouched') == {'filled': True}


def test_dataset_retention_keeps_twelve_current_and_protected_refs(tmp_path):
    store = store_at(tmp_path)
    directory = tmp_path / 'data/lab/datasets'; directory.mkdir(parents=True)
    versions = [f'{i:064x}' for i in range(18)]
    for version in versions: (directory / (version + '.parquet')).write_bytes(b'archive')
    store.meta('dataset_history', [{'version': v} for v in versions[5:17]])
    store.meta('dataset', {'version': versions[17]})
    for i, state in enumerate(('active', 'probation', 'qualified')):
        store.candidate({'id': state, 'state': state, 'dataset_version': versions[i]})
    unknown = directory / 'operator.parquet'; unknown.write_text('keep')
    linked = directory / ('f' * 64 + '.parquet'); linked.symlink_to(unknown)
    result = store.prune_research_evidence(tmp_path / 'data/lab')
    assert result['deleted_dataset_bytes'] == 14
    for version in versions[:3] + versions[5:]: assert (directory / (version + '.parquet')).exists()
    for version in versions[3:5]: assert not (directory / (version + '.parquet')).exists()
    assert unknown.exists() and linked.is_symlink()


def test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(tmp_path):
    store = store_at(tmp_path)
    store.candidate({'id': 'q', 'state': 'qualified'})
    for i in range(120):
        store.candidate({'id': str(i), 'state': 'rejected'})
        store.meta('shadow:' + str(i), {'closed_pnl': [1]})
    assert any(r['id'] == 'q' for r in store.candidates())
    store.prune_research_evidence(tmp_path / 'data/lab')
    assert len(store.meta('research_evidence_history')) <= 100


def test_malformed_dataset_refs_and_pins_keep_archives(tmp_path):
    store = store_at(tmp_path)
    directory = tmp_path / 'data/lab/datasets'; directory.mkdir(parents=True)
    archive = directory / ('a' * 64 + '.parquet'); archive.write_text('retain')
    store.meta('dataset_history', [{'version': ['invalid']}])
    assert store.prune_research_evidence(tmp_path / 'data/lab')['errors'] == ['dataset_reference_invalid']
    assert archive.exists()
    store.meta('dataset_history', [])
    (directory / '.pin').touch()
    assert store.prune_research_evidence(tmp_path / 'data/lab')['deleted_dataset_bytes'] == 0
    assert archive.exists()
