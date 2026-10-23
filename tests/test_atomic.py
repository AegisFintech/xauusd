"""The durable-write primitives every writer in this repository shares."""
import threading
import time

import pytest

from xauusd.atomic import atomic_write_bytes, file_lock


def test_atomic_write_replaces_the_target_and_leaves_no_temporary(tmp_path):
    target = tmp_path / "status.json"
    atomic_write_bytes(target, b'{"state":"ok"}')

    assert target.read_bytes() == b'{"state":"ok"}'
    assert [path.name for path in tmp_path.iterdir()] == ["status.json"]


def test_file_lock_is_exclusive_between_holders(tmp_path):
    """Two holders must never be inside the section at once.

    `flock` is per open file description, so this holds across threads and across
    processes -- which is the case that matters: the feed and the data-update
    timer are different processes writing one store.
    """
    target = tmp_path / "XAUUSD_M1.parquet"
    steps = []

    def worker(name):
        with file_lock(target, timeout=10):
            steps.append(f"{name}:enter")
            time.sleep(0.02)
            steps.append(f"{name}:exit")

    threads = [threading.Thread(target=worker, args=(f"w{index}",)) for index in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(steps) == 8
    for enter, leave in zip(steps[0::2], steps[1::2]):
        assert enter.split(":")[0] == leave.split(":")[0], steps


def test_file_lock_times_out_instead_of_waiting_forever(tmp_path):
    """A wedged writer has to fail loudly, not hang a trading loop."""
    target = tmp_path / "XAUUSD_M1.parquet"

    with file_lock(target, timeout=5):
        with pytest.raises(TimeoutError, match="write lock"):
            with file_lock(target, timeout=0.2):
                pytest.fail("the lock was handed to a second holder")


def test_lock_file_lives_beside_the_target_and_is_released(tmp_path):
    target = tmp_path / "XAUUSD_M1.parquet"

    with file_lock(target) as lock_path:
        assert lock_path == tmp_path / "XAUUSD_M1.parquet.lock"
        assert lock_path.exists()
        assert not target.exists()

    with file_lock(target, timeout=0.2):
        pass


def test_file_lock_creates_a_missing_parent_directory(tmp_path):
    target = tmp_path / "processed" / "XAUUSD_M1.parquet"

    with file_lock(target, timeout=1) as lock_path:
        assert lock_path.parent == tmp_path / "processed"
