from __future__ import annotations

import json
import os
import uuid
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
    run = uuid.uuid4().hex[:12]
    with psycopg.connect(url) as db:
        stage = f"catalog_stage_{run}"
        db.execute(f"CREATE UNLOGGED TABLE {stage} (LIKE experiments INCLUDING DEFAULTS)")
        now = datetime.now(timezone.utc).isoformat()
        columns = "fingerprint,strategy_family,formula,parameters_json,dataset_version,dataset_fingerprint,engine_version,cost_model_version,code_commit,status,priority,created_at"
        rows = []
        seen = created = 0
        def flush() -> None:
            nonlocal created
            if not rows: return
            with db.cursor() as cur:
                cur.executemany(f"INSERT INTO {stage} ({columns}) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)
            rows.clear()
        for strategy, execution in candidate_specs():
            base = from_strategy(strategy, dataset, commit)
            spec = ExperimentSpec(base.strategy_family, base.formula,
                {"strategy": strategy.parameters, "execution": execution},
                base.dataset_version, base.dataset_fingerprint, base.engine_version,
                base.cost_model_version, commit)
            rows.append((spec.fingerprint,spec.strategy_family,spec.formula,canonical_json(spec.parameters),spec.dataset_version,spec.dataset_fingerprint,spec.engine_version,spec.cost_model_version,spec.code_commit,"queued",0,now))
            seen += 1
            if len(rows) >= 2000: flush(); print("staged", seen, flush=True)
        flush()
        db.execute(f"CREATE TEMP TABLE new_catalog_ids (id BIGINT PRIMARY KEY) ON COMMIT DROP")
        db.execute(f"INSERT INTO experiments ({columns}) SELECT {columns} FROM {stage} ON CONFLICT (fingerprint) DO NOTHING RETURNING id")
        ids = db.fetchall()
        if ids:
            db.executemany("INSERT INTO new_catalog_ids (id) VALUES (%s)", ids)
            db.execute("INSERT INTO experiment_events (experiment_id,occurred_at,event,payload_json) SELECT id,%s,'registered',%s FROM new_catalog_ids", (now, json.dumps({"priority":0,"source":"bulk_catalog"}, separators=(",",":"))))
        created = len(ids)
        db.execute(f"DROP TABLE {stage}")
        db.commit()
        print(json.dumps({"catalog_size": catalog_size(), "considered": seen, "created": created}, indent=2))


if __name__ == "__main__": main()
