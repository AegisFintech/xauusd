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
