# XAUUSD Autonomous Research and Demo Harness

An auditable XAUUSD research system being extended with an autonomous AI harness and cTrader **demo-account-only** automation. It uses reproducible historical research, deterministic risk controls, and persistent operational state. It makes no profitability claim.

## Current Status

- Historical cTrader Open API acquisition, reproducible datasets, backtesting, validation, experiment registry, and read-only dashboard are implemented.
- Shadow observation mode persists signals and an emergency stop without broker execution.
- The autonomous AI harness, Firecrawl research ingestion, paper lifecycle, and a fail-closed demo execution adapter are implemented. Live execution is not.
- No real-money execution is supported or approved.

## Architecture

```text
market data + paper state -> Datadog workflow -> Bits xauusd/1 JSON
           ^                                      |
           |                                      v
           +-------- persisted results <- arbitrary shell jobs
                                                  |
                                    existing gated trading CLI
                                                  |
                                     paper / cTrader demo adapter
```

Bits selects arbitrary shell commands in the user-authorized container. The
execution wrapper persists intent, bounds runtime/output, and suppresses detected
secrets. It is not a security sandbox: arbitrary shell access can alter local
code and controls. The agent is instructed to use the existing deterministic
trade interface and never bypass demo-only restrictions or risk gates.

## Demo-Only Controls

The cTrader demo adapter requires all of the following before it can send a request:

- `CTRADER_DEMO_ONLY=true`
- cTrader host exactly `demo.ctraderapi.com`
- verified demo account metadata and the configured XAUUSD symbol
- successful account and pending-order reconciliation after restart; only a fresh (never-stopped) execution switch starts automatically, every persisted stop needs `demo-automation start --reason ...`
- fresh market data and a healthy state store
- a clear persistent kill switch
- deterministic risk and idempotency checks

On uncertainty, restart recovery failure, data staleness, or API failure, the system will stop and alert rather than act. A broker error reply is recorded as `BROKER_REJECTED`. A transport failure or timeout after sending is recorded as `OUTCOME_UNKNOWN`, because the order may still have executed. Either one stops paper (`broker_execution_failed`) and demo execution, and neither switch resumes on its own. Check the account's broker positions before restarting.

## Configuration

Credentials belong in `.env` with mode `0600`; never commit them. Current historical-data settings and the demo-only assertion are documented in `.env.example`.

`.env.sample` links to `.env.example`. Set `AGENT_PLANNER=datadog` and the `DD_*` settings to use the Bits workflow. See
[Datadog connection status](docs/datadog-connection.md) for the verified invocation
path, protocol, recovery, and deployment checks. The ready-to-paste
[Bits system prompt](docs/bits-system-prompt.md) defines the server-executed JSON contract.

## Demo Automation

`demo-automation` is explicit and defaults to a no-network status check. It uses only the local normalized M1 data file, the fixed confirmed-breakout canary, CockroachDB paper/demo state, and the demo-only cTrader adapter.

```bash
.venv/bin/python -m xauusd.cli demo-automation status
.venv/bin/python -m xauusd.cli demo-automation once
.venv/bin/python -m xauusd.cli demo-automation run
.venv/bin/python -m xauusd.cli demo-automation start --reason 'broker exposure checked'  # explicit override
```

`once` and `run` do nothing beyond returning disabled status unless `CTRADER_AUTOMATION_ENABLED=true`. When enabled, they require `CTRADER_DEMO_ONLY=true`, the demo cTrader settings, `DATABASE_URL`, and a positive integer `CTRADER_VOLUME_PER_PAPER_UNIT`. Set paper risk limits and the canary quantity explicitly in `.env`; `status` never opens a database or broker connection.

On start, `once` and `run` apply the same restart policy as the agent to both kill switches. They reconcile and then start only a fresh account. If either the paper or the demo execution switch holds a persisted stop (operator, risk limit, broker/transport/reconciliation failure, corrupt state), the runner does not reconcile or clear anything. It records `resume_refused` with the blocking switch and reason in `reports/demo_runner_status.json` and exits. Clear the paper switch with `paper start` and the demo execution switch with `demo-automation start --reason ...`, which reconciles first and changes nothing if reconciliation fails.

A broker-free **paper-only** stage runs the deterministic paper pipeline without any cTrader credentials or volumes: set `CTRADER_PAPER_ONLY=true` and `CTRADER_AUTOMATION_ENABLED=true` (the cTrader demo settings become unnecessary). It exercises the same paper risk, idempotency, and decision records, records `PAPER_ONLY_MODE` for the demo leg, and never touches a kill switch beyond the paper lifecycle.

## Market Data & Authentication

Historical and live M1 data is fetched through the cTrader Open API demo host (`demo.ctraderapi.com`, read-only) and normalized into `data/processed/XAUUSD_M1.parquet` by:

```bash
.venv/bin/python -m xauusd.cli data download --start 2026-09-17   # backfill a window
.venv/bin/python -m xauusd.cli data update                        # catch up to now
.venv/bin/python -m xauusd.cli data validate                      # report rows/gaps
```

Credentials are an **OAuth2 token pair** (`CTRADER_ACCESS_TOKEN`, `CTRADER_REFRESH_TOKEN`) minted once through the cTrader ID granting-access flow (`xauusd.oauth.authorize_url` → `/apps/token`). With `CTRADER_CTID_TRADER_ACCOUNT_ID` left empty, both the data downloader and the demo execution adapter auto-discover the demo account and its XAUUSD symbol from the token (`ProtoOAGetAccountListByAccessTokenReq`); set the explicit id to pin a specific account (legacy leaf-token mode). On a `CH_ACCESS_TOKEN_INVALID`, `data update/download` refresh via `grant_type=refresh_token` once and atomically rewrite only the two token keys in `.env` (`0o600`) — nothing is ever logged. Both paths require `CTRADER_DEMO_ONLY=true`.

Every `data update/download` run records `reports/data_update_status.json` (`state: ok | auth_error | failed`, `error_code`, `recorded_at`, `end`), surfaced by the live view at `/api/data-update`, so timer failures are loud instead of silent `exit-code` entries. The `xauusd-data-update.timer` re-enables scheduled 6-hourly refreshes.

## Autonomous Agent

`agent` runs one continuously trading AI plan-tool loop whose thinking is visible in a live web view. It is paper-first and reads `DD_*` and `AGENT_*` settings. The workflow returns one correlated `xauusd/1` envelope per invocation.

```bash
.venv/bin/python -m xauusd.cli agent status   # paper + recent transcript runs, no network
.venv/bin/python -m xauusd.cli agent once     # a single tick, then exit
.venv/bin/python -m xauusd.cli agent run      # continuous loop (view is a separate service)
.venv/bin/python -m xauusd.cli agent view     # live view only
```

The paper lifecycle and local state store have their own explicit commands:

```bash
.venv/bin/python -m xauusd.cli paper status   # kill-switch state, position, equity, recent fills
.venv/bin/python -m xauusd.cli paper stop     # persistent kill switch (reason defaults to operator)
.venv/bin/python -m xauusd.cli paper start    # explicit override (requires a reason)
.venv/bin/python -m xauusd.cli state integrity  # quick_check on paper + transcript DB
.venv/bin/python -m xauusd.cli state backup --root backups/local-state   # gzip + sha256 snapshot
.venv/bin/python -m xauusd.cli state restore --backup <dir|state.db.gz>  # verified restore
```

`paper stop` persists a kill switch across restarts, whatever `--reason` it is given, and neither the agent nor `demo-automation` auto-resumes it; `paper start` is the explicit override. `state backup` snapshots the live SQLite file (verifies it with `quick_check`, gzips it, records a sha256 in a manifest), and `state restore` refuses any archive whose checksum or database integrity does not verify. A daily `xauusd-state-backup.timer` (midnight + randomized delay) keeps one verified snapshot per day under `backups/local-state`.

The Bits loop persists its workflow instance, cycle IDs, shell jobs, and results
in the selected state database. It polls an outstanding workflow after restart
instead of submitting it again. Shell commands can invoke the deterministic tools:

```bash
.venv/bin/python -m xauusd.cli agent-tool read_market
.venv/bin/python -m xauusd.cli agent-tool paper_state
# propose_trade accepts side, quantity, and reason in --input JSON.
```

The `propose_trade` tool preserves the existing risk gates. The agent transcript
records sanitized decisions and command results. An independent monitor marks
fresh paper prices every five seconds and persists a `risk_limit` stop if daily
loss or drawdown is breached; it does not liquidate positions or place orders.
Uncertain, timed-out or interrupted commands require operator reconciliation:

```bash
.venv/bin/python -m xauusd.cli paper stop
# Reconcile external side effects first and ensure the agent service has exited.
.venv/bin/python -m xauusd.cli bits-recover --reason 'effects checked and reconciled'
.venv/bin/python -m xauusd.cli paper start --reason operator_reconciled
systemctl restart xauusd-agent.service
```

`agent once` advances one state-machine step and exits; use the service for complete
cycles. Do not run it concurrently with the service. Shell timeouts are 1–3600s,
output limits 1–1048576 bytes, and truncation is explicit. Keep large results in
files and request smaller selections. Completed cycles wait at least 60 seconds;
open positions cap requested review delays at 60 seconds, otherwise at one hour.


Paper account and transcript state live in a **local SQLite file** (`STATE_DB_PATH`, default `state/xauusd_local.db`) by default, so the running agent needs no external database or `DATABASE_URL`. Set `XAUUSD_STATE_BACKEND=cockroach` to return to the Cockroach-backed stores. The view serves the same transcript and paper endpoints from this store.

The view listens on `AGENT_VIEW_PORT` (default `8100`). It shows the transcript newest-first with the AI's plain-English reasons, a paper-account strip (equity, position, day/realized P&L, drawdown, recent fills from `/api/paper`), and a recent-runs line with per-run tick counts and duration. Times render in GMT+8, labelled `+08:00`; that is display-only — persisted timestamps and bar indices stay UTC, and the market-hours gate compares instants against the New York session. Each `agent_<uuid12>` is one process start: a graceful SIGTERM marks the old run stopped, so a restart cadence legitimately produces many short "runs" — this is one process, not many agents.

`agent run` and `agent once` are inert unless `CTRADER_AUTOMATION_ENABLED=true`. On every launch the agent verifies database integrity and then consults the paper kill switch. It continues a running account and starts a fresh one, but any persisted stop stays stopped (fail closed) until `paper start`. That covers `paper stop` with any reason, corrupt state, missing credentials, an unknown account type, a failed recovery, a risk limit, and a broker failure. Each tick also writes a heartbeat to `AGENT_STATUS_FILE` (default `reports/agent_status.json`); the live view's `/api/health` turns that heartbeat, stall/error counts, consecutive ticks that never reached the planner, paper-stop state, and data-update failures into a healthy/degraded status with `alerts`.

Each tick records market `fresh`/`age_seconds`/`market_open` on `tick_start`, so a stale or closed-market feed is always visible in the transcript as "no trade". `age_seconds` counts from when the newest M1 bar **closed**, not from its open timestamp: persisted bars are stamped at bar open, so an open-based age is intrinsically 60-120s and any gate tighter than that can never pass — the loop would report `stale_data` forever while the feed looked healthy. `AGENT_MAX_MARKET_DATA_AGE_SECONDS`, `PAPER_MAX_MARKET_DATA_AGE_SECONDS`, and `CTRADER_AUTOMATION_MAX_MARKET_DATA_AGE_SECONDS` share that close-based semantic (default 180s, three bars); keep them consistent or proposals are refused as `STALE_MARKET_DATA`. **When XAUUSD is not trading (weekends, and the daily 17:00-18:00 New York break), the deterministic paper gate refuses every proposal with `MARKET_CLOSED` — the agent never trades a closed market.** The session follows New York time, so in UTC the break is 21:00-22:00 during US daylight time and 22:00-23:00 in winter (first Sunday of November to second Sunday of March), and the weekly close and open move by the same hour. Exchange holidays are not modelled; the freshness gates refuse trading when no new bars arrive. Optionally set `AGENT_DATA_REFRESH_ENABLED=true` to let a stale tick refresh the local M1 parquet in-loop before the planner reasons (bounded by `AGENT_DATA_REFRESH_*`; still gated by the paper freshness and market-hours checks).

To run the agent as a persistent background service (paper-only, live view on `http://127.0.0.1:8100/`):

```bash
sudo cp deploy/systemd/xauusd-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now xauusd-agent.service
```

The view runs in its own `xauusd-agent-view.service`. Use `/api/paper`, `/api/runs`,
the transcript, and `/api/health` to confirm activity.

The agent reads `.env` through `EnvironmentFile`. Configure `AGENT_PLANNER=datadog`,
`DD_REGION`, `DD_API_KEY`, `DD_APP_KEY`, `DD_AGENT_ID`, `DD_BITS_WORKFLOW_ID`,
`CTRADER_AUTOMATION_ENABLED=true`, and the selected paper/state settings.
`CTRADER_PAPER_ONLY=true` keeps broker orders disabled. Data refresh uses the
cTrader demo OAuth credentials and downloads an initial seven days if no local
file exists. Restart the service after configuration changes. Graceful termination
cancels shell process groups and leaves pending workflow IDs available for restart.

The former OpenAI endpoint and credentials have been removed from the deployment
and template. Legacy `AGENT_PLANNER=openai` code remains for compatibility tests;
using it requires independently configuring its `OPENAI_*` settings.

The service writes no console or journald logs; the transcript, state store, and the live view (including `/api/health` at `http://127.0.0.1:8100/api/health`) are the only observability.

## Live history and session reset

The activity feed shows plain-English decisions and keeps tool calls visible.
Open a `>` Details disclosure for commands, output, errors and raw JSON. The
protocol used for execution remains unchanged. Bits receives bounded recent
history and source-linked working memory; see [memory details](docs/datadog-connection.md#history-and-readable-activity).

For an explicitly requested fresh local paper session, stop the paper account
and agent service, then run `state reset --confirm-reset`. This verifies a backup
and atomically clears paper fills/decisions, agent runs/transcripts, Bits jobs,
cycle state and memory. It resets cash to `PAPER_INITIAL_CASH` (default $100,000)
and leaves the account stopped. Market data, credentials and research tables are
preserved. Explicitly `paper start --reason operator_reset`, then restart the
agent service. Reset is refused unless `CTRADER_PAPER_ONLY=true` and no Bits agent
holds the local runtime lock. Never use a reset to hide or bypass a risk stop.

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests -q -p no:cacheprovider
git diff --check
```

An unscoped `pytest` from the repo root hangs while collecting `reports/` and `data/`; always scope it to `tests`.

## Demo Automation Service

Deployment templates under `deploy/systemd/` cover the Bits agent, live view, data update, state backup, and optional demo automation. Legacy host-only units remain installed but disabled; see [the local handoff audit](docs/local-handoff-audit-2026-09-24.md) for the inventory. The demo template grants write access to `reports/` and the default SQLite `state/` directory. A custom database path requires an explicit unit-path review before deployment.

The service is deliberately disabled by default. It exits without broker activity unless `.env` sets `CTRADER_AUTOMATION_ENABLED=true`; it requires a successful demo reconciliation, fresh M1 data, a confirmed-breakout transition, and all paper risk gates. A persisted paper or demo stop makes it record `resume_refused` and exit cleanly on every restart until the matching explicit start. Install and enable it only after a validated demo canary:

```bash
sudo cp deploy/systemd/xauusd-demo-automation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now xauusd-demo-automation.service
```

## Delivery Stages

1. Autonomous planning harness with persistent runs, tool controls, and audit records.
2. Firecrawl source ingestion with provenance and prompt-injection isolation.
3. Deterministic paper trading, risk gates, notifications, and restart recovery.
4. cTrader demo-only adapter, persistent idempotency, and sandbox integration tests.
5. Limited demo canary followed by continuous demo operation only after all gates pass.

See `AGENTS.md` for repository operating rules and `docs/ARCHITECTURE.md` for the existing research platform.


### Research continuity and output retrieval

Bits receives repository rules once per revision (delivery is acknowledged by a
successful correlated response), persistent research guidance, and descriptive
15/60/240-bar close summaries with actual window timestamps. These observations
are not trade signals or evidence of profitability. The agent should run concrete
cost-aware experiments and save source-linked notes before waiting on measurable
conditions. Arbitrary shell access and deterministic trading gates are unchanged.

Stored-output pages are unwrapped before prompt compression, retaining the original
job ID and correct next offset. Follow that cursor instead of paging retrieval jobs.
The health dashboard flags three completed cycles without changed research notes.
This is a transparent progress proxy: no trade or unchanged notes alone does not
prove analytical failure. Updating only a note timestamp does not clear the count.

Use `bits-memory show --notes-only` to retrieve research notes without duplicating conversation history.

Bits shell jobs use a server-enforced 1200-second (20-minute) execution timeout.
The tool-call audit and stored job request record the effective timeout. This is
separate from the Datadog workflow HTTP timeout. Existing recovery-stop behaviour
is unchanged; changing this limit does not clear a persistent stop.

### Operator pause for overhaul — 2026-09-24

The operator paused this deployment for work with another harness. Paper is
persistently stopped (`operator`); the agent, live view, data-update timer and
state-backup timer are stopped and disabled. No XAUUSD cron entries were found.
Credentials, datasets, existing backups and the unresolved timed-out job are
preserved. Resumption requires explicit operator action and reconciliation of
that job; changing the shell timeout does not replay it.
