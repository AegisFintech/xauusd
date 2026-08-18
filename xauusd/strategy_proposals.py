from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from .experiment_registry import ExperimentRegistry, ExperimentSpec


GENERATOR_VERSION="deterministic-novelty-v1"


@dataclass(frozen=True)
class Proposal:
    family: str
    formula: str
    strategy: dict
    execution: dict
    rationale: str


def novel_proposals() -> list[Proposal]:
    proposals=[]
    execution_options=(
        {"stop_distance":1.5,"target_distance":3.0,"max_holding_bars":20},
        {"stop_distance":2.5,"target_distance":4.0,"max_holding_bars":30},
        {"stop_distance":4.0,"target_distance":6.0,"max_holding_bars":60},
    )
    for fast,slow,strength,pullback,direction in (
        (5,34,.20,.75,"both"),(8,50,.35,1.0,"both"),(5,20,.15,.60,"long"),(5,20,.15,.60,"short")):
        for execution in execution_options:
            proposals.append(Proposal("trend_pullback",
                "trend(ema_fast,ema_slow) confirmed by strength; enter counter-move zscore pullback",
                {"fast":fast,"slow":slow,"min_strength":strength,"pullback_z":pullback,"direction":direction},
                execution,"Combine persistent trend direction with discounted pullback entries."))
    for lookback,strength,range_ratio,direction in (
        (20,.20,1.1,"both"),(40,.35,1.25,"both"),(60,.50,1.5,"both"),(30,.25,1.2,"long"),(30,.25,1.2,"short")):
        for execution in execution_options:
            proposals.append(Proposal("confirmed_breakout",
                "channel breakout confirmed by EMA/ATR trend strength and range expansion",
                {"lookback":lookback,"min_strength":strength,"range_ratio":range_ratio,"direction":direction},
                execution,"Filter noisy channel breaks using trend and volatility confirmation."))
    return proposals


class ProposalEngine:
    def __init__(self,registry: ExperimentRegistry,output_path: Path=Path("reports/tournament/proposals.json")):
        self.registry=registry; self.output_path=output_path

    def generate(self,dataset: dict,limit: int=100) -> dict:
        leaders=self.registry.leaderboard(10)
        parents=[{"id":row["id"],"family":row["strategy_family"],"score":row["validation"].get("score")}
                 for row in leaders]
        created=[]; duplicates=0
        for proposal in novel_proposals():
            parameters={"strategy":proposal.strategy,"execution":proposal.execution,
                        "provenance":{"generator":GENERATOR_VERSION,"rationale":proposal.rationale,
                                      "parent_experiment_ids":[row["id"] for row in parents]}}
            spec=ExperimentSpec(proposal.family,proposal.formula,parameters,dataset["version"],dataset["fingerprint"],
                                dataset["engine_version"],dataset["cost_model_version"])
            row,is_new=self.registry.register(spec,priority=10)
            if is_new:
                created.append({"experiment_id":row["id"],"family":proposal.family,"formula":proposal.formula,
                                "parameters":parameters,"rationale":proposal.rationale})
            else: duplicates+=1
            if len(created)>=limit: break
        report={"generator_version":GENERATOR_VERSION,"dataset_version":dataset["version"],"parents":parents,
                "available_proposals":len(novel_proposals()),"created":len(created),"duplicates":duplicates,
                "exhausted":len(created)==0,"proposals":created}
        self.output_path.parent.mkdir(parents=True,exist_ok=True)
        temporary=self.output_path.with_suffix(".json.tmp"); temporary.write_text(json.dumps(report,indent=2))
        temporary.replace(self.output_path)
        return report
