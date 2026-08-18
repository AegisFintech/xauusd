from xauusd.adaptive_search import AdaptiveSearch,BOUNDS,semantic_identity
from xauusd.experiment_registry import ExperimentRegistry,ExperimentSpec


DATASET={"version":"v1","fingerprint":"abc","engine_version":"e1","cost_model_version":"c1"}


def completed(registry,family,value,score):
 parameters={"strategy":{"fast":5+value,"slow":34,"threshold_atr":.1},
             "execution":{"stop_distance":2.5,"target_distance":4.,"max_holding_bars":30}}
 row,_=registry.register(ExperimentSpec(family,"formula",parameters,"v1","abc","e1","c1"))
 claimed=registry.claim_next("w"); registry.complete(claimed["id"],"w",{"validation":{"net_profit":score}},
                                                     {"passed":score>0,"score":score})
 return row


def test_adaptive_search_creates_bounded_lineage(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db")
 parent=completed(registry,"momentum",0,2.0)
 report=AdaptiveSearch(registry,tmp_path/"adaptive.json").generate(DATASET,5)
 assert report["created"]==5
 for row in registry.list(limit=5):
  provenance=row["parameters"]["provenance"]
  assert provenance["parent_experiment_ids"]==[parent["id"]]
  key=provenance["mutated_parameter"]
  value=row["parameters"]["strategy"].get(key,row["parameters"]["execution"].get(key))
  if key in BOUNDS: assert BOUNDS[key][0] <= value <= BOUNDS[key][1]


def test_adaptive_search_preserves_family_exploration(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db")
 completed(registry,"momentum",0,10); completed(registry,"micro_trend",1,1)
 report=AdaptiveSearch(registry,tmp_path/"adaptive.json").generate(DATASET,50)
 assert set(report["family_counts"])=={"micro_trend","momentum"}


def test_semantic_identity_ignores_provenance():
 base={"strategy":{"fast":5},"execution":{"stop_distance":2}}
 with_lineage={**base,"provenance":{"parent_experiment_ids":[1]}}
 assert semantic_identity("momentum",base)==semantic_identity("momentum",with_lineage)


def test_adaptive_generation_walks_past_duplicates(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db"); completed(registry,"momentum",0,2)
 engine=AdaptiveSearch(registry,tmp_path/"adaptive.json")
 first=engine.generate(DATASET,3); second=engine.generate(DATASET,3)
 assert first["created"]==3 and second["created"]==3 and second["duplicates"]>=3
 assert first["generation"]==1 and second["generation"]==2
 assert (tmp_path/"adaptive"/"generation-0001.json").exists()
 assert (tmp_path/"adaptive"/"generation-0002.json").exists()
 rows=[x for x in registry.list(limit=20) if x["parameters"].get("provenance")]
 assert {x["parameters"]["provenance"]["generation"] for x in rows}=={1,2}
