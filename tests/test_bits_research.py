import pandas as pd
from types import SimpleNamespace
from xauusd.bits_research import (PATH_REPEAT_THRESHOLD, PATH_WINDOW, command_paths, finish_research_cycle,
                                  market_research, record_cycle_paths, repeated_paths)
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


def test_command_paths_keeps_only_existing_scoped_files(tmp_path):
    """Observation has to be conservative, or the evidence is noise.

    A token counts only when it resolves to a real file under cwd, so a
    hallucinated path, an absolute one, an extension-less one and anything inside
    a generated tree cannot become something the model is told to stop reading.
    """
    (tmp_path / 'reports' / 'research').mkdir(parents=True)
    (tmp_path / 'reports' / 'research' / 'prereg.json').write_text('{}')
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data' / 'bars.parquet').write_text('x')
    command = ("prereg=Path('reports/research/prereg.json')\n"
               "for p in Path('.').glob('**/*cftc*'): pass\n"
               "data/bars.parquet reports/research/absent.json /etc/hosts notes.md")

    assert command_paths(command, cwd=str(tmp_path)) == ['reports/research/prereg.json']


def test_repeated_paths_names_a_retrieval_loop(tmp_path):
    """19 cycles re-read one 7,271-byte file and nothing could say which file.

    `cycles_without_new_notes` proved the streak was unproductive but not what was
    being re-fetched, so each cycle concluded the content was "still omitted" and
    fetched it again. The evidence is descriptive: it never blocks a command.
    """
    (tmp_path / 'reports').mkdir()
    (tmp_path / 'reports' / 'prereg.json').write_text('{}')
    store = Store()
    command = 'cat reports/prereg.json'
    for cycle in range(PATH_REPEAT_THRESHOLD - 1):
        record_cycle_paths(store, f'c{cycle}', command, cwd=str(tmp_path))
    assert repeated_paths(store, cwd=str(tmp_path)) == []

    record_cycle_paths(store, f'c{PATH_REPEAT_THRESHOLD - 1}', command, cwd=str(tmp_path))

    assert repeated_paths(store, cwd=str(tmp_path)) == [
        {'path': 'reports/prereg.json', 'cycles': PATH_REPEAT_THRESHOLD,
         'window': PATH_REPEAT_THRESHOLD, 'bytes': 2}]


def test_one_cycle_counts_once_however_many_commands_it_runs(tmp_path):
    """A cycle runs several steps; the window counts cycles, not commands."""
    (tmp_path / 'reports').mkdir()
    (tmp_path / 'reports' / 'a.json').write_text('{}')
    store = Store()

    record_cycle_paths(store, 'c1', 'cat reports/a.json', cwd=str(tmp_path))
    record_cycle_paths(store, 'c1', 'head -1 reports/a.json && wc -c reports/a.json', cwd=str(tmp_path))

    assert len(store.get('cycle_paths')['window']) == 1
    assert store.get('cycle_paths')['window'][0]['paths'] == ['reports/a.json']
    assert repeated_paths(store, cwd=str(tmp_path)) == []


def test_path_window_is_bounded_and_progress_clears_it(tmp_path):
    (tmp_path / 'reports').mkdir()
    (tmp_path / 'reports' / 'a.json').write_text('{}')
    store = Store()
    for cycle in range(PATH_WINDOW + 3):
        record_cycle_paths(store, f'c{cycle}', 'cat reports/a.json', cwd=str(tmp_path))
    assert len(store.get('cycle_paths')['window']) == PATH_WINDOW
    assert repeated_paths(store, cwd=str(tmp_path))[0]['window'] == PATH_WINDOW

    # Writing notes is progress, so the streak -- and its evidence -- ends there.
    store.put('working_notes', {'notes': {'findings': ['implemented the backtest']}})
    finish_research_cycle(store, 'progress-cycle')

    assert store.get('cycle_paths')['window'] == []
    assert repeated_paths(store, cwd=str(tmp_path)) == []


def test_context_publishes_repeated_paths_with_an_instruction(tmp_path, monkeypatch):
    """The evidence has to reach the model, not just the store."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'reports').mkdir()
    (tmp_path / 'reports' / 'prereg.json').write_text('{}')
    agent = runner(tmp_path)
    for cycle in range(PATH_REPEAT_THRESHOLD):
        record_cycle_paths(agent.bits_store, f'c{cycle}', 'cat reports/prereg.json')

    published = agent._context(agent.source.read())['repeated_paths']

    assert published['paths'][0]['path'] == 'reports/prereg.json'
    assert 'not progress' in published['instruction']
    assert str(PATH_REPEAT_THRESHOLD) in published['instruction']
    agent.stop()
