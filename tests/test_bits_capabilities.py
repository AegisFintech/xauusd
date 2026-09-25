"""The shell-job environment is discoverable from the environment jobs really get."""
import json
import os
from pathlib import Path
import shlex
import sys
import time
from uuid import uuid4

import pytest

from xauusd.bits_capabilities import (TOOLS, build_manifest, heartbeat_view, missing_executables, prompt_view,
                                      record_observed, shell_environment, shell_path)
from xauusd.bits_jobs import BitsStore, SecretFilter, ShellJobs
from xauusd.cli import build_parser
from xauusd.local_state import SQLiteAgentTranscriptStore

IN_VENV = sys.prefix != sys.base_prefix
SERVICE_BIN = str(Path(sys.executable).parent)


def fake_tool(directory, name, output):
    directory.mkdir(parents=True, exist_ok=True)
    tool = directory / name
    tool.write_text(f"#!/bin/sh\necho '{output}'\n")
    tool.chmod(0o755)
    return tool


def test_shell_path_prepends_service_interpreter_and_declared_directories(tmp_path):
    tools = tmp_path / 'tools'
    tools.mkdir()
    base = {'PATH': '/usr/bin:/bin:/usr/bin', 'BITS_SHELL_EXTRA_PATH': f'relative/bin:{tmp_path}/missing:{tools}'}
    path, report = shell_path(base)
    entries = path.split(os.pathsep)
    assert entries == report['entries'] and len(entries) == len(set(entries))
    expected = ([SERVICE_BIN] if IN_VENV else []) + [str(tools), '/usr/bin', '/bin']
    assert entries == expected
    assert {'entry': str(tools), 'origin': 'BITS_SHELL_EXTRA_PATH'} in report['prepended']
    assert report['ignored'] == [{'entry': 'relative/bin', 'reason': 'not_absolute'},
                                 {'entry': f'{tmp_path}/missing', 'reason': 'not_a_directory'}]
    assert shell_path({})[1]['inherited_from'] == 'os.defpath'


def test_shell_environment_keeps_the_latest_refreshed_tokens(tmp_path):
    env_file = tmp_path / '.env'
    env_file.write_text('CTRADER_ACCESS_TOKEN=refreshed-access\nUNRELATED=ignored\n')
    env = shell_environment({'PATH': '/bin', 'CTRADER_ACCESS_TOKEN': 'stale'}, str(env_file))
    assert env['CTRADER_ACCESS_TOKEN'] == 'refreshed-access' and 'UNRELATED' not in env
    assert env['PATH'].endswith('/bin')


def test_restricted_path_manifest_reports_missing_tools_with_fallbacks(tmp_path, monkeypatch):
    # Only the given directory is searched, so tools installed in the local .venv cannot leak in.
    monkeypatch.setattr('xauusd.bits_capabilities._in_virtualenv', lambda: False)
    bin_dir = tmp_path / 'bin'
    fake_tool(bin_dir, 'rg', 'ripgrep 99.0.0')
    manifest = build_manifest({'PATH': str(bin_dir), 'HOME': str(tmp_path)}, cwd=str(tmp_path),
                              env_file=str(tmp_path / 'no-env'))
    tools = manifest['tools']
    assert tools['rg'] == {'state': 'available', 'available': True, 'path': str(bin_dir / 'rg'),
                           'purpose': TOOLS['rg']['purpose'], 'version': 'ripgrep 99.0.0', 'version_state': 'probed'}
    assert tools['graphify']['state'] == 'missing' and tools['graphify']['version_state'] == 'not_applicable'
    assert manifest['status'] == 'ok' and manifest['errors'] == [] and manifest['configuration_errors'] == []
    for name in ('graphify', 'grep', 'git'):
        assert not tools[name]['available'] and tools[name]['fallback'] == TOOLS[name]['fallback']
    assert 'GRAPH_REPORT.md' in tools['graphify']['fallback']
    assert manifest['required_missing'] == [] and manifest['cwd'] == str(tmp_path)
    assert manifest['python']['path'] == sys.executable
    assert manifest['python']['cli_prefix'] == shlex.quote(sys.executable) + ' -m xauusd.cli'
    assert manifest['python']['bare_python'] is None and not manifest['python']['bare_python_is_service_interpreter']
    assert manifest['path']['entries'] == [str(bin_dir)]
    assert manifest['data']['entry_point'] == 'xauusd.data.HistoricalDataStore'
    assert manifest['data']['exists'] is False and manifest['data']['columns'][:4] == ['open', 'high', 'low', 'close']
    assert {'bits-memory', 'bits-job', 'bits-capabilities', 'agent-tool'} <= set(manifest['cli_commands'])
    view = prompt_view(manifest)
    assert view['tools']['graphify'] == {'available': False, 'fallback': TOOLS['graphify']['fallback']}
    assert not any(key.startswith('notes_') for key in view['operations'])
    assert heartbeat_view(manifest)['unavailable_tools'] == ['git', 'graphify', 'grep']


def test_every_published_operation_is_a_real_cli_command(tmp_path):
    parser = build_parser()
    prefix = shlex.quote(sys.executable) + ' -m xauusd.cli '
    for name, command in build_manifest(cwd=str(tmp_path))['operations'].items():
        assert command.startswith(prefix), name
        # Drop the heredoc body and any optional [..] suffix, fill documented placeholders with
        # concrete values, then parse with the real grammar.
        rest = command[len(prefix):].split(' <<')[0].split(' [')[0]
        rest = rest.replace('VERSION', '1').replace('DRAFT_ID', 'draft_' + '0' * 12)
        parser.parse_args(shlex.split(rest))  # raises SystemExit on an unsupported example


def test_manifest_never_includes_environment_values(tmp_path, monkeypatch):
    secret, setting = uuid4().hex, uuid4().hex
    monkeypatch.setenv('EXAMPLE_API_KEY', secret)
    monkeypatch.setenv('SOME_SETTING', setting)
    text = json.dumps(build_manifest(cwd=str(tmp_path)))
    assert secret not in text and setting not in text and 'EXAMPLE_API_KEY' not in text


@pytest.mark.parametrize('stderr,expected', [
    ('/bin/bash: line 1: python: command not found\n', ['python']),
    ('bash: rg: command not found', ['rg']),
    ('/bin/bash: line 3: bits-memory: command not found\n/bin/bash: line 4: rg: command not found', ['bits-memory', 'rg']),
    ("/usr/bin/env: 'python': No such file or directory", ['python']),
    ('/usr/bin/env: \u2018graphify\u2019: No such file or directory', ['graphify']),
    ("python3: can't open file 'x.py': [Errno 2] No such file or directory", []),
])
def test_missing_executables_are_detected_from_shell_messages(stderr, expected):
    assert missing_executables({'stderr': stderr}) == expected


def test_observed_missing_executables_are_bounded_and_counted():
    observed = record_observed(None, ['rg'], 'job-1')
    observed = record_observed(observed, ['rg', 'graphify'], 'job-2')
    assert observed['rg']['count'] == 2 and observed['rg']['job_id'] == 'job-2'
    assert record_observed(observed, ['rg'], 'job-2')['rg']['count'] == 2  # idempotent per job
    for index in range(20):
        observed = record_observed(observed, [f'tool{index}'], f'job-{index}')
    assert len(observed) == 10 and 'tool19' in observed


def wait(store, job):
    for _ in range(600):
        result = store.job(job['job_id'])
        if result['status'] != 'running':
            return result
        time.sleep(.05)
    raise AssertionError('job did not finish')


def test_service_like_shell_runs_documented_examples_without_profile(tmp_path, monkeypatch):
    """Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI prefix."""
    empty_bin, home = tmp_path / 'empty-bin', tmp_path / 'home'
    empty_bin.mkdir()
    home.mkdir()
    (home / '.bashrc').write_text('echo PROFILE-SOURCED\n')
    monkeypatch.setenv('PATH', str(empty_bin))
    monkeypatch.setenv('HOME', str(home))
    for name in ('BASH_ENV', 'ENV', 'BITS_SHELL_EXTRA_PATH'):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv('XAUUSD_STATE_BACKEND', 'local')
    monkeypatch.setenv('STATE_DB_PATH', str(tmp_path / 'isolated.db'))
    manifest = build_manifest(cwd=str(tmp_path))
    cli = manifest['python']['cli_prefix']
    notes = json.dumps({'notes': {key: [] for key in ('findings', 'hypotheses', 'rejected_approaches',
                                                       'open_questions', 'next_steps')}})
    command = '\n'.join([
        f'{cli} bits-capabilities > caps.json',
        f'{manifest["operations"]["notes_validate"].split(" <<")[0]} <<\'JSON\'', notes, 'JSON',
        'command -v python || echo NO-BARE-PYTHON',
        'rg --version',
    ])
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'jobs.db')))
    jobs = ShellJobs(store, SecretFilter(str(tmp_path / 'no-env')))
    try:
        action = dict(id='probe', type='shell', args=dict(command=command, cwd=str(tmp_path), timeout_sec=120,
                                                            max_output_bytes=65536))
        result = wait(store, jobs.start('cycle', action))
    finally:
        jobs.stop()
    assert result['exit_code'] == 127 and 'PROFILE-SOURCED' not in result['stdout']
    assert '"status": "valid"' in result['stdout']
    assert missing_executables(result) == ['rg']
    if IN_VENV:
        assert SERVICE_BIN + '/python' in result['stdout']
    job_view = json.loads((tmp_path / 'caps.json').read_text())
    assert job_view['path']['entries'][-1] == str(empty_bin)
    assert not job_view['tools']['rg']['available'] and not job_view['tools']['grep']['available']
    assert job_view['required_missing'] == [] and job_view['cwd'] == str(tmp_path)


# --- R2: discovery status stays honest in stored, prompt and heartbeat views ---
from datetime import datetime, timedelta, timezone
from xauusd.agent_status import bits_alerts
from xauusd.bits_capabilities import STALE_AFTER_SECONDS, check_manifest, minimal_manifest


def test_failed_discovery_is_explicit_in_every_view():
    manifest = minimal_manifest('os_error')
    assert manifest['status'] == 'failed' and manifest['errors'] == [{'section': 'manifest', 'error_code': 'os_error'}]
    assert all(tool['state'] == 'unknown' and tool['available'] is None for tool in manifest['tools'].values())
    view = prompt_view(manifest)
    assert view['status'] == 'failed' and view['discovery']['error_code'] == 'os_error'
    assert view['tools']['rg'] == {'available': None, 'state': 'unknown', 'fallback': TOOLS['rg']['fallback']}
    beat = heartbeat_view(manifest)
    assert beat['status'] == 'failed' and beat['error_code'] == 'os_error' and beat['unavailable_tools'] == []
    assert beat['unknown_tools'] == sorted(TOOLS)
    verdict = check_manifest(manifest)
    assert not verdict['passed'] and verdict['failures'][0] == {
        'kind': 'discovery', 'status': 'failed', 'error_code': 'os_error',
        'errors': [{'section': 'manifest', 'error_code': 'os_error'}]}
    assert bits_alerts({'capabilities': beat}) == [
        'Bits shell capability discovery failed (os_error); tool availability is unknown']
    # A manifest without an explicit status (previous release or corrupted) is unknown, never passing.
    legacy = {key: value for key, value in build_manifest().items() if key not in ('status', 'errors', 'error_code')}
    assert check_manifest(legacy)['status'] == 'unknown' and not check_manifest(legacy)['passed']


def test_partial_discovery_names_failed_sections_and_fails_the_check(tmp_path, monkeypatch):
    def broken(*args, **kwargs):
        raise OSError('unreadable data directory')
    monkeypatch.setattr('xauusd.bits_capabilities.data_access', broken)
    monkeypatch.setattr('xauusd.bits_capabilities.cli_commands', lambda: 1 / 0)
    manifest = build_manifest(cwd=str(tmp_path))
    # Sections are reported in discovery order; the summary code is the first failure's.
    assert manifest['status'] == 'partial' and manifest['error_code'] == 'unclassified'
    assert manifest['errors'] == [{'section': 'cli_commands', 'error_code': 'unclassified'},
                                  {'section': 'data', 'error_code': 'os_error'}]
    assert manifest['data'] == {'entry_point': 'xauusd.data.HistoricalDataStore', 'state': 'unknown'}
    assert manifest['tools']['grep']['state'] in ('available', 'missing')  # other sections still discovered
    assert prompt_view(manifest)['discovery']['errors'] == manifest['errors']
    assert [failure['kind'] for failure in check_manifest(manifest)['failures']] == ['discovery']
    assert bits_alerts({'capabilities': heartbeat_view(manifest)}) == [
        'Bits shell capability discovery incomplete: cli_commands (unclassified), data (os_error)']


def test_invalid_declared_directories_are_configuration_errors_not_missing_tools(tmp_path):
    base = {'PATH': '/usr/bin:/bin', 'BITS_SHELL_EXTRA_PATH': f'relative/bin:{tmp_path}/absent'}
    manifest = build_manifest(base, cwd=str(tmp_path), env_file=str(tmp_path / 'no-env'))
    assert manifest['status'] == 'ok'  # discovery itself succeeded
    assert manifest['configuration_errors'] == [
        {'kind': 'invalid_extra_path', 'variable': 'BITS_SHELL_EXTRA_PATH', 'entry': 'relative/bin', 'reason': 'not_absolute'},
        {'kind': 'invalid_extra_path', 'variable': 'BITS_SHELL_EXTRA_PATH', 'entry': f'{tmp_path}/absent',
         'reason': 'not_a_directory'}]
    verdict = check_manifest(manifest)
    assert not verdict['passed'] and {failure['kind'] for failure in verdict['failures']} == {'configuration'}
    assert verdict['failures'][0]['issue'] == 'invalid_extra_path' and verdict['failures'][0]['entry'] == 'relative/bin'
    assert prompt_view(manifest)['configuration_errors'] == manifest['configuration_errors']
    alerts = bits_alerts({'capabilities': heartbeat_view(manifest)})
    assert 'Bits shell configuration: BITS_SHELL_EXTRA_PATH entry relative/bin ignored (not_absolute)' in alerts


def test_stored_manifest_probe_time_and_staleness_are_checked(tmp_path):
    manifest = build_manifest(cwd=str(tmp_path))
    fresh = check_manifest(manifest, stored=True)
    assert fresh['passed'] and not fresh['stale'] and fresh['probed_at'] == manifest['generated_at']
    old = {**manifest, 'generated_at': (datetime.now(timezone.utc) - timedelta(seconds=STALE_AFTER_SECONDS + 5)).isoformat()}
    stale = check_manifest(old, stored=True)
    assert not stale['passed'] and stale['stale'] and stale['failures'][-1]['kind'] == 'stale'
    assert stale['age_seconds'] > STALE_AFTER_SECONDS
    assert not check_manifest({**manifest, 'generated_at': 'not a time'}, stored=True)['passed']
    assert check_manifest(old)['passed']  # a direct probe is judged on its content, not a stored age


def test_version_probe_results_are_distinguished(tmp_path, monkeypatch):
    monkeypatch.setattr('xauusd.bits_capabilities._in_virtualenv', lambda: False)
    bin_dir = tmp_path / 'bin'
    fake_tool(bin_dir, 'graphify', 'never run')
    silent = bin_dir / 'git'
    silent.write_text('#!/bin/sh\nexit 3\n')
    silent.chmod(0o755)
    tools = build_manifest({'PATH': str(bin_dir)}, cwd=str(tmp_path), env_file=str(tmp_path / 'no-env'))['tools']
    assert (tools['graphify']['state'], tools['graphify']['version'], tools['graphify']['version_state']) == \
        ('available', None, 'not_probed')
    assert (tools['git']['state'], tools['git']['version_state']) == ('available', 'probe_failed')


def test_optional_absent_tool_with_fallback_passes_and_does_not_alert(tmp_path, monkeypatch):
    monkeypatch.setattr('xauusd.bits_capabilities._in_virtualenv', lambda: False)
    bin_dir = tmp_path / 'bin'
    fake_tool(bin_dir, 'grep', 'grep (GNU grep) 3.11')
    manifest = build_manifest({'PATH': str(bin_dir)}, cwd=str(tmp_path), env_file=str(tmp_path / 'no-env'))
    assert manifest['status'] == 'ok' and manifest['tools']['graphify']['state'] == 'missing'
    assert check_manifest(manifest)['passed']
    beat = heartbeat_view(manifest)
    assert 'graphify' in beat['unavailable_tools'] and bits_alerts({'capabilities': beat}) == []


def test_a_repaired_tool_clears_the_observed_missing_alert(tmp_path, monkeypatch):
    monkeypatch.setattr('xauusd.bits_capabilities._in_virtualenv', lambda: False)
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    observed = record_observed(None, ['rg'], 'job-1')
    before = build_manifest({'PATH': str(bin_dir)}, cwd=str(tmp_path), observed=observed, env_file=str(tmp_path / 'x'))
    assert heartbeat_view(before)['observed_missing'] == ['rg'] and bits_alerts({'capabilities': heartbeat_view(before)})
    fake_tool(bin_dir, 'rg', 'ripgrep 14.1.0')
    after = build_manifest({'PATH': str(bin_dir)}, cwd=str(tmp_path), observed=observed, env_file=str(tmp_path / 'x'))
    assert after['tools']['rg']['state'] == 'available' and after['observed_missing'][0]['now_available']
    assert heartbeat_view(after)['observed_missing'] == [] and bits_alerts({'capabilities': heartbeat_view(after)}) == []
    assert prompt_view(after)['observed_missing'] == []
