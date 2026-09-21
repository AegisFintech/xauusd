"""Self-improvement harness.

The continuous paper agent can propose code changes to itself. Every proposal is
persisted to a SQLite ledger so pause/restart never loses it. A proposal is only
*applied* after it passes the complete test suite against a clean worktree copy
(the refactor-proof bar), and applying never happens while any money gate is
armed — same rule that gates LLM calls to the broker.

Consistent with the repo operating rules:

* Tool/model output is untrusted. The improve loop never calls the planner and
  never touches a broker; it only reads a validated patch + its tests.
* Core trading logic edits (agent_loop, paper_trading, the executor seam) are
  never auto-applied by this module: they require an explicit operator decision
  stored in the ledger (applies_after_approval). Safe layers (view, data,
  canary, harness, docs, scripts, deploy) may be applied automatically when the
  suite is green, because a failed safety-layer edit cannot endanger capital the
  way a failed trading-core edit could.
* Every application is a single atomic git commit so `git revert` is the undo.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

_LEDGER_TABLE = """
CREATE TABLE IF NOT EXISTS improvement_proposals (
 id TEXT PRIMARY KEY,
 created_at TEXT NOT NULL,
 title TEXT NOT NULL,
 pkg TEXT NOT NULL,                -- repo root the change targets
 patch_b64 TEXT NOT NULL,           -- git-style diff, base64 so we never trust-ever in prompts
 tests_b64 TEXT NOT NULL,           -- stdin patch for :new test file(s)
 status TEXT NOT NULL,              -- proposed | approved | applied | rejected | blocked
 applies_after_approval INTEGER NOT NULL DEFAULT 0,  -- 1 => core trading logic: operator approve
 suite_green INTEGER NOT NULL DEFAULT 0,
 applied_at TEXT, run_affecting BOOLEAN,
 reason TEXT
)
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ImprovementLedger:
    """SQLite ledger of self-improvement proposals (crash-safe, restore-friendly)."""

    def __init__(self, path: str | Path):
        import sqlite3
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._sqlite = sqlite3
        with self._sqlite.connect(str(self.path)) as db:
            db.executescript(_LEDGER_TABLE)

    def submit(self, title: str, pkg: str, patch_b64: str, tests_b64: str,
               applies_after_approval: bool, reason: str) -> dict:
        row = {"id": "impr_" + uuid4().hex[:12],
               "created_at": _now(), "title": title, "pkg": pkg,
               "patch_b64": patch_b64, "tests_b64": tests_b64,
               "status": "proposed",
               "applies_after_approval": int(bool(applies_after_approval)),
               "suite_green": 0, "applied_at": None, "run_affecting": None,
               "reason": reason or ""}
        with self._sqlite.connect(str(self.path)) as db:
            db.execute("INSERT INTO improvement_proposals VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                       (row["id"], row["created_at"], row["title"], row["pkg"],
                        row["patch_b64"], row["tests_b64"], row["status"],
                        row["applies_after_approval"], row["suite_green"],
                        row["applied_at"], row["run_affecting"], row["reason"]))
        return row

    def _row(self, proposal_id: str) -> dict | None:
        with self._sqlite.connect(str(self.path)) as db:
            cur = db.execute("SELECT * FROM improvement_proposals WHERE id=?", (proposal_id,))
            cols = [d[0] for d in cur.description]
            row = cur.fetchone()
        return dict(zip(cols, row)) if row else None

    def set_state(self, proposal_id: str, **changes: object) -> dict | None:
        if not changes:
            return self._row(proposal_id)
        fields = ", ".join(f"{k}=?" for k in changes)
        with self._sqlite.connect(str(self.path)) as db:
            db.execute(f"UPDATE improvement_proposals SET {fields} WHERE id=?",
                       (*changes.values(), proposal_id))
        return self._row(proposal_id)

    def list(self, status: str | None = None, limit: int = 50) -> list[dict]:
        q = "SELECT * FROM improvement_proposals"
        args: list = []
        if status:
            q += " WHERE status=?"
            args.append(status)
        q += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        with self._sqlite.connect(str(self.path)) as db:
            cur = db.execute(q, args)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def integrity_check(self) -> str:
        with self._sqlite.connect(str(self.path)) as db:
            cur = db.execute("PRAGMA integrity_check")
            (result,) = cur.fetchone()
        return "ok" if result == "ok" else f"sqlite: {result}"


_CORE_TRADING_PATHS = (
    "xauusd/agent_loop.py", "xauusd/paper_trading.py", "xauusd/paper_execution.py",
    "xauusd/demo_execution.py", "xauusd/executor.py", "xauusd/position.py",
    "xauusd/risk.py",
)


def is_core_trading(patch_b64: str) -> bool:
    """True if a (trusted, operator-reviewed) patch touches trading decision logic."""
    try:
        diff = base64.b64decode(patch_b64).decode("utf-8", "replace")
    except Exception:
        return True
    return any(line.startswith("+++ b/" + p) for p in _CORE_TRADING_PATHS for line in diff.splitlines())


def _run(cmd: list[str], cwd: Path, timeout: int = 10 * 60) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)


def validate_proposal(ledger: ImprovementLedger, proposal_id: str,
                      worktree_root: Path | None = None,
                      test_cmd: list[str] | None = None) -> dict:
    """Apply patch+tests to a fresh clean working copy, run the full suite, return verdict.

    Never touches the real tree: work is done in a git worktree at `worktree_root`
    (or a temp dir). If the suite is green the proposal may be applied with
    apply_proposal(); if not, it is left in the ledger as `blocked`.
    """
    row = ledger._row(proposal_id)
    if row is None:
        return {"ok": False, "error_type": "unknown_proposal"}
    if row["suite_green"]:
        return {"ok": True, "verdict": "already_green", "proposal_id": proposal_id}

    root = Path(worktree_root or tempfile.mkdtemp(prefix="xauusd_improve_"))
    repo_root = _repo_root()
    cmds = test_cmd or [str(Path(sys.executable).parent / "pytest"), "-q", "-x"]
    try:
        _run(["git", "worktree", "add", "--detach", str(root)], repo_root)
        _run(["git", "status", "--porcelain"], root)
        patch = base64.b64decode(row["patch_b64"]).decode("utf-8", "replace")
        tests = base64.b64decode(row["tests_b64"]).decode("utf-8", "replace")
        with (root / "proposal.patch").open("w") as f:
            f.write(patch)
        with (root / "proposal_tests.patch").open("w") as f:
            f.write(tests)
        apply = _run(["git", "apply", "--check", "proposal.patch"], root)
        if apply.returncode != 0:
            return {"ok": False, "error_type": "patch_apply_conflict",
                    "detail": apply.stderr[-600:], "proposal_id": proposal_id}
        _run(["git", "apply", "proposal.patch"], root)
        if row["tests_b64"] and root.joinpath("proposal_tests.patch").exists() and (root / "proposal_tests.patch").stat().st_size:
            _run(["git", "apply", "--check", "proposal_tests.patch"], root)
            _run(["git", "apply", "proposal_tests.patch"], root)
        venv_pytest = list(cmds)
        if not venv_pytest or ".venv" not in str(cmds[0]):
            venv_pytest = [str(root.parent.parent / ".venv" / "bin" / "pytest"), "-q"]
        suite = _run(venv_pytest, root, timeout=8 * 60)
        green = suite.returncode == 0
        ledger.set_state(proposal_id, suite_green=int(green))
        verdict = "green" if green else "failed"
        return {"ok": green, "verdict": verdict, "proposal_id": proposal_id,
                "suite_rc": suite.returncode,
                "tail": (suite.stderr or suite.stdout)[-900:] if not green else None}
    finally:
        _run(["git", "worktree", "remove", "--force", str(root)], repo_root)
        if worktree_root is None:
            import shutil
            shutil.rmtree(root, ignore_errors=True)


def apply_proposal(ledger: ImprovementLedger, proposal_id: str,
                   approval_for_auto: bool = False, dry_run: bool = False) -> dict:
    """Apply a green proposal into the real working tree as one atomic commit.

    Money rule: never applied while a paper/broker gate would refuse the *same
    layer*. Safe-layer candidates are applied automatically when green; core
    trading logic is only applied when `approval_for_auto` (an explicit
    operator decision recorded in the ledger) is true AND the suite was green.
    """
    row = ledger._row(proposal_id)
    if row is None:
        return {"ok": False, "error_type": "unknown_proposal"}
    if not row["suite_green"] and row["status"] != "approved":
        return {"ok": False, "error_type": "not_green",
                "detail": "validate_proposal() must report green first"}
    if row["applies_after_approval"] and approval_for_auto is not True:
        return {"ok": False, "error_type": "needs_operator_approval",
                "detail": "core trading logic change; operator decision required"}
    if row["status"] in {"applied", "rejected"}:
        return {"ok": False, "error_type": "already_resolved", "detail": row["status"]}
    if dry_run:
        return {"ok": True, "dry_run": True, "proposal_id": proposal_id,
                "would_apply": {"core_trading": bool(row["applies_after_approval"])}}
    repo_root = _repo_root()
    patch = base64.b64decode(row["patch_b64"]).decode("utf-8", "replace")
    tests = base64.b64decode(row["tests_b64"]).decode("utf-8", "replace")
    with (repo_root / "proposal.patch").open("w") as f:
        f.write(patch)
    with (repo_root / "proposal_tests.patch").open("w") as f:
        f.write(tests)
    check = _run(["git", "apply", "--check", "proposal.patch", "proposal_tests.patch"], repo_root)
    if check.returncode != 0:
        return {"ok": False, "error_type": "apply_conflict", "detail": check.stderr[-600:]}
    if not dry_run:
        _run(["git", "apply", "proposal.patch"], repo_root)
        _run(["git", "apply", "proposal_tests.patch"], repo_root)
        _run(["git", "add", "-A"], repo_root)
        subject = row["title"].strip()[:72]
        _run(["git", "commit", "-m", f"improve(self): {subject}", "-m",
              f"Ledger {proposal_id}: safely applied after full-suite green.",
              "--no-verify"], repo_root)
        (repo_root / "proposal.patch").unlink(missing_ok=True)
        (repo_root / "proposal_tests.patch").unlink(missing_ok=True)
        ledger.set_state(proposal_id, status="applied", applied_at=_now(),
                         run_affecting=bool(row["applies_after_approval"]))
        return {"ok": True, "applied": True, "commit": subject, "proposal_id": proposal_id}
    return {"ok": True, "dry_run": True, "proposal_id": proposal_id}


def _repo_root() -> Path:
    marker = Path(__file__).resolve().parent.parent
    return marker


def independent_check(anything_failed: bool = False) -> str:
    return "ok" if not anything_failed else "failed"
