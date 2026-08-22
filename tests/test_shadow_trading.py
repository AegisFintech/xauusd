from pathlib import Path

from xauusd.core import synthetic_bars
from xauusd.experiment_registry import ExperimentRegistry
from xauusd.shadow_trading import ShadowTradingReadiness
from tests.memory_registry import MemoryRegistry


class Dataset:
 def active(self): return {"version":"v1"}


def test_shadow_is_hard_blocked_without_champion(tmp_path):
 manager=ShadowTradingReadiness(MemoryRegistry(),Dataset(),tmp_path/"state.json",tmp_path/"STOP")
 status=manager.readiness()
 assert not status["ready"] and status["mode"]=="shadow_only"
 assert not status["gates"]["holdout_qualified_champion"] and status["gates"]["execution_connector_absent"]


def test_emergency_stop_forces_flat_signal(tmp_path):
 manager=ShadowTradingReadiness(MemoryRegistry(),Dataset(),tmp_path/"state.json",tmp_path/"STOP")
 manager.emergency_stop("test")
 result=manager.evaluate_signal(synthetic_bars(500))
 assert result["status"]=="emergency_stopped" and result["signal"]==0


def test_readiness_never_enables_execution(tmp_path):
 manager=ShadowTradingReadiness(MemoryRegistry(),Dataset(),tmp_path/"state.json",tmp_path/"STOP")
 status=manager.readiness()
 assert status["gates"]["explicit_activation"] is False and status["ready"] is False


def test_research_package_contains_no_broker_order_connector():
 source="\n".join(path.read_text(errors="ignore") for path in Path("xauusd").glob("*.py"))
 assert all(term not in source for term in ("submit_order","place_order","broker_order","MetaTrader5","ccxt"))
