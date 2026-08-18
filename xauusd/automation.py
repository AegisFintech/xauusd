from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import time
import traceback

import pandas as pd

from .data import HistoricalDataStore
from .engine import ExecutionConfig
from .research import DEFAULT_STRATEGIES, ResearchCampaign, StrategySpec
from .validation import StrategyValidator, ValidationConfig


@dataclass(frozen=True)
class AutomationConfig:
    lookback_days: int = 180
    validate_top: int = 3
    minimum_freshness_hours: int = 48
    reports_dir: Path = Path("reports/automation")
    registry_path: Path = Path("reports/champion.json")
    status_path: Path = Path("reports/automation/status.json")
    attempts_path: Path = Path("reports/automation/attempts.jsonl")


def atomic_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, allow_nan=False))
    temporary.replace(path)


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps(payload, allow_nan=False) + "\n")


class RunLock:
    def __init__(self, path: Path):
        self.path = path
        self.handle = None

    def __enter__(self):
        import fcntl
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("w")
        try:
            fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self.handle.close()
            raise RuntimeError("another automated research run is already active") from exc
        self.handle.write(str(os.getpid())); self.handle.flush()
        return self

    def __exit__(self, *_):
        import fcntl
        fcntl.flock(self.handle, fcntl.LOCK_UN)
        self.handle.close()


class ChampionRegistry:
    def __init__(self, path: Path):
        self.path = path

    def read(self) -> dict | None:
        return json.loads(self.path.read_text()) if self.path.exists() else None

    def consider(self, candidate: dict) -> dict:
        current = self.read()
        eligible = bool(candidate.get("passed"))
        promoted = eligible and (current is None or candidate["score"] > current["score"])
        if promoted:
            atomic_json(self.path, candidate)
        return {"eligible": eligible, "promoted": promoted, "previous": current, "champion": candidate if promoted else current}


def render_html(manifest: dict) -> str:
    rows = "".join(
        f"<tr><td>{item['strategy']}</td><td>{item['score']:.3f}</td>"
        f"<td>{item['net_profit']:.2f}</td><td>{item['profit_factor']:.3f}</td>"
        f"<td>{'PASS' if item.get('passed') else 'FAIL'}</td></tr>"
        for item in manifest["candidates"]
    )
    return ("<!doctype html><html><head><meta charset='utf-8'><title>XAUUSD Research Run</title>"
            "<style>body{font-family:sans-serif;background:#111;color:#eee;margin:2rem}"
            "table{border-collapse:collapse}td,th{padding:.5rem;border:1px solid #555}</style></head><body>"
            f"<h1>XAUUSD Research Run</h1><p>Run: {manifest['run_id']}</p>"
            f"<p>Data: {manifest['data']['start']} — {manifest['data']['end']} ({manifest['data']['rows']} bars)</p>"
            "<table><thead><tr><th>Strategy</th><th>Score</th><th>Net P&amp;L</th><th>PF</th><th>Gate</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></body></html>")


def weekly_comparison(reports_dir: Path = Path("reports/automation"), limit: int = 7) -> dict:
    manifests = []
    for path in sorted(reports_dir.glob("*/manifest.json"), reverse=True)[:limit]:
        manifests.append(json.loads(path.read_text()))
    strategies: dict[str, list[dict]] = {}
    for manifest in reversed(manifests):
        for candidate in manifest["candidates"]:
            strategies.setdefault(candidate["strategy"], []).append({
                "run_id": manifest["run_id"], "score": candidate["score"],
                "net_profit": candidate["net_profit"], "passed": candidate["passed"],
            })
    report = {"runs": len(manifests), "strategies": strategies}
    atomic_json(reports_dir / "weekly.json", report)
    return report


def run_history(reports_dir: Path = Path("reports/automation"), limit: int = 100) -> list[dict]:
    history = []
    for path in sorted(reports_dir.glob("*/manifest.json"))[-limit:]:
        manifest = json.loads(path.read_text())
        best = manifest["candidates"][0] if manifest["candidates"] else None
        history.append({"run_id": manifest["run_id"], "created_at": manifest["created_at"],
                        "data_end": manifest["data"]["end"], "best": best,
                        "promoted": manifest["promotion"]["promoted"]})
    return history


def automated_attempt(config: AutomationConfig | None = None) -> dict:
    """Run the scheduled research stage with overlap protection and durable status."""
    config = config or AutomationConfig()
    started = datetime.now(timezone.utc)
    attempt = {"started_at": started.isoformat(), "stage": "research", "status": "running"}
    atomic_json(config.status_path, attempt)
    try:
        with RunLock(config.reports_dir / "automation.lock"):
            manifest = DailyResearchPipeline(config).run(now=started)
        attempt.update(status="success", run_id=manifest["run_id"])
    except Exception as exc:
        attempt.update(status="failed", error=str(exc), error_type=type(exc).__name__)
    finished = datetime.now(timezone.utc)
    attempt.update(finished_at=finished.isoformat(), duration_seconds=(finished-started).total_seconds())
    atomic_json(config.status_path, attempt)
    append_jsonl(config.attempts_path, attempt)
    return attempt


class DailyResearchPipeline:
    def __init__(self, config: AutomationConfig | None = None, execution: ExecutionConfig | None = None,
                 validation: ValidationConfig | None = None):
        self.config = config or AutomationConfig()
        self.execution = execution or ExecutionConfig()
        self.validation = validation or ValidationConfig()

    def run(self, now: datetime | None = None, update_data: bool = False) -> dict:
        now = now or datetime.now(timezone.utc)
        if update_data:
            raise RuntimeError("data updates must be invoked separately before the research run")
        store = HistoricalDataStore()
        bars = store.read()
        cutoff = pd.Timestamp(now) - pd.Timedelta(days=self.config.lookback_days)
        sample = bars.loc[bars.index >= cutoff]
        if sample.empty:
            raise RuntimeError("no bars in configured research lookback")
        age_hours = (pd.Timestamp(now) - bars.index.max()).total_seconds() / 3600
        freshness = {"age_hours": age_hours, "fresh": age_hours <= self.config.minimum_freshness_hours}
        if not freshness["fresh"]:
            raise RuntimeError(f"historical data is stale by {age_hours:.1f} hours; run data update")

        fingerprint = hashlib.sha256(f"{sample.index.min()}|{sample.index.max()}|{len(sample)}".encode()).hexdigest()[:12]
        run_id = f"{now:%Y%m%dT%H%M%SZ}-{fingerprint}"
        final_dir = self.config.reports_dir / run_id
        working_dir = self.config.reports_dir / f".{run_id}.working"
        if final_dir.exists():
            return json.loads((final_dir / "manifest.json").read_text())
        if working_dir.exists():
            shutil.rmtree(working_dir)
        working_dir.mkdir(parents=True)

        ranked = ResearchCampaign(self.execution).run(sample, DEFAULT_STRATEGIES, working_dir / "research")
        specs = {spec.name: spec for spec in DEFAULT_STRATEGIES}
        validations = {}
        for candidate in ranked[:self.config.validate_top]:
            spec = specs[candidate["strategy"]]
            validations[spec.name] = StrategyValidator(self.execution, self.validation).validate(
                sample, spec, working_dir / "validation")
        candidates = []
        for candidate in ranked:
            report = validations.get(candidate["strategy"])
            candidates.append({**candidate, "passed": bool(report and report["passed"]),
                               "gates": report["gates"] if report else None})
        best = candidates[0]
        registry = ChampionRegistry(self.config.registry_path)
        promotion = registry.consider({"run_id": run_id, **best})
        manifest = {"run_id": run_id, "created_at": now.isoformat(), "mode": "research-only",
                    "data": {"start": sample.index.min().isoformat(), "end": sample.index.max().isoformat(),
                             "rows": len(sample), **freshness},
                    "execution": asdict(self.execution), "candidates": candidates, "promotion": promotion}
        atomic_json(working_dir / "manifest.json", manifest)
        (working_dir / "report.html").write_text(render_html(manifest))
        working_dir.replace(final_dir)
        atomic_json(self.config.reports_dir / "latest.json", {"run_id": run_id, "path": str(final_dir)})
        return manifest
