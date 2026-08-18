from __future__ import annotations

from collections import defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path
import json
import math

from .experiment_registry import ExperimentRegistry


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
  tests=max(1,len(completed)); familywise_05=1-(1-.05)**tests
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
          "champion":champion,"champion_tenure_hours":tenure_hours,
          "multiple_testing":{"experiments":tests,"nominal_alpha":.05,"familywise_false_positive_probability":familywise_05,
                              "warning":"Many trials inflate false discoveries; promotion still requires walk-forward, bootstrap, and holdout gates."}}
  self.output_root.mkdir(parents=True,exist_ok=True); run_id=now.strftime("%Y%m%dT%H%M%SZ")
  (self.output_root/f"{run_id}.json").write_text(json.dumps(report,indent=2,allow_nan=False))
  latest=self.output_root/"latest.json"; temporary=latest.with_suffix(".json.tmp"); temporary.write_text(json.dumps(report,indent=2,allow_nan=False)); temporary.replace(latest)
  return report
