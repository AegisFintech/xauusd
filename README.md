# XAUUSD Research Platform

Research-only, event-driven XAUUSD M1 scalping platform. It never submits orders or connects to execution APIs. Configure historical data credentials with environment variables (`CTRADER_CLIENT_ID`, `CTRADER_CLIENT_SECRET`, `CTRADER_ACCESS_TOKEN`); demo account details are not stored in source.

## Quick start

```bash
./start.sh
```

The API/dashboard is available at http://localhost:8080. To run a local synthetic campaign (useful before credentials/data are available):

```bash
python -m xauusd.cli campaign --synthetic
```

With cTrader Open API credentials in `.env`, download and incrementally update
historical XAUUSD M1 bars:

```bash
python -m xauusd.cli data download --start 2024-01-01
python -m xauusd.cli data update
python -m xauusd.cli data validate
```

Each API page is archived under `data/raw/ctrader`; normalized, deduplicated UTC
bars are merged into `data/processed/XAUUSD_M1.parquet`. The downloader is
read-only and contains no order or position-management requests.

Run the event-driven backtester on a bounded real-data window:

```bash
python -m xauusd.cli backtest --strategy momentum --start 2026-08-01
```

Signals execute at the next bar open. Reports include a trade ledger, equity
curve, and JSON summary under `reports/backtests`.

Run the Milestone 3 baseline research campaign:

```bash
python -m xauusd.cli research --start 2026-07-01 --end 2026-07-31
```

This compares causal mean-reversion, momentum, breakout, micro-trend,
volatility-expansion, session, and regime-switching signals. The deterministic
manifest and leaderboard are written under `reports/research`.

Run the Milestone 4 out-of-sample validation gates:

```bash
python -m xauusd.cli validate-strategy \
  --strategy mean_reversion --start 2026-01-01 --end 2026-07-31
```

The validator creates chronological train/validation/test splits, anchored
walk-forward folds, ±20% parameter-neighborhood tests, seeded bootstrap trade
paths, and an explicit pass/fail gate report under `reports/validation`.

Run the first Milestone 5 gradient-boosting research model:

```bash
python -m xauusd.cli ml-research \
  --start 2026-01-01 --end 2026-07-31 --threshold 0.58
```

The model uses causal price features, chronological partitions, probability-
filtered signals, and the same realistic execution engine. Outputs are research
artifacts under `reports/ml`; failing models are never promoted.

Run the regime-aware ensemble across anchored walk-forward folds:

```bash
python -m xauusd.cli ml-walk-forward \
  --start 2026-01-01 --end 2026-07-31 --threshold 0.58
```

The core ensemble uses histogram boosting, random forests, extra trees, and a
training-only KMeans regime transformer. XGBoost, LightGBM, CatBoost, HMM, and
PyTorch adapters are optional install extras (`boosting`, `regimes`, and
`sequence`) so the research core stays lightweight. All policy interfaces are
offline-only and have no broker execution methods.

## Automated research

Run the idempotent daily research workflow after updating data:

```bash
python -m xauusd.cli data update
python -m xauusd.cli daily-run
python -m xauusd.cli weekly-report
```

Daily runs use the latest 180 days, rank all baselines, validate the top three,
write atomic JSON/HTML archives, and only promote candidates that pass every
validation gate and improve the champion score. `scripts/research-cron.sh` is a
cron-compatible composition of the update and research steps; installing it in
the host scheduler remains an explicit operational action.

Install with `pip install -e .` or Docker Compose. Historical bars are stored under `data/raw` and processed Parquet under `data/processed`.

## Build roadmap

This repository is being implemented one verified milestone at a time. Each milestone must include code, tests, documentation, and a reproducible example before we move on.

### Milestone 1 — Data foundation

- Implement a cTrader historical-data-only adapter (no execution API permissions).
- Download the maximum available XAUUSD M1 history and optional ticks.
- Store immutable raw files and normalized Parquet partitions under `data/raw` and `data/processed`.
- Add incremental updates, UTC normalization, duplicate detection, OHLC validation, and missing-bar reports/repair.
- Add CLI commands: `data download`, `data update`, `data validate`.

### Milestone 2 — Backtest engine

- Build an event-driven engine with deterministic intrabar simulation.
- Model raw spread, commission, slippage, configurable latency, position sizing, stops, targets, and time-based exits.
- Produce a complete trade ledger and equity curve.
- Add CAGR, Sharpe, Sortino, Calmar, profit factor, win rate, expectancy, drawdown, Ulcer Index, recovery factor, exposure, hold-time, monthly returns, and trade-distribution metrics.

### Milestone 3 — Baseline research

- Implement mean reversion, momentum, breakout, micro-trend, volatility expansion/compression, session, and regime-switching strategies.
- Add price and microstructure features with leakage-safe rolling windows.
- Run parallel backtests across all available CPU cores and cache reusable features.

### Milestone 4 — Validation and optimization

- Add train/validation/test splits, anchored and rolling walk-forward evaluation.
- Add Monte Carlo trade reshuffling, bootstrap robustness, parameter sensitivity, and overfit/stability gates.
- Add Optuna multi-objective optimization and a reproducible ranked leaderboard.

### Milestone 5 — ML research

- Add gradient-boosting adapters (XGBoost, LightGBM, CatBoost), regime models (HMM/GMM/clustering), and an ensemble interface.
- Add optional PyTorch sequence models (LSTM, temporal CNN, Transformer) behind extras so the core remains installable.
- Keep PPO/SAC research-only and offline; no broker connectivity.

### Milestone 6 — Automation and reporting

- Add a daily scheduler for data updates, research, retraining, walk-forward tests, ranking, champion promotion, and archival.
- Generate daily HTML/PDF and weekly comparison, regime, and drawdown reports.

### Milestone 7 — Dashboard and operations

- Expand the FastAPI dashboard with authentication, dark/mobile UI, Plotly equity/drawdown/trade/research/optimization views, exports, and system/data freshness monitoring.
- Add Docker Compose, health checks, structured logs, unit/integration tests, and one-command startup.

## Safety and completion criteria

The platform is strictly for historical research and backtesting. It must never submit market orders, manage positions, or connect to execution endpoints. Credentials belong in an untracked `.env` file or a secret manager; rotate any credentials that have been exposed in chat or source control.

The project is complete only when all milestones have passing tests, a real-data campaign has produced validated reports, and the dashboard can display the resulting leaderboard. Until then, the current synthetic campaign is a development smoke test—not evidence of trading performance.
