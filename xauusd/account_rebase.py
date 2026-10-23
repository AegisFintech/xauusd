"""Explicit operator-only, flat paper account rebase; no research reset."""
import math
from datetime import datetime,timezone
from .local_state import SQLitePaperTradingStore
from .paper_trading import _default_state, validated_paper_state
from .experiment_registry import canonical_json


def rebase(paper, cash):
    if not isinstance(paper.store,SQLitePaperTradingStore):raise ValueError('local_paper_required')
    if not isinstance(cash,(int,float)) or isinstance(cash,bool) or not math.isfinite(cash) or cash<=0:raise ValueError('invalid_cash')
    db=paper.store.connect() if hasattr(paper.store,'connect') else None
    if db is None:
        from .local_state import _connect
        db=_connect(paper.store.db_path)
    try:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute("SELECT state_json FROM paper_trading_state WHERE state_key='primary'").fetchone()
        import json
        prior=validated_paper_state(json.loads(row['state_json']),paper.store.initial_cash)
        if prior['position']!=0:raise ValueError('flat_account_required')
        state=_default_state(float(cash))
        state.update(stopped=prior['stopped'],kill_switch_reason=prior['kill_switch_reason'])
        db.execute("UPDATE paper_trading_state SET state_json=?,updated_at=? WHERE state_key='primary'",(canonical_json(state),datetime.now(timezone.utc).isoformat()))
        db.execute('DELETE FROM paper_trading_decisions')
        db.execute("DELETE FROM bits_state WHERE state_key IN ('lab:equity','lab:execution_intent','lab:position_owner')")
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK');raise
    finally:db.close()
    return {'equity':float(cash),'stopped':state['stopped'],'research_preserved':True}
