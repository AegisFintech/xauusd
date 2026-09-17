from pathlib import Path
import json

import pytest

from xauusd.core import synthetic_bars
from xauusd.experiment_registry import ExperimentRegistry
from xauusd.shadow_trading import ShadowRiskLimits, ShadowTradingReadiness
from tests.memory_registry import MemoryRegistry


class Dataset:
 def active(self): return {"version":"v1"}


class ChampionRegistry(MemoryRegistry):
 def champion(self,dataset_version): return {"experiment_id":1}


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
 assert json.loads((tmp_path/"state.json").read_text())["status"]=="emergency_stopped"
 assert json.loads((tmp_path/"STOP").read_text())["reason"]=="test"


def test_invalid_risk_limits_are_rejected(tmp_path):
 with pytest.raises(ValueError,match="max_drawdown"):
  ShadowTradingReadiness(MemoryRegistry(),Dataset(),tmp_path/"state.json",tmp_path/"STOP",
                         limits=ShadowRiskLimits(max_drawdown=1.1))


def test_empty_data_is_recorded_as_flat(tmp_path):
 manager=ShadowTradingReadiness(ChampionRegistry(),Dataset(),tmp_path/"state.json",tmp_path/"STOP",
                                alert_path=tmp_path/"alert.json")
 result=manager.evaluate_signal(synthetic_bars(0))
 assert result["status"]=="flat_no_data" and result["signal"]==0
 assert json.loads((tmp_path/"alert.json").read_text())["status"]=="flat_no_data"


def test_readiness_never_enables_execution(tmp_path):
 manager=ShadowTradingReadiness(MemoryRegistry(),Dataset(),tmp_path/"state.json",tmp_path/"STOP")
 status=manager.readiness()
 assert status["gates"]["explicit_activation"] is False and status["ready"] is False


def test_research_package_contains_no_broker_order_connector():
 source="\n".join(path.read_text(errors="ignore") for path in Path("xauusd").glob("*.py"))
 assert all(term not in source for term in ("submit_order","place_order","broker_order","MetaTrader5","ccxt"))
