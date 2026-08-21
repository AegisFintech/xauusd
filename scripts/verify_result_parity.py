"""Compare two or more compute-job result directories without mutating them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def compare(reference: Path, candidate: Path, atol: float = 1e-9, rtol: float = 1e-8) -> dict:
    left = json.loads((reference / "result.json").read_text())
    right = json.loads((candidate / "result.json").read_text())
    checks = {
        "experiment_id": left["experiment_id"] == right["experiment_id"],
        "experiment_fingerprint": left["experiment_fingerprint"] == right["experiment_fingerprint"],
        "dataset": left["dataset"] == right["dataset"],
        "metrics": left["metrics"] == right["metrics"],
        "validation": left["validation"] == right["validation"],
        "strategy": left["strategy"] == right["strategy"],
        "execution": left["execution"] == right["execution"],
        "artifact_retention": left["artifact_retention"] == right["artifact_retention"],
        "file_manifest": left["files"] == right["files"],
    }
    files = {}
    for filename in sorted(set(left["files"].values()) | set(right["files"].values())):
        left_path, right_path = reference / filename, candidate / filename
        if not left_path.is_file() or not right_path.is_file():
            files[filename] = {"present": False, "equal": False, "max_abs_diff": None}
            continue
        a = pd.read_csv(left_path) if filename.endswith(".csv.gz") else pd.read_parquet(left_path)
        b = pd.read_csv(right_path) if filename.endswith(".csv.gz") else pd.read_parquet(right_path)
        same_shape = a.shape == b.shape and list(a.columns) == list(b.columns)
        equal = same_shape
        maximum = 0.0
        if same_shape:
            numeric = a.select_dtypes(include=np.number).columns
            if len(numeric):
                differences = (a[numeric] - b[numeric]).abs().to_numpy()
                maximum = float(np.nanmax(differences)) if differences.size else 0.0
                equal = equal and bool(np.allclose(a[numeric], b[numeric], atol=atol, rtol=rtol, equal_nan=True))
            other = [column for column in a.columns if column not in numeric]
            equal = equal and (not other or a[other].equals(b[other]))
        files[filename] = {"present": True, "rows": len(a), "equal": bool(equal), "max_abs_diff": maximum}
    passed = all(checks.values()) and all(item["equal"] for item in files.values())
    return {"reference": str(reference), "candidate": str(candidate), "passed": passed,
            "atol": atol, "rtol": rtol, "checks": checks, "files": files}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidates", type=Path, nargs="+")
    parser.add_argument("--atol", type=float, default=1e-9)
    parser.add_argument("--rtol", type=float, default=1e-8)
    args = parser.parse_args()
    reports = [compare(args.reference, candidate, args.atol, args.rtol) for candidate in args.candidates]
    print(json.dumps(reports, indent=2, allow_nan=False))
    if not all(report["passed"] for report in reports):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
