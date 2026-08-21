from xauusd.adaptive_search import AdaptiveSearch,BOUNDS,semantic_identity,mutation_analytics
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


def test_small_adaptive_batch_round_robins_families(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db")
 completed(registry,"mean_reversion",0,10); completed(registry,"momentum",1,1)
 report=AdaptiveSearch(registry,tmp_path/"adaptive.json").generate(DATASET,4)
 assert report["family_counts"]=={"mean_reversion":2,"momentum":2}


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


def test_mutation_analytics_measures_improvement_and_duplicates():
 rows=[{"id":1,"status":"completed","strategy_family":"momentum",
        "parameters":{"provenance":{"generator":"adaptive-search-v1","generation":2,"mutated_parameter":"fast",
        "multiplier":1.15,"parent_validation_score":1.0}},
        "validation":{"score":1.5,"passed":False,"gates":{"profit":True,"drawdown":False}}},
       {"id":2,"status":"completed","strategy_family":"momentum",
        "parameters":{"provenance":{"generator":"adaptive-search-v1","generation":2,"mutated_parameter":"slow",
        "multiplier":.85,"parent_validation_score":2.0}},
        "validation":{"score":1.0,"passed":False,"gates":{"profit":False,"drawdown":False}}}]
 report=mutation_analytics(rows,[{"created":3,"duplicates":2}])
 assert report["attempted"]==5 and report["duplicate_fraction"]==.4 and report["pending"]==1
 assert report["unmatched_completed"]==0
 assert report["completed"]==2 and report["improved"]==1 and report["improvement_rate"]==.5
 assert report["near_passes"]==1 and report["median_score_delta"]==-.25
 assert report["groups"]["parameter:fast"]["median_score_delta"]==.5


def test_adaptive_analyze_updates_existing_report(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db"); completed(registry,"momentum",0,2)
 row=registry.list("completed",1)[0]; parameters=row["parameters"]
 parameters["provenance"]={"generator":"adaptive-search-v1","generation":1,"mutated_parameter":"fast",
                           "multiplier":1.15,"parent_validation_score":1.0}
 with registry.connect() as db:
  db.execute("UPDATE experiments SET parameters_json=? WHERE id=?",(__import__('json').dumps(parameters),row["id"]))
 path=tmp_path/"adaptive.json"; path.write_text('{"generation":1}')
 history=tmp_path/"adaptive"; history.mkdir(); (history/"generation-0001.json").write_text('{"created":1,"duplicates":0}')
 report=AdaptiveSearch(registry,path).analyze()
 assert report["generation"]==1 and report["mutation_analytics"]["improved"]==1
 assert __import__('json').loads(path.read_text())["mutation_analytics"]["completed"]==1
