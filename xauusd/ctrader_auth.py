"""Shared, pure cTrader Open API account and symbol selection helpers.

Used by both the fail-closed demo execution adapter and the read-only
historical downloader so account discovery and symbol resolution behave
identically in every data and execution path.
"""
from __future__ import annotations

from typing import Any

DEMO_HOST = "demo.ctraderapi.com"


def _field(value: Any, name: str, default: Any = None) -> Any:
    return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)


def _is_explicitly_demo(account: Any) -> bool:
    """True only when the broker positively reported this account as non-live.

    Presence has to be checked explicitly. ``isLive`` is a proto3 ``optional``
    (explicit-presence) field, so an account whose live/demo status the broker
    never sent reads back as ``False`` through ``getattr`` and a plain default
    argument is never consulted. Relying on that default therefore admits an
    account of unknown type, and account type is the one thing standing between
    this code and a live account.
    """
    if isinstance(account, dict):
        if "isLive" not in account:
            return False
        flag = account["isLive"]
    elif hasattr(account, "HasField"):
        try:
            if not account.HasField("isLive"):
                return False
        except ValueError:
            # Field without presence tracking: fall back to the value itself.
            pass
        flag = getattr(account, "isLive", None)
    else:
        if not hasattr(account, "isLive"):
            return False
        flag = account.isLive
    # Anything other than a definite false is unknown, and unknown is not demo.
    return flag is False


def is_error(message: Any) -> tuple[str, str] | None:
    """Return ``(code, description)`` when a cTrader message carries an error, else None."""
    code = _field(message, "errorCode")
    message_type = type(message).__name__
    if isinstance(message, dict):
        message_type = message.get("type", message_type)
    rejected = _field(message, "executionType") in (7, "ORDER_REJECTED")
    if not code and (message_type in {"ProtoOAErrorRes", "ProtoOAOrderErrorEvent", "ProtoErrorRes"} or rejected):
        code = "ORDER_REJECTED" if rejected else "BROKER_ERROR"
    if not code:
        return None
    return str(code), str(_field(message, "description") or "")


def demo_accounts(accounts: list[Any]) -> list[Any]:
    """Reduce a cTrader account list to non-live (demo) accounts.

    An account the broker did not classify is excluded, not admitted: see
    :func:`_is_explicitly_demo`.
    """
    return [account for account in accounts if _is_explicitly_demo(account)]


def resolve_symbol(symbols: list[Any], wanted: str) -> tuple[int, str] | None:
    """Return ``(symbol_id, symbol_name)`` for ``wanted``, or None when unavailable.

    Prefers an enabled match; falls back to the first matching symbol otherwise.
    """
    def clean(value: str) -> str:
        return "".join(char for char in str(value).upper() if char.isalnum())

    wanted_clean = clean(wanted)
    matches = [symbol for symbol in symbols if clean(_field(symbol, "symbolName", "")) == wanted_clean]
    if not matches:
        return None
    selected = next((value for value in matches if bool(_field(value, "enabled", False))), matches[0])
    symbol_id = _field(selected, "symbolId")
    symbol_name = _field(selected, "symbolName")
    if not isinstance(symbol_id, int) or isinstance(symbol_id, bool) or symbol_id <= 0:
        return None
    return int(symbol_id), str(symbol_name)