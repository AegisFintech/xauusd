from types import SimpleNamespace

from xauusd.ctrader_auth import DEMO_HOST, demo_accounts, is_error, resolve_symbol


def account(account_id, is_live):
    return SimpleNamespace(ctidTraderAccountId=account_id, isLive=is_live)


def test_demo_host_is_the_only_allowed_host():
    assert DEMO_HOST == "demo.ctraderapi.com"


def test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo():
    """An unclassified account is not a demo account.

    ``isLive`` is a proto3 optional field, so an account whose live/demo status
    the broker never sent reads back as ``False`` and the old ``True`` default
    was never consulted. Unknown type used to be admitted, and account type is
    the only thing separating this code from a live account.
    """
    accounts = demo_accounts([account(1, True), account(2, False), account(3, None)])
    assert [a.ctidTraderAccountId for a in accounts] == [2]


def test_demo_accounts_excludes_a_dict_without_the_flag():
    assert demo_accounts([{"ctidTraderAccountId": 5}]) == []
    assert demo_accounts([{"ctidTraderAccountId": 5, "isLive": None}]) == []
    assert demo_accounts([{"ctidTraderAccountId": 5, "isLive": False}]) == [{"ctidTraderAccountId": 5, "isLive": False}]


def test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account():
    """The discriminator has to work on the actual SDK message, not just dicts."""
    from ctrader_open_api.messages.OpenApiModelMessages_pb2 import ProtoOACtidTraderAccount

    unclassified = ProtoOACtidTraderAccount(ctidTraderAccountId=1)
    demo = ProtoOACtidTraderAccount(ctidTraderAccountId=2, isLive=False)
    live = ProtoOACtidTraderAccount(ctidTraderAccountId=3, isLive=True)

    assert unclassified.HasField("isLive") is False
    assert [a.ctidTraderAccountId for a in demo_accounts([unclassified, demo, live])] == [2]


def test_demo_accounts_empty_when_all_live():
    assert demo_accounts([account(1, True)]) == []


def test_resolve_symbol_prefers_enabled_match():
    symbols = [SimpleNamespace(symbolName="EURUSD", symbolId=1, enabled=False),
               SimpleNamespace(symbolName="XAUUSD", symbolId=2, enabled=True),
               SimpleNamespace(symbolName="XAUUSD.sp", symbolId=3, enabled=False)]
    assert resolve_symbol(symbols, "xau usd") == (2, "XAUUSD")


def test_resolve_symbol_falls_back_to_first_match():
    symbols = [SimpleNamespace(symbolName="XAUUSD", symbolId=7, enabled=True),
               SimpleNamespace(symbolName="XAUUSD", symbolId=8, enabled=True)]
    assert resolve_symbol(symbols, "XAUUSD") == (7, "XAUUSD")


def test_resolve_symbol_returns_none_when_absent():
    symbols = [SimpleNamespace(symbolName="EURUSD", symbolId=1, enabled=True)]
    assert resolve_symbol(symbols, "XAUUSD") is None


def test_resolve_symbol_rejects_invalid_id():
    symbols = [SimpleNamespace(symbolName="XAUUSD", symbolId="2", enabled=True)]
    assert resolve_symbol(symbols, "XAUUSD") is None


def test_is_error_extracts_code_and_description():
    assert is_error(SimpleNamespace(errorCode="X", description="d")) == ("X", "d")


def test_is_error_none_when_clear():
    assert is_error(SimpleNamespace(errorCode="", description="d")) is None
    assert is_error(SimpleNamespace(errorCode=None, description="d")) is None
    assert is_error(SimpleNamespace(errorCode="X")) == ("X", "")