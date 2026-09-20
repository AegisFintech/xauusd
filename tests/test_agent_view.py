import json
from datetime import datetime, timedelta, timezone
import threading
import time
from urllib import request

import pytest

from xauusd.agent_loop import InMemoryAgentTranscriptStore
from xauusd.agent_view import create_app
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


def test_steps_endpoint_defaults_to_newest_first(server):
    with request.urlopen(server + "/api/steps?run_id=agent_test_1") as response:
        payload = json.loads(response.read())
    assert payload["run_status"] == "running"
    assert payload["order"] == "desc"
    assert payload["count"] == 2
    assert payload["steps"][0]["phase"] == "tick_end"
    assert payload["steps"][1]["content"]["content"] == "thinking about the bar"


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