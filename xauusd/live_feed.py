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
# Bars whose open is older than this are ignored: a reconnect can replay
# history, and a late bar must never overwrite a newer one.
MAX_BAR_AGE_SECONDS = 15 * 60
HEARTBEAT_PATH_DEFAULT = "reports/data_feed_status.json"


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
            raise ValueError(f"live feed is restricted to {DEMO_HOST}")
        if not isinstance(self.port, int) or isinstance(self.port, bool) or self.port <= 0:
            raise ValueError("live feed port must be a positive integer")
        if not self.symbol.strip():
            raise ValueError("live feed symbol is required")
        if not isinstance(self.backfill_bars, int) or self.backfill_bars < 1:
            raise ValueError("backfill_bars must be a positive integer")

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


def _trendbar_row(payload: Any) -> dict[str, Any] | None:
    """Normalise one live trendbar into an OHLCV row, or None when unusable."""
    if isinstance(payload, dict):
        get = payload.get
    else:
        get = lambda name, default=None: getattr(payload, name, default)  # noqa: E731
    stamp = get("timeStamp") or get("timestamp")
    if stamp is None:
        return None
    try:
        moment = pd.Timestamp(int(stamp), unit="ms", tz="UTC")
    except (TypeError, ValueError, OverflowError):
        return None
    values = {"open": get("open"), "high": get("high"), "low": get("low"), "close": get("close")}
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value)
           for value in values.values()):
        return None
    # Full OHLC consistency, matching what HistoricalDataStore.normalize enforces.
    # Checking only low<=high let a row with open above high through to the store,
    # where normalize would then raise and fail the write for the whole batch.
    high, low = values["high"], values["low"]
    if low > high or min(values.values()) <= 0:
        return None
    if not (low <= values["open"] <= high) or not (low <= values["close"] <= high):
        return None
    volume = get("tickVolume") or get("volume") or 0
    if not isinstance(volume, (int, float)) or isinstance(volume, bool) or not math.isfinite(volume) or volume < 0:
        volume = 0
    return {"timestamp": moment, **values, "volume": int(volume)}


class LiveBarFeed:
    """Subscribe to live M1 bars and persist each closed bar exactly once.

    ``handle_bar`` is injectable so the subscription, the closed-bar rule and the
    persistence path are all testable without a broker connection.
    """

    def __init__(self, config: LiveFeedConfig, store=None,
                 handle_bar: Callable[[dict[str, Any]], None] | None = None,
                 client_factory: Callable[[str, int], Any] | None = None,
                 reactor_runner: Callable[[Callable[[], None]], None] | None = None,
                 sleep: Callable[[float], None] = time.sleep):
        self.config = config
        self.config.validate()
        if os.getenv("CTRADER_DEMO_ONLY") != "true" and config.demo_only_required:
            raise ValueError("CTRADER_DEMO_ONLY=true is required for the live data feed")
        if store is None:
            from .data import DataConfig, HistoricalDataStore
            store = HistoricalDataStore(DataConfig(processed_dir=config.processed_dir))
        self.store = store
        self.handle_bar = handle_bar or self.persist_bar
        self.client_factory = client_factory
        self.reactor_runner = reactor_runner
        self.sleep = sleep
        self._stop = threading.Event()
        self.bars_written = 0
        self.last_bar_time: datetime | None = None
        self.subscribed_at: float | None = None
        self.status = {"state": "starting", "recorded_at": None, "error_code": None,
                       "bars_written": 0, "last_bar_utc": None, "session": None}

    # -- persistence ------------------------------------------------------
    def persist_bar(self, bar: dict[str, Any]) -> None:
        """Append one closed bar to the shared store.

        Goes through ``HistoricalDataStore.write``, which merges and swaps
        atomically, so the agent's tick, the engine and the research layer never
        observe a partial parquet file.
        """
        now = datetime.now(timezone.utc)
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
        self._stop.set()

    def _resume(self) -> None:
        if self.subscribed_at is not None and (time.monotonic() - self.subscribed_at) < RESUBSCRIBE_SECONDS:
            return
        self._subscribe()
        self.subscribed_at = time.monotonic()

    def _subscribe(self) -> None:
        raise NotImplementedError

    def _discover(self) -> dict[str, Any]:
        raise NotImplementedError

    def run(self, iterations: int | None = None) -> dict[str, Any]:
        """Drive the subscription until stopped.

        ``iterations`` bounds the loop for tests. The real service passes nothing
        and runs until SIGTERM.
        """
        self._resume()
        if self.reactor_runner is not None:
            # Deterministic driving for tests: no reactor, no sockets.
            for _ in range(iterations or 1):
                if self._stop.is_set():
                    break
                self.sleep(0)
            return dict(self.status)
        return self._run_reactor()

    def _run_reactor(self) -> dict[str, Any]:
        from twisted.internet import reactor
        from ctrader_open_api import Client, TcpProtocol

        client = (self.client_factory(self.config.host, self.config.port) if self.client_factory
                  else Client(self.config.host, self.config.port, TcpProtocol))
        self._client = client
        state: dict[str, Any] = {"account_id": None, "symbol_id": None, "connected": False}

        def on_message(payload: Any, protobuf: Any = None) -> None:
            try:
                for bar in self._bars_from(payload):
                    self.handle_bar(bar)
            except Exception as exc:  # a bad frame must not kill the feed
                self._note("bar_rejected", type(exc).__name__)

        def on_error(failure: Any) -> None:
            self._note("transport_error", "transport_error")
            if reactor.running:
                reactor.stop()

        def on_connect(payload: Any, protobuf: Any = None) -> None:
            state["connected"] = True
            self._write_status("ok")

        client.set_on_message_callback(on_message)
        client.set_on_error_callback(on_error)
        client.set_on_connect_callback(on_connect)
        client.set_on_disconnect_callback(lambda *a: self._note("disconnected", "transport_error"))

        def start() -> None:
            client.start_service()
            client.send_wait_for_responses(
                {"version": 1, "client": None, "client_id": None, "timestamp": 0})

        reactor.callWhenRunning(start)
        self._write_status("ok")
        reactor.run()
        return dict(self.status)

    def _bars_from(self, payload: Any) -> list[dict[str, Any]]:
        """Pull closed-bar candidates out of one live subscription payload."""
        from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOATrendbarListRes  # noqa: F401
        rows: list[dict[str, Any]] = []

        def walk(node: Any, depth: int = 0) -> None:
            if depth > 4 or len(rows) >= 500:
                return
            if isinstance(node, list):
                for item in node:
                    walk(item, depth + 1)
                return
            if not isinstance(node, dict) and not hasattr(node, "trendbar"):
                return
            bars = getattr(node, "trendbar", None) or (node.get("trendbar") if isinstance(node, dict) else None)
            if bars is None:
                return
            for item in (bars if isinstance(bars, list) else [bars]):
                row = _trendbar_row(item)
                if row is not None:
                    rows.append(row)

        walk(payload)
        return rows


def run_feed(config: LiveFeedConfig | None = None, iterations: int | None = None) -> dict[str, Any]:
    feed = LiveBarFeed(config or LiveFeedConfig.from_env())

    def handle_signal(signum, frame):  # noqa: ARG001
        feed.stop()
        feed._write_status("stopped")

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, handle_signal)
        except ValueError:
            pass
    return feed.run(iterations=iterations)
