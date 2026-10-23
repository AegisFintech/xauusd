"""Independent release restart/health worker, outside the agent's process group."""
from pathlib import Path
import os
import subprocess
import time


def release_healthy(health, previous_run):
    heartbeat=(health.get('agent') or {}).get('heartbeat') or {}
    monitor=health.get('monitor') or {}
    return (health.get('status')=='ok' and not health.get('alerts') and
            heartbeat.get('planner')=='codex' and heartbeat.get('state')=='running' and
            heartbeat.get('run_id') and heartbeat.get('run_id')!=previous_run and
            (health.get('agent') or {}).get('heartbeat_age_seconds',999)<30 and
            monitor.get('status')=='ok' and monitor.get('thread_alive') is True)


def schedule_verification(store,manager):
    pending=store.meta('engineering_pending')
    if not pending or pending.get('state')!='pending_health': return {'ok':True,'state':'none'}
    try:
        result=subprocess.run(['systemctl','start','--no-block','xauusd-release-verify.service'],
                              stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
        if result.returncode: raise ValueError('worker_unavailable')
        return {'ok':True,'state':'scheduled'}
    except (OSError,subprocess.TimeoutExpired,ValueError):
        rollback=manager.verify_pending(False)
        store.event('deployment','Release worker unavailable; installation rolled back.',{'result':rollback})
        return {'ok':False,'error_code':'release_worker_unavailable'}


def run(recover_only=False):
    from dotenv import load_dotenv
    load_dotenv('.env')
    from .agent_loop import agent_transcript_store_from_env
    from .lab_store import LabStore
    from .agent_engineering import EngineeringManager
    from .agent_status import read_status
    from .atomic import file_lock
    import requests
    store=LabStore(agent_transcript_store_from_env())
    manager=EngineeringManager(Path.cwd(),store)
    if recover_only:
        result=manager.recover_pending()
        if not result.get('ok'):
            store.event('deployment','Interrupted engineering release needs attention.',{'result':result})
            raise SystemExit(1)
        return
    with file_lock('data/lab/releases/.verify',timeout=5):
        pending=store.meta('engineering_pending')
        if not pending: return
        if pending.get('state')=='installing':
            manager.recover_pending(); return
        release_id=pending['id'];previous_run=(read_status() or {}).get('run_id')
        def restart():
            return subprocess.run(['systemctl','restart','xauusd-agent.service','xauusd-agent-view.service'],
                                  stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=60).returncode==0
        healthy=False
        try:
            if restart():
                deadline=time.monotonic()+120; consecutive=0
                while time.monotonic()<deadline:
                    time.sleep(5)
                    current=store.meta('engineering_pending')
                    if not current or current['id']!=release_id: return
                    try:
                        health=requests.get('http://127.0.0.1:'+os.getenv('AGENT_VIEW_PORT','8100')+'/api/health',timeout=5).json()
                        consecutive=consecutive+1 if release_healthy(health,previous_run) else 0
                    except (requests.RequestException,ValueError): consecutive=0
                    if consecutive>=3: healthy=True;break
        except (OSError,subprocess.TimeoutExpired): pass
        result=manager.verify_pending(healthy)
        store.event('deployment','Release health verification completed.',{'healthy':healthy,'result':result})
        if not healthy and result.get('ok'): restart()


if __name__=='__main__':
    import sys
    run(recover_only='--recover-only' in sys.argv)
