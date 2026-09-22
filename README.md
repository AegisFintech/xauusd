# XAUUSD Autonomous Research and Demo Harness

An auditable XAUUSD research system being extended with an autonomous AI harness and cTrader **demo-account-only** automation. It uses reproducible historical research, deterministic risk controls, and persistent operational state. It makes no profitability claim.

## Current Status

- Historical cTrader Open API acquisition, reproducible datasets, backtesting, validation, experiment registry, and read-only dashboard are implemented.
- Shadow observation mode persists signals and an emergency stop without broker execution.
- The autonomous AI harness, Firecrawl research ingestion, paper lifecycle, and a fail-closed demo execution adapter are implemented. Live execution is not.
- No real-money execution is supported or approved.

## Architecture

```text
read-only market data + Firecrawl sources
              |
              v
autonomous planner -> allow-listed tools -> evidence store
              |                                  |
              v                                  v
       AI proposal review                 deterministic gates
                                                  |
                                                  v
                                  paper state -> demo-only adapter
                                                  |
                                                  v
                              audit, dashboard, alerts, kill switch
```

The planner can only request tools registered by the application. Model and web responses are untrusted evidence. They cannot activate execution, change risk limits, expose secrets, or add new tools.

## Demo-Only Controls

The cTrader demo adapter requires all of the following before it can send a request:

- `CTRADER_DEMO_ONLY=true`
- cTrader host exactly `demo.ctraderapi.com`
- verified demo account metadata and the configured XAUUSD symbol
- successful account and pending-order reconciliation after restart, followed by an explicit operator start
- fresh market data and a healthy state store
- a clear persistent kill switch
- deterministic risk and idempotency checks

On uncertainty, restart recovery failure, data staleness, or API failure, the system will stop and alert rather than act.

## Configuration

Credentials belong in `.env` with mode `0600`; never commit them. Current historical-data settings and the demo-only assertion are documented in `.env.example`.

## Demo Automation

`demo-automation` is explicit and defaults to a no-network status check. It uses only the local normalized M1 data file, the fixed confirmed-breakout canary, CockroachDB paper/demo state, and the demo-only cTrader adapter.

```bash
.venv/bin/python -m xauusd.cli demo-automation status
.venv/bin/python -m xauusd.cli demo-automation once
.venv/bin/python -m xauusd.cli demo-automation run
```

`once` and `run` do nothing beyond returning disabled status unless `CTRADER_AUTOMATION_ENABLED=true`. When enabled, they require `CTRADER_DEMO_ONLY=true`, the demo cTrader settings, `DATABASE_URL`, and a positive integer `CTRADER_VOLUME_PER_PAPER_UNIT`. Set paper risk limits and the canary quantity explicitly in `.env`; `status` never opens a database or broker connection.

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

`agent` runs one continuously trading AI plan-tool loop whose thinking is visible in a live web view. It is paper-first and reads `OPENAI_*`, `AGENT_*`, and (optionally) `FIRECRAWL_*` settings.

```bash
.venv/bin/python -m xauusd.cli agent status   # paper + recent transcript runs, no network
.venv/bin/python -m xauusd.cli agent once     # a single tick, then exit
.venv/bin/python -m xauusd.cli agent run      # continuous loop + live view (Ctrl-C to stop)
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

`paper stop` persists a kill switch across restarts, and the agent refuses to auto-resume it; `paper start` is the explicit override. `state backup` snapshots the live SQLite file (verifies it with `quick_check`, gzips it, records a sha256 in a manifest), and `state restore` refuses any archive whose checksum or database integrity does not verify. A daily `xauusd-state-backup.timer` (midnight + randomized delay) keeps one verified snapshot per day under `backups/local-state`.

Every tick the planner may call a fixed allow-list of read-only tools (`read_market`, `paper_state`, `canary_signal`, `firecrawl_fetch`) and `propose_trade`. A proposal is only a proposal: the same deterministic paper risk, idempotency, freshness, and duplicate-order gates decide, and the coordinator reports exactly what the gates did. `propose_trade` returns `filled` as the authoritative verdict with `gate_reason` explaining it; in paper-only mode `sent_to_broker` is false because nothing reaches a broker, while `filled` still reports the paper fill. `canary_signal` emits each confirmed-breakout transition once and recovers a transition that landed on a bar the tick skipped — bounded by `max_backlog_bars` (default 2) so an old breakout is dropped rather than traded late — reporting `signal_bar_utc`/`signal_age_seconds` for the bar that fired. The planner's raw output, each tool call and result, and the final tick summary are appended to the agent transcript, rendered by the live view at `http://127.0.0.1:8100/`. Web content and model output are untrusted data; they can never expand the tool allow-list or change risk settings.

Paper account and transcript state live in a **local SQLite file** (`STATE_DB_PATH`, default `state/xauusd_local.db`) by default, so the running agent needs no external database or `DATABASE_URL`. Set `XAUUSD_STATE_BACKEND=cockroach` to return to the Cockroach-backed stores. The view serves the same transcript and paper endpoints from this store.

The view listens on `AGENT_VIEW_PORT` (default `8100`). It shows the transcript newest-first with the AI's plain-English reasons, a paper-account strip (equity, position, day/realized P&L, drawdown, recent fills from `/api/paper`), and a recent-runs line with per-run tick counts and duration. Times render in GMT+8, labelled `+08:00`; that is display-only — persisted timestamps, bar indices, and the market-hours gate stay UTC. Each `agent_<uuid12>` is one process start: a graceful SIGTERM marks the old run stopped, so a restart cadence legitimately produces many short "runs" — this is one process, not many agents., so a restart cadence legitimately produces many short "runs" — this is one process, not many agents.

`agent run` and `agent once` are inert unless `CTRADER_AUTOMATION_ENABLED=true`. On every launch the agent verifies database integrity and then consults the paper kill switch: it auto-resumes a clean paper account, but a stop left behind by `paper stop`, corrupt state, missing credentials, an unknown account type, or a failed recovery stays stopped (fail closed) until `paper start`. Each tick also writes a heartbeat to `AGENT_STATUS_FILE` (default `reports/agent_status.json`); the live view's `/api/health` turns that heartbeat, stall/error counts, consecutive ticks that never reached the planner, paper-stop state, and data-update failures into a healthy/degraded status with `alerts`.

Each tick records market `fresh`/`age_seconds`/`market_open` on `tick_start`, so a stale or closed-market feed is always visible in the transcript as "no trade". `age_seconds` counts from when the newest M1 bar **closed**, not from its open timestamp: persisted bars are stamped at bar open, so an open-based age is intrinsically 60-120s and any gate tighter than that can never pass — the loop would report `stale_data` forever while the feed looked healthy. `AGENT_MAX_MARKET_DATA_AGE_SECONDS`, `PAPER_MAX_MARKET_DATA_AGE_SECONDS`, and `CTRADER_AUTOMATION_MAX_MARKET_DATA_AGE_SECONDS` share that close-based semantic (default 180s, three bars); keep them consistent or proposals are refused as `STALE_MARKET_DATA`. **When XAUUSD is not trading (weekends, the 21:00-22:00 UTC daily break), the deterministic paper gate refuses every proposal with `MARKET_CLOSED` — the agent never trades a closed market.** Optionally set `AGENT_DATA_REFRESH_ENABLED=true` to let a stale tick refresh the local M1 parquet in-loop before the planner reasons (bounded by `AGENT_DATA_REFRESH_*`; still gated by the paper freshness and market-hours checks).

To run the agent as a persistent background service (paper-only, live view on `http://127.0.0.1:8100/`):

```bash
sudo cp deploy/systemd/xauusd-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now xauusd-agent.service
```

The unit captures the view port and `.env`; there is nothing to follow in the journal (see the observability note above). Use `/api/paper`, `/api/runs`, and the transcript to confirm activity.

The service reads only `EnvironmentFile=/root/xauusd/.env` (it inherits no shell exports), so `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_API_KEY`, `CTRADER_AUTOMATION_ENABLED=true`, `CTRADER_PAPER_ONLY=true`, and the local-state keys (`XAUUSD_STATE_BACKEND=local`, `STATE_DB_PATH`) must all be set there. With in-loop refresh desired, also set `AGENT_DATA_REFRESH_ENABLED=true`, `AGENT_DATA_REFRESH_MAX_AGE_SECONDS=30`, and `AGENT_DATA_REFRESH_MIN_INTERVAL_SECONDS=60` (the example ships these values). `OPENAI_*` must point at an OpenAI-compatible HTTP endpoint; that endpoint sits behind a Cloudflare WAF that rejects urllib's default `User-Agent` with `403 error code: 1010`, so the planner always sends a browser-grade `User-Agent`. Restart it (`systemctl restart xauusd-agent.service`) after editing `.env`. SIGTERM finishes the transcript run cleanly before the process stops.

The service writes no console or journald logs; the transcript, state store, and the live view (including `/api/health` at `http://127.0.0.1:8100/api/health`) are the only observability.

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest tests -q -p no:cacheprovider
git diff --check
```

An unscoped `pytest` from the repo root hangs while collecting `reports/` and `data/`; always scope it to `tests`.

## Demo Automation Service

The legacy research dashboard, coordinator, and timers have been retired and their templates removed. The only deployment template is `deploy/systemd/xauusd-demo-automation.service`.

The service is deliberately disabled by default. It exits without broker activity unless `.env` sets `CTRADER_AUTOMATION_ENABLED=true`; it requires a successful demo reconciliation, fresh M1 data, a confirmed-breakout transition, and all paper risk gates. Install and enable it only after a validated demo canary:

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
