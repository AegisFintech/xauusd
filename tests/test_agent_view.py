import json
import threading
import time
from urllib import request

import pytest

from xauusd.agent_loop import InMemoryAgentTranscriptStore
from xauusd.agent_view import create_app


@pytest.fixture
def server():
    import uvicorn

    store = InMemoryAgentTranscriptStore()
    store.initialize()
    store.start_run("agent_test_1")
    store.append("agent_test_1", 1, "assistant", {"content": "thinking about the bar"})
    store.append("agent_test_1", 1, "tick_end", {"summary": "done", "steps": 2})

    app = create_app(store)
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