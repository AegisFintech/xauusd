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

 def generate(self,dataset: dict,limit: int=50) -> dict:
  parents=self._parents(); all_rows=self.registry.list(limit=max(1000,self.registry.count()))
  seen={semantic_identity(row["strategy_family"],row["parameters"]) for row in all_rows}
  created=[]; duplicates=0
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
   for child_strategy,child_execution,operation,key,multiplier in candidates:
    identity=semantic_identity(parent["strategy_family"],{"strategy":child_strategy,"execution":child_execution})
    if identity in seen: duplicates+=1; continue
    seen.add(identity)
    provenance={"generator":GENERATOR_VERSION,"operation":operation,"parent_experiment_ids":[parent["id"]],
                "mutated_parameter":key,"multiplier":multiplier,
                "parent_validation_score":parent["validation"].get("score")}
    parameters={"strategy":child_strategy,"execution":child_execution,"provenance":provenance}
    spec=ExperimentSpec(parent["strategy_family"],parent["formula"],parameters,dataset["version"],dataset["fingerprint"],
                        dataset["engine_version"],dataset["cost_model_version"])
    row,is_new=self.registry.register(spec,priority=20)
    if is_new: created.append({"experiment_id":row["id"],"family":row["strategy_family"],"provenance":provenance})
    else: duplicates+=1
    if len(created)>=limit: break
   if len(created)>=limit: break
  family_counts=dict(sorted(__import__("collections").Counter(x["family"] for x in created).items()))
  report={"generator_version":GENERATOR_VERSION,"dataset_version":dataset["version"],"parents":len(parents),
          "created":len(created),"duplicates":duplicates,"family_counts":family_counts,
          "exhausted":len(created)==0,"challengers":created}
  self.output_path.parent.mkdir(parents=True,exist_ok=True)
  temporary=self.output_path.with_suffix(".json.tmp"); temporary.write_text(json.dumps(report,indent=2)); temporary.replace(self.output_path)
  return report
