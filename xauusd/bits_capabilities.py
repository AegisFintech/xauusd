"""Safe description of the environment that runs Bits shell jobs.

Guidance must name the interpreter that is actually running this code rather
than a bare ``python`` or a standalone ``bits-memory`` executable: service shells
do not source a login profile, so neither is guaranteed to exist on ``PATH``.
"""
from __future__ import annotations

import shlex
import sys


def python_executable() -> str:
    """Absolute path of the running interpreter (the service virtualenv)."""
    return sys.executable or "python3"


def cli_prefix() -> str:
    """Complete, shell-quoted command prefix for this repository's CLI."""
    return shlex.quote(python_executable()) + " -m xauusd.cli"
