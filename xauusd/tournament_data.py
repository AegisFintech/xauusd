from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json
import os

import pandas as pd

from .data import HistoricalDataStore


@dataclass(frozen=True)
class TournamentDataConfig:
    root: Path = Path("data/tournaments")
    active_path: Path = Path("data/tournaments/active.json")
    days: int = 365
    train_fraction: float = .60
    validation_fraction: float = .20
    symbol: str = "XAUUSD"
    timeframe: str = "M1"
    cost_model_version: str = "fixed-v1"
    engine_version: str = "event-v1"

    def __post_init__(self):
        if self.days < 30:
            raise ValueError("tournament dataset must cover at least 30 days")
        if not 0 < self.train_fraction < 1 or not 0 < self.validation_fraction < 1:
            raise ValueError("split fractions must be between zero and one")
        if self.train_fraction + self.validation_fraction >= 1:
            raise ValueError("split fractions must leave a test partition")


def frame_digest(frame: pd.DataFrame) -> str:
    """Hash canonical timestamps, schema, and values independent of Parquet bytes."""
    canonical = frame.sort_index()
    digest = hashlib.sha256()
    digest.update("|".join(canonical.columns).encode())
    digest.update("|".join(map(str, canonical.dtypes)).encode())
    digest.update(pd.util.hash_pandas_object(canonical.index, index=False).values.tobytes())
    digest.update(pd.util.hash_pandas_object(canonical, index=False).values.tobytes())
    return digest.hexdigest()


class TournamentDataset:
    def __init__(self, config: TournamentDataConfig | None = None):
        self.config = config or TournamentDataConfig()

    def create(self, bars: pd.DataFrame | None = None) -> dict:
        bars = HistoricalDataStore().read() if bars is None else bars.copy()
        bars = bars.sort_index()
        if bars.empty:
            raise ValueError("cannot freeze an empty dataset")
        end = bars.index.max()
        start = end - pd.Timedelta(days=self.config.days)
        snapshot = bars[(bars.index > start) & (bars.index <= end)].copy()
        if snapshot.empty or (snapshot.index.max() - snapshot.index.min()) < pd.Timedelta(days=self.config.days-7):
            raise ValueError("source does not contain the requested tournament coverage")
        digest = frame_digest(snapshot)
        version = f"{self.config.symbol}-{self.config.timeframe}-{end:%Y%m%d}-{digest[:12]}"
        directory = self.config.root / version
        data_path = directory / "bars.parquet"
        manifest_path = directory / "manifest.json"
        if directory.exists():
            manifest = json.loads(manifest_path.read_text())
            self.verify(manifest)
            self._activate(manifest)
            return manifest
        directory.mkdir(parents=True)
        temporary = directory / "bars.parquet.tmp"
        snapshot.to_parquet(temporary, engine="pyarrow")
        temporary.replace(data_path)
        n = len(snapshot); train_end = int(n*self.config.train_fraction)
        validation_end = train_end + int(n*self.config.validation_fraction)
        partitions = {
            "train": self._partition(snapshot.iloc[:train_end]),
            "validation": self._partition(snapshot.iloc[train_end:validation_end]),
            "test": self._partition(snapshot.iloc[validation_end:]),
        }
        manifest = {"version": version, "fingerprint": digest, "symbol": self.config.symbol,
                    "timeframe": self.config.timeframe, "rows": n,
                    "start": snapshot.index.min().isoformat(), "end": snapshot.index.max().isoformat(),
                    "source": str(HistoricalDataStore().path), "data_path": str(data_path),
                    "engine_version": self.config.engine_version, "cost_model_version": self.config.cost_model_version,
                    "columns": list(snapshot.columns), "dtypes": {c:str(t) for c,t in snapshot.dtypes.items()},
                    "partitions": partitions, "config": {**asdict(self.config), "root": str(self.config.root),
                                                          "active_path": str(self.config.active_path)}}
        manifest_path.write_text(json.dumps(manifest, indent=2))
        os.chmod(data_path, 0o444); os.chmod(manifest_path, 0o444)
        self._activate(manifest)
        return manifest

    @staticmethod
    def _partition(frame: pd.DataFrame) -> dict:
        return {"rows": len(frame), "start": frame.index.min().isoformat(), "end": frame.index.max().isoformat()}

    def _activate(self, manifest: dict) -> None:
        self.config.active_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.config.active_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps({"version":manifest["version"], "manifest":str(self.config.root/manifest["version"]/"manifest.json")},indent=2))
        temporary.replace(self.config.active_path)

    def active(self) -> dict:
        pointer = json.loads(self.config.active_path.read_text())
        return json.loads(Path(pointer["manifest"]).read_text())

    def read(self, partition: str | None = None) -> pd.DataFrame:
        manifest = self.active()
        frame = pd.read_parquet(manifest["data_path"])
        if partition is None:
            return frame
        if partition not in manifest["partitions"]:
            raise ValueError(f"unknown partition: {partition}")
        bounds = manifest["partitions"][partition]
        return frame.loc[bounds["start"]:bounds["end"]]

    def verify(self, manifest: dict | None = None) -> dict:
        manifest = manifest or self.active()
        frame = pd.read_parquet(manifest["data_path"])
        actual = frame_digest(frame)
        checks = {"fingerprint": actual == manifest["fingerprint"], "rows": len(frame) == manifest["rows"],
                  "start": frame.index.min().isoformat() == manifest["start"],
                  "end": frame.index.max().isoformat() == manifest["end"],
                  "duplicates": not frame.index.duplicated().any(), "nulls": not frame.isna().any().any()}
        return {"valid": all(checks.values()), "checks": checks, "version": manifest["version"],
                "expected_fingerprint": manifest["fingerprint"], "actual_fingerprint": actual}
