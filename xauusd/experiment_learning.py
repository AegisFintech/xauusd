"""Bounded prospective attribution and review schedule; never execution authority."""
from datetime import datetime, timedelta, timezone
import hashlib
import json

REVIEW_DAYS = 7
MIN_CLOSES = 30


def initialize(row, state, now):
    if 'learning' not in row:
        row['learning']={'started_at':now.isoformat(),'next_review_at':(now+timedelta(days=REVIEW_DAYS)).isoformat(),
            'baseline_equity':state['cash']+state['position']*state['mark_price'],
            'baseline_realized':sum(f['realized_pnl'] for f in state['ledger']),
            'accepted_fills':0,'closed_fills':0,'wins':0,'losses':0,'net_realized':0.,
            'matched_gross_mid':0.,'matched_net':0.,'matched_cost':0.,'matched_closes':0,
            'unmatched_closes':0,'spread_cost':0.,'slippage_commission_cost':0.,
            'best_two_closes':[],'positive_net_sum':0.,'last_decision_id':None,'entry':None,'reviews':[]}
    return row['learning']


def observe_fill(row, before, decision, quote, now):
    """Observe an accepted, non-replayed fill; do not mutate the account."""
    a=initialize(row,before,now)
    if a['last_decision_id']==decision.decision_id:return
    a['last_decision_id']=decision.decision_id
    mid=(quote['bid']+quote['ask'])/2
    side=1 if decision.side=='BUY' else -1
    cost_per_unit=side*(decision.price-mid)
    spread=(quote['ask']-quote['bid'])/2
    a['accepted_fills']+=1
    a['spread_cost']+=spread*decision.quantity
    a['slippage_commission_cost']+=(cost_per_unit-spread)*decision.quantity
    position=before['position'];entry=a['entry']
    if position and position*side<0:
        closed=min(abs(position),decision.quantity)
        net=closed*(decision.price-before['average_entry_price'])*(1 if position>0 else -1)
        a['closed_fills']+=1;a['net_realized']+=net
        a['wins']+=net>0;a['losses']+=net<0
        if net>0:
            a['positive_net_sum']+=net
            a['best_two_closes']=sorted(a['best_two_closes']+[net],reverse=True)[:2]
        if entry is not None:
            gross=closed*(mid-entry['mid'])*entry['side']
            costs=closed*(entry['cost_per_unit']+cost_per_unit)
            a['matched_closes']+=1;a['matched_gross_mid']+=gross
            a['matched_net']+=net;a['matched_cost']+=costs
        else:a['unmatched_closes']+=1
    current=position+side*decision.quantity
    if abs(current)<1e-9:a['entry']=None
    elif position==0 or position*current<0:
        a['entry']={'mid':mid,'side':side,'cost_per_unit':cost_per_unit}
    elif position*side>0 and entry is not None:
        total=abs(position)+decision.quantity
        a['entry']={'mid':(abs(position)*entry['mid']+decision.quantity*mid)/total,
                    'side':side,'cost_per_unit':(abs(position)*entry['cost_per_unit']+decision.quantity*cost_per_unit)/total}


def assessment(row, now=None):
    now=now or datetime.now(timezone.utc);a=row.get('learning')
    if not a:return {'coverage':'not_observed','review_due':False,'next':'Prospective attribution starts with the next valid market observation; historical costs are not reconstructed.'}
    enough=a['closed_fills']>=MIN_CLOSES
    due=now>=datetime.fromisoformat(a['next_review_at'])
    diagnosis=('insufficient_sample' if not enough else
               'execution_costs' if a['matched_closes']>=MIN_CLOSES and a['matched_gross_mid']>0 and a['matched_net']<=0 else
               'signal_or_exit' if a['net_realized']<=0 else 'positive_unvalidated_sample')
    return {'coverage':'prospective_only','started_at':a['started_at'],'next_review_at':a['next_review_at'],
            'review_due':due,'minimum_closed_fills':MIN_CLOSES,'sample_sufficient':enough,
            'closed_fills':a['closed_fills'],'accepted_fills':a['accepted_fills'],
            'win_rate':a['wins']/a['closed_fills'] if a['closed_fills'] else None,
            'net_realized':a['net_realized'],'matched_gross_mid':a['matched_gross_mid'],
            'matched_net':a['matched_net'],'matched_cost':a['matched_cost'],
            'spread_cost':a['spread_cost'],'slippage_commission_cost':a['slippage_commission_cost'],
            'unmatched_closes':a['unmatched_closes'],'diagnosis':diagnosis,
            'net_without_best_two_closes':a['net_realized']-sum(a['best_two_closes']),
            'top_two_positive_concentration':sum(a['best_two_closes'])/a['positive_net_sum'] if a['positive_net_sum'] else None,
            'source_question':'Check documented spreads/commission and market-session liquidity before changing execution assumptions.' if diagnosis=='execution_costs' else
                              'Investigate event/session conditioning using dated primary sources; verify point-in-time availability before testing.' if diagnosis=='signal_or_exit' else
                              'Collect independent observations; source research must answer a concrete missing-data question.',
            'next':'Extend observation; no conclusion from insufficient closes.' if not enough else
                   'Test execution sensitivity on identical data.' if diagnosis=='execution_costs' else
                   'Preregister an entry/exit hypothesis and compare against this baseline.' if diagnosis=='signal_or_exit' else
                   'Continue independent prospective evaluation; no automatic qualification.',
            'causal_attribution':False,'qualification':False,
            'evidence_digest':hashlib.sha256(json.dumps(a,sort_keys=True,allow_nan=False).encode()).hexdigest()}


def record_review(store,args,now=None):
    if set(args)!={'id','evidence_digest','decision','reason'} or args.get('decision') not in ('continue','retire') or not isinstance(args.get('reason'),str) or not 1<=len(args['reason'])<=1000:
        return {'ok':False,'error_code':'invalid_experiment_review'}
    now=now or datetime.now(timezone.utc)
    with store.execution_lock:
        rows=store.meta('experiments') or [];row=next((r for r in rows if r['id']==args['id']),None)
        if row is None:return {'ok':False,'error_code':'experiment_not_found'}
        observed=assessment(row,now)
        if observed.get('evidence_digest')!=args['evidence_digest']:
            return {'ok':False,'error_code':'stale_experiment_review'}
        a=row['learning'];a['reviews']=(a['reviews']+[{**args,'recorded_at':now.isoformat(),
            'metrics':{k:observed[k] for k in ('closed_fills','net_realized','diagnosis','sample_sufficient')}}])[-12:]
        a['next_review_at']=(now+timedelta(days=REVIEW_DAYS)).isoformat()
        store.meta('experiments',rows)
        store.event('experiment_reviewed','Recorded an evidence-linked experimental review.',{'id':row['id'],'decision':args['decision']})
    return {'ok':True,'id':row['id'],'decision':args['decision'],
            'next':'Use experiment_retire through normal gates.' if args['decision']=='retire' else 'Continue observation; not strategy qualification.'}
