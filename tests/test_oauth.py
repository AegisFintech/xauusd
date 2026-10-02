import json
from threading import Event, Thread
import time
import urllib.error
import urllib.request

import pytest

from xauusd.oauth import (
    CTraderOAuthError,
    _env_lock,
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


def test_persist_tokens_keeps_the_stored_refresh_token_when_none_is_returned(tmp_path):
    """cTrader does not always return a new refresh token.

    Dropping the stored one turns a routine refresh into a permanent
    ``auth_error`` for every later process, because nothing can refresh it back.
    The old behaviour asserted the opposite; that assertion was the bug.
    """
    env = tmp_path / "app.env"
    env.write_text("CTRADER_ACCESS_TOKEN=old-at\nCTRADER_REFRESH_TOKEN=keep-me\n")

    persist_tokens_env("new-at", None, env)

    lines = env.read_text().splitlines()
    assert "CTRADER_ACCESS_TOKEN=new-at" in lines
    assert "CTRADER_REFRESH_TOKEN=keep-me" in lines


def test_persist_tokens_never_truncates_the_file(tmp_path):
    """A crash mid-write must not destroy the other credentials.

    ``write_text`` truncates before writing, so a failure between truncation and
    completion leaves an empty ``.env`` and with it CTRADER_CLIENT_SECRET, the
    Datadog keys and every other setting. The swap is now atomic.
    """
    env = tmp_path / "app.env"
    env.write_text("CTRADER_CLIENT_SECRET=shh\nCTRADER_ACCESS_TOKEN=old\nCTRADER_REFRESH_TOKEN=rt\n")

    persist_tokens_env("fresh-at", "fresh-rt", env)

    text = env.read_text()
    assert "CTRADER_CLIENT_SECRET=shh" in text
    assert "CTRADER_ACCESS_TOKEN=fresh-at" in text
    assert "CTRADER_REFRESH_TOKEN=fresh-rt" in text
    # No temporary residue left behind by the swap.
    assert [p.name for p in tmp_path.iterdir() if p.name.endswith(".tmp")] == []


def test_persist_tokens_rewrites_an_exported_assignment(tmp_path):
    """An ``export KEY=`` line must not survive alongside the rewritten key.

    Otherwise the file carries the old token twice and which one wins depends on
    the loader, which is worse than either outcome.
    """
    env = tmp_path / "app.env"
    env.write_text("export CTRADER_ACCESS_TOKEN=old-at\nOTHER=1\n")

    persist_tokens_env("new-at", "new-rt", env)

    text = env.read_text()
    assert "old-at" not in text
    assert text.count("CTRADER_ACCESS_TOKEN") == 1
    assert "CTRADER_ACCESS_TOKEN=new-at" in text
    assert "OTHER=1" in text


def test_persist_tokens_keeps_the_last_duplicate_assignment(tmp_path):
    """The last assignment is the one that loaded, so it is the one rewritten."""
    env = tmp_path / "app.env"
    env.write_text("CTRADER_ACCESS_TOKEN=first\nCTRADER_ACCESS_TOKEN=last\n")

    persist_tokens_env("new-at", None, env)

    text = env.read_text()
    assert "first" not in text
    assert text.count("CTRADER_ACCESS_TOKEN") == 1
    assert "CTRADER_ACCESS_TOKEN=new-at" in text


def test_persist_tokens_takes_an_exclusive_lock_for_the_read_modify_write(tmp_path):
    """The rewrite must hold a lock for the whole read-modify-write.

    Two independent producers refresh the same ``.env``: the data-update timer
    and the agent's in-tick refresh. cTrader rotates refresh tokens, so if both
    read, both refresh, and both write, the survivor may already be invalidated.
    Asserting the lock is held is deterministic; a test that merely runs many
    writers proves nothing, because without a lock they still tend to pass.
    """
    env = tmp_path / "app.env"
    env.write_text("CTRADER_ACCESS_TOKEN=0\n")
    progress = Event()

    def writer():
        progress.set()
        persist_tokens_env("new-at", "new-rt", env)

    with _env_lock(env):
        thread = Thread(target=writer, daemon=True)
        thread.start()
        assert progress.wait(timeout=5), "writer never started"
        # The writer must be blocked on the lock, not halfway through the file.
        time.sleep(0.3)
        assert thread.is_alive(), "writer completed while the lock was held"
        assert env.read_text() == "CTRADER_ACCESS_TOKEN=0\n"

    thread.join(timeout=30)
    assert not thread.is_alive()
    assert "CTRADER_ACCESS_TOKEN=new-at" in env.read_text()


def test_persist_tokens_leaves_a_valid_file_after_many_writers(tmp_path):
    """Smoke test: concurrent writers never produce an unparseable env file."""
    env = tmp_path / "app.env"
    env.write_text("CTRADER_CLIENT_SECRET=shh\nCTRADER_ACCESS_TOKEN=0\n")

    def writer(index):
        persist_tokens_env(f"at-{index}", f"rt-{index}", env)

    threads = [Thread(target=writer, args=(index,)) for index in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive()

    lines = env.read_text().splitlines()
    assert "CTRADER_CLIENT_SECRET=shh" in lines
    assert len([line for line in lines if line.startswith("CTRADER_ACCESS_TOKEN=")]) == 1
    assert len([line for line in lines if line.startswith("CTRADER_REFRESH_TOKEN=")]) == 1