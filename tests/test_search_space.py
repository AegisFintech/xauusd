from xauusd.core import synthetic_bars
from xauusd.experiment_registry import ExperimentRegistry
from xauusd.research import StrategySpec,build_features,generate_signal
from xauusd.search_space import candidate_specs,catalog_size,seed_catalog


DATASET={"version":"v1","fingerprint":"abc","engine_version":"e1","cost_model_version":"c1"}


def test_catalog_is_deterministic_and_valid():
 first=list(candidate_specs()); second=list(candidate_specs())
 assert first==second and len(first)==catalog_size() and len(first)>1000
 assert all(s.parameters.get("fast",0)<s.parameters.get("slow",10**9) for s,_ in first)


def test_catalog_seeding_is_batched_and_duplicate_safe(tmp_path):
 registry=ExperimentRegistry(tmp_path/"x.db")
 one=seed_catalog(registry,DATASET,"commit",limit=25); two=seed_catalog(registry,DATASET,"commit",limit=25)
 assert one["created"]==25 and two["created"]==0 and two["existing"]==25


def test_dynamic_parameters_change_signal():
 features=build_features(synthetic_bars(1000,seed=61))
 a=generate_signal(features,StrategySpec("momentum",{"fast":5,"slow":20,"threshold_atr":.1}))
 b=generate_signal(features,StrategySpec("momentum",{"fast":12,"slow":50,"threshold_atr":.5}))
 assert not a.equals(b)
