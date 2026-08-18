from __future__ import annotations

from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json

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


class ShadowTradingReadiness:
 """Read-only readiness and shadow signals; incapable of submitting orders."""
 def __init__(self,registry: ExperimentRegistry | None=None,dataset: TournamentDataset | None=None,
              state_path=Path("reports/tournament/shadow/state.json"),stop_path=Path("reports/tournament/shadow/STOP"),
              limits: ShadowRiskLimits | None=None):
  self.registry=registry or ExperimentRegistry(); self.dataset=dataset or TournamentDataset()
  self.state_path=Path(state_path); self.stop_path=Path(stop_path); self.limits=limits or ShadowRiskLimits()

 def readiness(self) -> dict:
  manifest=self.dataset.active(); champion=self.registry.champion(manifest["version"])
  stopped=self.stop_path.exists()
  gates={"holdout_qualified_champion":champion is not None,"emergency_stop_clear":not stopped,
         "risk_limits_configured":all(value>0 for value in asdict(self.limits).values()),
         "execution_connector_absent":True,"explicit_activation":False}
  return {"ready":False,"mode":"shadow_only","gates":gates,"champion":champion,
          "limits":asdict(self.limits),"blocked_reason":"No execution capability is implemented; research-only contract enforced."}

 def emergency_stop(self,reason: str) -> dict:
  self.stop_path.parent.mkdir(parents=True,exist_ok=True)
  state={"stopped":True,"reason":reason,"stopped_at":datetime.now(timezone.utc).isoformat()}
  self.stop_path.write_text(json.dumps(state,indent=2)); return state

 def evaluate_signal(self,bars: pd.DataFrame) -> dict:
  readiness=self.readiness(); champion=readiness["champion"]
  if self.stop_path.exists(): return {**readiness,"signal":0,"status":"emergency_stopped"}
  if champion is None: return {**readiness,"signal":0,"status":"blocked_no_champion"}
  experiment=self.registry.get(champion["experiment_id"]); raw=experiment["parameters"]
  features=build_features(bars); spec=StrategySpec(experiment["strategy_family"],raw.get("strategy",raw))
  signal=int(generate_signal(features,spec).iloc[-1]) if not features.empty else 0
  age=(pd.Timestamp.now("UTC")-bars.index.max()).total_seconds()/60
  if age>self.limits.stale_data_minutes: signal=0
  state={"mode":"shadow_only","status":"observing" if signal else "flat","signal":signal,
         "evaluated_at":datetime.now(timezone.utc).isoformat(),"bar_time":bars.index.max().isoformat(),
         "data_age_minutes":age,"experiment_id":experiment["id"],"orders_submitted":0}
  self.state_path.parent.mkdir(parents=True,exist_ok=True); self.state_path.write_text(json.dumps(state,indent=2))
  return state
