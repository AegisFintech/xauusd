from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
import socket
import time

import numpy as np
import pandas as pd

from .engine import EventDrivenBacktester, ExecutionConfig
from .experiment_registry import ExperimentRegistry
from .research import StrategySpec, build_features, generate_signal
from .tournament_data import TournamentDataset
from .search_space import replenish_catalog
from .validation import bootstrap_trade_paths
from .strategy_proposals import ProposalEngine
from .codex_workflow import CodexImprovementWorkflow
from .adaptive_search import AdaptiveSearch
from .portfolio_research import PortfolioResearch


@dataclass(frozen=True)
class TournamentGates:
    development_min_trades: int = 20
    validation_min_trades: int = 20
    min_profit_factor: float = 1.0
    min_expectancy: float = 0.0
    max_drawdown: float = -0.05
    walk_forward_folds: int = 4
    minimum_positive_folds: float = 0.75
    bootstrap_samples: int = 300
    maximum_bootstrap_loss_probability: float = 0.05


def _finite(value):
    if isinstance(value, dict):
        return {key: _finite(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_finite(item) for item in value]
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return None
    if isinstance(value, np.integer):
        return int(value)
    return value


class TournamentRunner:
    """Consume deterministic experiments without reading the holdout test set."""

    def __init__(self, registry: ExperimentRegistry | None = None,
                 dataset: TournamentDataset | None = None,
                 output_root: Path = Path("reports/tournament"),
                 gates: TournamentGates | None = None,
                 worker_id: str | None = None):
        self.registry = registry or ExperimentRegistry()
        self.dataset = dataset or TournamentDataset()
        self.output_root = output_root
        self.gates = gates or TournamentGates()
        self.worker_id = worker_id or f"{socket.gethostname()}-{os.getpid()}"

    @staticmethod
    def reconstruct(experiment: dict) -> tuple[StrategySpec, ExecutionConfig]:
        raw = experiment["parameters"] or {}
        strategy_parameters = raw.get("strategy", raw)
        execution_parameters = raw.get("execution", {})
        strategy = StrategySpec(experiment["strategy_family"], strategy_parameters)
        allowed = set(ExecutionConfig.__dataclass_fields__)
        execution = ExecutionConfig(**{key: value for key, value in execution_parameters.items() if key in allowed})
        return strategy, execution

    @staticmethod
    def score(metrics: dict) -> float:
        profit_factor = min(float(metrics["profit_factor"]), 3.0)
        return float(metrics["sharpe"] + 0.25 * profit_factor + 5 * metrics["max_drawdown"])

    def _backtest(self, partition: str, strategy: StrategySpec, execution: ExecutionConfig) -> dict:
        bars = self.dataset.read(partition)
        features = build_features(bars)
        if features.empty:
            raise ValueError(f"not enough {partition} bars to build features")
        return EventDrivenBacktester(execution).run(features, generate_signal(features, strategy))

    def _development_passed(self, metrics: dict) -> bool:
        return metrics["trades"] >= self.gates.development_min_trades

    def _validation(self, metrics: dict, result: dict | None = None,
                    features=None, strategy: StrategySpec | None = None,
                    execution: ExecutionConfig | None = None) -> dict:
        checks = {
            "minimum_trades": metrics["trades"] >= self.gates.validation_min_trades,
            "positive_expectancy": metrics["expectancy"] > self.gates.min_expectancy,
            "profit_factor": metrics["profit_factor"] > self.gates.min_profit_factor,
            "drawdown": metrics["max_drawdown"] >= self.gates.max_drawdown,
            "positive_net_profit": metrics["net_profit"] > 0,
        }
        report = {"passed": all(checks.values()), "gates": checks, "score": self.score(metrics),
                  "walk_forward": None, "bootstrap": None}
        if not report["passed"] or result is None or features is None or strategy is None or execution is None:
            return report
        folds=[]
        boundaries=np.linspace(0,len(features),self.gates.walk_forward_folds+1,dtype=int)
        for number in range(1,self.gates.walk_forward_folds+1):
            fold=features.iloc[boundaries[number-1]:boundaries[number]]
            fold_result=EventDrivenBacktester(execution).run(fold,generate_signal(fold,strategy))
            folds.append({"fold":number,"start":fold.index.min().isoformat(),"end":fold.index.max().isoformat(),
                          **_finite(fold_result["metrics"])})
        positive_fraction=float(np.mean([fold["net_profit"]>0 for fold in folds]))
        trades=result["trades"]
        bootstrap=bootstrap_trade_paths(trades.net_pnl if not trades.empty else pd.Series(dtype=float),
                                        self.gates.bootstrap_samples,seed=17)
        checks["walk_forward_consistency"]=positive_fraction>=self.gates.minimum_positive_folds
        checks["bootstrap_confidence"]=bootstrap["loss_probability"]<=self.gates.maximum_bootstrap_loss_probability and bootstrap["p05_net_pnl"]>0
        report.update({"passed":all(checks.values()),"walk_forward":{"folds":folds,
                       "positive_fold_fraction":positive_fraction},"bootstrap":_finite(bootstrap)})
        return report

    def _promote(self, experiment: dict, strategy: StrategySpec, execution: ExecutionConfig,
                 validation: dict, directory: Path) -> tuple[bool, dict | None, dict]:
        if not validation["passed"]:
            return False,None,{}
        previous=self.registry.champion(experiment["dataset_version"])
        if previous and float(previous["validation_score"]) >= validation["score"]:
            return False,None,{"eligible":False,"reason":"validation_score_not_better"}
        holdout=self._backtest("test",strategy,execution)
        holdout_validation=self._validation(holdout["metrics"])
        holdout_score=holdout_validation["score"]
        finalist={"eligible":True,"evaluated_at":datetime.now(timezone.utc).isoformat(),
                  "passed":holdout_validation["passed"],"score":holdout_score,
                  "gates":holdout_validation["gates"],"metrics":_finite(holdout["metrics"])}
        holdout["trades"].to_csv(directory/"holdout_trades.csv",index=False)
        holdout["equity"].to_frame().to_parquet(directory/"holdout_equity.parquet")
        if not finalist["passed"] or (previous and float(previous["holdout_score"])>=holdout_score):
            finalist["reason"]="holdout_gates_failed" if not finalist["passed"] else "holdout_score_not_better"
            return False,holdout,finalist
        self.registry.promote_champion(experiment["dataset_version"],experiment["id"],validation["score"],
                                       holdout_score,_finite(holdout["metrics"]))
        champion_dir=self.output_root/experiment["dataset_version"]
        champion_dir.mkdir(parents=True,exist_ok=True)
        path=champion_dir/"champion.json"
        champion = {"experiment_id": experiment["id"], "fingerprint": experiment["fingerprint"],
                    "strategy": strategy.name, "parameters": strategy.parameters,
                    "score": holdout_score, "validation_score":validation["score"],
                    "metrics": _finite(holdout["metrics"]),
                    "promoted_at": datetime.now(timezone.utc).isoformat()}
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(champion, indent=2, allow_nan=False))
        temporary.replace(path)
        return True,holdout,finalist

    def run_once(self) -> dict | None:
        experiment = self.registry.claim_next(self.worker_id)
        if experiment is None:
            return None
        directory = self.output_root / experiment["dataset_version"] / str(experiment["id"])
        directory.mkdir(parents=True, exist_ok=True)
        try:
            strategy, execution = self.reconstruct(experiment)
            development = self._backtest("train", strategy, execution)
            self.registry.heartbeat(experiment["id"], self.worker_id)
            validation_result = None
            validation = {"passed": False, "stage": "development",
                          "gates": {"minimum_trades": self._development_passed(development["metrics"])}}
            if self._development_passed(development["metrics"]):
                bars=self.dataset.read("validation")
                validation_features=build_features(bars)
                validation_result=EventDrivenBacktester(execution).run(
                    validation_features,generate_signal(validation_features,strategy))
                validation = {"stage": "validation", **self._validation(validation_result["metrics"],
                    validation_result,validation_features,strategy,execution)}
            result = validation_result or development
            result["trades"].to_csv(directory / "trades.csv", index=False)
            result["equity"].to_frame().to_parquet(directory / "equity.parquet")
            promoted,holdout,finalist = self._promote(experiment,strategy,execution,validation,directory)
            metrics = {"development": _finite(development["metrics"]),
                       "validation": _finite(validation_result["metrics"]) if validation_result else None,
                       "holdout":_finite(holdout["metrics"]) if holdout else None}
            validation["finalist"]=finalist
            summary = {"experiment_id": experiment["id"], "strategy": asdict(strategy),
                       "execution": asdict(execution), "metrics": metrics,
                       "validation": validation, "promoted": promoted}
            (directory / "summary.json").write_text(json.dumps(_finite(summary), indent=2, allow_nan=False))
            artifacts = {"directory": str(directory), "summary": str(directory / "summary.json"),
                         "trades": str(directory / "trades.csv"), "equity": str(directory / "equity.parquet")}
            if holdout:
                artifacts.update({"holdout_trades":str(directory/"holdout_trades.csv"),
                                  "holdout_equity":str(directory/"holdout_equity.parquet")})
            return self.registry.complete(experiment["id"], self.worker_id, metrics, validation, artifacts, promoted)
        except Exception as error:
            self.registry.fail(experiment["id"], self.worker_id, f"{type(error).__name__}: {error}",
                               {"directory": str(directory)})
            raise

    def run(self, count: int = 1) -> list[dict]:
        completed = []
        for _ in range(count):
            result = self.run_once()
            if result is None:
                break
            completed.append(result)
        return completed


class ContinuousTournamentWorker:
    def __init__(self, runner: TournamentRunner | None = None,
                 status_path: Path = Path("reports/tournament/worker-status.json"),
                 idle_seconds: float = 30, queue_floor: int = 100, replenish_size: int = 500):
        self.runner = runner or TournamentRunner()
        self.status_path = status_path
        self.idle_seconds = idle_seconds
        self.queue_floor = queue_floor
        self.replenish_size = replenish_size

    def _status(self, state: str, **details) -> None:
        self.status_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"state": state, "worker_id": self.runner.worker_id,
                   "updated_at": datetime.now(timezone.utc).isoformat(), **details}
        temporary = self.status_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(_finite(payload), indent=2, allow_nan=False))
        temporary.replace(self.status_path)

    def run_forever(self) -> None:
        replaced=self.runner.registry.recover_other_workers(self.runner.worker_id)
        self._status("starting",recovered_replaced_workers=replaced)
        while True:
            try:
                recovered=self.runner.registry.recover_stale(datetime.now(timezone.utc)-timedelta(minutes=10))
                queued=self.runner.registry.count("queued")
                replenishment=None
                adaptive=None
                completed=self.runner.registry.count("completed")
                adaptive_path=Path("reports/tournament/adaptive.json")
                if completed>=100 and not adaptive_path.exists():
                    adaptive=AdaptiveSearch(self.runner.registry).generate(self.runner.dataset.active(),50)
                portfolio_path=Path("reports/tournament/portfolio/latest.json")
                portfolio=None
                if completed>=150 and not portfolio_path.exists():
                    portfolio=PortfolioResearch(self.runner.registry,self.runner.dataset).run()
                if queued < self.queue_floor:
                    replenishment=replenish_catalog(self.runner.registry,self.runner.dataset.active(),self.replenish_size)
                    if replenishment["exhausted"]:
                        replenishment["novelty"]=ProposalEngine(self.runner.registry).generate(
                            self.runner.dataset.active(),self.replenish_size)
                        if replenishment["novelty"]["exhausted"]:
                            latest_path=Path("reports/tournament/codex/latest.json")
                            latest=json.loads(latest_path.read_text()) if latest_path.exists() else None
                            if latest is None:
                                replenishment["codex"]=CodexImprovementWorkflow(self.runner.registry).run(
                                    self.runner.dataset.active())
                self._status("running", recovered_stale=recovered,adaptive=adaptive,portfolio=portfolio)
                result = self.runner.run_once()
                if result is None:
                    self._status("idle", message="experiment catalog is exhausted", catalog=replenishment)
                    time.sleep(self.idle_seconds)
                else:
                    self._status("running", last_experiment_id=result["id"],
                                 last_result=result["status"], promoted=result["promoted"], catalog=replenishment)
            except KeyboardInterrupt:
                self._status("stopped")
                return
            except Exception as error:
                self._status("error", error=f"{type(error).__name__}: {error}")
                time.sleep(self.idle_seconds)
