"""Broker-free lifecycle sequences: the first correlated response is not necessarily a fill."""
from types import SimpleNamespace

import pytest

from xauusd.ctrader_auth import is_error
from xauusd.ctrader_demo import (CTraderDemoAccount, CTraderDemoAdapter, CTraderDemoOpenApiConfig,
    CTraderDemoOpenApiTransport, CTraderOrder, InMemoryCTraderDemoStore, OUTCOME_UNKNOWN,
    build_new_order_request)


class Reactor:
    running = True
    def callFromThread(self, fn): fn()


def event(kind, volume=0, account=7, client_id="decision", code=None):
    value = {"ctidTraderAccountId": account, "executionType": kind,
             "order": {"clientOrderId": client_id, "orderId": 20, "executedVolume": volume},
             "position": {"positionId": 30}, "deal": {"dealId": 40}}
    if code is not None: value["errorCode"] = code
    return value


class Client:
    def __init__(self, events): self.events = events; self.calls = 0
    def startService(self): pass
    def setMessageReceivedCallback(self, fn): self.callback = fn
    def send(self, request, clientMsgId, responseTimeoutInSeconds):
        self.calls += 1
        owner = self
        class Deferred:
            def addCallbacks(self, success, failure):
                for i, value in enumerate(owner.events):
                    envelope = SimpleNamespace(clientMsgId=clientMsgId, value=value)
                    owner.callback(owner, envelope)
                    if i == 0: success(envelope)
        return Deferred()


def setup(monkeypatch, events):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = Client(events)
    transport = CTraderDemoOpenApiTransport(CTraderDemoOpenApiConfig("id", "secret", "token", 7),
        client_factory=lambda *_: client, reactor=Reactor(), extract=lambda envelope: envelope.value)
    transport._account = CTraderDemoAccount(7, 99)
    store = InMemoryCTraderDemoStore()
    adapter = CTraderDemoAdapter(transport._account, store, transport, .01)
    store.mark_reconciled({})
    adapter.start("test")
    return adapter, store, client


def test_acceptance_then_partial_then_fill(monkeypatch):
    adapter, store, client = setup(monkeypatch, [event(2), event(11, 40), event(3, 100)])
    outcome = adapter.execute(CTraderOrder("decision", "BUY", 100))
    assert outcome["accepted"]
    assert [x["execution_type"] for x in outcome["response"]["events"]] == [2, 11, 3]
    assert outcome["response"]["deal_id"] == 40
    assert not store.pending_request_ids()
    assert adapter.execute(CTraderOrder("decision", "BUY", 100)) == outcome
    assert client.calls == 1


@pytest.mark.parametrize("events", [[event(2)], [event(2), event(11, 40)],
    [event(3, 50)], [event(3, 100, account=8)], [event(99)]])
def test_incomplete_or_invalid_execution_stays_pending(monkeypatch, events):
    adapter, store, client = setup(monkeypatch, events)
    outcome = adapter.execute(CTraderOrder("decision", "BUY", 100))
    assert outcome["reason"] == OUTCOME_UNKNOWN
    assert store.pending_request_ids() == ["decision"]
    assert store.state()["stopped"]
    adapter.execute(CTraderOrder("decision", "BUY", 100))
    assert client.calls == 1


def test_rejection_without_error_code_is_not_a_fill(monkeypatch):
    adapter, store, _ = setup(monkeypatch, [event(2), event(7)])
    outcome = adapter.execute(CTraderOrder("decision", "BUY", 100))
    assert outcome["reason"] == "BROKER_REJECTED"
    assert not store.pending_request_ids()


def test_partial_fill_followed_by_rejection_requires_reconciliation(monkeypatch):
    adapter, store, _ = setup(monkeypatch, [event(11, 40), event(7)])
    assert adapter.execute(CTraderOrder("decision", "BUY", 100))["reason"] == OUTCOME_UNKNOWN
    assert store.pending_request_ids() == ["decision"]


def test_real_protobuf_error_types_with_empty_codes():
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (
        ProtoOAErrorRes, ProtoOAOrderErrorEvent, ProtoOAExecutionEvent)
    for message in [ProtoOAErrorRes(errorCode=""),
                    ProtoOAOrderErrorEvent(ctidTraderAccountId=7, errorCode=""),
                    ProtoOAExecutionEvent(ctidTraderAccountId=7, executionType=7)]:
        assert message.IsInitialized()
        assert is_error(message) is not None
