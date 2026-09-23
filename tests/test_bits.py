import json
import pytest
from xauusd.bits import BitsClient, BitsError, validate_envelope


def envelope(**changes):
    obj = dict(protocol="xauusd/1", cycle_id="cycle", reply_to="message", status="completed",
               summary="ok", actions=[], next_review_at=None, blocker=None)
    obj.update(changes)
    return obj


def shell_action(**changes):
    args = dict(command="pwd", cwd="/tmp", timeout_sec=30, max_output_bytes=4096)
    args.update(changes)
    return dict(id="first", type="shell", args=args)


@pytest.mark.parametrize("changes", [dict(reply_to="wrong"), dict(cycle_id="wrong"),
    dict(status="action_required"), dict(actions=[shell_action()]), dict(extra=1),
    dict(next_review_at="2026-09-23T10:00:00"), dict(next_review_at="2026-09-23T10:00:00+08:00"),
    dict(status="blocked"), dict(actions="")])
def test_refuses_invalid_envelopes(changes):
    with pytest.raises(BitsError): validate_envelope(json.dumps(envelope(**changes)), "cycle", "message")


@pytest.mark.parametrize("args", [dict(timeout_sec=True), dict(timeout_sec=3601),
    dict(max_output_bytes=0), dict(cwd="relative"), dict(command=""), dict(command="a\0b")])
def test_refuses_invalid_shell_limits(args):
    with pytest.raises(BitsError):
        validate_envelope(json.dumps(envelope(status="action_required", actions=[shell_action(**args)])), "cycle", "message")


def test_strict_json_and_arbitrary_command():
    obj = envelope(status="action_required", actions=[shell_action(command="python -c 'print(2)' | cat")])
    assert validate_envelope(json.dumps(obj), "cycle", "message") == obj
    for raw in ['```json\n{}\n```', '{"a":1,"a":2}', '{"a":NaN}']:
        with pytest.raises(BitsError): validate_envelope(raw, "cycle", "message")


def test_transport_submission_and_polling(monkeypatch):
    client = object.__new__(BitsClient)
    calls = []
    def request(path, payload=None):
        calls.append((path,payload))
        if payload: return {"data":{"id":"instance"}}
        return {"data":{"attributes":{"instanceStatus":{"detailsKind":"SUCCEEDED"},
                                      "outputs":{"output":json.dumps(envelope())}}}}
    monkeypatch.setattr(client, "_request", request)
    assert client.submit({"message_id":"message"}) == "instance"
    assert json.loads(calls[0][1]["meta"]["payload"]["input"])["message_id"] == "message"
    assert client.poll("instance", "cycle", "message")["actions"] == []
    monkeypatch.setattr(client, "_request", lambda *a: {"data":{"attributes":{"instanceStatus":{"detailsKind":"IN_PROGRESS"}}}})
    assert client.poll("instance", "cycle", "message") is None
    monkeypatch.setattr(client, "_request", lambda *a: {"data":{"attributes":{"instanceStatus":{"detailsKind":"FAILED"}}}})
    with pytest.raises(BitsError): client.poll("instance", "cycle", "message")


def test_workflow_agent_identity_is_verified(monkeypatch):
    client = object.__new__(BitsClient)
    spec = {"data":{"attributes":{"published":True,"spec":{
        "steps":[{"actionId":"com.datadoghq.dd.bitsai.customagent.customAgentExecute",
                  "parameters":[{"name":"customAgentId","value":"expected-agent"}]}],
        "outputSchema":{"parameters":[{"name":"output","value":"{{ Steps.agent.finalResponse }}"}]}}}}}
    monkeypatch.setattr(client,"_request",lambda: spec)
    client.verify_agent("expected-agent")
    with pytest.raises(BitsError): client.verify_agent("other-agent")
    spec['data']['attributes']['spec']['outputSchema']['parameters'][0]['value']=''
    with pytest.raises(BitsError): client.verify_agent("expected-agent")
