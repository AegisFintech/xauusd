"""Bounded research agenda, preregistration, discovery and cumulative lessons.

These records organize untrusted proposals. They confer no trading authority.
"""
from copy import deepcopy
import hashlib
import json
import math
import re
from urllib.parse import urlparse
from .lab_store import serialized, timestamp

TOPICS = {'macro':'Rates, dollar and macro transmission', 'events':'Scheduled news and release timing',
          'positioning':'Positioning and cross-market relationships', 'liquidity':'Liquidity, spreads and execution',
          'methods':'Research methods, data quality and tooling', 'price':'Price and volume behavior'}
TERMINAL = {'completed','blocked','abandoned'}

PLAN_INPUT_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'properties': {
        **{k: {'type': 'string', 'minLength': 1, 'maxLength': maximum}
           for k, maximum in {
               'family': 100, 'question': 2000, 'hypothesis': 2000,
               'baseline': 2000, 'dataset_version': 200, 'data_requirements': 2000,
               'success_criteria': 2000, 'change_reason': 2000}.items()},
        'topic': {'type': 'string', 'enum': sorted(TOPICS)},
        'source_ids': {'type': 'array', 'maxItems': 5, 'items': {'type': 'string'}},
        'costs': {'type': 'object', 'minProperties': 1, 'maxProperties': 20,
                  'propertyNames': {'minLength': 1, 'maxLength': 80},
                  'additionalProperties': {'type': 'number', 'minimum': 0}},
        'max_variants': {'type': 'integer', 'minimum': 1, 'maximum': 12},
        'parent_id': {'type': ['string', 'null']},
    },
}
PLAN_INPUT_SCHEMA['required'] = sorted(PLAN_INPUT_SCHEMA['properties'])


def dataset_version_hint(store):
    dataset=store.meta('dataset')
    if not isinstance(dataset,dict): return None
    version=dataset.get('version')
    return version if isinstance(version,str) and re.fullmatch(r'[a-f0-9]{64}',version) else None


def plan_input_schema(store):
    schema=deepcopy(PLAN_INPUT_SCHEMA)
    version=dataset_version_hint(store)
    if version is not None:
        schema['properties']['dataset_version']['const']=version
    return schema


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,allow_nan=False).encode()).hexdigest()


def text(value, maximum=2000):
    return isinstance(value,str) and 0 < len(value) <= maximum


def finite(value):
    try: return type(value) in (int,float) and math.isfinite(value)
    except OverflowError: return False


def ensure(store):
    def initialize(current):
        return current or {'schema':'xauusd.research-program/1','started_at':timestamp(),
                           'plan_required':True,'cycles':0,'topics':{k:{'plans':0,'findings':0,'rejected':0} for k in TOPICS}}
    return store.update('research_program',initialize)


def begin_cycle(store):
    ensure(store)
    # Upgrade only still-retained exact evidence; never reconstruct missing results.
    for row in store.meta('agent_calls') or []:
        if row.get('plan_id') and any(p['id']==row['plan_id'] and
                row.get('variant_id') in p['variants'] and
                'evidence' not in p['variants'][row['variant_id']] for p in store.meta('research_plans') or []):
            finish_call(store,row)
    def advance(program):
        program['cycles']=program.get('cycles',0)+1
        return program
    store.update('research_program',advance)


def _trim_plans(plans):
    terminal=sorted((p for p in plans or [] if p['state'] in TERMINAL),key=lambda p:p.get('closed_at') or p['created_at'])[-80:]
    return terminal+[p for p in plans or [] if p['state'] not in TERMINAL]


def _summary_source(row):
    return {k:row.get(k) for k in ('id','kind','url','retrieved_at','digest','call_id')}


@serialized
def capture_source(store, name, arguments, result, call_id):
    if name not in ('source_search','source_fetch') or result.get('ok') is not True: return
    retrieved=result.get('retrieved_at')
    if not text(retrieved,100) or not re.fullmatch('[a-f0-9]{64}',str(result.get('digest',''))): return
    candidates=result.get('results',[])[:10] if name=='source_search' else [result]
    incoming=[]
    for source in candidates:
        url=source.get('url','')
        if not text(url,1000): continue
        parsed=urlparse(url)
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password: continue
        kind='lead' if name=='source_search' else 'retrieved'
        incoming.append({'id':digest([url,result['digest'],kind])[:24], 'kind':kind,'url':url,
                         'retrieved_at':retrieved,'digest':result['digest'],'call_id':call_id,
                         'title':str(source.get('title',''))[:250],
                         'excerpt':str(source.get('excerpt',''))[:2000] if kind=='retrieved' else '',
                         'trusted':False,'historical_availability_verified':False})
    def append(current):
        rows=current or []
        return ([r for r in rows if r['id'] not in {v['id'] for v in incoming}]+incoming)[-100:]
    store.update('research_sources',append,[])
    return [_summary_source(r) for r in incoming]


@serialized
def insight(store, args):
    if set(args)!={'topic','question','finding','next_test','source_ids'} or args.get('topic') not in TOPICS:
        return {'ok':False,'error_code':'invalid_insight'}
    if any(not text(args[k]) for k in ('question','finding','next_test')):
        return {'ok':False,'error_code':'invalid_insight'}
    ids=args['source_ids']; sources=store.meta('research_sources') or []
    if not isinstance(ids,list) or not 1<=len(ids)<=5 or any(not isinstance(i,str) for i in ids):
        return {'ok':False,'error_code':'retrieved_sources_required'}
    selected=[r for r in sources if r['id'] in ids and r['kind']=='retrieved']
    if len({r['id'] for r in selected})!=len(set(ids)):
        return {'ok':False,'error_code':'retrieved_sources_required'}
    row={**deepcopy(args),'id':digest(args)[:24],'recorded_at':timestamp(),
         'classification':'advisor_interpretation_unvalidated','historical_availability_verified':False,
         'sources':[_summary_source(r) for r in selected]}
    def append(rows): return ([r for r in rows or [] if r['id']!=row['id']]+[row])[-100:]
    store.update('research_insights',append,[])
    return {'ok':True,'id':row['id'],'classification':row['classification']}


@serialized
def create_plan(store, args):
    required=set(PLAN_INPUT_SCHEMA['required'])
    if (not isinstance(args,dict) or set(args)!=required or
            not isinstance(args.get('topic'),str) or args['topic'] not in TOPICS):
        supplied=set(args) if isinstance(args,dict) else set()
        return {'ok':False,'error_code':'invalid_plan_shape','path':'$',
                'expected_fields':sorted(required),'missing_fields':sorted(required-supplied),
                'unexpected_field_count':len(supplied-required),
                'allowed_topics':sorted(TOPICS)}
    if any(not text(args[k]) for k in ('family','question','hypothesis','baseline','dataset_version',
                                     'data_requirements','success_criteria','change_reason')):
        return {'ok':False,'error_code':'invalid_plan_text'}
    if len(args['family'])>100 or len(args['dataset_version'])>200 or type(args['max_variants']) is not int or not 1<=args['max_variants']<=12:
        return {'ok':False,'error_code':'invalid_plan_budget'}
    costs=args['costs']
    if not isinstance(costs,dict) or not costs or len(costs)>20 or any(not text(k,80) or not finite(v) or v<0 for k,v in costs.items()):
        return {'ok':False,'error_code':'finite_costs_required'}
    dataset=store.meta('dataset')
    if dataset is None: dataset={}
    if not isinstance(dataset,dict): return {'ok':False,'error_code':'dataset_metadata_invalid'}
    if dataset.get('version') and args['dataset_version']!=dataset['version']:
        result={'ok':False,'error_code':'current_training_dataset_required'}
        version=dataset_version_hint(store)
        if version is not None: result['expected_dataset_version']=version
        return result
    sources=store.meta('research_sources') or []
    ids=args['source_ids']
    if not isinstance(ids,list) or len(ids)>5 or any(not isinstance(i,str) for i in ids):
        return {'ok':False,'error_code':'invalid_plan_sources'}
    selected=[r for r in sources if r['id'] in ids]
    if len({r['id'] for r in selected})!=len(set(ids)):
        return {'ok':False,'error_code':'source_not_retained'}
    plans=store.meta('research_plans') or []
    if args['parent_id'] is not None and not any(p['id']==args['parent_id'] for p in plans):
        return {'ok':False,'error_code':'parent_plan_not_retained'}
    identity=digest({k:args[k] for k in required-{'question','change_reason','parent_id','source_ids'}})
    prior=next((p for p in plans if p['identity']==identity),None)
    if prior: return {'ok':True,'id':prior['id'],'replayed':True,'state':prior['state']}
    if sum(p['state'] not in TERMINAL for p in plans)>=20:
        return {'ok':False,'error_code':'open_plan_limit'}
    row={**deepcopy(args),'id':identity[:24],'identity':identity,'created_at':timestamp(),
         'state':'planned','variants':{},'finding_ids':[],'sources':[_summary_source(s) for s in selected]}
    store.update('research_plans',lambda current:_trim_plans(current)+[row],[],observation=('research_plans',row))
    def topic_count(program):
        program['topics'][args['topic']]['plans']+=1
        program['topics'][args['topic']]['last_plan_at']=timestamp()
        return program
    ensure(store);store.update('research_program',topic_count)
    store.event('research_plan',args['question'],{'id':row['id'],'topic':row['topic'],'max_variants':row['max_variants']})
    return {'ok':True,'id':row['id'],'state':'planned'}


@serialized
def reserve(store, name, arguments, call_id):
    if name not in ('analysis','tc02_run') or not (store.meta('research_program') or {}).get('plan_required'):
        return {'ok':True,'arguments':arguments}
    args=dict(arguments);plan_id=args.pop('plan_id',None);variant=args.pop('variant_id',None)
    if not text(plan_id,100) or not isinstance(variant,str) or not re.fullmatch('[a-zA-Z0-9_-]{1,64}',variant):
        return {'ok':False,'error_code':'research_plan_required'}
    # One transaction reserves the variant before any external execution.
    with store.state.transaction() as tx:
        tx.lock('lab:research_plans');plans=tx.get('lab:research_plans',[])
        plan=next((p for p in plans if p['id']==plan_id),None)
        if not plan or plan['state'] in TERMINAL:return {'ok':False,'error_code':'plan_not_open'}
        if variant in plan['variants']:
            return {'ok':False,'error_code':'plan_variant_already_reserved','call_id':plan['variants'][variant]['call_id']}
        if len(plan['variants'])>=plan['max_variants']:return {'ok':False,'error_code':'plan_variant_budget_exhausted'}
        if any(p['state'] not in TERMINAL and not p.get('finding_ids') and
               any(v.get('state')=='completed' and v.get('ok') is True for v in p['variants'].values()) for p in plans):
            return {'ok':False,'error_code':'record_completed_result_first'}
        if plan['state']!='running' and sum(p['state']=='running' for p in plans)>=2:
            return {'ok':False,'error_code':'active_experiment_limit'}
        plan['variants'][variant]={'call_id':call_id,'reserved_at':timestamp(),'state':'reserved',
                                   'command_sha256':digest(args),'remote_job_id':hashlib.sha256(call_id.encode()).hexdigest()[:32] if name=='tc02_run' else None}
        plan['state']='running';tx.put('lab:research_plans',plans)
    return {'ok':True,'arguments':args,'plan_id':plan_id,'variant_id':variant}


@serialized
def finish_call(store, row):
    if not row.get('plan_id'):return
    def update(plans):
        for p in plans or []:
            if p['id']!=row['plan_id']:continue
            v=p['variants'].get(row['variant_id'])
            if not v or v['call_id']!=row['id']:continue
            result=row.get('result') or {}
            v.update(state=row['state'],ok=result.get('ok') is True,
                     error_code=result.get('error_code'),remote_job_id=row.get('remote_job_id'),
                     finished_at=row.get('finished_at'))
            if row.get('provenance'):v['provenance']=row['provenance']
            v['tool_name']=row.get('name','analysis')
            if row['state'] in ('completed','unknown'):
                v['evidence']=result
        return plans
    store.update('research_plans',update,[])


@serialized
def close_plan(store,args):
    if set(args)!={'id','state','reason'} or args.get('state') not in TERMINAL or not text(args.get('reason')):
        return {'ok':False,'error_code':'invalid_plan_close'}
    with store.state.transaction() as tx:
        tx.lock('lab:research_plans');plans=tx.get('lab:research_plans',[])
        p=next((r for r in plans if r['id']==args['id']),None)
        if not p:return {'ok':False,'error_code':'plan_not_retained'}
        if any(v['state'] in ('reserved','running','unknown') for v in p['variants'].values()):
            return {'ok':False,'error_code':'plan_has_unresolved_variants'}
        if args['state']=='completed' and not p['finding_ids']:
            return {'ok':False,'error_code':'plan_finding_required'}
        if p['state'] in TERMINAL:return {'ok':True,'id':p['id'],'replayed':True}
        previous=deepcopy(p)
        p.update(state=args['state'],reason=args['reason'],closed_at=timestamp())
        from .lab_statistics import transition
        transition(tx,'research_plans',previous,p)
        tx.put('lab:research_plans',_trim_plans(plans))
    return {'ok':True,'id':p['id'],'state':p['state']}


@serialized
def learn(store,finding,topic=None):
    def bind(plans):
        nonlocal topic
        for p in plans or []:
            if finding.get('call_id') and any(v['call_id']==finding['call_id'] for v in p['variants'].values()):
                topic=p['topic']
                p['finding_ids']=list(dict.fromkeys(p['finding_ids']+[finding['id']]))[-12:]
        return plans
    store.update('research_plans',bind,[])
    if topic not in TOPICS:return
    family=(finding.get('experiment') or {}).get('family') or finding['hypothesis'][:100]
    key=digest([topic,family])[:24]
    def update(current):
        rows=current or [];previous=next((r for r in rows if r['id']==key),None)
        row=previous or {'id':key,'topic':topic,'family':family,'findings':0,'rejected':0,'recent_ids':[]}
        if finding['id'] in row['recent_ids']:return rows
        row['findings']+=1;row['rejected']+=finding['verdict']=='reject'
        row.update(last_conclusion=finding['conclusion'][:1000],last_finding_id=finding['id'],
                   recent_ids=(row['recent_ids']+[finding['id']])[-12:],updated_at=timestamp())
        return ([r for r in rows if r['id']!=key]+[row])[-64:]
    before=store.meta('research_lessons') or []
    after=store.update('research_lessons',update,[])
    if before==after:return
    def count(program):
        program['topics'][topic]['findings']+=1
        program['topics'][topic]['rejected']+=finding['verdict']=='reject'
        program['last_topic']=topic
        return program
    ensure(store);store.update('research_program',count)


def context(store, compact=False):
    program=store.meta('research_program') or {}
    plans=store.meta('research_plans') or [];lessons=store.meta('research_lessons') or []
    counts=program.get('topics',{k:{'plans':0,'findings':0,'rejected':0} for k in TOPICS})
    repeated={r['topic'] for r in lessons if r['rejected']>=3}
    choices=[k for k in TOPICS if k not in repeated] or list(TOPICS)
    topic=min(choices,key=lambda k:(counts[k]['plans'],counts[k]['findings'],list(TOPICS).index(k)))
    sources=store.meta('research_sources') or []
    awaiting=[p for p in plans if p['state']=='running' and not p['finding_ids'] and
              any(v.get('state')=='completed' and v.get('ok') is True for v in p['variants'].values())]
    open_plans=[p for p in plans if p['state']=='planned']
    stagnation=(store.meta('agent') or {}).get('stagnation_cycles',0)
    action='source_search_then_retrieve'
    target=None
    if awaiting:action='interpret_and_record_result';target=awaiting[0]['id']
    elif open_plans and stagnation<3:action='execute_preregistered_variant';target=open_plans[0]['id']
    elif program.get('cycles',0)%4==0 and store.meta('improvements'):
        action='review_measured_bottlenecks'
    result = {'schema':program.get('schema'),'started_at':program.get('started_at'),
            'plan_required':program.get('plan_required',False),'cycles':program.get('cycles',0),'topics':counts,
            'recommendation':{'topic':topic,'question_area':TOPICS[topic],'action':action,'plan_id':target,
                              'reason':'Investigate a less explored explanation; repeated rejected families need new evidence.',
                              'kind':'recommendation_not_permission'},
            'plans':[{k:v for k,v in p.items() if k not in ('identity','sources','variants')} |
                     {'variants':{key:{k:v for k,v in variant.items() if k not in ('evidence','provenance')}
                                  for key,variant in p['variants'].items()}} for p in plans[-12:]],
            'lessons':[{k:v for k,v in r.items() if k!='recent_ids'} for r in lessons[-12:]],
            'insights':(store.meta('research_insights') or [])[-5:],
            'sources':[_summary_source(r) for r in sources[-10:]],
            'workflow':__import__('xauusd.research_workflow',fromlist=['workflow_status']).workflow_status(store),
            'counts':{'open_plans':sum(p['state'] not in TERMINAL for p in plans),
                      'completed_plans':sum(p['state']=='completed' for p in plans),
                      'blocked_plans':sum(p['state']=='blocked' for p in plans),
                      'retained_sources':len(sources),'retained_insights':len(store.meta('research_insights') or [])}}

    if compact:
        result['workflow']['blockers']=result['workflow']['blockers'][-5:]
        result['plans']=[{k:(v[:350] if isinstance(v,str) else v) for k,v in p.items()
                          if k in ('id','topic','family','question','hypothesis','state','dataset_version','max_variants','finding_ids')}
                         | {'variants':{k:{field:value for field,value in v.items() if field in ('call_id','state','ok','remote_job_id')}
                                        for k,v in p['variants'].items()}}
                         for p in plans[-4:]]
        result['lessons']=[{k:(v[:400] if isinstance(v,str) else v) for k,v in r.items() if k!='recent_ids'} for r in lessons[-6:]]
        result['insights']=[{k:(v[:400] if isinstance(v,str) else v) for k,v in r.items() if k!='sources'}
                            for r in (store.meta('research_insights') or [])[-3:]]
        result['summary_only']=True
        result['retrieval']='research_program with kind (plan/source/insight/measurement), id, offset, limit retrieves complete retained records.'
    return result


def read(store,args):
    if not args:return {'ok':True,**context(store,compact=True)}
    if set(args)-{'kind','id','offset','limit'} or args.get('kind') not in ('plan','source','insight','measurement') or not text(args.get('id'),100):
        return {'ok':False,'error_code':'invalid_program_read'}
    offset=args.get('offset',0);limit=args.get('limit',2000)
    if type(offset) is not int or offset<0 or type(limit) is not int or not 1<=limit<=4000:
        return {'ok':False,'error_code':'invalid_program_range'}
    key={'plan':'research_plans','source':'research_sources','insight':'research_insights','measurement':'improvement_measurements'}[args['kind']]
    row=next((r for r in store.meta(key) or [] if r['id']==args['id']),None)
    if row is None:return {'ok':False,'error_code':'program_record_not_retained'}
    content=json.dumps(row,sort_keys=True,allow_nan=False);end=min(offset+limit,len(content))
    return {'ok':True,'content':content[offset:end],'offset':offset,'total_chars':len(content),
            'next_offset':end if end<len(content) else None,'sha256':hashlib.sha256(content.encode()).hexdigest()}
