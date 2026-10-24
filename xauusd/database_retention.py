"""Seven-day operational log retention; learning and execution controls survive."""
from datetime import datetime,timedelta,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess

from .lab_store import LabStore

DAYS=7
BATCH=500
TERMINAL={'succeeded','failed','cancelled','timed_out'}
EPHEMERAL={'lab:events','lab:jobs','lab:agent_calls','lab:equity','lab:research_inference','lab:db_retention','lab:storage','lab:db_retention_job_cursor'}


def moment(value):
    try:
        parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo is not None else None
    except (ValueError,TypeError,AttributeError):return None


def _old(row,cutoff,fields):
    dates=[moment(row.get(k)) for k in fields]
    dates=[d for d in dates if d is not None]
    return bool(dates) and max(dates)<cutoff


def _references(tx):
    references=set()
    def collect(value):
        if isinstance(value,str):
            if len(value)<=512:references.add(value)
            references.update(re.findall(r'\b[a-f0-9]{32}\b',value))
            references.update(re.findall(r'(?:transcript|step)[:/#](\d+)',value))
        elif isinstance(value,dict):
            for key,child in value.items():
                if key in ('transcript_id','step_id') and type(child) is int:references.add(str(child))
                collect(child)
        elif isinstance(value,list):
            for child in value:collect(child)
    for row in tx.db.execute('SELECT state_key,value_json FROM bits_state').fetchall():
        if row['state_key'] in EPHEMERAL:continue
        # Unknown/malformed learning is never a justification to expire evidence.
        collect(json.loads(row['value_json']))
    return references


def prune_monitor_records(store,now):
    cutoff=(now-timedelta(days=DAYS)).isoformat();removed=0;cursor=''
    for _ in range(20):
        with store.state.transaction() as tx:
            rows=tx.db.execute("SELECT decision_id,result_json FROM paper_trading_decisions WHERE decision_id LIKE 'monitor:%' AND created_at < ? AND decision_id > ? ORDER BY decision_id LIMIT ?",(cutoff,cursor,BATCH)).fetchall()
            for row in rows:
                cursor=row['decision_id']
                try:result=json.loads(row['result_json'])
                except (ValueError,TypeError):continue
                # Trade results have accepted/decision_id, even if named monitor:*.
                if not isinstance(result,dict) or any(k in result for k in ('accepted','decision_id','reason')):continue
                tx.db.execute('DELETE FROM paper_trading_decisions WHERE decision_id=?',(cursor,));removed+=1
        if len(rows)<BATCH:break
    return removed


def _job_outputs(store,now,cutoff,refs):
    cursor=store.meta('db_retention_job_cursor') or '';expired=0;dated=0;bytes_removed=0
    for _ in range(20):
        with store.state.transaction() as tx:
            refs=_references(tx)
            rows=tx.db.execute('SELECT job_id,status FROM bits_jobs WHERE job_id > ? ORDER BY job_id LIMIT ?',(cursor,50)).fetchall()
            for record in rows:
                cursor=record['job_id']
                if record['status'] not in TERMINAL or record['job_id'] in refs:continue
                raw=tx.db.execute('SELECT result_json FROM bits_jobs WHERE job_id=?',(cursor,)).fetchone()
                value=json.loads(raw['result_json'])
                if not isinstance(value,dict) or value.get('output_expired'):continue
                if not any(moment(value.get(k)) for k in ('finished_at','created_at','retention_observed_at')):
                    value['retention_observed_at']=now.isoformat();dated+=1
                elif _old(value,cutoff,('finished_at','created_at','retention_observed_at')):
                    text=json.dumps({k:value.get(k,'') for k in ('stdout','stderr')},sort_keys=True)
                    captured_bytes=sum(len(value.get(k,'').encode()) for k in ('stdout','stderr'))
                    value.update(stdout='',stderr='',output_expired=True,truncated=True,
                                 output_sha256=hashlib.sha256(text.encode()).hexdigest(),
                                 output_expired_at=now.isoformat())
                    expired+=1;bytes_removed+=captured_bytes
                else:continue
                # Identity, request, outcome and exit code are unchanged.
                tx.db.execute('UPDATE bits_jobs SET result_json=? WHERE job_id=?',(json.dumps(value,allow_nan=False),cursor))
        store.meta('db_retention_job_cursor',cursor if len(rows)==50 else '')
        if len(rows)<50:break
    return {'expired_job_outputs':expired,'undated_jobs_first_observed':dated,'output_bytes_removed':bytes_removed}


def _transcripts(store,cutoff,refs):
    cursor=0;removed=0
    for _ in range(20):
        with store.state.transaction() as tx:
            refs=_references(tx)
            rows=tx.db.execute('SELECT id FROM agent_transcript WHERE occurred_at < ? AND id > ? ORDER BY id LIMIT ?',
                               (cutoff.isoformat(),cursor,BATCH)).fetchall()
            for row in rows:
                cursor=row['id']
                if str(cursor) in refs:continue
                tx.db.execute('DELETE FROM agent_transcript WHERE id=?',(cursor,));removed+=1
        if len(rows)<BATCH:break
    return removed


def rotate(transcript,now=None):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None:raise ValueError('timezone_required')
    now=now.astimezone(timezone.utc);cutoff=now-timedelta(days=DAYS)
    store=LabStore(transcript)
    with store.state.transaction() as tx:
        tx.lock('lab:db_retention')
        refs=_references(tx)
        removed={}
        for key,fields,terminal in [('events',('time',),None),('jobs',('finished_at','started_at'),{'completed','failed','interrupted'}),
                                   ('agent_calls',('finished_at','started_at'),{'completed','refused'}),('equity',('time',),None)]:
            value=tx.get('lab:'+key)
            rows=value.get('events',[]) if key=='events' and isinstance(value,dict) else value
            if rows is None:continue
            if not isinstance(rows,list):raise ValueError('invalid_log_ledger')
            kept=[]
            for row in rows:
                if not isinstance(row,dict):raise ValueError('invalid_log_row')
                protected=(row.get('id') in refs or (terminal is not None and row.get('state') not in terminal))
                if protected or not _old(row,cutoff,fields):kept.append(row)
            removed[key]=len(rows)-len(kept)
            if key=='events':tx.put('lab:'+key,{**value,'events':kept})
            else:tx.put('lab:'+key,kept)
        inference=tx.get('lab:research_inference')
        if isinstance(inference,dict) and isinstance(inference.get('samples'),list):
            samples=inference['samples'];inference['samples']=[r for r in samples if not _old(r,cutoff,('recorded_at',))]
            removed['inference_samples']=len(samples)-len(inference['samples'])
            tx.put('lab:research_inference',inference)
    # Batch table operations use short transactions, independent of trade-loop cadence.
    removed['monitor_marks']=prune_monitor_records(store,now)
    jobs=_job_outputs(store,now,cutoff,refs)
    removed['transcript_steps']=_transcripts(store,cutoff,refs)
    with store.state.transaction() as tx:
        tx.lock('lab:db_retention')
        old_runs=tx.db.execute('SELECT run_id FROM agent_runs WHERE status != ? AND finished_at < ? AND NOT EXISTS (SELECT 1 FROM agent_transcript t WHERE t.run_id=agent_runs.run_id)',('running',cutoff.isoformat())).fetchall()
        removed['run_summaries']=0
        for row in old_runs:
            if row['run_id'] not in refs:
                tx.db.execute('DELETE FROM agent_runs WHERE run_id=?',(row['run_id'],));removed['run_summaries']+=1
        totals=tx.get('lab:db_retention_totals',{})
        for key,value in {**removed,**jobs}.items():totals[key]=totals.get(key,0)+value
        tx.put('lab:db_retention_totals',totals)
        report={'state':'ok','recorded_at':now.isoformat(),'retention_days':DAYS,'removed':removed,**jobs,
                'cumulative':totals,'policy':'Rolling UTC logs; preserve learning, references, active/unknown work, account and trade identities.'}
        tx.put('lab:db_retention',report)
    if isinstance(getattr(transcript,'db_path',None),str):
        with transcript.connect() as db:
            db.execute('CREATE INDEX IF NOT EXISTS idx_paper_decisions_created ON paper_trading_decisions(created_at)')
            db.execute('CREATE INDEX IF NOT EXISTS idx_transcript_occurred ON agent_transcript(occurred_at)')
            db.execute('PRAGMA optimize').fetchall()
            db.execute('PRAGMA wal_checkpoint(PASSIVE)').fetchall()
            if db.execute('PRAGMA auto_vacuum').fetchone()[0]==2:
                db.execute('PRAGMA incremental_vacuum(256)').fetchall()
        db.close()
    return report


def compact_local(transcript):
    """Operator maintenance only; scheduled service never runs a full VACUUM."""
    if not isinstance(getattr(transcript,'db_path',None),str):raise ValueError('local_backend_required')
    for unit in ('xauusd-agent.service','xauusd-engine.service','xauusd-agent-view.service'):
        state=subprocess.run(['systemctl','is-active',unit],capture_output=True,text=True,timeout=10)
        if state.stdout.strip()!='inactive':
            raise ValueError('stop_database_services_before_compaction')
    db=transcript.connect()
    try:
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('integrity_check_failed')
        before=Path(transcript.db_path).stat().st_size
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchall()
        db.execute('PRAGMA auto_vacuum=INCREMENTAL')
        db.execute('VACUUM')
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchall()
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('integrity_check_failed')
        return {'state':'ok','before_bytes':before,'after_bytes':Path(transcript.db_path).stat().st_size,'auto_vacuum':'incremental'}
    finally:db.close()


def read_status():
    path=Path(os.getenv('DB_RETENTION_STATUS_PATH','reports/db_retention_status.json'))
    try:
        value=json.loads(path.read_text())
        if not isinstance(value,dict):raise ValueError('invalid_status')
        return value
    except FileNotFoundError:return {'state':'not_run'}
    except (OSError,ValueError):return {'state':'failed','error_code':'maintenance_status_unreadable'}


def main():
    import argparse
    from dotenv import load_dotenv
    from .agent_loop import agent_transcript_store_from_env
    from .atomic import atomic_write_json,file_lock
    load_dotenv('.env')
    parser=argparse.ArgumentParser();parser.add_argument('--compact',action='store_true');args=parser.parse_args()
    path=Path(os.getenv('DB_RETENTION_STATUS_PATH','reports/db_retention_status.json'))
    try:
        with file_lock(path):
            transcript=agent_transcript_store_from_env()
            report=rotate(transcript)
            if args.compact:
                report['compaction']=compact_local(transcript)
                LabStore(transcript).meta('db_optimization',{'recorded_at':datetime.now(timezone.utc).isoformat(),**report['compaction']})
            atomic_write_json(path,report)
        print(json.dumps(report,allow_nan=False))
    except Exception:
        atomic_write_json(path,{'state':'failed','recorded_at':datetime.now(timezone.utc).isoformat(),'error_code':'database_retention_failed'})
        raise SystemExit(1) from None


if __name__=='__main__':main()
