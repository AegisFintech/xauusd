"""UTC goal/display boundaries, independent of account and risk state."""
from datetime import datetime,timezone


def utc_day(now=None):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None: raise ValueError('timezone_required')
    day=now.astimezone(timezone.utc).date().isoformat()
    return {'day':day,'timezone':'UTC','started_at':day+'T00:00:00+00:00',
            'aspirational_daily_return_pct':100,'preferred_backtest_worker':'tc02'}


def roll_daily_goal(store,now=None):
    daily=utc_day(now)
    with store.execution_lock:
        previous=store.meta('daily_goal')
        if previous and previous.get('day')==daily['day']: return previous
        agent=store.meta('agent') or {}
        if previous:
            history=store.meta('daily_goal_history') or []
            store.meta('daily_goal_history',(history+[{**previous,'goal':agent.get('goal',{})}])[-7:])
        if agent:
            agent['goal']={**agent.get('goal',{}),'aspirational_daily_return_pct':100,
                           'achieved':False,'day':daily['day'],'timezone':'UTC','mode':'paper'}
            agent['daily_started_at']=daily['started_at']
            store.meta('agent',agent)
        store.meta('daily_goal',daily)
        store.event('goal','Fresh UTC day: daily goal progress and visible history start anew; research learning continues.',daily)
    return daily
