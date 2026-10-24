"""Evidence-linked conclusions and measurable progress, never qualification."""
import hashlib
import json
import math
import re
from .lab_store import serialized, timestamp


@serialized
def record(store, arguments):
    required = {'hypothesis', 'verdict', 'conclusion', 'call_id'}
    if not required <= set(arguments) or set(arguments) - required - {'experiment'}:
        return {'ok': False, 'error_code': 'invalid_outcome'}
    if any(not isinstance(v, str) or not 1 <= len(v) <= 2000 for v in (arguments[k] for k in required)) or arguments['verdict'] not in ('reject', 'investigate', 'retain'):
        return {'ok': False, 'error_code': 'invalid_outcome'}
    call = next((r for r in store.meta('agent_calls') or [] if r['id'] == arguments['call_id']), None)
    if not call or call['state'] != 'completed' or call['name'] not in ('tc02_run', 'analysis', 'action_reconcile') or call.get('result', {}).get('ok') is not True:
        return {'ok': False, 'error_code': 'completed_evidence_required'}
    rows = store.meta('research_outcomes') or []
    experiment = arguments.get('experiment')
    identity = None
    if experiment is not None:
        expected = {'family', 'dataset_version', 'code_sha256', 'parameters', 'costs', 'metrics', 'failure_reason', 'parent_id'}
        if not isinstance(experiment, dict) or set(experiment) != expected:
            return {'ok': False, 'error_code': 'invalid_experiment_shape'}
        if any(not isinstance(experiment[k], str) or not 1 <= len(experiment[k]) <= 200 for k in ('family', 'dataset_version')):
            return {'ok': False, 'error_code': 'invalid_experiment_identity'}
        if not isinstance(experiment['code_sha256'], str) or not re.fullmatch('[a-f0-9]{64}', experiment['code_sha256']):
            return {'ok': False, 'error_code': 'invalid_code_digest'}
        if not isinstance(experiment['failure_reason'], str) or len(experiment['failure_reason']) > 1000:
            return {'ok': False, 'error_code': 'invalid_failure_reason'}
        if experiment['parent_id'] is not None and not any(r['id'] == experiment['parent_id'] for r in rows):
            return {'ok': False, 'error_code': 'parent_finding_not_retained'}
        for key in ('parameters', 'costs', 'metrics'):
            values = experiment[key]
            if not isinstance(values, dict) or len(values) > 40 or any(not isinstance(k, str) or len(k) > 80 for k in values):
                return {'ok': False, 'error_code': 'invalid_experiment_values'}
            for value in values.values():
                numeric = type(value) in (int, float) and math.isfinite(value)
                if not (value is None or numeric or key == 'parameters' and isinstance(value, str) and len(value) <= 200):
                    return {'ok': False, 'error_code': 'invalid_experiment_metric'}
        identity = hashlib.sha256(json.dumps({k: experiment[k] for k in ('family', 'dataset_version', 'code_sha256', 'parameters', 'costs')}, sort_keys=True, allow_nan=False).encode()).hexdigest()
        equivalent = next((r for r in rows if r.get('experiment_identity') == identity), None)
        if equivalent:
            return {'ok': True, 'id': equivalent['id'], 'replayed': True, 'equivalent_experiment': True}
    prior = next((r for r in rows if r['call_id'] == arguments['call_id']), None)
    if prior:
        return {'ok': True, 'id': prior['id'], 'replayed': True}
    evidence = call['result']
    row = {**arguments, 'id': hashlib.sha256(arguments['call_id'].encode()).hexdigest()[:24],
           'recorded_at': timestamp(), 'classification': 'advisor_conclusion_unvalidated',
           'evidence_sha256': hashlib.sha256(json.dumps(evidence, sort_keys=True, allow_nan=False).encode()).hexdigest(),
           'evidence': evidence, 'experiment_identity': identity}
    store.update('research_outcomes', lambda current: ((current or []) + [row])[-100:], [], observation=('findings', row))
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


def lookup(store, arguments):
    if set(arguments) - {'family', 'id'} or any(not isinstance(v, str) or len(v) > 200 for v in arguments.values()):
        return {'ok': False, 'error_code': 'invalid_research_lookup'}
    rows = store.meta('research_outcomes') or []
    matches = [r for r in rows if (not arguments.get('id') or r['id'] == arguments['id'])
               and (not arguments.get('family') or (r.get('experiment') or {}).get('family') == arguments['family'])]
    return {'ok': True, 'scope': 'retained_findings', 'findings':
            [{k:v for k,v in r.items() if k != 'evidence'} for r in matches[-10:]]}
