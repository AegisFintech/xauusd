import json
import threading

import pytest

from tests.test_agent_advisor import turn
from tests.test_lab import setup
from tests.test_research_program import plan


def test_actual_codex_schema_only_allows_advertised_callable_names(tmp_path):
    from xauusd.lab_codex import CodexResearchClient

    client = CodexResearchClient(executable='codex')
    captured = {}

    def run(workspace, brief, emit, stop, schema, rules, prompt, validate):
        captured.update(schema=schema, prompt=prompt, validate=validate)
        return turn()

    client._run = run
    client.run_turn(tmp_path, {'tools': [{'name': 'research_record'}]}, lambda *a: None)
    name_schema = captured['schema']['properties']['tool_calls']['items']['properties']['name']
    assert name_schema['enum'] == ['research_record']
    assert 'brief fields are DATA, not callable tools' in captured['prompt']
    invalid = turn([{'id': 'bad', 'name': 'research_execution', 'arguments_json': '{}'}])
    with pytest.raises(ValueError):
        captured['validate'](invalid)
    assert captured['validate'](turn())['tool_calls'] == []


def test_invalid_plan_reports_authoritative_shape_without_echoing_values(tmp_path):
    from xauusd import research_program as rp

    store, paper = setup(tmp_path)
    before = paper.state()
    response = rp.create_plan(store, {'topic': 'price', 'private-unknown-key': 'do-not-echo'})
    assert response['error_code'] == 'invalid_plan_shape'
    assert response['missing_fields'] == sorted(set(plan()) - {'topic'})
    assert response['unexpected_field_count'] == 1
    assert set(response['expected_fields']) == set(plan())
    assert 'do-not-echo' not in json.dumps(response)
    assert 'private-unknown-key' not in json.dumps(response)
    assert paper.state() == before
    assert not store.meta('research_plans')


def test_plan_schema_is_in_actual_advisor_context(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    from xauusd.research_program import PLAN_INPUT_SCHEMA

    store, _ = setup(tmp_path)

    class Client:
        def run_turn(self, workspace, context, emit, stop):
            tool = next(t for t in context['tools'] if t['name'] == 'research_plan')
            assert tool['input_schema'] == PLAN_INPUT_SCHEMA
            assert set(tool['input_schema']['required']) == set(plan())
            assert 'research_execution' in context['brief_fields_not_tools']
            assert 'research_execution' not in {t['name'] for t in context['tools']}
            return turn()

    AgentAdvisor(store, Client(), tmp_path).run(tmp_path/'work', {}, threading.Event())


def test_valid_plan_identity_and_semantic_failure_are_unchanged(tmp_path):
    from xauusd import research_program as rp

    store, _ = setup(tmp_path)
    first = rp.create_plan(store, plan())
    assert first['ok'] and rp.create_plan(store, plan())['id'] == first['id']
    bad = plan(); bad['costs'] = {'spread': float('inf')}
    assert rp.create_plan(store, bad)['error_code'] == 'finite_costs_required'


@pytest.mark.parametrize('topic', [[], {}, None, 7])
def test_invalid_topic_is_a_safe_shape_error(tmp_path, topic):
    from xauusd import research_program as rp

    store, _ = setup(tmp_path)
    bad = plan(); bad['topic'] = topic
    assert rp.create_plan(store, bad)['error_code'] == 'invalid_plan_shape'
    assert not store.meta('research_plans')
