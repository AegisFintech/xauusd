import json
from datetime import datetime, timedelta, timezone
import threading
import time
from urllib import request

import pytest

from xauusd.agent_loop import InMemoryAgentTranscriptStore
from xauusd.agent_status import write_status
from xauusd.agent_view import STALE_TICK_ALERT_THRESHOLD, create_app, step_display
from xauusd.paper_trading import InMemoryPaperTradingStore, PaperDecision, PaperRiskConfig, PaperTrading


@pytest.fixture
def paper_trading():
    return PaperTrading(InMemoryPaperTradingStore(), PaperRiskConfig(max_market_data_age_seconds=120))


@pytest.fixture
def server(paper_trading):
    import uvicorn

    store = InMemoryAgentTranscriptStore()
    store.initialize()
    store.start_run("agent_test_1")
    store.append("agent_test_1", 1, "assistant", {"content": "thinking about the bar"})
    store.append("agent_test_1", 1, "tick_end", {"summary": "done", "steps": 2})

    app = create_app(store, paper=paper_trading)
    config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 10
    while not server.started and time.time() < deadline:
        time.sleep(0.02)
    if not server.started:
        pytest.skip("uvicorn did not start")
    port = server.servers[0].sockets[0].getsockname()[1]
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


def test_index_html_renders_live_view(server):
    with request.urlopen(server + "/") as response:
        body = response.read().decode()
    assert "live thinking" in body
    assert "newest first" in body
    assert "load older decisions" in body
    assert "raw json" in body
    assert "steps" in body
    assert "&middot;" not in body
    assert 'id="paper"' in body


def test_index_html_renders_times_in_gmt_plus_eight(server):
    with request.urlopen(server + "/") as response:
        body = response.read().decode()

    # Display-only conversion: a fixed +08:00 offset, not the browser's own zone.
    assert "DISPLAY_OFFSET_MINUTES=480" in body
    assert "+08:00" in body
    assert "' UTC'" not in body


def test_steps_endpoint_defaults_to_newest_first(server):
    with request.urlopen(server + "/api/steps?run_id=agent_test_1") as response:
        payload = json.loads(response.read())
    assert payload["run_status"] == "running"
    assert payload["order"] == "desc"
    assert payload["count"] == 2
    assert payload["steps"][0]["phase"] == "tick_end"
    assert payload["steps"][1]["content"]["content"] == "thinking about the bar"
    assert payload["steps"][1]["display"]["text"] == "thinking about the bar"


def test_bits_decisions_show_summary_instead_of_protocol_json():
    reply={"protocol":"xauusd/1","status":"action_required","summary":"Checking volatility before considering a trade.",
           "actions":[{"id":"one","type":"shell","args":{"command":"echo inspect"}}]}
    display=step_display({"phase":"assistant","content":{"action":"tool","reply":json.dumps(reply),"summary":reply['summary']}})
    assert display=={"title":"Next action","text":reply['summary']}
    assert 'undefined' not in display['text'] and 'xauusd/1' not in display['text']


def test_shell_command_and_output_are_not_in_collapsed_text():
    call=step_display({"phase":"tool_call","content":{"tool":"shell","input":{"command":"echo implementation"}}})
    result=step_display({"phase":"tool_result","content":{"status":"succeeded","exit_code":0,
                        "stdout":"private implementation details","total_bytes":4096,"truncated":True}})
    assert 'implementation' not in call['text']+result['text']
    assert 'successfully' in result['text'] and 'shortened' in result['text']
    assert step_display({'phase':'bits_submit','content':{'cycle_id':'internal'}})['title']=='Analyzing'


def test_disclosures_are_collapsed_and_render_untrusted_text_safely():
    # Execute the real page renderer with a minimal DOM; no browser dependency.
    import subprocess
    from xauusd.agent_view import _PAGE
    script=_PAGE.split('<script>',1)[1].split('</script>',1)[0]
    script=script[:script.index(' setInterval(pull,1000)')]
    harness='''
const assert=require('node:assert/strict');
global.document={createElement:tag=>({tag,children:[],textContent:'',appendChild(n){this.children.push(n)}})};
global.window={};
'''+script+'''
const node=stepNode({id:1,phase:'tool_call',tick:1,occurred_at:'2026-09-23T10:00:00Z',
 display:{title:'Tool call',text:'Inspecting market data.'},content:{input:{command:'<script>alert(1)</script>',cwd:'/tmp'}}});
const details=node.children[2];
assert.equal(details.tag,'details');assert.notEqual(details.open,true);
assert.equal(node.children[1].textContent,'Inspecting market data.');
assert(details.children.some(n=>n.tag==='pre'&&n.textContent==='<script>alert(1)</script>'));
assert.equal(details.children[0].textContent,'Details');
'''
    result=subprocess.run(['node','-e',harness],capture_output=True,text=True)
    assert result.returncode==0,result.stderr


def test_steps_endpoint_after_cursor_returns_newer_ascending(server):
    with request.urlopen(server + "/api/steps?run_id=agent_test_1&after=1") as response:
        payload = json.loads(response.read())
    assert payload["order"] == "asc"
    assert [s["phase"] for s in payload["steps"]] == ["tick_end"]


def test_steps_endpoint_before_cursor_pages_older_history(server):
    with request.urlopen(server + "/api/steps?run_id=agent_test_1&before=2") as response:
        payload = json.loads(response.read())
    assert payload["order"] == "desc"
    assert [s["phase"] for s in payload["steps"]] == ["assistant"]

    with request.urlopen(server + "/api/steps?run_id=agent_test_1&before=1") as response:
        payload = json.loads(response.read())
    assert payload["count"] == 0


def test_status_endpoint_returns_latest_run(server):
    with request.urlopen(server + "/api/status") as response:
        payload = json.loads(response.read())
    assert payload["latest_run_id"] == "agent_test_1"
    assert payload["latest_run_status"] == "running"


def test_runs_endpoint_reports_tick_counts(server):
    with request.urlopen(server + "/api/runs?limit=6") as response:
        payload = json.loads(response.read())
    assert payload["runs"][0]["run_id"] == "agent_test_1"
    assert payload["runs"][0]["ticks"] == 0


def test_paper_endpoint_reports_headline_metrics(server):
    with request.urlopen(server + "/api/paper") as response:
        payload = json.loads(response.read())
    summary = payload["paper"]["summary"]
    assert summary["position"] == 0.0
    assert summary["side"] == "flat"
    assert summary["cash"] == pytest.approx(100_000.0)
    assert summary["equity"] == pytest.approx(100_000.0)
    assert summary["day_pl"] == pytest.approx(0.0)
    assert summary["realized_pl"] == pytest.approx(0.0)
    assert summary["trades_today"] == 0
    assert summary["recent_fills"] == []
    assert payload["paper"]["risk"]["daily_loss_limit"] > 0


def test_paper_endpoint_reflects_accepted_fill(server, paper_trading):
    paper_trading.start("test")
    now = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)  # Thursday midday, market open
    result = paper_trading.evaluate(PaperDecision("fill-test-1", "XAUUSD", "BUY", 0.5, 4290.0, now - timedelta(seconds=5)), now)
    assert result["accepted"] is True

    with request.urlopen(server + "/api/paper") as response:
        payload = json.loads(response.read())
    summary = payload["paper"]["summary"]
    assert summary["position"] == pytest.approx(0.5)
    assert summary["side"] == "long"
    assert summary["trades_today"] == 1
    assert summary["equity"] == pytest.approx(100_000.0)
    assert len(summary["recent_fills"]) == 1
    assert summary["recent_fills"][0]["decision_id"] == "fill-test-1"


def test_health_endpoint_reports_all_sections(server, paper_trading):
    paper_trading.start("test")
    with request.urlopen(server + "/api/health") as response:
        payload = json.loads(response.read())
    assert payload["status"] in {"ok", "degraded"}
    assert isinstance(payload["alerts"], list)
    assert payload["agent"]["latest_run_id"] == "agent_test_1"
    assert "heartbeat" in payload["agent"]
    assert payload["paper"]["stopped"] is False
    assert "market_open" in payload["paper"]
    assert payload["paper"]["market_open"] in {True, False}
    assert "data_update" in payload
    assert "age_seconds" in payload["data_update"]
    assert payload["database"]["backend"] in {"local", "cockroach"}
    assert "integrity" in payload["database"]


def test_age_seconds_parses_timezone_aware_timestamps():
    from xauusd.agent_view import _age_seconds
    moment = datetime.now(timezone.utc) - timedelta(seconds=30)
    age = _age_seconds(moment.isoformat())
    assert age is not None
    assert 25 < age < 35
    naive = moment.replace(tzinfo=None)
    assert _age_seconds(naive.isoformat()) is not None
    assert _age_seconds(None) is None
    assert _age_seconds("not-a-timestamp") is None


def _write_heartbeat(path, stale_ticks):
    now = datetime.now(timezone.utc).isoformat()
    write_status({"run_id": "agent_stuck", "pid": 1, "status": "stale_data",
                  "last_tick_status": "stale_data", "started_at": now, "last_tick_at": now,
                  "tick": 900, "market_open": True, "consecutive_errors": 0, "stalled": False,
                  "consecutive_stale_ticks": stale_ticks}, path)


def test_health_degrades_when_ticks_never_reach_the_planner(server, paper_trading, tmp_path, monkeypatch):
    # A stuck freshness gate keeps the heartbeat fresh and the feed downloading, so
    # liveness checks alone reported "ok" while the agent never reasoned once.
    paper_trading.start("test")
    status_path = tmp_path / "agent_status.json"
    monkeypatch.setenv("AGENT_STATUS_FILE", str(status_path))
    _write_heartbeat(status_path, STALE_TICK_ALERT_THRESHOLD)

    with request.urlopen(server + "/api/health") as response:
        payload = json.loads(response.read())

    assert payload["status"] == "degraded"
    assert any("unproductive" in alert for alert in payload["alerts"])


def test_health_does_not_alert_below_the_stale_tick_threshold(server, paper_trading, tmp_path, monkeypatch):
    paper_trading.start("test")
    status_path = tmp_path / "agent_status.json"
    monkeypatch.setenv("AGENT_STATUS_FILE", str(status_path))
    _write_heartbeat(status_path, STALE_TICK_ALERT_THRESHOLD - 1)

    with request.urlopen(server + "/api/health") as response:
        payload = json.loads(response.read())

    assert not any("unproductive" in alert for alert in payload["alerts"])


def test_health_surfaces_missing_research_progress(server, tmp_path, monkeypatch):
    path = tmp_path / 'status.json'
    monkeypatch.setenv('AGENT_STATUS_FILE', str(path))
    path.write_text(json.dumps({'recorded_at': datetime.now(timezone.utc).isoformat(),
        'research_progress': {'needs_attention': True, 'cycles_without_new_notes': 3}}))
    with request.urlopen(server + '/api/health') as response:
        data = json.load(response)
    assert any('3 cycles without updated research notes' in alert for alert in data['alerts'])
