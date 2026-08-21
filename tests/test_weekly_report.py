from datetime import datetime,timezone

from xauusd.experiment_registry import ExperimentRegistry,ExperimentSpec
from xauusd.weekly_report import WeeklyTournamentReport,gate_analytics


def test_weekly_report_tracks_throughput_families_and_multiple_testing(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db")
 spec=ExperimentSpec("momentum","f",{},"v","d","e","c"); row,_=registry.register(spec); claimed=registry.claim_next("w")
 registry.complete(claimed["id"],"w",{"validation":{"net_profit":2}}, {"score":1.5,"passed":True})
 report=WeeklyTournamentReport(registry,tmp_path/"weekly").build(datetime.now(timezone.utc))
 assert report["all_time_completed"]==1 and report["families"]["momentum"]["passed"]==1
 assert report["multiple_testing"]["experiments"]==1 and (tmp_path/"weekly"/"latest.json").exists()


def row(identifier,family,gates,score=0,metrics=None,stage="validation"):
 return {"id":identifier,"strategy_family":family,"validation":{"passed":all(gates.values()),"gates":gates,
         "score":score,"stage":stage},"metrics":{"validation":metrics}}


def test_gate_analytics_counts_failures_near_passes_and_coverage():
 rows=[row(1,"momentum",{"profit_factor":False,"drawdown":True},2,
           {"net_profit":3,"trades":20,"turnover":4}),
       row(2,"momentum",{"profit_factor":False,"drawdown":False},1,{"net_profit":-2,"trades":30}),
       row(3,"breakout",{"profit_factor":True,"drawdown":True},3,{"net_profit":4,"trades":10})]
 report=gate_analytics(rows)
 assert report["evaluated_with_gates"]==3 and report["passed"]==1 and report["near_pass_count"]==1
 assert report["failed_gate_counts"]=={"profit_factor":2,"drawdown":1}
 assert report["failure_combinations"]["drawdown + profit_factor"]==1
 assert report["families"]["momentum"]["near_passes"]==1
 assert report["near_passes"][0]["experiment_id"]==1
 assert report["metric_coverage"]["net_profit"]=={"available":3,"missing":0,"fraction":1.0}
 assert report["metric_coverage"]["turnover"]["available"]==1
 assert report["metric_coverage"]["expected_shortfall"]["available"]==0


def test_gate_analytics_handles_development_and_missing_gate_evidence():
 rows=[row(1,"momentum",{"minimum_trades":False},metrics=None,stage="development"),
       {"id":2,"strategy_family":"breakout","validation":None,"metrics":{"validation":None}}]
 report=gate_analytics(rows,near_pass_limit=0)
 assert report["stages"]=={"development":1,"unknown":1}
 assert report["evaluated_with_gates"]==1 and report["near_pass_count"]==1
 assert report["near_passes"]==[] and report["metric_coverage"]["total_cost"]["missing"]==2
