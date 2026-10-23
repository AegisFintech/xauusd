"""Causal strategy programs and deterministic, cost-aware research evaluation.

Programs are Python *expressions*, interpreted here without eval/exec. This is
the automatically deployable extension surface; it cannot alter account gates.
"""
from __future__ import annotations

import ast
from dataclasses import asdict
import hashlib
import json
import math
import operator

import numpy as np
import pandas as pd

from .engine import EventDrivenBacktester, ExecutionConfig
from .validation import bootstrap_trade_paths

MAX_WINDOW = 240
EMBARGO = 256
MIN_TRADES = 100
MIN_FORWARD_TRADES = 30
MAX_DRAWDOWN = -.10
MAX_ATTEMPTS = 20
FUNCTIONS = ("ema", "mean", "std", "high", "low", "lag", "where", "abs", "clip")


class StrategyError(ValueError):
    """A classified invalid program; never includes the submitted program."""


def identity(candidate: dict) -> str:
    return hashlib.sha256(str(candidate["expression"]).strip().encode()).hexdigest()[:24]


def signals(expression: str, bars: pd.DataFrame) -> pd.Series:
    if not isinstance(expression, str) or not 0 < len(expression) <= 4096:
        raise StrategyError("invalid_expression_size")
    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, RecursionError):
        raise StrategyError("invalid_expression") from None
    if len(list(ast.walk(tree))) > 256:
        raise StrategyError("expression_too_complex")
    columns = {name: bars[name].astype(float) for name in ("open", "high", "low", "close", "volume")}
    binary = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
              ast.Div: operator.truediv, ast.BitAnd: operator.and_, ast.BitOr: operator.or_}
    comparisons = {ast.Gt: operator.gt, ast.GtE: operator.ge, ast.Lt: operator.lt,
                   ast.LtE: operator.le, ast.Eq: operator.eq, ast.NotEq: operator.ne}

    def visit(node, depth=0):
        if depth > 24:
            raise StrategyError("expression_too_deep")
        go = lambda child: visit(child, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if not math.isfinite(node.value) or abs(node.value) > 1_000_000:
                raise StrategyError("invalid_constant")
            return node.value
        if isinstance(node, ast.Name) and node.id in columns:
            return columns[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd, ast.Invert)):
            return {ast.USub: operator.neg, ast.UAdd: operator.pos, ast.Invert: operator.invert}[type(node.op)](go(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in binary:
            with np.errstate(all="ignore"):
                return binary[type(node.op)](go(node.left), go(node.right))
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in comparisons:
            return comparisons[type(node.ops[0])](go(node.left), go(node.comparators[0]))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
            name = node.func.id
            if name not in FUNCTIONS:
                raise StrategyError("unknown_function")
            args = [go(a) for a in node.args]
            if name == "where" and len(args) == 3:
                return pd.Series(np.where(*args), index=bars.index)
            if name == "abs" and len(args) == 1:
                return abs(args[0])
            if name == "clip" and len(args) == 3:
                return np.clip(*args)
            if name in ("ema", "mean", "std", "high", "low", "lag") and len(args) == 2:
                value, window = args
                minimum = 0 if name == "lag" else 2
                if type(window) is not int or not minimum <= window <= MAX_WINDOW:
                    raise StrategyError("invalid_causal_window")
                if not isinstance(value, pd.Series):
                    raise StrategyError("series_required")
                if name == "lag":
                    return value.shift(window)
                if name == "ema":
                    # A finite exponentially weighted window gives identical
                    # last-bar values in bounded live and historical contexts.
                    alpha = 2 / (window + 1)
                    weights = (1 - alpha) ** np.arange(window)
                    weights /= weights.sum()
                    data = np.convolve(value.to_numpy(), weights, mode="full")[:len(value)]
                    data[:window - 1] = np.nan
                    return pd.Series(data, index=value.index)
                method = {"mean": "mean", "std": "std", "high": "max", "low": "min"}[name]
                return getattr(value.rolling(window, min_periods=window), method)()
            raise StrategyError("invalid_function_arguments")
        raise StrategyError("unsupported_expression")

    try:
        values = visit(tree.body)
        result = pd.Series(values, index=bars.index, dtype=float)
        # Warm-up values may be undefined; infinities are never a warm-up.
        if np.isinf(result.to_numpy()).any() or result.iloc[MAX_WINDOW:].isna().any():
            raise StrategyError("nonfinite_signal")
        return np.sign(result.fillna(0)).astype(int).rename(None)
    except StrategyError:
        raise
    except (TypeError, ValueError, ZeroDivisionError, OverflowError, RecursionError):
        raise StrategyError("invalid_signal") from None


def freeze_dataset(bars: pd.DataFrame, embargo: int = EMBARGO) -> dict:
    if len(bars) < 500 or not bars.index.is_monotonic_increasing or bars.index.has_duplicates:
        raise StrategyError("insufficient_or_unordered_data")
    a, b = int(len(bars) * .6), int(len(bars) * .8)
    if a <= embargo:
        raise StrategyError("insufficient_training_after_embargo")
    # Hash the complete frozen version, not only timestamps: corrected OHLC values
    # are a new dataset, never a silently changed experiment.
    digest = hashlib.sha256(pd.util.hash_pandas_object(bars, index=True).values.tobytes()).hexdigest()
    return {"version": digest, "rows": len(bars), "start": bars.index[0].isoformat(),
            "end": bars.index[-1].isoformat(), "train_end": bars.index[a - embargo - 1].isoformat(),
            "validation_start": bars.index[a].isoformat(), "validation_end": bars.index[b - 1].isoformat(),
            "holdout_start": bars.index[b].isoformat(), "embargo": embargo,
            "holdout_consumed": False, "maximum_attempts": MAX_ATTEMPTS}


def partition(bars: pd.DataFrame, manifest: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = bars.loc[manifest["start"]:manifest["train_end"]]
    validation = bars.loc[manifest["validation_start"]:manifest["validation_end"]]
    if train.empty or validation.empty:
        raise StrategyError("frozen_data_missing")
    return train, validation


def execution_config(quantity: float = .1) -> ExecutionConfig:
    # Match target-position execution: exits come from the program. Do not test
    # favourable intrabar stops which the paper runner does not implement.
    return ExecutionConfig(quantity_oz=quantity, spread=.30, slippage=.05,
                           stop_distance=None, target_distance=None, max_holding_bars=None)


def evaluate(expression: str, bars: pd.DataFrame, quantity: float = .1) -> dict:
    raw = signals(expression, bars)
    effective, prior = [], 0
    for target in raw.to_numpy():
        prior = 0 if prior * target < 0 else int(target)
        effective.append(prior)
    return EventDrivenBacktester(execution_config(quantity)).run(bars, pd.Series(effective, index=bars.index))


def _finite(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def gates_for(metrics: dict, pnl: pd.Series, minimum_trades: int = MIN_TRADES) -> dict:
    bootstrap = bootstrap_trade_paths(pnl, samples=300)
    gates = {"minimum_trades": _finite(metrics.get("trades")) and metrics["trades"] >= minimum_trades,
             "positive_expectancy": _finite(metrics.get("expectancy")) and metrics["expectancy"] > 0,
             "net_profit": _finite(metrics.get("net_profit")) and metrics["net_profit"] > 0,
             "profit_factor": _finite(metrics.get("profit_factor")) and metrics["profit_factor"] >= 1.15,
             "drawdown": _finite(metrics.get("max_drawdown")) and metrics["max_drawdown"] >= MAX_DRAWDOWN,
             "bootstrap_positive": _finite(bootstrap.get("p05_net_pnl")) and bootstrap["p05_net_pnl"] > 0}
    return {"gates": gates, "bootstrap": bootstrap}


def assess(candidate: dict, bars: pd.DataFrame, manifest: dict, quantity: float = .1) -> dict:
    train, validation = partition(bars, manifest)
    training = evaluate(candidate["expression"], train, quantity)
    result = evaluate(candidate["expression"], validation, quantity)
    pnl = result["trades"].net_pnl if len(result["trades"]) else pd.Series(dtype=float)
    checks = gates_for(result["metrics"], pnl)
    # Disjoint chronological validation folds. Each prefix gives indicators their
    # causal warm-up, but only that fold's returns are evaluated.
    folds = []
    for positions in np.array_split(np.arange(len(validation)), 4):
        if len(positions):
            block = validation.iloc[positions]
            folds.append(evaluate(candidate["expression"], block, quantity)["metrics"])
    fraction = sum(m["net_profit"] > 0 for m in folds) / len(folds)
    checks["gates"]["positive_folds"] = fraction >= .75
    return {"candidate_id": identity(candidate), "dataset_version": manifest["version"],
            "training": training["metrics"], "metrics": result["metrics"], **checks,
            "folds": folds, "positive_fold_fraction": fraction,
            "execution": asdict(execution_config(quantity)), "holdout_consumed": False,
            "passed": all(checks["gates"].values())}


def evidence_digest(candidate: dict) -> str:
    """Binds the program, historical gates and prospective evidence together."""
    payload = {key: candidate.get(key) for key in ("id", "expression", "report", "forward", "dataset_version")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()
