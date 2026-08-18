from __future__ import annotations
import argparse,json,logging
from pathlib import Path
from dotenv import load_dotenv
from .core import synthetic_bars, features, Backtester
from .data import HistoricalDataStore, CTraderHistoricalAdapter, CTraderOpenApiConfig, CTraderOpenApiDownloader
from .engine import EventDrivenBacktester, ExecutionConfig
from .research import ResearchCampaign, StrategySpec
from .validation import StrategyValidator, ValidationConfig
from .ml import GradientBoostingResearch, MLConfig
from .ml_campaign import WalkForwardMLCampaign
from .automation import DailyResearchPipeline, automated_attempt, weekly_comparison
from .tournament_data import TournamentDataset
from .experiment_registry import ExperimentRegistry, from_strategy
from .search_space import catalog_size,seed_catalog
from .tournament_runner import ContinuousTournamentWorker, TournamentRunner
from .codex_workflow import CodexImprovementWorkflow
from .operations import OperationsManager
from .weekly_report import WeeklyTournamentReport
import subprocess
def campaign(synthetic: bool=False):
 Path("reports").mkdir(exist_ok=True); bars=synthetic_bars() if synthetic else None
 if bars is None: raise RuntimeError("Configure cTrader historical-data adapter before downloading live data")
 f=features(bars); results=[]
 for name, sig in [("mean_reversion",(-f.bb_z).clip(-1,1)),("momentum",f.momentum.clip(-1,1)),("breakout",(f.close>f.close.rolling(30).max().shift(1)).astype(int))]:
  m=Backtester().run(f,sig); m.update(strategy=name,stability_score=max(0,min(1,1+m["max_drawdown"]))); m["score"]=.35*m["sharpe"]+.25*m["profit_factor"]+.2*(1+m["max_drawdown"])+.2*m["stability_score"]; results.append(m)
 results.sort(key=lambda x:x["score"],reverse=True); Path("reports/leaderboard.json").write_text(json.dumps(results,indent=2)); print(json.dumps(results[:10],indent=2))

def event_backtest(strategy: str, start: str|None, end: str|None):
 bars=HistoricalDataStore().read()
 if start: bars=bars.loc[start:]
 if end: bars=bars.loc[:end]
 f=features(bars)
 if strategy=="momentum": signal=(f.momentum>0).astype(int)-(f.momentum<0).astype(int)
 elif strategy=="mean-reversion": signal=(f.bb_z < -1).astype(int)-(f.bb_z > 1).astype(int)
 else: raise ValueError(f"unknown strategy: {strategy}")
 result=EventDrivenBacktester(ExecutionConfig()).run(f,signal)
 directory=Path("reports")/"backtests"; directory.mkdir(parents=True,exist_ok=True)
 result["trades"].to_csv(directory/f"{strategy}_trades.csv",index=False)
 result["equity"].to_frame().to_parquet(directory/f"{strategy}_equity.parquet")
 summary={"strategy":strategy,"start":f.index.min().isoformat(),"end":f.index.max().isoformat(),**result["metrics"]}
 (directory/f"{strategy}_summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False))
 print(json.dumps(summary,indent=2,allow_nan=False))

def research_campaign(start: str|None, end: str|None):
 bars=HistoricalDataStore().read()
 if start: bars=bars.loc[start:]
 if end: bars=bars.loc[:end]
 leaderboard=ResearchCampaign().run(bars)
 print(json.dumps(leaderboard,indent=2,allow_nan=False))

def validate_strategy(strategy: str, start: str|None, end: str|None, bootstrap_samples: int):
 bars=HistoricalDataStore().read()
 if start: bars=bars.loc[start:]
 if end: bars=bars.loc[:end]
 defaults={
  "mean_reversion":StrategySpec("mean_reversion",{"entry_z":1.5,"exit_z":.25}),
  "momentum":StrategySpec("momentum",{"fast":8,"slow":34,"threshold_atr":.1}),
 }
 report=StrategyValidator(config=ValidationConfig(bootstrap_samples=bootstrap_samples)).validate(bars,defaults[strategy])
 summary={"strategy":strategy,"passed":report["passed"],"gates":report["gates"],
          "test":report["splits"]["test"],"positive_fold_fraction":report["positive_fold_fraction"],
          "stable_neighbor_fraction":report["stable_neighbor_fraction"],"bootstrap":report["bootstrap"]}
 print(json.dumps(summary,indent=2,allow_nan=False))

def ml_research(start: str|None, end: str|None, threshold: float):
 bars=HistoricalDataStore().read()
 if start: bars=bars.loc[start:]
 if end: bars=bars.loc[:end]
 report=GradientBoostingResearch(MLConfig(probability_threshold=threshold)).run(bars)
 print(json.dumps(report,indent=2,allow_nan=False))

def ml_walk_forward(start: str|None, end: str|None, threshold: float):
 bars=HistoricalDataStore().read()
 if start: bars=bars.loc[start:]
 if end: bars=bars.loc[:end]
 report=WalkForwardMLCampaign(MLConfig(probability_threshold=threshold)).run(bars)
 print(json.dumps(report,indent=2,allow_nan=False))

def daily_run():
 print(json.dumps(DailyResearchPipeline().run(),indent=2,allow_nan=False))

def main():
 load_dotenv(".env")
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd"); c=sub.add_parser("campaign"); c.add_argument("--synthetic",action="store_true")
 b=sub.add_parser("backtest"); b.add_argument("--strategy",choices=["momentum","mean-reversion"],default="momentum"); b.add_argument("--start"); b.add_argument("--end")
 r=sub.add_parser("research"); r.add_argument("--start"); r.add_argument("--end")
 vld=sub.add_parser("validate-strategy"); vld.add_argument("--strategy",choices=["mean_reversion","momentum"],default="mean_reversion"); vld.add_argument("--start"); vld.add_argument("--end"); vld.add_argument("--bootstrap-samples",type=int,default=500)
 ml=sub.add_parser("ml-research"); ml.add_argument("--start"); ml.add_argument("--end"); ml.add_argument("--threshold",type=float,default=.58)
 mlwf=sub.add_parser("ml-walk-forward"); mlwf.add_argument("--start"); mlwf.add_argument("--end"); mlwf.add_argument("--threshold",type=float,default=.58)
 sub.add_parser("daily-run"); sub.add_parser("weekly-report")
 sub.add_parser("automated-run")
 td=sub.add_parser("tournament-data"); td.add_argument("action",choices=["create","status","verify"]); td.add_argument("--partition",choices=["train","validation","test"])
 er=sub.add_parser("experiments"); er.add_argument("action",choices=["seed","seed-catalog","catalog","summary","list"]); er.add_argument("--status",choices=["queued","running","completed","failed","cancelled"]); er.add_argument("--limit",type=int,default=100)
 worker=sub.add_parser("tournament-worker"); worker.add_argument("--count",type=int,default=1); worker.add_argument("--continuous",action="store_true"); worker.add_argument("--idle-seconds",type=float,default=30)
 codex=sub.add_parser("codex-improve"); codex.add_argument("action",choices=["prepare","run","status"])
 ops=sub.add_parser("operations"); ops.add_argument("action",choices=["health","backup"])
 sub.add_parser("tournament-weekly-report")
 d=sub.add_parser("data"); ds=d.add_subparsers(dest="data_cmd"); i=ds.add_parser("import"); i.add_argument("csv"); v=ds.add_parser("validate")
 download=ds.add_parser("download"); download.add_argument("--start",required=True,help="UTC start date/time (for example 2026-08-01)"); download.add_argument("--end",help="UTC end date/time; defaults to now"); download.add_argument("--page-size",type=int,default=5000)
 update=ds.add_parser("update"); update.add_argument("--overlap-minutes",type=int,default=10)
 a=p.parse_args(); logging.basicConfig(level=logging.INFO)
 if a.cmd=="campaign": campaign(a.synthetic)
 if a.cmd=="backtest": event_backtest(a.strategy,a.start,a.end)
 if a.cmd=="research": research_campaign(a.start,a.end)
 if a.cmd=="validate-strategy": validate_strategy(a.strategy,a.start,a.end,a.bootstrap_samples)
 if a.cmd=="ml-research": ml_research(a.start,a.end,a.threshold)
 if a.cmd=="ml-walk-forward": ml_walk_forward(a.start,a.end,a.threshold)
 if a.cmd=="daily-run": daily_run()
 if a.cmd=="weekly-report": print(json.dumps(weekly_comparison(),indent=2,allow_nan=False))
 if a.cmd=="automated-run":
  attempt=automated_attempt(); print(json.dumps(attempt,indent=2,allow_nan=False))
  if attempt["status"]!="success": raise SystemExit(1)
 if a.cmd=="tournament-data":
  tournament=TournamentDataset()
  if a.action=="create": result=tournament.create()
  elif a.action=="verify": result=tournament.verify()
  else:
   result=tournament.active()
   if a.partition: result={"manifest":result,"partition":a.partition,"rows":len(tournament.read(a.partition))}
  print(json.dumps(result,indent=2,allow_nan=False,default=str))
 if a.cmd=="experiments":
  registry=ExperimentRegistry()
  if a.action=="seed":
   dataset=TournamentDataset().active()
   try: commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
   except Exception: commit=None
   created=[]; existing=[]
   for strategy in __import__('xauusd.research',fromlist=['DEFAULT_STRATEGIES']).DEFAULT_STRATEGIES:
    row,is_new=registry.register(from_strategy(strategy,dataset,commit))
    (created if is_new else existing).append(row["fingerprint"])
   result={"created":len(created),"existing":len(existing),"summary":registry.summary()}
  elif a.action=="seed-catalog":
   dataset=TournamentDataset().active()
   try: commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
   except Exception: commit=None
   result=seed_catalog(registry,dataset,commit,a.limit)
  elif a.action=="catalog": result={"catalog_size":catalog_size()}
  elif a.action=="summary": result=registry.summary()
  else: result=registry.list(a.status,a.limit)
  print(json.dumps(result,indent=2,allow_nan=False,default=str))
 if a.cmd=="tournament-worker":
  if a.continuous:
   if a.idle_seconds <= 0: p.error("--idle-seconds must be positive")
   ContinuousTournamentWorker(idle_seconds=a.idle_seconds).run_forever()
  else:
   if a.count < 1: p.error("--count must be positive")
   result=TournamentRunner().run(a.count)
   print(json.dumps({"processed":len(result),"experiments":result},indent=2,allow_nan=False,default=str))
 if a.cmd=="codex-improve":
  workflow=CodexImprovementWorkflow()
  if a.action=="status": result=__import__('xauusd.dashboard',fromlist=['read_json']).read_json(Path("reports/tournament/codex/latest.json"),{"status":"never_run"})
  elif a.action=="prepare": result=workflow.prepare(TournamentDataset().active())
  else: result=workflow.run(TournamentDataset().active())
  print(json.dumps(result,indent=2,default=str))
 if a.cmd=="operations":
  manager=OperationsManager(); result=manager.health() if a.action=="health" else manager.backup()
  print(json.dumps(result,indent=2,default=str))
 if a.cmd=="tournament-weekly-report": print(json.dumps(WeeklyTournamentReport().build(),indent=2,default=str))
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
