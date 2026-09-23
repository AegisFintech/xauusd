import pandas as pd
from types import SimpleNamespace
from xauusd.bits_research import market_research, finish_research_cycle
from xauusd.bits_memory import result_for_prompt
from tests.test_bits_runner import runner
import json


class Store:
    def __init__(self): self.values = {}
    def get(self, key, default=None): return self.values.get(key, default)
    def put(self, key, value): self.values[key] = value


def test_research_progress_is_idempotent_and_resets_only_on_changed_notes():
    store = Store()
    for i in range(3): finish_research_cycle(store, str(i))
    assert finish_research_cycle(store, '2')['cycles_without_new_notes'] == 3
    assert store.get('research_progress')['needs_attention']
    store.put('working_notes', {'notes': {'findings': ['tested hypothesis']}, 'recorded_at': 'one'})
    assert finish_research_cycle(store, '3')['cycles_without_new_notes'] == 0
    store.put('working_notes', {'notes': {'findings': ['tested hypothesis']}, 'recorded_at': 'two'})
    assert finish_research_cycle(store, '4')['cycles_without_new_notes'] == 1


def test_market_windows_use_observed_data_and_handle_missing_source():
    frame = pd.DataFrame({'close': range(100, 340)}, index=pd.date_range('2026-09-23', periods=240, freq='min', tz='UTC'))
    source = SimpleNamespace(store=SimpleNamespace(read=lambda:frame, normalize=lambda x:x))
    result = market_research(source)
    assert result['windows']['15']['close_change'] == 14
    assert result['windows']['240']['mean_close'] == 219.5
    assert not market_research(None)['available']


def test_nested_output_page_preserves_original_cursor_without_skipping_text():
    text = '\\"\n' * 3000
    page = dict(job_id='original', stream='stdout', text=text, offset=7000,
                next_offset=16000, stored_characters=20000, capture_truncated=False)
    result = result_for_prompt(dict(job_id='retrieval', stdout=json.dumps(page), stderr='', status='succeeded', exit_code=0))
    assert result['source'] == 'bits-job original'
    assert result['stdout'] == text[:2500]
    assert result['output_page']['next_offset'] == 9500
    page.update(text='tail', offset=19996, next_offset=None)
    result = result_for_prompt(dict(job_id='retrieval', stdout=json.dumps(page), stderr=''))
    assert result['output_page']['next_offset'] is None
    assert not result['context_excerpt']


def test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path/'AGENTS.md').write_text('Repository rules revision 1')
    agent = runner(tmp_path)
    agent.run_tick()
    ctx = agent.planner.invocations[-1]['context']
    assert ctx['repository_guidance']['text'] == 'Repository rules revision 1'
    agent.run_tick()
    assert agent._context(agent.source.read())['bootstrap']['reviewed']
    assert agent._context(agent.source.read())['repository_guidance'] is None
    (tmp_path/'AGENTS.md').write_text('Repository rules revision 2')
    assert not agent._context(agent.source.read())['bootstrap']['reviewed']
    agent.stop()
