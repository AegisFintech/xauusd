from __future__ import annotations

from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json
import math

import pandas as pd

from .experiment_registry import ExperimentRegistry
from .research import StrategySpec,build_features,generate_signal
from .tournament_data import TournamentDataset


@dataclass(frozen=True)
class ShadowRiskLimits:
 max_daily_loss: float=50.0
 max_drawdown: float=.02
 max_position_oz: float=1.0
 max_trades_per_day: int=100
 stale_data_minutes: int=15

 def validate(self) -> None:
  values=asdict(self)
  if any(not isinstance(value,(int,float)) or isinstance(value,bool) or not math.isfinite(value) or value<=0
         for value in values.values()):
   raise ValueError("shadow risk limits must be finite positive numbers")
  if self.max_drawdown>1:
   raise ValueError("max_drawdown must be between zero and one")
  if not float(self.max_trades_per_day).is_integer():
   raise ValueError("max_trades_per_day must be a whole number")


class ShadowTradingReadiness:
 """Read-only readiness and shadow signals; incapable of submitting orders."""
 def __init__(self,registry: ExperimentRegistry | None=None,dataset: TournamentDataset | None=None,
              state_path=Path("reports/tournament/shadow/state.json"),stop_path=Path("reports/tournament/shadow/STOP"),
              audit_path=Path("reports/tournament/shadow/audit.jsonl"),alert_path=Path("reports/tournament/shadow/alert.json"),
              limits: ShadowRiskLimits | None=None):
  self.registry=registry or ExperimentRegistry(); self.dataset=dataset or TournamentDataset()
  self.state_path=Path(state_path); self.stop_path=Path(stop_path); self.audit_path=Path(audit_path); self.alert_path=Path(alert_path)
  self.limits=limits or ShadowRiskLimits(); self.limits.validate()

 def _write_json(self,path: Path,payload: dict) -> None:
  path.parent.mkdir(parents=True,exist_ok=True)
  temporary=path.with_suffix(f"{path.suffix}.tmp")
  temporary.write_text(json.dumps(payload,indent=2,allow_nan=False))
  temporary.replace(path)

 def _record(self,state: dict,alert: bool=False) -> dict:
  self._write_json(self.state_path,state)
  self.audit_path.parent.mkdir(parents=True,exist_ok=True)
  with self.audit_path.open("a") as audit:
   audit.write(json.dumps(state,allow_nan=False,sort_keys=True)+"\n")
  if alert: self._write_json(self.alert_path,state)
  return state

 def readiness(self) -> dict:
  manifest=self.dataset.active(); champion=self.registry.champion(manifest["version"])
  stopped=self.stop_path.exists()
  gates={"holdout_qualified_champion":champion is not None,"emergency_stop_clear":not stopped,
         "risk_limits_configured":all(value>0 for value in asdict(self.limits).values()),
         "execution_connector_absent":True,"explicit_activation":False}
  return {"ready":False,"mode":"shadow_only","gates":gates,"champion":champion,
          "limits":asdict(self.limits),"blocked_reason":"No execution capability is implemented; research-only contract enforced."}

 def emergency_stop(self,reason: str) -> dict:
  if not reason.strip(): raise ValueError("emergency stop reason is required")
  state={"stopped":True,"reason":reason,"stopped_at":datetime.now(timezone.utc).isoformat()}
  self._write_json(self.stop_path,state)
  return self._record({"mode":"shadow_only","status":"emergency_stopped","signal":0,**state},alert=True)

 def _flat(self,status: str,reason: str,alert: bool=True) -> dict:
  return self._record({"mode":"shadow_only","status":status,"signal":0,
                       "reason":reason,"evaluated_at":datetime.now(timezone.utc).isoformat(),"orders_submitted":0},alert)

 def evaluate_signal(self,bars: pd.DataFrame) -> dict:
  readiness=self.readiness(); champion=readiness["champion"]
  if self.stop_path.exists(): return self._record({**readiness,"signal":0,"status":"emergency_stopped","orders_submitted":0},alert=True)
  if champion is None: return {**readiness,"signal":0,"status":"blocked_no_champion"}
  if bars.empty: return self._flat("flat_no_data","no bars available")
  if not isinstance(bars.index,pd.DatetimeIndex) or bars.index.tz is None:
   return self._flat("flat_invalid_data","bars must use a timezone-aware DatetimeIndex")
  try:
   experiment=self.registry.get(champion["experiment_id"]); raw=experiment["parameters"]
   features=build_features(bars); spec=StrategySpec(experiment["strategy_family"],raw.get("strategy",raw))
   signal=int(generate_signal(features,spec).iloc[-1]) if not features.empty else 0
   age=(pd.Timestamp.now("UTC")-bars.index.max()).total_seconds()/60
  except Exception as error:
   return self._flat("flat_evaluation_failed",str(error))
  if age>self.limits.stale_data_minutes:
   return self._flat("flat_stale_data",f"data age {age:.2f} minutes exceeds limit",alert=True)
  state={"mode":"shadow_only","status":"observing" if signal else "flat","signal":signal,
          "evaluated_at":datetime.now(timezone.utc).isoformat(),"bar_time":bars.index.max().isoformat(),
          "data_age_minutes":age,"experiment_id":experiment["id"],"orders_submitted":0}
  return self._record(state)
