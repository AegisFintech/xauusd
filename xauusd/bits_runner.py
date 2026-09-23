"""Persistent Bits decision/result loop within the existing single agent service."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from threading import Thread
from uuid import uuid4

from .agent_loop import ContinuousAgentRunner, paper_state_tool
from .bits import BitsError, PROTOCOL
from .bits_jobs import BitsStore, ShellJobs, SecretFilter, AgentLock
from .paper_trading import market_is_open
from .bits_memory import BitsMemory, result_for_prompt, excerpt
from .bits_research import RESEARCH_POLICY, guidance_revision, market_research, finish_research_cycle


class BitsAgentRunner(ContinuousAgentRunner):
    def __init__(self, *args, **kwargs):
        transcript = kwargs.get("transcript") or args[2]
        self.lock = AgentLock(transcript)
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
        self.monitor_thread = None
        self.monitor_error = None
        self.workflow_timeout = float(os.getenv("DD_WORKFLOW_TIMEOUT_SECONDS", "300"))
        if not 1 <= self.workflow_timeout <= 3600:
            raise BitsError("invalid workflow timeout")
        interrupted = self.bits_store.recover()
        pending = self.bits_store.get("cycle", {})
        if interrupted or pending.get("phase") == "submitting":
            self.paper_trading.stop("recovery_failed")
            self.bits_store.put("cycle", {"phase": "blocked", "reason": "uncertain interrupted operation"})

    def _record(self, phase, content):
        self.transcript.append(self.run_id, self._tick, phase, self.secrets.clean(content))

    def _outcome(self, status, **extra):
        self._write_status(status, planner="datadog_bits", monitor=self.bits_store.get("monitor"),
                           research_progress=self.bits_store.get("research_progress", {}),
                           next_review_at=self.bits_store.get("cycle", {}).get("next_at"), **extra)
        return {"tick": self._tick, "status": status, **extra}

    def _guidance(self):
        from pathlib import Path
        revision = guidance_revision()
        if revision and self.bits_store.get("guidance_reviewed") != revision:
            return {"revision": revision, "text": Path("AGENTS.md").read_text(),
                    "instruction": "Review these repository rules now; the server remembers successful delivery."}
        return None

    def _context(self, market):
        return {"utc_now": self._now().isoformat(), "market": self._market_view(market),
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
                "tools": [tool for tool in self.registry.definitions()
                          if tool["name"] in {"read_market", "paper_state", "propose_trade"}],
                "execution": "The server harness executes your JSON shell action; do not use Datadog sandbox tools. "
                "The current paper.stopped boolean is authoritative: a historical kill_switch_reason "
                "does not imply an active stop when stopped=false. Never clear a true operator stop. "
                "Run existing trading tools with .venv/bin/python -m xauusd.cli agent-tool TOOL --input 'JSON'. "
                "Available TOOL names and input schemas are in tools. Use propose_trade for every trade; "
                "never bypass the deterministic gates. Shell cwd is /root/xauusd. "
                "Search/download/analysis commands may run directly in shell. Never print .env or secrets. "
                "A shell job is already async: do not daemonize or background commands. "
                "No command allow-list or per-command approval is required. Return strict xauusd/1 JSON. "
                "Maximum one shell action per response; timeout_sec 1..3600, max_output_bytes 1..1048576. "
                "Write summary as a short plain-English decision for the human live view: what you observed, "
                "why the next action is useful, or why you are waiting. No JSON, shell code or internal IDs in summary. "
                "Finish with waiting/completed and a UTC next_review_at when no further action is useful."}

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
        self._record("bits_submit", {"cycle_id": cycle["cycle_id"], "message_id": invocation["message_id"]})
        return self._outcome("bits_waiting")

    def run_tick(self):
        self._tick += 1
        cycle = self.bits_store.get("cycle", {})
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
            if result["status"] == "running":
                return self._outcome("shell_running")
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
                raise BitsError("workflow deadline exceeded; no commands executed")
            reply = self.planner.poll(cycle["instance"], cycle["cycle_id"], cycle["invocation"]["message_id"])
            if reply is None:
                return self._outcome("bits_waiting")
            if self.secrets.unsafe(json.dumps(reply)):
                raise BitsError("agent response contains sensitive content")
            guidance = cycle["invocation"]["context"].get("repository_guidance")
            if guidance:
                self.bits_store.put("guidance_reviewed", guidance["revision"])
            cycle.update(phase="response", reply=reply)
            self.bits_store.put("cycle", cycle)
            self._record("assistant", {"reply": json.dumps(reply), "summary": reply["summary"],
                                       "action": "tool" if reply["actions"] else "final"})
            phase = "response"
        if phase == "response" and not cycle["reply"]["actions"]:
            reply = cycle["reply"]
            requested = datetime.fromisoformat(reply["next_review_at"].replace("Z", "+00:00")) if reply["next_review_at"] else self._now()
            # Bound credit consumption and never suppress reviews indefinitely.
            next_at = min(max(requested, self._now()+timedelta(seconds=60)), self._now()+timedelta(hours=1)).isoformat()
            if self.paper_trading.state().get("position"):
                next_at = min(datetime.fromisoformat(next_at), self._now()+timedelta(seconds=60)).isoformat()
            finish_research_cycle(self.bits_store, cycle["cycle_id"])
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
            action = cycle["reply"]["actions"][0]
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

    def monitor_once(self):
        try:
            market = self.source.read()
            result = self.paper_trading.monitor(float(market.price), market.observed_at, self._now())
        except Exception as exc:
            result = {"status": "unavailable", "error_type": type(exc).__name__}
        self.bits_store.put("monitor", {**result, "recorded_at": self._now().isoformat()})
        if self.paper_trading.state().get("stopped"):
            self.jobs.stop()
        return result

    def _monitor_forever(self):
        while not self._stop.is_set():
            try:
                self.monitor_once()
            except Exception:
                self.monitor_error = "state_monitor_failed"
                try: self.paper_trading.stop("recovery_failed")
                finally: self._stop.set()
            self._stop.wait(5)

    def run_forever(self, stop=None, on_tick=None):
        if stop is not None: self._stop = stop
        self.monitor_thread = Thread(target=self._monitor_forever, daemon=True)
        self.monitor_thread.start()
        try:
            super().run_forever(stop=self._stop, on_tick=on_tick)
        finally:
            self.stop()
