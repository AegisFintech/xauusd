"""Content-addressed reusable research tools, tested only inside Codex sandbox.

Passing generated tests permits reuse in research workspaces. It conveys no
strategy qualification, application deployment, broker or trading privileges.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import os
import signal
import subprocess
from pathlib import Path

from .atomic import atomic_write_bytes, atomic_write_json, file_lock
from .lab_codex import child_environment, permission_arguments

MAX_FILES = 20
MAX_BYTES = 2 * 1024 * 1024
MAX_FILE_BYTES = 256 * 1024
MAX_LIBRARY_BYTES = 64 * 1024 * 1024
MAX_LIBRARY_OBJECTS = 512
MAX_LIBRARY_MANIFESTS = 128


def _result(**values):
    return {'promoted': False, 'count': 0, 'tests': 0, 'test_exit_code': None,
            'digest': None, 'error_code': None, **values}


def _safe(path):
    return not any(p.is_symlink() for p in (path, *path.parents))


def _allowed(relative):
    return (not relative.is_absolute() and '..' not in relative.parts and
            relative.suffix == '.py' and len(relative.parts) >= 2 and
            (relative.parts[0] == 'tools' or
             (len(relative.parts) == 2 and relative.parts[0] == 'tests' and relative.name.startswith('test_'))))


def _snapshot(workspace):
    if not _safe(workspace): raise ValueError('unsafe_tool_path')
    paths = []
    for directory_name in ('tools', 'tests'):
        directory = workspace / directory_name
        if not _safe(directory): raise ValueError('unsafe_tool_path')
        if not directory.is_dir(): continue
        for path in directory.rglob('*'):
            # Fail closed on every symlink, including symlinked subdirectories.
            if not _safe(path): raise ValueError('unsafe_tool_path')
            relative = path.relative_to(workspace)
            if path.is_file() and _allowed(relative): paths.append(path)
    if len(paths) > MAX_FILES: raise ValueError('tool_file_limit')
    total = 0; records = {}; tests = 0
    for path in sorted(paths):
        if path.stat().st_size > MAX_FILE_BYTES: raise ValueError('tool_size_limit')
        data = path.read_bytes()
        if len(data) > MAX_FILE_BYTES: raise ValueError('tool_size_limit')
        total += len(data)
        if total > MAX_BYTES: raise ValueError('tool_total_size_limit')
        try:
            tree = ast.parse(data)
        except (SyntaxError, UnicodeError, ValueError):
            raise ValueError('tool_syntax_invalid') from None
        relative = path.relative_to(workspace).as_posix()
        if relative.startswith('tests/'):
            tests += sum(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith('test_') for node in ast.walk(tree))
        records[relative] = data
    return records, tests


def _manifest(records):
    rows = [{'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
            for name, data in sorted(records.items())]
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'schema': 'xauusd.lab-tools/1', 'digest': digest, 'files': rows}


def _run_sandbox(command, *, timeout, **kwargs):
    """Kill the whole generated-test process group on timeout or interruption."""
    process = subprocess.Popen(command, **kwargs)
    try:
        code = process.wait(timeout=timeout)
        return subprocess.CompletedProcess(command, code)
    except BaseException:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)
        raise


def promote_tools(workspace: Path, library: Path, executable='codex') -> dict:
    workspace, library = Path(workspace).absolute(), Path(library).absolute()
    try:
        records, tests = _snapshot(workspace)
        count = sum(name.startswith('tools/') for name in records)
        if not count or not tests: return _result(error_code='tool_tests_required')
        if not all(_safe(library / name) for name in ('objects', 'manifests', 'current.json', 'current.json.lock')):
            return _result(error_code='unsafe_tool_library')
        interpreter = str(Path(__file__).absolute().parent.parent / '.venv/bin/python')
        command = [executable, 'sandbox', '--permission-profile', 'lab', *permission_arguments(workspace),
                   '-c', 'permissions.lab.network.enabled=false', '-c', 'features.network_proxy=false',
                   '--cd', str(workspace), '--', interpreter, '-m', 'pytest', str(workspace / 'tests'),
                   '-q', '-p', 'no:cacheprovider', '--noconftest', '--confcutdir', str(workspace)]
        environment = child_environment(workspace)
        environment.update({'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'PYTHONDONTWRITEBYTECODE': '1'})
        result = _run_sandbox(command, cwd=workspace, env=environment, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=60, start_new_session=True)
        if result.returncode:
            return _result(tests=tests, test_exit_code=result.returncode, error_code='tool_tests_failed')
        after, _ = _snapshot(workspace)
        if records != after: return _result(tests=tests, test_exit_code=0, error_code='tool_sources_changed')
        manifest = _manifest(records)
        with file_lock(library / 'current.json'):
            if not all(_safe(library / name) for name in ('objects', 'manifests', 'current.json')):
                return _result(error_code='unsafe_tool_library')
            existing = list((library / 'objects').glob('*.py'))
            versions = list((library / 'manifests').glob('*.json'))
            if len(versions) >= MAX_LIBRARY_MANIFESTS and not (library / 'manifests' / (manifest['digest'] + '.json')).exists():
                return _result(error_code='tool_library_full', tests=tests, test_exit_code=0)
            if any(not _safe(path) for path in existing): return _result(error_code='unsafe_tool_library')
            incoming = {row['sha256']: row['bytes'] for row in manifest['files']
                        if not (library / 'objects' / (row['sha256'] + '.py')).exists()}
            if len(existing) + len(incoming) > MAX_LIBRARY_OBJECTS or sum(path.stat().st_size for path in existing) + sum(incoming.values()) > MAX_LIBRARY_BYTES:
                return _result(error_code='tool_library_full', tests=tests, test_exit_code=0)
            for row in manifest['files']:
                target = library / 'objects' / (row['sha256'] + '.py')
                if not _safe(target): return _result(error_code='unsafe_tool_library')
                if target.exists():
                    if target.read_bytes() != records[row['path']]: return _result(error_code='tool_object_corrupt')
                else:
                    atomic_write_bytes(target, records[row['path']], mode=0o400)
            version_path = library / 'manifests' / (manifest['digest'] + '.json')
            if not _safe(version_path): return _result(error_code='unsafe_tool_library')
            if version_path.exists():
                if json.loads(version_path.read_text()) != manifest: return _result(error_code='tool_manifest_corrupt')
            else:
                atomic_write_json(version_path, manifest)
            atomic_write_json(library / 'current.json', manifest)
        return _result(promoted=True, count=count, tests=tests, test_exit_code=0, digest=manifest['digest'])
    except subprocess.TimeoutExpired:
        return _result(error_code='tool_tests_timeout')
    except ValueError as exc:
        code = str(exc)
        return _result(error_code=code if code in {'unsafe_tool_path', 'tool_file_limit', 'tool_size_limit', 'tool_total_size_limit', 'tool_syntax_invalid'} else 'tool_validation_failed')
    except (OSError, TypeError):
        return _result(error_code='tool_promotion_failed')


def seed_tools(workspace: Path, library: Path) -> dict:
    workspace, library = Path(workspace).absolute(), Path(library).absolute()
    if not (library / 'current.json').exists(): return _result()
    try:
        if not _safe(library / 'current.json') or not _safe(library / 'current.json.lock') or not _safe(workspace): raise ValueError()
        with file_lock(library / 'current.json'):
            manifest = json.loads((library / 'current.json').read_text())
            if not isinstance(manifest, dict) or manifest.get('schema') != 'xauusd.lab-tools/1': raise ValueError()
            rows = manifest.get('files')
            if not isinstance(rows, list) or len(rows) > MAX_FILES: raise ValueError()
            records = {}; total = 0
            for row in rows:
                if not isinstance(row, dict) or not isinstance(row.get('path'), str): raise ValueError()
                relative = Path(row['path'])
                if not _allowed(relative) or not re.fullmatch('[a-f0-9]{64}', row.get('sha256', '')): raise ValueError()
                source = library / 'objects' / (row['sha256'] + '.py')
                target = workspace / relative
                if not _safe(source) or not _safe(target) or source.stat().st_size > MAX_FILE_BYTES: raise ValueError()
                data = source.read_bytes(); total += len(data)
                if total > MAX_BYTES or len(data) != row.get('bytes') or hashlib.sha256(data).hexdigest() != row['sha256']: raise ValueError()
                records[row['path']] = data
            if _manifest(records) != manifest: raise ValueError()
            for name, data in records.items(): atomic_write_bytes(workspace / name, data)
        return _result(count=sum(name.startswith('tools/') for name in records), digest=manifest['digest'])
    except (OSError, ValueError, KeyError, TypeError):
        return _result(error_code='tool_library_invalid')
