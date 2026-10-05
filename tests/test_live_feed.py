import json
import subprocess
import sys
from pathlib import Path

import pytest

from xauusd.ctrader_auth import DEMO_HOST as DEMO_HOST_SUFFIX
from xauusd.live_feed import LiveBarFeed, LiveFeedConfig, closed_bar, run_feed


def unavailable_type():
    from xauusd.live_feed import LiveFeedUnavailable
    return LiveFeedUnavailable


def config(tmp_path, **overrides):
    values = {"processed_dir": str(tmp_path / "processed"),
              "status_path": str(tmp_path / "status.json"),
              "state_path": str(tmp_path / "feed.json")}
    values.update(overrides)
    return LiveFeedConfig(**values)


def test_data_feed_run_exits_nonzero_and_refuses_a_non_demo_host(tmp_path):
    # Exiting 0 under Restart=always is an invisible infinite restart loop; the
    # exit code is the only signal systemd gets. A host that is not the pinned
    # demo host fails before any socket is opened, so this is fast and offline.
    result = subprocess.run(
        [sys.executable, "-m", "xauusd.cli", "data-feed", "run"],
        capture_output=True, text=True, timeout=120, cwd=str(Path(__file__).resolve().parents[1]),
        env={"PATH": "/usr/bin:/bin", "CTRADER_DEMO_ONLY": "true",
             "CTRADER_OPEN_API_HOST": "live.ctraderapi.com",
             "DATA_FEED_STATUS_PATH": str(tmp_path / "status.json"),
             "DATA_FEED_STATE_PATH": str(tmp_path / "feed.json"),
             "XAUUSD_STATE_BACKEND": "local"})
    assert result.returncode != 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["error_code"] == "live_feed_host_not_pinned"
    assert DEMO_HOST_SUFFIX in payload["detail"]
    # A refused configuration still has to leave a status for /api/health.
    assert json.loads((tmp_path / "status.json").read_text())["state"] == "unavailable"


def test_data_feed_status_is_none_before_the_feed_has_ever_run(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "xauusd.cli", "data-feed", "status"],
        capture_output=True, text=True, timeout=120, cwd=str(Path(__file__).resolve().parents[1]),
        env={"PATH": "/usr/bin:/bin", "DATA_FEED_STATUS_PATH": str(tmp_path / "absent.json")})
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "none"


def test_a_closed_bar_is_the_only_bar_that_may_be_persisted():
    from datetime import datetime, timedelta, timezone
    now = datetime(2026, 10, 5, 14, 30, tzinfo=timezone.utc)
    assert closed_bar(now - timedelta(minutes=1), now) is True
    # The forming bar is not closed, so persisting it would let a later, longer
    # bar overwrite a complete one.
    assert closed_bar(now, now) is False


# -- execution boundary -------------------------------------------------------
# The feed is a broker connection. These guards are the only thing stopping it
# becoming a live-market client, and they had no coverage at all.

def test_feed_refuses_any_host_but_the_pinned_demo_host(tmp_path, monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    LiveFeedConfig(host="demo.ctraderapi.com", status_path=str(tmp_path / "s.json")).validate()
    for host in ("live.ctraderapi.com", "", "demo.ctraderapi.com.evil.test"):
        with pytest.raises(ValueError, match="restricted to demo.ctraderapi.com"):
            LiveFeedConfig(host=host, status_path=str(tmp_path / "s.json")).validate()


def test_feed_refuses_to_start_without_the_demo_only_flag(tmp_path, monkeypatch):
    monkeypatch.delenv("CTRADER_DEMO_ONLY", raising=False)
    with pytest.raises(ValueError, match="CTRADER_DEMO_ONLY"):
        LiveBarFeed(config(tmp_path), store=object())
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "false")
    with pytest.raises(ValueError, match="CTRADER_DEMO_ONLY"):
        LiveBarFeed(config(tmp_path), store=object())


def test_feed_config_rejects_a_nonsense_port_or_empty_symbol(tmp_path):
    with pytest.raises(ValueError, match="positive integer"):
        LiveFeedConfig(port=0).validate()
    with pytest.raises(ValueError, match="symbol is required"):
        LiveFeedConfig(symbol="  ").validate()


# -- subscription path, with no broker ----------------------------------------

class FakeDeferred:
    def __init__(self, result):
        self._result = result

    def addCallbacks(self, ok, err=None):
        ok(self._result)
        return self


def envelope(response):
    """Wrap a real response proto the way the SDK hands it to a callback."""
    from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import ProtoMessage
    message = ProtoMessage()
    message.payloadType = response.payloadType
    message.payload = response.SerializeToString()
    return message


def account_list(accounts):
    from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOAGetAccountListByAccessTokenRes
    response = ProtoOAGetAccountListByAccessTokenRes(accessToken="token")
    for spec in accounts:
        item = response.ctidTraderAccount.add()
        item.ctidTraderAccountId = spec["id"]
        if "live" in spec:
            item.isLive = spec["live"]
    return response


def symbol_list(symbols):
    from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOASymbolsListRes
    response = ProtoOASymbolsListRes(ctidTraderAccountId=42)
    for spec in symbols:
        item = response.symbol.add()
        item.symbolId = spec["id"]
        item.symbolName = spec["name"]
        item.enabled = spec.get("enabled", True)
    return response


DEMO_ACCOUNT = [{"id": 42, "live": False}]
XAU_SYMBOL = [{"id": 7, "name": "XAUUSD"}]


class FakeClient:
    """A cTrader client double: answers each request synchronously."""

    def __init__(self, accounts=None, symbols=None, error_code=None):
        self.sent = []
        self._accounts = DEMO_ACCOUNT if accounts is None else accounts
        self._symbols = XAU_SYMBOL if symbols is None else symbols
        self._error_code = error_code

    def _error(self, name):
        from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import ProtoErrorRes
        response = ProtoErrorRes()
        response.errorCode = self._error_code
        return envelope(response)

    def send(self, request, responseTimeoutInSeconds=0):
        from ctrader_open_api.messages.OpenApiMessages_pb2 import (
            ProtoOAAccountAuthRes, ProtoOASubscribeLiveTrendbarRes)
        name = type(request).__name__
        self.sent.append(name)
        if self._error_code is not None and name != "ProtoOAGetAccountListByAccessTokenReq":
            return FakeDeferred(self._error(name))
        if name == "ProtoOAApplicationAuthReq":
            from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOAApplicationAuthRes
            return FakeDeferred(envelope(ProtoOAApplicationAuthRes()))
        if name == "ProtoOAGetAccountListByAccessTokenReq":
            return FakeDeferred(envelope(account_list(self._accounts)))
        if name == "ProtoOAAccountAuthReq":
            return FakeDeferred(envelope(ProtoOAAccountAuthRes(ctidTraderAccountId=42)))
        if name == "ProtoOASymbolsListReq":
            return FakeDeferred(envelope(symbol_list(self._symbols)))
        if name in ("ProtoOASubscribeSpotsReq", "ProtoOASubscribeLiveTrendbarReq"):
            return FakeDeferred(envelope(ProtoOASubscribeLiveTrendbarRes(ctidTraderAccountId=42)))
        raise AssertionError(f"unexpected request {name}")


def credentials(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    monkeypatch.setenv("CTRADER_CLIENT_ID", "id")
    monkeypatch.setenv("CTRADER_CLIENT_SECRET", "secret")
    monkeypatch.setenv("CTRADER_ACCESS_TOKEN", "token")
    monkeypatch.delenv("CTRADER_CTID_TRADER_ACCOUNT_ID", raising=False)


def test_subscribe_discovers_the_demo_account_then_subscribes_to_m1(tmp_path, monkeypatch):
    credentials(monkeypatch)
    client = FakeClient()
    feed = LiveBarFeed(config(tmp_path), store=object(), client_factory=lambda h, p: client,
                       reactor_runner=lambda call: None)
    feed._subscribe()
    # Application auth must come first: the broker rejects a token request sent
    # before it with UNSUPPORTED_MESSAGE.
    # Spot subscription precedes the trendbar one: the broker answers a
    # trendbar request sent first with INVALID_REQUEST.
    assert client.sent == ["ProtoOAApplicationAuthReq", "ProtoOAGetAccountListByAccessTokenReq",
                           "ProtoOAAccountAuthReq", "ProtoOASymbolsListReq",
                           "ProtoOASubscribeSpotsReq", "ProtoOASubscribeLiveTrendbarReq"]
    assert feed._discovered["account_id"] == 42
    assert feed._discovered["symbol_id"] == 7
    # subscribed_at is only set on the confirmed subscription, never on send.
    assert feed.subscribed_at is not None


def test_subscribe_sends_m1_and_never_a_live_account(tmp_path, monkeypatch):
    from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOASubscribeLiveTrendbarReq
    credentials(monkeypatch)
    live = FakeClient(accounts=[{"id": 99, "live": True}])
    feed = LiveBarFeed(config(tmp_path), store=object(), client_factory=lambda h, p: live,
                       reactor_runner=lambda call: None)
    with pytest.raises(unavailable_type()) as caught:
        feed._subscribe()
    # An account the broker reports as live is never subscribed to.
    assert caught.value.error_code == "live_feed_no_demo_account"
    assert "ProtoOASubscribeLiveTrendbarReq" not in live.sent
    assert "ProtoOASubscribeSpotsReq" not in live.sent

    demo = FakeClient()
    feed2 = LiveBarFeed(config(tmp_path), store=object(), client_factory=lambda h, p: demo,
                        reactor_runner=lambda call: None)
    feed2._subscribe()
    assert demo.sent[-1] == "ProtoOASubscribeLiveTrendbarReq"
    assert feed2._discovered["account_id"] == 42


def test_an_unclassified_account_is_not_treated_as_demo(tmp_path, monkeypatch):
    # isLive is proto3 explicit presence: a broker that never classified the
    # account has said nothing, and silence is not consent to trade a demo feed.
    credentials(monkeypatch)
    client = FakeClient(accounts=[{"id": 7}])
    feed = LiveBarFeed(config(tmp_path), store=object(), client_factory=lambda h, p: client,
                       reactor_runner=lambda call: None)
    with pytest.raises(unavailable_type()) as caught:
        feed._subscribe()
    assert caught.value.error_code == "live_feed_no_demo_account"


def test_a_missing_symbol_fails_before_any_subscription(tmp_path, monkeypatch):
    credentials(monkeypatch)
    client = FakeClient(symbols=[{"id": 1, "name": "EURUSD"}])
    feed = LiveBarFeed(config(tmp_path), store=object(), client_factory=lambda h, p: client,
                       reactor_runner=lambda call: None)
    with pytest.raises(unavailable_type()) as caught:
        feed._subscribe()
    assert caught.value.error_code == "live_feed_symbol_not_found"
    assert "ProtoOASubscribeLiveTrendbarReq" not in client.sent
    assert "ProtoOASubscribeSpotsReq" not in client.sent
    assert json.loads(Path(feed.config.status_path).read_text())["error_code"] == "live_feed_symbol_not_found"


def test_a_configured_account_skips_the_account_list_request(tmp_path, monkeypatch):
    credentials(monkeypatch)
    monkeypatch.setenv("CTRADER_CTID_TRADER_ACCOUNT_ID", "4242")
    client = FakeClient()
    feed = LiveBarFeed(config(tmp_path), store=object(), client_factory=lambda h, p: client,
                       reactor_runner=lambda call: None)
    feed._subscribe()
    assert "ProtoOAGetAccountListByAccessTokenReq" not in client.sent
    assert feed._discovered["account_id"] == 4242


# -- persistence and parsing ---------------------------------------------------

def test_a_forming_bar_is_never_persisted(tmp_path, monkeypatch):
    import pandas as pd
    from datetime import datetime, timezone
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None)
    now = datetime.now(timezone.utc)
    feed.persist_bar({"timestamp": pd.Timestamp(now), "open": 1, "high": 2, "low": 1,
                      "close": 1.5, "volume": 3})
    assert store.written == []


def test_a_closed_bar_is_persisted_and_an_out_of_order_replay_is_not(tmp_path, monkeypatch):
    import pandas as pd
    from datetime import datetime, timedelta, timezone
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None)
    now = datetime.now(timezone.utc)
    older = pd.Timestamp(now - timedelta(minutes=2))
    newer = pd.Timestamp(now - timedelta(minutes=1))
    feed.persist_bar({"timestamp": older, "open": 1, "high": 2, "low": 1, "close": 1.5, "volume": 3})
    feed.persist_bar({"timestamp": newer, "open": 2, "high": 3, "low": 2, "close": 2.5, "volume": 4})
    feed.persist_bar({"timestamp": older, "open": 1, "high": 2, "low": 1, "close": 1.5, "volume": 3})
    assert [list(frame.index)[0] for frame in store.written] == [older, newer]
    assert feed.bars_written == 2


def test_a_replayed_old_bar_is_refused_by_the_age_guard(tmp_path, monkeypatch):
    import pandas as pd
    from datetime import datetime, timedelta, timezone
    from xauusd.live_feed import MAX_BAR_AGE_SECONDS
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None)
    late = pd.Timestamp(datetime.now(timezone.utc) - timedelta(seconds=MAX_BAR_AGE_SECONDS + 60))
    feed.persist_bar({"timestamp": late, "open": 1, "high": 2, "low": 1, "close": 1.5, "volume": 3})
    assert store.written == []
    assert json.loads(Path(feed.config.status_path).read_text())["error_code"] == "stale_bar_ignored"


def test_session_phase_reports_the_new_york_break_and_the_weekend():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from xauusd.live_feed import _heartbeat_phase
    ny = ZoneInfo("America/New_York")
    assert _heartbeat_phase(datetime(2026, 10, 7, 12, 0, tzinfo=ny)) == "open"
    assert _heartbeat_phase(datetime(2026, 10, 7, 17, 30, tzinfo=ny)) == "daily_break"
    assert _heartbeat_phase(datetime(2026, 10, 3, 12, 0, tzinfo=ny)) == "weekend_closed"
    assert _heartbeat_phase(datetime(2026, 10, 4, 17, 0, tzinfo=ny)) == "weekend_closed"


def test_an_inconsistent_decoded_bar_is_refused(tmp_path, monkeypatch):
    from xauusd.live_feed import _bar_is_usable
    good = {"open": 1.0, "high": 2.0, "low": 1.0, "close": 1.5, "volume": 7}
    assert _bar_is_usable(good) is True
    # open above high would fail normalize() inside the store and take the whole
    # batch write down with it, so the bar has to be refused here.
    assert _bar_is_usable({**good, "open": 9.0}) is False
    assert _bar_is_usable({**good, "close": 9.0}) is False
    assert _bar_is_usable({**good, "low": 0.0}) is False
    assert _bar_is_usable({**good, "high": float("nan")}) is False
    assert _bar_is_usable({**good, "volume": -1}) is False
    assert _bar_is_usable({**good, "volume": True}) is False


def test_a_live_spot_event_is_decoded_to_an_absolute_row(tmp_path, monkeypatch):
    # The live stream carries low-plus-delta trendbars, not absolute OHLC. This
    # pins the real wire shape so a decoder swap cannot silently write
    # nonsense prices into the store.
    from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOASpotEvent
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    feed = LiveBarFeed(config(tmp_path), store=object(), reactor_runner=lambda call: None)
    event = ProtoOASpotEvent(symbolId=7)
    bar = event.trendbar.add()
    bar.utcTimestampInMinutes = 29327040           # 2025-10-05 00:00 UTC, in MINUTES
    bar.low = 400_000                               # 4.00000
    bar.deltaOpen = 0
    bar.deltaHigh = 10_000                          # high 4.10000
    bar.deltaClose = 5_000                          # close 4.05000
    bar.volume = 42
    rows = feed._bars_from(event)
    assert len(rows) == 1
    row = rows[0]
    assert row["open"] == 4.0 and row["low"] == 4.0
    assert row["high"] == 4.1 and row["close"] == 4.05
    assert row["volume"] == 42
    assert str(row["timestamp"]) == "2025-10-05 00:00:00+00:00"
    assert feed._bars_from(ProtoOASpotEvent(symbolId=7)) == []


class FakeStore:
    def __init__(self):
        self.written = []

    def write(self, frame, merge=False):
        self.written.append(frame)


# -- the forming-bar buffer ----------------------------------------------------

def test_a_forming_bar_is_held_until_a_newer_bar_proves_it_closed(tmp_path, monkeypatch):
    # The stream carries the forming minute, updated repeatedly, and the last
    # frame for a minute arrives before that minute closes. Testing each arrival
    # against the clock discards every bar, because none is seen again once
    # closed. This is the bug that produced bars_written: 0 against a live broker.
    import pandas as pd
    from datetime import datetime, timezone
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    # The production transition across a minute boundary, on an injected clock.
    minute = pd.Timestamp("2026-10-05 05:23:00+00:00")
    clock = [minute + pd.Timedelta(seconds=30)]
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None,
                       now_provider=lambda: clock[0].to_pydatetime())
    forming = {"timestamp": minute, "open": 1.0, "high": 2.0, "low": 1.0, "close": 1.5,
               "volume": 3}
    feed.on_bar(forming)
    assert store.written == [], "a forming bar must never be written"
    clock[0] = minute + pd.Timedelta(minutes=1)
    feed.on_bar({"timestamp": minute + pd.Timedelta(minutes=1), "open": 2.0, "high": 3.0,
                 "low": 2.0, "close": 2.5, "volume": 4})
    assert [list(f.index)[0] for f in store.written] == [minute]
    assert store.written[0]["close"].iloc[0] == 1.5


def test_repeated_updates_to_one_minute_replace_rather_than_accumulate(tmp_path, monkeypatch):
    import pandas as pd
    from datetime import datetime, timezone
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None)
    minute = pd.Timestamp("2026-10-05 05:23:00+00:00")
    clock = [minute + pd.Timedelta(seconds=30)]
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None,
                       now_provider=lambda: clock[0].to_pydatetime())
    for close in (1.1, 1.2, 1.3):
        feed.on_bar({"timestamp": minute, "open": 1.0, "high": 2.0, "low": 1.0,
                     "close": close, "volume": 3})
    assert store.written == []
    clock[0] = minute + pd.Timedelta(minutes=1)
    feed.on_bar({"timestamp": minute + pd.Timedelta(minutes=1), "open": 2.0, "high": 3.0,
                 "low": 2.0, "close": 2.5, "volume": 4})
    # One row, carrying the last value seen for that minute.
    assert len(store.written) == 1
    assert store.written[0]["close"].iloc[0] == 1.3


def test_an_out_of_order_bar_never_rewinds_the_buffer(tmp_path, monkeypatch):
    import pandas as pd
    from datetime import datetime, timezone
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    minute = pd.Timestamp("2026-10-05 05:23:00+00:00")
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None,
                       now_provider=lambda: (minute + pd.Timedelta(seconds=30)).to_pydatetime())
    now = minute
    feed.on_bar({"timestamp": now, "open": 1.0, "high": 2.0, "low": 1.0, "close": 1.5, "volume": 3})
    feed.on_bar({"timestamp": now - pd.Timedelta(minutes=5), "open": 9.0, "high": 9.5,
                 "low": 8.5, "close": 9.2, "volume": 1})
    assert store.written == [], "a replay must not displace the bar being held"
    assert feed._pending["timestamp"] == now


def test_a_closed_bar_arriving_out_of_order_is_refused_by_the_store(tmp_path, monkeypatch):
    import pandas as pd
    from datetime import datetime, timedelta, timezone
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None)
    now = datetime.now(timezone.utc)
    older = {"timestamp": pd.Timestamp(now - timedelta(minutes=2)), "open": 1.0, "high": 2.0,
             "low": 1.0, "close": 1.5, "volume": 3}
    feed.persist_bar(older)
    feed.persist_bar({"timestamp": older["timestamp"] - pd.Timedelta(minutes=1), "open": 1.0,
                      "high": 2.0, "low": 1.0, "close": 1.4, "volume": 3})
    assert len(store.written) == 1


def test_stopping_flushes_a_held_bar_that_has_since_closed(tmp_path, monkeypatch):
    import pandas as pd
    from datetime import datetime, timedelta, timezone
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None)
    moment = pd.Timestamp(datetime.now(timezone.utc) - timedelta(minutes=1)).floor("min")
    feed.on_bar({"timestamp": moment, "open": 1.0, "high": 2.0, "low": 1.0, "close": 1.5,
                 "volume": 3})
    feed.stop()
    assert [list(f.index)[0] for f in store.written] == [moment]


def test_the_default_handler_is_the_buffering_path_not_the_raw_write(tmp_path, monkeypatch):
    # Wiring matters: if handle_bar defaults to persist_bar the forming bar is
    # tested against the clock on arrival and every bar is dropped, which is
    # exactly the bars_written: 0 seen against a live broker.
    import pandas as pd
    from datetime import datetime, timezone
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = FakeStore()
    minute = pd.Timestamp("2026-10-05 05:23:00+00:00")
    clock = [minute + pd.Timedelta(seconds=30)]
    feed = LiveBarFeed(config(tmp_path), store=store, reactor_runner=lambda call: None,
                       now_provider=lambda: clock[0].to_pydatetime())
    assert feed.handle_bar == feed.on_bar
    feed.handle_bar({"timestamp": minute, "open": 1.0, "high": 2.0, "low": 1.0,
                     "close": 1.5, "volume": 3})
    assert store.written == []


def test_the_default_store_is_built_with_a_path_not_a_string(tmp_path, monkeypatch):
    # A str processed_dir made HistoricalDataStore.path do `str / str` and every
    # write raise AttributeError, which the message handler reported as a
    # rejected bar: a store failure disguised as stream noise.
    from pathlib import Path
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    feed = LiveBarFeed(config(tmp_path), reactor_runner=lambda call: None)
    assert isinstance(feed.store.config.processed_dir, Path)
    import pandas as pd
    frame = pd.DataFrame([{"open": 1.0, "high": 2.0, "low": 1.0, "close": 1.5, "volume": 2}],
                         index=pd.DatetimeIndex([pd.Timestamp("2026-10-05 05:23:00+00:00")],
                                                name="timestamp"))
    feed.store.write(frame, merge=True)
    reread = feed.store.normalize(feed.store.read())
    assert len(reread) == 1 and reread["close"].iloc[0] == 1.5
