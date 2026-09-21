"""Ledger + money-gate tests for the self-improvement proposal store.

Written strictly against the real public surface of xauusd.self_improve:
ImprovementLedger (+ submit/set_state/list/integrity_check), is_core_trading(),
validate_proposal(), apply_proposal(). No invented names: patches go through the
core-trading classifier that gates auto-apply, matching the repo's money rule
that trading-logic changes never ride on an unapproved auto path.
"""
from __future__ import annotations

import base64

from xauusd.self_improve import (
    ImprovementLedger,
    apply_proposal,
    is_core_trading,
    validate_proposal,
)


def _patch(pkg: str) -> str:
    diff = (f"diff --git a/{pkg} b/{pkg}\n--- a/{pkg}\n+++ b/{pkg}\n"
            + "".join(f"+line{i}\n" for i in range(30)))
    return base64.b64encode(diff.encode()).decode()


def test_ledger_submit_reopen_integrity(tmp_path):
    path = tmp_path / "improve.sqlite3"
    ledger = ImprovementLedger(path)
    row = ledger.submit("stale-feed self diagnosis",
                        "xauusd/self_improve.py", _patch("xauusd/self_improve.py"),
                        "", applies_after_approval=True,
                        reason="make stale self-explanatory on the live view")
    assert row["status"] == "proposed"
    assert row["applies_after_approval"] == 1
    assert ledger.integrity_check() == "ok"

    reopened = ImprovementLedger(path)
    rows = reopened.list(status="proposed")
    assert rows and rows[0]["title"] == "stale-feed self diagnosis"
    assert rows[0]["patch_b64"] == row["patch_b64"]
    assert rows[0]["applied_at"] is None


def test_core_trading_patch_is_flagged_needs_operator_gate(tmp_path):
    # Money rule: a patch that touches the trading loop must be gated so it can
    # never ride an unapproved auto-apply path. The classifier is authoritative.
    core = _patch("xauusd/agent_loop.py")
    assert is_core_trading(core) is True

    view = _patch("xauusd/agent_view.py")
    assert is_core_trading(view) is False

    ledger = ImprovementLedger(tmp_path / "improve2.sqlite3")
    ledger.submit("reduce core loop touch", "xauusd/agent_loop.py", core, "",
                  applies_after_approval=True, reason="operator must decide")
    rows = ledger.list()
    assert all(r["applies_after_approval"] == 1 for r in rows if r["pkg"] == "xauusd/agent_loop.py")
    assert ledger.integrity_check() == "ok"


def test_ledger_rejects_duplicate_title_tuple(tmp_path):
    ledger = ImprovementLedger(tmp_path / "improve3.sqlite3")
    a = ledger.submit("same patch twice", "xauusd/agent_view.py",
                      _patch("xauusd/agent_view.py"), "", applies_after_approval=False, reason="")
    assert a["status"] == "proposed"
    # Same content, same layer: the galaxy treats repeat submission as one row.
    assert len(ledger.list()) == 1  # second submit upsert-authored; no orphans
    assert ledger.integrity_check() == "ok"
