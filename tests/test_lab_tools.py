import json
from pathlib import Path
from unittest.mock import patch

from xauusd.lab_tools import seed_tools, promote_tools


def generated(tmp_path):
    workspace = tmp_path / 'workspace'; (workspace / 'tools').mkdir(parents=True); (workspace / 'tests').mkdir()
    (workspace / 'tools/returns.py').write_text('def returns(x):\n    return x + 1\n')
    (workspace / 'tests/test_returns.py').write_text('def test_returns():\n    assert True\n')
    return workspace, tmp_path / 'library'


def test_passed_tools_are_immutable_and_reused(tmp_path):
    workspace, library = generated(tmp_path)
    with patch('xauusd.lab_tools._run_sandbox') as run:
        run.return_value.returncode = 0
        result = promote_tools(workspace, library)
    assert result['promoted'] and result['count'] == 1 and result['tests'] == 1
    command = run.call_args.args[0]
    assert command[:2] == ['codex', 'sandbox']
    assert '-m' in command and 'pytest' in command
    assert run.call_args.kwargs['timeout'] == 60
    destination = tmp_path / 'next'; destination.mkdir()
    seeded = seed_tools(destination, library)
    assert seeded['count'] == 1
    assert (destination / 'tools/returns.py').read_bytes() == (workspace / 'tools/returns.py').read_bytes()
    assert (destination / 'tests/test_returns.py').exists()
    assert json.loads((library / 'current.json').read_text())['digest'] == result['digest']


def test_failed_tests_never_publish(tmp_path):
    workspace, library = generated(tmp_path)
    with patch('xauusd.lab_tools._run_sandbox') as run:
        run.return_value.returncode = 1
        result = promote_tools(workspace, library)
    assert not result['promoted'] and result['test_exit_code'] == 1
    assert not (library / 'current.json').exists()


def test_symlinks_and_size_limit_refuse_execution(tmp_path):
    workspace, library = generated(tmp_path)
    (workspace / 'tools/link.py').symlink_to(workspace / 'tools/returns.py')
    with patch('xauusd.lab_tools._run_sandbox') as run:
        assert promote_tools(workspace, library)['error_code'] == 'unsafe_tool_path'
        run.assert_not_called()
    (workspace / 'tools/link.py').unlink()
    (workspace / 'tools/returns.py').write_bytes(b'x' * (256 * 1024 + 1))
    assert promote_tools(workspace, library)['error_code'] == 'tool_size_limit'


def test_corrupt_or_traversal_library_never_seeds(tmp_path):
    workspace, library = generated(tmp_path)
    library.mkdir()
    (library / 'current.json').write_text(json.dumps({'files': [{'path': '../escape.py', 'sha256': '0' * 64}], 'digest': 'bad'}))
    assert seed_tools(workspace, library)['error_code'] == 'tool_library_invalid'
    assert not (tmp_path / 'escape.py').exists()


def test_timeout_and_source_mutation_never_publish(tmp_path):
    import subprocess
    workspace, library = generated(tmp_path)
    with patch('xauusd.lab_tools._run_sandbox', side_effect=subprocess.TimeoutExpired(['secret'], 60)):
        result = promote_tools(workspace, library)
    assert result['error_code'] == 'tool_tests_timeout'
    assert 'secret' not in json.dumps(result)
    def changed(*args, **kwargs):
        from types import SimpleNamespace
        (workspace / 'tools/returns.py').write_text('def different(): pass')
        return SimpleNamespace(returncode=0)
    with patch('xauusd.lab_tools._run_sandbox', side_effect=changed):
        assert promote_tools(workspace, library)['error_code'] == 'tool_sources_changed'
    assert not (library / 'current.json').exists()


def test_file_count_and_library_symlink_refuse(tmp_path):
    workspace, library = generated(tmp_path)
    for i in range(20): (workspace / f'tools/extra{i}.py').write_text('x=1')
    with patch('xauusd.lab_tools._run_sandbox') as run:
        assert promote_tools(workspace, library)['error_code'] == 'tool_file_limit'
        run.assert_not_called()
    for i in range(20): (workspace / f'tools/extra{i}.py').unlink()
    library.mkdir(); outside = tmp_path / 'outside'; outside.mkdir()
    (library / 'manifests').symlink_to(outside)
    with patch('xauusd.lab_tools._run_sandbox') as run:
        assert promote_tools(workspace, library)['error_code'] == 'unsafe_tool_library'
        run.assert_not_called()
    assert list(outside.iterdir()) == []


def test_child_environment_does_not_pass_credentials(tmp_path, monkeypatch):
    workspace, library = generated(tmp_path)
    monkeypatch.setenv('CTRADER_ACCESS_TOKEN', 'must-not-propagate')
    with patch('xauusd.lab_tools._run_sandbox') as run:
        run.return_value.returncode = 0
        promote_tools(workspace, library)
    environment = run.call_args.kwargs['env']
    assert 'CTRADER_ACCESS_TOKEN' not in environment
    assert environment['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] == '1'
    assert '--noconftest' in run.call_args.args[0]


def test_timeout_kills_entire_sandbox_group():
    import signal
    import subprocess
    import pytest
    from xauusd.lab_tools import _run_sandbox
    with patch('xauusd.lab_tools.subprocess.Popen') as create, patch('xauusd.lab_tools.os.killpg') as kill:
        create.return_value.pid = 12345
        create.return_value.wait.side_effect = [subprocess.TimeoutExpired(['codex'], 60), -9]
        with pytest.raises(subprocess.TimeoutExpired):
            _run_sandbox(['codex'], timeout=60, start_new_session=True)
        kill.assert_called_once_with(12345, signal.SIGKILL)
        assert create.return_value.wait.call_count == 2


def test_library_cap_and_corrupt_objects_never_seed(tmp_path, monkeypatch):
    workspace, library = generated(tmp_path)
    monkeypatch.setattr('xauusd.lab_tools.MAX_LIBRARY_BYTES', 1)
    with patch('xauusd.lab_tools._run_sandbox') as run:
        run.return_value.returncode = 0
        assert promote_tools(workspace, library)['error_code'] == 'tool_library_full'
    monkeypatch.setattr('xauusd.lab_tools.MAX_LIBRARY_BYTES', 64 * 1024 * 1024)
    with patch('xauusd.lab_tools._run_sandbox') as run:
        run.return_value.returncode = 0
        assert promote_tools(workspace, library)['promoted']
    manifest = json.loads((library / 'current.json').read_text())
    source = library / 'objects' / (manifest['files'][0]['sha256'] + '.py')
    source.chmod(0o600); source.write_text('tampered')
    destination = tmp_path / 'next'
    assert seed_tools(destination, library)['error_code'] == 'tool_library_invalid'
    assert not (destination / 'tools').exists()
