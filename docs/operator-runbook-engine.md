# Operator runbook: engine, live feed, and the visible harness

**Operator-only.** Every command here is an operator action. The agent, the
engine and the live view never execute them, and no code path may perform them
without explicit operator approval (`AGENTS.md`, "Operator-only").

This covers deploying the two new services, publishing the Datadog workflow
change, and restarting the live view so the new observability becomes visible.

---

## 1. What was built and why

The supervised agent ran 6,666 ticks and proposed **zero** trades. Every one of
its 313 tool calls was a shell command; `propose_trade` was never entered once.
Every risk gate would have passed. The model was told repeatedly that waiting was
valid, then wrote its own prohibition into memory ("Remain flat") and re-read it
every cycle.

An LLM round trip measured 22.8s median, 39.3s p90. That is a ceiling of roughly
158 cycles per hour no matter how the review floor is tuned, so execution is now
split:

| Component | Role | Cadence |
| --- | --- | --- |
| `xauusd-data-feed.service` | keeps the M1 store continuously fresh via a live subscription | continuous |
| `xauusd-engine.service` | decides and trades, in code, through the existing risk gates | every closed bar |
| `xauusd-agent.service` | supervises: reviews, questions itself, halts or resumes the engine | 25s–300s |
| `xauusd-agent-view.service` | serves the live harness page | always on |

**The engine has no privilege the agent did not have.** It proposes a decision
and hands it to the same `PaperTrading.evaluate` gate, so the symbol, sizing,
daily-loss, drawdown, exposure, duplicate, freshness, market-hours and
kill-switch gates all apply unchanged.

---

## 2. Publish the Datadog workflow message stream (required for the thinking panel)

Until this is done the "Thinking" panel shows only the terminal summary, because
the current workflow returns only the final `xauusd/1` output. The protocol
validator already accepts the new optional `interrogation` field, and
`xauusd/1` without it still validates, so publishing is backwards compatible.

The workflow's agent must return the intermediate message stream alongside its
output, so `BitsClient.poll` can persist each turn as an `agent_message`
transcript row. Two properties are enforced on our side and will reject a
malformed stream rather than render it:

- each turn is `{role, content}` with `role` in `user|assistant|tool|system`;
- content is truncated to 8,000 characters and the stream to 200 turns.

If the stream is absent the panel degrades to the summary. It never fails a
cycle.

---

## 3. Enable the live data feed

**The feed cannot run yet: the cTrader subscription is not implemented.**
`LiveBarFeed._subscribe` and `LiveBarFeed._discover` in `xauusd/live_feed.py`
raise `LiveFeedUnavailable("live_feed_not_implemented")`; nothing subclasses
`LiveBarFeed`. Everything around them is in place — demo host pin, closed-bar
rule, atomic merge into the shared store, status file, reactor driver — but no
bar can be subscribed, so `data-feed run` exits 1 and writes
`reports/data_feed_status.json` with `state: unavailable`.

Do not `enable --now` this unit until `_subscribe` is implemented. An earlier
revision of this runbook and the unit itself had `Restart=always` against a CLI
that exited 0 on the unimplemented path, so enabling it produced an invisible
infinite restart loop: no status file, no exit code, and `StandardError=null`
so nothing in the journal either. The exit code and status file now make that
failure loud, and the unit is left undeployed in `/etc/systemd/system` until
the subscription exists.

The freshness gate is 180 seconds and the scheduled downloader runs four times a
day, so the newest bar is normally hours old and **every** proposal is refused as
`STALE_MARKET_DATA`. The feed is what makes either the engine or a 3-minute gate
viable, so this is the blocking prerequisite for live engine execution.

Once implemented, deploy with:

```bash
cp deploy/systemd/xauusd-data-feed.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now xauusd-data-feed.service
```

Verify before anything else:

```bash
systemctl is-active xauusd-data-feed.service
.venv/bin/python -m xauusd.cli data-feed status
.venv/bin/python -m xauusd.cli data-feed once   # bounded supervised smoke test
```

Expect `state: ok` and a `last_bar_utc` that advances once a minute while the
market is open. Check the session field: `open`, `daily_break` at 17:00–18:00 New
York, `weekend_closed` otherwise. A feed reporting `weekend_closed` with a stale
bar is **correct**, not broken.

Note that `xauusd/live_feed.py` has no broker-free unit tests for the
subscription, the closed-bar rule or the persistence path, unlike the rest of
the module. Those guards are what stop a late or replayed bar overwriting a
complete one, so they need tests before the feed is trusted with real data.

`/api/health` carries a `data_feed` section, so a deployed feed is visible
without opening the file. It is informational and deliberately does not raise an
alert or change the `ok`/`degraded` verdict, because the feed is not deployed yet
and an absent feed is not a degraded deployment. `data_feed.state` is
`not_deployed` when the status file does not exist, which is how an absent feed
is told apart from one that failed to start.

Requirements: `CTRADER_DEMO_ONLY=true` and the demo host pin are enforced at
startup, exactly as for the execution adapter. The feed refuses any other host.

---

## 4. Enable the deterministic engine

**The engine and the agent are meant to run together.** The engine trades; the
agent supervises. Neither takes the container `AgentLock` — that lock belongs to
the Bits agent runner, `bits-recover` and `state reset`, so a second *agent*
process refuses with `agent_already_running` while the engine is unaffected.
An earlier revision of this runbook claimed the engine also took the lock; it
does not, and following that claim only meant stopping a healthy agent for no
reason.

```bash
cp deploy/systemd/xauusd-engine.service /etc/systemd/system/
systemctl daemon-reload
```

Inspect before starting:

```bash
.venv/bin/python -m xauusd.cli engine status
```

The engine reports its own state and the paper account. Confirm `state: running`
and that `paper.stopped` matches what you intend. **If paper is stopped the
engine will be refused by `KILL_SWITCH` on every bar** — that is the kill switch
working, not an engine fault.

Suggested `.env` additions (operator choice; the defaults are deliberately
conservative):

```
ENGINE_ENABLED=true
ENGINE_QUANTITY=0.1
ENGINE_POLL_SECONDS=5
ENGINE_MAX_BAR_AGE_SECONDS=180
ENGINE_HALT_AFTER_ERRORS=3
ENGINE_STRATEGY=confirmed_breakout
ENGINE_STATUS_PATH=reports/engine_status.json
```

Then:

```bash
systemctl enable --now xauusd-engine.service
.venv/bin/python -m xauusd.cli engine status
```

The engine halts itself after `ENGINE_HALT_AFTER_ERRORS` consecutive internal
failures rather than looping silently. A halt is durable across restarts.

### Engine control

```bash
.venv/bin/python -m xauusd.cli engine halt  --reason "supervisor: edge not justified"
.venv/bin/python -m xauusd.cli engine resume --reason "evidence attached"
```

A halt is **not** a trading stop. It stops deterministic proposals only; paper
trading stays available and the paper kill switch is untouched. The agent can
issue these, which is the point of the split — the model supervises, it does not
decide entries.

---

## 5. Restart the live view so the new observability is visible

The running `xauusd-agent-view.service` started 2026-09-28 and is serving
pre-change code: `/api/health` has no `monitor` or `storage` keys, and `/harness`
does not exist. All of it is invisible until the unit restarts.

```bash
systemctl restart xauusd-agent-view.service
```

Then open:

- `http://127.0.0.1:8100/` — the original compact view, unchanged
- `http://127.0.0.1:8100/harness` — the nof1-style live harness

The harness page shows: the live log (event-streamed), the agent's **Thinking**
panel, the **Deterministic engine** panel with the last gate verdict, the
**Self-review** panel rendering the agent's own question/answer pairs, account
and market state, and the research memory with its `candidates` list.

It is **read-only by construction**. There is no control on that page that can
halt the engine, start or stop paper, or recover a job. Those stay CLI-only.

---

## 6. Resume the agent (only after the feed and engine are verified)

The agent is currently stopped with `recovery_failed` from a shell job that hit
the 20-minute ceiling on 2026-09-29. Follow `docs/agent-recovery-runbook.md` in
full; it has the completed side-effect audit and the refusal table.

```bash
.venv/bin/python -m xauusd.cli state integrity
.venv/bin/python -m xauusd.cli bits-recover --reason "operator: feed and engine verified"
.venv/bin/python -m xauusd.cli paper start
systemctl start xauusd-agent.service
```

---

## 7. Verifying the whole loop

```bash
curl -s localhost:8100/api/health | .venv/bin/python -m json.tool
curl -s localhost:8100/api/harness | .venv/bin/python -m json.tool
.venv/bin/python -m xauusd.cli engine status
.venv/bin/python -m xauusd.cli data-feed status
```

Expect:

- `alerts` free of `paper trading stopped` and `position monitor stale`;
- `harness.engine.state: running` and `data_feed.age_seconds` under 180;
- the harness page showing engine signals and, within a cycle, the agent's
  thinking and self-review.

If the engine is running and the feed is fresh but there is still no trade, that
is **the correct outcome** when no signal qualifies. Check the engine panel for
the gate verdict; `no qualifying signal on this bar` and a specific gate refusal
are both legitimate. Do not lower a risk gate to produce activity.

---

## 8. Refusal and rollback

| Symptom | Cause | Action |
| --- | --- | --- |
| Feed will not start | `CTRADER_DEMO_ONLY` not `true`, or host not the demo host | **Stop.** Fix the flag; never relax the host pin. |
| `agent_already_running` | agent and engine contend for the container lock | **Stop one of them.** The lock is intentional. |
| Engine refuses every bar with `STALE_MARKET_DATA` | feed is not keeping up | Check `data-feed status`; the feed is the prerequisite, not a gate to bypass. |
| Engine refused with `KILL_SWITCH` | paper is stopped | Intended. See `docs/agent-recovery-runbook.md`. |
| `agent status: invalid_site` / auth failure | Datadog credentials or region | Re-check `DD_REGION`, `DD_API_KEY`, `DD_APP_KEY`. |
| `/harness` 404 | view unit serving old code | `systemctl restart xauusd-agent-view.service`. |

To leave the system down, safely:

```bash
systemctl stop xauusd-engine.service
.venv/bin/python -m xauusd.cli paper stop --reason "operator: engine deployment rollback"
```

---

## 9. Related documents

- `docs/agent-recovery-runbook.md` — interrupted-job recovery
- `AGENTS.md` — repository operating rules and the operator-only boundary
- `docs/bits-system-prompt.md` — the agent contract
- `docs/datadog-connection.md` — Bits workflow configuration
