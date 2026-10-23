import sys
import types

from fastapi import FastAPI
from fastapi.testclient import TestClient


def client(monkeypatch):
    from xauusd.lab_dashboard import attach_routes
    from xauusd import lab_api
    monkeypatch.setattr(lab_api, 'snapshot', lambda transcript, paper: {'status': {'state': 'running'}, 'account': paper})
    monkeypatch.setattr(lab_api, 'chart', lambda timeframe, limit: {'timeframe': timeframe, 'limit': limit, 'bars': []})
    monkeypatch.setattr(lab_api, 'events', lambda transcript, after, limit: {'events': [], 'latest_id': after, 'limit': limit})
    app = FastAPI()
    attach_routes(app, object(), lambda: {'equity': 1000})
    return TestClient(app), app


def test_read_only_routes_and_snapshot(monkeypatch):
    c, app = client(monkeypatch)
    assert c.get('/api/lab').json()['account']['equity'] == 1000
    assert c.get('/lab').status_code == 200
    assert c.post('/api/lab').status_code == 405
    assert all(route.methods <= {'GET', 'HEAD'} for route in app.routes)


def test_query_bounds_and_timeframes(monkeypatch):
    c, _ = client(monkeypatch)
    assert c.get('/api/lab/chart?timeframe=M5&limit=100').json()['timeframe'] == 'M5'
    assert c.get('/api/lab/chart?timeframe=evil').status_code == 422
    assert c.get('/api/lab/chart?limit=1001').status_code == 422
    assert c.get('/api/lab/events?after=10&limit=20').json()['latest_id'] == 10
    assert c.get('/api/lab/events?limit=201').status_code == 422


def test_page_has_local_interactive_read_only_surfaces():
    from xauusd.lab_dashboard import PAGE
    for token in ['price-chart', 'equity-chart', '/api/lab/chart', '/api/lab/events', 'textContent', 'pointermove', 'Research pipeline', 'Data coverage', 'Storage', '/legacy']:
        assert token in PAGE
    assert 'innerHTML' not in PAGE
    assert 'https://cdn' not in PAGE
    assert "method: 'POST'" not in PAGE


def test_real_renderer_preserves_untrusted_activity_as_text():
    import shutil
    import subprocess
    import pytest
    from xauusd.lab_dashboard import PAGE
    if not shutil.which('node'):
        pytest.skip('Node unavailable for dashboard renderer execution')
    script = PAGE.split('<script>', 1)[1].split('</script>', 1)[0]
    script = script[:script.index("$('timeframes').addEventListener")]
    harness = r'''
const assert=require('node:assert/strict');
function element(tag){return {tag,children:[],textContent:'',value:'all',append(...nodes){this.children.push(...nodes)},replaceChildren(){this.children=[]}};}
const nodes={activity:element('div'),'event-filter':element('select')};
global.document={getElementById:id=>nodes[id],createElement:element};
'''+script+r'''
mergeEvents([{id:1,kind:'codex',summary:'<img src=x onerror=alert(1)>',payload:{command:'<script>danger()</script>'}}]);
const event=nodes.activity.children[0];
assert.equal(event.children[1].textContent,'<img src=x onerror=alert(1)>');
assert.equal(event.children[2].tag,'details');
assert.equal(event.children[2].children[1].textContent,JSON.stringify({command:'<script>danger()</script>'},null,2));
assert.equal(latest,1);
mergeEvents([{id:1,summary:'duplicate'}]);
assert.equal(nodes.activity.children.length,1);
'''
    result = subprocess.run(['node', '-e', harness], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr


def test_curated_panels_keep_raw_records_collapsed():
    import subprocess
    from xauusd.lab_dashboard import PAGE
    script = PAGE.split('<script>', 1)[1].split('</script>', 1)[0]
    script = script[:script.index("$('timeframes').addEventListener")]
    harness = r'''
const assert=require('node:assert/strict');
function element(tag){return {tag,children:[],textContent:'',append(...nodes){this.children.push(...nodes)},replaceChildren(){this.children=[]}};}
const nodes={data:element('div'),storage:element('div'),positions:element('div'),'data-state':element('span')};
global.document={getElementById:id=>nodes[id],createElement:element};
'''+script+r'''
renderData({rows:2410519,start:'2019-12-01T00:00:00Z',end:'2026-10-21T00:00:00Z',fresh:false,quote_fresh:true,quote:{bid:2700,ask:2700.25,spread:.25},needs:['tick history']});
assert.equal(nodes['data-state'].textContent,'Stale');
assert.equal(nodes.data.children[0].children[1].textContent,'2,410,519');
renderStorage({used_bytes:2000000000,free_bytes:4000000000,deleted_bytes:1000000000,policy:{events:300}});
assert.equal(nodes.storage.children[0].children[1].textContent,'2.00 GB');
renderPositions({position:1,mark_price:2700,recent_fills:[{side:'BUY',quantity:1,price:2700,decision_id:'never show this enormous ID'}]},{});
assert(!nodes.positions.children.some(n=>n.textContent.includes('enormous ID')));
assert.equal(nodes.positions.children.at(-1).tag,'details');
'''
    result = subprocess.run(['node', '-e', harness], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr


def test_snapshot_projects_current_agent_and_archived_jobs(tmp_path, monkeypatch):
    from xauusd import lab_api
    from xauusd.lab_store import LabStore
    from xauusd.local_state import SQLiteAgentTranscriptStore, SQLitePaperTradingStore
    from xauusd.paper_trading import PaperTrading, PaperRiskConfig
    transcript = SQLiteAgentTranscriptStore(str(tmp_path / 'state.db'))
    store = LabStore(transcript)
    agent = {'session_id': 'new', 'started_at': '2026-10-21T10:00:00+00:00',
             'goal': {'aspirational_daily_return_pct': 100, 'achieved': False},
             'agenda': [{'id': 'a', 'title': 'Find independent sources', 'status': 'active'}],
             'assessment': '<img onerror=bad>', 'compute': {'tc02': {'state': 'unavailable'}}}
    store.meta('agent', agent)
    store.meta('engineering', {'state': 'testing'})
    store.job({'id': 'old', 'started_at': '2026-10-20T10:00:00+00:00', 'state': 'succeeded'})
    store.job({'id': 'fresh', 'session_id': 'new', 'started_at': '2026-10-21T10:01:00+00:00', 'state': 'running'})
    monkeypatch.setattr(lab_api, '_data', lambda: (_ for _ in ()).throw(ValueError()))
    paper = PaperTrading(SQLitePaperTradingStore(str(tmp_path / 'state.db')), PaperRiskConfig())
    result = lab_api.snapshot(transcript, paper)
    assert result['agent'] == agent
    assert result['engineering']['state'] == 'testing'
    assert [j['id'] for j in result['current_jobs']] == ['fresh']
    assert [j['id'] for j in result['archived_jobs']] == ['old']
    assert result['performance']['daily_return_pct'] == 0
    assert result['performance']['target_achieved'] is False


def test_agent_renderer_uses_public_text_and_honest_missing_state():
    import subprocess
    from xauusd.lab_dashboard import PAGE
    script = PAGE.split('<script>', 1)[1].split('</script>', 1)[0]
    script = script[:script.index("$('timeframes').addEventListener")]
    harness = r'''
const assert=require('node:assert/strict');
function element(tag){return {tag,children:[],textContent:'',append(...nodes){this.children.push(...nodes)},replaceChildren(){this.children=[]}};}
const ids=['agent-goal','agent-assessment','agent-agenda','agent-capabilities','agent-compute','agent-engineering','agent-session','agent-phase','agent-tools'];
const nodes=Object.fromEntries(ids.map(id=>[id,element('div')]));
global.document={getElementById:id=>nodes[id],createElement:element};
'''+script+r'''
renderAgent({agent:{session_id:'new',phase:'investigating',goal:{aspirational_daily_return_pct:100},assessment:'<script>alert(1)</script>',agenda:[{title:'<img src=x>',status:'active'}],compute:{tc02:{state:'unavailable'}},capabilities:['source_search'],latest_tool_results:[{name:'search',state:'completed'}]},performance:{daily_return_pct:0,target_achieved:false},engineering:{state:'testing'}});
assert(nodes['agent-goal'].textContent.includes('100% daily aspiration'));
assert(nodes['agent-goal'].textContent.includes('0.00% measured'));
assert.equal(nodes['agent-assessment'].textContent,'<script>alert(1)</script>');
assert.equal(nodes['agent-agenda'].children[0].children[0].textContent,'<img src=x>');
assert(JSON.stringify(nodes['agent-compute']).includes('unavailable'));
renderAgent({});
assert(nodes['agent-assessment'].textContent.includes('No public assessment'));
assert(nodes['agent-session'].textContent.includes('No agent session'));
'''
    result = subprocess.run(['node', '-e', harness], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr


def test_activity_session_boundary_keeps_old_events_out_of_live_stream():
    import subprocess
    from xauusd.lab_dashboard import PAGE
    script = PAGE.split('<script>', 1)[1].split('</script>', 1)[0]
    script = script[:script.index("$('timeframes').addEventListener")]
    harness = r'''
const assert=require('node:assert/strict');
function element(tag){return {tag,children:[],value:'all',textContent:'',append(...nodes){this.children.push(...nodes)},replaceChildren(){this.children=[]}};}
const nodes={activity:element('div'),'archived-activity':element('div'),'event-filter':element('select')};
global.document={getElementById:id=>nodes[id],createElement:element};
'''+script+r'''
mergeEvents([{id:1,time:'2026-10-20T00:00:00Z',summary:'Prior session'}]);
assert.equal(nodes['archived-activity'].children.length,1);
sessionStarted='2026-10-21T00:00:00Z';
mergeEvents([{id:2,time:'2026-10-21T01:00:00Z',kind:'tool_call',summary:'New actual tool'}]);
assert.equal(nodes.activity.children.length,1);
assert.equal(nodes.activity.children[0].children[1].textContent,'New actual tool');
assert.equal(nodes['archived-activity'].children.length,1);
'''
    result = subprocess.run(['node', '-e', harness], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr


def test_codex_efficiency_panel_shows_observed_usage_without_billing_claims():
    import subprocess
    from xauusd.lab_dashboard import PAGE
    script=PAGE.split('<script>',1)[1].split('</script>',1)[0]
    script=script[:script.index("$('timeframes').addEventListener")]
    harness=r'''
const assert=require('node:assert/strict');
function element(tag){return {tag,children:[],textContent:'',append(...nodes){this.children.push(...nodes)},replaceChildren(){this.children=[]}};}
const nodes={'codex-usage':element('div')};
global.document={getElementById:id=>nodes[id],createElement:element};
'''+script+r'''
renderCodex({state:'ok',observed_model:'gpt-6-luna',compactions:450,last_token_usage:{input_tokens:10000,cached_input_tokens:8000,output_tokens:300},brief_bytes:30000,recent_compactions:['2026-10-23T01:00:00Z'],auto_compact_token_limit:80000});
const root=nodes['codex-usage'];
assert.equal(root.children[0].children[1].textContent,'gpt-6-luna');
assert.equal(root.children[1].children[1].textContent,'10,000 / 8,000');
assert.equal(root.children[4].children[1].textContent,'450');
assert.equal(root.children.at(-1).tag,'details');
renderCodex({state:'unavailable',compactions:null});
assert.equal(root.children[4].children[1].textContent,'Unavailable');
'''
    result=subprocess.run(['node','-e',harness],capture_output=True,text=True,timeout=10)
    assert result.returncode==0,result.stderr


def test_dashboard_tabs_preserve_one_selected_panel_and_reject_unknown_names():
    import subprocess
    from xauusd.lab_dashboard import PAGE
    script=PAGE.split('<script>',1)[1].split('</script>',1)[0]
    script=script[:script.index("$('timeframes').addEventListener")]
    harness=r'''
const assert=require('node:assert/strict');
const names=['overview','experiments','research','system'];
const tabs=names.map(name=>({dataset:{view:name},attrs:{},setAttribute(k,v){this.attrs[k]=v},classList:{toggle(){}}}));
const panels=names.map(name=>({dataset:{panel:name},hidden:false}));
global.document={getElementById:()=>null,querySelectorAll:selector=>selector==='[data-view]'?tabs:panels};
'''+script+r'''
selectView('experiments');
assert.deepEqual(panels.map(p=>p.hidden),[true,false,true,true]);
assert.equal(tabs[1].attrs['aria-selected'],'true');
assert.equal(tabs[0].tabIndex,-1);
assert.equal(tabs[1].tabIndex,0);
selectView('unknown');
assert.deepEqual(panels.map(p=>p.hidden),[true,false,true,true]);
'''
    result=subprocess.run(['node','-e',harness],capture_output=True,text=True,timeout=10)
    assert result.returncode==0,result.stderr
