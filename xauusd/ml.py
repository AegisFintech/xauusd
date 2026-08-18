from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score

from .engine import EventDrivenBacktester, ExecutionConfig
from .research import build_features
from .validation import chronological_split, ValidationConfig


FEATURE_COLUMNS = (
    "return_1", "return_5", "return_15", "atr_14", "range_ratio",
    "body_fraction", "direction", "zscore_20", "trend_strength", "hour_utc",
)


@dataclass(frozen=True)
class MLConfig:
    prediction_horizon: int = 5
    probability_threshold: float = 0.58
    max_iter: int = 150
    max_leaf_nodes: int = 15
    learning_rate: float = 0.05
    random_state: int = 31

    def __post_init__(self) -> None:
        if self.prediction_horizon < 1 or not .5 < self.probability_threshold < 1:
            raise ValueError("horizon must be positive and probability threshold must exceed 0.5")


def supervised_frame(bars: pd.DataFrame, config: MLConfig) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Return causal features and a future-return label aligned at decision time."""
    features = build_features(bars)
    future_return = features.close.shift(-config.prediction_horizon) / features.close - 1
    target = (future_return > 0).astype(int)
    valid = future_return.notna()
    return features.loc[valid, FEATURE_COLUMNS], target.loc[valid], future_return.loc[valid]


class GradientBoostingResearch:
    def __init__(self, ml_config: MLConfig | None = None, execution: ExecutionConfig | None = None):
        self.ml_config = ml_config or MLConfig()
        self.execution = execution or ExecutionConfig()

    def _model(self) -> HistGradientBoostingClassifier:
        c = self.ml_config
        return HistGradientBoostingClassifier(max_iter=c.max_iter, max_leaf_nodes=c.max_leaf_nodes,
                                              learning_rate=c.learning_rate, random_state=c.random_state)

    def run(self, bars: pd.DataFrame, output_dir: Path = Path("reports/ml")) -> dict:
        features = build_features(bars)
        x, y, _ = supervised_frame(bars, self.ml_config)
        split_x = chronological_split(x, ValidationConfig())
        boundaries = {name: part.index for name, part in split_x.items()}
        train_x, validation_x, test_x = (split_x[name] for name in ("train", "validation", "test"))
        train_y, validation_y, test_y = (y.loc[boundaries[name]] for name in ("train", "validation", "test"))

        model = self._model()
        model.fit(train_x, train_y)
        validation_probability = model.predict_proba(validation_x)[:, 1]
        test_probability = model.predict_proba(test_x)[:, 1]
        threshold = self.ml_config.probability_threshold
        test_signal = pd.Series(np.where(test_probability >= threshold, 1,
                                np.where(test_probability <= 1 - threshold, -1, 0)), index=test_x.index, dtype=int)
        test_bars = features.loc[test_x.index]
        backtest = EventDrivenBacktester(self.execution).run(test_bars, test_signal)

        def classification_metrics(labels, probability):
            return {"accuracy": float(accuracy_score(labels, probability >= .5)),
                    "roc_auc": float(roc_auc_score(labels, probability)) if labels.nunique() > 1 else .5,
                    "log_loss": float(log_loss(labels, probability, labels=[0, 1]))}

        report = {
            "model": "HistGradientBoostingClassifier", "config": asdict(self.ml_config),
            "execution": asdict(self.execution),
            "train": {"start": train_x.index.min().isoformat(), "end": train_x.index.max().isoformat(), "rows": len(train_x)},
            "validation": {"start": validation_x.index.min().isoformat(), "end": validation_x.index.max().isoformat(),
                           "rows": len(validation_x), **classification_metrics(validation_y, validation_probability)},
            "test": {"start": test_x.index.min().isoformat(), "end": test_x.index.max().isoformat(),
                     "rows": len(test_x), "active_signal_fraction": float((test_signal != 0).mean()),
                     **classification_metrics(test_y, test_probability), **backtest["metrics"]},
        }
        report["passed"] = (report["test"]["profit_factor"] >= 1 and report["test"]["expectancy"] > 0
                            and report["test"]["trades"] >= 100 and report["test"]["roc_auc"] > .5)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "gradient_boosting.json").write_text(json.dumps(report, indent=2, allow_nan=False))
        backtest["trades"].to_csv(output_dir / "gradient_boosting_trades.csv", index=False)
        backtest["equity"].to_frame().to_parquet(output_dir / "gradient_boosting_equity.parquet")
        return report
