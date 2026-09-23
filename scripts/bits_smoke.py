"""Two-invocation, no-trading smoke test of Bits -> shell -> Bits.

Run from the repository: .venv/bin/python scripts/bits_smoke.py
Consumes two workflow executions. It never touches the trading state database.
"""
from pathlib import Path
import sys
import tempfile
import time
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from xauusd.bits import BitsClient, BitsError
from xauusd.bits_jobs import BitsStore, ShellJobs
from xauusd.local_state import SQLiteAgentTranscriptStore


def main():
    load_dotenv(".env")
    client = BitsClient.from_env()
    cycle = uuid4().hex

    def call(payload):
        invocation = dict(protocol="xauusd/1", cycle_id=cycle, message_id=uuid4().hex, **payload)
        instance = client.submit(invocation)
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            reply = client.poll(instance, cycle, invocation["message_id"])
            if reply is not None: return reply
            time.sleep(2)
        raise BitsError("smoke workflow deadline exceeded")

    reply = call({"instruction": "Connectivity test. The server executes your JSON shell action. "
                  "Do not use Datadog tools. Request exactly command printf 42, cwd /root/xauusd, "
                  "timeout_sec 10, max_output_bytes 1024, in one xauusd/1 action_required envelope. "
                  "No trading, credential reads or other changes."})
    if len(reply["actions"]) != 1 or reply["actions"][0]["args"] != dict(
            command="printf 42", cwd="/root/xauusd", timeout_sec=10, max_output_bytes=1024):
        raise BitsError("unexpected smoke action; not executed")
    with tempfile.TemporaryDirectory(prefix="bits-smoke-") as directory:
        store = BitsStore(SQLiteAgentTranscriptStore(str(Path(directory)/"state.db")))
        jobs = ShellJobs(store)
        try:
            job = jobs.start(cycle, reply["actions"][0])
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                result = store.job(job["job_id"])
                if result["status"] != "running": break
                time.sleep(.1)
            if result["status"] != "succeeded" or result["stdout"] != "42":
                raise BitsError("smoke shell result mismatch")
            final = call({"results": [result], "instruction": "Connectivity test finished. "
                          "Acknowledge stdout 42 and exit_code 0. Return completed envelope with "
                          "actions [], null next_review_at and blocker. No tools or commands."})
            if final["status"] != "completed" or final["actions"]:
                raise BitsError("smoke feedback mismatch")
            print("PASS: Bits command -> local shell -> Bits acknowledgement")
        finally:
            jobs.stop()


if __name__ == "__main__":
    try: main()
    except Exception as exc:
        print("FAIL: " + type(exc).__name__)
        raise SystemExit(1) from None
