import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from xauusd.retention import compact_raw_archive, retention_plan, apply_retention


def archive(tmp_path, pages):
    directory = tmp_path / 'data/raw/ctrader/XAUUSD/M1'
    directory.mkdir(parents=True)
    for name, bars in pages.items():
        (directory / name).write_text(json.dumps({'digits': 2, 'symbol': 'XAUUSD', 'timeframe': 'M1', 'bars': bars}))
    return SimpleNamespace(raw_archive_dir=directory, raw_archive_pages=lambda: [(0, 10, p) for p in sorted(directory.glob('*.json'))])


def test_overlaps_need_exact_content_and_preserve_coverage(tmp_path):
    a, b, changed = {'t': 1, 'close': 3}, {'t': 2, 'close': 4}, {'t': 1, 'close': 5}
    store = archive(tmp_path, {'0_2_a.json': [a, b], '0_2_b.json': [a, b], '0_2_c.json': [changed]})
    plan = compact_raw_archive(store)
    assert [Path(f['path']).name for f in plan['files']] == ['0_2_a.json']
    assert len(list(store.raw_archive_dir.glob('*.json'))) == 3
    applied = compact_raw_archive(store, apply=True)
    assert applied['deleted_bytes'] > 0
    assert (store.raw_archive_dir / '0_2_c.json').exists()


def test_symlink_and_different_digits_never_removed(tmp_path):
    store = archive(tmp_path, {'0_1_a.json': [{'t': 1}], '0_1_b.json': [{'t': 1}]})
    p = store.raw_archive_dir / '0_1_b.json'
    payload = json.loads(p.read_text()); payload['digits'] = 3; p.write_text(json.dumps(payload))
    (store.raw_archive_dir / '0_1_c.json').symlink_to(store.raw_archive_dir / '0_1_a.json')
    assert compact_raw_archive(store)['files'] == []


def test_completed_logs_only_and_pins(tmp_path):
    root = tmp_path / 'data/lab/workspaces'
    for name in ['done', 'running', 'pinned']:
        job = root / name; job.mkdir(parents=True)
        (job / 'stdout.log').write_text('verbose')
        if name != 'running':
            (job / 'completion.json').write_text(json.dumps({'status': 'completed', 'completed_at': '2020-01-01T00:00:00+00:00'}))
        if name == 'pinned': (job / '.pin').touch()
    plan = retention_plan(tmp_path, now=datetime(2026, 10, 21, tzinfo=timezone.utc))
    assert [Path(f['path']).parent.name for f in plan['files']] == ['done']
    apply_retention(tmp_path, now=datetime(2026, 10, 21, tzinfo=timezone.utc))
    assert (root / 'running/stdout.log').exists()
    assert (root / 'pinned/stdout.log').exists()
    assert (root / 'done/completion.json').exists()


def test_verified_backup_retains_newest_two_and_unknown_files(tmp_path):
    import gzip
    import hashlib
    root = tmp_path / 'backups/tournament'
    for day in range(1, 5):
        directory = root / f'2020010{day}T000000Z'; directory.mkdir(parents=True)
        compressed = gzip.compress(b'{"experiments":[],"experiment_events":[],"champion_history":[]}')
        (directory / 'registry.json.gz').write_bytes(compressed)
        (directory / 'manifest.json').write_text(json.dumps({
            'created_at': f'2020-01-0{day}T00:00:00+00:00',
            'registry_sha256': hashlib.sha256(compressed).hexdigest(),
        }))
    unknown = root / '20200101T000000Z/operator.txt'; unknown.write_text('keep')
    plan = retention_plan(tmp_path)
    assert {Path(f['path']).parent.name for f in plan['files']} == {'20200102T000000Z'}
    apply_retention(tmp_path)
    assert unknown.exists()
    assert (root / '20200104T000000Z/registry.json.gz').exists()


def test_compaction_preserves_rebuild_revision_winner(tmp_path):
    import pandas as pd
    from xauusd.data import HistoricalDataStore, DataConfig
    store = HistoricalDataStore(DataConfig(raw_dir=tmp_path / 'data/raw', processed_dir=tmp_path / 'processed'))
    directory = store.raw_archive_dir; directory.mkdir(parents=True)
    original = {'utcTimestampInMinutes': 28000000, 'low': 120000000, 'deltaOpen': 1000,
                'deltaClose': 1500, 'deltaHigh': 2000, 'volume': 10}
    revised = {**original, 'low': 130000000}
    extra = {**original, 'utcTimestampInMinutes': 28000001}
    for name, bars in [('28000000_28000001_a.json', [original, extra]), ('28000000_28000001_b.json', [revised]), ('28000000_28000001_c.json', [original])]:
        (directory / name).write_text(json.dumps({'source': 'ctrader-open-api', 'digits': 2, 'symbol': 'XAUUSD', 'timeframe': 'M1', 'bars': bars}))
    cutoff = pd.Timestamp(28000000 * 60, unit='s', tz='UTC')
    store.rebuild_from_raw(cutoff=cutoff, chunk_pages=1)
    before = store.read()
    compact_raw_archive(store, apply=True)
    store.rebuild_from_raw(cutoff=cutoff, chunk_pages=1)
    pd.testing.assert_frame_equal(before, store.read())


def test_completed_workspace_reclaims_training_and_scripts_but_keeps_memory(tmp_path):
    workspace = tmp_path / 'data/lab/workspaces/completed'
    workspace.mkdir(parents=True)
    (workspace / 'completion.json').write_text(json.dumps({'status': 'completed', 'completed_at': '2020-01-01T00:00:00+00:00'}))
    for name in ['train.parquet', 'research.py', 'proposal.json']:
        (workspace / name).write_bytes(b'generated')
    (workspace / 'nested').mkdir(); (workspace / 'nested/result.csv').write_text('data')
    memory = tmp_path / 'data/lab/memory.json'; memory.write_text('compact conclusion')
    apply_retention(tmp_path)
    assert not (workspace / 'train.parquet').exists()
    assert not (workspace / 'research.py').exists()
    assert not (workspace / 'nested/result.csv').exists()
    assert memory.exists()
    assert (workspace / 'completion.json').exists()


def test_completed_workspace_with_nested_symlink_retained(tmp_path):
    workspace = tmp_path / 'data/lab/workspaces/completed'
    workspace.mkdir(parents=True)
    (workspace / 'completion.json').write_text(json.dumps({'status': 'completed', 'completed_at': '2020-01-01T00:00:00+00:00'}))
    (workspace / 'train.parquet').write_text('training')
    outside = tmp_path / 'state.sqlite3'; outside.write_text('authoritative')
    (workspace / 'linked-state').symlink_to(outside)
    assert retention_plan(tmp_path)['files'] == []
    apply_retention(tmp_path)
    assert (workspace / 'train.parquet').exists()
    assert outside.read_text() == 'authoritative'


def test_invalid_newest_backup_contents_do_not_displace_valid_recovery(tmp_path):
    import gzip
    import hashlib
    root = tmp_path / 'backups/tournament'
    for day in range(1, 5):
        directory = root / f'2020010{day}T000000Z'; directory.mkdir(parents=True)
        valid = {'experiments': [], 'experiment_events': [], 'champion_history': []}
        content = json.dumps(valid).encode() if day <= 2 else (b'not json' if day == 3 else b'[]')
        compressed = gzip.compress(content)
        (directory / 'registry.json.gz').write_bytes(compressed)
        (directory / 'manifest.json').write_text(json.dumps({'created_at': f'2020-01-0{day}T00:00:00+00:00', 'registry_sha256': hashlib.sha256(compressed).hexdigest()}))
    assert retention_plan(tmp_path)['files'] == []


def test_malformed_manifest_and_completion_are_retained(tmp_path):
    backup = tmp_path / 'backups/tournament/bad'; backup.mkdir(parents=True)
    (backup / 'manifest.json').write_text('[]')
    workspace = tmp_path / 'data/lab/workspaces/bad'; workspace.mkdir(parents=True)
    (workspace / 'completion.json').write_text('[]')
    (workspace / 'train.parquet').write_text('keep')
    assert retention_plan(tmp_path)['files'] == []


def test_registry_validation_streams_rows_and_rejects_non_array_tables(tmp_path):
    import gzip
    from xauusd.retention import _registry_schema_valid
    path = tmp_path / 'registry.json.gz'
    valid = {'experiments': [{'id': i, 'notes': 'x' * 70000} for i in range(3)],
             'experiment_events': [], 'champion_history': []}
    path.write_bytes(gzip.compress(json.dumps(valid).encode()))
    assert _registry_schema_valid(path)
    valid['experiments'] = {}
    path.write_bytes(gzip.compress(json.dumps(valid).encode()))
    try:
        result = _registry_schema_valid(path)
    except ValueError:
        result = False
    assert not result


def test_compress_raw_archive_exact_bytes_and_dry_run(tmp_path):
    import gzip
    from xauusd.retention import compress_raw_archive
    store = archive(tmp_path, {'0_1_a.json': [{'t': 1, 'notes': 'repeat' * 500}]})
    path = store.raw_archive_dir / '0_1_a.json'; original = path.read_bytes()
    dry = compress_raw_archive(store)
    assert dry['files'] == 1 and dry['candidate_bytes'] == len(original)
    assert path.exists() and not path.with_suffix('.json.gz').exists()
    applied = compress_raw_archive(store, apply=True)
    assert applied['saved_bytes'] > 0 and not path.exists()
    assert gzip.decompress(path.with_suffix('.json.gz').read_bytes()) == original
    assert applied['before_bytes'] - applied['after_bytes'] == applied['saved_bytes']


def test_compress_raw_archive_retains_corrupt_targets_pins_and_symlinks(tmp_path):
    from xauusd.retention import compress_raw_archive
    store = archive(tmp_path, {'0_1_a.json': [{'t': 1}], '0_1_b.json': [{'t': 1}], '0_1_c.json': [{'t': 1}]})
    directory = store.raw_archive_dir
    (directory / '0_1_a.json.gz').write_bytes(b'bad gzip')
    outside = tmp_path / 'outside'; outside.write_text('unchanged')
    (directory / '0_1_b.json.gz').symlink_to(outside)
    (directory / '0_1_c.json').unlink(); (directory / '0_1_c.json').symlink_to(outside)
    result = compress_raw_archive(store, apply=True)
    assert (directory / '0_1_a.json').exists()
    assert (directory / '0_1_b.json').exists()
    assert (directory / '0_1_c.json').is_symlink()
    assert outside.read_text() == 'unchanged'
    assert result['saved_bytes'] == 0
    (directory / '.pin').touch()
    assert compress_raw_archive(store, apply=True)['files'] == 0


def test_compress_raw_archive_changed_source_preserved(tmp_path, monkeypatch):
    from xauusd.retention import compress_raw_archive
    import xauusd.retention as retention
    store = archive(tmp_path, {'0_1_a.json': [{'t': 1, 'data': 'x' * 1000}]})
    path = store.raw_archive_dir / '0_1_a.json'
    original_writer = retention.atomic_write_bytes
    def changed(target, payload, **kwargs):
        result = original_writer(target, payload, **kwargs)
        if str(target).endswith('.json.gz'): path.write_text('changed')
        return result
    monkeypatch.setattr(retention, 'atomic_write_bytes', changed)
    result = compress_raw_archive(store, apply=True)
    assert path.read_text() == 'changed'
    assert 'artifact_changed' in result['errors']
    assert not path.with_name(path.name + '.gz').exists()


def test_compress_existing_exact_target_and_deterministic_bytes(tmp_path):
    import gzip
    from xauusd.retention import compress_raw_archive
    store = archive(tmp_path, {'0_1_a.json': [{'t': 1, 'notes': 'same' * 500}], '0_1_b.json': [{'t': 1, 'notes': 'same' * 500}]})
    directory = store.raw_archive_dir
    a = directory / '0_1_a.json'; data = a.read_bytes()
    existing = gzip.compress(data, compresslevel=1, mtime=0)
    (directory / '0_1_a.json.gz').write_bytes(existing)
    result = compress_raw_archive(store, apply=True)
    assert result['compressed_files'] == 2
    assert not a.exists()
    assert (directory / '0_1_b.json.gz').read_bytes() == existing
    assert result['before_bytes'] - result['after_bytes'] == result['saved_bytes']


def test_compaction_reads_compressed_raw_pages(tmp_path):
    import gzip
    store = archive(tmp_path, {'0_1_a.json': [{'t': 1}], '0_1_b.json': [{'t': 1}]})
    directory = store.raw_archive_dir
    for path in directory.glob('*.json'):
        path.with_name(path.name + '.gz').write_bytes(gzip.compress(path.read_bytes(), mtime=0))
        path.unlink()
    store.raw_archive_pages = lambda: [(0, 1, p) for p in sorted(directory.glob('*.json.gz'))]
    result = compact_raw_archive(store, apply=True)
    assert result['deleted_bytes'] > 0
    assert (directory / '0_1_b.json.gz').exists()
    assert not (directory / '0_1_a.json.gz').exists()


def _local_backups(tmp_path, count):
    import gzip
    import hashlib
    import sqlite3
    source = tmp_path / 'snapshot.db'
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE retained(value TEXT)')
        db.execute("INSERT INTO retained VALUES ('state')")
    data = source.read_bytes()
    root = tmp_path / 'backups/local-state'
    for day in range(1, count + 1):
        directory = root / f'202001{day:02d}T000000Z'; directory.mkdir(parents=True)
        archive_bytes = gzip.compress(data)
        (directory / 'state.db.gz').write_bytes(archive_bytes)
        (directory / 'manifest.json').write_text(json.dumps({'run_id': directory.name,
            'created_at': f'2020-01-{day:02d}T00:00:00+00:00', 'archive': 'state.db.gz',
            'archive_bytes': len(archive_bytes), 'sha256': hashlib.sha256(data).hexdigest(),
            'format': 'sqlite-gzip-json-v1', 'integrity': 'ok'}))
    return root


def test_local_backup_retention_preserves_newest_fourteen(tmp_path):
    root = _local_backups(tmp_path, 16)
    plan = retention_plan(tmp_path)
    assert plan['verified_local_state_backups'] == 16
    assert {Path(f['path']).parent.name for f in plan['files']} == {'20200101T000000Z', '20200102T000000Z'}
    assert all(f['reason'] == 'obsolete_verified_local_state_backup' for f in plan['files'])
    apply_retention(tmp_path)
    assert (root / '20200103T000000Z/state.db.gz').exists()
    assert (root / '20200116T000000Z/state.db.gz').exists()
    assert not (root / '20200101T000000Z/state.db.gz').exists()


def test_invalid_newest_local_backups_do_not_displace_good_copies(tmp_path):
    import gzip
    import hashlib
    root = _local_backups(tmp_path, 16)
    for day in (15, 16):
        directory = root / f'202001{day:02d}T000000Z'
        # Even a hash-correct gzip payload must pass SQLite quick_check.
        data = b'not a database'
        compressed = gzip.compress(data)
        (directory / 'state.db.gz').write_bytes(compressed)
        manifest = json.loads((directory / 'manifest.json').read_text())
        manifest.update(sha256=hashlib.sha256(data).hexdigest(), archive_bytes=len(compressed))
        (directory / 'manifest.json').write_text(json.dumps(manifest))
    plan = retention_plan(tmp_path)
    assert plan['files'] == []
    assert plan['verified_local_state_backups'] == 14
