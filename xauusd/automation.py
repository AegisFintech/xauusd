from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import html
import json
import math
import os
import shutil
import subprocess
import time

import pandas as pd

from .atomic import atomic_write_json
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
    atomic_write_json(path, payload, indent=2)


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
    """Champion record bound to the exact data and code that authorised it.

    The record used to be a bare dict written to ``reports/champion.json``, so a
    consumer could not tell which bars, which dataset digest or which backtester
    version produced it, and ``consider`` compared a candidate score from the
    current window against an incumbent score computed on a *different* trailing
    window. A months-old score therefore blocked promotion permanently, or was
    displaced by a score that was not comparable.
    """
    SCHEMA = "xauusd.champion/2"

    def __init__(self, path: Path):
        self.path = path

    def read(self) -> dict | None:
        return json.loads(self.path.read_text()) if self.path.exists() else None

    def consider(self, candidate: dict, dataset_fingerprint: str | None = None,
                 dataset_version: str | None = None, code_commit: str | None = None) -> dict:
        current = self.read()
        eligible = bool(candidate.get("passed")) and candidate.get("score") is not None
        if not eligible:
            return {"eligible": False, "promoted": False, "previous": current,
                    "champion": current,
                    "reason": "candidate did not pass validation" if not candidate.get("passed")
                              else "candidate has no score"}
        if current is None:
            promoted, reason = True, "promoted (first champion)"
        elif dataset_fingerprint and current.get("dataset_fingerprint") == dataset_fingerprint:
            # Same bars on both sides: the two scores are comparable.
            promoted = candidate["score"] > current["score"]
            reason = "promoted (higher validation score)" if promoted else "incumbent score is not beaten"
        elif dataset_fingerprint and current.get("dataset_fingerprint"):
            # The dataset changed, so the incumbent's score was computed on bars
            # that no longer exist. A candidate that passed validation on the new
            # data stands on its own; the stale number is not compared against it.
            promoted, reason = True, "promoted (dataset changed; incumbent score not comparable)"
        else:
            # Either side is unbound to a dataset, so nothing can be shown to be
            # comparable. Keep the incumbent rather than replace it on a guess.
            promoted, reason = False, "incumbent is not bound to a dataset; score comparison refused"
        if promoted:
            record = {**candidate, "schema": self.SCHEMA, "dataset_fingerprint": dataset_fingerprint,
                      "dataset_version": dataset_version, "code_commit": code_commit,
                      "promoted_at": datetime.now(timezone.utc).isoformat()}
            atomic_json(self.path, record)
            return {"eligible": True, "promoted": True, "previous": current,
                    "champion": record, "reason": reason}
        return {"eligible": True, "promoted": False, "previous": current, "champion": current,
                "reason": reason}


def render_html(manifest: dict) -> str:
    def number(value: object, spec: str = ".3f") -> str:
        # A metric can legitimately be None (undefined profit factor, no return
        # variance). Formatting it directly raised for exactly the candidates an
        # operator most needs to see.
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            return "n/a"
        return format(float(value), spec if spec != "d" else ".0f")

    rows = "".join(
        f"<tr><td>{html.escape(str(item['strategy']))}</td><td>{number(item.get('score'))}</td>"
        f"<td>{number(item.get('net_profit'), '.2f')}</td><td>{number(item.get('profit_factor'))}</td>"
        f"<td>{'PASS' if item.get('passed') else 'FAIL'}</td></tr>"
        for item in manifest["candidates"]
    )
    data = manifest["data"]
    return ("<!doctype html><html><head><meta charset='utf-8'><title>XAUUSD Research Run</title>"
            "<style>body{font-family:sans-serif;background:#111;color:#eee;margin:2rem}"
            "table{border-collapse:collapse}td,th{padding:.5rem;border:1px solid #555}</style></head><body>"
            f"<h1>XAUUSD Research Run</h1><p>Run: {html.escape(str(manifest['run_id']))}</p>"
            f"<p>Data: {html.escape(str(data['start']))} — {html.escape(str(data['end']))} "
            f"({number(data.get('rows'), 'd')} bars)</p>"
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

        # Content-addressed run id. The previous identity was bounds + row count,
        # so a broker data revision that preserved the start, end and row count
        # produced the *same* run_id and short-circuited the whole run: the stored
        # manifest, and therefore reports/champion.json, stayed silently stale.
        # tournament_data.frame_digest hashes content, columns, dtypes and index.
        from .tournament_data import frame_digest
        fingerprint = frame_digest(sample)
        run_id = f"{now:%Y%m%dT%H%M%SZ}-{fingerprint}"
        final_dir = self.config.reports_dir / run_id
        working_dir = self.config.reports_dir / f".{run_id}.working"
        if final_dir.exists():
            return json.loads((final_dir / "manifest.json").read_text())
        if working_dir.exists():
            shutil.rmtree(working_dir)
        working_dir.mkdir(parents=True)

        # Rank, validate and finally select on three disjoint partitions.
        #
        # The old order ranked every candidate on the whole 180-day sample and then
        # validated the top N on a split *carved out of that same sample*, so the
        # held-out "test" segment was inside the data that chose the candidate. The
        # candidates are now ranked on the training partition only, gated on
        # validation, and the final champion is the validation winner.
        train_end = sample.index[int(len(sample) * self.validation.train_fraction)]
        validation_end = sample.index[int(len(sample) * (self.validation.train_fraction
                                                         + self.validation.validation_fraction))]
        partitions = {"train": sample.loc[sample.index <= train_end],
                      "validation": sample.loc[(sample.index > train_end) & (sample.index <= validation_end)],
                      "test": sample.loc[sample.index > validation_end]}
        if min(len(frame) for frame in partitions.values()) < 100:
            raise RuntimeError("not enough bars for the configured train/validation/test proportions")

        ranked = ResearchCampaign(self.execution).run(partitions["train"], DEFAULT_STRATEGIES,
                                                      working_dir / "research")
        specs = {spec.name: spec for spec in DEFAULT_STRATEGIES}
        validations = {}
        for candidate in ranked[:self.config.validate_top]:
            spec = specs[candidate["strategy"]]
            validations[spec.name] = StrategyValidator(self.execution, self.validation).validate(
                partitions["validation"], spec, working_dir / "validation")
        candidates = []
        for candidate in ranked:
            report = validations.get(candidate["strategy"])
            candidates.append({**candidate,
                               "passed": bool(report and report["passed"]),
                               "validation_score": report.get("score") if report else None,
                               "gates": report["gates"] if report else None})
        # The champion is the best *validation* performer, not the best ranker: the
        # ranking is a screen to limit how many candidates get validated at all.
        eligible = [row for row in candidates if row["passed"] and row["validation_score"] is not None]
        if not eligible:
            raise RuntimeError("no candidate passed validation on the held-out validation partition")
        best = max(eligible, key=lambda row: row["validation_score"])
        registry = ChampionRegistry(self.config.registry_path)
        promotion = registry.consider({"run_id": run_id, **best},
                                      dataset_fingerprint=fingerprint, dataset_version=None,
                                      code_commit=self._code_commit())
        manifest = {"run_id": run_id, "created_at": now.isoformat(), "mode": "research-only",
                    "data": {"start": sample.index.min().isoformat(), "end": sample.index.max().isoformat(),
                             "rows": len(sample), "fingerprint": fingerprint,
                             "partitions": {name: {"start": frame.index.min().isoformat(),
                                                   "end": frame.index.max().isoformat(),
                                                   "rows": len(frame)}
                                            for name, frame in partitions.items()},
                             **freshness},
                    "execution": asdict(self.execution), "candidates": candidates, "promotion": promotion}
        atomic_json(working_dir / "manifest.json", manifest)
        (working_dir / "report.html").write_text(render_html(manifest))
        working_dir.replace(final_dir)
        atomic_json(self.config.reports_dir / "latest.json", {"run_id": run_id, "path": str(final_dir)})
        return manifest

    @staticmethod
    def _code_commit() -> str | None:
        try:
            return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                                  timeout=10).stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            return None
