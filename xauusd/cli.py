from __future__ import annotations
import argparse,json,logging
from pathlib import Path
from .core import synthetic_bars, features, Backtester
def campaign(synthetic: bool=False):
 Path("reports").mkdir(exist_ok=True); bars=synthetic_bars() if synthetic else None
 if bars is None: raise RuntimeError("Configure cTrader historical-data adapter before downloading live data")
 f=features(bars); results=[]
 for name, sig in [("mean_reversion",(-f.bb_z).clip(-1,1)),("momentum",f.momentum.clip(-1,1)),("breakout",(f.close>f.close.rolling(30).max().shift(1)).astype(int))]:
  m=Backtester().run(f,sig); m.update(strategy=name,stability_score=max(0,min(1,1+m["max_drawdown"]))); m["score"]=.35*m["sharpe"]+.25*m["profit_factor"]+.2*(1+m["max_drawdown"])+.2*m["stability_score"]; results.append(m)
 results.sort(key=lambda x:x["score"],reverse=True); Path("reports/leaderboard.json").write_text(json.dumps(results,indent=2)); print(json.dumps(results[:10],indent=2))
def main():
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd"); c=sub.add_parser("campaign"); c.add_argument("--synthetic",action="store_true"); a=p.parse_args(); logging.basicConfig(level=logging.INFO)
 if a.cmd=="campaign": campaign(a.synthetic)
if __name__=="__main__": main()
