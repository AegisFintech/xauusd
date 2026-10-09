from types import SimpleNamespace

import errno
import json
import threading

import pandas as pd
import pytest

from xauusd.atomic import file_lock
from xauusd.data import (CTraderAuthError, CTraderOpenApiConfig, CTraderOpenApiDownloader,
                         DataConfig, HistoricalDataStore, StoreCorruptError,
                         classify_store_error, trendbars_to_frame)


def _bars(offset):
    """Three valid, non-overlapping minutes, shifted so writers never collide."""
    index = pd.date_range("2024-01-01", periods=3, freq="min", tz="UTC") + pd.Timedelta(minutes=10 * offset)
    return pd.DataFrame({"open": [1.0, 2.0, 3.0], "high": [2.0, 3.0, 4.0], "low": [0.0, 1.0, 2.0],
                         "close": [1.5, 2.5, 3.5], "volume": [1.0, 2.0, 3.0]}, index=index)


def _store(tmp_path):
    return HistoricalDataStore(DataConfig(processed_dir=tmp_path / "data" / "processed",
                                          raw_dir=tmp_path / "data" / "raw"))


def _raw_page(tmp_path, first_minute, count, low=120_000_000):
    """One archived page in the downloader's own format: low plus deltas, 1/100000."""
    directory = tmp_path / "data" / "raw" / "ctrader" / "XAUUSD" / "M1"
    directory.mkdir(parents=True, exist_ok=True)
    payload = {"source": "ctrader-open-api", "digits": 2, "symbol": "XAUUSD",
               "timeframe": "M1",
               "bars": [{"utcTimestampInMinutes": first_minute + step, "low": low + step,
                         "deltaOpen": 1000, "deltaHigh": 2000, "deltaClose": 1500,
                         "volume": 10} for step in range(count)]}
    path = directory / f"{first_minute}_{first_minute + count - 1}_page0001.json"
    path.write_text(json.dumps(payload))
    return path


def test_a_corrupt_store_is_reported_as_corrupt_not_as_a_bare_oserror(tmp_path):
    """`error_type: OSError` with `error_code: null` was undiagnosable.

    That is all the status file said for the rest of 2026-10-08, after two writers
    shared one temporary name and the parquet footer became undecodable. Telling a
    corrupt store from a network failure meant reproducing the failure by hand.
    """
    store = _store(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_bytes(b"not a parquet file")

    for call in (store.read, store.last_timestamp):
        with pytest.raises(StoreCorruptError) as info:
            call()
        assert info.value.code == "store_corrupt"
        assert classify_store_error(info.value) == "store_corrupt"
    # Still an OSError, so every handler that catches OSError keeps working.
    assert isinstance(StoreCorruptError(store.path), OSError)


def test_classify_store_error_names_a_full_disk_and_refuses_to_guess():
    assert classify_store_error(OSError(errno.ENOSPC, "No space left on device")) == "disk_full"
    # An unrecognised failure gets no code. An invented one is worse than none, and
    # message text is never persisted because it can carry a token inside a URL.
    assert classify_store_error(OSError("socket reset by peer")) is None
    assert classify_store_error(ValueError("nope")) is None


def test_rebuild_from_raw_reproduces_the_store_without_the_broker(tmp_path):
    """Recovery has to work with the store unreadable and the market open.

    That was the 2026-10-09 situation: 2.4M bars unreadable, 15 hours of an open
    session already lost, and no supported way back.
    """
    first = 2_800_000
    _raw_page(tmp_path, first, 5)
    _raw_page(tmp_path, first + 3, 5)   # overlapping, exactly as real re-downloads are
    store = _store(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_bytes(b"corrupt footer")

    summary = store.rebuild_from_raw(cutoff=pd.Timestamp(first, unit="m", tz="UTC"))

    assert summary["rows"] == 8          # 5 + 5, with the 2 overlapping minutes deduped
    assert summary["duplicates"] == 0
    rebuilt = store.read()
    assert rebuilt.index.min() == pd.Timestamp(first, unit="m", tz="UTC")
    assert rebuilt.index.max() == pd.Timestamp(first + 7, unit="m", tz="UTC")
    # Decoded through the same path as a live download, so low-plus-delta is right.
    assert float(rebuilt["low"].iloc[0]) == pytest.approx(1200.0)
    assert float(rebuilt["open"].iloc[0]) == pytest.approx(1200.01)


def test_rebuild_refuses_to_guess_the_range_of_an_unreadable_store(tmp_path):
    """The archive reaches back years before the store did.

    Rebuilding from all of it would grow the store backwards, change the dataset
    version, and risk consuming a protected holdout twice -- so an unreadable store
    has to be told what range it held.
    """
    _raw_page(tmp_path, 2_800_000, 5)
    store = _store(tmp_path)
    store.path.parent.mkdir(parents=True, exist_ok=True)
    store.path.write_bytes(b"corrupt footer")

    with pytest.raises(ValueError, match="cutoff"):
        store.rebuild_from_raw()


def test_rebuild_bounds_the_store_to_the_cutoff(tmp_path):
    early = 2_000_000
    _raw_page(tmp_path, early, 5)
    _raw_page(tmp_path, early + 1000, 5)
    store = _store(tmp_path)

    summary = store.rebuild_from_raw(cutoff=pd.Timestamp(early + 1000, unit="m", tz="UTC"))

    assert summary["rows"] == 5
    assert store.read().index.min() == pd.Timestamp(early + 1000, unit="m", tz="UTC")


def test_rebuild_from_raw_needs_an_archive(tmp_path):
    store = _store(tmp_path)

    with pytest.raises(FileNotFoundError, match="no raw page archive"):
        store.rebuild_from_raw(cutoff="2020-01-01")


def test_the_rebuild_command_is_in_the_cli_grammar():
    from xauusd.cli import build_parser

    parsed = build_parser().parse_args(["data", "rebuild", "--cutoff", "2019-12-01",
                                        "--chunk-pages", "50"])

    assert (parsed.data_cmd, parsed.cutoff, parsed.chunk_pages) == ("rebuild", "2019-12-01", 50)


def test_raw_retention_plan_names_the_redundancy_and_preserves_the_range(tmp_path):
    """The archive is the only rebuild path, so a plan must prove it loses no range.

    `_archive` skips a page only when that exact filename exists, so overlapping
    re-downloads accumulate: the live archive holds 6,806 pages for 2.4M unique
    minutes. Reporting the redundancy is useful; silently deleting it is not.
    """
    _raw_page(tmp_path, 0, 10)     # 0-9
    _raw_page(tmp_path, 3, 10)     # 3-12, fully covered by 0-9 plus 5-20
    _raw_page(tmp_path, 5, 16)     # 5-20, extends the run furthest
    _raw_page(tmp_path, 30, 10)    # 30-39, after a gap
    store = _store(tmp_path)

    plan = store.raw_retention_plan()

    assert (plan["pages"], plan["cover_pages"], plan["redundant_pages"]) == (4, 3, 1)
    assert plan["cover_preserves_the_full_range"] is True
    assert plan["archive_range_minutes"] == plan["cover_range_minutes"] == [0, 39]
    assert plan["gaps_in_archive"] == 1
    assert plan["redundant_bytes"] > 0
    assert plan["deletes"].startswith("nothing")


def test_raw_retention_plan_deletes_nothing(tmp_path):
    for minute in (0, 3, 5, 30):
        _raw_page(tmp_path, minute, 10)
    store = _store(tmp_path)
    before = sorted(path.name for path in store.raw_archive_dir.glob("*.json"))

    store.raw_retention_plan()

    assert sorted(path.name for path in store.raw_archive_dir.glob("*.json")) == before
    assert len(before) == 4


def test_raw_retention_plan_on_an_empty_archive(tmp_path):
    plan = _store(tmp_path).raw_retention_plan()

    assert plan["pages"] == 0
    assert plan["redundant_pages"] == 0


def test_the_raw_retention_command_is_in_the_cli_grammar():
    from xauusd.cli import build_parser

    assert build_parser().parse_args(["data", "raw-retention"]).data_cmd == "raw-retention"


def test_write_never_reuses_one_temporary_name(tmp_path, monkeypatch):
    """A shared temporary name lets two writers interleave into one inode.

    That is how the store was destroyed on 2026-10-08: the data-update timer and
    the feed both wrote `XAUUSD_M1.parquet.tmp`, and the file that landed had an
    undecodable thrift footer, so 2,391,574 bars became unreadable.
    """
    store = _store(tmp_path)
    seen = []
    real = pd.DataFrame.to_parquet

    def spy(frame, destination, *args, **kwargs):
        seen.append(destination)
        return real(frame, destination, *args, **kwargs)

    monkeypatch.setattr(pd.DataFrame, "to_parquet", spy)
    store.write(_bars(0), merge=False)
    store.write(_bars(1), merge=False)

    assert len(seen) == 2
    assert not any(str(item).endswith("XAUUSD_M1.parquet.tmp") for item in seen), seen
    assert seen[0] is not seen[1]


def test_write_waits_for_the_store_lock_and_fails_loudly(tmp_path, monkeypatch):
    """Read-merge-swap has to be exclusive, and a wedged writer must not be skipped.

    An atomic swap alone still lets two writers merge the same stale frame and
    lose one of their updates, which for the feed means silently dropped bars.
    """
    monkeypatch.setattr("xauusd.data.STORE_LOCK_TIMEOUT_SECONDS", 0.2)
    store = _store(tmp_path)

    with file_lock(store.path, timeout=5):
        with pytest.raises(TimeoutError, match="write lock"):
            store.write(_bars(0), merge=False)


def test_concurrent_writers_leave_a_readable_complete_store(tmp_path):
    """The invariant the corruption broke: every writer's bars survive, and it reads."""
    store = _store(tmp_path)
    store.write(_bars(0), merge=False)
    errors = []

    def append(offset):
        try:
            store.write(_bars(offset), merge=True)
        except BaseException as exc:
            errors.append(exc)

    threads = [threading.Thread(target=append, args=(offset,)) for offset in range(1, 6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    result = store.validate(store.read())
    assert result["rows"] == 18
    assert result["duplicates"] == 0


def test_last_timestamp_agrees_with_a_full_read(tmp_path):
    store = _store(tmp_path)
    store.write(_bars(0), merge=False)
    store.write(_bars(3), merge=True)

    assert store.last_timestamp() == store.read().index.max()


def test_last_timestamp_reads_the_index_column_only(tmp_path, monkeypatch):
    """One value must not cost the whole frame.

    `data update` runs four times a day on a timer and needs only the newest bar to
    decide where to resume downloading. Reading all six columns of 2.4M rows for that
    costs ~134 MB on a host with ~1.4 GB available; the index column alone is ~20 MB.
    """
    store = _store(tmp_path)
    store.write(_bars(0), merge=False)
    calls = []
    real = pd.read_parquet

    def spy(path, *args, **kwargs):
        calls.append(kwargs.get("columns", "unset"))
        return real(path, *args, **kwargs)

    monkeypatch.setattr(pd, "read_parquet", spy)

    assert store.last_timestamp() == _bars(0).index.max()
    assert calls == [[]], calls


def test_last_timestamp_raises_for_a_missing_store(tmp_path):
    """Silently returning None would make `data update` download from the epoch."""
    store = _store(tmp_path)

    with pytest.raises(FileNotFoundError):
        store.last_timestamp()


def test_store_roundtrip(tmp_path):
 idx=pd.date_range("2024-01-01",periods=3,freq="min",tz="UTC"); b=pd.DataFrame({"open":[1,2,3],"high":[2,3,4],"low":[0,1,2],"close":[1.5,2.5,3.5],"volume":[1,2,3]},index=idx)
 s=HistoricalDataStore(); object.__setattr__(s.config,"processed_dir",tmp_path)
 s.write(b); assert s.validate(s.read())["absent_minutes"]==0


def test_trendbar_delta_decoding():
 bar=SimpleNamespace(low=200012345,deltaOpen=10,deltaHigh=40,deltaClose=20,volume=7,utcTimestampInMinutes=28_000_000)
 frame=trendbars_to_frame([bar],digits=5)
 assert frame.iloc[0].to_dict()=={"open":2000.12355,"high":2000.12385,"low":2000.12345,"close":2000.12365,"volume":7.0}
 assert str(frame.index.tz)=="UTC"


def test_store_rejects_invalid_ohlc():
 index=pd.date_range("2024-01-01",periods=1,freq="min",tz="UTC")
 bars=pd.DataFrame({"open":[2],"high":[1],"low":[0],"close":[1],"volume":[1]},index=index)
 with pytest.raises(ValueError,match="invalid OHLCV"):
  HistoricalDataStore().normalize(bars)


def demo_env(monkeypatch):
 monkeypatch.setenv("CTRADER_CLIENT_ID","c"); monkeypatch.setenv("CTRADER_CLIENT_SECRET","s")
 monkeypatch.setenv("CTRADER_ACCESS_TOKEN","at"); monkeypatch.setenv("CTRADER_DEMO_ONLY","true")
 monkeypatch.delenv("CTRADER_CTID_TRADER_ACCOUNT_ID",raising=False)
 monkeypatch.delenv("CTRADER_OPEN_API_HOST",raising=False)
 monkeypatch.delenv("CTRADER_REFRESH_TOKEN",raising=False)


def test_data_config_from_env_account_optionally_discovered(monkeypatch):
 demo_env(monkeypatch)
 config=CTraderOpenApiConfig.from_env()
 assert config.account_id is None
 monkeypatch.setenv("CTRADER_CTID_TRADER_ACCOUNT_ID","10098695")
 assert CTraderOpenApiConfig.from_env().account_id==10098695


def test_data_config_requires_demo_only_flag(monkeypatch):
 monkeypatch.setenv("CTRADER_CLIENT_ID","c"); monkeypatch.setenv("CTRADER_CLIENT_SECRET","s")
 monkeypatch.setenv("CTRADER_ACCESS_TOKEN","at"); monkeypatch.delenv("CTRADER_DEMO_ONLY",raising=False)
 with pytest.raises(RuntimeError,match="CTRADER_DEMO_ONLY=true"):
  CTraderOpenApiConfig.from_env()


def test_data_config_rejects_non_demo_host(monkeypatch):
 demo_env(monkeypatch); monkeypatch.setenv("CTRADER_OPEN_API_HOST","live.ctraderapi.com")
 with pytest.raises(RuntimeError,match="restricted"):
  CTraderOpenApiConfig.from_env()


def test_download_revalidates_the_execution_boundary_at_the_network_call(monkeypatch,tmp_path):
 """validate() is no longer a one-time check performed only by from_env().

 The execution adapter re-checks the demo host and flag immediately before every
 connect. The downloader did not, so a mutated config object or a new caller
 could reach a non-demo host with the flag unset. These tests previously passed
 with no flag in the environment at all, which is the hole.
 """
 store=HistoricalDataStore(DataConfig(processed_dir=tmp_path,raw_dir=tmp_path/"raw"))
 downloader=CTraderOpenApiDownloader(downloader_config(access_token="at"),store)
 monkeypatch.setenv("CTRADER_DEMO_ONLY","true")
 reached={"n":0}
 def counting_fetch(start_ms,end_ms,page_size):
  reached["n"]+=1
  return [],{"symbol_name":"XAUUSD","symbol_id":2,"digits":5,"account_id":42}
 monkeypatch.setattr(downloader,"_fetch",counting_fetch)
 monkeypatch.setattr(downloader,"_archive",lambda pages,metadata,start_ms,end_ms: [])
 assert downloader.download("2026-09-01","2026-09-02")["downloaded_rows"]==0
 assert reached["n"]==1

 monkeypatch.delenv("CTRADER_DEMO_ONLY",raising=False)
 with pytest.raises(RuntimeError,match="CTRADER_DEMO_ONLY=true"):
  downloader.download("2026-09-01","2026-09-02")

 monkeypatch.setenv("CTRADER_DEMO_ONLY","true")
 object.__setattr__(downloader.config,"host","live.ctraderapi.com")
 with pytest.raises(RuntimeError,match="restricted"):
  downloader.download("2026-09-01","2026-09-02")
 # Neither refusal reached the network boundary.
 assert reached["n"]==1


def downloader_config(access_token="at",refresh_token=None,account_id=None):
 return CTraderOpenApiConfig(client_id="c",client_secret="s",access_token=access_token,
                             refresh_token=refresh_token,account_id=account_id)


def minute_60(ts):
 return int(pd.Timestamp(ts,tz="UTC").timestamp()//60)


def one_bar_at(ts):
 return SimpleNamespace(low=200012345,deltaOpen=10,deltaHigh=40,deltaClose=20,volume=7,
                        utcTimestampInMinutes=minute_60(ts))


def test_download_refreshes_once_then_retries_in_a_fresh_process(monkeypatch,tmp_path):
 demo_env(monkeypatch)
 """The post-refresh retry cannot run in-process, and must not try.

 ``_fetch`` drives Twisted's process-global reactor and stops it. A second call
 in the same process raises ReactorNotRestartable, so retrying in place always
 failed and the real auth error was replaced by a transport one, which
 reports/data_update_status.json then classified as `failed` with no error_code.
 The retry therefore re-runs the whole download in a fresh interpreter.
 """
 store=HistoricalDataStore(DataConfig(processed_dir=tmp_path,raw_dir=tmp_path/"raw"))
 downloader=CTraderOpenApiDownloader(downloader_config(access_token="old",refresh_token="rt"),store)
 metadata={"symbol_name":"XAUUSD","symbol_id":2,"digits":5,"account_id":42}
 calls={"n":0}
 def fake_fetch(start_ms,end_ms,page_size):
  calls["n"]+=1
  assert downloader.config.access_token=="old", "the first attempt must use the stale token"
  raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID","Invalid access token")
 monkeypatch.setattr(downloader,"_fetch",fake_fetch)
 monkeypatch.setattr(downloader,"_refresh_tokens",
                     lambda: {"access_token":"fresh","refresh_token":"newrt"})
 reruns={"n":0}
 def fake_subprocess(start_ms,end_ms,page_size):
  reruns["n"]+=1
  assert downloader.config.access_token=="fresh", "the retry must use the refreshed token"
  return {"account_id":42,"downloaded_rows":1,"reran":True}
 monkeypatch.setattr(downloader,"_rerun_in_subprocess",fake_subprocess)
 monkeypatch.setattr(downloader,"_archive",lambda pages,metadata,start_ms,end_ms: [])

 result=downloader.download("2026-09-01","2026-09-02")

 # Exactly one in-process fetch, and exactly one fresh-process retry.
 assert calls["n"]==1
 assert reruns["n"]==1
 assert downloader.config.access_token=="fresh"
 assert downloader.config.refresh_token=="newrt"
 assert result=={"account_id":42,"downloaded_rows":1,"reran":True}


def test_download_does_not_retry_without_a_refresh_token(monkeypatch,tmp_path):
 demo_env(monkeypatch)
 store=HistoricalDataStore(DataConfig(processed_dir=tmp_path,raw_dir=tmp_path/"raw"))
 downloader=CTraderOpenApiDownloader(downloader_config(access_token="old",refresh_token=None),store)
 monkeypatch.setattr(downloader,"_fetch",
                     lambda *a: (_ for _ in ()).throw(CTraderAuthError("CH_ACCESS_TOKEN_INVALID","nope")))
 with pytest.raises(CTraderAuthError):
  downloader.download("2026-09-01","2026-09-02")


def test_download_does_not_retry_non_token_auth_error(monkeypatch,tmp_path):
 demo_env(monkeypatch)
 store=HistoricalDataStore(DataConfig(processed_dir=tmp_path,raw_dir=tmp_path/"raw"))
 downloader=CTraderOpenApiDownloader(downloader_config(access_token="old",refresh_token="rt"),store)
 calls={"n":0}
 def fake_fetch(start_ms,end_ms,page_size):
  calls["n"]+=1
  raise CTraderAuthError("CH_CTID_TRADER_ACCOUNT_NOT_FOUND","nope")
 monkeypatch.setattr(downloader,"_fetch",fake_fetch)
 with pytest.raises(CTraderAuthError,match="CH_CTID_TRADER_ACCOUNT_NOT_FOUND"):
  downloader.download("2026-09-01","2026-09-02")
 assert calls["n"]==1
 assert downloader.config.access_token=="old"


def test_download_without_refresh_token_raises_instead_of_retrying(monkeypatch,tmp_path):
 demo_env(monkeypatch)
 store=HistoricalDataStore(DataConfig(processed_dir=tmp_path,raw_dir=tmp_path/"raw"))
 downloader=CTraderOpenApiDownloader(downloader_config(access_token="old"),store)
 calls={"n":0}
 def fake_fetch(start_ms,end_ms,page_size):
  calls["n"]+=1
  raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID","Invalid access token")
 monkeypatch.setattr(downloader,"_fetch",fake_fetch)
 with pytest.raises(CTraderAuthError):
  downloader.download("2026-09-01","2026-09-02")
 assert calls["n"]==1


def frame(periods=200):
    idx = pd.date_range("2024-01-01", periods=periods, freq="min", tz="UTC")
    return pd.DataFrame({"open": range(periods), "high": range(periods), "low": range(periods),
                         "close": range(periods), "volume": range(periods)}, index=idx)


def test_positions_matches_get_indexer():
    store = HistoricalDataStore()
    bars = frame()
    required = pd.date_range("2024-01-01 00:00:20", "2024-01-01 00:04:00", freq="10s", tz="UTC")
    assert list(store.positions(bars, required)) == list(bars.index.get_indexer(required))
    # A gap and a bar outside the frame are missing, exactly as get_indexer reports.
    missing = pd.DatetimeIndex(["2023-12-31 23:59:00", "2024-01-01 00:00:30",
                                "2024-01-01 00:00:45", "2024-01-01 00:00:00", "2024-01-01 09:00:00"], tz="UTC")
    assert list(store.positions(bars, missing)) == [-1, -1, -1, 0, -1]
    assert list(store.positions(bars, bars.index)) == list(range(len(bars)))
    assert list(store.positions(bars, pd.DatetimeIndex([], tz="UTC"))) == []


def test_positions_requires_a_sorted_unique_index():
    store = HistoricalDataStore()
    bars = frame(5)
    with pytest.raises(ValueError, match="sorted"):
        store.positions(bars.iloc[::-1], pd.DatetimeIndex(["2024-01-01"], tz="UTC"))
    with pytest.raises(ValueError, match="unique"):
        store.positions(bars.iloc[[0, 1, 2, 2, 3, 4]], pd.DatetimeIndex(["2024-01-01"], tz="UTC"))


def test_positions_resolves_an_anchor_sweep_in_one_pass(monkeypatch):
    # A per-anchor get_indexer loop over an M1 frame builds a hash table per call and
    # overran the 1200s shell ceiling twice, tripping a recovery stop each time. A
    # whole anchor sweep must resolve in a fixed number of passes, so the cost cannot
    # grow with the number of anchors the way the timed-out job's did.
    store = HistoricalDataStore()
    bars = frame(200_000)
    calls = []
    original = pd.DatetimeIndex.searchsorted

    def counted(self, values, *args, **kwargs):
        calls.append(len(values))
        return original(self, values, *args, **kwargs)

    monkeypatch.setattr(pd.DatetimeIndex, "searchsorted", counted)
    for anchors in (2, 50, 500):
        calls.clear()
        batch = pd.date_range(bars.index[0], periods=anchors * 60, freq="min", tz="UTC")
        positions = store.positions(bars, batch)
        assert (positions >= 0).all() and len(positions) == anchors * 60
        # Two passes over the batch regardless of how many anchors it covers.
        assert len(calls) == 2 and sum(calls) == 2 * len(batch)
