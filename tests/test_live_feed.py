import json
import subprocess
import sys
from pathlib import Path

import pytest

from xauusd.live_feed import LiveBarFeed, LiveFeedConfig, closed_bar, run_feed


def unavailable_type():
    from xauusd.live_feed import LiveFeedUnavailable
    return LiveFeedUnavailable


def config(tmp_path, **overrides):
    values = {"processed_dir": str(tmp_path / "processed"),
              "status_path": str(tmp_path / "status.json"),
              "state_path": str(tmp_path / "feed.json")}
    values.update(overrides)
    return LiveFeedConfig(**values)


def test_unimplemented_subscription_is_a_coded_failure_not_a_bare_error(tmp_path, monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    feed = LiveBarFeed(config(tmp_path), store=object(), reactor_runner=lambda call: None)
    with pytest.raises(unavailable_type()) as caught:
        feed._subscribe()
    assert caught.value.error_code == "live_feed_not_implemented"
    with pytest.raises(unavailable_type()) as discovered:
        feed._discover()
    assert discovered.value.error_code == "live_feed_not_implemented"


def test_a_feed_that_cannot_run_writes_its_status_and_reraises(tmp_path, monkeypatch):
    # The unit is Restart=always and StandardError=null, so an unimplemented feed
    # that raised quietly restarted forever leaving no status file and no journal
    # entry. It has to record the reason where /api/health can see it.
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    cfg = config(tmp_path)
    with pytest.raises(unavailable_type()):
        run_feed(cfg)
    status = json.loads(Path(cfg.status_path).read_text())
    assert status["state"] == "unavailable"
    assert status["error_code"] == "live_feed_not_implemented"


def test_data_feed_run_exits_nonzero_when_the_feed_cannot_run(tmp_path):
    # Exiting 0 under Restart=always is an invisible infinite restart loop; the
    # exit code is the only signal systemd gets.
    result = subprocess.run(
        [sys.executable, "-m", "xauusd.cli", "data-feed", "run"],
        capture_output=True, text=True, timeout=120, cwd=str(Path(__file__).resolve().parents[1]),
        env={"PATH": "/usr/bin:/bin", "CTRADER_DEMO_ONLY": "true",
             "DATA_FEED_STATUS_PATH": str(tmp_path / "status.json"),
             "DATA_FEED_STATE_PATH": str(tmp_path / "feed.json"),
             "XAUUSD_STATE_BACKEND": "local"})
    assert result.returncode != 0, result.stdout
    assert "live_feed_not_implemented" in result.stdout


def test_data_feed_status_is_none_before_the_feed_has_ever_run(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "xauusd.cli", "data-feed", "status"],
        capture_output=True, text=True, timeout=120, cwd=str(Path(__file__).resolve().parents[1]),
        env={"PATH": "/usr/bin:/bin", "DATA_FEED_STATUS_PATH": str(tmp_path / "absent.json")})
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "none"


def test_a_closed_bar_is_the_only_bar_that_may_be_persisted():
    from datetime import datetime, timedelta, timezone
    now = datetime(2026, 10, 5, 14, 30, tzinfo=timezone.utc)
    assert closed_bar(now - timedelta(minutes=1), now) is True
    # The forming bar is not closed, so persisting it would let a later, longer
    # bar overwrite a complete one.
    assert closed_bar(now, now) is False
