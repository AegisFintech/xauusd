import json
import sys
from datetime import datetime, timezone

import pytest

from xauusd import cli
from xauusd.paper_trading import InMemoryPaperTradingStore, PaperRiskConfig, PaperTrading


def no_broker():
    raise AssertionError("network setup")


class DemoTransport:
    def __init__(self, is_demo=True):
        self.is_demo = is_demo

    def send(self, request, timeout_seconds):
        return {"account_id": 7, "is_demo": self.is_demo, "symbol": "XAUUSD", "symbol_id": 99, "positions": [], "open_orders": []}


def stopped_demo_adapter(monkeypatch, reason, is_demo=True):
    from xauusd.ctrader_demo import CTraderDemoAccount, CTraderDemoAdapter, InMemoryCTraderDemoStore
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    adapter = CTraderDemoAdapter(CTraderDemoAccount(7, 99), InMemoryCTraderDemoStore(), DemoTransport(is_demo))
    adapter.stop(reason)
    return adapter


def test_demo_automation_start_requires_a_reason(monkeypatch):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    monkeypatch.setattr(cli, "_ctrader_demo_adapter", no_broker)
    monkeypatch.setattr(sys, "argv", ["xauusd", "demo-automation", "start"])

    with pytest.raises(SystemExit):
        cli.main()


def test_demo_automation_start_reconciles_then_clears_only_the_demo_switch(monkeypatch, capsys):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    # Set, not deleted: cli.main() loads .env, which would otherwise re-add a deployed `true`.
    monkeypatch.setenv("CTRADER_PAPER_ONLY", "false")
    adapter = stopped_demo_adapter(monkeypatch, "transport_failure")
    monkeypatch.setattr(cli, "_ctrader_demo_adapter", lambda: adapter)
    monkeypatch.setattr(cli, "_paper_from_env", lambda: (_ for _ in ()).throw(AssertionError("paper touched")))
    monkeypatch.setattr(sys, "argv", ["xauusd", "demo-automation", "start", "--reason", "broker exposure checked"])

    cli.main()

    assert json.loads(capsys.readouterr().out) == {"state": "demo_started", "demo_started": True, "stopped": False,
                                                   "kill_switch_reason": "broker exposure checked"}
    assert adapter.state()["stopped"] is False


def test_demo_automation_start_keeps_the_switch_stopped_when_reconciliation_fails(monkeypatch):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    monkeypatch.setenv("CTRADER_PAPER_ONLY", "false")
    adapter = stopped_demo_adapter(monkeypatch, "transport_failure", is_demo=False)
    monkeypatch.setattr(cli, "_ctrader_demo_adapter", lambda: adapter)

    result = cli.demo_automation("start", "broker exposure checked")

    assert result["state"] == "refused" and result["demo_started"] is False
    assert adapter.state()["stopped"] is True
    assert adapter.state()["kill_switch_reason"] == "reconciliation_failed"


def test_demo_automation_once_reports_a_refused_restart(tmp_path, monkeypatch, capsys):
    from xauusd.demo_execution import PaperToCTraderDemoCoordinator
    from xauusd.demo_runner import DemoAutomationRunner
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    monkeypatch.setenv("CTRADER_AUTOMATION_STATUS_PATH", str(tmp_path / "status.json"))
    paper = PaperTrading(InMemoryPaperTradingStore(), PaperRiskConfig())
    paper.stop("maintenance")
    monkeypatch.setattr(cli, "_demo_automation_runner", lambda config: DemoAutomationRunner(
        PaperToCTraderDemoCoordinator(paper, paper_only=True), None, None, config))
    monkeypatch.setattr(sys, "argv", ["xauusd", "demo-automation", "once"])

    cli.main()

    printed = json.loads(capsys.readouterr().out)
    assert (printed["state"], printed["kill_switch"], printed["kill_switch_reason"]) == ("resume_refused", "paper", "maintenance")
    assert paper.state()["stopped"] is True


def test_demo_automation_start_in_paper_only_mode_contacts_no_broker(monkeypatch):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    monkeypatch.setenv("CTRADER_PAPER_ONLY", "true")
    monkeypatch.setattr(cli, "_ctrader_demo_adapter", no_broker)

    assert cli.demo_automation("start", "operator")["state"] == "paper_only"


def test_demo_automation_disabled_returns_status_without_constructing_clients(monkeypatch, capsys):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "false")
    monkeypatch.setattr(cli, "_demo_automation_runner", lambda config: (_ for _ in ()).throw(AssertionError("network setup")))
    monkeypatch.setattr(sys, "argv", ["xauusd", "demo-automation", "once"])

    cli.main()

    assert '"state": "disabled"' in capsys.readouterr().out


def test_demo_automation_requires_explicit_positive_volume(monkeypatch):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    monkeypatch.delenv("CTRADER_PAPER_ONLY", raising=False)
    monkeypatch.delenv("CTRADER_VOLUME_PER_PAPER_UNIT", raising=False)

    try:
        cli._demo_automation_runner(cli.DemoRunnerConfig.from_env())
        assert False
    except ValueError as exc:
        assert "CTRADER_VOLUME_PER_PAPER_UNIT" in str(exc)


def test_demo_automation_paper_only_skips_broker_dependencies(monkeypatch):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    monkeypatch.setenv("CTRADER_PAPER_ONLY", "true")
    monkeypatch.delenv("CTRADER_VOLUME_PER_PAPER_UNIT", raising=False)

    class FakeStore:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def initialize(self):
            return None

    monkeypatch.setattr(cli, "_paper_from_env", lambda: PaperTrading(InMemoryPaperTradingStore(), PaperRiskConfig()))
    monkeypatch.setattr(cli, "HistoricalDataStore", lambda: object())
    monkeypatch.setattr(cli, "LocalHistoricalMarketDataSource", lambda *args: object())
    monkeypatch.setattr(cli, "ConfirmedBreakoutCanarySource", lambda *args: None)

    instance = cli._demo_automation_runner(cli.DemoRunnerConfig.from_env())

    assert instance.paper_only
    assert instance.coordinator.demo_adapter is None


def test_demo_automation_status_reports_paper_only_flag(monkeypatch, capsys):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "false")
    monkeypatch.setenv("CTRADER_PAPER_ONLY", "true")
    monkeypatch.setattr(sys, "argv", ["xauusd", "demo-automation", "status"])

    cli.main()

    assert '"paper_only": true' in capsys.readouterr().out


def test_paper_stop_persists_kill_switch(tmp_path, monkeypatch, capsys):
    trading = PaperTrading(InMemoryPaperTradingStore(), PaperRiskConfig())
    trading.start("agent_continuous_paper_loop")
    monkeypatch.setattr(cli, "_paper_from_env", lambda: trading)
    monkeypatch.setattr(sys, "argv", ["xauusd", "paper", "stop"])
    cli.main()
    assert trading.state()["stopped"] is True
    assert trading.state()["kill_switch_reason"] == "operator"


def test_paper_start_overrides_operator_stop(tmp_path, monkeypatch, capsys):
    trading = PaperTrading(InMemoryPaperTradingStore(), PaperRiskConfig())
    trading.stop("operator")
    monkeypatch.setattr(cli, "_paper_from_env", lambda: trading)
    monkeypatch.setattr(sys, "argv", ["xauusd", "paper", "start"])
    cli.main()
    assert trading.state()["stopped"] is False


def test_agent_resume_refused_after_operator_stop_writes_status(tmp_path, monkeypatch):
    trading = PaperTrading(InMemoryPaperTradingStore(), PaperRiskConfig())
    trading.start("agent_continuous_paper_loop")
    trading.stop("operator")
    monkeypatch.setattr(cli, "_paper_from_env", lambda: trading)
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    monkeypatch.setenv("STATE_DB_PATH", str(tmp_path / "state.db"))
    monkeypatch.delenv("XAUUSD_STATE_BACKEND", raising=False)
    status_file = tmp_path / "agent_status.json"
    monkeypatch.setenv("AGENT_STATUS_FILE", str(status_file))

    result = cli.agent_controller("once")

    assert result["state"] == "stopped"
    assert result["reason"] == "resume_refused"
    assert result["kill_switch_reason"] == "operator"
    assert status_file.is_file()


def test_agent_controller_refuses_on_corrupt_state(tmp_path, monkeypatch):
    trading = PaperTrading(InMemoryPaperTradingStore(), PaperRiskConfig())
    trading.store.corrupt_state_for_test()
    monkeypatch.setattr(cli, "_paper_from_env", lambda: trading)
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    monkeypatch.setenv("STATE_DB_PATH", str(tmp_path / "state.db"))
    monkeypatch.delenv("XAUUSD_STATE_BACKEND", raising=False)
    status_file = tmp_path / "agent_status.json"
    monkeypatch.setenv("AGENT_STATUS_FILE", str(status_file))

    result = cli.agent_controller("once")

    assert result["reason"] == "resume_refused"
    assert result["kill_switch_reason"] == "corrupt_state"


def test_data_update_retries_transient_failures(monkeypatch):
    class FlakyDownloader:
        def __init__(self):
            self.calls = 0

        def download(self, *args, **kwargs):
            self.calls += 1
            if self.calls < 3:
                raise ConnectionError("transient")
            return {"ok": True}

    downloader = FlakyDownloader()
    monkeypatch.setattr(cli.time, "sleep", lambda seconds: None)
    result = cli._download_with_retry(downloader, "2026-09-01")
    assert result == {"ok": True}
    assert downloader.calls == 3


def test_data_update_does_not_retry_auth_errors(monkeypatch):
    from xauusd.data import CTraderAuthError
    calls = {"n": 0}

    class AuthDownloader:
        def download(self, *args, **kwargs):
            calls["n"] += 1
            raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID")

    with pytest.raises(CTraderAuthError):
        cli._download_with_retry(AuthDownloader(), "2026-09-01")
    assert calls["n"] == 1


def test_state_integrity_backup_restore_round_trip(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("STATE_DB_PATH", str(tmp_path / "state.db"))
    monkeypatch.delenv("XAUUSD_STATE_BACKEND", raising=False)
    backup_root = tmp_path / "backups"

    monkeypatch.setattr(sys, "argv", ["xauusd", "state", "integrity"])
    cli.main()
    assert '"paper": "ok"' in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["xauusd", "state", "backup", "--root", str(backup_root)])
    cli.main()
    assert '"integrity": "ok"' in capsys.readouterr().out

    import json
    latest = json.loads((backup_root / "latest.json").read_text())
    run_dir = latest["directory"]
    monkeypatch.setattr(sys, "argv", ["xauusd", "state", "restore", "--backup", run_dir])
    cli.main()
    assert '"restored": true' in capsys.readouterr().out


def test_bits_notes_only_does_not_repeat_history(tmp_path, monkeypatch, capsys):
    import json
    from xauusd.bits_jobs import BitsStore
    from xauusd.local_state import SQLiteAgentTranscriptStore
    path = str(tmp_path / 'state.db')
    monkeypatch.setenv('XAUUSD_STATE_BACKEND', 'local')
    monkeypatch.setenv('STATE_DB_PATH', path)
    store = BitsStore(SQLiteAgentTranscriptStore(path))
    store.put('memory', {'recent': ['irrelevant history'], 'digest': []})
    store.put('working_notes', {'notes': {'findings': []}})
    monkeypatch.setattr('sys.argv', ['xauusd', 'bits-memory', 'show', '--notes-only'])
    cli.main()
    assert json.loads(capsys.readouterr().out) == {'notes': {'findings': []}}


def test_demo_factory_binds_authoritative_paper_exposure(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv("CTRADER_VOLUME_PER_PAPER_UNIT", "100")
    monkeypatch.setattr(cli.CTraderDemoOpenApiConfig, "from_env", lambda: SimpleNamespace(timeout_seconds=30))
    monkeypatch.setattr(cli, "CTraderDemoOpenApiTransport", lambda _: SimpleNamespace(discover=lambda: "account"))
    monkeypatch.setattr(cli, "CockroachCTraderDemoStore", lambda: "store")
    paper = {"position": -.5}
    monkeypatch.setattr(cli, "_paper_from_env", lambda: SimpleNamespace(state=lambda: paper))
    monkeypatch.setattr(cli, "CTraderDemoAdapter", lambda *args, **kwargs: kwargs)
    provider = cli._ctrader_demo_adapter()["expected_volume_provider"]
    assert provider() == -50
    paper["position"] = 0
    assert provider() == 0


def _isolated_bits_state(tmp_path, monkeypatch):
    # Never touch live notes: every CLI memory test uses its own SQLite file.
    path = str(tmp_path / 'isolated' / 'state.db')
    monkeypatch.setenv('XAUUSD_STATE_BACKEND', 'local')
    monkeypatch.setenv('STATE_DB_PATH', path)
    return path


def _run_cli(monkeypatch, capsys, *argv, stdin=None):
    import io
    import json
    monkeypatch.setattr('sys.argv', ['xauusd', *argv])
    if stdin is not None:
        monkeypatch.setattr('sys.stdin', io.StringIO(stdin))
    code = 0
    try:
        cli.main()
    except SystemExit as exc:
        code = exc.code
    captured = capsys.readouterr()
    return code, json.loads(captured.out), captured.err


def _wrapped_notes():
    notes = {key: [] for key in ('findings', 'hypotheses', 'rejected_approaches', 'open_questions', 'next_steps')}
    notes['findings'] = [{'text': "Weekly reproduction: 34 signals; it's unverified.",
                          'sources': ['53e4380f3e2e4b01b772a46da08601b5']}]
    return {'notes': notes}


def test_bits_memory_cli_writes_heredoc_input_and_reads_back_digest(tmp_path, monkeypatch, capsys):
    import json
    _isolated_bits_state(tmp_path, monkeypatch)
    code, saved, _ = _run_cli(monkeypatch, capsys, 'bits-memory', 'write', '--input-file', '-',
                              stdin=json.dumps(_wrapped_notes(), indent=2))
    assert code == 0 and saved['status'] == 'saved' and saved['input_form'] == 'notes_wrapper'
    assert saved['version'] == 1 and saved['digest'].startswith('sha256:')
    assert ' -m xauusd.cli bits-memory show --notes-only' in saved['read_back']
    code, stored, _ = _run_cli(monkeypatch, capsys, 'bits-memory', 'show', '--notes-only')
    assert code == 0 and stored['digest'] == saved['digest'] and stored['notes'] == _wrapped_notes()['notes']
    notes_file = tmp_path / 'notes.json'
    notes_file.write_text(json.dumps(_wrapped_notes()['notes']))
    code, again, _ = _run_cli(monkeypatch, capsys, 'bits-memory', 'write', '--input-file', str(notes_file))
    assert code == 0 and again['status'] == 'unchanged' and again['version'] == 1


def test_bits_memory_cli_rejection_is_structured_safe_and_keeps_notes(tmp_path, monkeypatch, capsys):
    import json
    _isolated_bits_state(tmp_path, monkeypatch)
    _run_cli(monkeypatch, capsys, 'bits-memory', 'write', '--input', json.dumps(_wrapped_notes()))
    mixed = {**_wrapped_notes(), 'findings': []}
    code, report, err = _run_cli(monkeypatch, capsys, 'bits-memory', 'write', '--input', json.dumps(mixed))
    assert code == 2 and report['status'] == 'rejected' and report['schema'] == 'xauusd.notes/1'
    assert report['error']['code'] == 'ambiguous_shape' and report['error']['path'] == '$'
    assert report['error']['retryable'] and 'expected' in report['error']
    assert report['pending']['attempts'] == 1 and report['pending']['notes_unchanged']
    assert 'BitsError' not in err and 'Traceback' not in err and 'unverified' not in json.dumps(report)
    code, pending, _ = _run_cli(monkeypatch, capsys, 'bits-memory', 'pending')
    assert code == 0 and pending['pending_notes']['payload'] == mixed
    assert pending['memory_status']['notes_version'] == 1
    code, report, _ = _run_cli(monkeypatch, capsys, 'bits-memory', 'write', '--input', '{}', '--input-file', '-')
    assert code == 2 and report['error']['code'] == 'conflicting_input'
    assert report['pending']['attempts'] == 2 and report['pending']['needs_repair']


def test_bits_memory_validate_and_schema_never_open_state(tmp_path, monkeypatch, capsys):
    import json
    from pathlib import Path
    path = _isolated_bits_state(tmp_path, monkeypatch)
    code, result, _ = _run_cli(monkeypatch, capsys, 'bits-memory', 'validate', '--input', json.dumps(_wrapped_notes()))
    assert code == 0 and result['status'] == 'valid'
    code, result, _ = _run_cli(monkeypatch, capsys, 'bits-memory', 'validate', '--input', '{"findings": []}')
    assert code == 2 and result['error']['code'] == 'missing_field'
    code, schema, _ = _run_cli(monkeypatch, capsys, 'bits-memory', 'schema')
    assert code == 0 and schema['schema'] == 'xauusd.notes/1'
    assert not Path(path).parent.exists()


def test_bits_job_errors_are_structured(tmp_path, monkeypatch, capsys):
    _isolated_bits_state(tmp_path, monkeypatch)
    code, result, _ = _run_cli(monkeypatch, capsys, 'bits-job', 'f' * 32)
    assert code == 2 and result['error']['code'] == 'unknown_job' and not result['error']['retryable']
    code, result, _ = _run_cli(monkeypatch, capsys, 'bits-job', 'f' * 32, '--limit', '0')
    assert code == 2 and result['error']['code'] == 'invalid_page_bounds'
