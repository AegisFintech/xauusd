from __future__ import annotations

import json
import os
import random
import time
from datetime import datetime, timezone

import psycopg
from dotenv import load_dotenv

from xauusd.experiment_registry import ExperimentSpec, canonical_json, from_strategy
from xauusd.search_space import candidate_specs, catalog_size
from xauusd.tournament_data import TournamentDataset


def main() -> None:
    load_dotenv(".env")
    url = os.environ["DATABASE_URL_DIRECT"]
    dataset = TournamentDataset().active()
    commit = os.popen("git rev-parse HEAD").read().strip() or None
    with psycopg.connect(url) as db:
        existing={row[0] for row in db.execute("SELECT fingerprint FROM experiments")}
        now = datetime.now(timezone.utc).isoformat()
        columns = "fingerprint,strategy_family,formula,parameters_json,dataset_version,dataset_fingerprint,engine_version,cost_model_version,code_commit,status,priority,created_at"
        rows = []
        seen = created = 0
        def flush() -> None:
            nonlocal created
            if not rows: return
            for attempt in range(5):
                try:
                    ids=[]
                    for row in rows:
                        result=db.execute(
                            f"INSERT INTO experiments ({columns}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                            "ON CONFLICT (fingerprint) DO NOTHING RETURNING id",row).fetchone()
                        if result: ids.append(result[0])
                    if ids:
                        payload=json.dumps({"priority":0,"source":"bulk_catalog"},separators=(",",":"))
                        with db.cursor() as cur:
                            cur.executemany(
                                "INSERT INTO experiment_events (experiment_id,occurred_at,event,payload_json) VALUES (%s,%s,'registered',%s)",
                                ((experiment_id,now,payload) for experiment_id in ids))
                    db.commit()
                    break
                except psycopg.errors.SerializationFailure:
                    db.rollback()
                    if attempt == 4: raise
                    delay=min(8.0,.5*(2**attempt))+random.uniform(0,.5)
                    print("serialization_retry",attempt+1,round(delay,2),flush=True)
                    time.sleep(delay)
            created += len(ids)
            rows.clear()
        for strategy, execution in candidate_specs():
            base = from_strategy(strategy, dataset, commit)
            spec = ExperimentSpec(base.strategy_family, base.formula,
                {"strategy": strategy.parameters, "execution": execution},
                base.dataset_version, base.dataset_fingerprint, base.engine_version,
                base.cost_model_version, commit)
            seen += 1
            if spec.fingerprint in existing: continue
            existing.add(spec.fingerprint)
            rows.append((spec.fingerprint,spec.strategy_family,spec.formula,canonical_json(spec.parameters),spec.dataset_version,spec.dataset_fingerprint,spec.engine_version,spec.cost_model_version,spec.code_commit,"queued",0,now))
            if len(rows) >= 2000: flush(); print("seeded",seen,created,flush=True)
        flush()
        print(json.dumps({"catalog_size": catalog_size(), "considered": seen, "created": created}, indent=2))


if __name__ == "__main__": main()
