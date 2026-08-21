from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score

from .engine import EventDrivenBacktester, ExecutionConfig
from .research import build_features
from .validation import chronological_split, ValidationConfig


FEATURE_COLUMNS = (
    "return_1", "return_5", "return_15", "atr_14", "range_ratio",
    "body_fraction", "direction", "zscore_20", "trend_strength", "hour_utc",
)
MODEL_VERSION = "direction-classifier-v1"
FEATURE_VERSION = "causal-xauusd-features-v1"


@dataclass(frozen=True)
class MLConfig:
    prediction_horizon: int = 5
    probability_threshold: float = 0.58
    max_iter: int = 150
    max_leaf_nodes: int = 15
    learning_rate: float = 0.05
    random_state: int = 31
    calibration_bins: int = 10
    maximum_feature_psi: float = 0.20

    def __post_init__(self) -> None:
        if self.prediction_horizon < 1 or not .5 < self.probability_threshold < 1:
            raise ValueError("horizon must be positive and probability threshold must exceed 0.5")
        if self.calibration_bins < 2 or self.maximum_feature_psi <= 0:
            raise ValueError("calibration bins and feature PSI threshold must be positive")


def supervised_frame(bars: pd.DataFrame, config: MLConfig) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Return causal features and a future-return label aligned at decision time."""
    features = build_features(bars)
    future_return = features.close.shift(-config.prediction_horizon) / features.close - 1
    target = (future_return > 0).astype(int)
    valid = future_return.notna()
    return features.loc[valid, FEATURE_COLUMNS], target.loc[valid], future_return.loc[valid]


def classification_diagnostics(labels: pd.Series, probability: np.ndarray, bins: int = 10) -> dict:
    probability = np.asarray(probability, dtype=float)
    edges = np.linspace(0, 1, bins + 1)
    bucket = np.clip(np.digitize(probability, edges[1:-1]), 0, bins - 1)
    calibration_error = 0.0
    for number in range(bins):
        selected = bucket == number
        if selected.any():
            calibration_error += selected.mean() * abs(probability[selected].mean() - labels.to_numpy()[selected].mean())
    return {
        "accuracy": float(accuracy_score(labels, probability >= .5)),
        "roc_auc": float(roc_auc_score(labels, probability)) if labels.nunique() > 1 else .5,
        "log_loss": float(log_loss(labels, probability, labels=[0, 1])),
        "brier_score": float(brier_score_loss(labels, probability)),
        "expected_calibration_error": float(calibration_error),
    }


def feature_drift(reference: pd.DataFrame, observed: pd.DataFrame, threshold: float = .20) -> dict:
    """Population Stability Index with bins fitted exclusively on reference data."""
    values = {}
    epsilon = 1e-6
    for column in reference.columns:
        edges = np.unique(np.quantile(reference[column].dropna(), np.linspace(0, 1, 11)))
        if len(edges) < 3:
            categories = reference[column].dropna().unique().tolist()
            categories.extend(value for value in observed[column].dropna().unique() if value not in categories)
            expected = reference[column].value_counts(normalize=True).reindex(categories, fill_value=0).clip(lower=epsilon)
            actual = observed[column].value_counts(normalize=True).reindex(categories, fill_value=0).clip(lower=epsilon)
            values[column] = float(((actual - expected) * np.log(actual / expected)).sum())
            continue
        edges[0], edges[-1] = -np.inf, np.inf
        expected = pd.cut(reference[column], edges, include_lowest=True).value_counts(normalize=True, sort=False)
        actual = pd.cut(observed[column], edges, include_lowest=True).value_counts(normalize=True, sort=False)
        expected, actual = expected.clip(lower=epsilon), actual.clip(lower=epsilon)
        values[column] = float(((actual - expected) * np.log(actual / expected)).sum())
    numeric = {key: value for key, value in values.items() if value is not None}
    breached = sorted(key for key, value in numeric.items() if value > threshold)
    return {"method": "population_stability_index", "threshold": threshold, "features": values,
            "maximum": max(numeric.values(), default=0.0), "breached_features": breached,
            "status": "DEGRADED" if breached else "ACCEPTABLE"}


def model_card(bars: pd.DataFrame, config: MLConfig, model_name: str) -> dict:
    digest = hashlib.sha256(pd.util.hash_pandas_object(bars, index=True).values.tobytes()).hexdigest()
    return {
        "model_name": model_name, "model_version": MODEL_VERSION, "feature_version": FEATURE_VERSION,
        "dataset_fingerprint": digest, "prediction_target": f"close return over next {config.prediction_horizon} M1 bars > 0",
        "prediction_time_information": list(FEATURE_COLUMNS),
        "label_construction": "close[t+horizon] / close[t] - 1; positive is class 1",
        "feature_timestamps": "features at t use bars at or before t",
        "random_seed": config.random_state, "calibration": "reported only; probabilities are not recalibrated",
        "retraining_policy": "manual research rerun after approved dataset/model change; no automatic production retraining",
        "abstention": {"long_at_or_above": config.probability_threshold,
                       "short_at_or_below": 1 - config.probability_threshold, "otherwise": "no_trade"},
        "fallback": "no_trade", "drift_limit": {"feature_psi": config.maximum_feature_psi},
        "locked_test_policy": "this command consumes its test segment and is research-only; it cannot promote a model",
        "promotion_eligible": False, "live_trading_enabled": False,
    }


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

        train_prevalence = float(train_y.mean())
        validation_baseline = np.full(len(validation_y), train_prevalence)
        test_baseline = np.full(len(test_y), train_prevalence)

        report = {
            "model": "HistGradientBoostingClassifier", "config": asdict(self.ml_config),
            "execution": asdict(self.execution),
            "model_card": model_card(bars, self.ml_config, "HistGradientBoostingClassifier"),
            "train": {"start": train_x.index.min().isoformat(), "end": train_x.index.max().isoformat(), "rows": len(train_x)},
            "validation": {"start": validation_x.index.min().isoformat(), "end": validation_x.index.max().isoformat(),
                           "rows": len(validation_x),
                           **classification_diagnostics(validation_y, validation_probability, self.ml_config.calibration_bins),
                           "train_prevalence_baseline": classification_diagnostics(
                               validation_y, validation_baseline, self.ml_config.calibration_bins),
                           "feature_drift": feature_drift(train_x, validation_x, self.ml_config.maximum_feature_psi)},
            "test": {"start": test_x.index.min().isoformat(), "end": test_x.index.max().isoformat(),
                     "rows": len(test_x), "active_signal_fraction": float((test_signal != 0).mean()),
                     **classification_diagnostics(test_y, test_probability, self.ml_config.calibration_bins),
                     "train_prevalence_baseline": classification_diagnostics(
                         test_y, test_baseline, self.ml_config.calibration_bins),
                     "feature_drift": feature_drift(train_x, test_x, self.ml_config.maximum_feature_psi),
                     **backtest["metrics"]},
        }
        report["research_gate_passed"] = (
            report["test"]["profit_factor"] >= 1 and report["test"]["expectancy"] > 0
            and report["test"]["trades"] >= 100 and report["test"]["roc_auc"] > .5
            and report["test"]["log_loss"] < report["test"]["train_prevalence_baseline"]["log_loss"]
            and report["test"]["feature_drift"]["status"] == "ACCEPTABLE")
        report["passed"] = False
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "gradient_boosting.json").write_text(json.dumps(report, indent=2, allow_nan=False))
        backtest["trades"].to_csv(output_dir / "gradient_boosting_trades.csv", index=False)
        backtest["equity"].to_frame().to_parquet(output_dir / "gradient_boosting_equity.parquet")
        return report
