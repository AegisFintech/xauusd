import pandas as pd
from xauusd.data import HistoricalDataStore
def test_store_roundtrip(tmp_path):
 idx=pd.date_range("2024-01-01",periods=3,freq="min",tz="UTC"); b=pd.DataFrame({"open":[1,2,3],"high":[2,3,4],"low":[0,1,2],"close":[1.5,2.5,3.5],"volume":[1,2,3]},index=idx)
 s=HistoricalDataStore(); object.__setattr__(s.config,"processed_dir",tmp_path)
 s.write(b); assert s.validate(s.read())["missing_bars"]==0
