from types import SimpleNamespace

import pandas as pd
import pytest

from xauusd.data import HistoricalDataStore, trendbars_to_frame
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
