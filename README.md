# XAUUSD Research & Strategy Tournament

Offline, research-only XAUUSD M1 scalping platform. It reuses an immutable year of historical data, runs a large strategy tournament, dispatches train/validation backtests to a secondary compute server, and presents progress through a FastAPI dashboard. It never places trades or manages positions.

## Architecture

The primary server owns SQLite, the frozen dataset, orchestration, Codex Lab review, protected holdout, champion promotion, and the dashboard. The secondary Tencent server receives fingerprinted train/validation jobs over SSH and runs 16 workers (`COMPUTE_WORKERS=16`). Protected test data never leaves the primary server. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Quick start

```bash
source .venv/bin/activate
./start.sh
.venv/bin/python -m pytest -q
```

Useful commands:

```bash
.venv/bin/python -m xauusd.cli tournament-data status
.venv/bin/python -m xauusd.cli experiments summary
.venv/bin/python -m xauusd.cli operations health
.venv/bin/python -m xauusd.cli codex-improve status
```

Open `http://localhost:8080` (or the configured Cloudflare hostname). The UI uses Server-Sent Events at `/api/live`, so it updates without manual refresh.

## Data and experiments

Raw cTrader pages live under `data/raw/ctrader`; normalized UTC bars are stored in `data/processed/XAUUSD_M1.parquet`. Create the content-addressed snapshot with `data download`, `data validate`, `tournament-data create`, and `tournament-data verify`. The deterministic catalog currently contains 49,536 scenarios; replenishment starts below 10% queued, then novelty and rate-limited Codex proposals are added.

Lifecycle: `queued → running → completed/failed`. Every fingerprint, event, metric, artifact, gate decision, and promotion is retained in SQLite. Positive P&L is only a ranking signal; gates require minimum trades, expectancy/net profit, profit factor, drawdown, walk-forward robustness, and bootstrap risk limits. Only finalists reach the protected holdout, and a champion must beat the incumbent.

## Services

Units in `deploy/systemd/`: `xauusd-dashboard.service`, `xauusd-remote-coordinator.service`, `xauusd-data-update.service`, `xauusd-research.service`, `xauusd-weekly-report.service`, and `xauusd-backup.service`. Keep the legacy `xauusd-tournament.service` disabled while remote compute is active. Inspect with `systemctl status` and `journalctl -u <unit> -f`.

## Secrets and safety

Credentials belong only in the ignored `.env`; never print or commit them. Codex Lab is review-only and cannot alter credentials, protected data, deployment, or broker connectivity. Rotate credentials exposed in chat or source control.

For continuation instructions, read [AGENTS.md](AGENTS.md). For the component map and data flow, read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
