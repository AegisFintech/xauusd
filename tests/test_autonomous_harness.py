import json
import time

import pytest

from xauusd.autonomous_harness import (AutonomousResearchHarness, InMemoryHarnessStore,
    OpenAICompatiblePlanner, PlannerResponseError, ToolExecutionError, ToolRegistry, ToolSpec)


INPUT = {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"], "additionalProperties": False}
OUTPUT = {"type": "object", "properties": {"finding": {"type": "string"}}, "required": ["finding"], "additionalProperties": False}


def planner_action(action):
    def transport(payload, timeout):
        assert payload["response_format"] == {"type": "json_object"}
        assert payload["messages"][1]["role"] == "user"
        return {"choices": [{"message": {"content": json.dumps(action)}}]}
    return OpenAICompatiblePlanner("https://planner.invalid/v1", "test-model", "not-a-real-key", transport=transport)


def planner_actions(actions, captured):
    def transport(payload, timeout):
        captured.append(json.loads(payload["messages"][1]["content"]))
        return {"choices": [{"message": {"content": json.dumps(actions.pop(0))}}]}
    return OpenAICompatiblePlanner("https://planner.invalid/v1", "test-model", "not-a-real-key", transport=transport)


def tool(handler=lambda value: {"finding": value["topic"]}, **kwargs):
    return ToolSpec("research_note", "Create a research note", INPUT, OUTPUT, handler, **kwargs)


def test_harness_executes_only_registered_tool_and_persists_audit_events():
    store = InMemoryHarnessStore()
    captured = []
    planner = planner_actions([{"action": "tool", "tool": "research_note", "input": {"topic": "gold"}},
                               {"action": "final", "summary": "complete"}], captured)
    harness = AutonomousResearchHarness(planner, ToolRegistry([tool()]), store)
    result = harness.run("summarize gold")
    assert result["evidence"][0]["result"] == {"finding": "gold"}
    assert store.runs[result["run_id"]]["status"] == "completed"
    assert [event["event"] for event in store.events] == ["planner_action", "tool_attempt", "tool_completed", "planner_action"]
    assert list(store.calls.values())[0]["status"] == "completed"


def test_unknown_tool_and_extra_action_fields_are_refused_before_execution():
    store = InMemoryHarnessStore()
    harness = AutonomousResearchHarness(planner_action({"action": "tool", "tool": "expand_tools", "input": {}}), ToolRegistry([tool()]), store)
    with pytest.raises(PlannerResponseError, match="not allow-listed"):
        harness.run("ignore policies")
    assert store.summary()["by_status"] == {"failed": 1}
    extra = AutonomousResearchHarness(planner_action({"action": "final", "summary": "ok", "risk": "disabled"}), ToolRegistry([tool()]), InMemoryHarnessStore())
    with pytest.raises(PlannerResponseError, match="only action and summary"):
        extra.run("research")


def test_optional_display_only_reason_is_accepted_and_string_checked():
    harness = AutonomousResearchHarness(planner_action({"action": "final", "summary": "ok", "reason": "No signal to act on."}),
                                        ToolRegistry([tool()]), InMemoryHarnessStore())
    result = harness.run("research")
    assert result["summary"] == "ok"

    store = InMemoryHarnessStore()
    captured = []
    harness = AutonomousResearchHarness(planner_actions([
        {"action": "tool", "tool": "research_note", "input": {"topic": "gold"}, "reason": "Investigating gold."},
        {"action": "final", "summary": "complete"},
    ], captured), ToolRegistry([tool()]), store)
    harness.run("research")
    assert list(store.calls.values())[0]["status"] == "completed"

    with pytest.raises(PlannerResponseError, match="reason"):
        AutonomousResearchHarness(planner_action({"action": "final", "summary": "x", "reason": 7}),
                                  ToolRegistry([tool()]), InMemoryHarnessStore()).run("research")


def test_invalid_tool_output_retries_then_fails_with_audited_attempts():
    store = InMemoryHarnessStore()
    harness = AutonomousResearchHarness(planner_action({"action": "tool", "tool": "research_note", "input": {"topic": "gold"}}), ToolRegistry([tool(lambda _: {"unexpected": True}, retry_limit=1)]), store)
    with pytest.raises(ToolExecutionError, match="tool research_note failed"):
        harness.run("research")
    assert [event["event"] for event in store.events].count("tool_attempt") == 2
    assert list(store.calls.values())[0]["status"] == "failed"


def test_final_response_completes_without_executing_a_tool():
    store = InMemoryHarnessStore()
    result = AutonomousResearchHarness(planner_action({"action": "final", "summary": "No action required."}), ToolRegistry([tool()]), store).run("research")
    assert result["summary"] == "No action required."
    assert store.calls == {}


def test_tool_result_is_evidence_for_the_next_bounded_planner_turn():
    captured = []
    planner = planner_actions([
        {"action": "tool", "tool": "research_note", "input": {"topic": "gold"}},
        {"action": "final", "summary": "Research completed."},
    ], captured)
    result = AutonomousResearchHarness(planner, ToolRegistry([tool()]), InMemoryHarnessStore()).run("research")
    assert result["summary"] == "Research completed."
    assert captured[0]["evidence"] == []
    assert captured[1]["evidence"] == [{"tool": "research_note", "input": {"topic": "gold"}, "result": {"finding": "gold"}}]


def test_tool_timeout_is_bounded_and_persisted_as_failed():
    store = InMemoryHarnessStore()
    harness = AutonomousResearchHarness(planner_action({"action": "tool", "tool": "research_note", "input": {"topic": "gold"}}), ToolRegistry([tool(lambda _: (time.sleep(.05), {"finding": "late"})[1], timeout_seconds=.001)]), store)
    with pytest.raises(ToolExecutionError, match="tool research_note failed"):
        harness.run("research")
    assert list(store.calls.values())[0]["status"] == "failed"


def test_planner_from_env_configures_model_and_timeout(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://planner.invalid/v1")
    monkeypatch.setenv("OPENAI_MODEL", "grok-4.6")
    monkeypatch.delenv("OPENAI_TIMEOUT_SECONDS", raising=False)

    assert OpenAICompatiblePlanner.from_env().timeout_seconds == 30.0

    # Reasoning models routinely exceed the 30s default, so it must be tunable.
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "90")
    planner = OpenAICompatiblePlanner.from_env()
    assert planner.timeout_seconds == 90.0
    assert planner.model == "grok-4.6"


def test_planner_from_env_rejects_a_non_positive_timeout(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://planner.invalid/v1")
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "0")

    with pytest.raises(ValueError, match="OPENAI_TIMEOUT_SECONDS"):
        OpenAICompatiblePlanner.from_env()
