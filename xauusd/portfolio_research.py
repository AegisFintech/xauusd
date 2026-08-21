from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .experiment_registry import ExperimentRegistry
from .research import build_features
from .tournament_data import TournamentDataset


def classify_regimes(features: pd.DataFrame) -> pd.Series:
    """Causal labels using expanding historical thresholds, never future quantiles."""
    volatility = features["atr_14"] / features["close"]
    vol_threshold = volatility.expanding(min_periods=500).median().shift(1)
    trend_threshold = features["trend_strength"].expanding(min_periods=500).median().shift(1)
    volatility_label = np.where(volatility > vol_threshold, "high_vol", "low_vol")
    trend_label = np.where(features["trend_strength"] > trend_threshold, "trend", "range")
    session = np.where(features.index.hour < 7, "asia", np.where(features.index.hour < 13, "london", "new_york"))
    return pd.Series([f"{a}|{b}|{c}" for a, b, c in zip(trend_label, volatility_label, session)],
                     index=features.index, name="regime")


def equity_metrics(equity: pd.Series) -> dict:
    returns = equity.pct_change().fillna(0)
    drawdown = equity / equity.cummax() - 1
    downside = returns[returns < 0]
    scale = np.sqrt(252 * 1440)
    expected_shortfall = returns[returns <= returns.quantile(0.05)].mean()
    return {
        "initial_equity": float(equity.iloc[0]), "final_equity": float(equity.iloc[-1]),
        "net_profit": float(equity.iloc[-1] - equity.iloc[0]),
        "total_return": float(equity.iloc[-1] / equity.iloc[0] - 1),
        "volatility": float(scale * returns.std()),
        "sharpe": float(scale * returns.mean() / returns.std()) if returns.std() else 0.0,
        "sortino": float(scale * returns.mean() / downside.std()) if len(downside) > 1 and downside.std() else 0.0,
        "max_drawdown": float(drawdown.min()),
        "expected_shortfall_95": float(expected_shortfall) if pd.notna(expected_shortfall) else 0.0,
    }


def aligned_returns(curves: dict[str, pd.Series]) -> pd.DataFrame:
    aligned = pd.concat({name: curve.sort_index().astype(float) for name, curve in curves.items()},
                        axis=1, join="inner").dropna()
    if len(aligned) < 3:
        raise ValueError("at least three aligned equity observations are required")
    return aligned.pct_change().iloc[1:].replace([np.inf, -np.inf], np.nan).dropna()


def portfolio_weights(fit_returns: pd.DataFrame, method: str) -> pd.Series:
    if fit_returns.shape[1] < 1:
        raise ValueError("at least one strategy is required")
    if method == "equal":
        raw = pd.Series(1.0, index=fit_returns.columns)
    else:
        inverse_volatility = (1.0 / fit_returns.std().replace(0, np.nan)).replace(
            [np.inf, -np.inf], np.nan).fillna(0)
        if not inverse_volatility.sum():
            inverse_volatility[:] = 1.0
        if method == "inverse_volatility":
            raw = inverse_volatility
        elif method == "correlation_aware":
            correlation = fit_returns.corr().fillna(0).abs()
            correlation = correlation.where(~np.eye(len(correlation), dtype=bool), 0)
            raw = inverse_volatility / (1 + correlation.mean(axis=1))
        else:
            raise ValueError(f"unknown weighting method: {method}")
    return raw / raw.sum()


def portfolio_equity(returns: pd.DataFrame, weights: pd.Series, initial_equity: float = 100000.0) -> pd.Series:
    weights = weights.reindex(returns.columns)
    if weights.isna().any() or not np.isclose(weights.sum(), 1.0):
        raise ValueError("weights must cover every strategy and sum to one")
    growth = (1 + returns.mul(weights, axis=1).sum(axis=1)).cumprod()
    prior = pd.Series([initial_equity], index=[returns.index[0] - pd.Timedelta(nanoseconds=1)])
    return pd.concat([prior, initial_equity * growth]).rename("equity")


def effective_number_of_bets(returns: pd.DataFrame, weights: pd.Series) -> float:
    correlation = returns.corr().fillna(0).to_numpy()
    weighted = np.diag(weights.to_numpy()) @ correlation @ np.diag(weights.to_numpy())
    eigenvalues = np.linalg.eigvalsh(weighted).clip(min=0)
    denominator = np.square(eigenvalues).sum()
    return float(np.square(eigenvalues.sum()) / denominator) if denominator else 0.0


def leave_one_out(returns: pd.DataFrame, weights: pd.Series) -> list[dict]:
    full = equity_metrics(portfolio_equity(returns, weights))
    reports = []
    for omitted in returns.columns:
        reduced = weights.drop(omitted)
        if not reduced.sum():
            continue
        reduced /= reduced.sum()
        metrics = equity_metrics(portfolio_equity(returns.drop(columns=omitted), reduced))
        reports.append({
            "omitted": str(omitted),
            "marginal_total_return": full["total_return"] - metrics["total_return"],
            "marginal_volatility": full["volatility"] - metrics["volatility"],
            "marginal_max_drawdown": full["max_drawdown"] - metrics["max_drawdown"],
            "marginal_expected_shortfall_95": full["expected_shortfall_95"] - metrics["expected_shortfall_95"],
        })
    return reports


class PortfolioResearch:
    def __init__(self, registry: ExperimentRegistry | None = None, dataset: TournamentDataset | None = None,
                 output_root: Path = Path("reports/tournament/portfolio")):
        self.registry = registry or ExperimentRegistry()
        self.dataset = dataset or TournamentDataset()
        self.output_root = output_root

    def _diverse_leaders(self, per_family=1, limit=5):
        selected = []
        counts = defaultdict(int)
        for row in self.registry.leaderboard(500):
            if counts[row["strategy_family"]] >= per_family or not (row.get("artifacts") or {}).get("equity"):
                continue
            selected.append(row)
            counts[row["strategy_family"]] += 1
            if len(selected) >= limit:
                break
        return selected

    def run(self) -> dict:
        leaders = self._diverse_leaders()
        if len(leaders) < 2:
            return {"status": "insufficient_diversity", "strategies": len(leaders), "holdout_used": False}
        regimes = classify_regimes(build_features(self.dataset.read("validation")))
        curves, strategy_reports, exposures = {}, [], {}
        for row in leaders:
            identifier = str(row["id"])
            equity = pd.read_parquet(row["artifacts"]["equity"]).iloc[:, 0].sort_index()
            trades = pd.read_csv(row["artifacts"]["trades"], parse_dates=["exit_time"], compression="infer")
            trades["regime"] = regimes.reindex(pd.DatetimeIndex(trades.exit_time), method="ffill").to_numpy()
            by_regime = []
            for name, group in trades.groupby("regime"):
                profits, losses = group.net_pnl[group.net_pnl > 0].sum(), -group.net_pnl[group.net_pnl < 0].sum()
                by_regime.append({"regime": name, "trades": len(group), "net_profit": float(group.net_pnl.sum()),
                                  "expectancy": float(group.net_pnl.mean()),
                                  "profit_factor": float(profits / losses) if losses else None})
            strategy_reports.append({"experiment_id": identifier, "family": row["strategy_family"],
                                     "validation_score": row["validation"].get("score"), "regimes": by_regime})
            curves[identifier] = equity
            exposures[identifier] = float((row.get("metrics") or {}).get("validation", {}).get("exposure", 0))

        returns = aligned_returns(curves)
        split = max(2, min(len(returns) - 1, int(len(returns) * 0.6)))
        fit_returns, evaluation_returns = returns.iloc[:split], returns.iloc[split:]
        portfolios = {}
        for method in ("equal", "inverse_volatility", "correlation_aware"):
            weights = portfolio_weights(fit_returns, method)
            equity = portfolio_equity(evaluation_returns, weights)
            portfolios[method] = {
                "weights": {str(key): float(value) for key, value in weights.items()},
                "metrics": equity_metrics(equity),
                "combined_gross_exposure": float(sum(abs(weights[key]) * exposures[str(key)] for key in weights.index)),
                "effective_number_of_bets": effective_number_of_bets(fit_returns, weights),
                "leave_one_out": leave_one_out(evaluation_returns, weights),
            }
            if method == "equal":
                portfolio = equity
        individual = {str(column): equity_metrics(portfolio_equity(
            evaluation_returns[[column]], pd.Series({column: 1.0}))) for column in evaluation_returns.columns}
        best_id = max(individual, key=lambda key: individual[key]["total_return"])
        no_trade = pd.Series(100000.0, index=portfolio.index)
        metrics = portfolios["equal"]["metrics"]
        gates = {
            "positive_net_profit": metrics["net_profit"] > 0, "positive_sharpe": metrics["sharpe"] > 0,
            "maximum_drawdown": metrics["max_drawdown"] >= -0.05,
            "maximum_combined_gross_exposure": portfolios["equal"]["combined_gross_exposure"] <= 1.0,
            "strategy_diversity": len({row["strategy_family"] for row in leaders}) >= 2,
        }
        self.output_root.mkdir(parents=True, exist_ok=True)
        portfolio.to_frame().to_parquet(self.output_root / "equity.parquet")
        report = {
            "status": "completed", "partition": "validation", "holdout_used": False, "weight_fit_fraction": 0.6,
            "fit_period": {"start": fit_returns.index[0].isoformat(), "end": fit_returns.index[-1].isoformat()},
            "evaluation_period": {"start": evaluation_returns.index[0].isoformat(), "end": evaluation_returns.index[-1].isoformat()},
            "default_method": "equal", "experiment_ids": [str(row["id"]) for row in leaders],
            "correlation_matrix": fit_returns.corr().fillna(0).to_dict(), "portfolios": portfolios,
            "baselines": {"best_individual": {"experiment_id": best_id, "metrics": individual[best_id]},
                          "individuals": individual, "no_trade": equity_metrics(no_trade)},
            "metrics": metrics, "gates": gates, "passed": all(gates.values()),
            "strategies": strategy_reports, "equity": str(self.output_root / "equity.parquet"),
        }
        temporary = self.output_root / "latest.json.tmp"
        temporary.write_text(json.dumps(report, indent=2, allow_nan=False))
        temporary.replace(self.output_root / "latest.json")
        return report
