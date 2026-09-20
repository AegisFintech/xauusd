from types import SimpleNamespace

from xauusd.ctrader_auth import DEMO_HOST, demo_accounts, is_error, resolve_symbol


def account(account_id, is_live):
    return SimpleNamespace(ctidTraderAccountId=account_id, isLive=is_live)


def test_demo_host_is_the_only_allowed_host():
    assert DEMO_HOST == "demo.ctraderapi.com"


def test_demo_accounts_filters_live_and_missing_flag():
    accounts = demo_accounts([account(1, True), account(2, False), account(3, None)])
    assert [a.ctidTraderAccountId for a in accounts] == [2, 3]


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