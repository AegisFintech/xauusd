from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import os
import re
from typing import Any

import pandas as pd

log = logging.getLogger(__name__)
REQUIRED = ("open", "high", "low", "close", "volume")

@dataclass(frozen=True)
class DataConfig:
    raw_dir: Path = Path("data/raw")
    processed_dir: Path = Path("data/processed")
    symbol: str = "XAUUSD"
    timeframe: str = "M1"

class HistoricalDataStore:
    """Local OHLCV store. The adapter accepts historical exports only; no execution calls."""
    def __init__(self, config: DataConfig|None=None): self.config=config or DataConfig()
    @property
    def path(self) -> Path: return self.config.processed_dir / f"{self.config.symbol}_{self.config.timeframe}.parquet"
    def normalize(self, bars: pd.DataFrame) -> pd.DataFrame:
        x=bars.copy()
        # Accept either an indexed frame or a conventional timestamp column.
        if not isinstance(x.index, pd.DatetimeIndex):
            time_col = next((c for c in x.columns if c.lower() in {"timestamp", "time", "date"}), None)
            if time_col is None:
                raise ValueError("bars need a DatetimeIndex or timestamp/time/date column")
            x.index = x.pop(time_col)
        x.index=pd.to_datetime(x.index, utc=True, errors="raise"); x.index.name="timestamp"; x=x.sort_index()
        missing=[c for c in REQUIRED if c not in x.columns]
        if missing: raise ValueError(f"missing columns: {missing}")
        x=x[list(REQUIRED)].apply(pd.to_numeric, errors="coerce").dropna(); x=x[~x.index.duplicated(keep="last")]
        if (x.low>x.high).any() or (x.open> x.high).any() or (x.open<x.low).any() or (x.close>x.high).any() or (x.close<x.low).any() or (x.volume<0).any(): raise ValueError("invalid OHLCV values")
        return x
    def validate(self, bars: pd.DataFrame) -> dict:
        x=self.normalize(bars)
        if x.empty:
            return {"rows": 0, "start": None, "end": None, "absent_minutes": 0, "gap_events": 0, "gaps": [], "duplicates": int(bars.index.duplicated().sum())}
        expected=pd.date_range(x.index.min(),x.index.max(),freq="min",tz="UTC"); gaps=expected.difference(x.index)
        deltas=x.index.to_series().diff(); events=x.index[deltas>pd.Timedelta(minutes=1)]
        gap_events=[{"after":(timestamp-delta).isoformat(),"before":timestamp.isoformat(),"minutes":int(delta/pd.Timedelta(minutes=1))-1} for timestamp,delta in ((t,deltas.loc[t]) for t in events)]
        return {"rows":len(x),"start":x.index.min().isoformat(),"end":x.index.max().isoformat(),"absent_minutes":int(len(gaps)),"gap_events":len(gap_events),"gaps":gap_events[:100],"duplicates":int(bars.index.duplicated().sum())}
    def write(self, bars: pd.DataFrame, merge=True) -> pd.DataFrame:
        self.config.processed_dir.mkdir(parents=True,exist_ok=True); x=self.normalize(bars)
        if merge and self.path.exists(): x=pd.concat([pd.read_parquet(self.path),x]).sort_index(); x=x[~x.index.duplicated(keep="last")]
        x.to_parquet(self.path, engine="pyarrow"); return x
    def read(self) -> pd.DataFrame:
        if not self.path.exists(): raise FileNotFoundError(self.path)
        return pd.read_parquet(self.path)

class CTraderHistoricalAdapter:
    """Import cTrader CSV exports into the normalized historical store."""
    def __init__(self, store: HistoricalDataStore): self.store=store
    def import_csv(self, source: Path, merge=True) -> dict:
        df=pd.read_csv(source); time_col=next((c for c in df.columns if c.lower() in {"timestamp","time","date"}),None)
        if not time_col: raise ValueError("CSV needs timestamp/time/date column")
        df.index=pd.to_datetime(df.pop(time_col), utc=True); return self.store.validate(self.store.write(df,merge=merge))


@dataclass(frozen=True)
class CTraderOpenApiConfig:
    client_id: str
    client_secret: str
    access_token: str
    account_id: int
    host: str = "demo.ctraderapi.com"
    port: int = 5035

    @classmethod
    def from_env(cls) -> "CTraderOpenApiConfig":
        values = {
            "client_id": os.getenv("CTRADER_CLIENT_ID"),
            "client_secret": os.getenv("CTRADER_CLIENT_SECRET"),
            "access_token": os.getenv("CTRADER_ACCESS_TOKEN"),
            "account_id": os.getenv("CTRADER_CTID_TRADER_ACCOUNT_ID"),
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise RuntimeError(f"missing cTrader Open API settings: {', '.join(missing)}")
        return cls(
            client_id=str(values["client_id"]),
            client_secret=str(values["client_secret"]),
            access_token=str(values["access_token"]),
            account_id=int(str(values["account_id"])),
            host=os.getenv("CTRADER_OPEN_API_HOST", "demo.ctraderapi.com"),
            port=int(os.getenv("CTRADER_OPEN_API_PORT", "5035")),
        )


def trendbars_to_frame(trendbars: list[Any], digits: int = 5) -> pd.DataFrame:
    """Decode cTrader's low-plus-delta trendbar representation."""
    # Open API encodes all trendbar prices as 1/100000, independently of the
    # symbol's display digits. ``digits`` is retained for API compatibility and
    # archived metadata, but must not be used as the wire-price scale.
    scale = 100_000
    rows = []
    for bar in trendbars:
        low = int(bar.low)
        rows.append({
            "timestamp": pd.to_datetime(int(bar.utcTimestampInMinutes), unit="m", utc=True),
            "open": (low + int(bar.deltaOpen)) / scale,
            "high": (low + int(bar.deltaHigh)) / scale,
            "low": low / scale,
            "close": (low + int(bar.deltaClose)) / scale,
            "volume": int(bar.volume),
        })
    if not rows:
        return pd.DataFrame(columns=REQUIRED, index=pd.DatetimeIndex([], name="timestamp", tz="UTC"))
    return pd.DataFrame(rows).set_index("timestamp").sort_index()


class CTraderOpenApiDownloader:
    """Read-only cTrader Open API client for symbols and historical trendbars."""

    def __init__(self, config: CTraderOpenApiConfig, store: HistoricalDataStore):
        self.config = config
        self.store = store

    @staticmethod
    def _timestamp_ms(value: str | datetime | pd.Timestamp) -> int:
        timestamp = pd.Timestamp(value)
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        else:
            timestamp = timestamp.tz_convert("UTC")
        return int(timestamp.timestamp() * 1000)

    def download(self, start: str | datetime, end: str | datetime | None = None, page_size: int = 5000) -> dict:
        if not 1 <= page_size <= 5000:
            raise ValueError("page_size must be between 1 and 5000")
        start_ms = self._timestamp_ms(start)
        end_ms = self._timestamp_ms(end or datetime.now(timezone.utc))
        if start_ms >= end_ms:
            raise ValueError("start must be earlier than end")
        pages, metadata = self._fetch(start_ms, end_ms, page_size)
        frames = [trendbars_to_frame(page["trendbars"], metadata["digits"]) for page in pages]
        bars = pd.concat(frames).sort_index() if frames else trendbars_to_frame([])
        bars = bars[~bars.index.duplicated(keep="last")]
        lower = pd.to_datetime(start_ms, unit="ms", utc=True)
        upper = pd.to_datetime(end_ms, unit="ms", utc=True)
        bars = bars[(bars.index >= lower) & (bars.index <= upper)]
        archive_paths = self._archive(pages, metadata, start_ms, end_ms)
        merged = self.store.write(bars, merge=True) if not bars.empty else (self.store.read() if self.store.path.exists() else bars)
        result = self.store.validate(merged)
        result.update({
            "downloaded_rows": int(len(bars)),
            "pages": len(pages),
            "symbol": metadata["symbol_name"],
            "symbol_id": metadata["symbol_id"],
            "raw_archives": [str(path) for path in archive_paths],
            "processed_path": str(self.store.path),
        })
        return result

    def _fetch(self, start_ms: int, end_ms: int, page_size: int) -> tuple[list[dict], dict]:
        # Twisted's global reactor is intentionally isolated to one CLI invocation.
        from twisted.internet import reactor
        from ctrader_open_api import Client, Protobuf, TcpProtocol
        from ctrader_open_api.messages.OpenApiMessages_pb2 import (
            ProtoOAAccountAuthReq, ProtoOAApplicationAuthReq, ProtoOAGetTrendbarsReq,
            ProtoOASymbolByIdReq, ProtoOASymbolsListReq,
        )
        from ctrader_open_api.messages.OpenApiModelMessages_pb2 import ProtoOATrendbarPeriod

        client = Client(self.config.host, self.config.port, TcpProtocol)
        state: dict[str, Any] = {"pages": [], "cursor": end_ms}

        def stop_error(failure):
            message = failure.getErrorMessage() if hasattr(failure, "getErrorMessage") else str(failure)
            state["error"] = RuntimeError(f"cTrader request failed: {message}")
            if reactor.running:
                reactor.stop()

        def request_page():
            request = ProtoOAGetTrendbarsReq(
                ctidTraderAccountId=self.config.account_id, symbolId=state["symbol_id"],
                period=ProtoOATrendbarPeriod.Value(self.store.config.timeframe),
                fromTimestamp=start_ms, toTimestamp=state["cursor"], count=page_size,
            )
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(got_page, stop_error)

        def got_page(response):
            message = Protobuf.extract(response)
            bars = list(message.trendbar)
            if not bars:
                reactor.stop(); return
            state["pages"].append({"trendbars": bars})
            earliest_ms = min(int(bar.utcTimestampInMinutes) for bar in bars) * 60_000
            if earliest_ms <= start_ms:
                reactor.stop(); return
            state["cursor"] = earliest_ms - 1
            request_page()

        def got_symbol(response):
            message = Protobuf.extract(response)
            if not message.symbol:
                stop_error(Exception("cTrader returned no symbol details")); return
            state["digits"] = int(message.symbol[0].digits)
            request_page()

        def got_symbols(response):
            message = Protobuf.extract(response)
            wanted = re.sub(r"[^A-Z0-9]", "", self.store.config.symbol.upper())
            matches = [s for s in message.symbol if re.sub(r"[^A-Z0-9]", "", s.symbolName.upper()) == wanted]
            if not matches:
                available = [s.symbolName for s in message.symbol if "XAU" in s.symbolName.upper()]
                stop_error(Exception(f"symbol {self.store.config.symbol!r} not found; XAU candidates: {available}")); return
            symbol = next((s for s in matches if s.enabled), matches[0])
            state.update(symbol_id=int(symbol.symbolId), symbol_name=symbol.symbolName)
            request = ProtoOASymbolByIdReq(ctidTraderAccountId=self.config.account_id, symbolId=[symbol.symbolId])
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(got_symbol, stop_error)

        def account_ok(_):
            request = ProtoOASymbolsListReq(ctidTraderAccountId=self.config.account_id, includeArchivedSymbols=False)
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(got_symbols, stop_error)

        def app_ok(_):
            request = ProtoOAAccountAuthReq(ctidTraderAccountId=self.config.account_id, accessToken=self.config.access_token)
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(account_ok, stop_error)

        def connected(_):
            request = ProtoOAApplicationAuthReq(clientId=self.config.client_id, clientSecret=self.config.client_secret)
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(app_ok, stop_error)

        client.setConnectedCallback(connected)
        client.startService()
        # Every request has its own 30-second timeout. The overall allowance is
        # intentionally long because multi-year M1 backfills require many pages.
        reactor.callLater(3600, lambda: stop_error(Exception("cTrader download timed out")) if reactor.running else None)
        reactor.run()
        if "error" in state:
            raise state["error"]
        metadata = {key: state[key] for key in ("symbol_id", "symbol_name", "digits")}
        return state["pages"], metadata

    def _archive(self, pages: list[dict], metadata: dict, start_ms: int, end_ms: int) -> list[Path]:
        directory = self.store.config.raw_dir / "ctrader" / metadata["symbol_name"] / self.store.config.timeframe
        directory.mkdir(parents=True, exist_ok=True)
        paths = []
        for number, page in enumerate(pages, start=1):
            bars = page["trendbars"]
            payload = {
                "source": "ctrader-open-api", "account_id": self.config.account_id,
                "symbol": metadata["symbol_name"], "symbol_id": metadata["symbol_id"],
                "digits": metadata["digits"], "timeframe": self.store.config.timeframe,
                "requested_from_ms": start_ms, "requested_to_ms": end_ms,
                "bars": [{field.name: getattr(bar, field.name) for field in bar.DESCRIPTOR.fields} for bar in bars],
            }
            first = min(int(bar.utcTimestampInMinutes) for bar in bars) if bars else 0
            last = max(int(bar.utcTimestampInMinutes) for bar in bars) if bars else 0
            path = directory / f"{first}_{last}_page{number:04d}.json"
            if not path.exists():
                path.write_text(json.dumps(payload, separators=(",", ":")))
            paths.append(path)
        return paths
