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
