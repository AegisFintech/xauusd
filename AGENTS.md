# Agent handoff and operating rules

## Mission

Maintain an offline XAUUSD M1 research tournament. Improve reproducibility, robustness, observability, and safe automation. Never turn this repository into an execution bot.

## First five minutes in a new thread

```bash
cd /root/xauusd
git status --short
source .venv/bin/activate
.venv/bin/python -m pytest -q
.venv/bin/python -m xauusd.cli operations health
.venv/bin/python -m xauusd.cli experiments summary
```

Read `README.md` and `docs/ARCHITECTURE.md`. Inspect service status before changing anything. Read `.env` only through commands that do not print secrets.

## Boundaries

- Primary CockroachDB is authoritative for state, events, metrics, and champions.
- `DATABASE_URL` is mandatory. Do not add a local registry backend or fallback.
- `TournamentDataset` owns the immutable train/validation/test snapshot.
- Secondary workers receive only fingerprinted jobs and return result bundles.
- Protected test/holdout data never leaves the primary server.
- Dashboard is read-only; do not add mutation endpoints without authorization.

## Safe change protocol

Make small changes with `apply_patch`; run focused tests and then `.venv/bin/python -m pytest -q`; run `git diff --check`; never stage `.env`, `__pycache__`, `logs/`, egg-info, or backups. If deployment is requested, commit, push, sync the secondary code, restart only the relevant service, and verify live status.

## Operations

Use the configured SSH key and host variables. For failures, check key-only authentication, coordinator journal, and `sg-tunnel.service` before changing credentials. Validate CockroachDB connectivity before changing registry configuration. Keep `COMPUTE_WORKERS=16` unless capacity evidence supports a change. Avoid destructive git/filesystem commands.

## Research policy

Positive score is ranking, not proof. Preserve every attempted fingerprint and failure reason. New formulas must be deterministic, causal, cost-aware, and pass walk-forward/bootstrap gates. Codex proposals are review-only and must pass tests before human-approved merge. A champion requires protected-holdout eligibility and improvement over the incumbent.

## Resume checklist

Confirm a post-key-restore successful dispatch, secondary telemetry with 16 cores and non-zero throughput, then prioritize gate-failure/near-pass analytics, adaptive mutation analytics, multiple-testing controls, artifact retention, and portfolio/regime analysis.
