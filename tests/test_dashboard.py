import json

import pandas as pd
from fastapi.testclient import TestClient

import xauusd.dashboard as dashboard


def setup_files(tmp_path):
    reports=tmp_path/"reports"; run=reports/"automation"/"run-1"; research=run/"research"; research.mkdir(parents=True)
    candidate={"strategy":"mean_reversion","score":-1.0,"net_profit":-10.0,"profit_factor":.8,
               "max_drawdown":-.01,"passed":False}
    manifest={"run_id":"run-1","created_at":"2026-01-01T00:00:00+00:00","data":{"rows":3},
              "promotion":{"promoted":False},"candidates":[candidate]}
    (run/"manifest.json").write_text(json.dumps(manifest))
    (reports/"automation"/"latest.json").write_text(json.dumps({"path":str(run)}))
    index=pd.date_range(pd.Timestamp.now("UTC")-pd.Timedelta(minutes=2),periods=3,freq="min")
    data=tmp_path/"bars.parquet"; pd.DataFrame({"close":[1,2,3]},index=index).to_parquet(data)
    pd.DataFrame({"equity":[100,101,99]},index=index).to_parquet(research/"mean_reversion_equity.parquet")
    return reports,data


def test_health_is_public_but_api_can_require_auth(tmp_path,monkeypatch):
    reports,data=setup_files(tmp_path); monkeypatch.setattr(dashboard,"REPORTS",reports); monkeypatch.setattr(dashboard,"DATA_FILE",data); monkeypatch.setattr(dashboard,"tournament_status",lambda:None)
    monkeypatch.setenv("DASHBOARD_USERNAME","user"); monkeypatch.setenv("DASHBOARD_PASSWORD","secret"); monkeypatch.setenv("XAUUSD_EXPERIMENT_DB",str(tmp_path/"experiments.db"))
    client=TestClient(dashboard.app)
    assert client.get("/health").status_code==200
    assert client.get("/api/status").status_code==401
    assert client.get("/api/status",auth=("user","secret")).status_code==200


def test_dashboard_reads_latest_run_and_equity(tmp_path,monkeypatch):
    reports,data=setup_files(tmp_path); monkeypatch.setattr(dashboard,"REPORTS",reports); monkeypatch.setattr(dashboard,"DATA_FILE",data)
    monkeypatch.delenv("DASHBOARD_USERNAME",raising=False); monkeypatch.delenv("DASHBOARD_PASSWORD",raising=False); monkeypatch.setenv("XAUUSD_EXPERIMENT_DB",str(tmp_path/"experiments.db"))
    client=TestClient(dashboard.app)
    assert client.get("/api/leaderboard").json()[0]["strategy"]=="mean_reversion"
    figure=client.get("/api/equity/mean_reversion").json()
    assert len(figure["data"])==2
    assert client.get("/api/history").json()[0]["strategy"]=="mean_reversion"
    assert len(client.get("/api/history/chart").json()["data"])==1
    assert client.get("/").status_code==200
    assert client.get("/api/experiments").json()==[]


def test_export_blocks_path_traversal(tmp_path,monkeypatch):
    reports,data=setup_files(tmp_path); monkeypatch.setattr(dashboard,"REPORTS",reports); monkeypatch.setattr(dashboard,"DATA_FILE",data)
    client=TestClient(dashboard.app)
    assert client.get("/api/export/run-1/../../outside.txt").status_code==404


def test_tournament_equity_and_leaderboard(tmp_path,monkeypatch):
 reports,data=setup_files(tmp_path); monkeypatch.setattr(dashboard,"REPORTS",reports); monkeypatch.setattr(dashboard,"DATA_FILE",data)
 database=__import__("xauusd.experiment_registry",fromlist=["ExperimentRegistry"]).ExperimentRegistry(tmp_path/"registry.db")
 spec=__import__("xauusd.experiment_registry",fromlist=["ExperimentSpec"]).ExperimentSpec("momentum","f",{},"v","d","e","c")
 row,_=database.register(spec); claimed=database.claim_next("w")
 artifact=reports/"tournament"/"v"/str(row["id"]); artifact.mkdir(parents=True)
 index=pd.date_range("2026-01-01",periods=3,freq="min",tz="UTC"); pd.DataFrame({"equity":[100,101,99]},index=index).to_parquet(artifact/"equity.parquet")
 database.complete(claimed["id"],"w",{"validation":{"net_profit":-1,"max_drawdown":-.02}}, {"passed":False,"score":-1}, {"equity":str(artifact/"equity.parquet")})
 monkeypatch.setattr(dashboard,"registry",lambda:database)
 client=TestClient(dashboard.app)
 assert client.get("/api/tournament/leaderboard").json()[0]["id"]==row["id"]
 assert len(client.get(f"/api/tournament/equity/{row['id']}").json()["data"])==2


def test_system_metrics_include_capacity_network_and_services():
 metrics=dashboard.system_metrics()
 assert metrics["cpu"]["cores"]>=1
 assert metrics["memory"]["total"]["bytes"]>0
 assert metrics["disk"]["total"]["bytes"]>metrics["disk"]["free"]["bytes"]
 assert metrics["network"]["rx_bytes_per_second"]>=0
 assert {row["service"] for row in metrics["services"]}=={"xauusd-tournament","xauusd-dashboard"}


def test_system_metrics_calculate_network_rate(monkeypatch):
 monkeypatch.setattr(dashboard.time,"monotonic",lambda:102.)
 monkeypatch.setattr(dashboard,"_monitor_sample",{"time":100.,"network":{"eth0":{"rx_bytes":1000,"tx_bytes":2000}}})
 original=dashboard._read_proc
 def proc(path):
  if path=="/proc/net/dev": return "head\nhead\n eth0: 3000 0 0 0 0 0 0 0 5000 0 0 0 0 0 0 0\n"
  return original(path)
 monkeypatch.setattr(dashboard,"_read_proc",proc)
 metrics=dashboard.system_metrics()
 assert metrics["network"]["rx_bytes_per_second"]==1000 and metrics["network"]["tx_bytes_per_second"]==1500
