"""Measured research overhead and bounded before/after engineering evidence."""
from collections import Counter
from .lab_store import timestamp
from .research_program import finite

METRICS={'tool_failure_rate':'down','evidence_read_share':'down','tool_seconds':'down','inference_seconds':'down'}


def release_id(store):
    row=store.meta('engineering') or {}
    operator=store.meta('research_operator_release') or {}
    if operator.get('state')=='verified' and operator.get('engineering_base')==row.get('release_id'):
        return operator.get('release_id')
    return row.get('release_id') if row.get('state')=='verified' else None


def inference(store,seconds,ok,brief_bytes):
    row={'seconds':seconds,'ok':ok,'brief_bytes':brief_bytes,'recorded_at':timestamp(),'release_id':release_id(store)}
    def append(value):
        value=value or {'started_at':timestamp(),'count':0,'seconds':0.,'failed':0,'samples':[]}
        value['count']+=1;value['seconds']+=seconds;value['failed']+=not ok
        value['samples']=(value['samples']+[row])[-120:]
        return value
    store.update('research_inference',append)


def metric(store,name,release=None):
    if name=='inference_seconds':
        rows=(store.meta('research_inference') or {}).get('samples',[])
        rows=[r for r in rows if release is None or r.get('release_id')==release][-20:]
        values=[r['seconds'] for r in rows if finite(r.get('seconds'))]
        return {'value':sum(values)/len(values) if values else None,'samples':len(values)}
    rows=[r for r in store.meta('agent_calls') or [] if r.get('state') in ('completed','unknown')
          and (release is None or r.get('release_id')==release)]
    rows=sorted(rows,key=lambda r:r.get('finished_at') or r.get('started_at') or '')[-20:]
    if name=='tool_failure_rate':values=[float((r.get('result') or {}).get('ok') is not True) for r in rows]
    elif name=='evidence_read_share':values=[float(r.get('name')=='evidence_read') for r in rows]
    elif name=='tool_seconds':values=[r['duration_seconds'] for r in rows if finite(r.get('duration_seconds'))]
    else:return {'value':None,'samples':0}
    return {'value':sum(values)/len(values) if values else None,'samples':len(values)}


def start_measurement(store,identifier,name):
    if name not in METRICS:return {'ok':False,'error_code':'unknown_measurement_metric'}
    rows=store.meta('improvement_measurements') or []
    prior=next((r for r in rows if r['id']==identifier),None)
    if prior:return {'ok':True,'id':identifier,'replayed':True}
    baseline=metric(store,name)
    row={'id':identifier,'metric':name,'direction':METRICS[name],'baseline':baseline,
         'baseline_release_id':release_id(store),'created_at':timestamp(),'state':'awaiting_verified_release',
         'minimum_samples':10,'relative_improvement_required':.10,
         'interpretation':'observational_productivity_measure_not_causal_or_trading_evidence'}
    store.meta('improvement_measurements',(rows+[row])[-60:])
    return {'ok':True,'id':identifier,'baseline':baseline}


def review(store):
    # Seed only measured, actionable bottlenecks. Never overwrite an existing item.
    observations=diagnostics(store)
    backlog=store.meta('improvements') or []
    for issue in observations['bottlenecks']:
        name={'retrieval_overhead':'evidence_read_share','repeated_inspection':'tool_seconds','inference_failures':'inference_seconds'}.get(issue['id'])
        identifier='observed:'+issue['id']
        existing=next((r for r in backlog if r['id']==identifier),None)
        if name and existing and existing.get('state')=='verified':
            # Historical release verification survives; recurrence creates fresh work.
            def reopen(rows):
                return [{**r,'state':'planned','recurrence':True,'previous_verified_release_id':r.get('release_id'),
                         'problem':issue['problem'],'change':issue['next'],'updated_at':timestamp()}
                        if r['id']==identifier else r for r in rows]
            store.update('improvements',reopen,[])
        if name and existing is None:
            from .agent_outcomes import improvement
            improvement(store,{'id':identifier,'problem':issue['problem'],'change':issue['next'],
                'acceptance':'Observed improvement of at least 10% with ten samples per window; existing tests and controls unchanged.',
                'state':'planned','metric':name})
    rows=store.meta('improvement_measurements') or [];current=release_id(store)
    linked={r['id']:r for r in store.meta('improvements') or []}
    for row in rows:
        if row['state'] in ('improved','regressed','no_measurable_change','insufficient_baseline','superseded_without_measurement'):continue
        item=linked.get(row['id']) or {}
        if not current or current==row['baseline_release_id']:continue
        if item.get('state')!='verified' or item.get('release_id')!=current:
            row['state']='awaiting_linked_verified_improvement'
            continue
        if row.get('measured_release_id') not in (None,current):
            row.update(state='superseded_without_measurement');continue
        row['measured_release_id']=current
        if row['baseline']['samples']<10 or row['baseline']['value'] is None:
            row.update(state='insufficient_baseline');continue
        after=metric(store,row['metric'],current);row['after']=after
        if after['samples']<10:row.update(state='collecting_samples');continue
        before=row['baseline']['value'];delta=before-after['value']
        if before==0: state='regressed' if after['value']>0 else 'no_measurable_change'
        elif delta/before>=.10:state='improved'
        elif delta/before<=-.10:state='regressed'
        else:state='no_measurable_change'
        row.update(state=state,recorded_at=timestamp(),relative_change=delta/before if before else None)
    if rows:store.meta('improvement_measurements',rows)
    return {'ok':True,'measurements':rows,'policy':'At least 10 samples each; observed 10% change, not causal proof. Regressions need a normal tested corrective release.'}


def diagnostics(store):
    calls=[r for r in store.meta('agent_calls') or [] if r.get('state') in ('completed','unknown')]
    recent=sorted(calls,key=lambda r:r.get('finished_at') or r.get('started_at') or '')[-20:]
    counts=Counter(r.get('name') for r in recent)
    findings=store.meta('research_outcomes') or []
    recent_inference=store.meta('research_inference') or {}
    warnings=[]
    samples=recent_inference.get('samples',[])[-20:]
    if len(samples)>=10 and sum(not r['ok'] for r in samples)/len(samples)>=.2:
        warnings.append({'id':'inference_failures','problem':'At least 20% of recent advisor turns failed.',
                         'next':'Repair turn completion with a reproducible regression; preserve durable tool results and avoid replay.'})
    if len(recent)>=10 and counts['evidence_read']/len(recent)>=.5:
        warnings.append({'id':'retrieval_overhead','problem':'At least half of retained calls retrieve evidence.',
                         'next':'Inspect result structure; build/test a targeted summary or batch tool, then measure evidence_read_share.'})
    if len(recent)>=10 and counts['tc02_inspect']/len(recent)>=.2:
        warnings.append({'id':'repeated_inspection','problem':'Worker inspection is at least 20% of retained calls.',
                         'next':'Reuse recent capability evidence and measure tool_seconds.'})
    from .research_recovery import parked
    historical=sum(parked(r) for r in calls)
    unknown=sum(r.get('state')=='unknown' and not parked(r) for r in calls)
    if unknown:warnings.append({'id':'unknown_results','problem':str(unknown)+' unresolved outcomes remain.',
                               'next':'Retrieve known job status once; absent remote evidence stays unknown and must not replay.'})
    plans=store.meta('research_plans') or []
    from .research_workflow import pending_results
    missing=len({r['plan_id'] for r in pending_results(plans,True)})
    if missing:warnings.append({'id':'unrecorded_results','problem':str(missing)+' running plans have successful results but no finding.',
                               'next':'Read results and record a supported conclusion before launching another variation.'})
    failed=len({r['plan_id'] for r in pending_results(plans,False)})
    if failed:warnings.append({'id':'non_success_results','problem':str(failed)+' running plans have terminal results not confirmed successful and no finding.',
                               'next':'Inspect the exact retained result; preserve uncertainty and do not invent a finding or replay unknown work.'})
    return {'scope':'bounded_retained_samples','recorded_at':timestamp(),
            'calls':len(calls),'findings':len(findings),'unresolved':unknown,'historical_unknown':historical,
            'inference':{k:v for k,v in recent_inference.items() if k!='samples'},
            'metrics':{name:metric(store,name) for name in METRICS},'bottlenecks':warnings,
            'measurements':store.meta('improvement_measurements') or [],
            'current_regressions':[{'id':w['id'],'state':'recurring','historical_verification_preserved':True}
                for w in warnings if any(r.get('id')=='observed:'+w['id'] and r.get('state')=='verified'
                    for r in store.meta('improvements') or [])]}
