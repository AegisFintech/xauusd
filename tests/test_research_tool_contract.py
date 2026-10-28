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


def test_advisor_exposes_only_current_frozen_dataset_as_plan_hint(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    from xauusd.research_program import PLAN_INPUT_SCHEMA
    store, _ = setup(tmp_path)
    version = 'a' * 64
    store.meta('dataset', {'version': version})

    class Client:
        def run_turn(self, workspace, context, emit, stop):
            schema = next(t for t in context['tools'] if t['name'] == 'research_plan')['input_schema']
            assert schema['properties']['dataset_version']['const'] == version
            assert 'const' not in PLAN_INPUT_SCHEMA['properties']['dataset_version']
            return turn()

    AgentAdvisor(store, Client(), tmp_path).run(tmp_path/'work', {}, threading.Event())


def test_stale_dataset_error_exposes_only_valid_current_digest_without_rewriting_plan(tmp_path):
    from xauusd import research_program as rp
    store, _ = setup(tmp_path)
    version = 'b' * 64
    store.meta('dataset', {'version': version})
    stale = plan()
    response = rp.create_plan(store, stale)
    assert response == {'ok': False, 'error_code': 'current_training_dataset_required', 'expected_dataset_version': version}
    assert stale['dataset_version'] == 'v1' and not store.meta('research_plans')
    assert rp.create_plan(store, {**stale, 'dataset_version': version})['ok']


def test_malformed_dataset_metadata_is_never_echoed(tmp_path):
    from xauusd import research_program as rp
    store, _ = setup(tmp_path)
    store.meta('dataset', {'version': 'private-invalid-value'})
    response = rp.create_plan(store, plan())
    assert response == {'ok': False, 'error_code': 'current_training_dataset_required'}
    assert 'const' not in rp.plan_input_schema(store)['properties']['dataset_version']
    assert 'private-invalid-value' not in json.dumps(response)


def test_catalog_refreshes_when_frozen_dataset_changes_between_turns(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    store, _ = setup(tmp_path)
    first, second = 'a' * 64, 'b' * 64
    store.meta('dataset', {'version': first})

    class Client:
        calls = 0
        def run_turn(self, workspace, context, emit, stop):
            self.calls += 1
            schema = next(t for t in context['tools'] if t['name'] == 'research_plan')['input_schema']
            if self.calls == 1:
                assert schema['properties']['dataset_version']['const'] == first
                store.meta('dataset', {'version': second})
                args = {**plan(), 'dataset_version': first}
                return turn([{'id': 'stale', 'name': 'research_plan', 'arguments_json': json.dumps(args)}], True)
            assert schema['properties']['dataset_version']['const'] == second
            assert context['tool_results'][-1]['result']['expected_dataset_version'] == second
            return turn()

    client = Client()
    AgentAdvisor(store, client, tmp_path).run(tmp_path/'work', {}, threading.Event())
    assert client.calls == 2 and not store.meta('research_plans')


@pytest.mark.parametrize('invalid', [['corrupt'], [], 0, 'invalid'])
def test_invalid_manifest_shape_has_no_hint_and_fails_closed(tmp_path, invalid):
    from xauusd import research_program as rp
    store, _ = setup(tmp_path)
    store.meta('dataset', invalid)
    assert 'const' not in rp.plan_input_schema(store)['properties']['dataset_version']
    assert rp.create_plan(store, plan()) == {'ok': False, 'error_code': 'dataset_metadata_invalid'}
    assert not store.meta('research_plans')
