"""Conservative generated-artifact retention; authoritative state is never a target."""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .atomic import atomic_write_json, atomic_write_bytes, file_lock, _fsync_directory

POLICY = {'completed_log_days': 7, 'tournament_backup_days': 30,
          'verified_tournament_backups_preserved': 2,
          'verified_local_state_backups_preserved': 14,
          'raw_archives': 'exact canonical bar content in later retained rebuild pages only'}


def _now(now):
    value = now or datetime.now(timezone.utc)
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


def _safe(path: Path, root: Path) -> bool:
    """Reject symlinks at every component, including the configured root."""
    path, root = path.absolute(), root.absolute()
    if not path.is_relative_to(root): return False
    return not any(p.is_symlink() for p in [path, *path.parents])


def _pinned(path: Path, root: Path) -> bool:
    for parent in [path if path.is_dir() else path.parent, *path.parents]:
        if any((parent / name).exists() for name in ('.pin', '.pinned', '.inflight')): return True
        if parent == root: break
    return False


def _record(path, reason):
    stat = path.stat()
    return {'path': str(path), 'bytes': stat.st_size, 'reason': reason,
            'mtime_ns': stat.st_mtime_ns, 'inode': stat.st_ino}


def _delete(files, root):
    deleted, errors = 0, []
    for entry in files:
        path = Path(entry['path'])
        try:
            if not _safe(path, root) or _pinned(path, root): continue
            stat = path.stat()
            if (stat.st_ino, stat.st_mtime_ns, stat.st_size) != (entry['inode'], entry['mtime_ns'], entry['bytes']):
                errors.append('artifact_changed'); continue
            path.unlink(); _fsync_directory(path.parent); deleted += entry['bytes']
        except OSError:
            errors.append('artifact_delete_failed')
    return deleted, sorted(set(errors))


def _registry_schema_valid(registry):
    """Validate logical snapshot JSON in bounded memory (8 MiB per row).

    Snapshots contain three arrays of row objects. Oversized or malformed rows
    make a backup ineligible; they never justify removal of another backup.
    """
    decoder = json.JSONDecoder()
    limit = 8 * 1024 * 1024
    with gzip.open(registry, 'rt', encoding='utf-8') as stream:
        buffer = ''
        eof = False

        def fill():
            nonlocal buffer, eof
            block = stream.read(65536)
            if not block: eof = True
            buffer += block
            if len(buffer) > limit: raise ValueError('snapshot_row_too_large')

        def token():
            nonlocal buffer
            buffer = buffer.lstrip()
            while not buffer and not eof:
                fill(); buffer = buffer.lstrip()
            return buffer[:1]

        def take(character):
            nonlocal buffer
            if token() != character: raise ValueError('snapshot_invalid')
            buffer = buffer[1:]

        def value():
            nonlocal buffer
            token()
            while True:
                try:
                    result, end = decoder.raw_decode(buffer)
                    buffer = buffer[end:]
                    return result
                except json.JSONDecodeError:
                    if eof: raise
                    fill()

        take('{'); keys = set()
        while True:
            key = value()
            if not isinstance(key, str) or key in keys: return False
            keys.add(key)
            if key not in {'experiments', 'experiment_events', 'champion_history'}: return False
            take(':'); take('[')
            if token() != ']':
                while True:
                    # Decode only complete object rows; scalars are not snapshots.
                    if token() != '{' or not isinstance(value(), dict): return False
                    if token() == ']': break
                    take(',')
            take(']')
            if token() == '}': break
            take(',')
        take('}')
        if token(): return False
        return keys == {'experiments', 'experiment_events', 'champion_history'}


def _verified_backup(directory, root):
    try:
        manifest_path = directory / 'manifest.json'
        if not _safe(manifest_path, root) or _pinned(directory, root): return None
        manifest = json.loads(manifest_path.read_text())
        if not isinstance(manifest, dict): return None
        registry = directory / 'registry.json.gz'
        if not _safe(registry, root) or not registry.is_file(): return None
        digest = hashlib.sha256()
        with registry.open('rb') as stream:
            while block := stream.read(1024 * 1024): digest.update(block)
        if not _registry_schema_valid(registry): return None
        if digest.hexdigest() != manifest['registry_sha256']: return None
        created = datetime.fromisoformat(manifest['created_at'])
        if created.tzinfo is None: return None
        expected = {'manifest.json', 'registry.json.gz'}
        auxiliary = manifest.get('auxiliary_files', [])
        checkpoints = manifest.get('scaling_checkpoints', [])
        if not isinstance(auxiliary, list) or not isinstance(checkpoints, list): return None
        for entry in auxiliary + checkpoints:
            if not isinstance(entry, dict): return None
            target = directory / entry['backup']
            if not _safe(target, directory) or not target.is_file(): return None
            if hashlib.sha256(target.read_bytes()).hexdigest() != entry['sha256']: return None
            expected.add(str(target.relative_to(directory)))
        # Unknown files (including old SQLite state) retain the whole backup.
        actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
        if actual != expected: return None
        return created
    except (OSError, ValueError, KeyError, TypeError, EOFError, UnicodeError):
        return None


def _verified_local_backup(directory, root):
    """Stream a local backup into private temporary storage; never restore it."""
    from .state_backup import _quick_check
    try:
        manifest_path = directory / 'manifest.json'
        archive = directory / 'state.db.gz'
        if not all(_safe(p, root) for p in (directory, manifest_path, archive)) or _pinned(directory, root): return None
        if {p.name for p in directory.iterdir()} != {'manifest.json', 'state.db.gz'}: return None
        manifest = json.loads(manifest_path.read_text())
        if not isinstance(manifest, dict) or manifest.get('format') != 'sqlite-gzip-json-v1' or manifest.get('integrity') != 'ok' or manifest.get('archive') != 'state.db.gz': return None
        if not archive.is_file() or archive.stat().st_size != manifest.get('archive_bytes'): return None
        created = datetime.fromisoformat(manifest['created_at'])
        if created.tzinfo is None: return None
        before = _record(archive, 'local_state_backup')
        digest = hashlib.sha256(); size = 0
        # One MiB buffers; oversized snapshots are retained, never deletion evidence.
        with tempfile.TemporaryDirectory(prefix='xauusd-backup-verify-') as temporary:
            extracted = Path(temporary) / 'snapshot.db'
            with gzip.open(archive, 'rb') as source, extracted.open('wb') as target:
                while block := source.read(1024 * 1024):
                    size += len(block)
                    if size > 1024 * 1024 * 1024: return None
                    digest.update(block); target.write(block)
            if digest.hexdigest() != manifest.get('sha256') or _quick_check(extracted) != 'ok': return None
        if _record(archive, 'local_state_backup') != before: return None
        return created
    except (OSError, ValueError, KeyError, TypeError, EOFError, sqlite3.DatabaseError):
        return None


def retention_plan(root=Path('.'), now=None):
    root = Path(root).absolute(); clock = _now(now); files = []
    backup_root = root / 'backups/tournament'
    verified = []
    if _safe(backup_root, root) and backup_root.is_dir():
        for directory in sorted(backup_root.iterdir()):
            if _safe(directory, root) and directory.is_dir():
                created = _verified_backup(directory, root)
                if created is not None: verified.append((created, directory))
    for created, directory in sorted(verified, reverse=True)[2:]:
        if clock - created <= timedelta(days=30): continue
        files.extend(_record(p, 'obsolete_verified_tournament_backup') for p in sorted(directory.rglob('*')) if p.is_file())
    local_root = root / 'backups/local-state'
    local_verified = []
    protected_local = set()
    if _safe(local_root, root) and local_root.is_dir():
        latest_path = local_root / 'latest.json'
        try:
            if _safe(latest_path, root):
                latest = json.loads(latest_path.read_text())
                if isinstance(latest, dict) and isinstance(latest.get('run_id'), str):
                    protected_local.add(latest['run_id'])
        except (OSError, ValueError, TypeError): pass
        for directory in sorted(local_root.iterdir()):
            if _safe(directory, root) and directory.is_dir():
                created = _verified_local_backup(directory, root)
                if created is not None: local_verified.append((created, directory))
    for _, directory in sorted(local_verified, reverse=True)[14:]:
        if directory.name in protected_local: continue
        files.extend(_record(p, 'obsolete_verified_local_state_backup') for p in sorted(directory.iterdir()) if p.is_file())
    for relative in ('data/lab/workspaces', 'data/codex/workspaces'):
        workspace_root = root / relative
        if not _safe(workspace_root, root) or not workspace_root.is_dir(): continue
        for workspace in sorted(workspace_root.iterdir()):
            if not _safe(workspace, root) or not workspace.is_dir() or _pinned(workspace, root): continue
            marker = workspace / 'completion.json'
            try:
                if not _safe(marker, root): continue
                completed = json.loads(marker.read_text())
                if not isinstance(completed, dict): continue
                if completed.get('status') not in ('completed', 'failed', 'interrupted'): continue
                at = datetime.fromisoformat(completed['completed_at'])
                if at.tzinfo is None or clock - at <= timedelta(days=7): continue
            except (OSError, ValueError, KeyError, TypeError): continue
            # The whole completed scratch workspace is generated, not just logs.
            # Any symlink or pin in the tree makes the entire workspace ineligible.
            generated = list(workspace.rglob('*'))
            if any(not _safe(path, root) or path.name in ('.pin', '.pinned', '.inflight') for path in generated): continue
            for path in sorted(generated):
                if path.is_file() and path != marker:
                    files.append(_record(path, 'expired_completed_workspace_artifact'))
    usage = os.statvfs(root)
    return {'files': files, 'bytes_reclaimable': sum(f['bytes'] for f in files),
            'recorded_at': clock.isoformat(), 'policy': POLICY,
            'disk': {'total_bytes': usage.f_blocks * usage.f_frsize, 'free_bytes': usage.f_bavail * usage.f_frsize},
            'verified_tournament_backups': len(verified), 'verified_local_state_backups': len(local_verified), 'deleted_bytes': 0, 'errors': []}


def apply_retention(root=Path('.'), now=None):
    root = Path(root).absolute()
    with file_lock(root / 'reports/retention-status.json'):
        plan = retention_plan(root, now)
        # Persist intent before deletion and outcome afterwards.
        atomic_write_json(root / 'reports/retention-status.json', {**plan, 'state': 'applying'})
        plan['deleted_bytes'], plan['errors'] = _delete(plan['files'], root)
        plan['state'] = 'completed' if not plan['errors'] else 'partial'
        atomic_write_json(root / 'reports/retention-status.json', plan)
        return plan


def compact_raw_archive(store, apply=False):
    """Bounded-memory exact dedup. Each removed record exists in a retained page.

    Canonical JSON strings, rather than hashes alone, are indexed on disk. Malformed,
    pinned and symlinked pages are retained. No interpretation of filename ranges is
    used. Downloader appends new filenames; changed files fail the deletion check.
    """
    directory = Path(store.raw_archive_dir).absolute()
    plan = {'files': [], 'bytes_reclaimable': 0, 'deleted_bytes': 0, 'errors': [],
            'pages': 0, 'policy': POLICY, 'recorded_at': _now(None).isoformat()}
    if not _safe(directory, directory) or not directory.is_dir(): return plan
    with file_lock(directory / '.compaction'):
        # Index lives on the same volume; never retain it after the scan.
        with tempfile.TemporaryDirectory(prefix='.compaction-', dir=directory) as temporary:
            connection = sqlite3.connect(str(Path(temporary) / 'records.sqlite3'))
            try:
                connection.execute('PRAGMA journal_mode=OFF')
                connection.execute('PRAGMA synchronous=OFF')
                connection.execute('PRAGMA cache_size=-16384')
                connection.execute('CREATE TABLE records (content TEXT PRIMARY KEY) WITHOUT ROWID')
                paths = [Path(p) for _, _, p in store.raw_archive_pages()]
                # Only later retained pages may prove redundancy: retaining an older
                # copy across an intervening revision would change rebuild winners.
                paths = [p for p in paths if _safe(p, directory) and p.is_file() and not _pinned(p, directory)]
                paths.reverse()
                survivors = []
                for path in paths:
                    before = _record(path, 'content_exact_raw_duplicate')
                    try:
                        with gzip.open(path, 'rt') if path.suffix == '.gz' else path.open('r') as stream:
                            payload = json.load(stream)
                        bars = payload['bars']
                        if not isinstance(bars, list) or not bars or not all(isinstance(b, dict) for b in bars): continue
                        metadata = {k: payload.get(k) for k in ('source', 'symbol', 'symbol_id', 'digits', 'timeframe')}
                        records = [(json.dumps([metadata, bar], sort_keys=True, separators=(',', ':'), allow_nan=False),) for bar in bars]
                    except (OSError, ValueError, KeyError, TypeError, EOFError):
                        plan['errors'].append('raw_page_invalid'); continue
                    if before != _record(path, 'content_exact_raw_duplicate'):
                        plan['errors'].append('artifact_changed'); continue
                    plan['pages'] += 1
                    redundant = all(connection.execute('SELECT 1 FROM records WHERE content=?', record).fetchone() for record in records)
                    if redundant:
                        plan['files'].append(before)
                    else:
                        survivors.append(before)
                        connection.executemany('INSERT OR IGNORE INTO records VALUES (?)', records)
                        connection.commit()
                plan['bytes_reclaimable'] = sum(f['bytes'] for f in plan['files'])
                plan['errors'] = sorted(set(plan['errors']))
                if apply:
                    for survivor in survivors:
                        path = Path(survivor['path'])
                        if not _safe(path, directory) or not path.is_file() or survivor != _record(path, survivor['reason']):
                            plan['errors'] = sorted(set(plan['errors'] + ['surviving_archive_changed']))
                            return plan
                    audit = directory / '.compaction-audit.json'
                    atomic_write_json(audit, {**plan, 'state': 'applying'})
                    plan['deleted_bytes'], errors = _delete(plan['files'], directory)
                    plan['errors'] = sorted(set(plan['errors'] + errors))
                    atomic_write_json(audit, {**plan, 'state': 'completed' if not plan['errors'] else 'partial'})
            finally:
                connection.close()
    return plan


def compress_raw_archive(store, apply=False):
    """Losslessly compress ordinary raw pages; unlink only after durable verification.

    Run only after readers understand .json.gz. No broker calls or normalized
    state changes. A bounded whole-run intent/outcome audit supports recovery:
    interrupted runs leave either the original or a verified durable gzip copy.
    """
    directory = Path(store.raw_archive_dir).absolute()
    result = {'files': 0, 'compressed_files': 0, 'candidate_bytes': 0,
              'before_bytes': 0, 'after_bytes': None, 'saved_bytes': 0,
              'errors': [], 'recorded_at': _now(None).isoformat()}
    audit = directory / '.compression-audit.json'
    if not _safe(directory, directory) or not directory.is_dir(): return result
    if not all(_safe(p, directory) for p in (audit, directory / '.compression.lock')):
        result['errors'] = ['unsafe_archive_path']; return result
    with file_lock(directory / '.compression'):
        pages = [Path(p) for _, _, p in store.raw_archive_pages()]
        if len(pages) > 50000:
            result['errors'] = ['archive_page_limit']; return result
        entries = []
        for path in pages:
            if path.suffix != '.json' or not _safe(path, directory) or not path.is_file() or _pinned(path, directory): continue
            entry = _record(path, 'lossless_raw_compression')
            target = path.with_name(path.name + '.gz')
            target_bytes = target.stat().st_size if _safe(target, directory) and target.is_file() else 0
            entries.append({**entry, 'target_bytes': target_bytes, 'outcome': 'pending'})
        result['files'] = len(entries)
        result['candidate_bytes'] = sum(e['bytes'] for e in entries)
        result['before_bytes'] = sum(e['bytes'] + e['target_bytes'] for e in entries)
        if not apply: return result
        result['after_bytes'] = result['before_bytes']
        atomic_write_json(audit, {**result, 'state': 'applying', 'entries': entries})
        for entry in entries:
            path = Path(entry['path']); target = path.with_name(path.name + '.gz')
            try:
                if not _safe(path, directory) or _pinned(path, directory) or not _safe(target, directory) or _pinned(target, directory):
                    entry['outcome'] = 'unsafe_or_pinned'; continue
                if entry['bytes'] > 16 * 1024 * 1024:
                    entry['outcome'] = 'raw_page_size_limit'; result['errors'].append(entry['outcome']); continue
                expected = {key: entry[key] for key in ('path', 'bytes', 'reason', 'mtime_ns', 'inode')}
                if _record(path, entry['reason']) != expected:
                    entry['outcome'] = 'artifact_changed'; result['errors'].append(entry['outcome']); continue
                with path.open('rb') as source:
                    data = source.read(16 * 1024 * 1024 + 1)
                if len(data) != entry['bytes'] or _record(path, entry['reason']) != expected:
                    entry['outcome'] = 'artifact_changed'; result['errors'].append(entry['outcome']); continue
                existed = target.exists()
                if existed:
                    if not target.is_file() or target.stat().st_size > 20 * 1024 * 1024:
                        entry['outcome'] = 'compressed_target_invalid'; result['errors'].append(entry['outcome']); continue
                    # Read at most original-size+1, including gzip bombs.
                    with gzip.open(target, 'rb') as stream:
                        equivalent = stream.read(len(data) + 1) == data
                    if not equivalent:
                        entry['outcome'] = 'compressed_target_differs'; result['errors'].append(entry['outcome']); continue
                else:
                    compressed = gzip.compress(data, compresslevel=1, mtime=0)
                    if len(compressed) >= len(data):
                        entry['outcome'] = 'not_smaller'; continue
                    atomic_write_bytes(target, compressed)
                # Verify the actual durable target, not just the in-memory encoder.
                target_snapshot = _record(target, 'compressed_target')
                with gzip.open(target, 'rb') as stream:
                    verified = stream.read(len(data) + 1) == data
                if not verified:
                    entry['outcome'] = 'compressed_verification_failed'; result['errors'].append(entry['outcome']); continue
                with path.open('rb') as source:
                    current_data = source.read(16 * 1024 * 1024 + 1)
                if not _safe(path, directory) or not _safe(target, directory) or _pinned(path, directory) or _record(path, entry['reason']) != expected or current_data != data:
                    entry['outcome'] = 'artifact_changed'; result['errors'].append(entry['outcome'])
                    # An old compressed copy would sort after the changed source in
                    # rebuild order. Remove only our unchanged newly-created copy.
                    if not existed and _safe(target, directory) and not _pinned(target, directory) and _record(target, 'compressed_target') == target_snapshot:
                        target.unlink(); _fsync_directory(directory)
                    continue
                if _record(target, 'compressed_target') != target_snapshot:
                    entry['outcome'] = 'compressed_target_changed'; result['errors'].append(entry['outcome']); continue
                target_size = target.stat().st_size
                path.unlink(); _fsync_directory(directory)
                saving = len(data) if existed else len(data) - target_size
                result['saved_bytes'] += saving; result['after_bytes'] -= saving
                result['compressed_files'] += 1
                entry['outcome'] = 'compressed'; entry['compressed_bytes'] = target_size
            except (OSError, EOFError, ValueError):
                entry['outcome'] = 'compression_failed'; result['errors'].append(entry['outcome'])
        result['errors'] = sorted(set(result['errors']))
        atomic_write_json(audit, {**result, 'state': 'completed' if not result['errors'] else 'partial', 'entries': entries})
    return result


def prune_lab_dataset_archives(lab_root, preserved_versions):
    """Remove only inactive generated hash-named archives, never current dataset."""
    import re
    root = Path(lab_root).absolute()
    directory = root / 'datasets'
    result = {'deleted_dataset_bytes': 0, 'deleted_datasets': 0, 'errors': []}
    if not _safe(directory, root) or not directory.is_dir() or _pinned(directory, root): return result
    if any(not isinstance(v, str) or not re.fullmatch('[a-f0-9]{64}', v) for v in preserved_versions):
        result['errors'] = ['dataset_reference_invalid']; return result
    files = []
    for path in sorted(directory.iterdir()):
        if not _safe(path, root) or not path.is_file() or _pinned(path, root): continue
        if path.suffix != '.parquet' or not re.fullmatch('[a-f0-9]{64}', path.stem): continue
        if path.stem not in preserved_versions: files.append(_record(path, 'inactive_lab_dataset_archive'))
    audit = directory / '.retention-audit.json'
    if not _safe(audit, root):
        result['errors'] = ['unsafe_dataset_audit']; return result
    atomic_write_json(audit, {'state': 'applying', 'files': files, 'preserved_versions': sorted(preserved_versions)})
    result['deleted_dataset_bytes'], result['errors'] = _delete(files, root)
    result['deleted_datasets'] = sum(not Path(row['path']).exists() for row in files)
    atomic_write_json(audit, {**result, 'state': 'completed' if not result['errors'] else 'partial', 'files': files})
    return result
