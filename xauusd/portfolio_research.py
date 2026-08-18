from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .experiment_registry import ExperimentRegistry
from .research import build_features
from .tournament_data import TournamentDataset


def classify_regimes(features: pd.DataFrame) -> pd.Series:
    """Causal labels using expanding historical thresholds, never future quantiles."""
    volatility=features["atr_14"]/features["close"]
    vol_threshold=volatility.expanding(min_periods=500).median().shift(1)
    trend_threshold=features["trend_strength"].expanding(min_periods=500).median().shift(1)
    volatility_label=np.where(volatility>vol_threshold,"high_vol","low_vol")
    trend_label=np.where(features["trend_strength"]>trend_threshold,"trend","range")
    session=np.where(features.index.hour<7,"asia",np.where(features.index.hour<13,"london","new_york"))
    return pd.Series([f"{a}|{b}|{c}" for a,b,c in zip(trend_label,volatility_label,session)],index=features.index,name="regime")


def equity_metrics(equity: pd.Series) -> dict:
    returns=equity.pct_change().fillna(0); drawdown=equity/equity.cummax()-1; downside=returns[returns<0]
    scale=np.sqrt(252*1440)
    return {"initial_equity":float(equity.iloc[0]),"final_equity":float(equity.iloc[-1]),
            "net_profit":float(equity.iloc[-1]-equity.iloc[0]),
            "sharpe":float(scale*returns.mean()/returns.std()) if returns.std() else 0.,
            "sortino":float(scale*returns.mean()/downside.std()) if len(downside)>1 and downside.std() else 0.,
            "max_drawdown":float(drawdown.min())}


class PortfolioResearch:
    def __init__(self,registry: ExperimentRegistry | None=None,dataset: TournamentDataset | None=None,
                 output_root: Path=Path("reports/tournament/portfolio")):
        self.registry=registry or ExperimentRegistry(); self.dataset=dataset or TournamentDataset(); self.output_root=output_root

    def _diverse_leaders(self,per_family=1,limit=5):
        selected=[]; counts=defaultdict(int)
        for row in self.registry.leaderboard(500):
            if counts[row["strategy_family"]]>=per_family or not (row.get("artifacts") or {}).get("equity"): continue
            selected.append(row); counts[row["strategy_family"]]+=1
            if len(selected)>=limit: break
        return selected

    def run(self) -> dict:
        leaders=self._diverse_leaders()
        if len(leaders)<2: return {"status":"insufficient_diversity","strategies":len(leaders)}
        features=build_features(self.dataset.read("validation")); regimes=classify_regimes(features)
        curves=[]; strategy_reports=[]
        for row in leaders:
            equity=pd.read_parquet(row["artifacts"]["equity"]).iloc[:,0].sort_index()
            trades=pd.read_csv(row["artifacts"]["trades"],parse_dates=["exit_time"],compression="infer")
            exit_times=pd.DatetimeIndex(trades.exit_time); labels=regimes.reindex(exit_times,method="ffill").to_numpy()
            trades["regime"]=labels
            by_regime=[]
            for name,group in trades.groupby("regime"):
                profits=group.net_pnl[group.net_pnl>0].sum(); losses=-group.net_pnl[group.net_pnl<0].sum()
                by_regime.append({"regime":name,"trades":len(group),"net_profit":float(group.net_pnl.sum()),
                                  "expectancy":float(group.net_pnl.mean()),
                                  "profit_factor":float(profits/losses) if losses else None})
            strategy_reports.append({"experiment_id":row["id"],"family":row["strategy_family"],
                                     "validation_score":row["validation"].get("score"),"regimes":by_regime})
            curves.append(equity/equity.iloc[0])
        aligned=pd.concat(curves,axis=1,join="inner").dropna()
        weights=[1/len(curves)]*len(curves); portfolio=100000*(aligned*weights).sum(axis=1)
        metrics=equity_metrics(portfolio)
        average_exposure=float(np.mean([(row.get("metrics") or {}).get("validation",{}).get("exposure",0) for row in leaders]))
        gates={"positive_net_profit":metrics["net_profit"]>0,"positive_sharpe":metrics["sharpe"]>0,
               "maximum_drawdown":metrics["max_drawdown"]>=-.05,"maximum_average_exposure":average_exposure<=1.0,
               "strategy_diversity":len({row["strategy_family"] for row in leaders})>=2}
        self.output_root.mkdir(parents=True,exist_ok=True); portfolio.rename("equity").to_frame().to_parquet(self.output_root/"equity.parquet")
        report={"status":"completed","partition":"validation","holdout_used":False,
                "experiment_ids":[row["id"] for row in leaders],"weights":weights,
                "average_exposure":average_exposure,"metrics":metrics,"gates":gates,"passed":all(gates.values()),
                "strategies":strategy_reports,"equity":str(self.output_root/"equity.parquet")}
        temporary=(self.output_root/"latest.json.tmp"); temporary.write_text(json.dumps(report,indent=2,allow_nan=False)); temporary.replace(self.output_root/"latest.json")
        return report
