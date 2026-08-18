from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import socket
import time

import numpy as np

from .engine import EventDrivenBacktester, ExecutionConfig
from .experiment_registry import ExperimentRegistry
from .research import StrategySpec, build_features, generate_signal
from .tournament_data import TournamentDataset


@dataclass(frozen=True)
class TournamentGates:
    development_min_trades: int = 20
    validation_min_trades: int = 20
    min_profit_factor: float = 1.0
    min_expectancy: float = 0.0
    max_drawdown: float = -0.05


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

    def _validation(self, metrics: dict) -> dict:
        checks = {
            "minimum_trades": metrics["trades"] >= self.gates.validation_min_trades,
            "positive_expectancy": metrics["expectancy"] > self.gates.min_expectancy,
            "profit_factor": metrics["profit_factor"] > self.gates.min_profit_factor,
            "drawdown": metrics["max_drawdown"] >= self.gates.max_drawdown,
            "positive_net_profit": metrics["net_profit"] > 0,
        }
        return {"passed": all(checks.values()), "gates": checks, "score": self.score(metrics)}

    def _promote(self, experiment: dict, strategy: StrategySpec, validation: dict, metrics: dict) -> bool:
        if not validation["passed"]:
            return False
        directory = self.output_root / experiment["dataset_version"]
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "champion.json"
        previous = json.loads(path.read_text()) if path.exists() else None
        if previous and float(previous["score"]) >= validation["score"]:
            return False
        champion = {"experiment_id": experiment["id"], "fingerprint": experiment["fingerprint"],
                    "strategy": strategy.name, "parameters": strategy.parameters,
                    "score": validation["score"], "metrics": _finite(metrics),
                    "promoted_at": datetime.now(timezone.utc).isoformat()}
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(champion, indent=2, allow_nan=False))
        temporary.replace(path)
        return True

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
                validation_result = self._backtest("validation", strategy, execution)
                validation = {"stage": "validation", **self._validation(validation_result["metrics"])}
            result = validation_result or development
            result["trades"].to_csv(directory / "trades.csv", index=False)
            result["equity"].to_frame().to_parquet(directory / "equity.parquet")
            metrics = {"development": _finite(development["metrics"]),
                       "validation": _finite(validation_result["metrics"]) if validation_result else None}
            promoted = self._promote(experiment, strategy, validation,
                                     validation_result["metrics"] if validation_result else development["metrics"])
            summary = {"experiment_id": experiment["id"], "strategy": asdict(strategy),
                       "execution": asdict(execution), "metrics": metrics,
                       "validation": validation, "promoted": promoted}
            (directory / "summary.json").write_text(json.dumps(_finite(summary), indent=2, allow_nan=False))
            artifacts = {"directory": str(directory), "summary": str(directory / "summary.json"),
                         "trades": str(directory / "trades.csv"), "equity": str(directory / "equity.parquet")}
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
                 idle_seconds: float = 30):
        self.runner = runner or TournamentRunner()
        self.status_path = status_path
        self.idle_seconds = idle_seconds

    def _status(self, state: str, **details) -> None:
        self.status_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"state": state, "worker_id": self.runner.worker_id,
                   "updated_at": datetime.now(timezone.utc).isoformat(), **details}
        temporary = self.status_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(_finite(payload), indent=2, allow_nan=False))
        temporary.replace(self.status_path)

    def run_forever(self) -> None:
        self._status("starting")
        while True:
            try:
                self._status("running")
                result = self.runner.run_once()
                if result is None:
                    self._status("idle", message="experiment queue is empty")
                    time.sleep(self.idle_seconds)
                else:
                    self._status("running", last_experiment_id=result["id"],
                                 last_result=result["status"], promoted=result["promoted"])
            except KeyboardInterrupt:
                self._status("stopped")
                return
            except Exception as error:
                self._status("error", error=f"{type(error).__name__}: {error}")
                time.sleep(self.idle_seconds)
