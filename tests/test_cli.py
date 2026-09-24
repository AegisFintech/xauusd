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
        return {"account_id": 7, "is_demo": self.is_demo, "symbol": "XAUUSD", "symbol_id": 99}


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
