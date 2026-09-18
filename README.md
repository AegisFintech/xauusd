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

## Autonomous Agent

`agent` runs one continuously trading AI plan-tool loop whose thinking is visible in a live web view. It is paper-first and reads `OPENAI_*`, `AGENT_*`, and (optionally) `FIRECRAWL_*` settings.

```bash
.venv/bin/python -m xauusd.cli agent status   # paper + recent transcript runs, no network
.venv/bin/python -m xauusd.cli agent once     # a single tick, then exit
.venv/bin/python -m xauusd.cli agent run      # continuous loop + live view (Ctrl-C to stop)
.venv/bin/python -m xauusd.cli agent view     # live view only
```

Every tick the planner may call a fixed allow-list of read-only tools (`read_market`, `paper_state`, `canary_signal`, `firecrawl_fetch`) and `propose_trade`. A proposal is only a proposal: the same deterministic paper risk, idempotency, freshness, and duplicate-order gates decide, and the coordinator reports exactly what the gates did. The planner's raw output, each tool call and result, and the final tick summary are appended to `agent_transcript` in CockroachDB, rendered by the live view at `http://127.0.0.1:8100/`. Web content and model output are untrusted data; they can never expand the tool allow-list or change risk settings.

`agent run` and `agent once` are inert unless `CTRADER_AUTOMATION_ENABLED=true`. Paper trading starts explicitly on each launch; cTrader demo wiring is a deliberate follow-up and stays disabled unless added explicitly.

To run the agent as a persistent background service (paper-only, live view on `http://127.0.0.1:8100/`):

```bash
sudo cp deploy/systemd/xauusd-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now xauusd-agent.service
journalctl -u xauusd-agent.service -f   # follow the agent's printed ticks
```

The service reads only `EnvironmentFile=/root/xauusd/.env` (it inherits no shell exports), so `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_API_KEY`, `DATABASE_URL`, `CTRADER_AUTOMATION_ENABLED=true`, and `CTRADER_PAPER_ONLY=true` must all be set there. Restart it (`systemctl restart xauusd-agent.service`) after editing `.env`. SIGTERM finishes the transcript run cleanly before the process stops.

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
git diff --check
```

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
