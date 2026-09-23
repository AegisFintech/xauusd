"""Compact observations and persistent research-progress signals, never trade signals."""
import hashlib
import json
from pathlib import Path

RESEARCH_POLICY = (
    'Continue research across cycles; do not repeat bootstrap on every invocation. '
    'Current account and freshness are already supplied. Read repository guidance once per revision; '
    'when bootstrap.reviewed is true, do not reread it or CLI help without a specific new need. '
    'Use shell to inspect historical data and existing research, define a concrete hypothesis, '
    'then calculate indicators and run a cost-aware historical experiment. Save source-linked findings, '
    'hypotheses, rejected approaches and next steps with bits-memory write. '
    'Do not infer an edge from five closes or wait indefinitely because an edge has not yet been tested. '
    'A wait must identify measurable entry/invalidation conditions, the evidence supporting them, '
    'or a specific blocker and the next experiment. Never manufacture evidence or force a trade. '
    'Keep command output concise, with findings first; do not dump guidance and memory repeatedly. '
    'For omitted output retrieve pages from the ORIGINAL job ID using next_offset; never page a page job. '
    'No notes update is only a progress warning, not proof that analysis failed. '
    'All trade proposals still go through propose_trade and existing gates.'
)


def guidance_revision():
    try:
        return hashlib.sha256(Path('AGENTS.md').read_bytes()).hexdigest()
    except OSError:
        return None


def market_research(source):
    try:
        frame = source.store.normalize(source.store.read())
        closes = frame['close'].astype(float)
        result = {'rows': len(frame), 'start': str(frame.index[0]), 'end': str(frame.index[-1]),
                  'interpretation': 'Descriptive observations only; bar windows may contain time gaps.',
                  'windows': {}}
        for size in (15, 60, 240):
            part = closes.tail(size)
            if len(part) < size:
                continue
            result['windows'][str(size)] = {
                'bars': size, 'start': str(part.index[0]), 'end': str(part.index[-1]),
                'first_close': float(part.iloc[0]), 'last_close': float(part.iloc[-1]),
                'min_close': float(part.min()), 'max_close': float(part.max()),
                'mean_close': float(part.mean()),
                'close_change': float(part.iloc[-1] - part.iloc[0]),
                'mean_absolute_close_change': float(part.diff().abs().mean())}
        # Fail closed on invalid numerical observations; never send NaN as evidence.
        json.dumps(result, allow_nan=False)
        return result
    except Exception:
        return {'available': False, 'next_step': 'Inspect historical dataset through shell.'}


def finish_research_cycle(store, cycle_id):
    progress = store.get('research_progress', {})
    if progress.get('cycle_id') == cycle_id:
        return progress
    notes = store.get('working_notes') or {}
    fingerprint = hashlib.sha256(json.dumps(notes.get('notes'), sort_keys=True).encode()).hexdigest()
    changed = bool(notes.get('notes')) and fingerprint != progress.get('notes_fingerprint')
    count = 0 if changed else progress.get('cycles_without_new_notes', 0) + 1
    progress = {'cycle_id': cycle_id, 'notes_fingerprint': fingerprint,
                'cycles_without_new_notes': count, 'needs_attention': count >= 3,
                'description': 'Completed cycles without changed research notes; this is a progress proxy, not a trade requirement.'}
    store.put('research_progress', progress)
    return progress
