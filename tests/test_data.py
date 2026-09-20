from types import SimpleNamespace

import pandas as pd
import pytest

from xauusd.data import CTraderAuthError, CTraderOpenApiConfig, CTraderOpenApiDownloader, DataConfig, HistoricalDataStore, trendbars_to_frame
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


def downloader_config(access_token="at",refresh_token=None,account_id=None):
 return CTraderOpenApiConfig(client_id="c",client_secret="s",access_token=access_token,
                             refresh_token=refresh_token,account_id=account_id)


def minute_60(ts):
 return int(pd.Timestamp(ts,tz="UTC").timestamp()//60)


def one_bar_at(ts):
 return SimpleNamespace(low=200012345,deltaOpen=10,deltaHigh=40,deltaClose=20,volume=7,
                        utcTimestampInMinutes=minute_60(ts))


def test_download_retries_once_on_invalid_token(monkeypatch,tmp_path):
 store=HistoricalDataStore(DataConfig(processed_dir=tmp_path,raw_dir=tmp_path/"raw"))
 downloader=CTraderOpenApiDownloader(downloader_config(access_token="old",refresh_token="rt"),store)
 metadata={"symbol_name":"XAUUSD","symbol_id":2,"digits":5,"account_id":42}
 calls={"n":0}
 def fake_fetch(start_ms,end_ms,page_size):
  calls["n"]+=1
  if calls["n"]==1:
   assert downloader.config.access_token=="old"
   raise CTraderAuthError("CH_ACCESS_TOKEN_INVALID","Invalid access token")
  assert downloader.config.access_token=="fresh"
  return [{"trendbars":[one_bar_at("2026-09-01 00:05")]}],metadata
 monkeypatch.setattr(downloader,"_fetch",fake_fetch)
 monkeypatch.setattr(downloader,"_refresh_tokens",
                     lambda: {"access_token":"fresh","refresh_token":"newrt"})
 monkeypatch.setattr(downloader,"_archive",lambda pages,metadata,start_ms,end_ms: [])
 result=downloader.download("2026-09-01","2026-09-02")
 assert calls["n"]==2
 assert downloader.config.access_token=="fresh"
 assert downloader.config.refresh_token=="newrt"
 assert result["account_id"]==42
 assert result["downloaded_rows"]==1


def test_download_does_not_retry_non_token_auth_error(monkeypatch,tmp_path):
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
