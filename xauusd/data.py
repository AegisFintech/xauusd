from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import logging
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
        x=bars.copy(); x.index=pd.to_datetime(x.index, utc=True); x.index.name="timestamp"; x=x.sort_index()
        missing=[c for c in REQUIRED if c not in x.columns]
        if missing: raise ValueError(f"missing columns: {missing}")
        x=x[list(REQUIRED)].apply(pd.to_numeric, errors="coerce").dropna(); x=x[~x.index.duplicated(keep="last")]
        if (x[["high","low"]].min(axis=1)>x["high"]).any(): raise ValueError("invalid OHLC")
        if (x.low>x.high).any() or (x.open> x.high).any() or (x.open<x.low).any() or (x.close>x.high).any() or (x.close<x.low).any() or (x.volume<0).any(): raise ValueError("invalid OHLCV values")
        return x
    def validate(self, bars: pd.DataFrame) -> dict:
        x=self.normalize(bars); expected=pd.date_range(x.index.min(),x.index.max(),freq="min",tz="UTC"); gaps=expected.difference(x.index)
        return {"rows":len(x),"start":x.index.min().isoformat(),"end":x.index.max().isoformat(),"missing_bars":int(len(gaps)),"gaps":[t.isoformat() for t in gaps[:100]],"duplicates":int(bars.index.duplicated().sum())}
    def write(self, bars: pd.DataFrame, merge=True) -> pd.DataFrame:
        self.config.processed_dir.mkdir(parents=True,exist_ok=True); x=self.normalize(bars)
        if merge and self.path.exists(): x=pd.concat([pd.read_parquet(self.path),x]).sort_index(); x=x[~x.index.duplicated(keep="last")]
        x.to_parquet(self.path, engine="pyarrow"); return x
    def read(self) -> pd.DataFrame:
        if not self.path.exists(): raise FileNotFoundError(self.path)
        return pd.read_parquet(self.path)

class CTraderHistoricalAdapter:
    """Import a cTrader historical CSV export; deliberately has no trading API methods."""
    def __init__(self, store: HistoricalDataStore): self.store=store
    def import_csv(self, source: Path, merge=True) -> dict:
        df=pd.read_csv(source); time_col=next((c for c in df.columns if c.lower() in {"timestamp","time","date"}),None)
        if not time_col: raise ValueError("CSV needs timestamp/time/date column")
        df.index=pd.to_datetime(df.pop(time_col), utc=True); return self.store.validate(self.store.write(df,merge=merge))
