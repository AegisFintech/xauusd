from __future__ import annotations

import os
import sqlite3
import csv
import io
import uuid
import psycopg
from dotenv import load_dotenv


def main() -> None:
    load_dotenv(".env")
    url=os.environ.get("DATABASE_URL_DIRECT") or os.environ["DATABASE_URL"]
    # The rebuild requires one stable PostgreSQL session. Prefer the explicitly
    # supplied direct Neon endpoint; fall back to a non-pooler derivation only
    # for older deployments that do not define DATABASE_URL_DIRECT.
    if not os.environ.get("DATABASE_URL_DIRECT"):
        url=url.replace("-pooler.", ".", 1)
    target_url=url
    source=sqlite3.connect(os.getenv("SQLITE_REGISTRY","data/experiments/registry.sqlite3")); source.row_factory=sqlite3.Row
    with psycopg.connect(target_url) as target:
        target.execute("""CREATE TABLE IF NOT EXISTS experiments (id BIGSERIAL PRIMARY KEY,fingerprint TEXT NOT NULL UNIQUE,
          strategy_family TEXT NOT NULL,formula TEXT NOT NULL,parameters_json TEXT NOT NULL,dataset_version TEXT NOT NULL,
          dataset_fingerprint TEXT NOT NULL,engine_version TEXT NOT NULL,cost_model_version TEXT NOT NULL,code_commit TEXT,
          status TEXT NOT NULL CHECK(status IN ('queued','running','completed','failed','cancelled')),priority INTEGER NOT NULL DEFAULT 0,
          worker_id TEXT,created_at TEXT NOT NULL,started_at TEXT,finished_at TEXT,heartbeat_at TEXT,metrics_json TEXT,validation_json TEXT,
          artifacts_json TEXT,error TEXT,promoted INTEGER NOT NULL DEFAULT 0 CHECK(promoted IN (0,1)),retry_count INTEGER NOT NULL DEFAULT 0,failure_code TEXT)""")
        target.execute("""CREATE TABLE IF NOT EXISTS experiment_events (id BIGSERIAL PRIMARY KEY,experiment_id BIGINT NOT NULL REFERENCES experiments(id),occurred_at TEXT NOT NULL,event TEXT NOT NULL,payload_json TEXT)""")
        target.execute("""CREATE TABLE IF NOT EXISTS champion_history (id BIGSERIAL PRIMARY KEY,dataset_version TEXT NOT NULL,experiment_id BIGINT NOT NULL REFERENCES experiments(id),previous_experiment_id BIGINT REFERENCES experiments(id),promoted_at TEXT NOT NULL,validation_score DOUBLE PRECISION NOT NULL,holdout_score DOUBLE PRECISION NOT NULL,holdout_metrics_json TEXT NOT NULL)""")
        # Rebuild the target registry from the authoritative SQLite snapshot. This
        # prevents stale partial migrations from remapping IDs and breaking event FKs.
        target.execute("TRUNCATE champion_history, experiment_events, experiments RESTART IDENTITY CASCADE")
        target.commit()
        schemas={"experiments":["id","fingerprint","strategy_family","formula","parameters_json","dataset_version","dataset_fingerprint","engine_version","cost_model_version","code_commit","status","priority","worker_id","created_at","started_at","finished_at","heartbeat_at","metrics_json","validation_json","artifacts_json","error","promoted","retry_count","failure_code"],"experiment_events":["id","experiment_id","occurred_at","event","payload_json"],"champion_history":["id","dataset_version","experiment_id","previous_experiment_id","promoted_at","validation_score","holdout_score","holdout_metrics_json"]}
        for table,columns in schemas.items():
            staging=f"migration_{table}_{uuid.uuid4().hex[:12]}"
            target.execute(f"CREATE UNLOGGED TABLE {staging} (LIKE {table} INCLUDING DEFAULTS)")
            target.commit()
            rows=source.execute(f"SELECT {','.join(columns)} FROM {table}")
            count=0
            while batch := rows.fetchmany(2_000):
                buffer=io.StringIO()
                writer=csv.writer(buffer,lineterminator="\n")
                for row in batch:
                    writer.writerow(tuple("\\N" if row[column] is None else row[column] for column in columns))
                with target.cursor() as cursor:
                    with cursor.copy(
                        f"COPY {staging} ({','.join(columns)}) FROM STDIN "
                        "WITH (FORMAT CSV, NULL '\\N')"
                    ) as copy:
                        copy.write(buffer.getvalue())
                    cursor.execute(
                        f"INSERT INTO {table} ({','.join(columns)}) "
                        f"SELECT {','.join(columns)} FROM {staging}"
                    )
                    cursor.execute(f"TRUNCATE {staging}")
                target.commit()
                count += len(batch)
                print(table,count,flush=True)
            print(table,count,flush=True)
            target.execute(f"DROP TABLE {staging}")
            target.commit()
        for table in schemas: target.execute(f"SELECT setval(pg_get_serial_sequence('{table}','id'),COALESCE((SELECT max(id) FROM {table}),1),true)")
        target.commit()
        for table in schemas: print("postgres",table,target.execute(f"SELECT count(*) FROM {table}").fetchone()[0],flush=True)


if __name__=="__main__": main()
