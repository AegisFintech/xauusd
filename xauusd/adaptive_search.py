from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import hashlib
import json

from .experiment_registry import ExperimentRegistry,ExperimentSpec,canonical_json


GENERATOR_VERSION="adaptive-search-v1"
BOUNDS={
 "stop_distance":(.5,8.0),"target_distance":(1.0,12.0),"max_holding_bars":(5,120),
 "entry_z":(.5,3.0),"exit_z":(.05,1.0),"window":(5,80),"fast":(2,30),"slow":(10,100),
 "threshold_atr":(.03,1.5),"lookback":(5,120),"exit_ema":(5,80),"min_strength":(.03,1.5),
 "range_ratio":(1.0,3.0),"body_fraction":(.1,.95),"return_period":(2,60),
 "trend_threshold":(.05,1.5),"pullback_z":(.25,2.5),
}


def semantic_identity(family: str,parameters: dict) -> str:
 payload={"family":family,"strategy":parameters.get("strategy",parameters),"execution":parameters.get("execution",{})}
 return hashlib.sha256(canonical_json(payload).encode()).hexdigest()


def _bounded(key,value,multiplier):
 adjusted=value*multiplier
 low,high=BOUNDS.get(key,(None,None))
 if low is not None: adjusted=max(low,min(high,adjusted))
 return int(round(adjusted)) if isinstance(value,int) and not isinstance(value,bool) else round(float(adjusted),6)


class AdaptiveSearch:
 def __init__(self,registry: ExperimentRegistry,output_path: Path=Path("reports/tournament/adaptive.json")):
  self.registry=registry; self.output_path=output_path

 def _parents(self,per_family=3):
  grouped=defaultdict(list)
  for row in self.registry.leaderboard(500):
   if len(grouped[row["strategy_family"]])<per_family: grouped[row["strategy_family"]].append(row)
  return [row for family in sorted(grouped) for row in grouped[family]]

 def _previous(self) -> dict:
  if not self.output_path.exists(): return {}
  try: return json.loads(self.output_path.read_text())
  except (OSError,json.JSONDecodeError): return {}

 def generate(self,dataset: dict,limit: int=50,generation: int | None=None,
              trigger_completed: int | None=None) -> dict:
  previous=self._previous()
  previous_generation=int(previous.get("generation",1 if previous else 0) or 0)
  generation=generation or previous_generation+1
  parents=self._parents(); all_rows=self.registry.list(limit=max(1000,self.registry.count()))
  seen={semantic_identity(row["strategy_family"],row["parameters"]) for row in all_rows}
  created=[]; duplicates=0; candidate_groups=[]
  for parent in parents:
   raw=parent["parameters"]; strategy=dict(raw.get("strategy",raw)); execution=dict(raw.get("execution",{}))
   candidates=[]
   for scope,values in (("strategy",strategy),("execution",execution)):
    for key,value in sorted(values.items()):
     if isinstance(value,bool) or not isinstance(value,(int,float)) or value==0: continue
     for multiplier in (.85,1.15):
      child_strategy=dict(strategy); child_execution=dict(execution)
      target=child_strategy if scope=="strategy" else child_execution
      target[key]=_bounded(key,value,multiplier)
      if "fast" in child_strategy and "slow" in child_strategy and child_strategy["fast"]>=child_strategy["slow"]: continue
      candidates.append((child_strategy,child_execution,"bounded_mutation",key,multiplier))
   candidate_groups.append((parent,candidates))
  while candidate_groups and len(created)<limit:
   remaining=[]
   for parent,candidates in candidate_groups:
    if not candidates: continue
    child_strategy,child_execution,operation,key,multiplier=candidates.pop(0)
    identity=semantic_identity(parent["strategy_family"],{"strategy":child_strategy,"execution":child_execution})
    if identity in seen: duplicates+=1
    else:
     seen.add(identity)
     provenance={"generator":GENERATOR_VERSION,"operation":operation,"parent_experiment_ids":[parent["id"]],
                 "generation":generation,"mutated_parameter":key,"multiplier":multiplier,
                 "parent_validation_score":parent["validation"].get("score")}
     parameters={"strategy":child_strategy,"execution":child_execution,"provenance":provenance}
     spec=ExperimentSpec(parent["strategy_family"],parent["formula"],parameters,dataset["version"],dataset["fingerprint"],
                         dataset["engine_version"],dataset["cost_model_version"])
     row,is_new=self.registry.register(spec,priority=20)
     if is_new: created.append({"experiment_id":row["id"],"family":row["strategy_family"],"provenance":provenance})
     else: duplicates+=1
    if candidates: remaining.append((parent,candidates))
    if len(created)>=limit: break
   candidate_groups=remaining
  family_counts=dict(sorted(__import__("collections").Counter(x["family"] for x in created).items()))
  parent_details=[{"experiment_id":row["id"],"family":row["strategy_family"],
                   "score":row["validation"].get("score")} for row in parents]
  best_score=max((x["score"] for x in parent_details if x["score"] is not None),default=None)
  report={"generator_version":GENERATOR_VERSION,"dataset_version":dataset["version"],
          "generation":generation,"trigger_completed":trigger_completed,
          "last_completed_trigger":trigger_completed,"best_score_before":best_score,
          "parents":len(parents),"parent_details":parent_details,
          "created":len(created),"duplicates":duplicates,"family_counts":family_counts,
          "exhausted":len(created)==0,"challengers":created}
  self.output_path.parent.mkdir(parents=True,exist_ok=True)
  history=self.output_path.parent/"adaptive"/f"generation-{generation:04d}.json"
  history.parent.mkdir(parents=True,exist_ok=True)
  history_temporary=history.with_suffix(".json.tmp")
  history_temporary.write_text(json.dumps(report,indent=2)); history_temporary.replace(history)
  temporary=self.output_path.with_suffix(".json.tmp"); temporary.write_text(json.dumps(report,indent=2)); temporary.replace(self.output_path)
  return report
