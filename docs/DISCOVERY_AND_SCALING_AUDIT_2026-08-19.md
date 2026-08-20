# XAUUSD discovery, incident, quantitative, and scaling audit

Date: 2026-08-19 (Asia/Shanghai)

Scope: read-only discovery plus this report; no service restart, remote deletion, strategy change, or trading activation was performed.

Evidence labels: **confirmed** means observed in code/runtime/data; **hypothesis** requires the stated test; **not yet verified** means evidence was unavailable. Secret values were never printed.

## Executive decision

Do not start a 100,000- or 500,000-scenario run. The mainland compute path is presently unavailable because its 16 GiB `/tmp` tmpfs is 100% full with 15,026 retained result directories. Upload commands are blocked, all 16 coordinator slots report `dispatching`, remote CPU is approximately idle, and the registry contains 41,430 remote-error requeues. Root-filesystem telemetry incorrectly reports 74 GiB free because it does not measure `/tmp`.

The existing system should be preserved, not rewritten. It already has an immutable dataset, deterministic fingerprints, SQLite registry, protected holdout, cost-aware event backtester, validation gates, 16-worker SSH compute, retries, recovery, remote artifact fetching, SSE dashboard, backups, ML research, portfolio research, and hard-disabled execution. The immediate work is lifecycle/diagnostic repair, then instrumentation and batching/vectorization.

## A. What was actually inspected

- Working tree, all fetched refs, remote, commits, worktrees, submodules, tracked files, generated artifacts, README, architecture and agent rules. Only `main`/`origin/main` at `9ca3b5c` exists; no submodules or additional worktrees were found.
- All Python modules and tests, Docker files, systemd templates and installed dashboard/coordinator units. No Kubernetes, PM2, or repository CI workflow was found.
- Active systemd services, journals, processes, disk/inode/memory/CPU state, SQLite schema/content/events, backups, tournament manifests, report sizes and coordinator status.
- Production DNS, TCP, TLS/SNI and HTTP health from the primary host; configured key-only SSH, clock, tunnel, mounts, processes, deployment hashes and dataset status on the secondary.
- Actual dataset: 353,354 UTC M1 rows, 2025-08-18 through 2026-08-18; 60/20/20 train/validation/protected-test split.
- Full local test suite: 94 passed in 21.24 seconds. Health: SQLite integrity `ok`, current backup, no health alerts.
- A non-invasive component benchmark on the primary. A new remote benchmark was deliberately not launched onto the full tmpfs.
- Not inspected: cloud invoices/security groups/provider console, mainland-client network path, browser HAR, external packet capture, container image registry, and private refs not advertised by origin. These are **not yet verified**.

## B. Existing architecture and data flow

`cTrader history -> normalized Parquet -> immutable TournamentDataset -> deterministic catalog/SQLite -> primary SSH coordinator -> 16 secondary processes -> signed result summaries/remote artifacts -> SQLite gates -> primary-only protected holdout -> champion history -> read-only FastAPI/SSE dashboard`.

Primary SQLite is authoritative. Secondary receives train/validation only and has no test partition. Each scenario currently creates one JSON job, one SSH upload, one SSH Python invocation, rereads Parquet, rebuilds features, runs the event loop, writes a full trade ledger/equity curve to `/tmp/xauusd-result-ID`, and returns a digest-checked summary. Details remain remote and are fetched on demand.

## C. Existing features that should be preserved

| Requirement | Inventory and evidence | Classification |
|---|---|---|
| Determinism/idempotency | Canonical semantic fingerprint has a unique SQLite constraint; dataset/code/cost/engine identities travel in jobs; duplicate registration tests pass | Implemented and working |
| Immutable/locked data | Content-addressed manifest; secondary has only train/validation; holdout runs on primary | Implemented and working |
| Resume/recovery | Durable queued/running/completed state, events, stale/replaced-worker recovery | Implemented, but remote retry lifecycle is defective |
| Distributed bounded work | 16-thread primary dispatcher and 16-core secondary | Implemented, currently unavailable due to storage exhaustion |
| Backtest causality/costs | Next-open fills, spread, slippage, commissions, conservative ambiguous-bar rule | Implemented but incomplete cost model |
| Gates | trades, expectancy, profit factor, drawdown, walk-forward and bootstrap, protected finalist | Implemented but statistically incomplete |
| Individual/mixed strategies | 11 individual families; equal-weight diverse-family portfolio and regime reporting | Implemented but mixture functionality is incomplete |
| ML | chronological gradient boosting and walk-forward ensemble/regime transformer, fixed seeds | Implemented but research validation is incomplete |
| Observability | health command, telemetry, worker stages, SSE, backups | Implemented but defective for mount health and failures |
| Artifact retention | remote on-demand allow-listed fetch and compaction utility | Implemented but lifecycle/retention is defective |
| Safety | repository is offline research; secondary lacks holdout; shadow readiness always false; no broker/order connector | Implemented and working; keep it so |
| Cancellation/backpressure | bounded pool supplies basic backpressure; explicit cancellation and per-experiment retry cap absent | Incomplete/not implemented |
| Structured connectivity states | only connected/error strings, no diagnostic state machine | Not implemented |

## D. Repository, checkout, and production-deployment differences

- Public/fetched checkout and primary deployment are the same working directory and commit. Installed systemd units exist outside Git; dashboard has an extra live-stream drop-in. The working tree already contained generated caches/logs, egg-info changes and `pyproject.toml.bak`; none were altered.
- Secondary `/opt/xauusd` is an archive deployment with no `.git`. Hashes of `pyproject.toml`, requirements and sampled engine/research/distributed code match primary exactly.
- The two `active.json` file hashes differ because `data_path` is relative on primary and absolute on secondary and secondary adds `compute_only`/`available_partitions`. Semantic version/fingerprint/row counts/partitions match. Golden result parity is **not yet verified**.
- Docker configuration exists but production XAUUSD services run directly under systemd. Unrelated Docker containers are present. No XAUUSD production container was found.
- `.env` includes read-only cTrader and compute variables. Secret presence was inspected by name only. Secondary `.env` was absent/unreadable; jobs do not require it. Credential validity beyond SSH is **not yet verified**.

## E. Current 50,000-scenario architecture and benchmark

The exact baseline catalog is `search_space.candidate_specs()`/`seed_catalog()`: 49,536 deterministic combinations, subsequently extended by adaptive/proposal trials. Registry now holds 55,395 trials across 11 families: 19,308 completed, 36,071 queued and 16 running.

| Measure | Observed |
|---|---:|
| Workers | 16 configured/claimed |
| Historical completed runtime | median 12.45 s; mean 12.85 s; p95 18.45 s; p99 21.98 s |
| Most recent 500 registry runtimes | median 21.18 s; mean 25.90 s; p95 46.97 s; p99 93.62 s |
| Pre-incident observed completion | roughly 230–258/hour for many hours, then 1,669–4,084/hour during faster families |
| Coordinator session display | 759/hour, but includes a long mixed incident window and is not a valid steady-state benchmark |
| Local component: train read | 0.054 s |
| Local component: train features | 0.126 s |
| Local component: Python backtest loop | 10.418 s for 211,945 feature rows and 27,291 trades |
| Local component: ledger/equity write | 0.857 s; 2.72 MiB for this high-turnover sample |
| SSH telemetry RTT | 468 ms during inspection |
| Secondary resources during incident | 16 cores; CPU 0.5%; 32 GB RAM, 55.1% used; root 26% used; `/tmp` 100% used |
| Registry size / primary reports | 128 MiB / 4.5 GiB |
| GPU | No GPU workload or GPU implementation found; **not yet verified** at hardware level |
| Queue wait distribution, transfer split, cloud cost | Not instrumented / **not yet verified** |

The initial 30-minute benchmark was superseded by richer live history and the P0 incident. Starting new remote work would have been operationally unsafe. A clean controlled benchmark must follow P0 recovery.

## F. Measured bottlenecks preventing 500,000 scenarios

1. **Confirmed P0 storage/lifecycle:** 15,026 result directories fill the 16 GiB `/tmp` tmpfs. Full-detail retention for all trials is incompatible with 500,000.
2. **Confirmed failure amplification:** upload commands can wait 60 seconds and retry four times; failed experiments are immediately requeued with no durable retry count/dead-letter cap. There are 41,430 error requeues and many blocked `cat > job` processes.
3. **Confirmed compute hot path:** `DataFrame.iterrows()` and per-bar Python object work consume about 10.42 seconds versus 0.18 seconds for read/features. This is the principal healthy-path CPU bottleneck for high-turnover scenarios.
4. **Confirmed per-scenario overhead:** one Python interpreter and SSH command per scenario, repeated feature calculation/read and full ledger/equity serialization.
5. **Confirmed observability defect:** telemetry checks `/` only and classifies SSH contact as connected despite application-handshake/storage failure. Its cumulative throughput is misleading.
6. **Likely:** 16 independent jobs duplicate resident frames/features. Memory saturation under valid work must be measured; present idle sample cannot prove it.
7. SQLite is not currently shown to be the bottleneck; writes are small and primary-only. Queue/database latency is **not yet verified** because stage timings are absent.

At the historically optimistic 12.85 s/scenario with perfect 16-way utilization, 500,000 needs about 111.5 hours. At the displayed 759/hour it needs 27.4 days. Even the best observed 4,084/hour needs 5.1 days. A one-day goal requires 20,833/hour (5.79/s system-wide, 0.36 core-seconds/scenario at 16 cores), a measured 5.1x over the best hourly result and about 37x over the local high-turnover CPU sample. More hardware and/or major hot-loop/batch reuse gains are required; one 16-core host alone is not yet demonstrated capable.

## G. Proposed 100,000, 250,000, and 500,000 scaling plan

First repair P0, add stage/resource instrumentation, establish a clean 50,000 baseline, and choose a configurable SLA/cost ceiling. Proposed default SLA is 24 hours; acceptance is blocked until infrastructure cost is supplied.

| Checkpoint | Entry gate | Required measurements / pass condition |
|---|---|---|
| 50k baseline | `/tmp` below 70%, bounded retention, retry cap, clean 30-minute saturation test at 4/8/12/16 workers | p50/p95/p99 stage times, CPU/RSS/mount/network/SQLite, retries/duplicates; zero silent loss; projected storage < quota |
| 100k validation | Warm worker process, batch jobs, shared read-only features, compact result default | Exact parity fixture; failure <1%, duplicate completion 0, bounded RSS, throughput degradation <10% from steady 50k |
| 250k load | Incremental bulk import/checkpoints, partitioned persistent artifact store, cancellation and dead letter | Resume after killed coordinator/worker; artifact sampling policy audited; database write p95 within target; no mount >80% |
| 500k run | Measured capacity meets configured SLA and approved cost; multiple-testing report ready | 100% terminal/auditable IDs, retry <1%, duplicates 0, parity tolerance met, full cost/time/result-distribution report |

Optimize in this order: (1) compact metrics for all, ledgers/equity only for candidates/failures/boundaries/audit/worst cases; (2) persistent partitioned result root with quota/TTL; (3) worker daemon and batches to reuse data/features; (4) replace/vectorize/compile the event loop while preserving golden behavior; (5) bulk result import; (6) scale horizontally close to the data only after the saturation curve. Roll back each feature through configuration to single-job/full-artifact legacy mode.

## H. Ranked mainland-server disconnection hypotheses

1. **Confirmed:** `/tmp` tmpfs full, causing upload/application-handshake failure.
2. **Confirmed contributor:** unbounded remote result retention and monitoring the wrong filesystem.
3. **Confirmed contributor:** retry storm/no cap leaves blocked upload processes and 41,430 requeues.
4. **Hypothesis:** unsynchronized NTP (`NTPSynchronized=no`) may later affect signed/authenticated market APIs; current SSH path works and clock wall-time appeared aligned.
5. **Hypothesis:** China route packet loss/idle interruption. SSH keepalive/control multiplexing exists; no loss test from mainland client was obtained.
6. DNS/TLS/proxy/auth are lower-ranked for this incident: production DNS, TLS certificate/SNI, HTTPS health and SSH authentication all passed from primary. Behavior from an actual mainland browser remains **not yet verified**.

## I. Exact tests required to prove the connection root cause

Before recovery capture `df -hT / /tmp/$result_root`, `df -i`, directory count/bytes, blocked process list, coordinator error sample and correlation IDs. Move (do not initially delete) audited old result directories to a persistent quarantined path; verify free space; terminate only orphaned upload processes; restart only the coordinator; observe one fingerprint through DNS -> TCP -> SSH auth -> upload -> dataset handshake -> compute -> digest import -> SQLite completion. Then run 100 scenarios with `/tmp` and result-root alarms and prove zero requeue.

For regional completeness run the same protected diagnostic from primary host/container, secondary host/worker and an actual mainland client: A/AAAA resolution, IPv4/IPv6 TCP, TLS chain/SNI, SSH/app authentication, handshake version, RTT/packet loss, MTU, clock offset, heartbeat, stale age, reverse-proxy/SSE behavior and 30-minute idle survival. Expected structured result is `CONNECTED`; this incident must return `RESOURCE_EXHAUSTED` (add this state) rather than generic disconnected. Credentials/headers must be redacted.

## J. Quantitative and backtesting defects

| Location | Severity/evidence and quantitative impact | Correction, regression test and acceptance |
|---|---|
| `engine.py:94` event loop | P2: `iterrows()` measured 10.42 s, about 91% of sampled scenario work | Array/compiled loop preserving exact fills; golden trades/equity/metrics equal within documented tolerance; rollback flag |
| `engine.py:14-24` costs | P1: fixed spread/slippage/commission only; no swap, latency, partial/rejected fills or time-varying spread | Versioned cost scenarios and stress grid; candidates must survive configured stress; retain `fixed-v1` rollback |
| `engine.py:106-117` stops | P1: conservative same-bar priority exists, but gap-through stops fill at stop rather than worse next/open price | Explicit gap policy fixture for long/short; no fill better than available open; version cost/engine |
| `validation.py:45-55` | P1: anchored walk-forward has no purge/embargo; train slice is recorded but deterministic rule is not fitted within it | Purged/embargo splitter and nested selection; zero label/event overlap in tests; legacy splitter configurable |
| `tournament_runner.py` | P1: only finalists receive richer validation; 500k selection-adjustment/PBO/FDR absent | Full trial-count/search-space/neighbor/PBO/FDR reporting before promotion; holdout stays locked |
| `validation.py:73-86` | P1: IID trade bootstrap ignores serial dependence/regimes; drawdown field is currency and named p95 while using 5th percentile | Block/stationary bootstrap, explicit units/tail naming; deterministic calibrated fixtures |
| `engine.py:135-158` | P1: missing Calmar, drawdown duration, expected shortfall, turnover, payoff, cost/gross, probability loss/ruin and concentration | Add versioned metric schema and accounting tests; no ranking on one metric |
| `portfolio_research.py:49-77` | P3: equal normalized equity averaging only; exposure is averaged, not combined; correlation/hidden leverage and leave-one-out absent | Portfolio return alignment and constrained weight research strictly on development folds; compare required baselines |
| `ml.py:56-83` | P3: threshold is fixed (safe), but final `test` is used in pass decision and artifact naming; no calibration/drift/abstention metadata | Locked test only once after nested selection; model card and simple baseline; reject no OOS net benefit |

No look-ahead was found in the tested rule features: append-future, next-open and breakout-current-bar tests pass. That does not prove every external dataset/model free of leakage; such a conclusion is **not yet verified**.

## K. Losing-strategy failure classifications

Across 19,308 completed trials, zero passed all gates and zero was promoted. Validation-profitable counts: mean reversion 136/4,841; momentum 92/6,892; all other completed families 0. Bootstrap-confidence passed 0; momentum walk-forward passed 8 and mean reversion 124. Median validation P&L ranges from -1,145 (volatility expansion) to -8,040 (single regime-switch trial).

- Breakout, micro-trend, session momentum, volatility expansion: reject current variants; **no demonstrated signal and/or signal consumed by costs**, with high trade counts. Exact attribution is not yet verified because gross-versus-cost/turnover decomposition is missing.
- Mean reversion and momentum: retain only in research/shadow consideration; classify as parameter/regime instability and cost sensitivity until the profitable minority passes block bootstrap, walk-forward, cost stress and multiple-testing controls.
- Regime switch: insufficient evidence (one completion). Autocorrelation regime, multi-horizon momentum, quantile reversion and volatility-adjusted trend: not yet verified (zero completions).
- Do not optimize any loss blindly. First record gross P&L, spread/slippage/commission/swap contributions, turnover, session/regime and tail concentration, then choose reject/simplify/regime restriction/diversifying mix.

## L. Strategy-mixture improvements

Preserve the existing equal-weight diverse-family validation portfolio. Add equal weight as benchmark, inverse volatility, risk parity, shrinkage correlation-aware, drawdown-aware and regime activation; constrain gross/net exposure, leverage and turnover. Fit weights only in nested development folds and evaluate once on locked holdout. Add best individual, simple rule and no-trade/cost baselines, pairwise correlation, effective number of bets, leave-one-out marginal return/volatility/drawdown/ES/turnover/tail/regime contribution. AI stacking must consume strictly out-of-fold predictions. Acceptance: mixture improves a predeclared multi-metric objective net of costs without worse configured tail gates; otherwise keep equal weight.

## M. AI improvements

Preserve seeded gradient boosting, ensemble adapters and train-fitted regime transformer. Do not add a larger model yet. Add model/feature/data/code versions, prediction-time availability checks, calibration, abstention/fallback, drift thresholds, retraining policy and locked-test governance. Compare against majority, logistic/linear and simple technical baselines after costs. Use ML first for anomaly/spread/slippage/regime forecasts where labels can be audited. Reject if nested walk-forward improvement is not selection-adjusted and stable. LLM proposals remain review-only and never place trades.

## N. Local and remote parity plan

Create a golden content-addressed fixture/job/result bundle. Run it in local venv, Docker, secondary and staging with pinned Python/dependency/BLAS metadata, UTC/TZ and seed. Compare signals/orders/trades exactly and floats under a declared tolerance (proposal: absolute `1e-9`, relative `1e-8`, then adjust only from measured platform evidence). Validate semantic manifests rather than raw path-bearing JSON hashes. Add startup schema/config/dataset/code/protocol/disk/clock checks and migration version. Current code hashes and semantic dataset match; numerical result parity is **not yet verified**.

## O. Security and trading risks

- P0 availability: retry storm and unbounded tmpfs artifacts; failure reasons/status UI are misleading.
- P0 secrets: `.env` contains broker/API tokens and a password-based recovery variable. Permissions/rotation/history are **not yet verified**; remove recovery password after key validation and rotate any stale credentials through provider controls.
- P0 execution: no broker/order connector was found and readiness is permanently false. Preserve this. Never add mutation endpoints or enable live trading under this work.
- P1 command construction: remote shell paths are interpolated into shell strings. Values are trusted config/fingerprinted IDs today; validate/quote them defensively.
- P1 dashboard exposure/auth/rate limiting and Cloudflare policy are **not yet verified**. Health is public and API read-only.
- P1 clocks: secondary reports NTP unsynchronized. Enforce offset alarm before authenticated protocols.
- Backups cover registry/manifests/status but remote artifacts are not demonstrated backed up. Define retention/audit tiers.

## P. Prioritized P0–P4 implementation plan

Every item follows: existing/evidence -> change -> benefit -> risk -> test/acceptance -> rollback.

1. **P0 remote recovery:** on-demand remote retention fills `/tmp` -> quarantine audited old artifacts, move result root to persistent partitioned storage, quota/TTL, mount-aware readiness, retry cap/circuit breaker -> restores compute/prevents storm -> risk losing referenced detail -> reconcile registry before move; 100 jobs, 0 loss/requeue, mount <70% -> revert root and restore quarantine index.
2. **P0 structured diagnostics:** SSH keepalive/telemetry exists but generic state -> typed end-to-end diagnostic with correlation ID, mount/clock/handshake/stale/circuit state, redacted output -> actionable mainland failures -> information exposure -> security tests and fault injection map each failure to one code -> disable protected diagnostic.
3. **P0 safety/security:** shadow-only hard block exists -> assert no execution modules/endpoints in CI, validate env names/permissions, rotate/remove unused recovery credential, clock sync alarm -> preserves research-only boundary -> credential interruption -> key-only canary and secret rollback through provider.
4. **P1 correctness/observability:** cost engine/gates exist -> versioned cost stresses, purge/embargo, block bootstrap, metric schema, stage timestamps/retry counts/failure table -> valid rejection and honest benchmark -> result comparability changes -> golden/accounting/statistical tests; keep old engine/schema version.
5. **P2 scale:** per-job SSH/Python/read/features/full artifacts -> warm batch workers, shared immutable features, compact defaults, optimized event loop, bulk imports/checkpoints/cancel -> orders-of-magnitude opportunity -> parity/concurrency bugs -> saturation and golden tests at each flag; legacy mode rollback.
6. **P3 selection/mixtures/AI:** existing basic gates/equal portfolio/ML -> nested purged selection, PBO/FDR, stability surfaces, constrained mixtures and model cards -> reduces false discovery -> fewer candidates -> report both adjusted/unadjusted, never relax holdout.
7. **P4 UI/reporting:** SSE dashboard exists -> typed incident banner, trustworthy windowed throughput, gate-failure/near-pass and storage/cost projections -> operational clarity -> UI load -> API performance tests and feature flag.

## Q. Exact files proposed for modification

No production file was modified in this first response. Proposed small change sets:

- P0: `xauusd/distributed_compute.py`, `xauusd/experiment_registry.py`, `xauusd/operations.py`, `xauusd/cli.py`, `xauusd/dashboard.py`, `.env.example`, `deploy/systemd/xauusd-remote-coordinator.service`, `tests/test_distributed_compute.py`, `tests/test_experiment_registry.py`, `tests/test_operations.py`, `tests/test_dashboard.py`.
- P1/P2: `xauusd/engine.py`, `xauusd/validation.py`, `xauusd/tournament_runner.py`, `xauusd/tournament_data.py`, new migration/config module only if schema evolution requires it, and corresponding engine/validation/runner/data tests.
- P3: `xauusd/portfolio_research.py`, `xauusd/ml.py`, `xauusd/ml_campaign.py`, `xauusd/weekly_report.py` and their existing test files.
- Documentation/deployment: `README.md`, `docs/ARCHITECTURE.md`, Docker files and requirements/lockfile only when runtime contracts actually change.

## R. Tests and acceptance criteria

- Existing 94 tests remain green; focused tests first, full suite and `git diff --check` for every change.
- Incident: mount-full fault produces `RESOURCE_EXHAUSTED`, stops claims via circuit breaker, uses bounded retries, leaves one durable failure record, and resumes idempotently after space recovery.
- Registry: every scenario records experiment/scenario identity, strategy/code/dataset/model/feature/config/seed/worker/stage timestamps/runtime/status/retry/metrics/failure/location; schema migration is reversible and duplicate terminal completion impossible.
- Parity: golden local/Docker/secondary outputs meet declared exact/float tolerances on two repeated seeds; protected test never appears remotely.
- Performance: report p50/p95/p99 queue/upload/read/feature/signal/backtest/serialize/import times, windowed throughput, CPU/RSS/I/O/network/mount usage and cost at 4/8/12/16 workers. Select saturation from evidence.
- Storage: compact-result projection fits quota with 30% headroom; detailed artifact policy samples all mandated categories; restart/reconcile proves references valid.
- Quant: gap/cost/accounting, causal append, purge/embargo, block-bootstrap reproducibility, parameter perturbation, regime and cost stress tests pass; no candidate can promote without all configured gates and selection warning.
- Scale gates are those in section G. A 500,000 run is authorized only after measured 250,000 acceptance and approved SLA/cost; no profitability claim or live activation follows from completion.

## Recommendation record template for implementation PRs

Each PR must explicitly state: existing implementation; evidence; proposed change; expected benefit; risk; test; acceptance criterion; rollback. Unsupported claims must remain marked **not yet verified**. This report intentionally proposes no new component where an existing one can be extended.

## Recovery update — 2026-08-20

P0 recovery was executed after explicit authorization:

- Audited 15,007 registry-referenced remote artifact paths and found only 19 initially unreferenced directories. No result artifact was deleted.
- Moved all 15,024 retained result directories from the 16 GiB `/tmp` tmpfs to persistent root-backed storage under `/opt/xauusd/quarantine/20260820-p0/results`; compatibility symlinks preserve legacy registry paths.
- Reduced `/tmp` use from 100% to 3%. Persistent root storage was 41% used after migration.
- Changed new result placement to `/opt/xauusd/var/results`, constrained below `COMPUTE_ROOT`; legacy `/tmp` paths remain allow-listed only for existing artifacts.
- Added independent root and `/tmp` mount telemetry and documented `COMPUTE_RESULT_ROOT`.
- Synced the compute module to the secondary and restarted only the primary coordinator service.
- Post-restart canary observed 133 completed scenarios, 16 active workers, zero session failures, approximately 3,024 scenarios/hour, median 12.17 seconds, p95 17.76 seconds, and no new error events. Fourteen `requeued_replaced_pool_worker` events were expected ownership recovery during the controlled restart.
- Focused tests: 28 passed. Full primary suite: 95 passed in 26.04 seconds. Secondary code import and live job execution passed; its minimal virtual environment does not include pytest/pip entry points.

Rollback: stop the primary coordinator, restore the previous compute module, point `COMPUTE_RESULT_ROOT` back to a persistent reviewed location (never the capacity-limited tmpfs), restart, and retain both persistent artifact trees until registry reconciliation completes.

## P0/P1 implementation updates — 2026-08-20

Two separately committed and pushed slices are now deployed:

- `758bbf0 bound remote retries and circuit failures`: additive registry migration adds durable `retry_count` and `failure_code`; remote failures classify into structured codes; retries terminate after `COMPUTE_MAX_RETRIES`; consecutive infrastructure failures open a cooldown circuit and stop new claims. Defaults are 3 retries, threshold 8, cooldown 60 seconds.
- `1756cd8 add stage timing and mount readiness telemetry`: remote telemetry reports root and `/tmp` mounts; coordinator readiness is `CONNECTED`, `DEGRADED`, or `RESOURCE_EXHAUSTED`; critical storage suppresses claims; dispatch/compute/import/total median and p95 timing samples are published in status.

Verification after deployment: coordinator active, 16 workers, `/tmp` 3%, persistent result storage healthy, 99 primary tests passing, no new terminal failures during the canary observations. Existing restart-related pool-worker recovery events are expected; they are not remote compute errors.

Initial 16-worker stage sample (64 post-deployment scenarios): 2,428 scenarios/hour cumulative session throughput; median/p95 dispatch 2.09/8.19 seconds, compute 11.42/15.06 seconds, import 0.008/0.086 seconds, and total 14.48/22.45 seconds. The independent registry window contained 1,333 completions over ten minutes with median 12.98 and p95 18.36 seconds. Compute is the dominant stage; primary result import is negligible. CPU telemetry's instantaneous 1% sample conflicted with load average 16.7 because its 250 ms sample landed between process waves; saturation analysis must aggregate samples rather than use one point.

## Controlled worker smoke test — 2026-08-20

A maintenance-window smoke test ran 45 seconds at each configured worker count and restored `COMPUTE_WORKERS=16` afterward. It is **not valid for SLA selection** because each restart requeued leases from the previous pool; those recovery events contaminated the claim/completion windows. It is retained as an operational signal only:

| Workers | Claims | Completions | Requeues | Approx. completions/hour | Runtime median / p95 | CPU sample | Readiness |
|---:|---:|---:|---:|---:|---:|---:|---|
| 4 | 13 | 8 | 12 | 640 | 11.11 / 13.93 s | 50.5% | CONNECTED |
| 8 | 24 | 16 | 4 | 1,280 | 10.16 / 10.71 s | 0% sample; load 7.1 | CONNECTED |
| 12 | 24 | 24 | 8 | 1,920 | 14.12 / 17.68 s | 0% sample; load 9.3 | CONNECTED |
| 16 | 33 | 18 | 0 | 1,440 | 22.11 / 23.05 s | 93.7% | CONNECTED |

All points had zero terminal failures and storage stayed healthy (root 42.0–42.1%, `/tmp` 2.9%). The 16-worker point reached CPU saturation, but its throughput was distorted by restart backlog and is not evidence that 12 workers is optimal. Next benchmark must use a dedicated benchmark queue/registry or a lease-drain protocol, at least 10–15 minutes per point, aggregate CPU/load samples, and exclude recovery events.

## Clean lease-drained saturation benchmark — 2026-08-20

Graceful draining was deployed in commit `98383c1`. A two-minute measurement window with a 30-second warm-up was run at each worker count; the coordinator drained to zero active leases before every restart and production was restored to 16 workers afterward. Every point had zero remote retries and zero terminal failures. `completed` may exceed `claimed` where warm-up claims finished inside the measurement window; throughput is based on completed terminal scenarios and remains directional until a dedicated benchmark registry isolates the queue completely.

| Workers | Claimed | Completed | Retries | Approx. throughput/hour | Registry runtime median / p95 | CPU sample | Root / tmp use |
|---:|---:|---:|---:|---:|---:|---:|---|
| 4 | 32 | 32 | 0 | 960 | 8.57 / 14.06 s | 0.5% sample; load 2.75 | 42.6% / 2.9% |
| 8 | 64 | 64 | 0 | 1,920 | 9.34 / 12.22 s | 14.5% sample; load 3.97 | 42.7% / 2.9% |
| 12 | 111 | 99 | 0 | 2,970 | 10.11 / 14.03 s | 48.3%; load 8.36 | 42.8% / 2.9% |
| 16 | 96 | 102 | 0 | 3,060 | 12.52 / 20.46 s | 99.0%; load 13.93 | 42.9% / 2.9% |

The measured curve is near-linear through 12 workers and begins to flatten at 16 while CPU reaches saturation. Keep production at 16 workers; do not increase concurrency on this host without a longer benchmark and evidence of lower per-worker CPU cost. At 3,060/hour, 500,000 scenarios require approximately 163.4 hours (6.8 days), before retries, adaptive replenishment, and queue effects. A one-day target requires approximately 20,833/hour, so batching, feature reuse, event-loop optimization, or horizontal capacity remains necessary.

## Compact artifact retention — 2026-08-20

Commit `2a59f22 compact artifacts for development rejects` is deployed. New secondary jobs retain full `trades.csv.gz` and `equity.parquet` only for validation-stage candidates or a deterministic audit sample controlled by `COMPUTE_ARTIFACT_AUDIT_PERCENT` (default 1%). Ordinary development rejects retain compact metrics and an explicit retention reason. Existing artifacts were not deleted, and validation/gate behavior is unchanged. The first post-deployment window observed 424 completed result summaries with 118 validation candidates; no terminal failures, `/tmp` 3%, and readiness `CONNECTED`. A follow-up measurement must compare bytes/scenario by retention class after all pre-deployment jobs drain, because legacy summaries do not contain the new retention field.

## Local/remote golden parity — 2026-08-20

Using completed experiment `78390` and the active dataset, the same fingerprinted job was run locally and on the deployed secondary without changing registry state. Development and validation metric dictionaries had zero differing fields; dataset and protocol metadata matched; both selected validation-candidate detailed retention. The 578-row trade ledgers were exactly equal, all numeric trade fields had zero absolute difference, and the 70,620-row equity series was exactly equal with maximum absolute difference `0.0`. This validates the current local/secondary execution contract for one fixture; repeated seeds, another strategy family, Docker, and a separately provisioned staging host remain **not yet verified**.
