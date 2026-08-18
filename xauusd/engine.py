from __future__ import annotations

from dataclasses import asdict, dataclass
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

    def __post_init__(self) -> None:
        positive = ("initial_cash", "quantity_oz", "ounces_per_lot")
        if any(getattr(self, field) <= 0 for field in positive):
            raise ValueError("cash, quantity, and contract size must be positive")
        if self.spread < 0 or self.slippage < 0 or self.commission_per_lot_side < 0:
            raise ValueError("execution costs cannot be negative")


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
        cash = self.config.initial_cash
        position: dict | None = None
        trades: list[Trade] = []
        equity_rows: list[tuple[pd.Timestamp, float]] = []

        def commission() -> float:
            return self.config.commission_per_lot_side * self.config.quantity_oz / self.config.ounces_per_lot

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

        for i, (timestamp, bar) in enumerate(frame.iterrows()):
            desired = int(signal.iloc[i - 1]) if i else 0
            if position is not None and desired != position["side"]:
                close(timestamp, float(bar.open), "signal", i - position["entry_i"])
            if position is None and desired:
                fee = commission()
                position = {"side": desired, "entry_time": timestamp, "entry_i": i,
                            "entry_price": fill_price(float(bar.open), desired, True), "entry_commission": fee}
                cash -= fee

            if position is not None:
                side = position["side"]
                entry = position["entry_price"]
                stop = entry - side * self.config.stop_distance if self.config.stop_distance is not None else None
                target = entry + side * self.config.target_distance if self.config.target_distance is not None else None
                stop_hit = stop is not None and (float(bar.low) <= stop if side > 0 else float(bar.high) >= stop)
                target_hit = target is not None and (float(bar.high) >= target if side > 0 else float(bar.low) <= target)
                if stop_hit and target_hit:
                    reason = self.config.intrabar_priority
                    close(timestamp, stop if reason == "stop" else target, reason, i - position["entry_i"] + 1)
                elif stop_hit:
                    close(timestamp, stop, "stop", i - position["entry_i"] + 1)
                elif target_hit:
                    close(timestamp, target, "target", i - position["entry_i"] + 1)
                elif self.config.max_holding_bars and i - position["entry_i"] + 1 >= self.config.max_holding_bars:
                    close(timestamp, float(bar.close), "time", i - position["entry_i"] + 1)

            marked = cash
            if position is not None:
                liquidation = fill_price(float(bar.close), position["side"], False)
                marked += position["side"] * (liquidation - position["entry_price"]) * self.config.quantity_oz - commission()
            equity_rows.append((timestamp, marked))

        if position is not None:
            close(frame.index[-1], float(frame.close.iloc[-1]), "end", len(frame) - position["entry_i"])
            equity_rows[-1] = (frame.index[-1], cash)

        equity = pd.Series(dict(equity_rows), name="equity", dtype=float)
        ledger = pd.DataFrame([asdict(trade) for trade in trades])
        return {"metrics": self._metrics(equity, ledger, frame), "trades": ledger, "equity": equity}

    def _metrics(self, equity: pd.Series, trades: pd.DataFrame, bars: pd.DataFrame) -> dict:
        returns = equity.pct_change().fillna(0)
        drawdown = equity / equity.cummax() - 1
        downside = returns[returns < 0]
        years = max((equity.index[-1] - equity.index[0]).total_seconds() / (365.25 * 86400), 1 / 365.25)
        pnl = trades.net_pnl if not trades.empty else pd.Series(dtype=float)
        profits = pnl[pnl > 0].sum()
        losses = -pnl[pnl < 0].sum()
        scale = np.sqrt(252 * 1440)
        return {
            "initial_cash": self.config.initial_cash,
            "final_equity": float(equity.iloc[-1]),
            "net_profit": float(equity.iloc[-1] - self.config.initial_cash),
            "cagr": float((equity.iloc[-1] / self.config.initial_cash) ** (1 / years) - 1),
            "sharpe": float(scale * returns.mean() / returns.std()) if returns.std() else 0.0,
            "sortino": float(scale * returns.mean() / downside.std()) if len(downside) > 1 and downside.std() else 0.0,
            "max_drawdown": float(drawdown.min()),
            "profit_factor": float(profits / losses) if losses else (float("inf") if profits else 0.0),
            "win_rate": float((pnl > 0).mean()) if len(pnl) else 0.0,
            "expectancy": float(pnl.mean()) if len(pnl) else 0.0,
            "trades": int(len(trades)),
            "average_hold_bars": float(trades.bars_held.mean()) if len(trades) else 0.0,
            "exposure": float(sum(trades.bars_held) / len(bars)) if len(trades) else 0.0,
        }
