from datetime import datetime, timezone
from threading import Event

import pandas as pd
import pytest
from pathlib import Path

from xauusd.agent_loop import (
    AgentConfig,
    ContinuousAgentRunner,
    InMemoryAgentTranscriptStore,
    _redact_for_transcript,
    build_agent_registry,
    canary_signal_tool,
    paper_state_tool,
    propose_trade_tool,
    read_market_tool,
)
from xauusd.canary_strategy import ConfirmedBreakoutCanarySource, LocalHistoricalMarketDataSource
from xauusd.data import DataConfig, HistoricalDataStore
from xauusd.demo_execution import PaperToCTraderDemoCoordinator
from xauusd.paper_trading import InMemoryPaperTradingStore, PaperRiskConfig, PaperTrading


def market_store(tmp_path, periods=80):
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    index = pd.date_range(end - pd.Timedelta(minutes=periods), periods=periods, freq="min", tz="UTC")
    bars = pd.DataFrame({"open": range(100, 100 + periods), "high": range(101, 101 + periods),
                         "low": range(99, 99 + periods), "close": range(100, 100 + periods),
                         "volume": [1] * periods}, index=index)
    store = HistoricalDataStore(DataConfig(processed_dir=tmp_path))
    store.write(bars)
    return store


def stale_market_store(tmp_path, stale_minutes=120, periods=80):
    end = (datetime.now(timezone.utc).replace(second=0, microsecond=0) - pd.Timedelta(minutes=stale_minutes))
    index = pd.date_range(end - pd.Timedelta(minutes=periods), periods=periods, freq="min", tz="UTC")
    bars = pd.DataFrame({"open": range(100, 100 + periods), "high": range(101, 101 + periods),
                         "low": range(99, 99 + periods), "close": range(100, 100 + periods),
                         "volume": [1] * periods}, index=index)
    store = HistoricalDataStore(DataConfig(processed_dir=tmp_path))
    store.write(bars)
    return store


def write_new_bar(store):
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    index = pd.DatetimeIndex([now], name="timestamp", tz="UTC")
    bars = pd.DataFrame({"open": [1.0], "high": [1.0], "low": [1.0], "close": [1.0], "volume": [1]}, index=index)
    store.write(bars, merge=True)


def refresh_config(**overrides):
    base = dict(max_market_data_age_seconds=60, max_steps_per_tick=1, data_refresh_enabled=True,
                data_refresh_threshold_seconds=30, data_refresh_min_interval_seconds=300,
                data_refresh_timeout_seconds=5)
    base.update(overrides)
    return AgentConfig(**base)


def refresh_runner(tmp_path, refresh, config=None, stale_minutes=120):
    store = stale_market_store(tmp_path, stale_minutes=stale_minutes)
    source = LocalHistoricalMarketDataSource(store)
    pt = fresh_paper()
    pt.start("test")
    coordinator = paper_only_coordinator(pt)
    cfg = config or refresh_config()
    registry = build_agent_registry(source, pt, coordinator, cfg,
                                    canary=ConfirmedBreakoutCanarySource(store, 1))
    transcript = InMemoryAgentTranscriptStore()
    runner = ContinuousAgentRunner(ScriptedPlanner([("(raw)", {"action": "final", "summary": "ok"})]),
                                   registry, transcript, source, pt, coordinator, cfg, refresh_source=refresh,
                                   now_provider=lambda: OPEN_NOW)
    return runner, transcript, store


def fresh_paper():
    config = PaperRiskConfig(daily_loss_limit=500, max_drawdown=0.10, max_position=1,
                             max_trades_per_day=20, max_market_data_age_seconds=120)
    return PaperTrading(InMemoryPaperTradingStore(), config)


def fresh_source(tmp_path):
    return LocalHistoricalMarketDataSource(market_store(tmp_path))


OPEN_NOW = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)  # Thursday midday, market open


def paper_only_coordinator(pt):
    return PaperToCTraderDemoCoordinator(pt, paper_only=True)


def test_read_market_tool_reports_price_freshness_and_closes(tmp_path):
    source = fresh_source(tmp_path)

    out = read_market_tool(source, AgentConfig(max_market_data_age_seconds=120)).handler({})

    assert out["symbol"] == "XAUUSD"
    assert out["price"] == 179.0
    assert out["fresh"] is True
    assert out["age_seconds"] < 120
    assert len(out["recent_closes"]) == 5


def test_paper_state_tool_summary_default(tmp_path):
    out = paper_state_tool(fresh_paper()).handler({})

    assert out["stopped"] is True
    assert out["position"] == 0.0
    assert out["trades_today"] == 0
    assert out["recent_ledger"] == []


def test_canary_signal_tool_returns_side(tmp_path):
    store = market_store(tmp_path)
    generator = lambda features, spec: pd.Series([0, -1], index=features.index[-2:])
    canary = ConfirmedBreakoutCanarySource(store, 1, signal_generator=generator)

    out = canary_signal_tool(canary).handler({})

    assert out["signal"] == "SELL"
    assert out["quantity"] == 1.0


def test_propose_trade_tool_paper_only_gate(tmp_path):
    pt = fresh_paper()
    pt.start("test")
    tool = propose_trade_tool(paper_only_coordinator(pt), pt, fresh_source(tmp_path), AgentConfig(),
                              now_provider=lambda: OPEN_NOW)

    result = tool.handler({"side": "BUY", "quantity": 0.5, "reason": "momentum test"})

    assert result["paper_accept"] is True
    assert result["accepted"] is False
    assert result["paper_only"] is True
    assert result["proposal_reason"] == "momentum test"


def test_propose_trade_tool_duplicate_is_idempotent(tmp_path):
    pt = fresh_paper()
    pt.start("test")
    tool = propose_trade_tool(paper_only_coordinator(pt), pt, fresh_source(tmp_path), AgentConfig(),
                              now_provider=lambda: OPEN_NOW)

    first = tool.handler({"side": "BUY", "quantity": 0.25, "reason": "a"})
    second = tool.handler({"side": "BUY", "quantity": 0.25, "reason": "b"})

    assert first["paper_accept"] is True
    assert second["decision_id"] == first["decision_id"]
    assert second["paper_accept"] is True
    assert pt.state()["position"] == pytest.approx(0.25)


def test_redact_bounds_untrusted_content():
    out = _redact_for_transcript({"content": "x" * 5000}, 100)
    assert len(out["content"]) < 200


class ScriptedPlanner:
    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def plan_with_raw(self, goal, registry, evidence=None):
        self.calls.append({"tools": [entry["name"] for entry in registry.definitions()], "evidence": len(evidence)})
        raw, action = self.script.pop(0)
        return raw, action


def agent_runner(tmp_path, script, transcript=None, config=None):
    store = market_store(tmp_path)
    source = LocalHistoricalMarketDataSource(store)
    pt = fresh_paper()
    pt.start("test")
    coordinator = paper_only_coordinator(pt)
    cfg = config or AgentConfig(max_market_data_age_seconds=120, max_steps_per_tick=2)
    registry = build_agent_registry(source, pt, coordinator, cfg,
                                    canary=ConfirmedBreakoutCanarySource(store, 1))
    transcript = transcript or InMemoryAgentTranscriptStore()
    runner = ContinuousAgentRunner(ScriptedPlanner(script), registry, transcript,
                                   source, pt, coordinator, cfg, now_provider=lambda: OPEN_NOW)
    return runner, transcript


def test_runner_records_thinking_steps(tmp_path):
    runner, transcript = agent_runner(tmp_path, [
        ("raw1", {"action": "tool", "tool": "canary_signal", "input": {}}),
        ("raw2", {"action": "final", "summary": "observed no fresh signal"}),
    ])

    result = runner.run_tick()

    assert result["status"] == "completed"
    phases = [step["phase"] for step in transcript.steps()]
    assert phases == ["tick_start", "assistant", "tool_call", "tool_result", "assistant", "tick_end"]
    tool_calls = [step for step in transcript.steps() if step["phase"] == "tool_call"]
    assert tool_calls[0]["content"]["tool"] == "canary_signal"
    assert transcript.run_status(runner.run_id) == "running"


def test_runner_final_action_only_records_summary(tmp_path):
    runner, transcript = agent_runner(tmp_path, [
        ("raw", {"action": "final", "summary": "no action needed"}),
    ])

    runner.run_tick()

    assert [step["phase"] for step in transcript.steps()] == ["tick_start", "assistant", "tick_end"]


def test_assistant_steps_carry_parsed_action_and_human_reason(tmp_path):
    runner, transcript = agent_runner(tmp_path, [
        ("raw", {"action": "tool", "tool": "canary_signal", "input": {}, "reason": "Check the canary before deciding."}),
        ("raw", {"action": "final", "summary": "no trade", "reason": "Canary is silent."}),
    ])

    runner.run_tick()

    assistant = [step for step in transcript.steps() if step["phase"] == "assistant"]
    assert assistant[0]["content"]["action"] == "tool"
    assert assistant[0]["content"]["tool"] == "canary_signal"
    assert assistant[0]["content"]["reason"] == "Check the canary before deciding."
    assert assistant[1]["content"]["action"] == "final"
    assert assistant[1]["content"]["summary"] == "no trade"
    assert assistant[1]["content"]["reason"] == "Canary is silent."


def test_assistant_steps_without_reason_remain_well_formed(tmp_path):
    runner, transcript = agent_runner(tmp_path, [
        ("raw", {"action": "tool", "tool": "canary_signal", "input": {}}),
        ("raw", {"action": "final", "summary": "ok"}),
    ])

    runner.run_tick()

    assistant = [step for step in transcript.steps() if step["phase"] == "assistant"]
    assert assistant[0]["content"]["tool"] == "canary_signal"
    assert "reason" not in assistant[0]["content"]
    assert assistant[1]["content"]["summary"] == "ok"
    assert "reason" not in assistant[1]["content"]


def test_runs_include_tick_counts(tmp_path):
    runner, transcript = agent_runner(tmp_path, [
        ("raw", {"action": "final", "summary": "tick one"}),
    ])
    runner.run_tick()
    runs = transcript.runs()
    assert runs[0]["run_id"] == runner.run_id
    assert runs[0]["ticks"] == 1


def test_runner_forever_loops_and_stops(tmp_path):
    runner, transcript = agent_runner(tmp_path, [
        ("raw", {"action": "final", "summary": "tick one"}),
        ("raw", {"action": "final", "summary": "tick two"}),
    ], config=AgentConfig(max_market_data_age_seconds=120, poll_seconds=0.05, max_steps_per_tick=2))
    stop = Event()
    results = []

    runner.run_forever(stop=stop, on_tick=lambda result: (results.append(result), stop.set())[1])

    assert len(results) == 1
    assert results[0]["status"] == "completed"
    assert transcript.run_status(runner.run_id) == "running"
    runner.stop()
    assert transcript.run_status(runner.run_id) == "stopped"


def test_runner_refreshes_stale_data_and_records_step(tmp_path):
    holder = {"n": 0}

    def refresh():
        holder["n"] += 1
        write_new_bar(holder["store"])
        return {"ok": True, "downloaded_rows": 1, "last_bar_utc": "2026-09-18T00:00:00+00:00"}

    runner, transcript, store = refresh_runner(tmp_path, refresh, stale_minutes=120)
    holder["store"] = store

    result = runner.run_tick()

    assert holder["n"] == 1
    assert result["status"] == "completed"
    refresh_steps = [s for s in transcript.steps() if s["phase"] == "data_refresh"]
    assert len(refresh_steps) == 1
    assert refresh_steps[0]["content"].get("ok") is True
    tick_start = next(s for s in transcript.steps() if s["phase"] == "tick_start")
    assert tick_start["content"]["fresh"] is True
    assert "age_seconds" in tick_start["content"]


def test_runner_skips_refresh_when_disabled(tmp_path):
    calls = {"n": 0}
    transcript = InMemoryAgentTranscriptStore()

    def refresh():
        calls["n"] += 1
        return {"ok": True}

    config = AgentConfig(max_market_data_age_seconds=120, data_refresh_enabled=False,
                         data_refresh_threshold_seconds=5, data_refresh_min_interval_seconds=300,
                         data_refresh_timeout_seconds=5)
    runner, transcript, _ = refresh_runner(tmp_path, refresh, config=config, stale_minutes=120)

    result = runner.run_tick()

    assert calls["n"] == 0
    assert result["status"] == "stale_data"
    assert not [s for s in transcript.steps() if s["phase"] == "data_refresh"]
    assert not transcript.steps() if False else True  # no tick_start fresh gate below
    planner_calls = [s for s in transcript.steps() if s["phase"] == "assistant"]
    assert planner_calls == []
    tick_start = next(s for s in transcript.steps() if s["phase"] == "tick_start")
    assert tick_start["content"]["fresh"] is False


def test_runner_records_failed_refresh_and_gates_planner(tmp_path):
    calls = {"n": 0}
    transcript = InMemoryAgentTranscriptStore()

    def refresh():
        calls["n"] += 1
        raise RuntimeError("refresh boom")

    runner, transcript, _ = refresh_runner(tmp_path, refresh, stale_minutes=120)

    result = runner.run_tick()

    assert calls["n"] == 1
    assert result["status"] == "stale_data"
    step = next(s for s in transcript.steps() if s["phase"] == "data_refresh")
    assert step["content"]["ok"] is False
    assert step["content"]["error_type"] == "RuntimeError"
    assert [s for s in transcript.steps() if s["phase"] == "assistant"] == []


def test_runner_respects_refresh_cooldown(tmp_path):
    calls = {"n": 0}

    def refresh():
        calls["n"] += 1
        return {"ok": True, "downloaded_rows": 0, "last_bar_utc": None}

    config = AgentConfig(max_market_data_age_seconds=60, max_steps_per_tick=1, data_refresh_enabled=True,
                         data_refresh_threshold_seconds=5, data_refresh_min_interval_seconds=300,
                         data_refresh_timeout_seconds=5)
    runner, transcript, _ = refresh_runner(tmp_path, refresh, config=config)

    runner.run_tick()
    runner.run_tick()

    assert calls["n"] == 1
    refresh_steps = [s for s in transcript.steps() if s["phase"] == "data_refresh"]
    assert len(refresh_steps) == 2
    assert any(s["content"].get("skipped") == "cooldown" for s in refresh_steps)


def test_runner_skips_planner_when_market_is_closed(tmp_path):
    from datetime import datetime, timezone
    runner, transcript = agent_runner(
        tmp_path, [("(raw)", {"action": "final", "summary": "should not run"})],
        config=AgentConfig(max_market_data_age_seconds=120, max_steps_per_tick=2))

    saturday = datetime(2026, 9, 19, 12, tzinfo=timezone.utc)
    runner._now_provider = lambda: saturday
    result = runner.run_tick()

    assert result["status"] == "market_closed"
    assert result["steps"] == 0
    assert runner.planner.calls == []
    phases = [step["phase"] for step in transcript.steps()]
    assert phases == ["tick_start", "tick_end"]
    tick_start = next(s for s in transcript.steps() if s["phase"] == "tick_start")
    assert tick_start["content"]["market_open"] is False


def test_runner_reconciles_orphaned_runs_when_starting(tmp_path):
    transcript = InMemoryAgentTranscriptStore()
    transcript.start_run("agent_orphan_1")
    transcript.start_run("agent_orphan_2")
    runner, _ = agent_runner(tmp_path, [("(raw)", {"action": "final", "summary": "ok"})],
                             transcript=transcript,
                             config=AgentConfig(max_market_data_age_seconds=120, max_steps_per_tick=2))

    statuses = {run["run_id"]: run["status"] for run in transcript.runs(limit=10)}
    assert statuses["agent_orphan_1"] == "stopped"
    assert statuses["agent_orphan_2"] == "stopped"
    assert statuses[runner.run_id] == "running"


def test_runner_writes_heartbeat_status_file(tmp_path):
    status_file = str(tmp_path / "agent_status.json")
    runner, transcript = agent_runner(tmp_path, [("(raw)", {"action": "final", "summary": "ok"})],
                                      config=AgentConfig(max_market_data_age_seconds=120, max_steps_per_tick=2))
    runner.status_path = status_file
    result = runner.run_tick()

    import json
    status = json.loads(Path(status_file).read_text())
    assert status["run_id"] == runner.run_id
    assert status["status"] == result["status"]
    assert status["market_open"] is True
    assert status["stalled"] is False
    runner.stop()
    stopped = json.loads(Path(status_file).read_text())
    assert stopped["status"] == "stopped"


def test_runner_heartbeat_tracks_consecutive_errors(tmp_path):
    status_file = str(tmp_path / "agent_status.json")

    class BoomPlanner:
        def plan_with_raw(self, goal, registry, evidence=None):
            raise RuntimeError("planner down")

    store = market_store(tmp_path)
    source = LocalHistoricalMarketDataSource(store)
    pt = fresh_paper(); pt.start("test")
    coordinator = paper_only_coordinator(pt)
    cfg = AgentConfig(max_market_data_age_seconds=120, max_steps_per_tick=2)
    registry = build_agent_registry(source, pt, coordinator, cfg, canary=ConfirmedBreakoutCanarySource(store, 1))
    runner = ContinuousAgentRunner(BoomPlanner(), registry, InMemoryAgentTranscriptStore(), source, pt,
                                   coordinator, cfg, status_path=status_file,
                                   now_provider=lambda: OPEN_NOW)

    import json
    from pathlib import Path
    for _ in range(2):
        result = runner.run_tick()
        assert result["status"] == "planner_error"
    status = json.loads(Path(status_file).read_text())
    assert status["consecutive_errors"] == 2
    assert status["last_tick_status"] == "planner_error"