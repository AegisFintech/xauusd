from __future__ import annotations
import argparse,json,logging,os,time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
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
from .distributed_compute import RemoteComputeBridge,compute_job
from .codex_workflow import CodexImprovementWorkflow
from .operations import OperationsManager
from .weekly_report import WeeklyTournamentReport
from .shadow_trading import ShadowTradingReadiness
from .adaptive_search import AdaptiveSearch
from .canary_strategy import ConfirmedBreakoutCanarySource, LocalHistoricalMarketDataSource
from .ctrader_demo import (CTraderDemoAdapter, CTraderDemoOpenApiConfig,
                           CTraderDemoOpenApiTransport, CockroachCTraderDemoStore)
from .demo_execution import CTraderVolumeConversion, CTraderVolumePolicy, PaperToCTraderDemoCoordinator
from .demo_runner import DemoAutomationRunner, DemoRunnerConfig
from .paper_trading import CockroachPaperTradingStore, PaperRiskConfig, PaperTrading, paper_from_env
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

def _positive_env_float(name: str, default: float) -> float:
 value=float(os.getenv(name,str(default)))
 if value <= 0: raise ValueError(f"{name} must be positive")
 return value

def _paper_risk_config_from_env() -> PaperRiskConfig:
 return PaperRiskConfig.from_env()

def _demo_automation_status(config: DemoRunnerConfig) -> dict:
 return {"state":"disabled" if not config.enabled else "not_started","enabled":config.enabled,
         "paper_only":os.getenv("CTRADER_PAPER_ONLY")=="true",
         "status_path":str(config.status_path)}

def _paper_from_env() -> PaperTrading:
 return paper_from_env()

def _paper_to_demo_coordinator(paper: PaperTrading) -> PaperToCTraderDemoCoordinator:
 if os.getenv("CTRADER_PAPER_ONLY")=="true":
  # Broker-free stage: exercise the deterministic paper pipeline without credentials or volumes.
  return PaperToCTraderDemoCoordinator(paper,paper_only=True)
 volume_text=os.getenv("CTRADER_VOLUME_PER_PAPER_UNIT")
 if volume_text is None: raise ValueError("CTRADER_VOLUME_PER_PAPER_UNIT is required")
 volume=CTraderVolumeConversion(int(volume_text)); volume.validate()
 api_config=CTraderDemoOpenApiConfig.from_env()
 transport=CTraderDemoOpenApiTransport(api_config)
 adapter=CTraderDemoAdapter(transport.discover(),CockroachCTraderDemoStore(),transport,api_config.timeout_seconds)
 volume_policy=CTraderVolumePolicy.from_metadata(transport.symbol_metadata())
 return PaperToCTraderDemoCoordinator(paper,adapter,volume,volume_policy)

def _demo_automation_runner(config: DemoRunnerConfig) -> DemoAutomationRunner:
 paper_only=os.getenv("CTRADER_PAPER_ONLY")=="true"
 quantity=_positive_env_float("CTRADER_CANARY_PAPER_QUANTITY",1)
 if not paper_only and os.getenv("CTRADER_VOLUME_PER_PAPER_UNIT") is None:
  raise ValueError("CTRADER_VOLUME_PER_PAPER_UNIT is required")
 market_store=HistoricalDataStore()
 paper=_paper_from_env()
 coordinator=_paper_to_demo_coordinator(paper)
 return DemoAutomationRunner(coordinator,LocalHistoricalMarketDataSource(market_store),
                             ConfirmedBreakoutCanarySource(market_store,quantity),config)

def demo_automation(action: str) -> dict:
 """Run the explicitly enabled local-data paper-to-demo canary."""
 config=DemoRunnerConfig.from_env()
 # Status and disabled actions remain local: do not open a database or broker connection.
 if action=="status" or not config.enabled: return _demo_automation_status(config)
 runner=_demo_automation_runner(config)
 if action=="once":
  return runner.run_cycle() if runner.start() else runner.status()
 runner.run_forever()
 return runner.status()

def _agent_status_view() -> dict:
 from .agent_loop import agent_transcript_store_from_env
 store=agent_transcript_store_from_env()
 paper=_paper_from_env()
 state=paper.state()
 return {"runs":store.runs(limit=5),
         "paper":{"stopped":state.get("stopped"),"position":state.get("position"),"cash":state.get("cash"),
                  "trades_today":state.get("trades_today"),"day_start_equity":state.get("day_start_equity")}}

def _agent_status_path() -> str:
 return os.getenv("AGENT_STATUS_FILE","reports/agent_status.json")

def _download_with_retry(downloader: Any,*args: Any,attempts: int=3,
                         backoff: tuple[float,...]=(5.0,20.0),**kwargs: Any) -> Any:
 """Transient-failure retry around a scheduled data download; auth errors are permanent."""
 from .data import CTraderAuthError
 last: Exception|None=None
 for attempt in range(attempts):
  try: return downloader.download(*args,**kwargs)
  except CTraderAuthError: raise
  except Exception as exc:
   last=exc
   if attempt<attempts-1: time.sleep(backoff[min(attempt,len(backoff)-1)])
 raise last

def _serve_agent_view() -> None:
 import threading
 from .agent_view import DEFAULT_VIEW_HOST, DEFAULT_VIEW_PORT
 from .agent_view import create_app
 host=os.getenv("AGENT_VIEW_HOST",DEFAULT_VIEW_HOST)
 port=int(os.getenv("AGENT_VIEW_PORT",str(DEFAULT_VIEW_PORT)))
 print(f"agent live view: http://{host}:{port}/",flush=True)
 uvicorn_server=__import__("uvicorn")
 from .agent_loop import agent_transcript_store_from_env
 uvicorn_server.run(create_app(store=agent_transcript_store_from_env()),host=host,port=port,log_level="warning")

def _agent_data_refresh_source(market_store: HistoricalDataStore, config: AgentConfig) -> Callable[[], dict]:
 """Bound data refresh for a stale agent tick. Runs the one-shot downloader in a
 fresh subprocess so its Twisted reactor never outlives a single invocation (the
 long-lived agent must not restart a reactor): auth errors still fail loudly."""
 import subprocess, sys, json as _json
 from pathlib import Path
 status_path=Path(os.getenv("CTRADER_DATA_UPDATE_STATUS_PATH","reports/data_update_status.json"))
 def refresh():
  from dotenv import dotenv_values
  env=dict(os.environ)
  latest=dotenv_values(".env")
  for key in ("CTRADER_ACCESS_TOKEN","CTRADER_REFRESH_TOKEN"):
   if latest.get(key): env[key]=latest[key]
  command=[sys.executable,"-m","xauusd.cli","data","update"]
  if not market_store.path.exists():
   from datetime import timedelta
   command=[sys.executable,"-m","xauusd.cli","data","download","--start",
            (datetime.now(timezone.utc)-timedelta(days=7)).date().isoformat()]
  proc=subprocess.run(command,env=env,
                      capture_output=True,text=True,timeout=config.data_refresh_timeout_seconds)
  try: payload=_json.loads(status_path.read_text())
  except (OSError,ValueError):
   return {"ok":False,"error_type":"status_missing","returncode":proc.returncode}
  if payload.get("state")!="ok":
   return {"ok":False,"error_type":payload.get("error_type") or payload.get("state"),
           "error_code":payload.get("error_code"),"description":payload.get("description"),
           "returncode":proc.returncode}
  return {"ok":True,"downloaded_rows":int(payload.get("downloaded_rows",0)),
          "last_bar_utc":payload.get("end"),"symbol":payload.get("symbol"),
          "returncode":proc.returncode}
 return refresh

def agent_controller(action: str) -> dict:
 """Single continuously trading AI agent with a visible thinking process."""
 from .agent_loop import (AgentConfig, ContinuousAgentRunner, agent_transcript_store_from_env, build_agent_registry)
 from .autonomous_harness import OpenAICompatiblePlanner
 from .canary_strategy import ConfirmedBreakoutCanarySource
 from .agent_status import read_status, write_status
 status_path=_agent_status_path()
 if action=="status":
  view=_agent_status_view(); view["status_file"]=read_status(status_path); return view
 if action=="view":
  _serve_agent_view()
  return {}
 if os.getenv("CTRADER_AUTOMATION_ENABLED")!="true":
  return {"state":"disabled","reason":"CTRADER_AUTOMATION_ENABLED must equal true",
          "enabled":os.getenv("CTRADER_AUTOMATION_ENABLED")=="true"}
 config=AgentConfig.from_env(); config.validate()
 paper=_paper_from_env()
 integrity=paper.integrity_check()
 if integrity!="ok":
  write_status({"state":"failed","reason":"integrity_check_failed","detail":integrity},status_path)
  return {"state":"refused","reason":"integrity_check_failed","integrity":integrity}
 transcript_store=agent_transcript_store_from_env(initialize=True)
 transcript_integrity=getattr(transcript_store,"integrity_check",lambda:"ok")()
 if transcript_integrity!="ok":
  write_status({"state":"failed","reason":"transcript_integrity_check_failed","detail":transcript_integrity},status_path)
  return {"state":"refused","reason":"transcript_integrity_check_failed","integrity":transcript_integrity}
 if os.getenv("AGENT_PLANNER","openai")=="datadog":
  try:
   from .bits import BitsClient
   BitsClient.from_env().verify_agent(os.getenv("DD_AGENT_ID"))
   if config.data_refresh_enabled: CTraderOpenApiConfig.from_env()
  except Exception as exc:
   paper.stop("missing_credentials")
   write_status({"state":"stopped","reason":"missing_credentials","error_type":type(exc).__name__},status_path)
   return {"state":"stopped","reason":"missing_credentials"}
 resume=paper.maybe_resume("agent_continuous_paper_loop")
 if not resume["resumed"]:
  write_status({"state":"stopped","reason":"resume_refused","kill_switch_reason":resume["kill_switch_reason"]},status_path)
  return {"state":"stopped","reason":"resume_refused","kill_switch_reason":resume["kill_switch_reason"]}
 market_store=HistoricalDataStore()
 source=LocalHistoricalMarketDataSource(market_store)
 coordinator=_paper_to_demo_coordinator(paper)
 refresh_source=None
 if config.data_refresh_enabled:
  refresh_source=_agent_data_refresh_source(market_store,config)
 firecrawl_client=None
 try:
  from .firecrawl_research import CockroachSourceStore, FirecrawlConfig, FirecrawlResearchClient
  firecrawl_client=FirecrawlResearchClient(FirecrawlConfig.from_env(),CockroachSourceStore())
 except Exception:
  firecrawl_client=None  # research is optional; the loop still runs without web retrieval
 registry=build_agent_registry(
  source,paper,coordinator,config,
  canary=ConfirmedBreakoutCanarySource(market_store,_positive_env_float("CTRADER_CANARY_PAPER_QUANTITY",1)),
  firecrawl_client=firecrawl_client)
 backend=os.getenv("AGENT_PLANNER","openai")
 runner_type=ContinuousAgentRunner
 if backend=="datadog":
  from .bits import BitsClient
  from .bits_runner import BitsAgentRunner
  runner_type=BitsAgentRunner
  planner=BitsClient.from_env()
 elif backend=="openai": planner=OpenAICompatiblePlanner.from_env()
 else: raise ValueError("AGENT_PLANNER must be datadog or openai")
 try:
  runner=runner_type(planner,registry,
                    transcript_store,source,paper,coordinator,config,
                    refresh_source=refresh_source,status_path=status_path)
 except Exception as exc:
  from .bits_jobs import AgentAlreadyRunning
  if isinstance(exc,AgentAlreadyRunning):
   return {"state":"refused","reason":"agent_already_running"}
  if backend!="datadog": raise
  paper.stop("recovery_failed")
  write_status({"state":"stopped","reason":"recovery_failed","error_type":type(exc).__name__},status_path)
  return {"state":"stopped","reason":"recovery_failed"}
 if action=="once":
  try: result=runner.run_tick()
  finally: runner.stop()
  print(f"agent run {runner.run_id} tick recorded; live view http://127.0.0.1:{os.getenv('AGENT_VIEW_PORT','8100')}/",flush=True)
  return result
 if action=="run":
  import signal
  import threading
  stop=threading.Event()
  def _terminate(signum,frame):
   stop.set()
   runner._stop.set()
  signal.signal(signal.SIGTERM,_terminate)
  # The live view is a dedicated always-on unit (xauusd-agent-view.service) that
  # reads only the persisted stores; the bot process must never own the port so
  # pausing/stopping it never takes the site down.
  try:
   runner.run_forever(stop=stop)
  except KeyboardInterrupt:
   stop.set()
  finally:
   runner.stop()
  return runner.status()
 raise ValueError(f"unknown agent action: {action}")

def agent_tool(name: str, raw: str) -> dict:
 """CLI bridge to the existing deterministic tools, for Bits shell requests."""
 from .agent_loop import AgentConfig, build_agent_registry
 from .autonomous_harness import _validate_json
 from .bits_jobs import SecretFilter
 paper=_paper_from_env()
 source=LocalHistoricalMarketDataSource(HistoricalDataStore())
 # Read tools must not discover or connect to a broker.
 if name=="propose_trade":
  if os.getenv("CTRADER_AUTOMATION_ENABLED")!="true":
   return {"accepted":False,"reason":"AUTOMATION_DISABLED"}
  coordinator=_paper_to_demo_coordinator(paper)
 else: coordinator=PaperToCTraderDemoCoordinator(paper,paper_only=True)
 registry=build_agent_registry(source,paper,coordinator,AgentConfig.from_env())
 tool=registry.get(name)
 value=json.loads(raw)
 _validate_json(value,tool.input_schema)
 return SecretFilter().clean(tool.handler(value))

def bits_recover(reason: str) -> dict:
 """Explicit operator acknowledgement after reconciling uncertain side effects."""
 from .agent_loop import agent_transcript_store_from_env
 from .bits_jobs import AgentLock, BitsStore, SecretFilter
 if not reason.strip() or SecretFilter().unsafe(reason): raise ValueError("safe recovery reason required")
 paper=_paper_from_env()
 if not paper.state().get("stopped"): raise ValueError("paper stop is required before recovery")
 transcript=agent_transcript_store_from_env()
 lock=AgentLock(transcript)
 try:
  store=BitsStore(transcript)
  store.recover()
  store.put("last_recovery",{"reason":reason,"recorded_at":datetime.now(timezone.utc).isoformat(),
                             "previous_phase":store.get("cycle",{}).get("phase")})
  store.put("cycle",{"phase":"idle"})
 finally: lock.close()
 return {"status":"reconciled","paper_stopped":True,"next":"paper start --reason operator_reconciled"}

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
 remote=sub.add_parser("remote-coordinator"); remote.add_argument("action",nargs="?",choices=["run","drain","resume","status"],default="run"); remote.add_argument("--idle-seconds",type=float,default=10)
 compute=sub.add_parser("compute-job"); compute.add_argument("job"); compute.add_argument("output")
 codex=sub.add_parser("codex-improve"); codex.add_argument("action",choices=["prepare","run","status"])
 ops=sub.add_parser("operations"); ops.add_argument("action",choices=["health","backup","verify-backup","capacity-plan","compact-artifacts","artifact-retention-inventory","scaling-checkpoint","capture-scaling-checkpoints","remote-artifacts-plan","remote-artifacts-apply","remote-artifacts-reconcile"]); ops.add_argument("--plan"); ops.add_argument("--digest"); ops.add_argument("--journal"); ops.add_argument("--root"); ops.add_argument("--target-hours",type=float,default=24); ops.add_argument("--efficiency",type=float,default=.8); ops.add_argument("--host-hour-cost",type=float)
 sub.add_parser("tournament-weekly-report")
 shadow=sub.add_parser("shadow"); shadow.add_argument("action",choices=["status","stop"]); shadow.add_argument("--reason",default="manual emergency stop")
 demo=sub.add_parser("demo-automation",help="explicitly operate the local-data cTrader demo canary")
 demo.add_argument("action",nargs="?",choices=["status","once","run"],default="status")
 agent=sub.add_parser("agent",help="single continuous AI paper-trading agent with a live thinking view")
 agent.add_argument("action",nargs="?",choices=["status","once","view","run"],default="status")
 tool=sub.add_parser("agent-tool",help="invoke deterministic tools from a Bits shell action")
 tool.add_argument("name",choices=["read_market","paper_state","propose_trade"])
 tool.add_argument("--input",default="{}")
 recover=sub.add_parser("bits-recover",help="acknowledge reconciled interrupted commands; leaves paper stopped")
 recover.add_argument("--reason",required=True)
 memory=sub.add_parser("bits-memory",help="read or replace compact research notes")
 memory.add_argument("action",choices=["show","write"])
 memory.add_argument("--input")
 memory.add_argument("--notes-only",action="store_true",help="show structured working notes without conversation history")
 job=sub.add_parser("bits-job",help="retrieve a bounded page of stored command output")
 job.add_argument("job_id")
 job.add_argument("--stream",choices=["stdout","stderr"],default="stdout")
 job.add_argument("--offset",type=int,default=0)
 job.add_argument("--limit",type=int,default=2500)
 paper=sub.add_parser("paper",help="manage the deterministic paper trading lifecycle (kill switch)")
 paper.add_argument("action",choices=["status","start","stop"])
 paper.add_argument("--reason",default="operator")
 pst=sub.add_parser("state",help="local state database integrity, backup, and restore")
 pst.add_argument("action",choices=["integrity","backup","restore","reset"])
 pst.add_argument("--confirm-reset",action="store_true",help="explicitly discard stopped paper/session history after backup")
 pst.add_argument("--backup",help="backup directory or state.db.gz to restore")
 pst.add_argument("--root",default="backups/local-state")
 sub.add_parser("adaptive-analytics")
 d=sub.add_parser("data"); ds=d.add_subparsers(dest="data_cmd"); i=ds.add_parser("import"); i.add_argument("csv"); v=ds.add_parser("validate")
 download=ds.add_parser("download"); download.add_argument("--start",required=True,help="UTC start date/time (for example 2026-08-01)"); download.add_argument("--end",help="UTC end date/time; defaults to now"); download.add_argument("--page-size",type=int,default=int(os.getenv("CTRADER_DATA_UPDATE_PAGE_SIZE","5000")))
 update=ds.add_parser("update"); update.add_argument("--overlap-minutes",type=int,default=int(os.getenv("CTRADER_DATA_UPDATE_OVERLAP_MINUTES","10"))); update.add_argument("--page-size",type=int,default=int(os.getenv("CTRADER_DATA_UPDATE_PAGE_SIZE","5000")))
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
 if a.cmd=="remote-coordinator":
  bridge=RemoteComputeBridge()
  if a.action=="run": bridge.run_forever(a.idle_seconds)
  else: print(json.dumps(bridge.drain() if a.action=="drain" else bridge.resume() if a.action=="resume" else bridge.drain_status(),indent=2))
 if a.cmd=="compute-job": print(json.dumps(compute_job(Path(a.job),Path(a.output)),indent=2,default=str))
 if a.cmd=="codex-improve":
  workflow=CodexImprovementWorkflow()
  if a.action=="status": result=__import__('xauusd.dashboard',fromlist=['read_json']).read_json(Path("reports/tournament/codex/latest.json"),{"status":"never_run"})
  elif a.action=="prepare": result=workflow.prepare(TournamentDataset().active())
  else: result=workflow.run(TournamentDataset().active())
  print(json.dumps(result,indent=2,default=str))
 if a.cmd=="operations":
  manager=OperationsManager()
  if a.action in {"remote-artifacts-apply","remote-artifacts-reconcile"} and not all((a.plan,a.digest,a.journal)): p.error("--plan, --digest, and --journal are required")
  if a.action in {"artifact-retention-inventory","verify-backup"} and not a.root: p.error("--root is required")
  result=manager.health() if a.action=="health" else manager.backup() if a.action=="backup" else OperationsManager.verify_backup(Path(a.root)) if a.action=="verify-backup" else OperationsManager.capacity_plan(manager.scaling_checkpoint(),a.target_hours,a.efficiency,a.host_hour_cost) if a.action=="capacity-plan" else manager.scaling_checkpoint() if a.action=="scaling-checkpoint" else manager.capture_scaling_checkpoints() if a.action=="capture-scaling-checkpoints" else manager.remote_artifacts_plan() if a.action=="remote-artifacts-plan" else OperationsManager.apply_remote_artifacts_plan(Path(a.plan),a.digest,Path(a.journal)) if a.action=="remote-artifacts-apply" else manager.reconcile_remote_artifacts(Path(a.plan),a.digest,Path(a.journal)) if a.action=="remote-artifacts-reconcile" else OperationsManager.artifact_retention_inventory(Path(a.root)) if a.action=="artifact-retention-inventory" else manager.compact_artifacts()
  print(json.dumps(result,indent=2,default=str))
  if a.action=="verify-backup" and not result["valid"]: raise SystemExit(1)
 if a.cmd=="tournament-weekly-report": print(json.dumps(WeeklyTournamentReport().build(),indent=2,default=str))
 if a.cmd=="shadow":
  manager=ShadowTradingReadiness(); result=manager.readiness() if a.action=="status" else manager.emergency_stop(a.reason)
  print(json.dumps(result,indent=2,default=str))
 if a.cmd=="demo-automation":
  try: result=demo_automation(a.action)
  except Exception as exc: p.error(f"demo automation setup failed: {type(exc).__name__}")
  print(json.dumps(result,indent=2,allow_nan=False,default=str))
 if a.cmd=="agent":
  try: result=agent_controller(a.action)
  except KeyboardInterrupt: raise
  except Exception as exc:
   from .agent_status import write_status
   write_status({"state":"failed","error_type":type(exc).__name__})
   p.error(f"agent command failed: {type(exc).__name__}")
   raise SystemExit(1)
  print(json.dumps(result,indent=2,allow_nan=False,default=str))
 if a.cmd=="agent-tool":
  try: result=agent_tool(a.name,a.input)
  except Exception as exc: result={"status":"failed","error_type":type(exc).__name__}
  print(json.dumps(result,allow_nan=False))
 if a.cmd=="bits-recover":
  try: result=bits_recover(a.reason)
  except Exception as exc: p.error(type(exc).__name__)
  print(json.dumps(result))
 if a.cmd in {"bits-memory","bits-job"}:
  from .agent_loop import agent_transcript_store_from_env
  from .bits_jobs import BitsStore,SecretFilter
  from .bits_memory import BitsMemory
  try:
   store=BitsStore(agent_transcript_store_from_env())
   if a.cmd=="bits-memory":
    memory=BitsMemory(store)
    result=(store.get("working_notes") if a.notes_only else memory.context()) if a.action=="show" else memory.write_notes(json.loads(a.input or "null"))
   else:
    if a.offset<0 or not 1<=a.limit<=65536: raise ValueError("invalid output page bounds")
    job=store.job(a.job_id); text=job[a.stream]; end=min(len(text),a.offset+a.limit)
    result={"job_id":a.job_id,"status":job["status"],"exit_code":job["exit_code"],"stream":a.stream,
            "text":text[a.offset:end],"offset":a.offset,"next_offset":end if end<len(text) else None,
            "stored_characters":len(text),"capture_truncated":job["truncated"]}
   print(json.dumps(SecretFilter().clean(result),allow_nan=False))
  except Exception as exc: p.error(type(exc).__name__)
 if a.cmd=="paper":
  pt=_paper_from_env()
  if a.action=="stop": pt.stop(a.reason)
  elif a.action=="start": pt.start(a.reason or "operator_resume")
  print(json.dumps(pt.summary(),indent=2,allow_nan=False,default=str))
 if a.cmd=="state":
  from .local_state import state_db_path
  from .paper_trading import state_backend
  from .agent_loop import agent_transcript_store_from_env
  if state_backend()=="cockroach":
   print(json.dumps({"backend":"cockroach","action":a.action,"skipped":True,
                     "reason":"backup/restore/integrity are local-only commands"},indent=2))
  elif a.action=="integrity":
   result={"backend":"local","db_path":state_db_path(),
           "paper":_paper_from_env().integrity_check(),
           "transcript":getattr(agent_transcript_store_from_env(),"integrity_check",lambda:"ok")()}
   print(json.dumps(result,indent=2,allow_nan=False,default=str))
   if result["paper"]!="ok" or result["transcript"]!="ok": raise SystemExit(1)
  elif a.action=="backup":
   from .state_backup import backup_local_state
   print(json.dumps(backup_local_state(dest_root=a.root),indent=2,allow_nan=False,default=str))
  elif a.action=="reset":
   if not a.confirm_reset: p.error("--confirm-reset is required to discard paper/session history")
   if os.getenv("CTRADER_PAPER_ONLY")!="true": p.error("reset is only allowed with CTRADER_PAPER_ONLY=true")
   from .session_reset import reset_paper_session
   result=reset_paper_session(_paper_from_env(),agent_transcript_store_from_env(),a.root)
   from .agent_status import write_status
   write_status({"status":"stopped","paper_stopped":True,"reason":"session_reset","tick":0})
   print(json.dumps(result,indent=2))
  else:
   if not a.backup: p.error("--backup is required (backup directory or state.db.gz)")
   from .state_backup import restore_local_state
   print(json.dumps(restore_local_state(a.backup),indent=2,allow_nan=False,default=str))
 if a.cmd=="adaptive-analytics":
  print(json.dumps(AdaptiveSearch(ExperimentRegistry()).analyze(),indent=2,default=str))
 if a.cmd=="data":
  s=HistoricalDataStore(); status_path=Path(os.getenv("CTRADER_DATA_UPDATE_STATUS_PATH","reports/data_update_status.json"))
  try:
   if a.data_cmd=="import": result=CTraderHistoricalAdapter(s).import_csv(Path(a.csv))
   elif a.data_cmd=="validate": result=s.validate(s.read())
   elif a.data_cmd=="download": result=CTraderOpenApiDownloader(CTraderOpenApiConfig.from_env(),s).download(a.start,a.end,a.page_size)
   elif a.data_cmd=="update":
    if not s.path.exists(): raise RuntimeError("no local data; run data download --start DATE first")
    start=s.read().index.max()-__import__('pandas').Timedelta(minutes=a.overlap_minutes)
    result=_download_with_retry(CTraderOpenApiDownloader(CTraderOpenApiConfig.from_env(),s),
                                start,page_size=a.page_size)
   else: p.error("choose a data command")
   if a.data_cmd in ("download","update"):
    status_path.parent.mkdir(parents=True,exist_ok=True)
    status_path.write_text(json.dumps({"state":"ok","recorded_at":datetime.now(timezone.utc).isoformat(),
       "end":result.get("end"),"downloaded_rows":result.get("downloaded_rows"),"error_code":None}))
   print(json.dumps(result,indent=2))
  except Exception as exc:
   from .data import CTraderAuthError
   code=getattr(exc,"code",None) if isinstance(exc,CTraderAuthError) else None
   description=getattr(exc,"description",None) if isinstance(exc,CTraderAuthError) else None
   status={"state":"auth_error" if code else "failed","recorded_at":datetime.now(timezone.utc).isoformat(),
           "error_code":code,"description":description,"error_type":type(exc).__name__}
   status_path.parent.mkdir(parents=True,exist_ok=True); status_path.write_text(json.dumps(status))
   print(json.dumps(status,indent=2)); raise SystemExit(1)
if __name__=="__main__": main()
