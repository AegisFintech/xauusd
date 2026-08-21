"""Secret-free deterministic parity fixture for the runtime container."""

from __future__ import annotations

import json
import hashlib

import numpy as np
import pandas as pd

from xauusd.engine import EventDrivenBacktester, ExecutionConfig


def main() -> None:
    rng = np.random.default_rng(20260821)
    rows = 10_000
    close = 2_400 + np.cumsum(rng.normal(0, 0.7, rows))
    bars = pd.DataFrame(
        {
            "open": close + rng.normal(0, 0.08, rows),
            "high": close + rng.uniform(0.1, 1.8, rows),
            "low": close - rng.uniform(0.1, 1.8, rows),
            "close": close,
        },
        index=pd.date_range("2026-01-01", periods=rows, freq="min", tz="UTC"),
    )
    signals = pd.Series(rng.integers(-1, 2, rows), index=bars.index)
    config = ExecutionConfig(
        quantity_oz=3,
        spread=0.23,
        slippage=0.04,
        commission_per_lot_side=3.7,
        stop_distance=1.7,
        target_distance=2.4,
        max_holding_bars=17,
    )
    result = EventDrivenBacktester(config).run(bars, signals)
    trades = result["trades"]
    payload = {
        "fixture": "container-parity-v1",
        "seed": 20260821,
        "metrics": result["metrics"],
        "trade_rows": len(trades),
        "trade_digest": hashlib.sha256(
            pd.util.hash_pandas_object(trades, index=True).values.tobytes()
        ).hexdigest(),
        "equity_digest": hashlib.sha256(
            pd.util.hash_pandas_object(result["equity"], index=True).values.tobytes()
        ).hexdigest(),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
