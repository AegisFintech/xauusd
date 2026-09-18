import pytest

from xauusd.ctrader_demo import (CTraderDemoAccount, CTraderDemoAdapter, CTraderDemoSafetyError,
    CTraderDemoOpenApiConfig, CTraderDemoOpenApiTransport, CTraderOrder, CTraderSymbolMetadata,
    InMemoryCTraderDemoStore)


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
