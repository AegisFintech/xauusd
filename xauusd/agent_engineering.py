"""Tested application releases with immutable baselines and recoverable installation.

This manager never starts trading, edits credentials, or restarts its own process.
A supervisor outside the agent must restart and call ``verify_pending``; until
then another release is refused. Protected files and the original tests remain
immutable. Software test success conveys no trading qualification.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
from pathlib import Path
import signal
import secrets
import subprocess
import tempfile
import tomllib
import time
import uuid

from .atomic import atomic_write_bytes, atomic_write_json, file_lock
from .bits_jobs import SecretFilter

MAX_FILES = 1500
MAX_BYTES = 40 * 1024 * 1024
MAX_FILE_BYTES = 2 * 1024 * 1024
TEST_TIMEOUT_SECONDS = 1200
TEST_OUTPUT_BYTES = 2 * 1024 * 1024
TEST_WORKSPACE_BYTES = 256 * 1024 * 1024
# Execution, evidence, credential, storage, permission and deployment controls are
# operator-maintained. Their dependencies are protected too, not just the gates.
PROTECTED = frozenset('''__init__ atomic paper_trading core local_state oauth ctrader_auth
ctrader_demo demo_execution demo_runner automation agent_loop bits bits_runner
bits_jobs bits_capabilities bits_memory session_reset state_backup session_calendar
engine engine_loop experiment_registry lab lab_strategy lab_execution lab_store lab_codex lab_tools
agent_engineering agent_release_worker agent_advisor agent_tools agent_remote data live_feed quotes validation
operations agent_status autonomous_harness'''.split())
ROOT_FILES = frozenset({'AGENTS.md', 'README.md', 'pyproject.toml', '.gitignore', '.env.example', '.dockerignore', 'Dockerfile', 'docker-compose.yml'})


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _safe(path):
    return not any(p.is_symlink() for p in (path, *path.parents))


def _eligible(path):
    parts = path.parts
    if '__pycache__' in parts or '.pytest_cache' in parts: return False
    if len(parts) == 1: return path.name in ROOT_FILES
    if parts[0] == 'xauusd': return path.suffix in {'.py', '.html', '.css', '.js'}
    if parts[0] == 'tests': return path.suffix in {'.py', '.json', '.csv', '.md', '.txt'}
    if parts[0] == 'docs': return path.suffix in {'.md', '.json'}
    if parts[0] == 'scripts': return path.suffix == '.py'
    if parts[0] == 'deploy': return path.suffix in {'.service', '.timer'}
    return False


def _dependency_only(before, after):
    try:
        left, right = tomllib.loads(before.decode()), tomllib.loads(after.decode())
        for document in (left, right):
            project = document.get('project', {})
            for key in ('dependencies', 'optional-dependencies'):
                value = project.pop(key, None)
                groups = value.values() if isinstance(value, dict) else [value]
                if value is not None and any(not isinstance(group, list) or any(not isinstance(item, str) or len(item) > 500 for item in group) for group in groups):
                    return False
        return left == right
    except (ValueError, UnicodeError, AttributeError, TypeError):
        return False


def _protected(name, protected=PROTECTED):
    path = Path(name)
    return (path.name == 'AGENTS.md' or path.parts[0] in {'deploy', 'scripts'} or
            (len(path.parts) == 1 and path.name != 'README.md') or
            (path.parts[0] == 'xauusd' and path.stem in protected))


class EngineeringManager:
    def __init__(self, project_root: Path, store):
        self.root = Path(project_root).absolute()
        self.store = store
        self.releases = self.root / 'data/lab/releases'
        self.protected = set(PROTECTED)
        # Follow the load-bearing gate/evidence/auth/store dependency closure.
        # Supervisor/UI imports are intentionally not roots: adding a research
        # tool must remain possible without freezing the entire application.
        pending = ['paper_trading', 'lab_strategy', 'lab_execution', 'demo_execution',
                   'ctrader_auth', 'ctrader_demo', 'atomic', 'local_state']
        visited = set()
        while pending:
            name = pending.pop()
            if name in visited: continue
            visited.add(name); self.protected.add(name)
            source = self.root / 'xauusd' / (name + '.py')
            if not source.is_file() or not _safe(source): continue
            for node in ast.walk(ast.parse(source.read_bytes())):
                if isinstance(node, ast.ImportFrom) and node.level == 1:
                    pending.extend([node.module.split('.')[0]] if node.module else [alias.name for alias in node.names])

    def _records(self, root):
        if not _safe(root): raise ValueError('unsafe_path')
        records = {}; total = 0
        candidates = list(root.iterdir())
        for directory in ('xauusd', 'tests', 'docs', 'deploy', 'scripts'):
            base = root / directory
            if base.exists(): candidates.extend(base.rglob('*'))
        for path in sorted(set(candidates)):
            relative = path.relative_to(root)
            if not _eligible(relative): continue
            if not _safe(path): raise ValueError('unsafe_path')
            if not path.is_file(): continue
            if path.stat().st_size > MAX_FILE_BYTES: raise ValueError('snapshot_size_limit')
            content = path.read_bytes(); total += len(content)
            if total > MAX_BYTES or len(records) >= MAX_FILES: raise ValueError('snapshot_size_limit')
            records[relative.as_posix()] = content
        return records

    def _write_journal(self, release):
        atomic_write_json(self.releases / release['id'] / 'journal.json', release, mode=0o600)
        self.store.meta('engineering_pending', release)
        self.store.meta('engineering', {'state': release['state'], 'release_id': release['id'],
                                        'changes': len(release['changes']), 'tests': release['tests']})

    def snapshot(self, workspace: Path) -> dict:
        try:
            workspace = Path(workspace).absolute()
            if not _safe(workspace) or (workspace / 'project').exists(): raise ValueError('snapshot_exists')
            records = self._records(self.root)
            snapshot_id = uuid.uuid4().hex
            baseline = {'id': snapshot_id, 'workspace': str(workspace),
                        'files': {name: _hash(data) for name, data in records.items()}}
            for name, data in records.items():
                atomic_write_bytes(workspace / 'project' / name, data,
                                   mode=0o400 if _protected(name, self.protected) or name.startswith('tests/') else 0o600)
            # Only the opaque ID is writable by the model. Baselines are held in
            # authoritative state, never accepted from its editable workspace.
            atomic_write_json(workspace / 'engineering.json', {'id': snapshot_id})
            self.store.meta('engineering_snapshot:' + snapshot_id, baseline)
            history = (self.store.meta('engineering_snapshots') or []) + [snapshot_id]
            for expired in history[:-8]:
                with self.store.state.transaction() as tx:
                    tx.delete('lab:engineering_snapshot:' + expired)
            self.store.meta('engineering_snapshots', history[-8:])
            return {'ok': True, 'snapshot_id': snapshot_id, 'project': str(workspace / 'project'),
                    'files': len(records), 'protected_modules': sorted(self.protected)}
        except (OSError, ValueError, TypeError) as exc:
            return {'ok': False, 'error_code': 'unsafe_path' if str(exc) == 'unsafe_path' else 'snapshot_failed'}

    def _baseline(self, workspace):
        marker = workspace / 'engineering.json'
        if not _safe(marker) or marker.stat().st_size > 100: raise ValueError('unsafe_path')
        identity = json.loads(marker.read_text()).get('id')
        if not isinstance(identity, str) or len(identity) != 32: raise ValueError('snapshot_unknown')
        baseline = self.store.meta('engineering_snapshot:' + identity)
        if not baseline or baseline['workspace'] != str(workspace): raise ValueError('snapshot_unknown')
        return baseline

    def check(self, workspace: Path) -> dict:
        try:
            workspace = Path(workspace).absolute(); baseline = self._baseline(workspace)
            live = self._records(self.root); proposed = self._records(workspace / 'project')
            hashes = {name: _hash(content) for name, content in live.items()}
            if hashes != baseline['files']: return {'ok': False, 'error_code': 'live_base_changed'}
            changes = []
            for name in sorted(set(proposed) | set(hashes)):
                digest = _hash(proposed[name]) if name in proposed else None
                if hashes.get(name) == digest: continue
                dependency_change = (name == 'pyproject.toml' and name in live and name in proposed
                                     and _dependency_only(live[name], proposed[name]))
                if dependency_change:
                    return {'ok': False, 'error_code': 'dependency_environment_unavailable'}
                if ((_protected(name, self.protected) and not dependency_change) or (name.startswith('tests/') and
                        (name in hashes or not (Path(name).suffix == '.py' and Path(name).name.startswith('test_'))))):
                    return {'ok': False, 'error_code': 'protected_change', 'path': name}
                changes.append({'path': name, 'before': hashes.get(name), 'after': digest})
            if not changes: return {'ok': False, 'error_code': 'no_changes'}
            return {'ok': True, 'snapshot_id': baseline['id'], 'changes': changes,
                    'digest': _hash(json.dumps(changes, sort_keys=True).encode())}
        except (OSError, ValueError, TypeError, KeyError):
            return {'ok': False, 'error_code': 'snapshot_invalid'}

    def _test(self, project):
        from .lab_codex import child_environment
        workspace = project.parent
        interpreter = self.root / '.venv/bin/python'
        # A successful process exit is insufficient: generated code could call
        # os._exit(0) during collection. The trusted wrapper reports completion
        # only after pytest returns and every original test module was collected.
        expected = []
        for path in sorted((project / 'tests').rglob('test_*.py')):
            try:
                tree = ast.parse(path.read_bytes())
            except (SyntaxError, UnicodeError, ValueError) as exc:
                return {'ok': False, 'error_code': 'tests_collection_invalid',
                        'output': 'Invalid Python test syntax: ' + path.relative_to(project).as_posix(),
                        'line': getattr(exc, 'lineno', None)}
            if any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_') for node in ast.walk(tree)):
                expected.append(path.relative_to(project).as_posix())
        nonce = secrets.token_hex(32)
        wrapper = """import json, pathlib, pytest
class Completion:
    def __init__(self): self.modules=set(); self.collected=0; self.finished=0; self.skipped=0
    def pytest_collection_finish(self,session):
        self.collected=len(session.items)
        self.modules={pathlib.Path(item.path).relative_to(pathlib.Path.cwd()).as_posix() for item in session.items}
    def pytest_runtest_logfinish(self,nodeid,location): self.finished+=1
    def pytest_runtest_logreport(self,report):
        if report.skipped: self.skipped+=1
plugin=Completion()
code=pytest.main(['tests','-q','-p','no:cacheprovider','--noconftest'],plugins=[plugin])
expected=set(EXPECTED)
complete=int(code)==0 and plugin.collected>0 and plugin.finished==plugin.collected and expected.issubset(plugin.modules) and plugin.skipped<=1
print('COMPLETION:'+NONCE+':'+json.dumps({'complete':complete,'collected':plugin.collected,'finished':plugin.finished,'skipped':plugin.skipped}),flush=True)
raise SystemExit(0 if complete else 1)
""".replace('EXPECTED', repr(expected)).replace('NONCE', repr(nonce))
        command = ['bwrap', '--unshare-all', '--die-with-parent',
                   '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin',
                   '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
                   '--proc', '/proc', '--dev', '/dev', '--size', str(64 * 1024 * 1024), '--tmpfs', '/tmp',
                   '--ro-bind', '/etc/passwd', '/etc/passwd', '--ro-bind', '/etc/group', '/etc/group',
                   '--ro-bind', str(self.root / '.venv'), str(self.root / '.venv'),
                   '--bind', str(workspace), str(workspace),
                   '--ro-bind', str(self.root / '.venv'), str(project / '.venv'), '--chdir', str(project),
                   '--', str(interpreter), '-c', wrapper]
        environment = child_environment(workspace)
        environment.update({'PYTHONDONTWRITEBYTECODE': '1', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
                            'AGENT_PLANNER': 'openai', 'CTRADER_DEMO_ONLY': 'true',
                            'CTRADER_OPEN_API_HOST': 'demo.ctraderapi.com', 'PYTHONPATH': str(project),
                            'XAUUSD_STATE_BACKEND': 'local', 'STATE_DB_PATH': str(workspace / 'test-state.sqlite'),
                            'TMPDIR': str(workspace / 'test-tmp')})
        (workspace / 'test-tmp').mkdir(exist_ok=True)
        started = time.monotonic()
        with tempfile.TemporaryFile() as output:
            process = subprocess.Popen(command, cwd=project, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
            error = None
            checked_at = 0.0
            try:
                while process.poll() is None:
                    if time.monotonic() - started > TEST_TIMEOUT_SECONDS: error = 'tests_timeout'; break
                    if os.fstat(output.fileno()).st_size > TEST_OUTPUT_BYTES: error = 'tests_output_limit'; break
                    if time.monotonic() - checked_at >= 1:
                        checked_at = time.monotonic(); total = 0; count = 0
                        for path in workspace.rglob('*'):
                            if path.is_symlink() or not path.is_file(): continue
                            count += 1; total += path.stat().st_size
                            if count > 20000 or total > TEST_WORKSPACE_BYTES:
                                error = 'tests_workspace_limit'; break
                        if error: break
                    time.sleep(.1)
            except BaseException:
                os.killpg(process.pid, signal.SIGKILL); process.wait(); raise
            if error:
                try: os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError: pass
            process.wait()
            # Successful tests may have spawned children. They inherit this
            # session and must not outlive the bounded verification job.
            try: os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
            output_size = os.fstat(output.fileno()).st_size
            tail_size = 2000 if process.returncode == 0 and not error else 10000
            output.seek(max(0, output_size - tail_size))
            tail = output.read(tail_size).decode('utf-8', errors='replace')
            marker = 'COMPLETION:' + nonce + ':'
            if process.returncode == 0 and not error and marker not in tail:
                error = 'tests_completion_missing'
            if marker in tail:
                prefix, completion = tail.rsplit(marker, 1)
                try:
                    completed = json.loads(completion.strip())
                    if not completed.get('complete') and process.returncode == 0: error = 'tests_completion_invalid'
                except (ValueError, TypeError):
                    error = 'tests_completion_invalid'
                tail = prefix
            tail = SecretFilter(env_file=str(workspace / '.no-credentials')).clean(tail)
            return {'ok': process.returncode == 0 and not error, 'exit_code': process.returncode,
                    'seconds': round(time.monotonic() - started, 2),
                    'output': tail, 'truncated': output_size > tail_size,
                    'error_code': error or (None if process.returncode == 0 else 'tests_failed')}

    def deploy(self, workspace: Path) -> dict:
        workspace = Path(workspace).absolute()
        checked = self.check(workspace)
        if not checked['ok']: return checked
        if self.store.meta('engineering_pending'): return {'ok': False, 'error_code': 'release_pending'}
        try:
            tested = self._test(workspace / 'project')
            if not tested['ok']: return tested
            after = self.check(workspace)
            if not after['ok']: return after
            if after['digest'] != checked['digest']:
                return {'ok': False, 'error_code': 'sources_changed_during_tests'}
            if not _safe(self.releases): return {'ok': False, 'error_code': 'unsafe_release_path'}
            with file_lock(self.releases / 'install'):
                if self.store.meta('engineering_pending'): return {'ok': False, 'error_code': 'release_pending'}
                final = self.check(workspace)
                if not final['ok'] or final.get('digest') != checked['digest']: return {'ok': False, 'error_code': 'live_base_changed'}
                frozen = self._records(workspace / 'project')
                for row in checked['changes']:
                    if row['after'] is not None and _hash(frozen[row['path']]) != row['after']:
                        return {'ok': False, 'error_code': 'sources_changed_during_tests'}
                release = {'id': uuid.uuid4().hex, 'state': 'installing', 'changes': checked['changes'], 'tests': tested}
                directory = self.releases / release['id']
                # Backups and complete intent are durable before any live mutation.
                for row in release['changes']:
                    if row['before'] is not None:
                        atomic_write_bytes(directory / 'before' / row['path'], (self.root / row['path']).read_bytes(), mode=0o600)
                self._write_journal(release)
                try:
                    for row in release['changes']:
                        target = self.root / row['path']
                        if row['after'] is None: target.unlink()
                        else: atomic_write_bytes(target, frozen[row['path']], mode=0o644)
                    release['state'] = 'pending_health'; self._write_journal(release)
                    self.store.event('deployment', 'Tested application release installed; restart verification pending', {'release_id': release['id']})
                    return {'ok': True, 'release_id': release['id'], 'state': release['state'], 'restart_required': True, 'changes': len(release['changes'])}
                except BaseException:
                    self.verify_pending(healthy=False)
                    raise
        except (OSError, ValueError, subprocess.SubprocessError):
            return {'ok': False, 'error_code': 'deployment_failed'}

    def verify_pending(self, healthy: bool) -> dict:
        release = self.store.meta('engineering_pending')
        if not release: return {'ok': True, 'state': 'none'}
        try:
            if (not isinstance(release, dict) or not re.fullmatch('[a-f0-9]{32}', release.get('id', ''))
                    or not isinstance(release.get('changes'), list) or len(release['changes']) > MAX_FILES):
                raise ValueError('release_invalid')
            for row in release['changes']:
                relative = Path(row['path'])
                if (relative.is_absolute() or '..' in relative.parts or not _eligible(relative)
                        or _protected(row['path'], self.protected)
                        or any(value is not None and not re.fullmatch('[a-f0-9]{64}', value)
                               for value in (row['before'], row['after']))):
                    raise ValueError('release_invalid')
            if healthy and release['state'] == 'pending_health':
                for row in release['changes']:
                    target = self.root / row['path']
                    current = _hash(target.read_bytes()) if target.exists() else None
                    if not _safe(target) or current != row['after']: raise ValueError('rollback_conflict')
                release['state'] = 'verified'
            else:
                # An interrupted install may contain either old or new bytes.
                # Never overwrite unrelated operator work during rollback.
                for row in release['changes']:
                    target = self.root / row['path']
                    if not _safe(target): raise ValueError('rollback_conflict')
                    current = _hash(target.read_bytes()) if target.exists() else None
                    if current not in {row['before'], row['after']}: raise ValueError('rollback_conflict')
                for row in reversed(release['changes']):
                    target = self.root / row['path']
                    if row['before'] is None: target.unlink(missing_ok=True)
                    else:
                        backup = self.releases / release['id'] / 'before' / row['path']
                        if not _safe(backup): raise ValueError('backup_corrupt')
                        content = backup.read_bytes()
                        if _hash(content) != row['before']: raise ValueError('backup_corrupt')
                        atomic_write_bytes(target, content, mode=0o644)
                release['state'] = 'rolled_back'
            atomic_write_json(self.releases / release['id'] / 'journal.json', release, mode=0o600)
            self.store.meta('engineering_pending', None)
            self.store.meta('engineering', {'state': release['state'], 'release_id': release['id'],
                                            'changes': len(release['changes']), 'tests': release['tests']})
            history = (self.store.meta('engineering_releases') or []) + [release]
            self.store.meta('engineering_releases', history[-3:])
            self.store.event('deployment', 'Application release ' + release['state'], {'release_id': release['id']})
            self._prune_releases(history[:-3])
            return {'ok': True, 'state': release['state'], 'release_id': release['id']}
        except (OSError, ValueError, KeyError, TypeError):
            return {'ok': False, 'state': 'recovery_required', 'error_code': 'rollback_conflict'}

    def recover_pending(self):
        """Fail closed on interrupted installs; leave installed releases to worker."""
        release = self.store.meta('engineering_pending')
        if release and release.get('state') == 'installing': return self.verify_pending(healthy=False)
        return {'ok': True, 'state': 'pending_health' if release else 'none'}

    def _prune_releases(self, expired):
        import shutil
        for row in expired:
            path = self.releases / row['id']
            if path.is_dir() and _safe(path) and len(path.name) == 32:
                shutil.rmtree(path)
