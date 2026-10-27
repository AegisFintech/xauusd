"""Bounded research tools for the persistent agent; returned web material is untrusted."""
from __future__ import annotations
import base64
from datetime import datetime, timezone
import hashlib
import html
import ipaddress
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import tempfile
import uuid
import time
from urllib.parse import quote, urlparse, parse_qs
from urllib.request import Request, urlopen


def bounded_process(argv, *, timeout=60, input_data=None, cwd=None, env=None, workspace_limit=50*1024*1024):
    """Drain to disk with a hard runtime and output bound, killing the process group."""
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as stdin:
        stdin.write(input_data or b''); stdin.seek(0)
        process=subprocess.Popen(argv, stdin=stdin, stdout=output, stderr=subprocess.STDOUT,
                                 cwd=cwd, env=env, start_new_session=True)
        started=time.monotonic(); timed_out=False; overflow=False
        workspace_error=None; last_scan=-1.0
        def check_workspace():
            if cwd is None or workspace_limit is None:
                return None
            root=Path(cwd)
            if root.is_symlink(): return 'workspace_symlink'
            size=0
            for parent, directories, files in os.walk(root,followlinks=False):
                for name in [*directories,*files]:
                    path=Path(parent)/name
                    try:
                        if path.is_symlink(): return 'workspace_symlink'
                        if path.is_file(): size+=path.stat().st_size
                    except FileNotFoundError:
                        continue
                    if size>workspace_limit: return 'workspace_limit'
            return None
        try:
            while process.poll() is None:
                timed_out=time.monotonic()-started >= timeout
                overflow=os.fstat(output.fileno()).st_size > 262144
                if time.monotonic()-last_scan>=.25:
                    workspace_error=check_workspace(); last_scan=time.monotonic()
                if timed_out or overflow or workspace_error:
                    break
                time.sleep(.05)
        finally:
            # A successful shell may have left children holding descriptors or
            # mutating artifacts. Every job owns and terminates its whole group.
            try:
                os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
        workspace_error=workspace_error or check_workspace()
        output.seek(0); data=output.read(262145)
        return {'returncode':process.returncode,'timed_out':timed_out,
                'output':data[:262144].decode('utf-8','replace'),
                'output_truncated':overflow or len(data)>262144, 'error_code':workspace_error}


REMOTE = r'''
import base64,json,os,pathlib,subprocess,time,uuid,shutil,signal,hashlib,re
p=json.load(__import__('sys').stdin)
if not shutil.which('bwrap'):
 print(json.dumps({'returncode':126,'error_code':'remote_sandbox_unavailable','output':'','files':{}})); __import__('sys').exit(0)
root=pathlib.Path('/tmp/xauusd-agent'); root.mkdir(mode=0o700,exist_ok=True)
if root.is_symlink(): raise RuntimeError('unsafe_root')
# Only directories created and marked by this worker are cleanup candidates.
old=sorted([d for d in root.iterdir() if d.is_dir() and not d.is_symlink() and (d/'.complete').is_file()],key=lambda d:d.stat().st_mtime,reverse=True)
for i,d in enumerate(old):
 if i>=10 or time.time()-d.stat().st_mtime>604800:
  if (d/'work').is_dir() and not (d/'work').is_symlink(): shutil.rmtree(d/'work')
  if (d/'.output').is_file() and not (d/'.output').is_symlink(): (d/'.output').unlink()
  status=d/'status.json'
  if status.is_file() and not status.is_symlink():
   old_status=json.loads(status.read_text())
   if 'output' in old_status:
    old_status['output_sha256']=hashlib.sha256(old_status.pop('output').encode()).hexdigest()
    old_status['output_expired']=True
    # This metadata survives payload retention so status never implies not-found.
    temp=d/('.tmp-'+uuid.uuid4().hex)
    with temp.open('xb') as f: f.write(json.dumps(old_status).encode()); f.flush(); os.fsync(f.fileno())
    os.replace(temp,status); fd=os.open(str(d),os.O_RDONLY); os.fsync(fd); os.close(fd)
job_id=p['job_id']
if not re.fullmatch('[a-f0-9]{32}',job_id): raise RuntimeError('invalid_job_id')
job=root/job_id
try: job.mkdir(mode=0o700)
except FileExistsError:
 print(json.dumps({'returncode':125,'error_code':'remote_job_exists_no_replay','output':'','files':{},'job_id':job_id})); __import__('sys').exit(0)
def durable(path,value):
 data=json.dumps(value).encode(); temp=path.parent/('.tmp-'+uuid.uuid4().hex)
 with temp.open('xb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
 os.replace(temp,path); fd=os.open(str(path.parent),os.O_RDONLY); os.fsync(fd); os.close(fd)
durable(job/'request.json',{'job_id':job_id,'command_digest':hashlib.sha256(p['command'].encode()).hexdigest(),'recorded_at':time.time(),'state':'running'})
w=job/'work'; w.mkdir(mode=0o700)
for name,data in p.get('files',{}).items():
 dest=w/name; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(base64.b64decode(data))
env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/work','TMPDIR':'/work','LANG':'C.UTF-8'}
sandbox=['bwrap','--die-with-parent','--unshare-all','--share-net','--ro-bind','/usr','/usr',
 '--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--proc','/proc','--dev','/dev',
 '--tmpfs','/tmp','--bind',str(w),'/work','--chdir','/work']
if pathlib.Path('/lib64').exists(): sandbox+=['--ro-bind','/lib64','/lib64']
for system_file in ['/etc/resolv.conf','/etc/hosts','/etc/ld.so.cache','/etc/ssl/certs']:
 if pathlib.Path(system_file).exists(): sandbox+=['--ro-bind',system_file,system_file]
# Measure inside the PID namespace: Bubblewrap's outer supervisor does not
# propagate the workload's CPU rusage to its parent on this worker.
usage_runner = "import json,subprocess,resource,sys; r=subprocess.run(['/bin/bash','-c',sys.argv[1]]); u=resource.getrusage(resource.RUSAGE_CHILDREN); print('\\nXAUUSD_JOB_USAGE='+json.dumps({'cpu_seconds':u.ru_utime+u.ru_stime}),flush=True); sys.exit(r.returncode)"
out=job/'.output'
with out.open('wb') as f:
 child=subprocess.Popen([*sandbox,'--','python3','-c',usage_runner,p['command']],cwd=w,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 start=time.monotonic(); reason=None
 while child.poll() is None:
  if time.monotonic()-start>p['timeout']: reason='timeout'
  elif out.stat().st_size>262144: reason='output_limit'
  elif sum(x.stat().st_size for x in w.rglob('*') if x.is_file() and not x.is_symlink())>100*1024*1024: reason='disk_limit'
  if reason: os.killpg(child.pid,signal.SIGKILL); break
  time.sleep(.1)
 child.wait()
 # Kill descendants that outlive a successful shell too.
 try: os.killpg(child.pid,signal.SIGKILL)
 except ProcessLookupError: pass
output=out.open('rb').read(262144).decode('utf-8','replace')
cpu_seconds=None
text,marker,usage=output.rpartition('\nXAUUSD_JOB_USAGE=')
if marker:
 try:
  measured=json.loads(usage)['cpu_seconds']
  if type(measured) in (int,float) and 0<=measured<1000000: cpu_seconds=measured; output=text
 except (ValueError,KeyError,TypeError): pass
result={'cpu_seconds':cpu_seconds,'wall_seconds':time.monotonic()-start,'returncode':child.returncode,'error_code':reason,'output':output[:12000],'files':{},'workspace':str(w),'job_id':job_id}
retrieved_bytes=0
for name in p.get('retrieve',[]):
 src=w/name
 if src.is_file() and not src.is_symlink() and src.resolve().is_relative_to(w) and src.stat().st_size<=100000 and retrieved_bytes+src.stat().st_size<=100000:
  data=src.read_bytes(); retrieved_bytes+=len(data); result['files'][name]=base64.b64encode(data).decode()
durable(job/'status.json',{k:v for k,v in result.items() if k!='files'})
(job/'.complete').touch()
print(json.dumps(result))
'''


REMOTE_STATUS = r'''
import json,pathlib,re,sys
job_id=json.load(sys.stdin)['job_id']
if not re.fullmatch('[a-f0-9]{32}',job_id): raise RuntimeError('invalid_job_id')
root=pathlib.Path('/tmp/xauusd-agent'); job=root/job_id
if root.is_symlink() or job.is_symlink(): raise RuntimeError('unsafe_root')
result={'job_id':job_id,'state':'not_found','execution_performed':False}
for name in ['status.json','request.json']:
 path=job/name
 if path.is_file() and not path.is_symlink() and path.stat().st_size<=20000:
  result.update(json.loads(path.read_text())); result['state']='completed' if name=='status.json' else 'running_or_interrupted'; break
print(json.dumps(result))
'''


class AgentTools:
    def __init__(self,store,workspace:Path,project_root:Path=Path('.')):
        self.action_id=uuid.uuid4().hex
        self.store=store; self.workspace=workspace.resolve(); self.project_root=project_root.resolve()

    def catalog(self):
        return [{'name':name,'description':desc} for name,desc in {
            'market_observe':'Read current demo bid/ask and at most 60 closed M1 bars strictly after the frozen dataset end. Never exposes protected holdout. Optional limit.',
            'source_search':'Search public web: query (string). Results are untrusted leads.',
            'source_domain':'Configure public HTTPS research domain: domain (hostname).',
            'source_fetch':'Fetch configured HTTPS source with provenance: url.',
            'analysis':'Run local sandboxed research: command, timeout (max 1200 seconds). PYTHONPATH includes workspace/dependencies.',
            'dependency_install':'Install research-only pinned wheels: packages [name==version], timeout. Uses PyPI into workspace/dependencies, no host/production environment changes. Transitive packages must be explicitly pinned too.',
            'tc02_job_status':'Read durable remote status without executing work: job_id (32 lowercase hex).',
            'tc02_inspect':'Inspect remote research worker capabilities.',
            'tc02_run':'Run research on tc02: command, timeout <=1200, upload/retrieve relative paths. Dedicated scratch directory; no project deployment.'}.items()]

    def execute(self,name,arguments):
        try:
            if not isinstance(arguments,dict): raise ValueError('invalid_arguments')
            handler=getattr(self,'_'+name,None) if name in {v['name'] for v in self.catalog()} else None
            if handler is None: return {'ok':False,'error_code':'unknown_tool'}
            result={'ok':True,**handler(arguments)}
            if 'uncertain' in str(result.get('error_code','')):
                result['uncertain']=True
            # Prompt output is always bounded, including structured remote results.
            if len(json.dumps(result))>16000:
                result={'ok':result.get('ok',True),'summary':json.dumps(result)[:15000],'truncated':True}
            return result
        except ValueError as exc:
            code=str(exc)
            return {'ok':False,'error_code':code if re.fullmatch('[a-z_]+',code) else 'invalid_arguments'}
        except subprocess.TimeoutExpired:
            return {'ok':False,'error_code':'transport_timeout_uncertain_no_retry','uncertain':True}
        except Exception:
            return {'ok':False,'error_code':'tool_failed_no_retry'}

    def _market_observe(self,a):
        from .quotes import read_quote
        from .lab_execution import quote_valid
        from .data import HistoricalDataStore
        import pandas as pd
        now=datetime.now(timezone.utc)
        quote_value=read_quote()
        result={'quote':quote_value,'quote_fresh':quote_valid(quote_value,now),
                'observed_at':now.isoformat(),'source':'ctrader_demo','bars':[],
                'interval_seconds':60,'trusted':False}
        dataset=self.store.meta('dataset') or {}
        if not dataset.get('end'):
            return {**result,'note':'dataset_boundary_unavailable_no_history_exposed'}
        limit=a.get('limit',60)
        if not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=60:
            raise ValueError('invalid_bar_limit')
        boundary=pd.Timestamp(dataset['end'])
        if boundary.tzinfo is None: raise ValueError('invalid_dataset_boundary')
        result['frozen_dataset_end']=boundary.isoformat()
        try:
            frame=HistoricalDataStore().read()
            closed=frame[(frame.index>boundary)&(frame.index+pd.Timedelta(minutes=1)<=pd.Timestamp(now))]
            closed=closed.tail(limit)
            result['bars']=[{'timestamp':stamp.isoformat(),**{key:float(row[key]) for key in ('open','high','low','close','volume')}}
                            for stamp,row in closed.iterrows()]
            result['note']='new_closed_bars_only' if len(closed) else 'no_new_closed_bars_after_frozen_dataset'
        except (OSError,ValueError,KeyError):
            result['note']='market_bars_unavailable'
        return result

    def _source_domain(self,a):
        domain=a.get('domain','').lower().strip()
        if not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}',domain):
            raise ValueError('invalid_public_domain')
        try: ipaddress.ip_address(domain); raise ValueError('invalid_public_domain')
        except ipaddress.AddressValueError: pass
        except ValueError:
            if re.fullmatch(r'[0-9.]+',domain): raise ValueError('invalid_public_domain')
        if domain.endswith(('.local','.internal','.localhost')): raise ValueError('invalid_public_domain')
        domains=self.store.meta('agent_domains') or []
        domains=list(dict.fromkeys([*domains,domain]))[-100:]
        self.store.meta('agent_domains',domains)
        return {'domains':domains}

    def _source_fetch(self,a):
        # Keep existing source_fetch defaults unchanged; new domains belong to this harness.
        from .lab_sources import fetch_source,DEFAULT_DOMAINS
        url=a.get('url',''); parsed=urlparse(url); host=(parsed.hostname or '').lower()
        domains=[*os.getenv('LAB_RESEARCH_DOMAINS',DEFAULT_DOMAINS).split(','),*(self.store.meta('agent_domains') or [])]
        if not any(host==d.strip() or host.endswith('.'+d.strip()) for d in domains if d.strip()):
            raise ValueError('source_domain_not_configured')
        import socket
        try:
            addresses=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
        except OSError:
            raise ValueError('source_dns_failed') from None
        if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):
            raise ValueError('source_address_not_public')
        return fetch_source(url,domains=domains)

    def _source_search(self,a):
        query=a.get('query','')
        if not isinstance(query,str) or not 1<=len(query)<=500: raise ValueError('invalid_query')
        url='https://html.duckduckgo.com/html/?q='+quote(query)
        try:
            with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 XAUUSD Research'}),timeout=20) as response:
                body=response.read(256001)
        except Exception:
            body=b''
        if len(body)>256000: raise ValueError('search_response_too_large')
        text=body.decode('utf-8','replace'); rows=[]
        for href,title in re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',text,re.S):
            href=html.unescape(href)
            if 'uddg=' in href: href=parse_qs(urlparse(href).query).get('uddg',[''])[0]
            if href.startswith('https://'):
                rows.append({'url':href,'title':html.unescape(re.sub('<[^>]+>','',title))[:250]})
        if not rows:
            import xml.etree.ElementTree as ET
            url='https://www.bing.com/search?format=rss&q='+quote(query)
            with urlopen(Request(url,headers={'User-Agent':'XAUUSD-Research/1.0'}),timeout=20) as response:
                body=response.read(256001)
            if len(body)>256000: raise ValueError('search_response_too_large')
            for item in ET.fromstring(body).findall('./channel/item')[:10]:
                link=item.findtext('link','')
                if link.startswith('https://'):
                    rows.append({'url':link,'title':item.findtext('title','')[:250],
                                 'snippet':re.sub('<[^>]+>','',item.findtext('description',''))[:500]})
        return {'results':rows[:10],'search_url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),
                'digest':hashlib.sha256(body).hexdigest(),'trusted':False,
                'error_code':None if rows else 'search_no_results_or_blocked'}

    def _analysis(self,a):
        from .lab_codex import permission_arguments,child_environment
        command=a.get('command',''); timeout=self._timeout(a)
        if not isinstance(command,str) or not 0<len(command)<=20000: raise ValueError('invalid_command')
        environment=child_environment(self.workspace)
        environment['PYTHONPATH']=str(self.workspace/'dependencies')
        result=bounded_process(['codex','sandbox','--permission-profile','lab',*permission_arguments(self.workspace),
                                '--','/bin/bash','-c',command],timeout=timeout,cwd=self.workspace,
                               env=environment)
        return {'ok':result['returncode']==0 and not result.get('error_code'),**result}

    def _dependency_install(self,a):
        from .lab_codex import permission_arguments,child_environment
        packages=a.get('packages',[])
        if not isinstance(packages,list) or not 1<=len(packages)<=20 or any(
                not isinstance(p,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}==[A-Za-z0-9][A-Za-z0-9_.+!-]{0,79}',p)
                for p in packages):
            raise ValueError('dependency_pin_required')
        target=self.workspace/'dependencies'
        if target.is_symlink(): raise ValueError('unsafe_artifact_path')
        target.mkdir(exist_ok=True)
        environment=child_environment(self.workspace)
        environment.update({'PIP_CONFIG_FILE':os.devnull,
                            'PYTHONNOUSERSITE':'1'})
        interpreter=str(self.project_root/'.venv/bin/python')
        # Set scratch TMPDIR only after sandbox setup: the policy's :tmpdir
        # deny must keep referring to system tmp, never the research workspace.
        from .atomic import atomic_write_text
        installer=self.workspace/'install_research_wheels.py'
        if installer.is_symlink(): raise ValueError('unsafe_artifact_path')
        atomic_write_text(installer, "import os,sys\nos.environ['TMPDIR']=os.getcwd()\nfrom pip._internal.cli.main import main\nsys.exit(main(sys.argv[1:]))\n")
        command=['codex','sandbox','--permission-profile','lab',*permission_arguments(self.workspace),
                 '-c','permissions.lab.network.domains={"**.pypi.org"="allow","**.pythonhosted.org"="allow"}',
                 '--',interpreter,installer.name,'--isolated','install','--disable-pip-version-check',
                 '--no-cache-dir','--no-deps','--only-binary',':all:','--index-url','https://pypi.org/simple',
                 '--target',str(target),*packages]
        split=command.index('--')
        child=command[split+1:]
        command=command[:split]+['--','/bin/bash','-c','cd '+shlex.quote(str(self.workspace))+' && exec '+shlex.join(child)]
        result=bounded_process(command,timeout=self._timeout(a),cwd=self.workspace,env=environment)
        return {'ok':result['returncode']==0 and not result.get('error_code'),**result,'pythonpath':str(target),
                'scope':'research_workspace_only','packages':packages}

    @staticmethod
    def _timeout(a):
        value=a.get('timeout',120)
        if not isinstance(value,(int,float)) or isinstance(value,bool) or not 0<value<=1200: raise ValueError('invalid_timeout')
        return value

    def _tc02_inspect(self,a):
        command="import json,os,shutil; print(json.dumps({'cpus':os.cpu_count(),'disk_free_bytes':shutil.disk_usage('/tmp').free,'python':__import__('sys').version.split()[0],'tools':{k:bool(shutil.which(k)) for k in ['python3','uv','git','gcc']}}))"
        result=bounded_process(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','tc02',
                                'python3 -c '+shlex.quote(command)],timeout=20,env=self._ssh_env())
        if result['returncode']: return {'ok':False,'error_code':'remote_inspection_failed'}
        return {'capabilities':json.loads(result['output'])}

    @staticmethod
    def _ssh_env():
        return {k:v for k,v in os.environ.items() if k in ('PATH','HOME','SSH_AUTH_SOCK','LANG')}

    @staticmethod
    def _relative(name):
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or not p.parts or any(x.startswith('.') or x.lower() in ('auth.json','credentials','id_rsa','id_ed25519') for x in p.parts):
            raise ValueError('unsafe_artifact_path')
        return p

    def _tc02_run(self,a):
        command=a.get('command',''); timeout=self._timeout(a)
        if not isinstance(command,str) or not 0<len(command)<=20000: raise ValueError('invalid_command')
        files={}; total=0
        upload=a.get('upload',[]); retrieve=a.get('retrieve',[])
        if not isinstance(upload,list) or not isinstance(retrieve,list) or len(upload)>20 or len(retrieve)>10: raise ValueError('invalid_artifact_list')
        for name in upload:
            p=self._relative(name); source=self.workspace/p
            if any(part.is_symlink() for part in [source,*source.parents]) or not source.resolve().is_relative_to(self.workspace): raise ValueError('unsafe_artifact_path')
            if not source.is_file() or source.stat().st_size>8*1024*1024: raise ValueError('artifact_too_large_or_missing')
            data=source.read_bytes(); total+=len(data)
            if total>8*1024*1024: raise ValueError('artifact_too_large_or_missing')
            files[str(p)]=base64.b64encode(data).decode()
        for name in retrieve: self._relative(name)
        job_id=hashlib.sha256(self.action_id.encode()).hexdigest()[:32]
        payload=json.dumps({'job_id':job_id,'command':command,'timeout':timeout,'files':files,'retrieve':retrieve}).encode()
        started=time.monotonic()
        result=bounded_process(['ssh','-o','Compression=yes','-o','BatchMode=yes','-o','ConnectTimeout=10','tc02','python3 -c '+shlex.quote(REMOTE)],
                               timeout=timeout+20,input_data=payload,env=self._ssh_env())
        transport={'upload_bytes':total,'payload_bytes':len(payload),'seconds':round(time.monotonic()-started,3),
                   'timed_out':result['timed_out'],'returncode':result['returncode'],'compression':True}
        if result['returncode'] or result['timed_out']: return {'ok':False,'error_code':'remote_outcome_uncertain_no_retry','job_id':job_id,'transport':transport}
        remote=json.loads(result['output']); retrieved={}
        from .atomic import atomic_write_bytes
        for name,data in remote.pop('files',{}).items():
            target=self.workspace/'remote-results'/self._relative(name)
            if any(p.is_symlink() for p in [target,*target.parents]): raise ValueError('unsafe_artifact_path')
            target.parent.mkdir(parents=True,exist_ok=True); decoded=base64.b64decode(data)
            atomic_write_bytes(target,decoded); retrieved[name]={'bytes':len(decoded),'sha256':hashlib.sha256(decoded).hexdigest()}
        return {'ok':remote['returncode']==0,**remote,'job_id':job_id,'retrieved':retrieved,'transport':transport}

    def _tc02_job_status(self,a):
        job_id=a.get('job_id','')
        if not isinstance(job_id,str) or not re.fullmatch('[a-f0-9]{32}',job_id):
            raise ValueError('invalid_remote_job_id')
        result=bounded_process(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','tc02',
                                'python3 -c '+shlex.quote(REMOTE_STATUS)],timeout=20,
                               input_data=json.dumps({'job_id':job_id}).encode(),env=self._ssh_env())
        if result['returncode'] or result['timed_out']:
            return {'ok':False,'error_code':'remote_status_unavailable','job_id':job_id}
        return json.loads(result['output'])
