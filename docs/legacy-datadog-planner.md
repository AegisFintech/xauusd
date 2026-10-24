# Legacy Datadog planner operations

This is an optional planner, not the active Codex deployment. Historical settings below must not be read as current runtime state. The server-enforced Bits shell ceiling is 1200 seconds (20 minutes).

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
cycles. Do not run it concurrently with the service. Shell timeouts are 1–1200s,
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
