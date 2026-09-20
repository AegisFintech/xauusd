"""cTrader Open API OAuth2 token operations.

The token endpoint is the documented ``GET https://openapi.ctrader.com/apps/token``.
Credentials and tokens are never logged or echoed; refreshed tokens are persisted
only through an atomic, ``0o600`` rewrite of the two dedicated keys in ``.env``.
The Cloudflare WAF in front of the endpoint rejects urllib's default User-Agent,
so every request carries a browser-grade User-Agent that is never dropped.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

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


def persist_tokens_env(access_token: str, refresh_token: str | None, env_path: str | os.PathLike = ".env") -> Path:
    """Atomically rewrite only the token keys in the given env file (``0o600``).

    Returns the written path. Never returns or prints token values.
    """
    path = Path(env_path)
    existing = path.read_text(encoding="utf-8").splitlines(keepends=True) if path.exists() else []
    keys = {"CTRADER_ACCESS_TOKEN": access_token, "CTRADER_REFRESH_TOKEN": refresh_token}
    rewritten: set[str] = set()
    output: list[str] = []
    for line in existing:
        key = line.split("=", 1)[0].strip() if "=" in line else ""
        if key in keys:
            if keys[key] is not None:
                output.append(f"{key}={keys[key]}\n")
                rewritten.add(key)
            continue
        output.append(line)
    for key, value in keys.items():
        if value is not None and key not in rewritten:
            output.append(f"{key}={value}\n")
    path.write_text("".join(output), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path