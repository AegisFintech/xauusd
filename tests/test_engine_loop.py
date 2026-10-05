from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pandas as pd
import pytest

from xauusd.agent_loop import InMemoryAgentTranscriptStore
from xauusd.demo_execution import NormalizedDecision, PaperToCTraderDemoCoordinator
from xauusd.engine_loop import (HALT_STATE_KEY, EngineConfig, PaperTradingEngine,
                                 engine_decision_id)
from xauusd.paper_trading import (DAILY_LOSS_LIMIT, KILL_SWITCH, MARKET_CLOSED, MAX_POSITION,
                                  InMemoryPaperTradingStore, PaperRiskConfig, PaperTrading)

NOW = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)  # Thursday 08:00 New York, market open
SATURDAY = datetime(2026, 9, 19, 12, tzinfo=timezone.utc)


class Store:
    def __init__(self):
        self.rows = {}
    def get(self, key, default=None):
        return self.rows.get(key, default)
    def put(self, key, value):
        self.rows[key] = value
    def delete(self, key):
        self.rows.pop(key, None)


class Source:
    def __init__(self, price=4000.0, observed_at=NOW):
        self.price, self.observed_at = price, observed_at
    def read(self):
        return SimpleNamespace(price=self.price, observed_at=self.observed_at)


class Signals:
    """Deterministic signal double: returns the same proposal until told otherwise."""
    def __init__(self, side="BUY", quantity=0.1, transitions=None):
        self.side, self.quantity, self.transitions = side, quantity, transitions
        self.calls = 0
    def read(self, market):
        self.calls += 1
        if self.transitions is not None:
            if self.transitions <= 0:
                return None
            self.transitions -= 1
        if self.side is None:
            return None
        return NormalizedDecision("sig", "XAUUSD", self.side, self.quantity, market.observed_at)


def build(paper=None, source=None, signals=None, config=None, store=None, transcript=None):
    paper = paper or PaperTrading(InMemoryPaperTradingStore(),
                                  PaperRiskConfig(max_market_data_age_seconds=180))
    paper.start("test")
    source = source or Source()
    signals = signals or Signals()
    transcript = transcript or InMemoryAgentTranscriptStore()
    transcript.initialize()
    engine = PaperTradingEngine(
        paper, PaperToCTraderDemoCoordinator(paper, paper_only=True),
        source, signals, store or Store(), transcript,
        config or EngineConfig(quantity=0.1, poll_seconds=0.01),
        now_provider=lambda: NOW)
    return engine, paper, transcript


# ---------------------------------------------------------------- gating
def test_engine_passes_every_proposal_through_the_paper_gates():
    """The engine is deterministic, not privileged.

    A deterministic loop that could skip a risk gate would be strictly more
    dangerous than the LLM loop it replaces, so the engine hands every decision to
    the same PaperTrading.evaluate the agent uses.
    """
    engine, paper, transcript = build()
    outcome = engine.evaluate_once()

    assert outcome["status"] == "filled"
    assert outcome["decision"]["accepted"] is True
    # The real gate filled it, which is visible in the paper ledger.
    assert paper.state()["position"] == pytest.approx(0.1)
    assert len(paper.state()["ledger"]) == 1


def test_engine_cannot_exceed_max_position():
    engine, paper, _ = build(config=EngineConfig(quantity=5.0, poll_seconds=0.01))
    # PaperRiskConfig default max_position is 1.0; a 5-unit proposal must be refused.
    outcome = engine.evaluate_once()

    assert outcome["status"] == "refused"
    assert outcome["decision"]["gate_reason"] == MAX_POSITION
    assert paper.state()["position"] == 0.0
    assert paper.state()["ledger"] == []


def test_engine_is_refused_by_the_kill_switch():
    engine, paper, _ = build()
    paper.stop("operator halt")
    outcome = engine.evaluate_once()

    assert outcome["status"] == "refused"
    assert outcome["decision"]["gate_reason"] == KILL_SWITCH
    assert paper.state()["ledger"] == []


def test_engine_respects_market_closed():
    """Market hours are checked before freshness, as the agent does.

    On a weekend the newest bar is two days old, so a freshness-first check would
    report "stale data" for the whole weekend and could trigger a pointless data
    refresh, when the real answer is that the market is shut.
    """
    source = Source(observed_at=SATURDAY - timedelta(seconds=30))
    engine, paper, transcript = build(source=source)
    engine._now = lambda: SATURDAY

    outcome = engine.evaluate_once()

    assert outcome["status"] == "market_closed"
    assert paper.state()["ledger"] == []
    step = next(s for s in transcript.steps(engine.run_id) if s["phase"] == "engine_signal")
    assert step["content"]["market_open"] is False
    # No proposal was made, so the refusal is not a trade-shaped record.
    assert not [s for s in transcript.steps(engine.run_id) if s["phase"] in
                {"engine_decision", "engine_fill"}]


def test_engine_refuses_a_stale_bar_without_proposing():
    """Staleness is checked before a proposal exists, not after.

    The engine reads the same closed-bar rule as the gate. Proposing on a
    4-hour-old bar and letting the gate refuse it would still spend a decision and
    pollute the record with tradeable-looking intent.
    """
    source = Source(observed_at=NOW - timedelta(hours=4))
    engine, paper, transcript = build(source=source)
    outcome = engine.evaluate_once()

    assert outcome["status"] == "stale_data"
    assert paper.state()["ledger"] == []
    signals_recorded = [json.loads_ if False else c for c in []]
    step = [s for s in transcript.steps(engine.run_id) if s["phase"] == "engine_signal"]
    assert step and step[0]["content"]["fresh"] is False
    # And no proposal was ever made.
    assert not [s for s in transcript.steps(engine.run_id) if s["phase"] in
                {"engine_decision", "engine_fill"}]


def test_engine_refuses_a_future_dated_bar():
    source = Source(observed_at=NOW + timedelta(days=3))
    engine, paper, _ = build(source=source)
    outcome = engine.evaluate_once()

    assert outcome["status"] == "stale_data"
    assert paper.state()["ledger"] == []


def test_engine_does_nothing_when_the_signal_is_flat():
    engine, paper, _ = build(signals=Signals(side=None))
    outcome = engine.evaluate_once()

    assert outcome["status"] == "no_signal"
    assert paper.state()["ledger"] == []


def test_daily_loss_gate_still_applies_to_the_engine():
    paper = PaperTrading(InMemoryPaperTradingStore(),
                         PaperRiskConfig(daily_loss_limit=10, max_position=5,
                                         max_market_data_age_seconds=180))
    paper.start("test")
    # Mark the account down by opening long, then feeding a much lower price.
    paper.evaluate(SimpleNamespace(decision_id="pre", symbol="XAUUSD", side="BUY",
                                   quantity=1.0, price=4000.0, market_data_at=NOW), NOW)
    engine, _, _ = build(paper=paper, source=Source(price=3980.0), signals=Signals(quantity=0.5))

    outcome = engine.evaluate_once()

    assert outcome["status"] == "refused"
    assert outcome["decision"]["gate_reason"] == DAILY_LOSS_LIMIT


# ------------------------------------------------------------ idempotency
def test_engine_decision_id_is_derived_from_the_bar():
    """A restart re-proposes the same decision for the same bar, and the store's
    idempotency check refuses it instead of double-filling."""
    first = engine_decision_id("confirmed_breakout", "BUY", 0.1, NOW)
    same = engine_decision_id("confirmed_breakout", "BUY", 0.1, NOW)
    other_bar = engine_decision_id("confirmed_breakout", "BUY", 0.1, NOW + timedelta(minutes=1))
    other_side = engine_decision_id("confirmed_breakout", "SELL", 0.1, NOW)

    assert first == same
    assert first != other_bar
    assert first != other_side
    assert first.startswith("engine:")


def test_a_repeated_signal_on_the_same_bar_does_not_double_fill():
    engine, paper, _ = build()
    first = engine.evaluate_once()
    # A signal source that keeps returning the same transition is a real risk: the
    # decision id is bar-derived precisely so the store refuses the second.
    second = engine.evaluate_once()

    assert first["status"] == "filled"
    assert second["status"] == "refused"
    assert second["decision"]["gate_reason"] == "DUPLICATE_DECISION"
    assert paper.state()["position"] == pytest.approx(0.1)
    assert len(paper.state()["ledger"]) == 1


# ------------------------------------------------------------------ halt
def test_halt_stops_proposals_and_persists_the_reason():
    store = Store()
    engine, paper, _ = build(store=store)
    engine.halt("supervisor: awaiting validation of the breakout edge")

    outcome = engine.evaluate_once()
    assert outcome["status"] == "halted"
    assert paper.state()["ledger"] == []
    # Durable: a fresh process reading the same store stays halted.
    assert store.get(HALT_STATE_KEY)["reason"].startswith("supervisor")
    assert PaperTradingEngine(paper, PaperToCTraderDemoCoordinator(paper, paper_only=True),
                              Source(), Signals(), store, InMemoryAgentTranscriptStore(),
                              EngineConfig(), now_provider=lambda: NOW).halted is True


def test_halt_requires_a_reason():
    engine, _, _ = build()
    with pytest.raises(ValueError):
        engine.halt("   ")


def test_halt_does_not_clear_the_paper_kill_switch():
    """Halting the engine is not a trading stop, and resuming is not a start."""
    engine, paper, _ = build()
    engine.halt("operator pause")
    assert paper.state()["stopped"] is False
    assert paper.state()["kill_switch_reason"] == "test"

    engine.resume("operator resume")
    assert paper.state()["stopped"] is False


def test_resume_clears_a_persisted_halt():
    store = Store()
    engine, paper, _ = build(store=store)
    engine.halt("pause")
    assert engine.halted is True
    engine.resume("resume")
    assert engine.halted is False
    assert HALT_STATE_KEY not in store.rows


def test_repeated_internal_failures_halt_the_engine_rather_than_looping_silently():
    """The engine is the trade path; a persistent failure must be loud."""
    engine, paper, _ = build()
    engine._decide = lambda: (_ for _ in ()).throw(RuntimeError("store unreachable"))
    results = [engine.evaluate_once() for _ in range(3)]

    assert all(r["status"] == "error" for r in results)
    assert engine.halted is True
    assert "failed 3 times" in (engine.halted_reason or "")


def test_a_transient_failure_does_not_halt_the_engine():
    engine, _, _ = build()
    engine._decide = lambda: (_ for _ in ()).throw(RuntimeError("blip"))
    assert engine.evaluate_once()["status"] == "error"
    assert engine.consecutive_errors == 1
    assert engine.halted is False


# --------------------------------------------------------------- recording
def test_engine_records_signal_decision_and_fill_for_the_live_view():
    engine, _, transcript = build()
    engine.evaluate_once()
    phases = [s["phase"] for s in transcript.steps(engine.run_id)]

    assert "engine_signal" in phases
    assert "engine_fill" in phases
    signal_step = next(s for s in transcript.steps(engine.run_id) if s["phase"] == "engine_signal")
    assert signal_step["content"]["signal"] == "BUY"
    assert signal_step["content"]["price"] == 4000.0


def test_engine_does_not_clamp_an_oversized_proposal():
    """An oversized proposal must be visibly refused, not silently trimmed.

    Clamping the quantity to max_position turns a recorded MAX_POSITION refusal
    into a hidden partial fill, so the strategy believes it traded a size it did
    not and the gate stops protecting anything.
    """
    engine, paper, _ = build(config=EngineConfig(quantity=0.4, poll_seconds=0.01))
    paper.config = PaperRiskConfig(max_position=0.1, max_market_data_age_seconds=180)

    outcome = engine.evaluate_once()

    assert outcome["status"] == "refused"
    assert outcome["decision"]["gate_reason"] == MAX_POSITION
    # The proposal recorded the size the strategy actually asked for.
    assert outcome["decision"]["quantity"] == pytest.approx(0.4)
    assert paper.state()["position"] == 0.0


def test_engine_config_rejects_unbounded_values():
    for kwargs in ({"quantity": 0}, {"quantity": float("inf")}, {"poll_seconds": 0},
                   {"max_bar_age_seconds": -1}, {"auto_halt_after_consecutive_errors": 0},
                   {"strategy": "  "}):
        with pytest.raises(ValueError):
            EngineConfig(**kwargs).validate()


def test_run_forever_is_bounded_by_iterations():
    engine, _, transcript = build()
    result = engine.run_forever(iterations=3)

    assert result["tick"] == 3
    assert len([s for s in transcript.steps(engine.run_id) if s["phase"] == "engine_signal"]) == 3


def test_resume_takes_effect_on_a_running_engine_without_a_restart():
    # The halt reason was cached in memory, so `engine resume` from the CLI cleared
    # the key while the service kept reporting halted and ticking to no purpose.
    # The store is the source of truth and has to be re-read every tick.
    store = Store()
    engine, paper, _ = build(store=store)
    engine.halt("operator: no validated edge")
    assert engine.evaluate_once()["status"] == "halted"

    # A separate process resumes it: the running engine sees only the store.
    PaperTradingEngine(paper, PaperToCTraderDemoCoordinator(paper, paper_only=True),
                       Source(), Signals(), store, InMemoryAgentTranscriptStore(),
                       EngineConfig(), now_provider=lambda: NOW).resume("operator: run it in paper")

    outcome = engine.evaluate_once()
    assert outcome["status"] != "halted", "the running engine stayed halted after a resume"
    # It reached the gates and acted, which is the point: previously it ticked
    # 2,265 times returning "halted" and proposed nothing.
    assert paper.state()["ledger"], "a resumed engine should have proposed through the gates"


def test_a_halt_from_another_process_still_stops_a_running_engine():
    store = Store()
    engine, paper, _ = build(store=store)
    engine.evaluate_once()
    PaperTradingEngine(paper, PaperToCTraderDemoCoordinator(paper, paper_only=True),
                       Source(), Signals(), store, InMemoryAgentTranscriptStore(),
                       EngineConfig(), now_provider=lambda: NOW).halt("supervisor: halt now")
    assert engine.evaluate_once()["status"] == "halted"


def test_engine_status_reports_the_running_process_not_a_phantom(tmp_path, monkeypatch):
    # `engine status` built a fresh engine and reported it: `running`, tick 0, for a
    # service that was halted and had ticked thousands of times. It must read the
    # status file the running process writes.
    import json as _json
    from xauusd.cli import engine_controller
    status_path = tmp_path / "engine_status.json"
    status_path.write_text(_json.dumps({
        "run_id": "engine_real", "tick": 2265, "state": "halted", "phase": "halted",
        "halted_reason": "no validated edge", "decisions": 0, "recorded_at": "2026-10-05T05:48:07+00:00"}))
    monkeypatch.setenv("ENGINE_STATUS_PATH", str(status_path))
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    monkeypatch.setenv("CTRADER_VOLUME_PER_PAPER_UNIT", "100")
    result = engine_controller("status")
    assert result["run_id"] == "engine_real"
    assert result["tick"] == 2265
    assert result["state"] == "halted"
