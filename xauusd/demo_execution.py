"""Coordinates accepted paper decisions with explicitly started cTrader demo execution."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
from typing import Any, Protocol

from .ctrader_demo import CTraderOrder
from .paper_trading import PaperDecision, PaperTrading


@dataclass(frozen=True)
class NormalizedDecision:
    """Strategy proposal expressed in configured paper-trading quantity units."""
    decision_id: str
    symbol: str
    side: str
    quantity: float
    market_data_at: datetime


@dataclass(frozen=True)
class CTraderVolumeConversion:
    """Explicit conversion from paper quantity units to cTrader volume-in-cents units."""
    ctrader_volume_per_paper_unit: int

    def validate(self) -> None:
        if (not isinstance(self.ctrader_volume_per_paper_unit, int) or
                isinstance(self.ctrader_volume_per_paper_unit, bool) or
                self.ctrader_volume_per_paper_unit <= 0):
            raise ValueError("ctrader_volume_per_paper_unit must be a positive integer")

    def to_volume(self, quantity: float) -> int:
        self.validate()
        if (not isinstance(quantity, (int, float)) or isinstance(quantity, bool) or
                not math.isfinite(quantity) or quantity <= 0):
            raise ValueError("paper quantity must be finite and positive")
        volume = float(quantity * self.ctrader_volume_per_paper_unit)
        if not volume.is_integer():
            raise ValueError("paper quantity does not convert to a whole cTrader volume")
        return int(volume)


class DemoExecutor(Protocol):
    def execute(self, order: CTraderOrder) -> dict[str, Any]: ...
    def stop(self, reason: str) -> None: ...


@dataclass(frozen=True)
class CTraderVolumePolicy:
    """Broker-declared volume constraints; a volume failing any rule must be rejected before execution."""
    min_volume: int
    max_volume: int
    step_volume: int

    def validate(self) -> None:
        for value in (self.min_volume, self.max_volume, self.step_volume):
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError("broker volume bounds must be positive integers")
        if self.min_volume > self.max_volume:
            raise ValueError("broker min_volume cannot exceed max_volume")

    def reason(self, volume: int) -> str | None:
        """Return a rejection reason when volume violates broker constraints, else None."""
        if not isinstance(volume, int) or isinstance(volume, bool):
            return "volume_is_not_integer"
        if volume < self.min_volume:
            return "volume_below_broker_minimum"
        if volume > self.max_volume:
            return "volume_above_broker_maximum"
        if (volume - self.min_volume) % self.step_volume != 0:
            return "volume_not_aligned_to_broker_step"
        return None

    @classmethod
    def from_metadata(cls, metadata: Any) -> "CTraderVolumePolicy":
        metadata.validate()
        return cls(metadata.min_volume, metadata.max_volume, metadata.step_volume)


class PaperToCTraderDemoCoordinator:
    """Runs paper risk first; execution lifecycle remains explicitly operator controlled."""
    def __init__(self, paper_trading: PaperTrading, demo_adapter: DemoExecutor | None = None,
                 volume_conversion: CTraderVolumeConversion | None = None,
                 volume_policy: CTraderVolumePolicy | None = None,
                 paper_only: bool = False):
        self.paper_trading = paper_trading
        self.demo_adapter = demo_adapter
        self.volume_conversion = volume_conversion
        self.volume_policy = volume_policy
        self.paper_only = paper_only
        if not paper_only:
            if self.demo_adapter is None:
                raise ValueError("demo adapter is required unless paper_only is set")
            if self.volume_conversion is None:
                raise ValueError("volume conversion is required unless paper_only is set")
            self.volume_conversion.validate()
            if self.volume_policy is not None:
                self.volume_policy.validate()

    def execute(self, decision: NormalizedDecision, market_price: float, now: datetime) -> dict[str, Any]:
        """Evaluate paper risk first; broker submission only happens behind all gates."""
        if self.paper_only:
            return self._execute_paper_only(decision, market_price, now)
        assert self.demo_adapter is not None and self.volume_conversion is not None
        try:
            volume = self.volume_conversion.to_volume(decision.quantity)
        except (ValueError, TypeError) as exc:
            return {"accepted": False, "decision_id": decision.decision_id,
                    "reason": "INVALID_VOLUME", "detail": str(exc)}
        if self.volume_policy is not None:
            policy_reason = self.volume_policy.reason(volume)
            if policy_reason is not None:
                return {"accepted": False, "decision_id": decision.decision_id,
                        "reason": "VOLUME_POLICY", "detail": policy_reason}
        paper_decision = PaperDecision(decision.decision_id, decision.symbol, decision.side,
                                       decision.quantity, market_price, decision.market_data_at)
        paper_outcome = self.paper_trading.evaluate(paper_decision, now)
        if not paper_outcome["accepted"]:
            return {"accepted": False, "decision_id": decision.decision_id, "paper": paper_outcome}
        try:
            order = CTraderOrder(decision.decision_id, decision.side, volume)
            demo_outcome = self.demo_adapter.execute(order)
        except Exception as exc:
            demo_outcome = {"accepted": False, "request_id": decision.decision_id,
                            "reason": "BROKER_ERROR", "error_type": type(exc).__name__}
        self._audit_outcome(decision.decision_id, demo_outcome)
        if not demo_outcome.get("accepted", False):
            reason = "broker_execution_failed"
            self.paper_trading.stop(reason)
            self.demo_adapter.stop(reason)
        return {"accepted": bool(demo_outcome.get("accepted", False)), "decision_id": decision.decision_id,
                "paper": paper_outcome, "demo": demo_outcome}

    def _execute_paper_only(self, decision: NormalizedDecision, market_price: float, now: datetime) -> dict[str, Any]:
        """Broker-free validation of the paper pipeline; no adapter, volume, or kill-switch changes."""
        paper_decision = PaperDecision(decision.decision_id, decision.symbol, decision.side,
                                       decision.quantity, market_price, decision.market_data_at)
        paper_outcome = self.paper_trading.evaluate(paper_decision, now)
        demo_outcome = {"accepted": False, "request_id": decision.decision_id, "reason": "PAPER_ONLY_MODE"}
        self._audit_outcome(decision.decision_id, demo_outcome)
        return {"accepted": False, "decision_id": decision.decision_id, "paper": paper_outcome,
                "demo": demo_outcome, "paper_only": True}

    def _audit_outcome(self, decision_id: str, outcome: dict[str, Any]) -> None:
        """Use the adapter's persistent audit store when the concrete adapter exposes it."""
        store = getattr(self.demo_adapter, "store", None)
        audit = getattr(store, "audit", None)
        if callable(audit):
            audit("paper_demo_execution_outcome", {
                "decision_id": decision_id,
                "request_id": outcome.get("request_id"),
                "accepted": bool(outcome.get("accepted", False)),
                "reason": outcome.get("reason"),
                "error_type": outcome.get("error_type"),
            })
