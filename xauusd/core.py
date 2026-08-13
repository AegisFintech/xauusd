from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, logging, math
import numpy as np, pandas as pd

log = logging.getLogger(__name__)
@dataclass
class BacktestConfig:
    initial_cash: float = 100_000.0; spread: float = 0.20; commission: float = 3.5; slippage: float = 0.03; latency_seconds: int = 1

def features(df: pd.DataFrame) -> pd.DataFrame:
    x=df.copy(); close=x["close"].astype(float); ret=close.pct_change()
    x["return"]=ret; x["log_return"]=np.log(close).diff(); x["momentum"]=close.pct_change(10)
    x["atr"]=((x.high-x.low).rolling(14).mean()); delta=close.diff(); up=delta.clip(lower=0).rolling(14).mean(); dn=(-delta.clip(upper=0)).rolling(14).mean(); x["rsi"]=100-100/(1+up/dn.replace(0,np.nan))
    mid=close.rolling(20).mean(); sd=close.rolling(20).std(); x["bb_z"]=(close-mid)/(sd+1e-12); x["range_expansion"]=(x.high-x.low)/(x.high-x.low).rolling(20).mean(); return x.dropna()

class Backtester:
    def __init__(self, config: BacktestConfig|None=None): self.c=config or BacktestConfig()
    def run(self, bars: pd.DataFrame, signal: pd.Series) -> dict:
        b=bars.loc[signal.index].copy(); pos=signal.fillna(0).clip(-1,1); r=b.close.pct_change().fillna(0)*pos.shift(1).fillna(0)
        costs=(pos.diff().abs().fillna(0))*(self.c.spread/float(b.close.mean())+self.c.slippage/float(b.close.mean()))+pos.diff().abs().fillna(0)*self.c.commission/self.c.initial_cash
        pnl=r-costs; equity=self.c.initial_cash*(1+pnl).cumprod(); dd=equity/equity.cummax()-1; trades=pos.diff().abs().gt(0).sum(); sharpe=float(np.sqrt(252*1440)*pnl.mean()/(pnl.std()+1e-12)); pf=float(pnl[pnl>0].sum()/(-pnl[pnl<0].sum()+1e-12))
        return {"cagr":float((equity.iloc[-1]/self.c.initial_cash)**(365/max((b.index[-1]-b.index[0]).days,1))-1),"sharpe":sharpe,"sortino":float(np.sqrt(252*1440)*pnl.mean()/(pnl[pnl<0].std()+1e-12)),"profit_factor":pf,"win_rate":float((pnl>0).mean()),"max_drawdown":float(dd.min()),"trades":int(trades),"expectancy":float(pnl.mean()),"exposure":float((pos!=0).mean()),"equity":equity.tolist()}

def synthetic_bars(n=20000, seed=7):
    rng=np.random.default_rng(seed); idx=pd.date_range(end=pd.Timestamp.utcnow(), periods=n, freq="min"); close=2000+np.cumsum(rng.normal(0,1,n)); return pd.DataFrame({"open":close-rng.random(n),"high":close+rng.random(n),"low":close-rng.random(n),"close":close,"volume":rng.integers(10,1000,n)},index=idx)
