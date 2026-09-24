import pytest

from xauusd.ctrader_demo import (BROKER_REJECTED, OUTCOME_UNKNOWN, CTraderDemoAccount, CTraderDemoAdapter,
    CTraderDemoSafetyError, CTraderDemoOpenApiConfig, CTraderDemoOpenApiTransport, CTraderOrder,
    CTraderSymbolMetadata, InMemoryCTraderDemoStore)
from xauusd.paper_trading import restart_policy


class Transport:
    def __init__(self, response=None, error=None):
        self.calls = []
        self.response = response or {"account_id": 7, "is_demo": True, "symbol": "XAUUSD", "symbol_id": 99}
        self.error = error

    def send(self, request, timeout_seconds):
        self.calls.append(request)
        if self.error:
            raise self.error
        return self.response


def adapter(monkeypatch, **account):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store, transport = InMemoryCTraderDemoStore(), Transport()
    return CTraderDemoAdapter(CTraderDemoAccount(7, 99, **account), store, transport), store, transport


def test_host_and_environment_rejections_are_fail_closed(monkeypatch):
    monkeypatch.delenv("CTRADER_DEMO_ONLY", raising=False)
    store = InMemoryCTraderDemoStore()
    with pytest.raises(CTraderDemoSafetyError, match="CTRADER_DEMO_ONLY"):
        CTraderDemoAdapter(CTraderDemoAccount(7, 99), store, Transport())
    assert store.state()["stopped"]
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    with pytest.raises(CTraderDemoSafetyError, match="restricted"):
        CTraderDemoAdapter(CTraderDemoAccount(7, 99, host="live.ctraderapi.com"), InMemoryCTraderDemoStore(), Transport())


def test_duplicate_request_never_sends_a_second_transport_call(monkeypatch):
    instance, store, transport = adapter(monkeypatch)
    assert instance.reconcile_after_restart()
    instance.start("operator approved")
    transport.response = {"execution_type": 3, "filled_volume": 100, "order_id": 1,
                          "position_id": 2, "broker_client_order_id": "request-1"}
    first = instance.execute(CTraderOrder("request-1", "BUY", 100))
    duplicate = instance.execute(CTraderOrder("request-1", "BUY", 100))
    assert first == duplicate
    assert len(transport.calls) == 2  # One reconciliation and one order.
    assert store.requests["request-1"]["status"] == "completed"
    assert store.events[-1]["event"] == "request_finished"


def test_recovery_failure_kills_and_blocks_execution(monkeypatch):
    instance, store, transport = adapter(monkeypatch)
    transport.response = {"account_id": 7, "is_demo": False, "symbol": "XAUUSD", "symbol_id": 99}
    assert not instance.reconcile_after_restart()
    assert store.state()["kill_switch_reason"] == "reconciliation_failed"
    result = instance.execute(CTraderOrder("request-2", "BUY", 100))
    assert result["reason"] == "KILL_SWITCH"
    assert len(transport.calls) == 1


def test_unresolved_pre_crash_request_fails_recovery_closed(monkeypatch):
    instance, store, _ = adapter(monkeypatch)
    store.reserve("pending-1", {"symbol": "XAUUSD"})
    assert not instance.reconcile_after_restart()
    assert store.state()["kill_switch_reason"] == "reconciliation_failed"


def test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(monkeypatch):
    instance, store, transport = adapter(monkeypatch)
    assert instance.reconcile_after_restart()
    instance.start("operator approved")
    transport.response = {"status": "ProtoOAOrderErrorEvent", "error_code": "NOT_ENOUGH_MONEY",
                          "description": "broker text is not persisted"}

    result = instance.execute(CTraderOrder("request-3", "BUY", 100))

    assert result == {"accepted": False, "reason": BROKER_REJECTED, "request_id": "request-3",
                      "response": {"status": "ProtoOAOrderErrorEvent", "error_code": "NOT_ENOUGH_MONEY"}}
    assert store.requests["request-3"]["status"] == "completed"
    assert not store.pending_request_ids()
    assert instance.execute(CTraderOrder("request-3", "BUY", 100)) == result  # no second broker call
    assert len(transport.calls) == 2


def test_transport_failure_is_an_unknown_outcome_that_blocks_restart(monkeypatch):
    instance, store, transport = adapter(monkeypatch)
    assert instance.reconcile_after_restart()
    instance.start("operator approved")
    transport.error = TimeoutError("cTrader request timed out")

    result = instance.execute(CTraderOrder("request-4", "BUY", 100))

    assert result["accepted"] is False
    assert result["reason"] == OUTCOME_UNKNOWN
    assert result["error_type"] == "TimeoutError"
    state = instance.state()
    assert state["stopped"] is True and state["kill_switch_reason"] == "transport_failure"
    assert restart_policy(state) == "refuse"  # never auto-resumed with unknown broker exposure


class ImmediateDeferred:
    def __init__(self, value): self.value = value
    def addCallbacks(self, succeeded, failed): succeeded(self.value)


class FakeClient:
    def __init__(self, responses): self.responses, self.requests, self.started = list(responses), [], False
    def startService(self): self.started = True
    def send(self, request, responseTimeoutInSeconds):
        self.requests.append(request)
        return ImmediateDeferred(self.responses.pop(0))


class Message:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)


def test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = FakeClient([
        {}, {}, {"symbol": [{"symbolName": "XAUUSD", "symbolId": 99, "enabled": True}]},
        {"order": [{"clientOrderId": "pending-1", "orderId": 123}]},
    ])
    messages = {name: Message for name in ("ProtoOAApplicationAuthReq", "ProtoOAAccountAuthReq",
                                            "ProtoOASymbolsListReq")}
    transport = CTraderDemoOpenApiTransport(
        CTraderDemoOpenApiConfig("id", "secret", "token", 7), client_factory=lambda host, port: client,
        extract=lambda value: value, message_types=messages,
    )
    assert transport.discover() == CTraderDemoAccount(7, 99)
    details = transport.send({"type": "ProtoOAReconcileReq"}, 1)
    assert details["request_outcomes"]["pending-1"]["response"]["order_id"] == 123
    assert client.started and len(client.requests) == 4
    assert not any(type(request).__name__ == "ProtoOAGetAccountListByAccessTokenReq" for request in client.requests)


def test_open_api_transport_reports_an_order_error_reply_with_its_code(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = FakeClient([
        {}, {}, {"symbol": [{"symbolName": "XAUUSD", "symbolId": 99, "enabled": True}]},
        {"errorCode": "TRADING_BAD_VOLUME", "description": "Invalid volume", "orderId": 5},
    ])
    messages = {name: Message for name in ("ProtoOAApplicationAuthReq", "ProtoOAAccountAuthReq",
                                            "ProtoOASymbolsListReq")}
    transport = CTraderDemoOpenApiTransport(
        CTraderDemoOpenApiConfig("id", "secret", "token", 7), client_factory=lambda host, port: client,
        extract=lambda value: value, message_types=messages,
    )

    receipt = transport.send({"type": "ProtoOANewOrderReq"}, 1)

    assert receipt["error_code"] == "TRADING_BAD_VOLUME"
    assert receipt["order_id"] == 5


def test_open_api_transport_fails_reconciliation_on_an_error_reply(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = FakeClient([
        {}, {}, {"symbol": [{"symbolName": "XAUUSD", "symbolId": 99, "enabled": True}]},
        {"errorCode": "CH_CLIENT_AUTH_FAILURE", "description": "Trading account is not authorized"},
    ])
    messages = {name: Message for name in ("ProtoOAApplicationAuthReq", "ProtoOAAccountAuthReq",
                                            "ProtoOASymbolsListReq")}
    transport = CTraderDemoOpenApiTransport(
        CTraderDemoOpenApiConfig("id", "secret", "token", 7), client_factory=lambda host, port: client,
        extract=lambda value: value, message_types=messages,
    )
    store = InMemoryCTraderDemoStore()
    instance = CTraderDemoAdapter(transport.discover(), store, transport, 1)

    # Previously an error reply carried no orders and passed as a clean reconciliation.
    assert not instance.reconcile_after_restart()
    assert store.state()["kill_switch_reason"] == "reconciliation_failed"
    assert store.events[-1]["payload"]["error_type"] == "CTraderDemoSafetyError"


def test_open_api_transport_rejects_non_demo_before_constructing_client(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    calls = []
    with pytest.raises(CTraderDemoSafetyError, match="restricted"):
        CTraderDemoOpenApiTransport(CTraderDemoOpenApiConfig("id", "secret", "token", 7, host="live.ctraderapi.com"),
                                    client_factory=lambda *args: calls.append(args))
    assert not calls


def test_open_api_transport_selects_the_only_authorized_demo_account(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = FakeClient([{}, {"ctidTraderAccount": [{"ctidTraderAccountId": 7, "isLive": False}]}, {},
                         {"symbol": [{"symbolName": "XAUUSD", "symbolId": 99, "enabled": True}]}])
    messages = {name: Message for name in ("ProtoOAApplicationAuthReq", "ProtoOAGetAccountListByAccessTokenReq",
                                            "ProtoOAAccountAuthReq", "ProtoOASymbolsListReq")}
    transport = CTraderDemoOpenApiTransport(CTraderDemoOpenApiConfig("id", "secret", "token"),
        client_factory=lambda host, port: client, extract=lambda value: value, message_types=messages)
    assert transport.discover() == CTraderDemoAccount(7, 99)


def test_open_api_transport_reads_symbol_volume_metadata(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = FakeClient([{}, {}, {"symbol": [{"symbolName": "XAUUSD", "symbolId": 99, "enabled": True}]},
                         {"symbol": [{"symbolName": "XAUUSD", "symbolId": 99, "digits": 2, "lotSize": 100.0,
                                      "minVolume": 10, "maxVolume": 1000, "stepVolume": 10}]}])
    messages = {name: Message for name in ("ProtoOAApplicationAuthReq", "ProtoOAAccountAuthReq",
                                            "ProtoOASymbolsListReq", "ProtoOASymbolByIdReq")}
    transport = CTraderDemoOpenApiTransport(CTraderDemoOpenApiConfig("id", "secret", "token", 7),
        client_factory=lambda host, port: client, extract=lambda value: value, message_types=messages)

    metadata = transport.symbol_metadata()

    assert metadata == CTraderSymbolMetadata("XAUUSD", 99, digits=2, lot_size=100.0,
                                             min_volume=10, max_volume=1000, step_volume=10)


def test_configured_account_id_bypasses_account_list_scope(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = FakeClient([{}, {}, {"symbol": [{"symbolName": "XAUUSD", "symbolId": 99, "enabled": True}]}])
    messages = {name: Message for name in ("ProtoOAApplicationAuthReq", "ProtoOAAccountAuthReq",
                                            "ProtoOASymbolsListReq")}
    transport = CTraderDemoOpenApiTransport(CTraderDemoOpenApiConfig("id", "secret", "token", 7),
        client_factory=lambda host, port: client, extract=lambda value: value, message_types=messages)

    assert transport.discover() == CTraderDemoAccount(7, 99)
    assert not any(type(request).__name__ == "ProtoOAGetAccountListByAccessTokenReq" for request in client.requests)


def test_symbol_metadata_and_volume_policy_validate_invariants():
    metadata = CTraderSymbolMetadata("XAUUSD", 99, digits=2, lot_size=100.0,
                                     min_volume=10, max_volume=1000, step_volume=10)
    metadata.validate()
    with pytest.raises(CTraderDemoSafetyError, match="restricted"):
        CTraderSymbolMetadata("EURUSD", 99, digits=2, lot_size=100.0,
                              min_volume=10, max_volume=1000, step_volume=10).validate()


def test_open_api_transport_surfaces_access_token_error(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = FakeClient([{}, {"errorCode": "CH_ACCESS_TOKEN_INVALID", "description": "Invalid access token"}])
    messages = {name: Message for name in ("ProtoOAApplicationAuthReq", "ProtoOAGetAccountListByAccessTokenReq")}
    transport = CTraderDemoOpenApiTransport(CTraderDemoOpenApiConfig("id", "secret", "token"),
        client_factory=lambda host, port: client, extract=lambda value: value, message_types=messages)
    with pytest.raises(CTraderDemoSafetyError, match=r"CH_ACCESS_TOKEN_INVALID.*Invalid access token"):
        transport.discover()


def test_symbol_detail_error_is_fail_closed(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    client = FakeClient([{}, {}, {"symbol": [{"symbolName": "XAUUSD", "symbolId": 99, "enabled": True}]},
                         {"errorCode": "CH_UNKNOWN", "description": "symbol detail failure"}])
    messages = {name: Message for name in ("ProtoOAApplicationAuthReq", "ProtoOAAccountAuthReq",
                                            "ProtoOASymbolsListReq", "ProtoOASymbolByIdReq")}
    transport = CTraderDemoOpenApiTransport(CTraderDemoOpenApiConfig("id", "secret", "token", 7),
        client_factory=lambda host, port: client, extract=lambda value: value, message_types=messages)
    with pytest.raises(CTraderDemoSafetyError, match=r"symbol detail error CH_UNKNOWN"):
        transport.symbol_metadata()


def test_long_decision_id_is_persisted_but_broker_id_fits(monkeypatch):
    from xauusd.ctrader_demo import broker_client_order_id, build_new_order_request
    instance, store, transport = adapter(monkeypatch)
    assert instance.reconcile_after_restart()
    instance.start("test")
    original = "a" * 64
    order = CTraderOrder(original, "BUY", 100)
    request = build_new_order_request(instance.account, order)
    assert len(request.clientOrderId) <= 50
    assert request.clientOrderId == broker_client_order_id(original)
    assert request.clientOrderId != broker_client_order_id("b" * 64)
    instance.execute(order)
    assert store.requests[original]["request"]["broker_client_order_id"] == request.clientOrderId
    assert broker_client_order_id("legacy-1") == "legacy-1"


def test_reconcile_maps_persisted_broker_id_back_to_internal_id(monkeypatch):
    from xauusd.ctrader_demo import broker_client_order_id
    instance, store, transport = adapter(monkeypatch)
    original = "c" * 64
    broker_id = broker_client_order_id(original)
    store.reserve(original, {"broker_client_order_id": broker_id})
    transport.response["request_outcomes"] = {broker_id: {"accepted": False, "reason": "BROKER_REJECTED"}}
    assert instance.reconcile_after_restart()
    assert store.requests[original]["outcome"]["request_id"] == original
