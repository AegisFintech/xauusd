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
    assert "steps" in body


def test_steps_endpoint_returns_transcript(server):
    with request.urlopen(server + "/api/steps?run_id=agent_test_1") as response:
        payload = json.loads(response.read())
    assert payload["run_status"] == "running"
    assert payload["count"] == 2
    assert payload["steps"][0]["content"]["content"] == "thinking about the bar"
    assert payload["steps"][1]["phase"] == "tick_end"


def test_status_endpoint_returns_latest_run(server):
    with request.urlopen(server + "/api/status") as response:
        payload = json.loads(response.read())
    assert payload["latest_run_id"] == "agent_test_1"
    assert payload["latest_run_status"] == "running"