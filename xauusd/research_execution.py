"""Deterministic research stage selection; no trading or recovery authority."""
from .research_effectiveness import diagnostics
from .research_workflow import workflow_status


def directive(store):
    workflow=workflow_status(store); observed=diagnostics(store)
    blocked={r['id'] for r in store.meta('improvements') or [] if r.get('state')=='blocked'}
    issues=[i for i in observed['bottlenecks'] if 'observed:'+i['id'] not in blocked]
    pending=workflow['awaiting_findings']
    stage='interpret_result' if pending else 'repair' if issues else 'experiment'
    target=pending[0] if pending else next((i for i in issues if i['id']=='inference_failures'),issues[0] if issues else None)
    row={'stage':stage,'target':target,'stagnation_cycles':(store.meta('agent') or {}).get('stagnation_cycles',0),
         'paper_capacity_blocks_research':False,'blocked_repairs':sorted(blocked),
         'protected_repair_policy':'If the target requires protected files, prepare one regression and proposed patch, record a blocked improvement, then continue independent research. Never loop waiting or bypass protection.',
         'completion':'Record a supported finding, or deploy and measure a regression-tested repair. Reading alone is not completion.',
         'next':'Interpret the exact completed call and record its finding.' if pending else
                'Reproduce this defect, prepare one bounded patch and regression, check and deploy through existing engineering tools.' if issues else
                'Preregister one independent hypothesis and execute it on supplied training data; use tc02 for heavy computation.'}
    # Durable stage, refreshed from current evidence; never resets progress or clears controls.
    store.meta('research_execution',row)
    return row
