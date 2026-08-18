from pathlib import Path

import pandas as pd

from xauusd.core import synthetic_bars
from xauusd.experiment_registry import ExperimentRegistry, ExperimentSpec
from xauusd.tournament_data import TournamentDataConfig, TournamentDataset
from xauusd.tournament_runner import ContinuousTournamentWorker, TournamentGates, TournamentRunner


def setup_runner(tmp_path, parameters, gates=None):
    dataset = TournamentDataset(TournamentDataConfig(root=tmp_path/"data", active_path=tmp_path/"active.json", days=30))
    manifest = dataset.create(synthetic_bars(60*24*40, seed=91))
    registry = ExperimentRegistry(tmp_path/"registry.sqlite3")
    spec = ExperimentSpec("momentum", "formula", parameters, manifest["version"], manifest["fingerprint"],
                          manifest["engine_version"], manifest["cost_model_version"])
    row, _ = registry.register(spec)
    runner = TournamentRunner(registry, dataset, tmp_path/"reports", gates=gates)
    return runner, registry, row


def test_worker_completes_and_writes_artifacts_without_test_partition(tmp_path, monkeypatch):
    parameters={"strategy":{"fast":8,"slow":34,"threshold_atr":.1},
                "execution":{"stop_distance":2,"target_distance":3,"max_holding_bars":30}}
    runner,registry,row=setup_runner(tmp_path,parameters,TournamentGates(1,1,-1,-999,-1))
    original=runner.dataset.read; reads=[]
    def guarded(partition):
        reads.append(partition)
        assert partition != "test"
        return original(partition)
    monkeypatch.setattr(runner.dataset,"read",guarded)
    result=runner.run_once()
    assert result["status"]=="completed" and set(reads) <= {"train","validation"}
    assert Path(result["artifacts"]["summary"]).exists()
    assert registry.events(row["id"])[-1]["event"]=="completed"


def test_legacy_flat_parameters_are_reconstructed(tmp_path):
    runner,_,_=setup_runner(tmp_path,{"fast":8,"slow":34,"threshold_atr":.1})
    strategy,execution=runner.reconstruct(runner.registry.list()[0])
    assert strategy.parameters["fast"]==8 and execution.stop_distance==2


def test_failure_is_durable(tmp_path, monkeypatch):
    runner,registry,row=setup_runner(tmp_path,{"strategy":{"bad":1}})
    monkeypatch.setattr(runner,"_backtest",lambda *args: (_ for _ in ()).throw(RuntimeError("boom")))
    try: runner.run_once()
    except RuntimeError: pass
    assert registry.get(row["id"])["status"]=="failed"


def test_continuous_worker_records_idle_heartbeat(tmp_path, monkeypatch):
    class EmptyRunner:
        worker_id="worker-test"
        class Registry:
            def count(self,status): return 100 if status=="queued" else 0
            def recover_stale(self,before): return 0
            def recover_other_workers(self,worker): return 0
        registry=Registry()
        def run_once(self): return None
    worker=ContinuousTournamentWorker(EmptyRunner(),tmp_path/"status.json",.01)
    monkeypatch.setattr("xauusd.tournament_runner.time.sleep",lambda _: (_ for _ in ()).throw(KeyboardInterrupt()))
    worker.run_forever()
    status=__import__("json").loads((tmp_path/"status.json").read_text())
    assert status["state"]=="stopped" and status["worker_id"]=="worker-test"


def test_robust_validation_adds_walk_forward_and_bootstrap(tmp_path):
    parameters={"strategy":{"fast":8,"slow":34,"threshold_atr":.1},"execution":{}}
    gates=TournamentGates(1,1,-1,-999,-1,walk_forward_folds=2,minimum_positive_folds=0,
                          bootstrap_samples=20,maximum_bootstrap_loss_probability=1)
    runner,_,_=setup_runner(tmp_path,parameters,gates)
    strategy,execution=runner.reconstruct(runner.registry.list()[0])
    bars=runner.dataset.read("validation"); features=__import__("xauusd.research",fromlist=["build_features"]).build_features(bars)
    result=__import__("xauusd.engine",fromlist=["EventDrivenBacktester"]).EventDrivenBacktester(execution).run(
        features,__import__("xauusd.research",fromlist=["generate_signal"]).generate_signal(features,strategy))
    metrics={**result["metrics"],"net_profit":1,"expectancy":1,"profit_factor":2,"max_drawdown":0}
    report=runner._validation(metrics,result,features,strategy,execution)
    assert len(report["walk_forward"]["folds"])==2 and report["bootstrap"]["samples"]==20
