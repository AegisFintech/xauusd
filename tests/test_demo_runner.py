import json
from datetime import datetime, timedelta, timezone

from xauusd.demo_execution import CTraderVolumeConversion, PaperToCTraderDemoCoordinator
from xauusd.demo_runner import DemoAutomationRunner, DemoRunnerConfig, MarketData
from xauusd.paper_trading import InMemoryPaperTradingStore, PaperTrading


NOW = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)


class Adapter:
    def __init__(self, reconciled=True):
        self.reconciled = reconciled
        self.start_reasons = []
        self.stop_reasons = []

    def reconcile_after_restart(self):
        return self.reconciled

    def start(self, reason):
        self.start_reasons.append(reason)

    def stop(self, reason):
        self.stop_reasons.append(reason)

    def execute(self, order):
        return {"accepted": True, "request_id": order.request_id}


class MarketSource:
    def __init__(self, value=None, error=None):
        self.value = value or MarketData(4000.0, NOW)
        self.error = error

    def read(self):
        if self.error:
            raise self.error
        return self.value


class DecisionSource:
    def __init__(self, decision=None):
        self.decision = decision
        self.calls = 0

    def read(self, market_data):
        self.calls += 1
        return self.decision


def runner(tmp_path, *, enabled=True, reconciled=True, market=None, decisions=None, failures=1):
    paper = PaperTrading(InMemoryPaperTradingStore())
    adapter = Adapter(reconciled)
    coordinator = PaperToCTraderDemoCoordinator(paper, adapter, CTraderVolumeConversion(100))
    instance = DemoAutomationRunner(
        coordinator, market or MarketSource(), decisions or DecisionSource(),
        DemoRunnerConfig(enabled, 1, failures, 60, tmp_path / "runner-status.json"), clock=lambda: NOW,
    )
    return instance, paper, adapter


def test_disabled_config_does_not_reconcile_or_start(tmp_path):
    instance, paper, adapter = runner(tmp_path, enabled=False)

    assert not instance.start()
    assert not adapter.start_reasons
    assert not adapter.stop_reasons
    assert paper.state()["stopped"]


def test_environment_config_is_disabled_unless_explicitly_true(monkeypatch):
    monkeypatch.delenv("CTRADER_AUTOMATION_ENABLED", raising=False)

    assert not DemoRunnerConfig.from_env().enabled
    monkeypatch.setenv("CTRADER_AUTOMATION_ENABLED", "true")
    assert DemoRunnerConfig.from_env().enabled


def test_startup_reconciliation_failure_stops_paper_and_demo(tmp_path):
    instance, paper, adapter = runner(tmp_path, reconciled=False)

    assert not instance.start()
    assert paper.state()["stopped"]
    assert adapter.stop_reasons == ["startup_reconciliation_failed"]


def test_stale_market_data_and_no_decision_do_not_execute(tmp_path):
    stale = MarketSource(MarketData(4000.0, NOW - timedelta(seconds=61)))
    instance, _, adapter = runner(tmp_path, market=stale)
    assert instance.start()
    assert instance.run_cycle()["state"] == "stale_market_data"
    assert not adapter.stop_reasons

    instance, _, adapter = runner(tmp_path, decisions=DecisionSource())
    assert instance.start()
    assert instance.run_cycle()["state"] == "no_decision"
    assert not adapter.stop_reasons


def test_cycle_failure_stops_after_configured_consecutive_failures(tmp_path):
    instance, paper, adapter = runner(tmp_path, market=MarketSource(error=RuntimeError("offline")), failures=1)
    assert instance.start()

    assert instance.run_cycle()["state"] == "stopped"
    assert paper.state()["stopped"]
    assert adapter.stop_reasons == ["max_consecutive_failures"]


def test_status_artifact_is_persistent_and_records_terminal_state(tmp_path):
    instance, _, _ = runner(tmp_path, market=MarketSource(error=RuntimeError("offline")))
    assert instance.start()
    instance.run_cycle()

    status = json.loads((tmp_path / "runner-status.json").read_text())
    assert status["state"] == "stopped"
    assert status["reason"] == "max_consecutive_failures"
    assert not status["running"]
