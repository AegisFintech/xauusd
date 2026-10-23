"""One shared, cost-aware target execution path for prospective and paper runs."""
from datetime import datetime
import hashlib
import math

import pandas as pd

from .lab_strategy import execution_config, signals
from .paper_trading import PaperDecision, validated_paper_state, _default_state


def quote_valid(quote, now: datetime) -> bool:
    if not isinstance(quote, dict) or quote.get("source") != "ctrader_demo" or quote.get("symbol") != "XAUUSD":
        return False
    try:
        bid, ask = float(quote["bid"]), float(quote["ask"])
        if not math.isfinite(bid) or not math.isfinite(ask) or not 0 < bid <= ask:
            return False
        return all(-1 <= (pd.Timestamp(now) - pd.Timestamp(quote[key])).total_seconds() <= 5
                   for key in ("observed_at", "received_at") if quote.get(key)) and bool(quote.get("observed_at")) and bool(quote.get("received_at"))
    except (KeyError, TypeError, ValueError):
        return False


def target_decision(row, bars, state, now, quote, quantity):
    if not quote_valid(quote, now) or bars.empty:
        return None
    bar = bars.index[-1].to_pydatetime()
    desired = float(signals(row["expression"], bars.tail(8192)).iloc[-1]) * quantity
    position = float(state["position"])
    if position * desired < 0:
        desired = 0.0
    delta = desired - position
    if abs(delta) < 1e-9:
        return None
    side = "BUY" if delta > 0 else "SELL"
    execution = execution_config(quantity)
    # Encode commission in the executable side price. PaperTrading owns its
    # existing ledger and gates; no extra cash edits or bypass path is needed.
    cost = execution.slippage + execution.commission_per_lot_side / execution.ounces_per_lot
    price = float(quote["ask"]) + cost if side == "BUY" else float(quote["bid"]) - cost
    key = row["id"] + ":" + bar.isoformat()
    return PaperDecision("lab:" + hashlib.sha256(key.encode()).hexdigest(), "XAUUSD", side, abs(delta), price, bar)


class ShadowStore:
    """A prospective simulation account; never selects or replaces real state."""
    def __init__(self, payload=None):
        self.payload = payload or {"state": _default_state(100000), "last_result": None}
        if payload is None:
            self.payload["state"].update(stopped=False, kill_switch_reason="prospective_simulation")

    def initialize(self):
        pass

    def state(self):
        state = validated_paper_state(self.payload["state"], 100000)
        self.payload["state"] = state
        return state

    def run(self, decision_id, transition):
        prior = self.payload.get("last_result")
        if prior and prior["decision_id"] == decision_id:
            return dict(prior, replayed=True)
        result = transition(self.state())
        self.payload["last_result"] = dict(result, decision_id=decision_id)
        return result

    def set_kill_switch(self, stopped, reason):
        self.state().update(stopped=stopped, kill_switch_reason=reason)
