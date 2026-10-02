"""Persistent Bits decision/result loop within the existing single agent service."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from threading import Thread
from uuid import uuid4

from .agent_loop import ContinuousAgentRunner, paper_state_tool, _redact_for_transcript
from .bits import BitsError, PROTOCOL, error_details, message_fingerprint
from .bits_capabilities import (REFRESH_SECONDS, build_manifest, cli_prefix, heartbeat_view, minimal_manifest,
                                 missing_executables, prompt_view, record_observed)
from .bits_jobs import (BitsStore, ShellJobs, SecretFilter, AgentLock, MAX_SHELL_TIMEOUT_SECONDS,
                        STALE_RUNNING_JOB_SECONDS)
from .engine_loop import EngineConfig
from .paper_trading import market_is_open
from .bits_memory import BitsMemory, result_for_prompt, excerpt
from .bits_research import (RESEARCH_POLICY, fills_since, finish_research_cycle,
                           guidance_revision, market_research)


# The ceiling lives with the executor that enforces it; re-exported here because
# the runner is the component that records the effective value in the audit.
SHELL_TIMEOUT_SECONDS = MAX_SHELL_TIMEOUT_SECONDS
CYCLE_PHASES = {"idle", "submitting", "workflow", "response", "job", "feedback", "blocked"}
CAPABILITY_TTL_SECONDS = REFRESH_SECONDS
# Consecutive failed monitor cycles before the risk monitor escalates to a
# persisted `recovery_failed` stop. The monitor is the only independent position
# marker and the only writer of risk-limit stops, so it cannot be allowed to fail
# silently behind a healthy heartbeat.
MONITOR_FAILURE_LIMIT = 3
# Supervision cadence, approved by the operator alongside the engine split. These
# bound how often the LLM *reviews*; they do not bound trade frequency, which the
# engine owns and which is bounded by the M1 bar feed and the paper trade-count
# gate instead. The floor cannot usefully go below the model round trip, so the
# low value is a floor that simply never binds.
SUPERVISION_FLOOR_SECONDS = int(os.getenv("AGENT_SUPERVISION_FLOOR_SECONDS", "300"))
SUPERVISION_FLOOR_WHEN_SIGNALLED_SECONDS = int(
    os.getenv("AGENT_SUPERVISION_FLOOR_SIGNALLED_SECONDS", "25"))
# How recently the engine must have acted for the shorter floor to apply.
ENGINE_ACTIVITY_WINDOW_SECONDS = 300


class BitsAgentRunner(ContinuousAgentRunner):
    def __init__(self, *args, **kwargs):
        transcript = kwargs.get("transcript") or args[2]
        self.lock = AgentLock(transcript)
        self._tick_phase = None
        super().__init__(*args, **kwargs)
        self.bits_store = BitsStore(self.transcript)
        self.secrets = SecretFilter()
        self.memory = BitsMemory(self.bits_store, self.secrets)
        reset = self.bits_store.get("session_reset")
        if reset and not self.bits_store.get("session_start_recorded"):
            self._record("session_start", {"summary": f"Starting a fresh paper session with ${reset['initial_cash']:,.2f}. "
                                          "Previous decisions, trades and working memory have been cleared."})
            self.bits_store.put("session_start_recorded", {"run_id": self.run_id})
        self.jobs = ShellJobs(self.bits_store, self.secrets)
        self._capabilities(force=True)
        # Both stores grew without limit: the transcript gained a heartbeat row
        # per tick and bits_jobs a row per shell action, with no DELETE anywhere.
        # Prune once per process start, outside the tick loop.
        self._prune()
        self.monitor_thread = None
        self.monitor_error = None
        self._monitor_failures = 0
        self.workflow_timeout = float(os.getenv("DD_WORKFLOW_TIMEOUT_SECONDS", "300"))
        if not 1 <= self.workflow_timeout <= 3600:
            raise BitsError("invalid workflow timeout", "invalid_workflow_timeout")
        interrupted = self.bits_store.recover()
        pending = self.bits_store.get("cycle", {})
        if interrupted or pending.get("phase") == "submitting":
            self.paper_trading.stop("recovery_failed")
            self.bits_store.put("cycle", {"phase": "blocked", "reason": "uncertain interrupted operation"})

    def _record(self, phase, content):
        # Bound the durable copy as well as the live view. Without this the Bits
        # path stored the entire shell-job record, whose stdout/stderr may be the
        # full 1 MiB capture: 313 recorded tool results held 1.7 MB with a single
        # row of 135 KB, and `bits-job` reads them straight back. The non-Bits
        # path already applied this limit.
        cleaned = self.secrets.clean(content)
        self.transcript.append(self.run_id, self._tick, phase,
                               _redact_for_transcript(cleaned, self.config.transcript_content_limit))

    def _outcome(self, status, **extra):
        self._write_status(status, planner="datadog_bits", monitor=self.bits_store.get("monitor"),
                           # `monitor_error` used to be assigned and never read by
                           # anything, so a dead risk monitor produced no signal.
                           monitor_error=self.monitor_error,
                           monitor_thread_alive=bool(self.monitor_thread and self.monitor_thread.is_alive()),
                           research_progress=self.bits_store.get("research_progress", {}),
                           memory=self.memory.status(),
                           capabilities=heartbeat_view(self._capabilities()),
                           next_review_at=self.bits_store.get("cycle", {}).get("next_at"), **extra)
        return {"tick": self._tick, "status": status, **extra}

    def _capabilities(self, force=False):
        """Manifest of the shell-job environment, persisted so its facts survive cycles and restarts."""
        stored = self.bits_store.get("capabilities")
        if stored and not force:
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(stored["generated_at"])).total_seconds()
            except (KeyError, TypeError, ValueError):
                age = None
            if age is not None and 0 <= age < CAPABILITY_TTL_SECONDS:
                return stored
        try:
            manifest = build_manifest(observed=self.bits_store.get("observed_executables"))
        except Exception as exc:
            manifest = minimal_manifest(error_details(exc)["error_code"])
        manifest = self.secrets.clean(manifest)
        self.bits_store.put("capabilities", manifest)
        return manifest

    def _observe_job(self, result):
        names = missing_executables(result)
        if names:
            self.bits_store.put("observed_executables",
                                record_observed(self.bits_store.get("observed_executables"), names, result["job_id"]))
            self._capabilities(force=True)

    def _recent_engine_activity(self) -> bool:
        """True when the deterministic engine acted recently.

        Read from the engine's own status file rather than the transcript so the
        supervision cadence does not depend on paging history. A missing or
        unreadable file means "no recent activity", which keeps the longer floor
        rather than assuming the engine is live.
        """
        try:
            from pathlib import Path
            path = Path(EngineConfig.from_env().status_path)
            if not path.is_file():
                return False
            status = json.loads(path.read_text())
            decided = status.get("decided_at") or (status.get("last_decision") or {}).get("decided_at")
            if not decided:
                return False
            age = (self._now() - datetime.fromisoformat(str(decided).replace("Z", "+00:00"))).total_seconds()
            return 0 <= age <= ENGINE_ACTIVITY_WINDOW_SECONDS
        except (OSError, ValueError, TypeError, RuntimeError):
            return False

    def _record_messages(self, cycle, messages):
        """Persist agent turns once each, as the stream grows during a cycle.

        Keyed on a digest of the whole stream, so repeated polls of the same
        in-flight instance do not append duplicates. Nothing is written when the
        workflow publishes no message stream, which is a supported configuration.
        """
        if not messages:
            return
        digest = message_fingerprint(messages)
        if cycle.get("messages_digest") == digest:
            return
        cycle["messages_digest"] = digest
        self.bits_store.put("cycle", cycle)
        self._record("agent_message", {"cycle_id": cycle.get("cycle_id"),
                                       "instance": cycle.get("instance"),
                                       "count": len(messages),
                                       "messages": messages})

    def _prune(self):
        """Bound the durable stores. Never fails a start: growth is not worth a stop."""
        try:
            self.bits_store.prune()
        except Exception as exc:
            self._prune_error = error_details(exc)["error_code"]
        try:
            self.transcript.prune()
        except Exception as exc:
            self._prune_error = error_details(exc)["error_code"]

    def _error_details(self, exc):
        detail = error_details(exc)
        # The phase the tick started in locates the failure (workflow poll, job, submission...).
        if self._tick_phase in CYCLE_PHASES:
            detail["cycle_phase"] = self._tick_phase
        return self.secrets.clean(detail)

    def _guidance(self):
        from pathlib import Path
        revision = guidance_revision()
        if revision and self.bits_store.get("guidance_reviewed") != revision:
            return {"revision": revision, "text": Path("AGENTS.md").read_text(),
                    "instruction": "Review these repository rules now; the server remembers successful delivery."}
        return None

    def _context(self, market):
        cli = cli_prefix()
        capabilities = prompt_view(self._capabilities())
        context = {"utc_now": self._now().isoformat(), "market": self._market_view(market),
                  "paper": paper_state_tool(self.paper_trading).handler({}),
                  "paper_only": self.coordinator.paper_only,
                  "previous_summary": excerpt(self.bits_store.get("last_summary"), 1200),
                  "history": self.memory.context(),
                  "bootstrap": {"reviewed": bool(guidance_revision()) and self.bits_store.get("guidance_reviewed") == guidance_revision()},
                  "repository_guidance": self._guidance(),
                  "research_policy": RESEARCH_POLICY,
                  "research_progress": self.bits_store.get("research_progress", {}),
                  "market_research": market_research(self.source),
                  "session_reset": self.bits_store.get("session_reset"),
                  # canary_signal is advertised deliberately. It is a deterministic,
                  # already-implemented signal that fires ~44 times a day; the agent
                  # previously had no way to read it and could only re-derive one from
                  # scratch each cycle.
                  "tools": [tool for tool in self.registry.definitions()
                            if tool["name"] in {"read_market", "paper_state", "propose_trade", "canary_signal"}],
                  "capabilities": capabilities,
                  "execution": "The server harness executes your JSON shell action; do not use Datadog sandbox tools. "
                  "The current paper.stopped boolean is authoritative: a historical kill_switch_reason "
                  "does not imply an active stop when stopped=false. Never clear a true operator stop. "
                  f"Run existing trading tools with {cli} agent-tool TOOL --input 'JSON'. "
                  f"Run every repository CLI command through {cli}; bare python and standalone "
                  "bits-memory/bits-job executables are not guaranteed to exist in the service shell. "
                  "context.capabilities is computed from the shell-job environment: use the tools it lists "
                  "as available, otherwise their fallbacks; do not retry an executable listed in observed_missing. "
                  "Available TOOL names and input schemas are in tools. Use propose_trade for every trade; "
                  f"never bypass the deterministic gates. Before deriving a signal from scratch, call "
                  f"{cli} agent-tool canary_signal: it is the deterministic confirmed-breakout signal, "
                  "it fires many times a day, and its signal_age_seconds tells you how current it is. "
                  f"A deterministic engine also runs on the market feed; check `{cli} engine status` to see "
                  "whether it is active and what it decided. Shell cwd is " + str(capabilities["cwd"]) + ". "
                  "Search/download/analysis commands may run directly in shell. Never print .env or secrets. "
                  "A shell job is already async: do not daemonize or background commands. "
                  "No command allow-list or per-command approval is required. Return strict xauusd/1 JSON. "
                  "Maximum one shell action per response; set timeout_sec=1200 (20 minutes). "
                  "The harness enforces 1200 seconds for shell jobs regardless of the proposed timeout. "
                  "max_output_bytes 1..1048576. "
                  "Write summary as a short plain-English decision for the human live view: what you observed, "
                  "why the next action is useful, or why you are waiting. No JSON, shell code or internal IDs in summary. "
                  "Finish with waiting/completed and a UTC next_review_at when no further action is useful."}
        repair = self.memory.repair_task()
        if repair:
            context["repair_task"] = repair
        return context

    def _submit(self, cycle, market, results=None):
        if self._stop.is_set():
            return self._outcome("stopped")
        invocation = {"protocol": PROTOCOL, "cycle_id": cycle["cycle_id"], "message_id": uuid4().hex,
                      "goal": self.config.goal, "context": self._context(market),
                      "results": [result_for_prompt(r) for r in results or []],
                      "previous_decision": ({"status": cycle["reply"]["status"],
                                             "summary": excerpt(cycle["reply"]["summary"], 900)}
                                            if cycle.get("reply") else None),
                      "steps_remaining": max(0, self.config.max_steps_per_tick - cycle.get("steps", 0))}
        if invocation["steps_remaining"] == 0:
            invocation["instruction"] = "Cycle action budget exhausted. Return a final summary with actions []."
        invocation = self.secrets.clean(invocation)
        cycle.update(phase="submitting", invocation=invocation, submitted_at=self._now().isoformat())
        self.bits_store.put("cycle", cycle)
        # An ambiguous POST remains 'submitting'; it must not be blindly retried.
        instance = self.planner.submit(invocation)
        cycle.update(phase="workflow", instance=instance)
        self.bits_store.put("cycle", cycle)
        # Persist what the model was actually shown. The invocation is the only
        # record of the context that produced a decision, and it was previously
        # discarded once the POST returned, leaving no way to audit or replay why
        # the agent chose what it chose.
        self._record("bits_submit", {"cycle_id": cycle["cycle_id"], "message_id": invocation["message_id"],
                                     "instance": instance, "goal": invocation["goal"],
                                     "context": self.secrets.clean(invocation["context"]),
                                     "steps_remaining": invocation["steps_remaining"]})
        return self._outcome("bits_waiting")

    def run_tick(self):
        self._tick += 1
        cycle = self.bits_store.get("cycle", {})
        self._tick_phase = cycle.get("phase", "idle")
        if self.paper_trading.state().get("stopped"):
            self.jobs.stop()
            self._stop.set()
            self.transcript.finish_run(self.run_id, "stopped")
            return self._outcome("stopped")
        if cycle.get("phase") in ("blocked", "submitting"):
            self.paper_trading.stop("recovery_failed")
            return self._outcome("recovery_failed")
        try:
            market = self.source.read()
        except Exception:
            if not self._refresh_if_stale(self._tick, 1e12):
                self._stale_ticks += 1
                return self._outcome("stale_data")
            market = self.source.read()
        if market_is_open(self._now()) and self._refresh_if_stale(self._tick, self._age(market)):
            market = self.source.read()
        self._record("tick_start", self._market_view(market))
        phase = cycle.get("phase", "idle")
        # Poll existing jobs/workflows even when markets close; no new action is run.
        if phase == "job":
            result = self.jobs.store.job(cycle["job_id"])
            if result["status"] == "running" and self._running_job_is_stranded(result, cycle):
                # The worker thread is gone but the terminal status was never
                # written. Reporting shell_running forever keeps the heartbeat
                # fresh and alerts nothing, so the whole decision loop stalls
                # silently until the process is restarted.
                result.update(status="unknown", error_code="shell_job_stranded",
                              stderr="shell job exceeded the server timeout with no terminal status; "
                                     "reconcile effects before any retry")
                self.jobs.store.finish(result)
                self.paper_trading.stop("recovery_failed")
                self._record("tool_result", result)
                return self._outcome("recovery_failed")
            if result["status"] == "running":
                return self._outcome("shell_running")
            self._observe_job(result)
            if result["status"] in ("unknown", "cancelled", "timed_out"):
                self.paper_trading.stop("recovery_failed")
                self._record("tool_result", result)
                return self._outcome("recovery_failed")
            self._record("tool_result", result)
            self.memory.remember(cycle["cycle_id"], cycle["reply"], result)
            cycle.update(phase="feedback", results=[result])
            self.bits_store.put("cycle", cycle)
            phase = "feedback"
        if phase == "workflow":
            elapsed = (self._now() - datetime.fromisoformat(cycle["submitted_at"])).total_seconds()
            if elapsed > self.workflow_timeout:
                self.bits_store.put("cycle", {"phase": "idle", "next_at": (self._now()+timedelta(seconds=60)).isoformat()})
                raise BitsError("workflow deadline exceeded; no commands executed", "workflow_deadline_exceeded")
            reply, messages = self.planner.poll(cycle["instance"], cycle["cycle_id"],
                                                cycle["invocation"]["message_id"])
            # Persist intermediate agent turns on every poll, not just the terminal
            # one, so the live view can show the model thinking while it is still
            # running. Previously a cycle showed nothing for the length of a model
            # round trip (22.8s median) and then only a ~200-character summary.
            self._record_messages(cycle, messages)
            if reply is None:
                return self._outcome("bits_waiting")
            if self.secrets.unsafe(json.dumps(reply)):
                raise BitsError("agent response contains sensitive content", "sensitive_response")
            guidance = cycle["invocation"]["context"].get("repository_guidance")
            if guidance:
                self.bits_store.put("guidance_reviewed", guidance["revision"])
            cycle.update(phase="response", reply=reply)
            self.bits_store.put("cycle", cycle)
            self._record("assistant", {"reply": json.dumps(reply), "summary": reply["summary"],
                                       "action": "tool" if reply["actions"] else "final"})
            if reply.get("interrogation"):
                # The agent's own question-and-answer about its decision, in order.
                # Persisted separately so the live view can render it as a
                # dialogue rather than as one more blob inside the envelope.
                self._record("interrogation", {"pairs": reply["interrogation"],
                                              "summary": reply["summary"],
                                              "action": "tool" if reply["actions"] else "final"})
            phase = "response"
        if phase == "response" and not cycle["reply"]["actions"]:
            reply = cycle["reply"]
            requested = datetime.fromisoformat(reply["next_review_at"].replace("Z", "+00:00")) if reply["next_review_at"] else self._now()
            # Bound credit consumption and never suppress reviews indefinitely.
            #
            # The floor is a *supervision* cadence, not a trading one. Trade
            # frequency is the engine's, at bar cadence; the LLM reviews on this
            # schedule. With a flat account and a recently changed bar the floor
            # drops to AGENT_SUPERVISION_FLOOR_SECONDS so a new signal is reviewed
            # promptly instead of up to a minute later. It never drops below the
            # model round trip, which is 22.8s median: polling faster would spend
            # credits re-reading the same state, not gain information.
            floor = timedelta(seconds=min(SUPERVISION_FLOOR_SECONDS,
                                          SUPERVISION_FLOOR_WHEN_SIGNALLED_SECONDS))
            if self._recent_engine_activity():
                floor = timedelta(seconds=SUPERVISION_FLOOR_WHEN_SIGNALLED_SECONDS)
            next_at = min(max(requested, self._now()+floor), self._now()+timedelta(hours=1)).isoformat()
            if self.paper_trading.state().get("position"):
                next_at = min(datetime.fromisoformat(next_at), self._now()+floor).isoformat()
            finish_research_cycle(self.bits_store, cycle["cycle_id"],
                                  filled=fills_since(self.bits_store, self.paper_trading))
            self.bits_store.put("last_summary", reply["summary"])
            self.memory.remember(cycle["cycle_id"], reply)
            self.bits_store.put("cycle", {"phase": "idle", "next_at": next_at})
            self._record("tick_end", {"summary": reply["summary"], "steps": cycle["steps"]})
            self.consecutive_errors = 0
            return self._outcome("bits_blocked" if reply["status"] == "blocked" else "completed")
        if not market_is_open(self._now()):
            return self._outcome("market_closed")
        if self._age(market) > self.config.max_market_data_age_seconds:
            self._stale_ticks += 1
            return self._outcome("stale_data")
        self._stale_ticks = 0
        if phase == "response":
            if self._stop.is_set():
                return self._outcome("stopped")
            # Old analysis is discarded across long pauses; do not execute delayed commands.
            age = (self._now() - datetime.fromisoformat(cycle["submitted_at"])).total_seconds()
            if cycle["steps"] >= self.config.max_steps_per_tick or age > self.config.max_market_data_age_seconds:
                self.bits_store.put("cycle", {"phase": "idle"})
                self._record("tick_end", {"summary": "action not executed: budget or response age limit"})
                return self._outcome("step_limit")
            proposed = cycle["reply"]["actions"][0]
            action = {**proposed, "args": {**proposed["args"], "timeout_sec": SHELL_TIMEOUT_SECONDS}}
            self._record("tool_call", {"tool": "shell", "input": action["args"],
                                       "description": cycle["reply"]["summary"]})
            result = self.jobs.start(cycle["cycle_id"], action)
            cycle.update(phase="job", job_id=result["job_id"], steps=cycle["steps"]+1)
            self.bits_store.put("cycle", cycle)
            return self._outcome("shell_running")
        if phase == "feedback":
            return self._submit(cycle, market, cycle["results"])
        if cycle.get("next_at") and self._now() < datetime.fromisoformat(cycle["next_at"].replace("Z", "+00:00")):
            return self._outcome("waiting")
        return self._submit({"cycle_id": uuid4().hex, "steps": 0}, market)

    def stop(self):
        self._stop.set()
        self.jobs.stop()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        super().stop()
        self.lock.close()

    def _running_job_is_stranded(self, result, cycle) -> bool:
        """A "running" job older than the executor's own ceiling cannot be alive."""
        claimed = cycle.get("submitted_at") or cycle.get("started_at")
        try:
            moment = datetime.fromisoformat(str(claimed).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            # No usable start time: fall back to the ceiling from now, so a
            # malformed record still resolves instead of looping forever.
            return False
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return (self._now() - moment).total_seconds() > STALE_RUNNING_JOB_SECONDS

    def monitor_once(self):
        try:
            market = self.source.read()
            result = self.paper_trading.monitor(float(market.price), market.observed_at, self._now())
        except Exception as exc:
            result = {"status": "unavailable", "error_type": type(exc).__name__,
                      "error_code": error_details(exc)["error_code"]}
            self.monitor_error = result["error_code"]
            self._monitor_failures += 1
        else:
            self.monitor_failures = 0
        self.bits_store.put("monitor", {**result, "recorded_at": self._now().isoformat()})
        # A monitor that cannot reach the store is not a transient blip: it is the
        # only independent position marker and the only writer of risk_limit stops.
        # Escalate instead of retrying forever behind a healthy heartbeat.
        if self._monitor_failures >= MONITOR_FAILURE_LIMIT:
            self.monitor_error = self.monitor_error or "state_monitor_failed"
            try:
                self.paper_trading.stop("recovery_failed")
            finally:
                self._stop.set()
            return {**result, "status": "unavailable", "escalated": "recovery_failed"}
        if self.paper_trading.state().get("stopped"):
            self.jobs.stop()
        return result

    def _monitor_forever(self):
        while not self._stop.is_set():
            try:
                self.monitor_once()
            except Exception as exc:
                self.monitor_error = "state_monitor_failed"
                self._monitor_failures += 1
                if self._monitor_failures >= MONITOR_FAILURE_LIMIT:
                    try: self.paper_trading.stop("recovery_failed")
                    finally: self._stop.set()
                    return
            self._stop.wait(5)

    def run_forever(self, stop=None, on_tick=None):
        if stop is not None: self._stop = stop
        self.monitor_thread = Thread(target=self._monitor_forever, daemon=True)
        self.monitor_thread.start()
        try:
            super().run_forever(stop=self._stop, on_tick=on_tick)
        finally:
            self.stop()
