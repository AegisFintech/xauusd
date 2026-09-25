from pathlib import Path

import pytest

from xauusd.agent_status import read_status, write_status


def test_write_status_is_atomic_and_readable(tmp_path):
    path = tmp_path / "sub" / "agent_status.json"
    after = write_status({"state": "running", "tick": 3}, path)
    assert after is None
    payload = read_status(path)
    assert payload["state"] == "running"
    assert payload["tick"] == 3
    assert payload["recorded_at"]
    assert not list((tmp_path / "sub").glob("*.tmp"))


def test_write_status_overwrites_and_records_timestamp(tmp_path):
    path = tmp_path / "agent_status.json"
    write_status({"state": "starting"}, path)
    write_status({"state": "completed"}, path)
    payload = read_status(path)
    assert payload["state"] == "completed"
    assert payload["recorded_at"]


def test_read_status_missing_or_corrupt_returns_none(tmp_path):
    missing = tmp_path / "nope.json"
    assert read_status(missing) is None
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert read_status(bad) is None

def test_bits_alerts_name_repeated_memory_failures():
    from xauusd.agent_status import bits_alerts
    assert bits_alerts(None) == [] and bits_alerts({"memory": {"state": "failing", "needs_repair": False}}) == []
    alerts = bits_alerts({"memory": {"needs_repair": True, "consecutive_failures": 3,
                                     "last_error": {"code": "ambiguous_shape", "path": "$"}}})
    assert alerts == ["memory writes failing: 3 consecutive rejected writes (last ambiguous_shape at $); "
                      "stored notes unchanged"]


def test_bits_alerts_name_missing_executables():
    from xauusd.agent_status import bits_alerts
    heartbeat = {"capabilities": {"required_missing": ["bash"], "unavailable_tools": ["graphify"],
                                  "observed_missing": ["python", "rg"]}}
    assert bits_alerts(heartbeat) == ["Bits shell is missing required executables: bash",
                                      "Bits shell jobs hit missing executables: python, rg (see capabilities fallbacks)"]
    # An optional tool with a documented fallback is not, by itself, an alert.
    assert bits_alerts({"capabilities": {"required_missing": [], "unavailable_tools": ["graphify"],
                                         "observed_missing": []}}) == []
