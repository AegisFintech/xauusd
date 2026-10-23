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

A read-modify-write needs one more thing: :func:`file_lock` makes the whole
read-merge-swap exclusive, because two writers that both read the previous
content lose one of their updates even when every individual swap is atomic.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

SECURE_MODE = 0o600
LOCK_TIMEOUT_SECONDS = 30.0


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


@contextlib.contextmanager
def file_lock(target: str | Path, timeout: float = LOCK_TIMEOUT_SECONDS,
              poll_seconds: float = 0.05):
    """Exclusive cross-process lock around a read-modify-write of ``target``.

    ``atomic_write_bytes`` makes the swap safe; it cannot make a
    read-modify-write safe. Two processes that both read the previous content
    still lose one of their updates, so the read, the merge and the swap have to
    be one exclusive section. The lock file sits beside the target and is never
    the target, so no reader can mistake it for data.

    Raises ``TimeoutError`` rather than waiting forever: a writer that cannot get
    the lock has to fail loudly, not silently skip a merge.
    """
    destination = Path(target)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock_path = destination.with_name(destination.name + ".lock")
    handle = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out after {timeout}s waiting for the "
                                       f"{destination.name} write lock") from exc
                time.sleep(poll_seconds)
        try:
            yield lock_path
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
    finally:
        os.close(handle)
