# Agent recovery runbook

**Operator-only.** Every command in this file is an operator action. The agent,
the live view and the CLI never execute them autonomously, and no code path in
this repository may perform them without explicit operator approval
(`AGENTS.md`, "Operator-only" section).

This runbook covers the current stopped deployment: the agent process is down
with a persisted `recovery_failed` kill switch, and `bits-recover` / `paper start`
/ unit restart are pending operator action.

---

## 1. Current state (as recorded in the state store)

| Item | Value |
| --- | --- |
| `xauusd-agent.service` | `inactive`, `enabled` |
| `xauusd-data-update.timer` | `active` — last run `2026-09-30T04:06:28Z`, `state: ok` |
| `xauusd-state-backup.timer` | `active` |
| Paper kill switch | `stopped: true`, `kill_switch_reason: "recovery_failed"` |
| Paper position / cash | `0.0` / `100000.0`, ledger empty (0 entries) |
| Last successful tick | `2026-09-29T04:08:18Z`, tick `6666`, `status: "stopped"` |
| Persisted Bits cycle | `cycle_id 615b36431a084ee4b7d9cf0ec45757e6`, `phase: "job"`, `job_id bc7ead579c304b26961ffb4af93d8c5f` |

### Why it stopped

The shell action `test-lbma-auction-reversal` reached the server-enforced
1200-second limit. `bits_jobs` recorded `status: "timed_out"`, `exit_code: -9`
(SIGKILL to the process group). The runner treats an uncertain or timed-out
shell outcome as a fail-closed condition and persists `recovery_failed`
(`xauusd/bits_runner.py:195-198`). The service then exited 0, so
`Restart=on-failure` correctly did not re-attempt. Paper stayed stopped.

## 2. Side-effect audit (required before recovery)

The rule is: **never replay a job with an unknown outcome.** Inspect what the
interrupted job touched first. For this event the audit is already complete and
is recorded here so the operator can re-verify it cheaply.

The interrupted command was a read-only research script. It wrote exactly one
file and nothing else:

```
reports/research/lbma_auction_reversal_prereg_20260929T034757Z.json   PRESENT (1872 B)
reports/research/lbma_auction_reversal_result_20260929T034757Z.json   ABSENT
```

Verified as **not** touched:

- Paper ledger: 0 entries, `position: 0.0`, `cash: 100000.0` unchanged.
- `paper_trading_decisions`: no row for this job.
- Broker: never contacted — cTrader execution is disabled (`CTRADER_PAPER_ONLY=true`)
  and the job ran no order path.
- `.env`: untouched (`total_bytes: 0`; the script only read market data).

Re-verify with:

```bash
.venv/bin/python - <<'PY'
import sqlite3, json
db = sqlite3.connect('file:state/xauusd_local.db?mode=ro', uri=True)
db.row_factory = sqlite3.Row
row = db.execute("select state_json from paper_trading_state where state_key='primary'").fetchone()
state = json.loads(row['state_json'])
print('position   :', state['position'])
print('cash       :', state['cash'])
print('ledger     :', len(state.get('ledger', [])), 'entries')
print('decisions  :', db.execute('select count(*) from paper_trading_decisions').fetchone()[0])
PY
```

Expected: `position 0.0`, `cash 100000.0`, `ledger 0 entries`.

The orphan `*_prereg_*.json` is expected and harmless — a preregistration with no
result is the correct record of a preregistered hypothesis that was never
tested. Leave it in place. The agent's research-continuity rules treat the
missing result as "untested", not "failed", and the next cycle may legitimately
re-run it.

## 3. Integrity pre-flight

Run this **before** `bits-recover`. It is read-only.

```bash
.venv/bin/python -m xauusd.cli state integrity
.venv/bin/python -m xauusd.cli state backup
```

`state backup` performs a verified `quick_check`, writes a gzip archive and a
sha256 sidecar into `backups/local-state/`, and refuses to write an archive that
does not verify. If this command fails, **stop** — the state store is not
healthy and recovery must not proceed.

## 4. Recovery sequence

Run in this order. Each step is a gate: do not continue if one fails.

```bash
# 4.1 Reconcile the interrupted job. This is operator-only.
.venv/bin/python -m xauusd.cli bits-recover --reason "operator recovery: lbma auction shell job timed out, side effects audited"
```

`bits-recover` clears the pending-workflow / in-flight-job records that would
otherwise make `maybe_resume` refuse. It does **not** start paper.

```bash
# 4.2 Confirm the state before starting.
.venv/bin/python -m xauusd.cli paper status
```

Expect `stopped: true` and `kill_switch_reason: "recovered"`. Confirm the
`recovery_failed` reason is gone and the market is open.

```bash
# 4.3 Clear the paper kill switch. This is operator-only.
.venv/bin/python -m xauusd.cli paper start
```

```bash
# 4.4 Start the agent. This is operator-only.
systemctl start xauusd-agent.service
```

## 5. Post-recovery verification

Give the agent one full tick cadence (`AGENT_POLL_SECONDS`, default 20 s) plus
one monitor cycle before judging it.

```bash
# Heartbeat must advance and report a healthy/degraded status with the
# expected single alert cleared.
.venv/bin/python -m xauusd.cli agent status
```

Confirm:

- `runs[0].ticks` increases and `runs[0].status` becomes `running`.
- `status_file.last_tick_status` is no longer `stopped` and `status_file.tick` advances.
- `paper.stopped` is `false` and `kill_switch_reason` is no longer `recovery_failed`.
- `status_file.kill_switch_reason` is absent.

Then confirm the live view health endpoint, the designated observability surface,
agrees:

```bash
curl -s localhost:8100/api/health | .venv/bin/python -m json.tool
```

Expect `alerts` to no longer contain `paper trading stopped`, and
`database.integrity` to be `ok`.

Then read one research cycle from the live view and confirm the pending
`lbma_auction_reversal` preregistration is handled as untested rather than
silently retried with the same parameters.

Then read one research cycle from the live view and confirm the pending
`lbma_auction_reversal` preregistration is handled as untested rather than
silently retried with the same parameters.

## 6. Refusal and rollback

If `bits-recover` or `paper start` refuses, **do not force it.** A refusal writes
`reports/agent_status.json` and exits 0 deliberately. Read the recorded
`kill_switch_reason` and resolve the specific condition:

| Refusal reason | Meaning | Operator action |
| --- | --- | --- |
| `recovery_failed` still set | Interrupted job not reconciled | Re-run 4.1; confirm the cycle record is gone |
| `corrupt_state` | Paper state failed validation | **Stop.** Inspect `state_json`; restore from a verified backup (`state restore`) rather than editing by hand |
| `missing_credentials` | Planner or cTrader credentials unusable | Re-issue tokens; see `docs/datadog-connection.md` |
| `risk_limit` | Daily-loss or drawdown limit reached | **Stop.** Do not clear a risk stop to resume |
| `reconciliation_failed` (demo) | Paper/broker exposure mismatch | **Stop.** Requires manual reconciliation; never auto-cleared |

To abandon recovery and leave the system down:

```bash
.venv/bin/python -m xauusd.cli paper stop --reason "operator: recovery abandoned"
systemctl stop xauusd-agent.service
```

`paper stop` is the only supported way to keep the agent down across restarts.
It is fail-closed: the next boot consults `restart_policy` and refuses to resume
any reason other than `missing_state`.

## 7. Related documents

- `AGENTS.md` — repository operating rules and the operator-only boundary
- `docs/local-handoff-audit-2026-09-24.md` — prior audit of the same deployment
- `docs/activation-2026-09-28.md` — the activation this recovery follows
- `docs/bits-system-prompt.md` — the agent contract that defines `recovery_failed`
