"""Fail-closed operational loop for explicitly enabled cTrader demo automation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import tempfile
import time
from typing import Any, Callable, Protocol

from .demo_execution import NormalizedDecision, PaperToCTraderDemoCoordinator


@dataclass(frozen=True)
class DemoRunnerConfig:
    enabled: bool
    poll_seconds: float = 30.0
    max_consecutive_failures: int = 3
    max_market_data_age_seconds: float = 60.0
    status_path: Path = Path("reports/demo_runner_status.json")

    @classmethod
    def from_env(cls) -> "DemoRunnerConfig":
        return cls(
            enabled=os.getenv("CTRADER_AUTOMATION_ENABLED") == "true",
            poll_seconds=float(os.getenv("CTRADER_AUTOMATION_POLL_SECONDS", "30")),
            max_consecutive_failures=int(os.getenv("CTRADER_AUTOMATION_MAX_CONSECUTIVE_FAILURES", "3")),
            max_market_data_age_seconds=float(os.getenv("CTRADER_AUTOMATION_MAX_MARKET_DATA_AGE_SECONDS", "60")),
            status_path=Path(os.getenv("CTRADER_AUTOMATION_STATUS_PATH", "reports/demo_runner_status.json")),
        )

    def validate(self) -> None:
        if (not isinstance(self.poll_seconds, (int, float)) or isinstance(self.poll_seconds, bool) or
                not math.isfinite(self.poll_seconds) or self.poll_seconds <= 0):
            raise ValueError("poll_seconds must be finite and positive")
        if (not isinstance(self.max_consecutive_failures, int) or isinstance(self.max_consecutive_failures, bool) or
                self.max_consecutive_failures <= 0):
            raise ValueError("max_consecutive_failures must be a positive integer")
        if (not isinstance(self.max_market_data_age_seconds, (int, float)) or
                isinstance(self.max_market_data_age_seconds, bool) or
                not math.isfinite(self.max_market_data_age_seconds) or self.max_market_data_age_seconds <= 0):
            raise ValueError("max_market_data_age_seconds must be finite and positive")


@dataclass(frozen=True)
class MarketData:
    price: float
    observed_at: datetime


class MarketDataSource(Protocol):
    """Read-only source for the latest executable market observation."""
    def read(self) -> MarketData: ...


class DecisionSource(Protocol):
    """Read-only strategy proposal source; ``None`` means no proposed action."""
    def read(self, market_data: MarketData) -> NormalizedDecision | None: ...


class DemoLifecycle(Protocol):
    def start(self, reason: str) -> None: ...
    def stop(self, reason: str) -> None: ...
    def reconcile_after_restart(self) -> bool: ...


class DemoAutomationRunner:
    """Poll injected sources only after explicit enablement and reconciliation."""
    def __init__(self, coordinator: PaperToCTraderDemoCoordinator, market_data_source: MarketDataSource,
                 decision_source: DecisionSource, config: DemoRunnerConfig | None = None,
                 alert_sink: Callable[[dict[str, Any]], None] | None = None,
                 clock: Callable[[], datetime] | None = None, sleeper: Callable[[float], None] = time.sleep):
        self.coordinator = coordinator
        self.market_data_source = market_data_source
        self.decision_source = decision_source
        self.config = config or DemoRunnerConfig.from_env()
        self.config.validate()
        self.alert_sink = alert_sink
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.sleeper = sleeper
        self.running = False
        self.consecutive_failures = 0

    @property
    def demo_adapter(self) -> DemoLifecycle:
        return self.coordinator.demo_adapter  # type: ignore[return-value]

    def start(self) -> bool:
        """Reconcile first, then make the explicitly enabled paper/demo pair runnable."""
        if not self.config.enabled:
            self._record("disabled")
            return False
        try:
            if not self.demo_adapter.reconcile_after_restart():
                raise RuntimeError("startup_reconciliation_failed")
            self.demo_adapter.start("explicit demo automation enabled")
            self.coordinator.paper_trading.start("explicit demo automation enabled")
        except Exception:
            self._stop("startup_reconciliation_failed")
            return False
        self.running = True
        self.consecutive_failures = 0
        self._record("running")
        return True

    def run_cycle(self) -> dict[str, Any]:
        if not self.running:
            return self._record("not_running")
        try:
            market_data = self.market_data_source.read()
            self._validate_market_data(market_data)
            if self._market_data_age(market_data) > self.config.max_market_data_age_seconds:
                return self._record("stale_market_data")
            decision = self.decision_source.read(market_data)
            if decision is None:
                self.consecutive_failures = 0
                return self._record("no_decision")
            result = self.coordinator.execute(decision, market_data.price, self._now())
            if result.get("paper", {}).get("accepted") and not result.get("accepted"):
                return self._stop("broker_execution_failed", result=result)
            self.consecutive_failures = 0
            return self._record("executed", result=result)
        except Exception as exc:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.config.max_consecutive_failures:
                return self._stop("max_consecutive_failures", error_type=type(exc).__name__)
            else:
                return self._record("cycle_failure", error_type=type(exc).__name__)

    def run_forever(self) -> None:
        if not self.start():
            return
        while self.running:
            self.run_cycle()
            if self.running:
                self.sleeper(self.config.poll_seconds)

    def status(self) -> dict[str, Any]:
        return {"running": self.running, "consecutive_failures": self.consecutive_failures}

    def _stop(self, reason: str, **details: Any) -> dict[str, Any]:
        self.running = False
        # Attempt both stops even if one persistence backend is unavailable.
        for lifecycle in (self.coordinator.paper_trading, self.demo_adapter):
            try:
                lifecycle.stop(reason)
            except Exception as exc:
                details.setdefault("stop_error_type", type(exc).__name__)
        return self._record("stopped", reason=reason, **details)

    def _now(self) -> datetime:
        now = self.clock()
        if not isinstance(now, datetime) or now.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return now.astimezone(timezone.utc)

    def _market_data_age(self, market_data: MarketData) -> float:
        return (self._now() - market_data.observed_at.astimezone(timezone.utc)).total_seconds()

    @staticmethod
    def _validate_market_data(market_data: MarketData) -> None:
        if (not isinstance(market_data, MarketData) or not isinstance(market_data.price, (int, float)) or
                isinstance(market_data.price, bool) or not math.isfinite(market_data.price) or market_data.price <= 0 or
                not isinstance(market_data.observed_at, datetime) or market_data.observed_at.tzinfo is None):
            raise ValueError("market data must contain a finite positive price and timezone-aware observation time")

    def _record(self, state: str, **details: Any) -> dict[str, Any]:
        status = {"state": state, "recorded_at": self._now().isoformat(), **self.status(), **details}
        self._write_status(status)
        if state in {"stopped", "cycle_failure"} and self.alert_sink:
            try:
                self.alert_sink(status)
            except Exception:
                pass
        return status

    def _write_status(self, status: dict[str, Any]) -> None:
        path = self.config.status_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as artifact:
            json.dump(status, artifact, sort_keys=True, allow_nan=False)
            artifact.write("\n")
            artifact.flush()
            os.fsync(artifact.fileno())
            temporary_path = Path(artifact.name)
        os.replace(temporary_path, path)
