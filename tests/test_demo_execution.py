from datetime import datetime, timezone

import pytest

from xauusd.demo_execution import (CTraderVolumeConversion, CTraderVolumePolicy,
                                   NormalizedDecision, PaperToCTraderDemoCoordinator)
from xauusd.ctrader_demo import (CTraderDemoAccount, CTraderDemoAdapter,
                                 CTraderSymbolMetadata, InMemoryCTraderDemoStore)
from xauusd.paper_trading import InMemoryPaperTradingStore, PaperTrading, restart_policy


NOW = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)


class DemoAdapterDouble:
    def __init__(self, outcome=None, error=None):
        self.outcome = outcome or {"accepted": True, "request_id": "decision-1"}
        self.error = error
        self.orders = []
        self.stop_reasons = []
        self.start_calls = 0
        self.reconcile_calls = 0

    def execute(self, order):
        self.orders.append(order)
        if self.error:
            raise self.error
        return self.outcome

    def stop(self, reason):
        self.stop_reasons.append(reason)

    def start(self, reason):
        self.start_calls += 1

    def reconcile_after_restart(self):
        self.reconcile_calls += 1


def decision(identifier="decision-1", quantity=0.5):
    return NormalizedDecision(identifier, "XAUUSD", "BUY", quantity, NOW)


def coordinator(adapter):
    paper = PaperTrading(InMemoryPaperTradingStore())
    paper.start("test")
    return PaperToCTraderDemoCoordinator(paper, adapter, CTraderVolumeConversion(100)), paper


def test_risk_accepted_decision_uses_explicit_conversion_and_shared_id():
    adapter = DemoAdapterDouble()
    instance, _ = coordinator(adapter)

    result = instance.execute(decision(), 4000.0, NOW)

    assert result["accepted"]
    assert adapter.orders[0].request_id == "decision-1"
    assert adapter.orders[0].volume == 50
    assert adapter.start_calls == adapter.reconcile_calls == 0


def test_paper_rejection_never_submits_a_broker_request():
    adapter = DemoAdapterDouble()
    instance, paper = coordinator(adapter)
    paper.stop("risk session stopped")

    result = instance.execute(decision(), 4000.0, NOW)

    assert not result["accepted"]
    assert not adapter.orders
    assert not adapter.stop_reasons


class TransportDouble:
    def __init__(self):
        self.calls = []

    def send(self, request, timeout_seconds):
        self.calls.append(request)
        return {"account_id": 7, "is_demo": True, "symbol": "XAUUSD", "symbol_id": 99, "positions": [], "open_orders": []}


def test_duplicate_decision_cannot_produce_another_broker_request(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    transport = TransportDouble()
    adapter = CTraderDemoAdapter(CTraderDemoAccount(7, 99), InMemoryCTraderDemoStore(), transport)
    assert adapter.reconcile_after_restart()
    adapter.start("operator approved")
    instance, _ = coordinator(adapter)

    instance.execute(decision(), 4000.0, NOW)
    instance.execute(decision(), 4000.0, NOW)

    assert len(transport.calls) == 2  # One operator-triggered reconciliation and one order.


def test_broker_rejection_stops_paper_and_demo_kill_switches():
    adapter = DemoAdapterDouble({"accepted": False, "request_id": "decision-1", "reason": "REJECTED"})
    instance, paper = coordinator(adapter)

    result = instance.execute(decision(), 4000.0, NOW)

    assert not result["accepted"]
    assert paper.state()["stopped"]
    assert paper.state()["kill_switch_reason"] == "broker_execution_failed"
    assert adapter.stop_reasons == ["broker_execution_failed"]


def test_broker_error_stops_paper_and_demo_kill_switches():
    adapter = DemoAdapterDouble(error=RuntimeError("network unavailable"))
    instance, paper = coordinator(adapter)

    result = instance.execute(decision(), 4000.0, NOW)

    assert result["demo"]["reason"] == "BROKER_ERROR"
    assert paper.state()["stopped"]
    assert adapter.stop_reasons == ["broker_execution_failed"]


class SequencedTransport:
    """Replies in call order: the reconciliation first, then the order."""
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def send(self, request, timeout_seconds):
        self.calls.append(request)
        return self.responses.pop(0)


def test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = InMemoryCTraderDemoStore()
    transport = SequencedTransport({"account_id": 7, "is_demo": True, "symbol": "XAUUSD", "symbol_id": 99, "positions": [], "open_orders": []},
                                   {"status": "ProtoOAOrderErrorEvent", "error_code": "MARKET_CLOSED"})
    adapter = CTraderDemoAdapter(CTraderDemoAccount(7, 99), store, transport)
    assert adapter.reconcile_after_restart()
    adapter.start("operator approved")
    instance, paper = coordinator(adapter)

    result = instance.execute(decision(), 4000.0, NOW)

    assert result["accepted"] is False  # previously any reply, even an error, counted as accepted
    assert result["demo"]["reason"] == "BROKER_REJECTED"
    assert paper.state()["kill_switch_reason"] == "broker_execution_failed"
    assert paper.maybe_resume("unattended restart")["resumed"] is False
    assert restart_policy(store.state()) == "refuse"


def test_adapter_store_audits_the_broker_outcome(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = InMemoryCTraderDemoStore()
    adapter = CTraderDemoAdapter(CTraderDemoAccount(7, 99), store, TransportDouble())
    assert adapter.reconcile_after_restart()
    adapter.start("operator approved")
    instance, _ = coordinator(adapter)

    instance.execute(decision(), 4000.0, NOW)

    assert store.events[-1]["event"] == "paper_demo_execution_outcome"
    assert store.events[-1]["payload"]["decision_id"] == "decision-1"


def policy(minimum=10, maximum=1000, step=10):
    return CTraderVolumePolicy(minimum, maximum, step)


def test_volume_policy_rejects_below_minimum_before_paper_state_is_mutated():
    adapter = DemoAdapterDouble()
    instance, paper = coordinator(adapter)
    instance.volume_policy = policy()

    result = instance.execute(decision(quantity=0.05), 4000.0, NOW)

    assert not result["accepted"]
    assert result["reason"] == "VOLUME_POLICY"
    assert result["detail"] == "volume_below_broker_minimum"
    assert not adapter.orders
    assert not paper.state()["ledger"]


def test_volume_policy_rejects_above_maximum_without_broker_request():
    adapter = DemoAdapterDouble()
    instance, _ = coordinator(adapter)
    instance.volume_policy = policy()

    result = instance.execute(decision(quantity=15), 4000.0, NOW)

    assert result["detail"] == "volume_above_broker_maximum"
    assert not adapter.orders


def test_volume_policy_rejects_misaligned_step_without_broker_request():
    adapter = DemoAdapterDouble()
    instance, _ = coordinator(adapter)
    instance.volume_policy = policy(minimum=100)

    result = instance.execute(decision(quantity=1.05), 4000.0, NOW)

    assert result["detail"] == "volume_not_aligned_to_broker_step"
    assert not adapter.orders


def test_volume_policy_allows_accepted_volume_and_submits_broker_request():
    adapter = DemoAdapterDouble()
    instance, _ = coordinator(adapter)
    instance.volume_policy = policy(minimum=100)

    result = instance.execute(decision(quantity=1.0), 4000.0, NOW)

    assert result["accepted"]
    assert adapter.orders[0].volume == 100


def test_invalid_conversion_never_mutates_paper_state():
    adapter = DemoAdapterDouble()
    instance, paper = coordinator(adapter)

    result = instance.execute(decision(quantity=0.005), 4000.0, NOW)

    assert not result["accepted"]
    assert result["reason"] == "INVALID_VOLUME"
    assert not adapter.orders
    assert not paper.state()["ledger"]


def test_volume_policy_from_metadata():
    metadata = CTraderSymbolMetadata("XAUUSD", 42, digits=2, lot_size=100.0,
                                     min_volume=10, max_volume=1000, step_volume=10)

    instance = CTraderVolumePolicy.from_metadata(metadata)

    assert instance.min_volume == 10
    assert instance.max_volume == 1000
    assert instance.step_volume == 10


def test_paper_only_runs_without_adapter_or_volume_and_never_stops_switches():
    paper = PaperTrading(InMemoryPaperTradingStore())
    paper.start("test")
    instance = PaperToCTraderDemoCoordinator(paper, paper_only=True)

    result = instance.execute(decision(), 4000.0, NOW)

    assert result["paper_only"]
    assert result["paper"]["accepted"]
    assert result["demo"]["reason"] == "PAPER_ONLY_MODE"
    assert not result["accepted"]
    assert not paper.state()["stopped"]


def test_non_paper_only_requires_adapter_and_volume():
    paper = PaperTrading(InMemoryPaperTradingStore())
    with pytest.raises(ValueError, match="demo adapter"):
        PaperToCTraderDemoCoordinator(paper)
    with pytest.raises(ValueError, match="volume conversion"):
        PaperToCTraderDemoCoordinator(paper, DemoAdapterDouble())
