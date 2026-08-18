from __future__ import annotations
import argparse,json,logging
from pathlib import Path
from dotenv import load_dotenv
from .core import synthetic_bars, features, Backtester
from .data import HistoricalDataStore, CTraderHistoricalAdapter, CTraderOpenApiConfig, CTraderOpenApiDownloader
def campaign(synthetic: bool=False):
 Path("reports").mkdir(exist_ok=True); bars=synthetic_bars() if synthetic else None
 if bars is None: raise RuntimeError("Configure cTrader historical-data adapter before downloading live data")
 f=features(bars); results=[]
 for name, sig in [("mean_reversion",(-f.bb_z).clip(-1,1)),("momentum",f.momentum.clip(-1,1)),("breakout",(f.close>f.close.rolling(30).max().shift(1)).astype(int))]:
  m=Backtester().run(f,sig); m.update(strategy=name,stability_score=max(0,min(1,1+m["max_drawdown"]))); m["score"]=.35*m["sharpe"]+.25*m["profit_factor"]+.2*(1+m["max_drawdown"])+.2*m["stability_score"]; results.append(m)
 results.sort(key=lambda x:x["score"],reverse=True); Path("reports/leaderboard.json").write_text(json.dumps(results,indent=2)); print(json.dumps(results[:10],indent=2))
def main():
 load_dotenv(".env")
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd"); c=sub.add_parser("campaign"); c.add_argument("--synthetic",action="store_true"); d=sub.add_parser("data"); ds=d.add_subparsers(dest="data_cmd"); i=ds.add_parser("import"); i.add_argument("csv"); v=ds.add_parser("validate")
 download=ds.add_parser("download"); download.add_argument("--start",required=True,help="UTC start date/time (for example 2026-08-01)"); download.add_argument("--end",help="UTC end date/time; defaults to now"); download.add_argument("--page-size",type=int,default=5000)
 update=ds.add_parser("update"); update.add_argument("--overlap-minutes",type=int,default=10)
 a=p.parse_args(); logging.basicConfig(level=logging.INFO)
 if a.cmd=="campaign": campaign(a.synthetic)
 if a.cmd=="data":
  s=HistoricalDataStore()
  if a.data_cmd=="import": result=CTraderHistoricalAdapter(s).import_csv(Path(a.csv))
  elif a.data_cmd=="validate": result=s.validate(s.read())
  elif a.data_cmd=="download": result=CTraderOpenApiDownloader(CTraderOpenApiConfig.from_env(),s).download(a.start,a.end,a.page_size)
  elif a.data_cmd=="update":
   if not s.path.exists(): raise RuntimeError("no local data; run data download --start DATE first")
   start=s.read().index.max()-__import__('pandas').Timedelta(minutes=a.overlap_minutes)
   result=CTraderOpenApiDownloader(CTraderOpenApiConfig.from_env(),s).download(start)
  else: p.error("choose a data command")
  print(json.dumps(result,indent=2))
if __name__=="__main__": main()
