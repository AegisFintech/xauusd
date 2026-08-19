from xauusd.core import synthetic_bars
from xauusd.experiment_registry import ExperimentRegistry
from xauusd.research import StrategySpec,build_features,generate_signal
from xauusd.search_space import candidate_specs,catalog_size,replenish_catalog,seed_catalog


DATASET={"version":"v1","fingerprint":"abc","engine_version":"e1","cost_model_version":"c1"}


def test_catalog_is_deterministic_and_valid():
 first=list(candidate_specs()); second=list(candidate_specs())
 assert first==second and len(first)==catalog_size() and 45_000 < len(first) < 55_000
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


def test_quantitative_families_are_causal_and_generate_scenarios():
 features=build_features(synthetic_bars(2000,seed=71))
 scenarios=(
  StrategySpec("autocorrelation_regime",{"corr_window":20,"lag":1,"threshold":.05,"return_period":1}),
  StrategySpec("multi_horizon_momentum",{"fast_period":3,"slow_period":15,"threshold_atr":.05}),
  StrategySpec("quantile_reversion",{"window":20,"entry_quantile":.1,"exit_quantile":.5}),
  StrategySpec("volatility_adjusted_trend",{"return_period":5,"vol_window":30,"threshold":.5}),
 )
 for spec in scenarios:
  signal=generate_signal(features,spec)
  assert signal.index.equals(features.index) and set(signal.dropna().unique()) <= {-1,0,1}


def test_session_momentum_warmup_is_flat_not_an_integer_cast_error():
 features=build_features(synthetic_bars(1000,seed=72))
 signal=generate_signal(features,StrategySpec("session_momentum",
  {"start_hour":0,"end_hour":20,"return_period":30,"direction":"both"}))
 assert signal.iloc[:30].eq(0).all()


def test_replenishment_scans_past_existing_prefix(tmp_path):
 registry=ExperimentRegistry(tmp_path/"x.db"); seed_catalog(registry,DATASET,limit=10)
 result=replenish_catalog(registry,DATASET,target_new=5)
 assert result["created"]==5 and registry.count(dataset_version="v1")==15
