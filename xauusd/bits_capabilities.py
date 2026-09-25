"""Safe description of the environment that runs Bits shell jobs.

Guidance must name the interpreter that is actually running this code rather
than a bare ``python`` or a standalone ``bits-memory`` executable: service shells
run ``/bin/bash -c`` without a login profile, so neither is guaranteed to exist on
``PATH``. ``shell_environment`` is the single definition of the shell-job
environment, and the capability manifest is computed from that same function, so
discovery reflects what a job will actually see rather than an interactive shell.

The manifest lists paths, versions and supported operations. It never includes
environment variable values other than the resulting search ``PATH``.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys

CAPABILITIES_SCHEMA = "xauusd.capabilities/1"
SHELL = "/bin/bash"
EXTRA_PATH_ENV = "BITS_SHELL_EXTRA_PATH"
VERSION_TIMEOUT_SECONDS = 3
MAX_OBSERVED = 10
PROMPT_PATH_ENTRIES = 12
REFRESHED_TOKENS = ("CTRADER_ACCESS_TOKEN", "CTRADER_REFRESH_TOKEN")
# Optional tools. Only tools with a standard --version flag are probed; an unknown
# CLI is never run speculatively. Fallbacks keep work possible when one is absent.
TOOLS = {
    "graphify": {"purpose": "scoped code-graph queries (graphify query/path/explain)", "probe": False,
                 "fallback": "Read graphify-out/GRAPH_REPORT.md for architecture and search code with "
                             "grep -rnE PATTERN xauusd tests docs."},
    "rg": {"purpose": "fast text search", "probe": True,
           "fallback": "grep -rnE PATTERN xauusd tests docs (scope searches; never scan data/ or reports/ wholesale)."},
    "git": {"purpose": "code provenance and history", "probe": True,
            "fallback": "Record sha256 digests of producer files with the service Python interpreter."},
    "grep": {"purpose": "text search fallback", "probe": True,
             "fallback": "Search files with the service Python interpreter (pathlib and re)."},
}
_MISSING_COMMAND = re.compile(
    r"(?m)^(?:/usr)?(?:/bin/)?bash(?:: line \d+)?: ([A-Za-z0-9_.+-]{1,64}): command not found\s*$")
# How a '#!/usr/bin/env NAME' script (or 'env NAME') fails when NAME is not on PATH.
_MISSING_ENV_COMMAND = re.compile(
    r"(?m)^(?:/usr)?/bin/env: ['\u2018]?([A-Za-z0-9_.+-]{1,64})['\u2019]?: No such file or directory\s*$")


def python_executable() -> str:
    """Absolute path of the running interpreter (the service virtualenv)."""
    return sys.executable or "python3"


def cli_prefix() -> str:
    """Complete, shell-quoted command prefix for this repository's CLI."""
    return shlex.quote(python_executable()) + " -m xauusd.cli"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _in_virtualenv() -> bool:
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def shell_path(base_env: dict) -> tuple[str, dict]:
    """Deterministic search PATH: service virtualenv, declared extras, then inherited entries."""
    entries: list[str] = []
    prepended: list[dict] = []
    ignored: list[dict] = []

    def add(entry: str, origin: str) -> None:
        if entry and entry not in entries:
            entries.append(entry)
            if origin != "inherited":
                prepended.append({"entry": entry, "origin": origin})
    if _in_virtualenv():
        add(str(Path(python_executable()).parent), "service_virtualenv")
    for raw in (base_env.get(EXTRA_PATH_ENV) or "").split(os.pathsep):
        raw = raw.strip()
        if not raw:
            continue
        if not os.path.isabs(raw):
            ignored.append({"entry": raw, "reason": "not_absolute"})
        elif not os.path.isdir(raw):
            ignored.append({"entry": raw, "reason": "not_a_directory"})
        else:
            add(os.path.normpath(raw), EXTRA_PATH_ENV)
    inherited = base_env.get("PATH")
    for raw in (inherited if inherited is not None else os.defpath).split(os.pathsep):
        add(raw, "inherited")
    return os.pathsep.join(entries), {"entries": entries, "prepended": prepended, "ignored": ignored,
                                      "inherited_from": "PATH" if inherited is not None else "os.defpath"}


def _prepare(base: dict | None, env_file: str) -> tuple[dict, dict]:
    env = dict(os.environ if base is None else base)
    try:
        from dotenv import dotenv_values
        latest = dotenv_values(env_file) if Path(env_file).is_file() else {}
    except Exception:
        latest = {}
    # Refreshed OAuth tokens are persisted to .env by the downloader; jobs see the latest pair.
    for key in REFRESHED_TOKENS:
        if latest.get(key):
            env[key] = latest[key]
    env["PATH"], report = shell_path(env)
    return env, report


def shell_environment(base: dict | None = None, env_file: str = ".env") -> dict:
    """The environment every Bits shell job runs with."""
    return _prepare(base, env_file)[0]


def _version(executable: str, env: dict, cwd: str) -> str | None:
    try:
        done = subprocess.run([executable, "--version"], env=env, cwd=cwd, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, errors="replace", timeout=VERSION_TIMEOUT_SECONDS)
    except (OSError, subprocess.SubprocessError):
        return None
    for line in (done.stdout + "\n" + done.stderr).splitlines():
        if line.strip():
            return line.strip()[:120]
    return None


def cli_commands() -> list[str] | None:
    try:
        from .cli import build_parser
        return list(build_parser().subcommands)
    except Exception:
        return None


def operations(cli: str | None = None) -> dict:
    """Complete, copyable command forms for the supported Bits operations."""
    from .bits_memory import memory_commands
    cli = cli or cli_prefix()
    memory = memory_commands(cli)
    return {"read_market": f"{cli} agent-tool read_market",
            "paper_state": f"{cli} agent-tool paper_state",
            "propose_trade": f"{cli} agent-tool propose_trade --input "
                             "'{\"side\":\"BUY|SELL\",\"quantity\":QUANTITY,\"reason\":\"evidence-linked reason\"}'",
            "job_output": memory["job_output"],
            "notes_schema": memory["schema"], "notes_show": memory["show_notes"],
            "notes_validate": memory["validate"], "notes_write": memory["write"], "notes_pending": memory["pending"],
            "capabilities": f"{cli} bits-capabilities",
            "data_validate": f"{cli} data validate"}


def data_access(cwd: str) -> dict:
    """Where the M1 data lives and how to read it with the real data API."""
    python = shlex.quote(python_executable())
    try:
        from .data import REQUIRED, HistoricalDataStore
        store = HistoricalDataStore()
        path = store.path if store.path.is_absolute() else Path(cwd) / store.path
        return {"entry_point": "xauusd.data.HistoricalDataStore", "path": str(store.path), "exists": path.is_file(),
                "format": "parquet", "symbol": store.config.symbol, "timeframe": store.config.timeframe,
                "index": "timestamp (UTC, bar open time)", "columns": list(REQUIRED),
                "read_example": python + " -c \"from xauusd.data import HistoricalDataStore as S; s=S(); "
                                         "bars=s.normalize(s.read()); print(bars.tail(3))\"",
                "backtester": "xauusd.engine.EventDrivenBacktester",
                "market_session": "xauusd.paper_trading.market_is_open (New York session; the UTC break "
                                  "moves with US daylight time)"}
    except Exception as exc:
        from .bits import error_details
        return {"entry_point": "xauusd.data.HistoricalDataStore", "available": False,
                "error_code": error_details(exc)["error_code"]}


def missing_executables(result: dict) -> list[str]:
    """Names bash (or /usr/bin/env) reported as not found in a completed job's stderr."""
    stderr = str(result.get("stderr") or "")
    return sorted(set(_MISSING_COMMAND.findall(stderr)) | set(_MISSING_ENV_COMMAND.findall(stderr)))[:5]


def _fallback(name: str) -> str | None:
    if name in TOOLS:
        return TOOLS[name]["fallback"]
    if name in ("python", "python3", "pip", "pip3"):
        return "Use " + shlex.quote(python_executable()) + (" -m pip" if name.startswith("pip") else "")
    if name.startswith("bits-") or name in ("agent-tool", "xauusd"):
        return "Run it through " + cli_prefix() + " " + (name if name != "xauusd" else "SUBCOMMAND")
    return None


def observed_view(observed: dict | None, search_path: str) -> list[dict]:
    rows = []
    for name, seen in sorted((observed or {}).items(), key=lambda item: item[1].get("last_seen", ""), reverse=True):
        found = shutil.which(name, path=search_path)
        rows.append({"name": name, **seen, "now_available": bool(found), "path": found, "fallback": _fallback(name)})
    return rows[:MAX_OBSERVED]


def record_observed(observed: dict | None, names: list[str], job_id: str) -> dict:
    """Bounded, persistent record of executables a real job could not find."""
    observed = dict(observed or {})
    now = _now()
    for name in names:
        seen = dict(observed.get(name) or {"first_seen": now, "count": 0})
        if seen.get("job_id") == job_id:
            continue  # the same job observed again (a retried tick) is not a new occurrence
        seen.update(last_seen=now, job_id=job_id, count=int(seen.get("count", 0)) + 1)
        observed[name] = seen
    return dict(sorted(observed.items(), key=lambda item: item[1]["last_seen"], reverse=True)[:MAX_OBSERVED])


def build_manifest(base: dict | None = None, cwd: str | None = None, observed: dict | None = None,
                   env_file: str = ".env") -> dict:
    env, path_report = _prepare(base, env_file)
    cwd = os.path.abspath(cwd or os.getcwd())
    search = env["PATH"]
    tools = {}
    for name, spec in TOOLS.items():
        found = shutil.which(name, path=search)
        tool = {"available": bool(found), "path": found, "purpose": spec["purpose"],
                "version": _version(found, env, cwd) if found and spec["probe"] else None}
        if not found:
            tool["fallback"] = spec["fallback"]
        tools[name] = tool
    python = python_executable()
    bare = shutil.which("python", path=search)
    required = {"bash": os.access(SHELL, os.X_OK), "python": os.path.isabs(python) and os.access(python, os.X_OK)}
    return {"schema": CAPABILITIES_SCHEMA, "generated_at": _now(), "cwd": cwd,
            "shell": {"path": SHELL, "available": required["bash"],
                      "invocation": SHELL + " -c COMMAND: non-login and non-interactive, so no profile or rc file is read"},
            "python": {"path": python, "version": platform.python_version(), "virtualenv": _in_virtualenv(),
                       "cli_prefix": cli_prefix(), "bare_python": bare,
                       "bare_python_is_service_interpreter": bool(bare) and Path(bare).parent == Path(python).parent},
            "path": path_report, "tools": tools,
            "required_missing": [name for name, ok in required.items() if not ok],
            "operations": operations(), "cli_commands": cli_commands(), "data": data_access(cwd),
            "observed_missing": observed_view(observed, search),
            "note": "Computed from the shell-job environment. Interactive shells may differ; use absolute "
                    "paths and the listed fallbacks."}


def minimal_manifest(error_code: str) -> dict:
    """Used when discovery itself fails: diagnostics must never block the agent."""
    python = python_executable()
    return {"schema": CAPABILITIES_SCHEMA, "generated_at": _now(), "cwd": os.path.abspath(os.getcwd()),
            "error_code": error_code,
            "shell": {"path": SHELL, "available": os.access(SHELL, os.X_OK),
                      "invocation": SHELL + " -c COMMAND: non-login and non-interactive"},
            "python": {"path": python, "version": platform.python_version(), "virtualenv": _in_virtualenv(),
                       "cli_prefix": cli_prefix(), "bare_python": None, "bare_python_is_service_interpreter": False},
            "path": {"entries": [], "prepended": [], "ignored": [], "inherited_from": None},
            "tools": {}, "required_missing": [], "operations": {}, "cli_commands": None,
            "data": {}, "observed_missing": [], "note": "Capability discovery failed; use absolute paths."}


def prompt_view(manifest: dict) -> dict:
    """Compact per-cycle facts. Memory commands already appear in history.policy; the
    subcommand list, versions and other detail stay in the stored manifest."""
    tools = {name: ({"available": True, "path": tool["path"]} if tool["available"]
                    else {"available": False, "fallback": tool.get("fallback")})
             for name, tool in manifest["tools"].items()}
    ops = {key: value for key, value in manifest["operations"].items() if not key.startswith("notes_")}
    data = {key: manifest["data"][key] for key in ("entry_point", "path", "exists", "index", "read_example")
            if key in manifest["data"]}
    entries = manifest["path"]["entries"]
    return {"generated_at": manifest["generated_at"], "cwd": manifest["cwd"],
            "cli_prefix": manifest["python"]["cli_prefix"], "python_version": manifest["python"]["version"],
            "bare_python": manifest["python"]["bare_python"],
            "shell": "bash -c without a login profile", "path": entries[:PROMPT_PATH_ENTRIES],
            "path_entries_omitted": max(0, len(entries) - PROMPT_PATH_ENTRIES),
            "required_missing": manifest["required_missing"], "tools": tools, "operations": ops, "data": data,
            "observed_missing": [{key: row.get(key) for key in ("name", "last_seen", "job_id", "count", "fallback")}
                                 for row in manifest["observed_missing"] if not row["now_available"]],
            "full_manifest": manifest["python"]["cli_prefix"] + " bits-capabilities --stored"}


def heartbeat_view(manifest: dict | None) -> dict | None:
    if not manifest:
        return None
    return {"generated_at": manifest.get("generated_at"), "required_missing": manifest.get("required_missing", []),
            "unavailable_tools": sorted(name for name, tool in manifest.get("tools", {}).items() if not tool["available"]),
            "observed_missing": sorted(row["name"] for row in manifest.get("observed_missing", [])
                                       if not row["now_available"])}
