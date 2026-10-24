"""Small transactional counters; detailed evidence may expire independently."""
from datetime import datetime, timezone
import math

KEY = 'lab:statistics'


def transition(tx, kind, previous, row):
    """Called inside the transaction that writes the owning row."""
    known_tools = {'tc02_run','tc02_job_status','tc02_inspect','analysis','source_search','source_fetch','source_domain',
                   'market_observe','dependency_install','engineering_check','engineering_deploy','evidence_read',
                   'research_record','research_lookup','improvement_record','experiment_start','experiment_review',
                   'experiment_retire','action_reconcile','research_program','research_plan','research_plan_close','research_insight','improvement_review'}
    if kind.startswith('tools.') and kind[6:] not in known_tools:
        kind = 'tools.other'
    now = datetime.now(timezone.utc).isoformat()
    tx.lock(KEY)
    value = tx.get(KEY) or {'scope':'since_counter_installation', 'started_at':now,
                           'totals':{}, 'daily':{}}
    day = now[:10]
    daily = value['daily'].setdefault(day, {})
    def add(key, amount=1):
        value['totals'][key] = value['totals'].get(key, 0) + amount
        daily[key] = daily.get(key, 0) + amount
    state = row.get('state', row.get('verdict'))
    prior = (previous or {}).get('state', (previous or {}).get('verdict'))
    if previous is None and kind=='research_plans':
        add(kind+'.registered')
    if previous is None and state == 'running':
        add(kind + '.started')
    if state != prior and state in ('completed','failed','interrupted','unknown','rejected','qualified','active','reject','retain','investigate'):
        add(kind + '.' + state)
        duration=row.get('duration_seconds')
        if state=='completed' and type(duration) in (int,float) and math.isfinite(duration) and duration>=0:
            add(kind+'.seconds',duration)
            add(kind+'.timed_calls')
        if kind == 'tools.tc02_run' and state == 'completed':
            result = row.get('result') or {}
            add('tc02.successful' if result.get('ok') is True else 'tc02.unsuccessful')
            for key in ('cpu_seconds', 'wall_seconds'):
                metric = result.get(key)
                if type(metric) in (int,float) and math.isfinite(metric) and metric >= 0:
                    add('tc02.' + key, metric)
                    add('tc02.' + key + '_measured_jobs')
    value['daily'] = {k:value['daily'][k] for k in sorted(value['daily'])[-90:]}
    value['recorded_at'] = now
    tx.put(KEY, value)


def snapshot(store):
    return store.meta('statistics') or {'scope':'not_installed', 'started_at':None,
                                       'totals':{}, 'daily':{}}
