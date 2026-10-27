"""Independent exploratory paper accounts; never a promotion or broker path."""
from uuid import uuid4
import pandas as pd
from .lab_store import serialized, timestamp
from .lab_execution import ShadowStore, target_decision, quote_valid
from .lab_strategy import signals
from .paper_trading import PaperTrading, _default_state, market_is_open, market_data_age_seconds, observation_is_future

@serialized
def start(store, arguments):
    try:
        if set(arguments)!={'name','expression'} or not 0<len(arguments['name'])<=80:
            raise ValueError()
        expression=arguments['expression']
        frame=pd.DataFrame({key:[1.,2.,3.] for key in ('open','high','low','close','volume')})
        signals(expression,frame)
    except Exception:
        return {'ok':False,'error_code':'invalid_experiment'}
    rows=store.meta('experiments') or []
    if len(rows)>=4:
        return {'ok':False,'error_code':'experiment_capacity_four'}
    account=ShadowStore();account.payload['state']=_default_state(1000)
    account.payload['state'].update(stopped=False,kill_switch_reason='experimental_simulation')
    row={'id':'experiment_'+uuid4().hex[:12],**arguments,'created_at':timestamp(),
         'account':account.payload,'classification':'unvalidated_experimental_paper','last_bar':None}
    store.meta('experiments',rows+[row])
    store.event('experiment','Started independent $1,000 experimental paper account.',{'id':row['id'],'name':row['name']})
    return {'ok':True,'id':row['id'],'classification':row['classification']}

@serialized
def tick(store, config, bars, now, quote, quantity=.1):
    if not quote_valid(quote,now) or not market_is_open(now) or bars.empty:
        return
    closed=bars.loc[bars.index<=pd.Timestamp(now)-pd.Timedelta(minutes=1)]
    if closed.empty:return
    bar=closed.index[-1].to_pydatetime()
    if observation_is_future(bar,now) or market_data_age_seconds(bar,now)>config.max_market_data_age_seconds:return
    rows=store.meta('experiments') or []
    for row in list(rows):
        account_store=ShadowStore(row['account']);account=PaperTrading(account_store,config)
        mark=(quote['bid']+quote['ask'])/2
        account.monitor(mark,bar,now)
        if row['last_bar']!=bar.isoformat():
            decision=target_decision({**row, 'expression': '0'} if row.get('state')=='retiring' else row,closed,account.state(),now,quote,quantity)
            if decision:
                result=account.evaluate(decision,now)
                store.event('experimental_trade','Experimental paper proposal evaluated.',{'id':row['id'],'accepted':result.get('accepted',False),'side':decision.side,'reasons':[result.get('reason','unknown')]})
                row['last_verdict']={'accepted':result.get('accepted',False),'reasons':[result.get('reason','unknown')],'recorded_at':now.isoformat()}
            row['last_bar']=bar.isoformat()
        row['account']=account_store.payload
        row['summary']=account.summary()
        if row.get('state')=='retiring' and account.state()['position']==0:
            _archive(store,row)
            rows.remove(row)
    store.meta('experiments',rows)


def _archive(store, row):
    row.update(state='retired', retired_at=timestamp())
    store.meta('experiment_archive', ((store.meta('experiment_archive') or []) + [row])[-40:])
    store.event('experiment_retired', 'Experimental account retired with evidence retained.',
                {'id': row['id'], 'reason': row.get('retirement_reason'), 'summary': row.get('summary')})


@serialized
def retire(store, arguments):
    if set(arguments) != {'id', 'reason'} or not isinstance(arguments['reason'], str) or not 1 <= len(arguments['reason']) <= 500:
        return {'ok': False, 'error_code': 'invalid_retirement'}
    rows = store.meta('experiments') or []
    row = next((r for r in rows if r['id'] == arguments['id']), None)
    if row is None:
        return {'ok': False, 'error_code': 'experiment_not_found'}
    row.update(state='retiring', retirement_reason=arguments['reason'])
    account = ShadowStore(row['account'])
    if account.state()['position'] == 0:
        _archive(store, row)
        rows.remove(row)
    store.meta('experiments', rows)
    return {'ok': True, 'id': row['id'], 'state': row['state']}


def review(store):
    rows = store.meta('experiments') or []
    archive = store.meta('experiment_archive') or []
    return {'ok': True, 'active': len(rows), 'capacity': 4, 'retired': len(archive),
            'accounts': [{'id': r['id'], 'name': r['name'], 'state': r.get('state', 'running'),
                          'summary': r.get('summary'), 'last_verdict': r.get('last_verdict')} for r in rows],
            'archived': [{'id': r['id'], 'name': r['name'], 'summary': r.get('summary'),
                          'reason': r.get('retirement_reason')} for r in archive]}
