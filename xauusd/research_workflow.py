"""Evidence completion, training schema and bounded repair guidance; no trade authority."""
from collections import Counter
import hashlib
import json
from pathlib import Path

from .atomic import atomic_write_json, atomic_write_text


def prepare_training(workspace, frame, version):
    """Export the supplied training partition only; never reconstruct timestamps."""
    import numpy as np
    import pandas as pd
    if (not isinstance(frame.index,pd.DatetimeIndex) or frame.index.tz is None
            or not frame.index.is_monotonic_increasing or frame.index.has_duplicates or frame.empty):
        raise ValueError('invalid_training_timestamps')
    columns=['open','high','low','close','volume']
    values=frame[columns].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values[:,:4]<=0).any() or (values[:,4]<0).any():
        raise ValueError('invalid_training_values')
    if ((frame.high<frame[['open','close','low']].max(axis=1)) |
            (frame.low>frame[['open','close','high']].min(axis=1))).any():
        raise ValueError('invalid_training_ohlc')
    exported=frame[columns].copy()
    exported.insert(0,'timestamp',[t.isoformat() for t in frame.index.tz_convert('UTC')])
    content=exported.to_csv(index=False)
    report={'scope':'training_only','dataset_version':version,'rows':len(frame),
            'columns':['timestamp',*columns],'timestamps_verified':True,
            'start':exported.timestamp.iloc[0],'end':exported.timestamp.iloc[-1],
            'irregular_intervals':int((frame.index.to_series().diff().iloc[1:]!=pd.Timedelta(minutes=1)).sum()),
            'csv_sha256':hashlib.sha256(content.encode()).hexdigest(),
            'gap_policy':'Exclude every lookback/label window spanning an irregular interval; never infer cadence from row order.'}
    atomic_write_text(Path(workspace)/'train.csv',content)
    atomic_write_json(Path(workspace)/'training_schema.json',report)
    return report


def provenance(workspace, arguments):
    """Hashes only: never retain source text, shell commands or private paths."""
    root=Path(workspace);files={}
    names=list(arguments.get('upload',[])) if isinstance(arguments.get('upload',[]),list) else []
    # Root research scripts plus explicitly uploaded artifacts; no recursive project scan.
    names+=sorted(p.name for p in root.glob('*.py'))[:40]
    for name in names[:60]:
        if not isinstance(name,str):continue
        p=Path(name)
        if p.is_absolute() or '..' in p.parts:continue
        source=root/p
        if any(x.is_symlink() for x in [source,*source.parents]) or not source.is_file() or source.stat().st_size>8*1024*1024:continue
        files[name]=hashlib.sha256(source.read_bytes()).hexdigest()
    return {'command_sha256':hashlib.sha256(str(arguments.get('command','')).encode()).hexdigest(),'files':files}


def resolve_call(store, identifier):
    """Exact durable ID, including earlier workspace IDs; no fuzzy attribution."""
    for row in store.meta('agent_calls') or []:
        if row['id']==identifier:return row
    for plan in store.meta('research_plans') or []:
        for variant in plan.get('variants',{}).values():
            if variant.get('call_id')==identifier and variant.get('evidence') is not None:
                return {'id':identifier,'name':variant.get('tool_name','analysis'),
                        'state':variant['state'],'result':variant['evidence'],
                        'provenance':variant.get('provenance',{}),'plan_id':plan['id']}
    for finding in store.meta('research_outcomes') or []:
        if finding.get('call_id')==identifier:
            return {'id':identifier,'name':'analysis','state':'completed','result':finding['evidence']}
    return None


def result_summary(store, identifier):
    row=resolve_call(store,identifier)
    if row is None:return {'ok':False,'error_code':'evidence_not_retained'}
    result=row.get('result') or {};metrics={};data=result
    output=result.get('output','')
    if isinstance(output,str):
        try:data=json.loads(output)
        except (ValueError,TypeError):pass
    # Explicit structured values only. No invented extraction from prose/tracebacks.
    if isinstance(data,dict):
        for k,v in data.items():
            if len(metrics)>=30:break
            if isinstance(k,str) and len(k)<=80 and (v is None or type(v) in (int,float,bool) or isinstance(v,str) and len(v)<=160):
                metrics[k]=v
        for k in ('thirds','costs_per_roundtrip','remove_best_two','metrics'):
            value=data.get(k)
            if value is not None and len(json.dumps(value,allow_nan=False))<=1800:metrics[k]=value
    return {'ok':True,'call_id':identifier,'state':row['state'],'execution_ok':result.get('ok') is True,
            'returncode':result.get('returncode'),'error_code':result.get('error_code'),
            'classification':'unvalidated_evidence_summary','metrics':metrics,
            'provenance':row.get('provenance',{}),'complete_evidence':False,
            'evidence_sha256':hashlib.sha256(json.dumps(result,sort_keys=True,allow_nan=False).encode()).hexdigest(),
            'retrieval':'evidence_read uses this exact call_id across workspaces; read raw pages only for missing details.'}


def blocker_category(plan):
    text=str(plan.get('reason','')).lower()
    if any(t in text for t in ('timestamp','input-schema','schema failure','gap','calibration third')):return 'data_schema'
    if any(t in text for t in ('hash','digest','provenance','another workspace','foreign call','submitted arguments')):return 'evidence_provenance'
    if any(t in text for t in ('numpy','dependency','module','missing')):return 'tool_environment'
    if any(t in text for t in ('publication','point-in-time','release time')):return 'source_availability'
    return 'experiment_implementation'


def workflow_status(store):
    plans=store.meta('research_plans') or []
    blockers=[{'id':p['id'],'family':p['family'],'category':blocker_category(p),
               'reason':str(p.get('reason',''))[:650],
               'next':'Inspect shared training_schema.json and prepared train.csv; use original UTC timestamps.' if blocker_category(p)=='data_schema' else
                      'Use result_summary with exact call_id and retained artifact hashes; never re-execute unknown work.' if blocker_category(p)=='evidence_provenance' else
                      'Reproduce once, test a bounded fix, then create a linked replacement plan; preserve the original outcome.'}
              for p in plans if p['state']=='blocked']
    pending=[{'plan_id':p['id'],'call_id':v['call_id'],'state':p['state']}
             for p in plans if not p.get('finding_ids')
             for v in p.get('variants',{}).values() if v.get('state')=='completed' and v.get('ok') is True]
    counts=Counter(p['state'] for p in plans)
    return {'scope':'retained_research_records','counts':dict(counts),'blockers':blockers,
            'blocker_categories':dict(Counter(r['category'] for r in blockers)),
            'training_schema':store.meta('training_schema'),
            'operator_release':{k:v for k,v in (store.meta('research_operator_release') or {}).items() if k in ('state','release_id','recorded_at')},
            'awaiting_findings':pending,'active_experiment_limit':2,'working_improvement_limit':1,
            'next_action':'interpret_completed_result' if pending else 'repair_shared_blocker' if any(b['category']=='data_schema' for b in blockers) else 'execute_independent_experiment',
            'escalations':[{'id':r['id'],'problem':r['problem'],'change':r['change'],'acceptance':r['acceptance'],
                            'next':'Prepare reproducible regression and concrete patch; escalate protected changes once. Do not bypass the boundary.'}
                           for r in store.meta('improvements') or [] if r.get('state')=='blocked'],
            'completion_policy':'At most two running plans, one working repair. Computation success is not a finding; software verification is not trading qualification.'}
