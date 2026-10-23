"""Evidence-linked conclusions and measurable progress, never qualification."""
import hashlib
import json
from .lab_store import serialized, timestamp


@serialized
def record(store, arguments):
    if set(arguments) != {'hypothesis', 'verdict', 'conclusion', 'call_id'}:
        return {'ok': False, 'error_code': 'invalid_outcome'}
    if any(not isinstance(v, str) or not 1 <= len(v) <= 2000 for v in arguments.values()) or arguments['verdict'] not in ('reject', 'investigate', 'retain'):
        return {'ok': False, 'error_code': 'invalid_outcome'}
    call = next((r for r in store.meta('agent_calls') or [] if r['id'] == arguments['call_id']), None)
    if not call or call['state'] != 'completed' or call['name'] not in ('tc02_run', 'analysis', 'action_reconcile') or call.get('result', {}).get('ok') is not True:
        return {'ok': False, 'error_code': 'completed_evidence_required'}
    rows = store.meta('research_outcomes') or []
    prior = next((r for r in rows if r['call_id'] == arguments['call_id']), None)
    if prior:
        return {'ok': True, 'id': prior['id'], 'replayed': True}
    evidence = call['result']
    row = {**arguments, 'id': hashlib.sha256(arguments['call_id'].encode()).hexdigest()[:24],
           'recorded_at': timestamp(), 'classification': 'advisor_conclusion_unvalidated',
           'evidence_sha256': hashlib.sha256(json.dumps(evidence, sort_keys=True, allow_nan=False).encode()).hexdigest(),
           'evidence': evidence}
    store.meta('research_outcomes', (rows + [row])[-100:])
    store.event('research_outcome', arguments['hypothesis'], {k: row[k] for k in ('id', 'verdict', 'conclusion', 'call_id')})
    return {'ok': True, 'id': row['id']}


@serialized
def improvement(store, arguments):
    required = {'id', 'problem', 'change', 'acceptance', 'state'}
    if set(arguments) != required or any(not isinstance(v, str) or not 1 <= len(v) <= 2000 for v in arguments.values()) or arguments['state'] not in ('planned', 'working', 'blocked', 'verified'):
        return {'ok': False, 'error_code': 'invalid_improvement'}
    release = store.meta('engineering') or {}
    rows = store.meta('improvements') or []
    prior = next((r for r in rows if r['id'] == arguments['id']), None)
    if arguments['state'] == 'verified' and (release.get('state') != 'verified' or not prior or not release.get('release_id') or release['release_id'] == prior.get('baseline_release_id')):
        return {'ok': False, 'error_code': 'verified_release_required'}
    row = {**arguments, 'updated_at': timestamp(), 'baseline_release_id': prior.get('baseline_release_id') if prior else release.get('release_id'), 'release_id': release.get('release_id') if arguments['state'] == 'verified' else None}
    rows = [r for r in rows if r['id'] != row['id']]
    store.meta('improvements', (rows + [row])[-60:])
    return {'ok': True, 'id': row['id'], 'state': row['state']}


def progress_signature(store):
    # Discovery, changing prose, arbitrary scripts and job IDs are not outcomes.
    release = store.meta('engineering') or {}
    data = {'outcomes': [r['id'] for r in store.meta('research_outcomes') or []],
            'retired': [r['id'] for r in store.meta('experiment_archive') or []],
            'release': release.get('release_id') if release.get('state') == 'verified' else None}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
