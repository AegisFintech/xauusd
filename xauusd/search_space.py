from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterator

from .experiment_registry import ExperimentRegistry, ExperimentSpec, from_strategy
from .research import StrategySpec


EXECUTION_GRID={
 "stop_distance":(.75,1.0,1.25,1.75,2.5,3.25,4.0,5.0),
 "target_distance":(1.0,1.5,2.0,2.5,3.25,4.0,5.0,6.0),
 "max_holding_bars":(5,10,15,30,60,120,240),
}
STRATEGY_GRIDS={
 "mean_reversion":{"window":(10,20,40),"entry_z":(1.0,1.5,2.0),"exit_z":(.1,.3),"direction":("both","long","short")},
 "momentum":{"fast":(5,8,12),"slow":(20,34,50),"threshold_atr":(.1,.25,.5),"direction":("both","long","short")},
 "breakout":{"lookback":(15,30,60),"exit_ema":(10,20,40),"direction":("both","long","short")},
 "micro_trend":{"fast":(3,5,8),"slow":(15,20,34),"min_strength":(.1,.25,.5),"direction":("both","long","short")},
 "volatility_expansion":{"range_ratio":(1.25,1.5,2.0),"body_fraction":(.4,.6,.8),"direction":("both","long","short")},
 "session_momentum":{"start_hour":(0,7,12),"end_hour":(7,12,20),"return_period":(5,15,30),"direction":("both","long","short")},
 "regime_switch":{"trend_threshold":(.25,.5,.75),"entry_z":(1.0,1.5,2.0)},
 "autocorrelation_regime":{"corr_window":(20,40,80),"lag":(1,3,5),"threshold":(.05,.15,.3),"return_period":(1,5),"direction":("both","long","short")},
 "multi_horizon_momentum":{"fast_period":(3,5,10),"slow_period":(15,30,60),"threshold_atr":(0,.05,.15),"direction":("both","long","short")},
 "quantile_reversion":{"window":(20,40,80),"entry_quantile":(.05,.1,.2),"exit_quantile":(.4,.5),"direction":("both","long","short")},
 "volatility_adjusted_trend":{"return_period":(3,5,10,20),"vol_window":(15,30,60),"threshold":(.25,.5,1.0,1.5),"direction":("both","long","short")},
 "trend_pullback":{"fast":(3,5,8),"slow":(20,34,50),"min_strength":(.1,.25,.5),"pullback_z":(.5,.75,1.0,1.5),"direction":("both","long","short")},
 "confirmed_breakout":{"lookback":(15,30,60,120),"min_strength":(.1,.25,.5),"range_ratio":(1.1,1.5,2.0),"direction":("both","long","short")},
}


def combinations(grid: dict) -> Iterator[dict]:
 keys=tuple(grid)
 for values in product(*(grid[key] for key in keys)):
  item=dict(zip(keys,values))
  if "fast" in item and "slow" in item and item["fast"]>=item["slow"]: continue
  if "start_hour" in item and item["start_hour"]>=item["end_hour"]: continue
  yield item


def candidate_specs() -> Iterator[tuple[StrategySpec,dict]]:
 for family,grid in STRATEGY_GRIDS.items():
  for strategy_params in combinations(grid):
   for execution_params in combinations(EXECUTION_GRID):
    yield StrategySpec(family,strategy_params),execution_params


def catalog_size() -> int:
 return sum(1 for _ in candidate_specs())


def seed_catalog(registry: ExperimentRegistry,dataset: dict,commit: str|None=None,limit: int|None=None) -> dict:
 created=existing=seen=0
 for strategy,execution in candidate_specs():
  base=from_strategy(strategy,dataset,commit)
  parameters={"strategy":strategy.parameters,"execution":execution}
  spec=ExperimentSpec(base.strategy_family,base.formula,parameters,base.dataset_version,base.dataset_fingerprint,
                      base.engine_version,base.cost_model_version,commit)
  _,is_new=registry.register(spec); created+=int(is_new); existing+=int(not is_new); seen+=1
  if limit is not None and seen>=limit: break
 summary=registry.summary(); total=catalog_size()
 return {"catalog_size":total,"considered":seen,"created":created,"existing":existing,
         "registered_for_dataset":summary["total"],"completion":min(1.0,summary["total"]/total)}


def replenish_catalog(registry: ExperimentRegistry,dataset: dict,target_new: int=250,commit: str|None=None) -> dict:
 """Add the next unseen catalog entries, scanning deterministically past duplicates."""
 created=existing=considered=0
 for strategy,execution in candidate_specs():
  base=from_strategy(strategy,dataset,commit)
  spec=ExperimentSpec(base.strategy_family,base.formula,
   {"strategy":strategy.parameters,"execution":execution},base.dataset_version,base.dataset_fingerprint,
   base.engine_version,base.cost_model_version,commit)
  _,is_new=registry.register(spec)
  created+=int(is_new); existing+=int(not is_new); considered+=1
  if created>=target_new: break
 total=catalog_size()
 registered=registry.count(dataset_version=dataset["version"])
 return {"catalog_size":total,"considered":considered,"created":created,"existing":existing,
         "registered_for_dataset":registered,"remaining_unregistered":max(0,total-registered),
         "exhausted":created==0 and considered==total,"completion":min(1.0,registered/total)}
