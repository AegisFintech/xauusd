"""Live M1 bar feed: a standalone subscription that keeps the persisted store fresh.

Why this is a separate process
------------------------------
The freshness gate is three minutes and the scheduled downloader runs four times
a day, so a 180-second gate and a 6-hourly batch are mutually unsatisfiable: the
newest bar is hours old and every proposal is refused as `STALE_MARKET_DATA`.
In-loop refresh helped only because the agent happened to be running; it cannot
support a deterministic engine that must act on every bar.

The cTrader SDK already speaks live subscriptions
(``ProtoOASubscribeLiveTrendbarReq``, ``ProtoOASubscribeSpotsReq``) and this
module uses them. It has to be its own process for two reasons:

* the SDK drives Twisted's **process-global, non-restartable** reactor. Restarting
  it in-process is impossible, which is the same constraint that forces the
  token-refresh retry to re-execute in a fresh interpreter;
* a network client must never share a fate with the trading loop. If the feed
  stalls, the engine must refuse to trade rather than inherit a broken reactor.

The feed appends *closed* M1 bars to the same parquet the research layer already
reads, so nothing downstream changes: the engine, the agent, the validator and
the backtests all keep working against one store.

Every write still goes through :meth:`HistoricalDataStore.write`, which is atomic
(temp file plus ``os.replace``), so a reader never observes a partial file.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
import json
import logging
import math
import os
import signal
import sys
import threading
import time
from zoneinfo import ZoneInfo

import pandas as pd

from .ctrader_auth import DEMO_HOST, demo_accounts, resolve_symbol

log = logging.getLogger(__name__)

NEW_YORK = ZoneInfo("America/New_York")
# A live M1 bar is stamped at its open; it is only complete one interval later.
BAR_INTERVAL_SECONDS = 60
# Re-authenticate and resubscribe on this cadence so a silently dropped socket
# is recovered without operator involvement.
RESUBSCRIBE_SECONDS = 900
# How long to wait before restarting the service after an unexpected disconnect.
RECONNECT_SECONDS = 15
# Wall-clock bound for the supervised smoke test (`data-feed once`). Long enough
# for one closed M1 bar to arrive, since nothing is written before a bar closes.
SMOKE_TEST_SECONDS = 180
# How often the reactor checks whether a stop was requested.
STOP_POLL_SECONDS = 1.0
# Bars whose open is older than this are ignored: a reconnect can replay
# history, and a late bar must never overwrite a newer one.
MAX_BAR_AGE_SECONDS = 15 * 60
HEARTBEAT_PATH_DEFAULT = "reports/data_feed_status.json"


class LiveFeedUnavailable(RuntimeError):
    """The feed cannot run, with a stable code for status files and health.

    A bare ``NotImplementedError`` was caught by the CLI, reported as a failed
    status and still exited 0. The unit is ``Restart=always``, so an
    unimplemented feed restarted forever: no status file, no exit code, and
    ``StandardError=null`` so nothing in the journal either. A feed that cannot
    run has to say so and stay down.
    """

    def __init__(self, error_code: str, message: str):
        super().__init__(message)
        self.error_code = error_code
        # A short reason safe to print. Exception text is never echoed wholesale,
        # because an arbitrary message can carry a value this repository must not
        # surface; only the fixed messages written here are.
        self.detail = message


class LiveFeedConfigError(LiveFeedUnavailable, ValueError):
    """A refused configuration, carrying a stable code.

    Subclasses ``ValueError`` because a bad host or port is a value error, and
    an operator seeing only ``ValueError`` learns nothing about which check
    refused or why.
    """



@dataclass(frozen=True)
class LiveFeedConfig:
    host: str = DEMO_HOST
    port: int = 5035
    symbol: str = "XAUUSD"
    processed_dir: str = "data/processed"
    status_path: str = HEARTBEAT_PATH_DEFAULT
    state_path: str = "state/data_feed.json"
    demo_only_required: bool = True
    backfill_bars: int = 500

    def validate(self) -> None:
        # The feed is a broker connection, so it inherits the same execution
        # boundary as the adapter: the pinned demo host and the explicit flag.
        if self.host != DEMO_HOST:
            raise LiveFeedConfigError("live_feed_host_not_pinned",
                                      f"live feed is restricted to {DEMO_HOST}")
        if not isinstance(self.port, int) or isinstance(self.port, bool) or self.port <= 0:
            raise LiveFeedConfigError("live_feed_port_invalid", "live feed port must be a positive integer")
        if not self.symbol.strip():
            raise LiveFeedConfigError("live_feed_symbol_required", "live feed symbol is required")
        if not isinstance(self.backfill_bars, int) or self.backfill_bars < 1:
            raise LiveFeedConfigError("live_feed_backfill_invalid",
                                      "backfill_bars must be a positive integer")

    @classmethod
    def from_env(cls) -> "LiveFeedConfig":
        from .data import DataConfig
        store = DataConfig.from_env() if hasattr(DataConfig, "from_env") else DataConfig()
        return cls(host=os.getenv("CTRADER_OPEN_API_HOST", DEMO_HOST),
                   port=int(os.getenv("CTRADER_OPEN_API_PORT", "5035")),
                   symbol=os.getenv("CTRADER_SYMBOL", "XAUUSD"),
                   processed_dir=str(store.processed_dir),
                   status_path=os.getenv("DATA_FEED_STATUS_PATH", HEARTBEAT_PATH_DEFAULT),
                   state_path=os.getenv("DATA_FEED_STATE_PATH", "state/data_feed.json"))


def _heartbeat_phase(moment: datetime) -> str:
    """XAUUSD session phase, in New York time, for the operator-facing status file."""
    local = moment.astimezone(NEW_YORK)
    weekday = local.weekday()
    if weekday == 5:
        return "weekend_closed"
    if weekday == 6 and local.hour < 18:
        return "weekend_closed"
    if local.hour == 17:
        return "daily_break"
    if weekday == 4 and local.hour >= 17:
        return "weekend_closed"
    return "open"


def closed_bar(bar_time: datetime, now: datetime) -> bool:
    """True once an M1 bar stamped at ``bar_time`` is complete."""
    return now >= bar_time + pd.Timedelta(seconds=BAR_INTERVAL_SECONDS)


def _bar_is_usable(row: dict[str, Any]) -> bool:
    """True when a decoded bar is safe to hand to the store.

    Full OHLC consistency, matching what ``HistoricalDataStore.normalize``
    enforces. Checking only low<=high let a row with open above high through to
    the store, where normalize would then raise and fail the write for the whole
    batch rather than for the one bad bar.
    """
    values = [row["open"], row["high"], row["low"], row["close"]]
    if any(not isinstance(value, (int, float)) or isinstance(value, bool)
           or not math.isfinite(value) for value in values):
        return False
    high, low = row["high"], row["low"]
    if low > high or min(values) <= 0:
        return False
    if not (low <= row["open"] <= high) or not (low <= row["close"] <= high):
        return False
    volume = row["volume"]
    return isinstance(volume, int) and not isinstance(volume, bool) and volume >= 0


class LiveBarFeed:
    """Subscribe to live M1 bars and persist each closed bar exactly once.

    ``handle_bar`` is injectable so the subscription, the closed-bar rule and the
    persistence path are all testable without a broker connection.
    """

    def __init__(self, config: LiveFeedConfig, store=None,
                 handle_bar: Callable[[dict[str, Any]], None] | None = None,
                 client_factory: Callable[[str, int], Any] | None = None,
                 reactor_runner: Callable[[Callable[[], None]], None] | None = None,
                 sleep: Callable[[float], None] = time.sleep,
                 now_provider: Callable[[], datetime] | None = None):
        self.config = config
        self.config.validate()
        if os.getenv("CTRADER_DEMO_ONLY") != "true" and config.demo_only_required:
            raise LiveFeedConfigError("live_feed_demo_only_required",
                                      "CTRADER_DEMO_ONLY=true is required for the live data feed")
        if store is None:
            from .data import DataConfig, HistoricalDataStore
            # Path, not str: DataConfig does path arithmetic, and a str here made
            # every write fail with an AttributeError that the message handler
            # then reported as a rejected bar.
            store = HistoricalDataStore(DataConfig(processed_dir=Path(config.processed_dir)))
        self.store = store
        self.handle_bar = handle_bar or self.on_bar
        self.client_factory = client_factory
        self.reactor_runner = reactor_runner
        self.sleep = sleep
        # Injected so the closed-bar rule and the forming-bar buffer can be tested
        # across a minute boundary without waiting for a real one.
        self.now = now_provider or (lambda: datetime.now(timezone.utc))
        self._stop = threading.Event()
        self.bars_written = 0
        self.last_bar_time: datetime | None = None
        self.subscribed_at: float | None = None
        self._client: Any = None
        self._discovered: dict[str, Any] = {}
        self._pending: dict[str, Any] | None = None
        self.status = {"state": "starting", "recorded_at": None, "error_code": None,
                       "bars_written": 0, "last_bar_utc": None, "session": None}

    # -- persistence ------------------------------------------------------
    def on_bar(self, bar: dict[str, Any]) -> None:
        """Accept a live bar, writing only bars known to be closed.

        The stream carries the *forming* minute, updated repeatedly, and the
        last frame for a minute arrives before that minute has closed. Testing
        each arrival against the clock therefore discards every bar, because a
        bar is never seen again once it closes. Instead the newest bar is held
        and written when a newer timestamp proves it closed; its values are
        already final at that point. A bar that is closed on arrival is written
        immediately, so there is no one-minute delay when bars arrive in order.
        """
        moment = bar["timestamp"]
        pending = self._pending
        if pending is not None:
            if moment < pending["timestamp"]:
                # Out of order or a reconnect replay; never let it rewind the store.
                return
            if moment == pending["timestamp"]:
                self._pending = bar  # same minute, fresher values
                return
            self._flush_pending()    # the held bar is now known closed
        if closed_bar(moment.to_pydatetime(), self.now()):
            self.persist_bar(bar)
        else:
            self._pending = bar

    def _flush_pending(self) -> None:
        """Write the held bar. ``persist_bar`` re-checks close, age and order."""
        pending, self._pending = self._pending, None
        if pending is not None:
            self.persist_bar(pending)

    def persist_bar(self, bar: dict[str, Any]) -> None:
        """Append one closed bar to the shared store.

        Goes through ``HistoricalDataStore.write``, which merges and swaps
        atomically, so the agent's tick, the engine and the research layer never
        observe a partial parquet file.
        """
        now = self.now()
        moment = bar["timestamp"].to_pydatetime()
        if not closed_bar(moment, now):
            return
        if now - moment > pd.Timedelta(seconds=MAX_BAR_AGE_SECONDS):
            # A reconnect replay. Accepting a late bar would move the store's
            # newest observation backwards and make a fresh bar look stale.
            self._note("stale_bar_ignored", "stale_bar_ignored")
            return
        previous = self.last_bar_time
        if previous is not None and moment <= previous:
            return
        frame = pd.DataFrame([{key: bar[key] for key in ("open", "high", "low", "close", "volume")}],
                             index=pd.DatetimeIndex([bar["timestamp"]], name="timestamp"))
        self.store.write(frame, merge=True)
        self.last_bar_time = moment
        self.bars_written += 1
        self._write_status("ok", bar_utc=bar["timestamp"].isoformat())

    def _note(self, state: str, error_code: str | None = None) -> None:
        self._write_status(state, error_code=error_code)

    def _write_status(self, state: str, error_code: str | None = None,
                      bar_utc: str | None = None) -> None:
        from .atomic import atomic_write_json
        from pathlib import Path
        now = datetime.now(timezone.utc)
        self.status.update(state=state, recorded_at=now.isoformat(), error_code=error_code,
                           bars_written=self.bars_written,
                           last_bar_utc=bar_utc or self.status.get("last_bar_utc"),
                           session=_heartbeat_phase(now),
                           age_seconds=(round((now - datetime.fromisoformat(
                               self.status["last_bar_utc"])).total_seconds(), 1)
                               if self.status.get("last_bar_utc") else None))
        try:
            atomic_write_json(Path(self.config.status_path), self.status)
        except OSError as exc:
            log.warning("data feed status write failed: %s", type(exc).__name__)

    # -- lifecycle --------------------------------------------------------
    def stop(self) -> None:
        # Drop the subscription before the socket goes away. The reactor itself is
        # stopped by the watcher in _run_reactor, which is the only thing that
        # knows whether it is running; calling reactor.stop() from here raised
        # ReactorNotRunning when the loop had already ended.
        self._stop.set()
        self._flush_pending()
        self.unsubscribe()

    def _resume(self) -> None:
        if self.subscribed_at is not None and (time.monotonic() - self.subscribed_at) < RESUBSCRIBE_SECONDS:
            return
        self._subscribe()
        self.subscribed_at = time.monotonic()

    def _ensure_client(self) -> Any:
        """The broker client, created once.

        Injected through ``client_factory`` so the whole subscription path is
        testable with no broker: the only thing a test has to supply is a client
        double that invokes its callbacks.
        """
        if self._client is None:
            if self.client_factory is not None:
                self._client = self.client_factory(self.config.host, self.config.port)
            else:
                from ctrader_open_api import Client, TcpProtocol
                self._client = Client(self.config.host, self.config.port, TcpProtocol)
        return self._client

    def _discover(self, done: Callable[[], None] | None = None) -> None:
        """Authenticate the application, then resolve the demo account and symbol.

        Application auth first: the broker answers a token request sent before it
        with ``UNSUPPORTED_MESSAGE``. Then either the configured account, or
        discovery narrowed to accounts the broker explicitly classifies as demo.
        An account the broker never classified is not demo, so ``demo_accounts``
        excludes it rather than admitting it.
        """
        self._authenticate(lambda: self._discover_account(done))

    def _discover_account(self, done: Callable[[], None] | None = None) -> None:
        """Resolve the demo account and XAUUSD symbol id, then ``done``.

        Asynchronous, because every step is a round trip. A failure raises
        ``LiveFeedUnavailable`` with a stable code instead of subscribing blind.
        """
        from ctrader_open_api import Protobuf
        from ctrader_open_api.messages.OpenApiMessages_pb2 import (
            ProtoOAAccountAuthReq, ProtoOAGetAccountListByAccessTokenReq, ProtoOASymbolsListReq)
        from .data import CTraderOpenApiConfig, _error_code

        # Reuses the downloader's config, so the feed inherits the same demo-only
        # flag check and the same pinned host. A second path to the broker would
        # be a second place for that boundary to be forgotten.
        credentials = CTraderOpenApiConfig.from_env()
        client = self._ensure_client()

        def fail(code: str, message: str) -> None:
            self._note("unavailable", code)
            raise LiveFeedUnavailable(code, message)

        def got_symbols(response: Any, *_args: Any) -> None:
            message = Protobuf.extract(response)
            code = _error_code(message)
            if code is not None:
                fail(code, f"symbol list rejected: {code}")
            resolved = resolve_symbol(list(message.symbol), self.config.symbol)
            if resolved is None:
                fail("live_feed_symbol_not_found",
                     f"symbol {self.config.symbol!r} is not available on the demo account")
            symbol_id, symbol_name = resolved
            self._discovered.update(symbol_id=int(symbol_id), symbol_name=symbol_name)
            # No symbol-detail request: the live trendbar payload carries absolute
            # OHLC, so `digits` is a display concern the feed does not need. One
            # fewer round trip and one fewer way to fail before subscribing.
            if done is not None:
                done()

        def account_ok(response: Any, index: int = 0) -> None:
            message = Protobuf.extract(response)
            code = _error_code(message)
            if code is not None:
                # An invalid token is fatal for every account, so only a
                # per-account authorization failure moves on to the next one.
                if code != "CH_ACCESS_TOKEN_INVALID" and self._discovered.get("accounts"):
                    use_account(index + 1)
                    return
                fail(code, f"account auth rejected: {code}")
            client.send(ProtoOASymbolsListReq(ctidTraderAccountId=self._discovered["account_id"],
                                              includeArchivedSymbols=False),
                        responseTimeoutInSeconds=30).addCallbacks(got_symbols, transport_failed)

        def use_account(index: int) -> None:
            accounts = self._discovered.get("accounts") or []
            if index >= len(accounts):
                fail("live_feed_no_demo_account", "no authorized demo account serves the feed")
            account_id = int(accounts[index].ctidTraderAccountId)
            self._discovered["account_id"] = account_id
            client.send(ProtoOAAccountAuthReq(ctidTraderAccountId=account_id,
                                              accessToken=credentials.access_token),
                        responseTimeoutInSeconds=30).addCallbacks(
                lambda response, i=index: account_ok(response, i), transport_failed)

        def got_accounts(response: Any) -> None:
            message = Protobuf.extract(response)
            if _error_code(message) is not None:
                fail("live_feed_account_list_failed", "the broker rejected the account list request")
            accounts = demo_accounts(list(message.ctidTraderAccount))
            if not accounts:
                fail("live_feed_no_demo_account",
                     "no account the broker explicitly reports as demo is authorized for this token")
            self._discovered["accounts"] = accounts
            use_account(0)

        def transport_failed(failure: Any = None) -> None:
            self._note("transport_error", "transport_error")
            self._stop.set()

        if credentials.account_id is not None:
            self._discovered["account_id"] = int(credentials.account_id)
            client.send(ProtoOAAccountAuthReq(ctidTraderAccountId=int(credentials.account_id),
                                              accessToken=credentials.access_token),
                        responseTimeoutInSeconds=30).addCallbacks(account_ok, transport_failed)
        else:
            client.send(ProtoOAGetAccountListByAccessTokenReq(accessToken=credentials.access_token),
                        responseTimeoutInSeconds=30).addCallbacks(got_accounts, transport_failed)

    def _authenticate(self, then: Callable[[], None]) -> None:
        """Application auth, which the broker requires before any token request.

        Sending the account list first is answered ``UNSUPPORTED_MESSAGE``, so
        this cannot be reordered or skipped.
        """
        from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOAApplicationAuthReq
        from .data import CTraderOpenApiConfig, _error_code

        credentials = CTraderOpenApiConfig.from_env()
        client = self._ensure_client()

        def app_ok(_response: Any) -> None:
            then()

        def app_failed(response: Any) -> None:
            code = _error_code(response)
            self._note("unavailable", "live_feed_app_auth_failed")
            raise LiveFeedUnavailable("live_feed_app_auth_failed",
                                      f"cTrader application auth rejected: {code or 'no code'}")

        client.send(ProtoOAApplicationAuthReq(clientId=credentials.client_id,
                                              clientSecret=credentials.client_secret),
                    responseTimeoutInSeconds=30).addCallbacks(app_ok, app_failed)

    def _subscribe(self) -> None:
        """Subscribe to live M1 trendbars for the discovered account and symbol.

        Runs discovery first, because the request needs both ids. The broker
        refuses a trendbar subscription before a spot subscription with
        ``INVALID_REQUEST: Impossible to get trendbars before the spot
        subscribing``, so the spot request is not optional.
        """
        from ctrader_open_api.messages.OpenApiMessages_pb2 import (
            ProtoOASubscribeLiveTrendbarReq, ProtoOASubscribeSpotsReq)
        from ctrader_open_api.messages.OpenApiModelMessages_pb2 import ProtoOATrendbarPeriod
        from .data import _error_code

        client = self._ensure_client()

        def guard(what: str, then: Callable[[], None]) -> Callable[[Any], None]:
            def check(response: Any) -> None:
                # A rejected request still arrives as a successful callback
                # carrying ProtoOAErrorRes, so the code has to be read or a
                # refused subscription would be recorded as a confirmed one.
                code = _error_code(response)
                if code is not None:
                    self._note("subscribe_failed", "subscribe_failed")
                    raise LiveFeedUnavailable("live_feed_subscribe_rejected",
                                              f"{what} rejected: {code}")
                then()
            return check

        def confirmed() -> None:
            self.subscribed_at = time.monotonic()
            self._write_status("ok")

        def send_trendbars() -> None:
            self._note("subscribing")
            client.send(ProtoOASubscribeLiveTrendbarReq(
                ctidTraderAccountId=int(self._discovered["account_id"]),
                period=ProtoOATrendbarPeriod.M1,
                symbolId=int(self._discovered["symbol_id"])),
                responseTimeoutInSeconds=30).addCallbacks(
                guard("live trendbar subscription", confirmed), self._subscribe_failed)

        def send_spots() -> None:
            # subscribeToSpotTimestamp=0 asks for no spot backfill: this feed only
            # wants bars, and a backfill would be a burst of stale ticks.
            self._note("subscribing_spots")
            client.send(ProtoOASubscribeSpotsReq(
                ctidTraderAccountId=int(self._discovered["account_id"]),
                # symbolId is repeated on this request, unlike the trendbar one.
                symbolId=[int(self._discovered["symbol_id"])], subscribeToSpotTimestamp=0),
                responseTimeoutInSeconds=30).addCallbacks(
                guard("spot subscription", send_trendbars), self._subscribe_failed)

        if self._discovered.get("symbol_id") is not None:
            send_spots()
        else:
            self._discover(done=send_spots)

    def _subscribe_failed(self, failure: Any = None) -> None:
        """A subscription request that never got an answer.

        Stops rather than retrying: the smoke test and the service both treat a
        feed that cannot subscribe as a feed that is not running, and a silent
        retry would report neither.
        """
        self._note("subscribe_failed", "subscribe_failed")
        self._stop.set()

    def unsubscribe(self) -> None:
        """Drop the subscription so a restart cannot replay bars into the store.

        Best effort: a socket that is already gone has nothing to unsubscribe.
        ``MAX_BAR_AGE_SECONDS`` remains the backstop, but a late bar is still a
        bar written out of order.
        """
        if self._discovered.get("symbol_id") is None or self._client is None:
            return
        from ctrader_open_api.messages.OpenApiMessages_pb2 import (
            ProtoOASubscribeSpotsReq, ProtoOAUnsubscribeLiveTrendbarReq)
        from ctrader_open_api.messages.OpenApiModelMessages_pb2 import ProtoOATrendbarPeriod
        try:
            # The spot subscription has to be dropped too, or a restart leaves two.
            self._client.send(ProtoOASubscribeSpotsReq(
                ctidTraderAccountId=int(self._discovered["account_id"]),
                symbolId=[int(self._discovered["symbol_id"])], subscribeToSpotTimestamp=0),
                responseTimeoutInSeconds=10)
            self._client.send(ProtoOAUnsubscribeLiveTrendbarReq(
                ctidTraderAccountId=int(self._discovered["account_id"]),
                period=ProtoOATrendbarPeriod.M1,
                symbolId=int(self._discovered["symbol_id"])), responseTimeoutInSeconds=10)
        except Exception as exc:  # noqa: BLE001 - teardown must not raise into a signal handler
            log.warning("data feed unsubscribe failed: %s", type(exc).__name__)

    def run(self, iterations: int | None = None) -> dict[str, Any]:
        """Drive the subscription until stopped.

        ``iterations`` bounds the loop. With an injected ``reactor_runner`` the
        loop is driven deterministically, which is how the subscription is tested
        with no broker. Without one, ``iterations`` becomes a wall-clock bound on
        the real reactor, so the supervised smoke test actually returns.
        """
        if self.reactor_runner is not None:
            self._resume()
            for _ in range(iterations or 1):
                if self._stop.is_set():
                    break
                self.sleep(0)
            return dict(self.status)
        return self._run_reactor(SMOKE_TEST_SECONDS if iterations is not None else None)

    def _run_reactor(self, bound_seconds: float | None = None) -> dict[str, Any]:
        """Run the real subscription until stopped.

        The callback names and signatures are the SDK's, verified against the
        installed ``ctrader_open_api``: ``setConnectedCallback(client)``,
        ``setMessageReceivedCallback(client, message)`` and
        ``setDisconnectedCallback(client, reason)``, with ``startService()`` and
        no error callback. Every response arrives as a ``ProtoMessage`` envelope,
        so it is parsed with ``Protobuf.extract`` before use.
        """
        from twisted.internet import reactor
        from ctrader_open_api import Protobuf

        client = self._ensure_client()

        def on_message(_client: Any, message: Any) -> None:
            try:
                bars = self._bars_from(Protobuf.extract(message))
            except Exception as exc:  # a bad frame must not kill the feed
                self._note("bar_rejected", type(exc).__name__)
                return
            for bar in bars:
                try:
                    self.handle_bar(bar)
                except Exception as exc:
                    # Distinguished from a bad frame: this is the store refusing
                    # the write, which is an operator problem, not stream noise.
                    self._note("bar_write_failed", type(exc).__name__)

        def on_connected(_client: Any) -> None:
            # Discovery and the subscription need a connected client, so they are
            # issued on connect rather than before the reactor starts.
            try:
                self._subscribe()
            except LiveFeedUnavailable:
                raise
            self._schedule_resubscribe(reactor)

        def on_disconnected(_client: Any, reason: Any = None) -> None:
            self.subscribed_at = None
            self._note("disconnected", "transport_error")
            if bound_seconds is None and not self._stop.is_set():
                self._note("reconnecting")
                reactor.callLater(RECONNECT_SECONDS, client.startService)

        client.setConnectedCallback(on_connected)
        client.setMessageReceivedCallback(on_message)
        client.setDisconnectedCallback(on_disconnected)

        def start() -> None:
            client.startService()

        reactor.callWhenRunning(start)
        # Not "ok": nothing is connected or subscribed yet. Claiming otherwise
        # would make /api/health report a working feed that has sent no bar.
        self._note("connecting")

        def watch_stop() -> None:
            # Nothing else stops the reactor: without this a stop request, the
            # smoke-test bound, or a SIGTERM would leave the process hanging
            # until systemd killed it at TimeoutStopSec.
            if self._stop.is_set():
                reactor.stop()
                return
            reactor.callLater(STOP_POLL_SECONDS, watch_stop)

        reactor.callLater(STOP_POLL_SECONDS, watch_stop)
        if bound_seconds is not None:
            # The supervised smoke test: bound the wall clock so `data-feed once`
            # returns, and stop early once a bar has actually been written.
            reactor.callLater(bound_seconds, self._stop.set)
        reactor.run()
        return dict(self.status)

    def _schedule_resubscribe(self, reactor: Any) -> None:
        """Re-subscribe on a cadence so a silently dropped stream recovers.

        ``RESUBSCRIBE_SECONDS`` is measured from the *confirmed* subscription, so
        this never fires on a socket that never came up.
        """

        def tick() -> None:
            if self._stop.is_set():
                return
            try:
                self._subscribe()
            except LiveFeedUnavailable:
                self._note("resubscribe_failed", "resubscribe_failed")
            reactor.callLater(RESUBSCRIBE_SECONDS, tick)

        reactor.callLater(RESUBSCRIBE_SECONDS, tick)

    def _bars_from(self, payload: Any) -> list[dict[str, Any]]:
        """Pull closed-bar candidates out of one live subscription payload.

        The live stream arrives as ``ProtoOASpotEvent`` frames carrying a
        repeated ``trendbar`` field, and each bar is the same low-plus-delta
        representation the historical downloader decodes, not absolute OHLC. So
        the decoding is delegated to :func:`trendbars_to_frame` rather than
        reimplemented: two decoders for one wire format is how they drift apart.
        """
        from .data import trendbars_to_frame

        items = getattr(payload, "trendbar", None)
        if not items:
            return []
        try:
            frame = trendbars_to_frame(list(items))
        except (AttributeError, TypeError, ValueError) as exc:
            self._note("bar_rejected", type(exc).__name__)
            return []
        rows: list[dict[str, Any]] = []
        for moment, record in frame.iterrows():
            row = {"timestamp": moment,
                   "open": float(record["open"]), "high": float(record["high"]),
                   "low": float(record["low"]), "close": float(record["close"]),
                   "volume": int(record["volume"])}
            if _bar_is_usable(row):
                rows.append(row)
        return rows

        return rows


def run_feed(config: LiveFeedConfig | None = None, iterations: int | None = None) -> dict[str, Any]:
    try:
        feed = LiveBarFeed(config or LiveFeedConfig.from_env())
    except LiveFeedConfigError as exc:
        # A refused configuration never reaches a feed object, so the status
        # file is written here or the operator is left with nothing at all.
        from .atomic import atomic_write_json
        from pathlib import Path
        atomic_write_json(Path((config or LiveFeedConfig.from_env()).status_path),
                          {"state": "unavailable", "error_code": exc.error_code,
                           "recorded_at": datetime.now(timezone.utc).isoformat(),
                           "session": _heartbeat_phase(datetime.now(timezone.utc)),
                           "bars_written": 0, "last_bar_utc": None, "detail": exc.detail})
        raise

    def handle_signal(signum, frame):  # noqa: ARG001
        feed.stop()
        feed._write_status("stopped")

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, handle_signal)
        except ValueError:
            pass
    try:
        return feed.run(iterations=iterations)
    except LiveFeedUnavailable as exc:
        # Write the status before propagating: a feed that cannot subscribe is
        # exactly the condition /api/health has to show, and a restart loop
        # would otherwise leave no evidence at all.
        feed._write_status("unavailable", error_code=exc.error_code)
        raise
