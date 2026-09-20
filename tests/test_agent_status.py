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