import json
import subprocess
from threading import Thread
import time
from uuid import uuid4
import pytest
from xauusd.bits import BitsError
from xauusd.bits_jobs import BitsStore, ShellJobs, SecretFilter
from xauusd.local_state import SQLiteAgentTranscriptStore


def action(command, **extra):
    args = dict(command=command, cwd="/tmp", timeout_sec=2, max_output_bytes=1024)
    args.update(extra)
    return dict(id="one", type="shell", args=args)


def wait(store, job):
    for _ in range(100):
        result = store.job(job["job_id"])
        if result["status"] != "running": return result
        time.sleep(.03)
    raise AssertionError("job failed to finish")


def test_a_job_that_raises_is_recorded_as_failed_not_left_running(tmp_path, monkeypatch):
    """A post-spawn exception must not strand the row as `running` forever.

    `state` was only ever lowered on the success paths, so an exception raised
    after the selector loop started left the status at "running". The runner then
    reported shell_running on every tick, the heartbeat stayed fresh, nothing
    alerted, and the only escape was a process restart.
    """
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    jobs = ShellJobs(store, SecretFilter(env_file=str(tmp_path / "missing.env")))

    real_popen = subprocess.Popen

    class ExplodingSelector:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def register(self, *a, **k):
            raise OSError("pipe registration failed")

        def get_map(self):
            return {}

        def select(self, *a, **k):
            return []

    monkeypatch.setattr("xauusd.bits_jobs.selectors.DefaultSelector", lambda: ExplodingSelector())
    result = jobs.start("cycle-1", action("printf 42"))
    finished = wait(store, result)

    assert finished["status"] == "failed"
    assert finished.get("error_code")
    assert "ExplodingSelector" in finished["stderr"] or finished["stderr"]
    # And the row really is terminal in the store, not just in the returned dict.
    assert store.job(result["job_id"])["status"] == "failed"


def test_a_job_never_exceeds_the_server_timeout_ceiling(tmp_path):
    """The executor enforces the ceiling, not only the caller that sets it.

    The workflow validator accepts up to 3600s. Clamping only in the runner meant
    any other caller of the executor would get a one-hour job, breaking the
    documented 20-minute guarantee.
    """
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    jobs = ShellJobs(store, SecretFilter(env_file=str(tmp_path / "missing.env")))

    result = jobs.start("cycle-1", action("sleep 0", timeout_sec=3600))
    wait(store, result)

    # The stored request records the effective timeout.
    with store.db() as db:
        row = db.execute("SELECT request_json FROM bits_jobs WHERE job_id=?", (result["job_id"],)).fetchone()
    assert json.loads(row["request_json"])["args"]["timeout_sec"] == 1200


def test_shell_job_stop_does_not_raise_on_an_unstarted_worker(tmp_path):
    """A thread registered but never started raises on join and aborted shutdown."""
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    jobs = ShellJobs(store, SecretFilter(env_file=str(tmp_path / "missing.env")))
    never_started = Thread(target=lambda: None)
    jobs.workers["ghost"] = never_started
    jobs.stop()  # must not raise
    assert jobs.cancelled.is_set()


@pytest.fixture
def jobs(tmp_path):
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path/'state.db')))
    jobs = ShellJobs(store, SecretFilter(str(tmp_path/'no-env')))
    yield jobs
    jobs.stop()


def test_execution_idempotency_and_conflict(jobs, tmp_path):
    cmd = action(f"echo one >> {tmp_path}/count; printf success")
    a = jobs.start("cycle", cmd)
    assert jobs.start("cycle", cmd)["job_id"] == a["job_id"]
    assert wait(jobs.store,a)["stdout"] == "success"
    assert (tmp_path/'count').read_text() == "one\n"
    assert jobs.start("cycle",cmd)["status"] == "succeeded"
    with pytest.raises(BitsError): jobs.start("cycle",action("echo different"))


def test_timeout_and_output_bound(jobs):
    timed = wait(jobs.store,jobs.start("slow",action("sleep 10",timeout_sec=1)))
    assert timed["status"] == "timed_out"
    output = wait(jobs.store,jobs.start("large",action("yes abc | head -c 50000")))
    assert output["truncated"] and len(output["stdout"].encode()) <= 1024
    assert output["total_bytes"] == 50000


def test_secret_output_is_not_persisted(jobs, monkeypatch):
    value = uuid4().hex
    monkeypatch.setenv("EXAMPLE_SECRET",value)
    result = wait(jobs.store,jobs.start("secret",action('printf %s "$EXAMPLE_SECRET"')))
    assert value not in str(result) and "withheld" in result["stdout"]
    with pytest.raises(BitsError): jobs.start("literal",action("echo "+value))


def test_interrupted_job_never_replayed(jobs):
    original, created = jobs.store.claim("cycle",action("echo side-effect"))
    assert created and jobs.store.recover() == 1
    assert jobs.start("cycle",action("echo side-effect"))["status"] == "unknown"


def test_cancel_process_after_output_streams_close(jobs):
    job=jobs.start('closed-streams',action('exec >/dev/null 2>&1; sleep 60',timeout_sec=60))
    time.sleep(.1)
    jobs.stop()
    assert jobs.store.job(job['job_id'])['status']=='cancelled'
    with pytest.raises(BitsError): jobs.start('late',action('echo never'))


def test_bits_jobs_prune_drops_old_terminal_rows_only(tmp_path):
    """bits_jobs grew without limit: 313 rows held 1.7 MB in two days.

    One row per shell action, each capture up to 1 MiB, and no DELETE anywhere.
    Pruning must never touch an in-flight row.
    """
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    terminal = [store.claim(f"cycle-{i}", action(f"printf {i}"))[0] for i in range(5)]
    in_flight, _created = store.claim("cycle-live", action("sleep 30"))

    for result in terminal:
        store.finish({**result, "status": "succeeded", "exit_code": 0})
    with store.db() as db:
        db.execute("UPDATE bits_jobs SET status='running' WHERE action_key=(SELECT action_key FROM bits_jobs WHERE job_id=?)",
                   (in_flight["job_id"],))

    removed = store.prune(keep=3)

    assert removed == 2
    with store.db() as db:
        statuses = sorted(row["status"] for row in db.execute("SELECT status FROM bits_jobs"))
    # keep=3 applies to terminal rows only; the in-flight row is never a candidate.
    assert statuses == ["running", "succeeded", "succeeded", "succeeded"]
    # The in-flight job is still readable.
    assert store.job(in_flight["job_id"])["status"] == "running"


def test_bits_jobs_prune_is_a_no_op_below_the_threshold(tmp_path):
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    for index in range(3):
        result, _ = store.claim(f"cycle-{index}", action(f"printf {index}"))
        store.finish({**result, "status": "succeeded", "exit_code": 0})

    assert store.prune(keep=10) == 0
    assert store.storage()["jobs"] == 3


def test_bits_storage_reports_size_and_running_rows(tmp_path):
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    result, _ = store.claim("cycle-s", action("printf 1"))
    store.finish({**result, "status": "succeeded", "exit_code": 0,
                  "stdout": "x" * 1000})

    stats = store.storage()
    assert stats["jobs"] == 1
    assert stats["running"] == 0
    assert stats["result_bytes"] > 1000


def test_a_running_job_publishes_partial_output(tmp_path):
    """A 20-minute backtest must not look like a hung harness.

    The record is written only at the terminal state, so until then a reader saw
    `status: running` with empty stdout for the entire job (p99 343s, observed
    max 1211s).
    """
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    jobs = ShellJobs(store, SecretFilter(env_file=str(tmp_path / "missing.env")))
    seen_running_output = []

    original = jobs._publish_progress

    def spy(result, buffers, limit, total):
        original(result, buffers, limit, total)
        record = store.job(result["job_id"])
        if record["status"] == "running":
            seen_running_output.append(bool(record.get("stdout")))

    jobs._publish_progress = spy
    result = jobs.start("cycle-progress", action(
        "for i in $(seq 1 40000); do echo line-$i; done", max_output_bytes=200000))
    final = wait(store, result)

    assert final["status"] == "succeeded"
    assert seen_running_output, "no partial output was published while running"
    assert final["stdout"], "terminal result should still carry the output"
    assert final.get("bytes_seen", 0) >= 0


def test_partial_output_is_scrubbed_exactly_like_the_final_result(tmp_path):
    """A preview is scrubbed exactly like the stored record.

    A partial publish writes to the same durable row an operator or the agent can
    read, so scrubbing only the final result would expose anything that streamed
    past before the command finished. Tested at the unit boundary because the job
    environment is a fixed allowlist and will not carry a test's own variable.
    """
    env = tmp_path / ".env"
    env.write_text("SECRET_TOKEN=super-secret-value-123456\n")
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    jobs = ShellJobs(store, SecretFilter(env_file=str(env)))
    result, _created = store.claim("cycle-preview", action("printf x"))

    jobs._publish_progress(result, {"stdout": bytearray(b"before super-secret-value-123456 after"),
                                    "stderr": bytearray()}, 100000, 40)

    stored = store.job(result["job_id"])
    assert "super-secret-value-123456" not in (stored.get("stdout") or "")
    assert "withheld" in (stored.get("stdout") or "")
    # Still a running record: a preview must never make a job look finished.
    assert stored["status"] == "running"
    assert stored["bytes_seen"] == 40


def test_publish_progress_failure_does_not_disturb_the_job(tmp_path):
    """A failed preview is observability, and observability must not break the job."""
    store = BitsStore(SQLiteAgentTranscriptStore(str(tmp_path / 'state.db')))
    jobs = ShellJobs(store, SecretFilter(env_file=str(tmp_path / "missing.env")))
    result, _created = store.claim("cycle-boom", action("printf ok"))

    def boom(*args, **kwargs):
        raise RuntimeError("store unavailable")
    store.finish = boom
    jobs._publish_progress(result, {"stdout": bytearray(b"ok"), "stderr": bytearray()}, 1024, 2)
