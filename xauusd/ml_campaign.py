from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .engine import EventDrivenBacktester, ExecutionConfig
from .ml import classification_diagnostics, feature_drift, MLConfig, model_card, supervised_frame
from .ml_models import ProbabilityEnsemble, RegimeTransformer, create_model
from .research import build_features
from .validation import walk_forward_splits


@dataclass(frozen=True)
class EnsembleConfig:
    backends: tuple[str, ...] = ("hist_gradient_boosting", "random_forest", "extra_trees")
    regimes: int = 3
    folds: int = 4


class WalkForwardMLCampaign:
    def __init__(self, ml: MLConfig | None = None, ensemble: EnsembleConfig | None = None,
                 execution: ExecutionConfig | None = None):
        self.ml = ml or MLConfig()
        self.ensemble = ensemble or EnsembleConfig()
        self.execution = execution or ExecutionConfig()

    def run(self, bars: pd.DataFrame, output_dir: Path = Path("reports/ml/walk_forward")) -> dict:
        x, y, _ = supervised_frame(bars, self.ml)
        price_features = build_features(bars)
        folds, all_trades = [], []
        for number, (train_x, test_x) in enumerate(walk_forward_splits(x, self.ensemble.folds), 1):
            train_y, test_y = y.loc[train_x.index], y.loc[test_x.index]
            regime_columns = ["return_1", "atr_14", "range_ratio", "trend_strength"]
            regime = RegimeTransformer(self.ensemble.regimes, self.ml.random_state + number).fit(train_x[regime_columns])
            train_augmented = np.c_[train_x.to_numpy(), regime.transform(train_x[regime_columns])]
            test_augmented = np.c_[test_x.to_numpy(), regime.transform(test_x[regime_columns])]
            ensemble = ProbabilityEnsemble([create_model(name, self.ml.random_state + number)
                                            for name in self.ensemble.backends]).fit(train_augmented, train_y)
            probability = ensemble.predict_proba(test_augmented)[:, 1]
            baseline_probability = np.full(len(test_y), float(train_y.mean()))
            threshold = self.ml.probability_threshold
            signal = pd.Series(np.where(probability >= threshold, 1,
                               np.where(probability <= 1-threshold, -1, 0)), index=test_x.index, dtype=int)
            backtest = EventDrivenBacktester(self.execution).run(price_features.loc[test_x.index], signal)
            if not backtest["trades"].empty:
                trades = backtest["trades"].copy(); trades["fold"] = number; all_trades.append(trades)
            folds.append({"fold": number, "train_start": train_x.index.min().isoformat(),
                          "train_end": train_x.index.max().isoformat(), "test_start": test_x.index.min().isoformat(),
                          "test_end": test_x.index.max().isoformat(), "rows": len(test_x),
                          **classification_diagnostics(test_y, probability, self.ml.calibration_bins),
                          "train_prevalence_baseline": classification_diagnostics(
                              test_y, baseline_probability, self.ml.calibration_bins),
                          "feature_drift": feature_drift(train_x, test_x, self.ml.maximum_feature_psi),
                          "active_signal_fraction": float((signal != 0).mean()), **backtest["metrics"]})
        positive = float(np.mean([fold["net_profit"] > 0 for fold in folds]))
        report = {"config": {"ml": asdict(self.ml), "ensemble": asdict(self.ensemble),
                              "execution": asdict(self.execution)}, "folds": folds,
                  "model_card": model_card(bars, self.ml, "out_of_fold_probability_ensemble"),
                  "positive_fold_fraction": positive,
                  "aggregate_net_profit": float(sum(fold["net_profit"] for fold in folds)),
                  "mean_roc_auc": float(np.mean([fold["roc_auc"] for fold in folds]))}
        report["research_gate_passed"] = (
            positive >= .6 and report["aggregate_net_profit"] > 0 and report["mean_roc_auc"] > .5
            and all(fold["log_loss"] < fold["train_prevalence_baseline"]["log_loss"] for fold in folds)
            and all(fold["feature_drift"]["status"] == "ACCEPTABLE" for fold in folds))
        report["passed"] = False
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "ensemble.json").write_text(json.dumps(report, indent=2, allow_nan=False))
        ledger = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
        ledger.to_csv(output_dir / "ensemble_trades.csv", index=False)
        return report
