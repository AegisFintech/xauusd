from xauusd.core import synthetic_bars
from xauusd.experiment_registry import ExperimentRegistry
from xauusd.research import StrategySpec,build_features,generate_signal
from xauusd.strategy_proposals import ProposalEngine,novel_proposals


DATASET={"version":"v1","fingerprint":"abc","engine_version":"e1","cost_model_version":"c1"}


def test_novel_formulas_generate_valid_signals():
 features=build_features(synthetic_bars(1000,seed=101))
 for proposal in novel_proposals():
  signal=generate_signal(features,StrategySpec(proposal.family,proposal.strategy))
  assert signal.index.equals(features.index) and set(signal.unique()) <= {-1,0,1}


def test_proposal_engine_is_duplicate_safe_and_records_provenance(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db"); engine=ProposalEngine(registry,tmp_path/"proposals.json")
 first=engine.generate(DATASET,5); second=engine.generate(DATASET,5)
 assert first["created"]==5 and second["created"]==5
 assert registry.count(dataset_version="v1")==10
 row=registry.list(limit=1)[0]
 assert row["parameters"]["provenance"]["generator"]=="deterministic-novelty-v1"


def test_proposal_catalog_eventually_exhausts(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db"); engine=ProposalEngine(registry,tmp_path/"proposals.json")
 first=engine.generate(DATASET,1000); second=engine.generate(DATASET,1000)
 assert first["created"]==len(novel_proposals()) and second["exhausted"]
