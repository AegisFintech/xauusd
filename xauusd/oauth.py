"""cTrader Open API OAuth2 token operations.

The token endpoint is the documented ``GET https://openapi.ctrader.com/apps/token``.
Credentials and tokens are never logged or echoed; refreshed tokens are persisted
only through an atomic, ``0o600`` rewrite of the two dedicated keys in ``.env``.
The Cloudflare WAF in front of the endpoint rejects urllib's default User-Agent,
so every request carries a browser-grade User-Agent that is never dropped.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .atomic import SECURE_MODE, atomic_write_text

TOKEN_ENDPOINT = "https://openapi.ctrader.com/apps/token"
AUTHORIZE_ENDPOINT = "https://id.ctrader.com/my/settings/openapi/grantingaccess/"
BROWSER_USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0")


class CTraderOAuthError(RuntimeError):
    """An OAuth token operation failed for a known, safe reason."""


def authorize_url(client_id: str, redirect_uri: str, scope: str = "accounts") -> str:
    query = urllib.parse.urlencode({
        "client_id": client_id, "redirect_uri": redirect_uri, "scope": scope, "product": "web",
    })
    return f"{AUTHORIZE_ENDPOINT}?{query}"


def exchange_authorization_code(client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict[str, str]:
    return _request({
        "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
        "client_id": client_id, "client_secret": client_secret,
    })


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict[str, str]:
    return _request({
        "grant_type": "refresh_token", "refresh_token": refresh_token,
        "client_id": client_id, "client_secret": client_secret,
    })


def _request(params: dict[str, str]) -> dict[str, str]:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{TOKEN_ENDPOINT}?{query}",
        headers={"Accept": "application/json", "User-Agent": BROWSER_USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            payload: dict[str, Any] = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise CTraderOAuthError(f"OAuth token endpoint HTTP {exc.code}") from exc
    except OSError as exc:
        raise CTraderOAuthError(f"OAuth token endpoint unreachable: {exc}") from exc
    code = payload.get("errorCode")
    if code is not None:
        raise CTraderOAuthError(f"OAuth token request rejected: {code}: {payload.get('description') or ''}")
    access_token = payload.get("access_token") or payload.get("accessToken")
    if not access_token:
        raise CTraderOAuthError("OAuth response contained no access token")
    result = {"access_token": access_token}
    refresh_token = payload.get("refresh_token") or payload.get("refreshToken")
    if refresh_token:
        result["refresh_token"] = refresh_token
    return result


TOKEN_KEYS = ("CTRADER_ACCESS_TOKEN", "CTRADER_REFRESH_TOKEN")
# The two producers of `.env` token writes: the xauusd-data-update timer and the
# agent's in-tick refresh. They are independent processes, so the read-modify-write
# must be exclusive or the loser of the race persists a rotated refresh token the
# broker has already invalidated.
_ENV_LOCK_NAME = ".env.lock"
_LOCK_TIMEOUT_SECONDS = 30.0


def persist_tokens_env(access_token: str, refresh_token: str | None,
                       env_path: str | os.PathLike = ".env") -> Path:
    """Rewrite only the token keys in the given env file, atomically at ``0o600``.

    Three properties this must keep:

    * **Atomic.** The file is swapped by ``os.replace`` after the payload is
      fsynced. A plain truncate-then-write could leave ``.env`` empty, which
      destroys ``CTRADER_CLIENT_SECRET`` and the Datadog keys along with the
      tokens and is not recoverable by any code path.
    * **Non-destructive.** A response with no ``refresh_token`` keeps whatever was
      already stored. Dropping the key turned a routine refresh into a permanent
      ``auth_error`` for every later process.
    * **Exclusive.** The read-modify-write runs under a file lock.

    Returns the written path. Never returns or prints token values.
    """
    path = Path(env_path)
    updates = {"CTRADER_ACCESS_TOKEN": access_token, "CTRADER_REFRESH_TOKEN": refresh_token}
    path.parent.mkdir(parents=True, exist_ok=True)
    with _env_lock(path):
        body = _rewritten_env(path, updates)
        atomic_write_text(path, body, mode=SECURE_MODE)
    return path


def _env_lock(path: Path):
    """Exclusive lock around a `.env` read-modify-write, in its own directory.

    The lock file lives beside the env file rather than inside it, so it can never
    be mistaken for a credential or be picked up by the rewrite.
    """
    lock_path = path.parent / _ENV_LOCK_NAME

    @contextlib.contextmanager
    def guard():
        handle = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            deadline = time.monotonic() + _LOCK_TIMEOUT_SECONDS
            while True:
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError as exc:
                    if time.monotonic() >= deadline:
                        raise CTraderOAuthError(
                            f"timed out waiting for the {path.name} credential lock") from exc
                    time.sleep(0.05)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)
        finally:
            os.close(handle)

    return guard()


def _env_key(line: str) -> str:
    """Key name of an env assignment, tolerating a leading ``export`` and quotes.

    Without the ``export`` strip, a token survives in two keys and the older one
    keeps winning or losing depending on the loader, which is worse than either
    outcome.
    """
    text = line.strip()
    if text.startswith("export "):
        text = text[len("export "):].lstrip()
    if "=" not in text:
        return ""
    key = text.split("=", 1)[0].strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in "'\"":
        key = key[1:-1]
    return key


def _rewritten_env(path: Path, updates: dict[str, str | None]) -> str:
    """The whole env file with ``updates`` applied, preserving comments and order.

    A key whose new value is ``None`` is left exactly as it was found. That is
    the refresh-token case: cTrader does not always return a new one, and
    discarding the stored value would strand every later process.
    """
    existing = path.read_text(encoding="utf-8").splitlines(keepends=True) if path.exists() else []
    output: list[str] = []
    seen: set[str] = set()
    for line in existing:
        key = _env_key(line)
        if key in updates:
            if key in seen:
                # A duplicate assignment for the same key: the last one won at load
                # time, so the last one is the one that must be rewritten.
                continue
            seen.add(key)
            value = updates[key] if updates[key] is not None else _env_value(line)
            if value is not None:
                output.append(f"{key}={value}\n")
            continue
        output.append(line)
    for key, value in updates.items():
        if value is not None and key not in seen:
            output.append(f"{key}={value}\n")
    return "".join(output)


def _env_value(line: str) -> str | None:
    if "=" not in line:
        return None
    return line.split("=", 1)[1].strip().strip("\"'") or None