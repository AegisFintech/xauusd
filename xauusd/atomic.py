"""Atomic durable-file writes.

One implementation, used by every writer in the repository. A torn status file,
a half-written ``.env`` or a truncated report are all the same failure: a reader
sees a partial file and silently degrades instead of failing loudly. The
previous copies of this helper were not equivalent, and the weakest one
(``write_text``, which truncates before it writes) was used on the credential
file.

Guarantees:

* the target is only ever observed complete, because it is swapped by ``os.replace``;
* the payload is on disk before the rename, because the file is fsynced;
* the directory entry is on disk too, so a crash cannot lose the rename;
* the temporary file is unique per writer, so two writers cannot interleave into
  one inode;
* ``0o600`` is applied to the temporary file *before* any content is written, so
  a credential file is never briefly world-readable.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

SECURE_MODE = 0o600


def atomic_write_bytes(target: str | Path, payload: bytes, mode: int | None = None) -> Path:
    """Replace ``target`` with ``payload`` atomically and durably."""
    destination = Path(target)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(dir=destination.parent,
                                              prefix=destination.name + ".",
                                              suffix=".tmp")
    temporary = Path(temporary_name)
    try:
        if mode is not None:
            # Before the content, not after: mkstemp creates 0600 already, but an
            # explicit chmod keeps the guarantee if the file is copied or replaced.
            os.fchmod(handle, mode)
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    _fsync_directory(destination.parent)
    return destination


def atomic_write_text(target: str | Path, text: str, mode: int | None = None) -> Path:
    return atomic_write_bytes(target, text.encode("utf-8"), mode)


def atomic_write_json(target: str | Path, payload: Any, mode: int | None = None,
                      indent: int | None = None, sort_keys: bool = True) -> Path:
    """Serialise ``payload`` as JSON and replace ``target`` atomically.

    ``allow_nan`` stays off by default: every reader in this repository consumes
    the result with a strict JSON parser, so a NaN or infinity is a defect to be
    surfaced at the write, not a value to smuggle into a report.
    """
    text = json.dumps(payload, indent=indent, sort_keys=sort_keys, allow_nan=False)
    return atomic_write_text(target, text + "\n", mode)


def _fsync_directory(directory: Path) -> None:
    """Persist a rename. Best effort: not every filesystem allows opening a dir."""
    try:
        fd = os.open(directory, os.O_DIRECTORY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)
