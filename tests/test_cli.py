import sys

from xauusd import cli


def test_demo_automation_disabled_returns_status_without_constructing_clients(monkeypatch, capsys):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "false")
    monkeypatch.setattr(cli, "_demo_automation_runner", lambda config: (_ for _ in ()).throw(AssertionError("network setup")))
    monkeypatch.setattr(sys, "argv", ["xauusd", "demo-automation", "once"])

    cli.main()

    assert '"state": "disabled"' in capsys.readouterr().out


def test_demo_automation_requires_explicit_positive_volume(monkeypatch):
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
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

    monkeypatch.setattr(cli, "CockroachPaperTradingStore", FakeStore)
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
