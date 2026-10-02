from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Literal

import numpy as np
import pandas as pd


ExitReason = Literal["signal", "stop", "target", "time", "end"]


@dataclass(frozen=True)
class ExecutionConfig:
    initial_cash: float = 100_000.0
    quantity_oz: float = 1.0
    spread: float = 0.20
    slippage: float = 0.03
    commission_per_lot_side: float = 3.50
    ounces_per_lot: float = 100.0
    stop_distance: float | None = 2.0
    target_distance: float | None = 3.0
    max_holding_bars: int | None = 30
    intrabar_priority: Literal["stop", "target"] = "stop"
    # Annualised financing charged on any bar that follows a session gap, i.e. any
    # overnight hold. XAUUSD spot has no swap, but the position carries a real
    # funding cost, and `max_holding_bars` reaches 240 in the search grid, so
    # multi-day holds were modelled with zero carry. Expressed as a fraction of
    # notional per year, applied per crossed gap.
    annual_financing_rate: float = 0.0
    # Seconds; a plain number rather than a Timedelta so ``asdict(config)`` stays
    # JSON-serialisable, which every research report depends on.
    session_gap_seconds: float = 60.0

    def __post_init__(self) -> None:
        positive = ("initial_cash", "quantity_oz", "ounces_per_lot")
        if any(getattr(self, field) <= 0 for field in positive):
            raise ValueError("cash, quantity, and contract size must be positive")
        if self.spread < 0 or self.slippage < 0 or self.commission_per_lot_side < 0:
            raise ValueError("execution costs cannot be negative")
        if not math.isfinite(self.annual_financing_rate) or self.annual_financing_rate < 0:
            raise ValueError("annual_financing_rate must be finite and non-negative")
        if not math.isfinite(self.session_gap_seconds) or self.session_gap_seconds <= 0:
            raise ValueError("session_gap_seconds must be finite and positive")
        if self.intrabar_priority != "stop":
            # "target" resolves an ambiguous bar optimistically. The search grid
            # and the tournament gates never set it, so production stays
            # conservative, but it is an unguarded footgun for a config that can
            # reach a champion.
            raise ValueError("intrabar_priority must be 'stop'; 'target' is optimistic and not permitted")


@dataclass
class Trade:
    side: int
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: pd.Timestamp
    exit_price: float
    quantity_oz: float
    gross_pnl: float
    commission: float
    net_pnl: float
    bars_held: int
    exit_reason: ExitReason


class EventDrivenBacktester:
    """Deterministic bar-by-bar simulator with next-open signal execution.

    Signals are target positions in {-1, 0, 1}. A signal observed at a bar's
    close can only be executed at the following bar's open. When stop and target
    are both touched in one OHLC bar, the configured conservative priority is
    used because the true tick path is unknown.
    """

    def __init__(self, config: ExecutionConfig | None = None):
        self.config = config or ExecutionConfig()

    def run(self, bars: pd.DataFrame, signals: pd.Series) -> dict:
        required = {"open", "high", "low", "close"}
        if missing := required.difference(bars.columns):
            raise ValueError(f"missing bar columns: {sorted(missing)}")
        if bars.empty:
            raise ValueError("bars cannot be empty")
        frame = bars.sort_index().copy()
        signal = signals.reindex(frame.index).fillna(0).clip(-1, 1)
        signal = np.sign(signal).astype(int)
        timestamps=frame.index
        opens=frame["open"].to_numpy(dtype=float,copy=False)
        highs=frame["high"].to_numpy(dtype=float,copy=False)
        lows=frame["low"].to_numpy(dtype=float,copy=False)
        closes=frame["close"].to_numpy(dtype=float,copy=False)
        signal_values=signal.to_numpy(dtype=int,copy=False)
        # A bar whose predecessor is more than one interval away is an overnight
        # or weekend hold. Financing is charged on entering such a bar.
        gaps=frame.index.to_series().diff().dt.total_seconds()
        crossed_gap=(gaps>self.config.session_gap_seconds).fillna(False).to_numpy()
        cash = self.config.initial_cash
        position: dict | None = None
        trades: list[Trade] = []
        equity_rows: list[tuple[pd.Timestamp, float]] = []
        financing_total = 0.0

        def commission() -> float:
            return self.config.commission_per_lot_side * self.config.quantity_oz / self.config.ounces_per_lot

        def overnight_cost(price: float) -> float:
            """Financing for one crossed session gap, as a fraction of notional."""
            if not self.config.annual_financing_rate:
                return 0.0
            per_gap = self.config.annual_financing_rate / 365.25
            return per_gap * abs(price) * self.config.quantity_oz

        def fill_price(mid: float, side: int, opening: bool) -> float:
            direction = side if opening else -side
            return float(mid + direction * (self.config.spread / 2 + self.config.slippage))

        def close(timestamp: pd.Timestamp, mid: float, reason: ExitReason, bars_held: int) -> None:
            nonlocal cash, position
            assert position is not None
            exit_price = fill_price(mid, position["side"], False)
            gross = position["side"] * (exit_price - position["entry_price"]) * self.config.quantity_oz
            fees = position["entry_commission"] + commission()
            net = gross - fees
            cash += gross - commission()
            trades.append(Trade(position["side"], position["entry_time"], position["entry_price"], timestamp,
                                exit_price, self.config.quantity_oz, gross, fees, net, bars_held, reason))
            position = None

        for i,timestamp in enumerate(timestamps):
            # A hold carried across a session gap pays financing, charged on the
            # bar that crosses it and before any exit is evaluated: the position
            # was open across the closed market, so the cost is owed regardless of
            # what this bar then does.
            if position is not None and i > position["entry_i"] and crossed_gap[i]:
                carry = overnight_cost(closes[i - 1])
                financing_total += carry
                cash -= position["side"] * carry
            desired = int(signal_values[i - 1]) if i else 0
            if position is not None and desired != position["side"]:
                close(timestamp, opens[i], "signal", i - position["entry_i"])
            if position is None and desired:
                fee = commission()
                position = {"side": desired, "entry_time": timestamp, "entry_i": i,
                            "entry_price": fill_price(opens[i], desired, True), "entry_commission": fee}
                cash -= fee

            if position is not None:
                side = position["side"]
                entry = position["entry_price"]
                stop = entry - side * self.config.stop_distance if self.config.stop_distance is not None else None
                target = entry + side * self.config.target_distance if self.config.target_distance is not None else None
                stop_hit = stop is not None and (lows[i] <= stop if side > 0 else highs[i] >= stop)
                target_hit = target is not None and (highs[i] >= target if side > 0 else lows[i] <= target)
                if stop_hit and target_hit:
                    reason = self.config.intrabar_priority
                    close(timestamp, stop if reason == "stop" else target, reason, i - position["entry_i"] + 1)
                elif stop_hit:
                    close(timestamp, stop, "stop", i - position["entry_i"] + 1)
                elif target_hit:
                    close(timestamp, target, "target", i - position["entry_i"] + 1)
                elif self.config.max_holding_bars and i - position["entry_i"] + 1 >= self.config.max_holding_bars:
                    close(timestamp, closes[i], "time", i - position["entry_i"] + 1)

            marked = cash
            if position is not None:
                liquidation = fill_price(closes[i], position["side"], False)
                marked += position["side"] * (liquidation - position["entry_price"]) * self.config.quantity_oz - commission()
            equity_rows.append((timestamp, marked))

        if position is not None:
            close(timestamps[-1], closes[-1], "end", len(frame) - position["entry_i"])
            equity_rows[-1] = (frame.index[-1], cash)

        equity = pd.Series((value for _,value in equity_rows),index=timestamps,name="equity",dtype=float)
        ledger = pd.DataFrame([asdict(trade) for trade in trades])
        metrics = self._metrics(equity, ledger, frame)
        metrics["overnight_financing"] = float(financing_total)
        return {"metrics": metrics, "trades": ledger, "equity": equity}

    def _metrics(self, equity: pd.Series, trades: pd.DataFrame, bars: pd.DataFrame) -> dict:
        returns = equity.pct_change().fillna(0)
        drawdown = equity / equity.cummax() - 1
        downside = returns[returns < 0]
        years = max((equity.index[-1] - equity.index[0]).total_seconds() / (365.25 * 86400), 1 / 365.25)
        pnl = trades.net_pnl if not trades.empty else pd.Series(dtype=float)
        profits = pnl[pnl > 0].sum()
        losses = -pnl[pnl < 0].sum()
        if trades.empty:
            implicit_costs = pd.Series(dtype=float)
            pre_cost_pnl = pd.Series(dtype=float)
            turnover = 0.0
        else:
            implicit_cost_per_trade = self.config.quantity_oz * (self.config.spread + 2 * self.config.slippage)
            implicit_costs = pd.Series(implicit_cost_per_trade, index=trades.index, dtype=float)
            pre_cost_pnl = trades.gross_pnl + implicit_costs
            half_spread_slippage = self.config.spread / 2 + self.config.slippage
            entry_mid = trades.entry_price - trades.side * half_spread_slippage
            exit_mid = trades.exit_price + trades.side * half_spread_slippage
            turnover = float((trades.quantity_oz * (entry_mid.abs() + exit_mid.abs())).sum())
        total_implicit_cost = float(implicit_costs.sum())
        total_commission = float(trades.commission.sum()) if not trades.empty else 0.0
        total_cost = total_implicit_cost + total_commission
        gross_profit = float(pre_cost_pnl.sum())
        if abs(gross_profit) < 1e-10:
            gross_profit = 0.0
        positive_pre_cost = float(pre_cost_pnl[pre_cost_pnl > 0].sum())
        tail_count = max(1, int(np.ceil(len(pnl) * 0.05))) if len(pnl) else 0
        expected_shortfall = float(pnl.nsmallest(tail_count).mean()) if tail_count else 0.0
        positive_pnl = pnl[pnl > 0].sort_values(ascending=False)
        concentration_count = max(1, int(np.ceil(len(positive_pnl) * 0.10))) if len(positive_pnl) else 0
        profit_concentration = (float(positive_pnl.iloc[:concentration_count].sum() / positive_pnl.sum())
                                if concentration_count and positive_pnl.sum() else 0.0)
        scale = np.sqrt(252 * 1440)
        return {
            "initial_cash": self.config.initial_cash,
            "final_equity": float(equity.iloc[-1]),
            "net_profit": float(equity.iloc[-1] - self.config.initial_cash),
            "gross_profit": gross_profit,
            "implicit_execution_cost": total_implicit_cost,
            "commission_cost": total_commission,
            "total_cost": total_cost,
            "cost_to_gross_profit_ratio": float(total_cost / positive_pre_cost) if positive_pre_cost else None,
            "turnover": turnover,
            "expected_shortfall": expected_shortfall,
            "profit_concentration": profit_concentration,
            "cagr": _cagr(float(equity.iloc[-1]), self.config.initial_cash, years),
            # Undefined rather than zero. A strategy with no losing trades has an
            # infinite profit factor, and `inf` was the value that broke every
            # report write: json.dumps(..., allow_nan=False) raises, so the *best*
            # strategy in the space could not be recorded at all. Every gate treats
            # None as a failure, which is the conservative direction.
            "sharpe": float(scale * returns.mean() / returns.std()) if returns.std() else None,
            "sortino": float(scale * returns.mean() / downside.std()) if len(downside) > 1 and downside.std() else None,
            "max_drawdown": float(drawdown.min()),
            "profit_factor": _profit_factor(profits, losses),
            "win_rate": float((pnl > 0).mean()) if len(pnl) else None,
            "expectancy": float(pnl.mean()) if len(pnl) else None,
            "trades": int(len(trades)),
            "average_hold_bars": float(trades.bars_held.mean()) if len(trades) else None,
            # Guarded on len(trades), not len(bars): with no trades the ledger is
            # an empty frame with no columns, so touching .bars_held raises.
            "exposure": float(sum(trades.bars_held) / len(bars)) if len(trades) and len(bars) else None,
        }


def metric_above(value: float | None, threshold: float) -> bool:
    """True only when a metric is defined and strictly above ``threshold``.

    ``None`` is how the engine reports an undefined metric (no losing trades, no
    return variance, no trades at all). Comparing it directly raises TypeError, and
    treating it as zero would let an unmeasurable strategy pass a zero threshold.
    Every gate in this repository uses these helpers so an undefined metric always
    fails closed.
    """
    return value is not None and float(value) > threshold


def metric_at_least(value: float | None, threshold: float) -> bool:
    return value is not None and float(value) >= threshold


def _profit_factor(profits: float, losses: float) -> float | None:
    """Gross profit over gross loss, or ``None`` when it is undefined.

    ``None`` covers no trades at all and no losing trades. The previous ``inf``
    was not just a serialisation problem: ``inf >= 1.0`` passes the profit-factor
    gate, so the metric also inverted a threshold check in the strategy's favour.
    """
    if losses > 0:
        return float(profits / losses)
    return None if profits > 0 else 0.0


def _cagr(final_equity: float, initial_cash: float, years: float) -> float | None:
    """Compound annual growth rate, or ``None`` when the account is not positive.

    A negative or zero terminal equity raised a fractional power to a fractional
    exponent, which yields NaN (or a complex number) and again broke the report
    write for exactly the strategies an operator most needs to see.
    """
    if final_equity <= 0 or initial_cash <= 0:
        return None
    value = (final_equity / initial_cash) ** (1 / years) - 1
    return float(value) if math.isfinite(value) else None
