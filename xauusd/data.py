from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
import errno
import gzip
import io
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any

import numpy as np
import pandas as pd

from .atomic import atomic_write_bytes, file_lock
from .ctrader_auth import DEMO_HOST
from .paper_trading import market_is_open

log = logging.getLogger(__name__)
REQUIRED = ("open", "high", "low", "close", "volume")


def read_raw_page(path: Path) -> dict:
    """The same wire page, whether plain or losslessly gzip-compressed."""
    if path.name.endswith(".json.gz"):
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return json.load(stream)
    return json.loads(path.read_text())
# The store has three independent writers (the feed's per-minute append, the
# data-update timer, the agent's in-loop refresh). They wait for each other
# rather than racing, but a wedged writer must not hang a trading loop forever.
STORE_LOCK_TIMEOUT_SECONDS = 60.0
# Bounded wall clock for a retried download in a fresh interpreter. The Twisted
# reactor in the child has its own request timeouts; this bounds the parent.
DOWNLOAD_TIMEOUT_SECONDS = 900.0
# The CLI entry point resolves `xauusd` from the working directory, so the retry
# child must run from the repository root rather than inherit the caller's cwd.
REPO_ROOT = Path(__file__).resolve().parent.parent


class CTraderAuthError(RuntimeError):
    """A cTrader authorization request failed; ``code`` carries the Open API error code."""

    def __init__(self, code: str, description: str = ""):
        super().__init__(f"cTrader authorization error {code}: {description}")
        self.code = str(code)
        self.description = str(description)


class StoreCorruptError(OSError):
    """The store file exists but cannot be parsed.

    Raised instead of letting pyarrow's OSError through, because "OSError" in a status
    file is indistinguishable from a network or permission failure. That is exactly
    what happened on 2026-10-08: two writers shared one temporary name, the parquet
    footer became undecodable, and `data update` reported `error_type: "OSError"` with
    `error_code: null` for the rest of the day -- the operator had to reproduce the
    failure by hand to learn the store was corrupt and recoverable only from the raw
    archive. Carries a code so the failure is diagnosable without persisting exception
    text, which can contain a URL with a token in it.
    """

    code = "store_corrupt"

    def __init__(self, path: Any):
        super().__init__(f"{Path(path).name} cannot be parsed; rebuild it with `data rebuild`")
        self.path = Path(path)


def classify_store_error(exc: BaseException) -> str | None:
    """A durable code for a store failure, or None when there is nothing safe to say.

    Only codes are returned, never message text: the status file is a report, and a
    traceback or a broker URL does not belong in one.
    """
    if isinstance(exc, StoreCorruptError):
        return exc.code
    if isinstance(exc, OSError) and getattr(exc, "errno", None) == errno.ENOSPC:
        return "disk_full"
    return None


def _error_code(message: Any, detail: bool = False) -> str | None:
    """Return the cTrader error code for an error message, or None when unset."""
    code = message.get("errorCode") if isinstance(message, dict) else getattr(message, "errorCode", None)
    if not code:
        return None
    if not detail:
        return str(code)
    description = message.get("description") if isinstance(message, dict) else getattr(message, "description", None)
    return f"{code}: {description or ''}"

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
        x.index=pd.to_datetime(x.index, utc=True, errors="raise"); x.index.name="timestamp"; x=x.sort_index(kind="stable")
        missing=[c for c in REQUIRED if c not in x.columns]
        if missing: raise ValueError(f"missing columns: {missing}")
        x=x[list(REQUIRED)].apply(pd.to_numeric, errors="coerce").dropna(); x=x[~x.index.duplicated(keep="last")]
        if (x.low>x.high).any() or (x.open> x.high).any() or (x.open<x.low).any() or (x.close>x.high).any() or (x.close<x.low).any() or (x.volume<0).any(): raise ValueError("invalid OHLCV values")
        return x
    def validate(self, bars: pd.DataFrame) -> dict:
        x=self.normalize(bars)
        if x.empty:
            return {"rows": 0, "start": None, "end": None, "absent_minutes": 0, "closed_minutes": 0, "gap_events": 0, "gaps": [], "duplicates": int(bars.index.duplicated().sum())}
        expected=pd.date_range(x.index.min(),x.index.max(),freq="min",tz="UTC")
        # Separate "the market was closed" from "data is missing". Counting every
        # absent minute reported the whole weekend and the daily New York break as
        # data loss, which made a perfectly healthy store look like it had holes in
        # it and hid the gaps that actually mattered.
        absent=expected.difference(x.index)
        closed=sum(1 for minute in absent if not market_is_open(minute.to_pydatetime()))
        missing_minutes=len(absent)-closed
        deltas=x.index.to_series().diff(); events=x.index[deltas>pd.Timedelta(minutes=1)]
        gap_events=[{"after":(timestamp-delta).isoformat(),"before":timestamp.isoformat(),"minutes":int(delta/pd.Timedelta(minutes=1))-1} for timestamp,delta in ((t,deltas.loc[t]) for t in events)]
        return {"rows":len(x),"start":x.index.min().isoformat(),"end":x.index.max().isoformat(),
                # Kept for compatibility: every absent minute, closed or not.
                "absent_minutes":int(len(absent)),
                # The honest number: minutes that were open and have no bar.
                "missing_market_minutes":int(missing_minutes),
                "closed_minutes":int(closed),
                "gap_events":len(gap_events),"gaps":gap_events[:100],
                "duplicates":int(bars.index.duplicated().sum())}
    def missing_windows(self, bars: pd.DataFrame | None = None, since: Any = None,
                        min_minutes: int = 2) -> list[dict[str, Any]]:
        """Contiguous runs of market-open minutes the store does not have.

        `validate` reports gap events but keeps only the first hundred and does not
        separate a closed market from a hole, and `data update` extends the tail
        only -- so an interior gap was permanent. On 2026-10-12 the feed restarted
        and 17 minutes went missing that no later run could ever recover, because
        every run computed its start from the newest bar. This is the input to
        healing, and it counts only minutes the market was actually open, using the
        same New York session logic as every other freshness decision here.

        ``since`` bounds the scan; without it this walks seven years of gaps.
        """
        frame = self.read() if bars is None else bars
        index = frame.index
        if since is not None:
            since = pd.Timestamp(since)
            if since.tzinfo is None:
                since = since.tz_localize("UTC")
            index = index[index >= since]
        if len(index) < 2:
            return []
        deltas = index.to_series().diff()
        # Positional, not label-based: a duplicated timestamp would make `.loc`
        # return several rows and silently corrupt the window arithmetic.
        positions = np.flatnonzero((deltas > pd.Timedelta(minutes=1)).to_numpy())
        windows = []
        for position in positions:
            stamp, previous = index[position], index[position - 1]
            absent = pd.date_range(previous + pd.Timedelta(minutes=1),
                                   stamp - pd.Timedelta(minutes=1), freq="min", tz="UTC")
            open_minutes = [minute for minute in absent if market_is_open(minute.to_pydatetime())]
            if len(open_minutes) < min_minutes:
                continue
            windows.append({"start": open_minutes[0].isoformat(), "end": open_minutes[-1].isoformat(),
                            "minutes": len(open_minutes), "after": previous.isoformat(),
                            "before": stamp.isoformat()})
        return windows
    def write(self, bars: pd.DataFrame, merge=True) -> pd.DataFrame:
        """Replace the store with `bars`, merged into whatever is already there.

        One durable write path under one exclusive lock. The previous version
        hand-rolled temp-plus-replace with a *fixed* temporary name, and three
        writers touch this file concurrently: the feed's per-minute append, the
        data-update timer and the agent's in-loop refresh. On 2026-10-08 the
        timer's 18:05 Asia/Shanghai run and the feed's 10:09Z append met on
        `XAUUSD_M1.parquet.tmp`, and the file that landed had an undecodable
        thrift footer: 2,391,574 bars became unreadable, every later feed write
        failed with a bare OSError, and 15 hours of an open session were lost
        with nothing alerting. `atomic` gives each writer a unique temporary plus
        fsync; the lock makes the read-merge-swap exclusive, so a writer can
        never merge a frame that another writer has already replaced.
        """
        self.config.processed_dir.mkdir(parents=True,exist_ok=True)
        with file_lock(self.path, STORE_LOCK_TIMEOUT_SECONDS):
            x=self.normalize(bars)
            if merge and self.path.exists():
                x=pd.concat([pd.read_parquet(self.path),x]).sort_index(kind="stable"); x=x[~x.index.duplicated(keep="last")]
            buffer=io.BytesIO()
            x.to_parquet(buffer, engine="pyarrow")
            atomic_write_bytes(self.path, buffer.getvalue())
        return x
    def read(self) -> pd.DataFrame:
        if not self.path.exists(): raise FileNotFoundError(self.path)
        try:
            return pd.read_parquet(self.path)
        except (OSError, ValueError) as exc:
            # Both, because pyarrow picks the type by how the file is broken:
            # undecodable thrift metadata surfaces as OSError, and missing magic
            # bytes as ArrowInvalid, which is a ValueError. The 2026-10-08
            # corruption was the OSError form; a truncated or empty file is the
            # other. Either way the store exists and cannot be read.
            raise StoreCorruptError(self.path) from exc
    def last_timestamp(self) -> "pd.Timestamp | None":
        """The newest bar in the store, reading the index column only.

        `data update` needs just this to decide where to resume downloading, but it
        called `read()`, which decompresses all six columns of a 2.4M row frame to
        answer a one-value question: measured 0.31s and ~134 MB against 0.05s and
        ~20 MB. It runs four times a day on a timer, on a host with ~1.4 GB available
        while the agent, engine, feed and view are all resident, and it is the same
        code path that was mid-write when two writers destroyed the store on
        2026-10-08. Reading only the final row group would be cheaper still, but this
        store has three row groups, so that saves little and would assume the rows are
        ordered; `write()` sorts, yet nothing here needs to depend on it.
        """
        if not self.path.exists(): raise FileNotFoundError(self.path)
        try:
            index=pd.read_parquet(self.path, columns=[]).index
        except (OSError, ValueError) as exc:
            raise StoreCorruptError(self.path) from exc
        return index.max() if len(index) else None
    @property
    def raw_archive_dir(self) -> Path:
        return self.config.raw_dir / "ctrader" / self.config.symbol / self.config.timeframe
    def raw_archive_pages(self) -> list[tuple[int, int, Path]]:
        """Every archived raw page as ``(first_minute, last_minute, path)``, sorted.

        The downloader names a page for the bar range it holds, so the archive can be
        reasoned about without opening 4 GB of JSON.
        """
        pages = []
        directory = self.raw_archive_dir
        for path in sorted([*directory.glob("*.json"), *directory.glob("*.json.gz")]) if directory.is_dir() else []:
            parts = path.name.split("_")
            if len(parts) < 2:
                continue
            try:
                pages.append((int(parts[0]), int(parts[1]), path))
            except ValueError:
                continue
        pages.sort()
        return pages
    def raw_retention_plan(self) -> dict[str, Any]:
        """Which archived pages a minimal cover makes redundant. Deletes nothing.

        The archive grows without bound because `_archive` skips a page only when that
        exact filename already exists, so overlapping re-downloads accumulate: 6,806
        pages and 34M bar records for 2.4M unique minutes, about 14x redundant. It is
        also the only rebuild path for the store, so this reports a plan and stops.

        Two costs are stated rather than hidden. A minimal cover keeps no overlap, so a
        single corrupt surviving page has no second copy to fall back on. And the cover
        is computed from the bar ranges in the filenames, not from the bars themselves;
        verifying that would mean reading the whole archive.
        """
        pages = self.raw_archive_pages()
        if not pages:
            return {"archive": str(self.raw_archive_dir), "pages": 0, "bytes": 0,
                    "redundant_pages": 0, "redundant_bytes": 0, "deletes": "nothing"}
        ordered = sorted(pages, key=lambda entry: (entry[0], -entry[1]))
        keep: list[tuple[int, int, Path]] = []
        index, reach, gaps = 0, None, 0
        while index < len(ordered):
            best = None
            if reach is not None:
                while index < len(ordered) and ordered[index][0] <= reach + 1:
                    if best is None or ordered[index][1] > best[1]:
                        best = ordered[index]
                    index += 1
            if best is None:
                # Either the first page or a gap in the archive: nothing chosen so far
                # reaches this page, so it has to be kept to cover what follows.
                if reach is not None:
                    gaps += 1
                best = ordered[index]
                index += 1
            keep.append(best)
            reach = best[1]

        kept = {entry[2] for entry in keep}
        sizes = {entry[2]: entry[2].stat().st_size for entry in ordered}
        total = sum(sizes.values())
        cover = sum(sizes[path] for path in kept)
        full_range = [ordered[0][0], max(entry[1] for entry in ordered)]
        cover_range = [min(entry[0] for entry in keep), max(entry[1] for entry in keep)]
        return {
            "archive": str(self.raw_archive_dir),
            "pages": len(ordered), "bytes": total,
            "cover_pages": len(keep), "cover_bytes": cover,
            "redundant_pages": len(ordered) - len(keep), "redundant_bytes": total - cover,
            "redundancy_ratio": round(len(ordered) / len(keep), 2),
            "archive_range_minutes": full_range,
            "cover_range_minutes": cover_range,
            "cover_preserves_the_full_range": cover_range == full_range,
            "gaps_in_archive": gaps,
            "deletes": "nothing -- this is a plan; applying it is an operator decision",
            "cost_of_applying": ("a minimal cover keeps no overlap, so a corrupt "
                                 "surviving page has no second copy to fall back on"),
        }
    def rebuild_from_raw(self, cutoff: "pd.Timestamp | str | None" = None, chunk_pages: int = 200,
                         progress: "Callable[[str], None] | None" = None) -> dict[str, Any]:
        """Rebuild the store offline from the archived raw page cache.

        The archive under ``raw_dir/ctrader/<symbol>/<timeframe>`` holds every page the
        downloader ever fetched, so a store that can no longer be parsed is recoverable
        with no broker access. That mattered on 2026-10-09: a shared temporary name left
        2.4M bars unreadable and there was no supported way back, so recovery meant
        improvising a script under time pressure while the market was open.

        Pages are streamed and merged into one deduplicated frame a chunk at a time. The
        cache is roughly 14x redundant -- 6,806 pages and 34M bar records for 2.4M unique
        minutes -- so accumulating whole chunks and concatenating at the end needs more
        memory than this host has.

        ``cutoff`` bounds the rebuild to the range the store actually held. The archive
        reaches back years earlier, and growing the store backwards changes the dataset
        version, which is how a protected holdout gets consumed twice. When omitted the
        current store's first bar is used; a corrupt store has no first bar, so the
        cutoff then has to be given explicitly.
        """
        from types import SimpleNamespace
        pages = self.raw_archive_pages()
        if not pages:
            raise FileNotFoundError(f"no raw page archive under {self.raw_archive_dir}")

        if cutoff is None:
            try:
                cutoff = self.read().index.min()
            except StoreCorruptError:
                raise ValueError("the store is unreadable, so a cutoff is required to "
                                 "reproduce the range it held") from None
        cutoff = pd.Timestamp(cutoff)
        if cutoff.tzinfo is None:
            cutoff = cutoff.tz_localize("UTC")
        cutoff_minute = int(cutoff.timestamp() // 60)
        pages = [entry for entry in pages if entry[1] >= cutoff_minute]
        if progress:
            progress(f"replaying {len(pages)} archived pages from {cutoff.isoformat()}")

        total = None
        for start in range(0, len(pages), chunk_pages):
            frames = []
            for _, _, path in pages[start:start + chunk_pages]:
                payload = read_raw_page(path)
                frame = trendbars_to_frame([SimpleNamespace(**bar) for bar in payload["bars"]],
                                           digits=int(payload.get("digits", 2)))
                frame = frame[frame.index >= cutoff]
                if len(frame):
                    frames.append(frame)
            if not frames:
                continue
            merged = pd.concat(frames).sort_index(kind="stable")
            merged = merged[~merged.index.duplicated(keep="last")]
            total = merged if total is None else pd.concat([total, merged]).sort_index(kind="stable")
            del frames, merged
            total = total[~total.index.duplicated(keep="last")]
            if progress:
                progress(f"  {min(start + chunk_pages, len(pages))}/{len(pages)} pages, "
                         f"{len(total)} rows")
        if total is None or total.empty:
            raise ValueError(f"no archived bars at or after {cutoff.isoformat()}")
        written = self.write(total, merge=False)
        summary = self.validate(written)
        summary.update({"pages_replayed": len(pages), "cutoff": cutoff.isoformat()})
        return summary
    def positions(self, bars: pd.DataFrame, required) -> "np.ndarray":
        """Resolve a whole batch of bar timestamps to row positions in one pass.

        `DatetimeIndex.get_indexer` rebuilds a hash table over every row on each
        call, so a per-anchor lookup loop over a multi-million row M1 frame costs
        minutes and overruns the Bits shell job ceiling. This is `O((n + m) log n)`
        and returns exactly what `get_indexer` returns, `-1` for a missing bar.
        """
        index=bars.index
        if not index.is_monotonic_increasing: raise ValueError("bar index must be sorted ascending")
        if index.has_duplicates: raise ValueError("bar index must be unique")
        required=pd.DatetimeIndex(required)
        left=index.searchsorted(required, side="left")
        right=index.searchsorted(required, side="right")
        return np.where(left<right, left, -1)

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
    account_id: int | None = None
    refresh_token: str | None = None
    host: str = DEMO_HOST
    port: int = 5035

    @classmethod
    def from_env(cls) -> "CTraderOpenApiConfig":
        values = {
            "client_id": os.getenv("CTRADER_CLIENT_ID"),
            "client_secret": os.getenv("CTRADER_CLIENT_SECRET"),
            "access_token": os.getenv("CTRADER_ACCESS_TOKEN"),
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise RuntimeError(f"missing cTrader Open API settings: {', '.join(missing)}")
        account_raw = os.getenv("CTRADER_CTID_TRADER_ACCOUNT_ID")
        if account_raw and not str(account_raw).strip().isdigit():
            raise RuntimeError("CTRADER_CTID_TRADER_ACCOUNT_ID must be a positive integer when configured")
        config = cls(
            client_id=str(values["client_id"]),
            client_secret=str(values["client_secret"]),
            access_token=str(values["access_token"]),
            account_id=int(str(account_raw).strip()) if account_raw and str(account_raw).strip() else None,
            refresh_token=os.getenv("CTRADER_REFRESH_TOKEN"),
            host=os.getenv("CTRADER_OPEN_API_HOST", DEMO_HOST),
            port=int(os.getenv("CTRADER_OPEN_API_PORT", "5035")),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if os.getenv("CTRADER_DEMO_ONLY") != "true":
            raise RuntimeError("CTRADER_DEMO_ONLY=true is required for cTrader data updates")
        if self.host != DEMO_HOST:
            raise RuntimeError(f"cTrader data updates are restricted to {DEMO_HOST}")
        if self.port <= 0:
            raise RuntimeError("cTrader port must be positive")
        if self.account_id is not None and (not isinstance(self.account_id, int) or
                                            isinstance(self.account_id, bool) or self.account_id <= 0):
            raise RuntimeError("account_id must be a positive integer when configured")


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
        # Boundary check first, so a refusal never reaches the network.
        self.config.validate()
        if not 1 <= page_size <= 5000:
            raise ValueError("page_size must be between 1 and 5000")
        start_ms = self._timestamp_ms(start)
        end_ms = self._timestamp_ms(end or datetime.now(timezone.utc))
        if start_ms >= end_ms:
            raise ValueError("start must be earlier than end")
        try:
            pages, metadata = self._fetch(start_ms, end_ms, page_size)
        except CTraderAuthError as exc:
            if exc.code != "CH_ACCESS_TOKEN_INVALID" or not self.config.refresh_token:
                raise
            tokens = self._refresh_tokens()
            self.config = replace(self.config, access_token=tokens["access_token"],
                                  refresh_token=tokens.get("refresh_token", self.config.refresh_token))
            # The refreshed token is persisted, but _fetch cannot be re-entered here:
            # it drives the process-global Twisted reactor, and the first call already
            # stopped it. Twisted refuses a second run(), so retrying in this process
            # always failed with ReactorNotRestartable and the real auth error was
            # replaced by a transport one. Re-run the whole download in a fresh
            # interpreter instead; that child performs the merge and returns its
            # result, so this call ends there.
            return self._rerun_in_subprocess(start_ms, end_ms, page_size)
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
            "account_id": metadata["account_id"],
            "raw_archives": [str(path) for path in archive_paths],
            "processed_path": str(self.store.path),
        })
        return result

    def _refresh_tokens(self) -> dict[str, str]:
        from .oauth import CTraderOAuthError, persist_tokens_env, refresh_access_token
        try:
            tokens = refresh_access_token(self.config.client_id, self.config.client_secret, self.config.refresh_token)
        except CTraderOAuthError as exc:
            raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID", f"OAuth refresh failed: {exc}") from exc
        try:
            persist_tokens_env(tokens["access_token"], tokens.get("refresh_token"))
        except OSError as exc:
            raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID", f"could not persist refreshed tokens: {exc}") from exc
        return tokens

    def _rerun_in_subprocess(self, start_ms: int, end_ms: int, page_size: int) -> dict:
        """Re-run the whole download in a fresh interpreter and return its result.

        A second ``_fetch`` in this process cannot work: the first call stopped the
        global Twisted reactor, and ``reactor.run()`` raises ReactorNotRestartable
        afterwards. The child re-reads the now-persisted token from ``.env``,
        performs the read-only download and merges it into the same store, and
        reports the outcome through a small result file.

        This is not a blind retry of an uncertain broker action. The refresh has
        already succeeded and its token is durable, so the child is guaranteed a
        working credential, and the request is a read-only historical download.
        """
        workspace = Path(tempfile.mkdtemp(prefix="xauusd-refetch-"))
        result_path = workspace / "result.json"
        command = [sys.executable, "-m", "xauusd.cli", "data", "download",
                   "--start", str(start_ms), "--end", str(end_ms), "--page-size", str(page_size),
                   "--result-file", str(result_path)]
        try:
            completed = subprocess.run(command, capture_output=True, text=True,
                                       timeout=DOWNLOAD_TIMEOUT_SECONDS, cwd=str(REPO_ROOT))
        except (OSError, subprocess.SubprocessError) as exc:
            raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID",
                                   f"refresh succeeded but the retried download could not start: "
                                   f"{type(exc).__name__}") from exc
        finally:
            shutil.rmtree(workspace, ignore_errors=True)
        if not result_path.is_file():
            # Report the auth failure the child hit, not a generic transport error.
            # `state: failed` with a null error_code would hide a credential
            # problem from reports/data_update_status.json and the live view.
            raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID",
                                   "refreshed download produced no result")
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID",
                                   "refreshed download returned unreadable output") from exc
        result = payload.get("result") if isinstance(payload, dict) else None
        if not isinstance(result, dict):
            raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID", "refreshed download returned no result")
        return result

    def _fetch(self, start_ms: int, end_ms: int, page_size: int) -> tuple[list[dict], dict]:
        # Re-check the execution boundary at the network boundary, not only when
        # the config was read from the environment. The execution adapter does the
        # same immediately before every connect; without it a mutated config
        # object or a new caller bypasses both the demo host pin and the flag.
        self.config.validate()
        # Twisted's global reactor is intentionally isolated to one CLI invocation.
        from twisted.internet import reactor
        from ctrader_open_api import Client, Protobuf, TcpProtocol
        from ctrader_open_api.messages.OpenApiMessages_pb2 import (
            ProtoOAAccountAuthReq, ProtoOAApplicationAuthReq, ProtoOAGetAccountListByAccessTokenReq,
            ProtoOAGetTrendbarsReq, ProtoOASymbolByIdReq, ProtoOASymbolsListReq,
        )
        from ctrader_open_api.messages.OpenApiModelMessages_pb2 import ProtoOATrendbarPeriod
        from .ctrader_auth import demo_accounts, resolve_symbol

        client = Client(self.config.host, self.config.port, TcpProtocol)
        state: dict[str, Any] = {"pages": [], "cursor": end_ms, "discover": self.config.account_id is None}
        state.setdefault("account_id", self.config.account_id)

        def stop_error(failure):
            message = failure.getErrorMessage() if hasattr(failure, "getErrorMessage") else str(failure)
            state["error"] = RuntimeError(f"cTrader request failed: {message}")
            if reactor.running:
                reactor.stop()

        def auth_stop(code: str, description: str = "") -> None:
            state["error"] = CTraderAuthError(code, description)
            if reactor.running:
                reactor.stop()

        def request_page():
            request = ProtoOAGetTrendbarsReq(
                ctidTraderAccountId=state["account_id"], symbolId=state["symbol_id"],
                period=ProtoOATrendbarPeriod.Value(self.store.config.timeframe),
                fromTimestamp=start_ms, toTimestamp=state["cursor"], count=page_size,
            )
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(got_page, stop_error)

        def got_page(response):
            message = Protobuf.extract(response)
            error = _error_code(message)
            if error is not None:
                stop_error(RuntimeError(f"cTrader data error {error}")); return
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
            if _error_code(message) is not None:
                stop_error(RuntimeError(f"cTrader symbol error {_error_code(message)}")); return
            if not message.symbol:
                stop_error(Exception("cTrader returned no symbol details")); return
            state["digits"] = int(message.symbol[0].digits)
            request_page()

        def symbol_detail(symbol_id: int) -> None:
            request = ProtoOASymbolByIdReq(ctidTraderAccountId=state["account_id"], symbolId=[symbol_id])
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(got_symbol, stop_error)

        def got_symbols(response, index: int):
            message = Protobuf.extract(response)
            code = _error_code(message, detail=False)
            if code is not None:
                if state["discover"] and code != "CH_ACCESS_TOKEN_INVALID":
                    probe_account(index + 1); return
                description = getattr(message, "description", "") or ""
                auth_stop(code, description); return
            resolved = resolve_symbol(list(message.symbol), self.store.config.symbol)
            if resolved is None:
                if state["discover"]:
                    probe_account(index + 1); return
                available = [s.symbolName for s in message.symbol if "XAU" in (s.symbolName.upper() or "")]
                auth_stop("CH_CTID_TRADER_ACCOUNT_NOT_FOUND",
                          f"symbol {self.store.config.symbol!r} not found; XAU candidates: {available}")
                return
            symbol_id, symbol_name = resolved
            state.update(symbol_id=symbol_id, symbol_name=symbol_name)
            symbol_detail(symbol_id)

        def account_ok(response, index: int):
            message = Protobuf.extract(response)
            code = _error_code(message, detail=False)
            if code is not None:
                if state["discover"] and code != "CH_ACCESS_TOKEN_INVALID":
                    probe_account(index + 1); return
                description = getattr(message, "description", "") or ""
                auth_stop(code, description); return
            request = ProtoOASymbolsListReq(ctidTraderAccountId=state["account_id"], includeArchivedSymbols=False)
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(
                lambda response, i=index: got_symbols(response, i), stop_error)

        def probe_account(index: int) -> None:
            accounts = state["accounts"]
            if index >= len(accounts):
                auth_stop("CH_CTID_TRADER_ACCOUNT_NOT_FOUND", "no authorized demo account serves XAUUSD")
                return
            account = accounts[index]
            account_id = int(getattr(account, "ctidTraderAccountId"))
            state["account_id"] = account_id
            request = ProtoOAAccountAuthReq(ctidTraderAccountId=account_id, accessToken=self.config.access_token)
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(
                lambda response, i=index: account_ok(response, i), stop_error)

        def got_accounts(response):
            message = Protobuf.extract(response)
            code = _error_code(message, detail=False)
            if code is not None:
                description = getattr(message, "description", "") or ""
                auth_stop(code, description); return
            accounts = demo_accounts(list(message.ctidTraderAccount))
            if not accounts:
                auth_stop("CH_CTID_TRADER_ACCOUNT_NOT_FOUND", "no authorized demo account returned by discovery")
                return
            state["accounts"] = accounts
            probe_account(0)

        def account_or_discover() -> None:
            if self.config.account_id is not None:
                state.setdefault("account_id", self.config.account_id)
                request = ProtoOAAccountAuthReq(ctidTraderAccountId=self.config.account_id, accessToken=self.config.access_token)
                client.send(request, responseTimeoutInSeconds=30).addCallbacks(
                    lambda response: account_ok(response, 0), stop_error)
                return
            request = ProtoOAGetAccountListByAccessTokenReq(accessToken=self.config.access_token)
            client.send(request, responseTimeoutInSeconds=30).addCallbacks(got_accounts, stop_error)

        def app_ok(_):
            account_or_discover()

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
        metadata = {key: state[key] for key in ("symbol_id", "symbol_name", "digits", "account_id")}
        return state["pages"], metadata

    def _archive(self, pages: list[dict], metadata: dict, start_ms: int, end_ms: int) -> list[Path]:
        directory = self.store.config.raw_dir / "ctrader" / metadata["symbol_name"] / self.store.config.timeframe
        directory.mkdir(parents=True, exist_ok=True)
        paths = []
        for number, page in enumerate(pages, start=1):
            bars = page["trendbars"]
            payload = {
                "source": "ctrader-open-api", "account_id": metadata["account_id"],
                "symbol": metadata["symbol_name"], "symbol_id": metadata["symbol_id"],
                "digits": metadata["digits"], "timeframe": self.store.config.timeframe,
                "requested_from_ms": start_ms, "requested_to_ms": end_ms,
                "bars": [{field.name: getattr(bar, field.name) for field in bar.DESCRIPTOR.fields} for bar in bars],
            }
            first = min(int(bar.utcTimestampInMinutes) for bar in bars) if bars else 0
            last = max(int(bar.utcTimestampInMinutes) for bar in bars) if bars else 0
            path = directory / f"{first}_{last}_page{number:04d}.json"
            compressed = path.with_name(path.name + ".gz")
            if compressed.exists() and not path.exists():
                path = compressed
            elif not path.exists():
                atomic_write_bytes(path, json.dumps(payload, separators=(",", ":")).encode())
            paths.append(path)
        return paths
