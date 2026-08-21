import json

import pandas as pd

from scripts.verify_result_parity import compare


def result(directory, profit=1.0):
    directory.mkdir()
    payload={"experiment_id":1,"experiment_fingerprint":"f","dataset":{"version":"v"},
             "metrics":{"validation":{"net_profit":profit}},"validation":{"passed":False},
             "strategy":{"name":"momentum"},"execution":{},"artifact_retention":{"detailed":True},
             "files":{"trades":"trades.csv.gz","equity":"equity.parquet"}}
    (directory/"result.json").write_text(json.dumps(payload))
    pd.DataFrame({"net_pnl":[1.,-1.],"reason":["target","stop"]}).to_csv(directory/"trades.csv.gz",index=False,compression="gzip")
    pd.DataFrame({"equity":[100.,101.]}).to_parquet(directory/"equity.parquet")


def test_result_parity_accepts_equal_bundles_and_rejects_metric_drift(tmp_path):
    left,right=tmp_path/"left",tmp_path/"right"; result(left); result(right)
    assert compare(left,right)["passed"]
    payload=json.loads((right/"result.json").read_text()); payload["metrics"]["validation"]["net_profit"]=2
    (right/"result.json").write_text(json.dumps(payload))
    report=compare(left,right)
    assert not report["passed"] and not report["checks"]["metrics"]
