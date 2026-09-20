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


def is_error(message: Any) -> tuple[str, str] | None:
    """Return ``(code, description)`` when a cTrader message carries an error, else None."""
    code = _field(message, "errorCode")
    if not code:
        return None
    return str(code), str(_field(message, "description") or "")


def demo_accounts(accounts: list[Any]) -> list[Any]:
    """Reduce a cTrader account list to non-live (demo) accounts."""
    return [account for account in accounts if not bool(_field(account, "isLive", True))]


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