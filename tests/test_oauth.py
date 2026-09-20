import json
import urllib.error
import urllib.request

import pytest

from xauusd.oauth import (
    CTraderOAuthError,
    authorize_url,
    exchange_authorization_code,
    persist_tokens_env,
    refresh_access_token,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def response_json(payload):
    return FakeResponse(payload)


def test_authorize_url_builds_documented_endpoint():
    url = authorize_url("app-1", "http://localhost:8080/callback", scope="accounts")
    assert url.startswith("https://id.ctrader.com/my/settings/openapi/grantingaccess/?")
    assert "client_id=app-1" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback" in url
    assert "scope=accounts" in url
    assert "product=web" in url


def test_refresh_access_token_returns_pair_with_browser_agent(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout=45):
        seen["url"] = request.full_url
        seen["ua"] = request.get_header("User-agent") or request.get_header("User-Agent")
        return response_json({"access_token": "a" * 43, "token_type": "bearer",
                              "expires_in": 2628000, "refresh_token": "r" * 43})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    result = refresh_access_token("cid", "secret", "refresh-tok")

    assert result["access_token"] == "a" * 43
    assert result["refresh_token"] == "r" * 43
    assert "grant_type=refresh_token" in seen["url"]
    assert "refresh_token=refresh-tok" in seen["url"]
    assert "client_id=cid" in seen["url"]
    assert "client_secret=secret" in seen["url"]
    assert "Mozilla" in seen["ua"]


def test_exchange_authorization_code_uses_code_and_redirect(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout=45):
        seen["url"] = request.full_url
        return response_json({"access_token": "x" * 43, "refresh_token": "y" * 43})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    exchange_authorization_code("cid", "secret", "code-1", "http://localhost:8080/callback")

    assert "grant_type=authorization_code" in seen["url"]
    assert "code=code-1" in seen["url"]
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback" in seen["url"]


def test_rejected_grant_raises_oauth_error(monkeypatch):
    monkeypatch.setattr(
        urllib.request, "urlopen",
        lambda request, timeout=45: response_json({"errorCode": "ACCESS_DENIED", "description": "Access denied."}))
    with pytest.raises(CTraderOAuthError, match="ACCESS_DENIED"):
        refresh_access_token("c", "s", "r")


def test_http_failure_raises_oauth_error(monkeypatch):
    def boom(request, timeout=45):
        raise urllib.error.HTTPError(request.full_url, 500, "err", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    with pytest.raises(CTraderOAuthError, match="HTTP 500"):
        refresh_access_token("c", "s", "r")


def test_missing_access_token_raises(monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda request, timeout=45: response_json({"expires_in": 1}))
    with pytest.raises(CTraderOAuthError, match="no access token"):
        refresh_access_token("c", "s", "r")


def test_persist_tokens_rewrites_only_token_keys(tmp_path):
    env = tmp_path / "app.env"
    env.write_text("CTRADER_CLIENT_ID=abc\nCTRADER_ACCESS_TOKEN=old-at\nSOME_KEY=keep\n")

    persist_tokens_env("new-at", "new-rt", env)

    lines = env.read_text().splitlines()
    assert "CTRADER_CLIENT_ID=abc" in lines
    assert "CTRADER_ACCESS_TOKEN=new-at" in lines
    assert "CTRADER_REFRESH_TOKEN=new-rt" in lines
    assert "SOME_KEY=keep" in lines
    assert "old-at" not in env.read_text()


def test_persist_tokens_appends_missing_key_and_sets_0600(tmp_path):
    env = tmp_path / "app.env"
    env.write_text("A=1\n")

    persist_tokens_env("at-new", None, env)

    text = env.read_text()
    assert "CTRADER_ACCESS_TOKEN=at-new" in text
    assert "CTRADER_REFRESH_TOKEN" not in text
    assert "A=1" in text
    assert (env.stat().st_mode & 0o777) == 0o600