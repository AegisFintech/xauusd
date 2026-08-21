from __future__ import annotations

from collections import defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path
import json
import itertools
import statistics

from .experiment_registry import ExperimentRegistry


ATTRIBUTION_METRICS=("net_profit","gross_profit","total_cost","turnover","profit_concentration",
                     "expected_shortfall","regime_results")


def gate_analytics(rows: list[dict],near_pass_limit: int=25) -> dict:
 gate_failures=defaultdict(int); combinations=defaultdict(int); stages=defaultdict(int)
 coverage=defaultdict(int); families=defaultdict(lambda:{"completed":0,"passed":0,"near_passes":0,"gate_failures":defaultdict(int)})
 near_passes=[]; evaluated=passed=0
 for row in rows:
  validation=row.get("validation") or {}; gates=validation.get("gates") or {}
  metrics=(row.get("metrics") or {}).get("validation") or {}
  family=families[row["strategy_family"]]; family["completed"]+=1
  stages[validation.get("stage") or ("validation" if metrics else "unknown")]+=1
  for metric in ATTRIBUTION_METRICS:
   coverage[metric]+=int(metrics.get(metric) is not None)
  if not gates: continue
  evaluated+=1; failed=sorted(name for name,value in gates.items() if not bool(value))
  if not failed:
   passed+=1; family["passed"]+=1
   continue
  for gate in failed:
   gate_failures[gate]+=1; family["gate_failures"][gate]+=1
  combinations[" + ".join(failed)]+=1
  if len(failed)==1:
   family["near_passes"]+=1
   near_passes.append({"experiment_id":row["id"],"family":row["strategy_family"],
                       "failed_gate":failed[0],"score":validation.get("score"),
                       "net_profit":metrics.get("net_profit"),"trades":metrics.get("trades")})
 def rank(candidate):
  score=candidate["score"]
  return (score is not None,float(score) if score is not None else float("-inf"),-candidate["experiment_id"])
 near_passes.sort(key=rank,reverse=True)
 family_rows={}
 for name,value in sorted(families.items()):
  family_rows[name]={**value,"gate_failures":dict(sorted(value["gate_failures"].items()))}
 return {"completed":len(rows),"evaluated_with_gates":evaluated,"passed":passed,
         "near_pass_count":sum(row["near_passes"] for row in family_rows.values()),
         "failed_gate_counts":dict(sorted(gate_failures.items(),key=lambda item:(-item[1],item[0]))),
         "failure_combinations":dict(sorted(combinations.items(),key=lambda item:(-item[1],item[0]))),
         "stages":dict(sorted(stages.items())),"families":family_rows,
         "near_passes":near_passes[:max(0,near_pass_limit)],
         "metric_coverage":{metric:{"available":coverage[metric],"missing":len(rows)-coverage[metric],
                                    "fraction":coverage[metric]/len(rows) if rows else 0}
                            for metric in ATTRIBUTION_METRICS},
         "limitations":["Gate failures are observed rejection reasons, not proof of economic loss cause.",
                        "Cost, turnover, concentration, regime, and tail attribution require their metric coverage before classification."]}


def _quantile(values: list[float],fraction: float) -> float | None:
 if not values: return None
 ordered=sorted(values); position=(len(ordered)-1)*fraction; low=int(position); high=min(len(ordered)-1,low+1)
 weight=position-low
 return ordered[low]*(1-weight)+ordered[high]*weight


def selection_bias_analytics(rows: list[dict],alpha: float=.05) -> dict:
 scores=[]; pvalues=[]; holdout=stability=0; families=defaultdict(int); cohorts=defaultdict(list)
 for row in rows:
  families[row["strategy_family"]]+=1; validation=row.get("validation") or {}; metrics=row.get("metrics") or {}
  score=validation.get("score")
  if score is not None: scores.append(float(score))
  pvalue=validation.get("p_value")
  if pvalue is not None and 0<=float(pvalue)<=1: pvalues.append(float(pvalue))
  holdout+=int(metrics.get("holdout") is not None)
  stability+=int(validation.get("stable_neighbor_fraction") is not None or "parameter_stability" in (validation.get("gates") or {}))
  folds=(validation.get("walk_forward") or {}).get("folds") or []
  profits=[fold.get("net_profit") for fold in folds]
  if len(profits)>=4 and len(profits)%2==0 and all(value is not None for value in profits):
   signature=(row.get("dataset_version"),tuple((fold.get("start"),fold.get("end")) for fold in folds))
   cohorts[signature].append([float(value) for value in profits])
 tests=max(1,len(rows)); bonferroni=alpha/tests
 discoveries=0
 for rank,pvalue in enumerate(sorted(pvalues),1):
  if pvalue<=alpha*rank/len(pvalues): discoveries=rank
 eligible=max(cohorts.values(),key=len,default=[]); split_count=overfit=0
 if len(eligible)>=2:
  fold_count=len(eligible[0]); half=fold_count//2
  for selected in itertools.combinations(range(fold_count),half):
   selected=set(selected); other=[index for index in range(fold_count) if index not in selected]
   in_sample=[statistics.mean(row[index] for index in selected) for row in eligible]
   winner=max(range(len(eligible)),key=lambda index:(in_sample[index],-index))
   out_sample=[statistics.mean(row[index] for index in other) for row in eligible]; winner_value=out_sample[winner]
   percentile=(sum(value<winner_value for value in out_sample)+.5*sum(value==winner_value for value in out_sample))/len(out_sample)
   split_count+=1; overfit+=int(percentile<.5)
 pbo=overfit/split_count if split_count else None
 return {"experiments":len(rows),"families":dict(sorted(families.items())),"nominal_alpha":alpha,
         "bonferroni_alpha":bonferroni,"familywise_false_positive_probability":1-(1-alpha)**tests,
         "score_distribution":{"available":len(scores),"best":max(scores) if scores else None,
             "median":statistics.median(scores) if scores else None,"interquartile_range":[_quantile(scores,.25),_quantile(scores,.75)],
             "worst_decile":_quantile(scores,.10)},
         "false_discovery_rate":{"status":"available" if pvalues else "unavailable","p_values":len(pvalues),
                                 "method":"Benjamini-Hochberg","discoveries":discoveries if pvalues else None},
         "probability_of_backtest_overfitting":{"status":"available" if split_count else "unavailable",
             "method":"aligned-fold combinatorially symmetric cross-validation","eligible_strategies":len(eligible),
             "splits":split_count,"probability":pbo},
         "parameter_stability":{"available":stability,"missing":len(rows)-stability},
         "holdout":{"evaluated":holdout,"not_evaluated":len(rows)-holdout,
                    "note":"Counts stored results only; this report does not access protected holdout data."},
         "warnings":["The best observed score is selection-biased across all attempted variants.",
                     "FDR is unavailable until valid predeclared null-hypothesis p-values are stored.",
                     "PBO applies only to strategies sharing an aligned fold matrix and does not replace locked holdout evaluation."]}


class WeeklyTournamentReport:
 def __init__(self,registry: ExperimentRegistry | None=None,output_root=Path("reports/tournament/weekly")):
  self.registry=registry or ExperimentRegistry(); self.output_root=Path(output_root)

 def build(self,now: datetime | None=None) -> dict:
  now=now or datetime.now(timezone.utc); start=now-timedelta(days=7)
  completed=self.registry.list("completed",limit=max(1,self.registry.count("completed")))
  current=[row for row in completed if row.get("finished_at") and datetime.fromisoformat(row["finished_at"])>=start]
  previous=[row for row in completed if row.get("finished_at") and start-timedelta(days=7)<=datetime.fromisoformat(row["finished_at"])<start]
  families=defaultdict(lambda:{"completed":0,"passed":0,"best_score":None,"best_net_profit":None})
  scores=[]; positive=0
  for row in current:
   validation=row.get("validation") or {}; metrics=(row.get("metrics") or {}).get("validation") or {}; family=families[row["strategy_family"]]
   family["completed"]+=1; family["passed"]+=int(bool(validation.get("passed")))
   score=validation.get("score"); profit=metrics.get("net_profit")
   if score is not None: scores.append(score); family["best_score"]=score if family["best_score"] is None else max(family["best_score"],score)
   if profit is not None:
    positive+=int(profit>0); family["best_net_profit"]=profit if family["best_net_profit"] is None else max(family["best_net_profit"],profit)
  leaders=self.registry.leaderboard(1); best=leaders[0] if leaders else None
  previous_scores=[(row.get("validation") or {}).get("score") for row in previous]
  previous_scores=[x for x in previous_scores if x is not None]
  current_best=max(scores) if scores else None; previous_best=max(previous_scores) if previous_scores else None
  champion=None
  if best: champion=self.registry.champion(best["dataset_version"])
  tenure_hours=(now-datetime.fromisoformat(champion["promoted_at"])).total_seconds()/3600 if champion else None
  report={"generated_at":now.isoformat(),"period_start":start.isoformat(),"period_end":now.isoformat(),
          "completed_this_week":len(current),"completed_previous_week":len(previous),
          "throughput_change":len(current)-len(previous),"positive_validation_fraction":positive/len(current) if current else 0,
          "passed_robust_gates":sum(row["passed"] for row in families.values()),
          "current_best_score":current_best,"previous_best_score":previous_best,
          "best_score_improvement":current_best-previous_best if current_best is not None and previous_best is not None else None,
          "all_time_completed":len(completed),"families":dict(sorted(families.items())),
          "gate_analytics":gate_analytics(current),
          "champion":champion,"champion_tenure_hours":tenure_hours,
          "multiple_testing":selection_bias_analytics(completed)}
  self.output_root.mkdir(parents=True,exist_ok=True); run_id=now.strftime("%Y%m%dT%H%M%SZ")
  (self.output_root/f"{run_id}.json").write_text(json.dumps(report,indent=2,allow_nan=False))
  latest=self.output_root/"latest.json"; temporary=latest.with_suffix(".json.tmp"); temporary.write_text(json.dumps(report,indent=2,allow_nan=False)); temporary.replace(latest)
  return report
