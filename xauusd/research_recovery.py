"""Bounded research investigations; uncertainty is never execution evidence."""
import hashlib
import json
from .lab_store import timestamp

MAX_MISSING_CHECKS = 2


def parked(row):
    return row.get('state') == 'unknown' and row.get('investigation', {}).get('state') == 'outcome_unavailable'


def synchronize(store):
    """Adopt prior recorded lookups without dispatching or inventing results."""
    calls = store.meta('agent_calls') or []
    changed = False
    for row in calls:
        if row.get('state') != 'unknown' or not row.get('remote_job_id'):
            continue
        investigation = row.setdefault('investigation', {})
        # Legacy last_remote_state proves one check, not an invented attempt count.
        fingerprint=hashlib.sha256(json.dumps({'name':'action_reconcile','arguments':{'call_id':row['id']}},sort_keys=True,allow_nan=False).encode()).hexdigest()
        retained=sum(c.get('name')=='action_reconcile' and c.get('fingerprint')==fingerprint and c.get('result',{}).get('state')=='not_found' for c in calls)
        count = max(investigation.get('missing_checks', 0), retained, int(row.get('last_remote_state') == 'not_found'))
        if count != investigation.get('missing_checks'):
            investigation['missing_checks'] = count
            changed = True
        if count >= MAX_MISSING_CHECKS and investigation.get('state') != 'outcome_unavailable':
            investigation.update(state='outcome_unavailable', recorded_at=timestamp())
            changed = True
    if changed:
        store.meta('agent_calls', calls)
    # Only dependent plans are parked; preserve variant IDs, evidence and budgets.
    ids = {r['id'] for r in calls if parked(r)}
    def pause(plans):
        for plan in plans:
            variants = list(plan.get('variants', {}).values())
            if (plan.get('state') == 'running' and variants
                    and any(v.get('call_id') in ids for v in variants)
                    and not any(v.get('state') in ('reserved', 'running') or
                                v.get('state') == 'unknown' and v.get('call_id') not in ids for v in variants)
                    and not any(v.get('state') == 'completed' and v.get('ok') is True for v in variants)):
                plan.update(state='blocked', reason='Historical execution outcome unavailable; dependent work parked, never replay its variants.',
                            recovery_parked=True)
        return plans
    store.update('research_plans', pause, [])


def status(store):
    calls = store.meta('agent_calls') or []
    unknown = [r for r in calls if r.get('state') == 'unknown']
    rows = [{'call_id':r['id'], 'state':'outcome_unavailable' if parked(r) else 'needs_investigation',
             'missing_checks':r.get('investigation', {}).get('missing_checks', 0),
             'last_checked_at':r.get('last_checked_at'), 'replay_allowed':False} for r in unknown]
    findings = store.meta('research_outcomes') or []
    cycles = (store.meta('agent') or {}).get('stagnation_cycles', 0)
    return {'pending':sum(not parked(r) for r in unknown), 'historical_unknown':sum(parked(r) for r in unknown),
            'actions':rows, 'missing_check_limit':MAX_MISSING_CHECKS, 'stagnation_cycles':cycles,
            'last_finding': {k:findings[-1].get(k) for k in ('id','hypothesis','recorded_at')} if findings else None,
            'required_next_step':'record_result_or_change_experiment_or_repair' if cycles >= 3 else 'continue_experiment',
            'policy':'Unavailable historical outcomes block dependent work only. Never replay. Reopen only with a newly retained matching completed job-status evidence reference.'}
