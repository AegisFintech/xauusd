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

## Dispatch and retention corrections — 2026-08-20

Commit `497a2e2` moved persistent result-root creation from every scenario to coordinator startup. At 16 workers, post-deployment dispatch median/p95 fell to 0.62/0.82 seconds, compared with the prior clean p95 of 7.55 seconds; a later sample measured 0.31/0.37 seconds. Compute remained dominant at approximately 11.77 seconds median.

Storage inspection found the initial compact policy ineffective: 13,922 of 13,929 new result directories retained full artifacts because reaching validation was treated as candidate status while the development gate required only minimum trade count. Commit `e8378c0` corrected retention to validation-pass candidates, one-gate near passes, and deterministic audit samples. The first clean post-deployment sample contained 41 compact rejects and one detailed deterministic audit, with zero failures. Root storage was 54.7% and `/tmp` 3%; historical artifact compaction remains pending a registry-aware dry run and explicit apply operation.

## Historical compaction apply — 2026-08-20

Commit `de2dec6 add resumable remote artifact compaction` was deployed after 104 tests passed. A fresh SQLite backup `20260820T052119Z` was created before applying frozen plan digest `6f6401da5f57facf3da885ee9a6bf040987c37139dd90d4013730b04a0d11e52`. The secondary executor removed only `trades.csv.gz` and `equity.parquet` from 29,289 ordinary completed rejects: 57,532 files and 30,425,932,663 bytes. It recorded 29,289 fsync-backed journal rows; three already-missing directories were recorded as nonfatal. Primary reconciliation updated all 29,289 SQLite artifact records and emitted `remote_artifacts_compacted` events. Protected candidates and audit samples were not touched.

Post-apply verification: secondary root usage fell from 55% to 26%, `/tmp` is 2%, 16 workers resumed, and 290 detailed files remain for protected/new candidates. The plan and journal remain in ignored operational storage under `reports/tournament/` and `/opt/xauusd/var/`; they are retained for audit but intentionally not force-added to Git.

## Event-loop optimization — 2026-08-20

Commit `8bce493 optimize deterministic backtest event loop` replaced `DataFrame.iterrows()` and repeated Series indexing with pre-extracted NumPy arrays while preserving the state-machine branch and arithmetic order. All 105 tests passed. Before deployment, the new local implementation was compared against the still-old secondary implementation with forced audit retention: development/validation metrics, all 578 trades, and all 70,620 equity values were exactly equal; maximum absolute difference was `0.0`.

The sampled local 211,945-row, 23,422-trade backtest ran in 1.00 second versus the earlier 10.42-second sample (different current family, so directional rather than a strict microbenchmark). After graceful production deployment, a 147-scenario live window measured approximately 6,015 scenarios/hour, total median/p95 4.83/6.98 seconds, compute 4.19/5.47 seconds, dispatch 0.52/1.98 seconds, import 0.005/0.112 seconds, and zero failures. Root storage was 26.1%, `/tmp` 1.2%, readiness `CONNECTED`. At this observed rate, 500,000 scenarios require approximately 83.1 hours (3.5 days); one-day capacity still needs about 3.46x additional throughput.

## Gate-failure and near-pass analytics — 2026-08-21

Existing implementation: `WeeklyTournamentReport` already owned completed-trial reporting, family summaries, leaderboard context, and the dashboard's read-only weekly artifact. The milestone extended that path rather than adding another analytics service or mutable endpoint.

Evidence: the first Cockroach-backed report analyzed 51,093 completed trials in 16.4 seconds. No trial passed every recorded gate. It found 248 one-gate near-passes: 124 mean-reversion and 124 momentum trials. Failed-gate counts were positive expectancy 50,827, positive net profit 50,827, profit factor 50,827, drawdown 20,791, bootstrap confidence 150, minimum trades 116, and walk-forward consistency 18. The dominant combinations were expectancy + net profit + profit factor (30,036) and the same three plus drawdown (20,791). These are observed rejection reasons, not proof of economic loss causes.

Change: the versioned weekly JSON now includes deterministic gate counts, failure combinations, stage and family breakdowns, ranked one-gate near-passes, and per-field attribution coverage. Coverage was 51,055/51,093 for validation net profit and zero for gross profit, total costs, turnover, profit concentration, Expected Shortfall, and regime results. Those loss-source classifications therefore remain **not yet verified** and are explicitly reported as missing evidence.

Expected benefit: researchers can prioritize the actual rejection boundary and distinguish robust near-passes from broad failures without relaxing gates or selecting on a single score. Risk: loading all completed rows is linear in trial count and a high score can still reflect correlated or duplicated parameter regions. Tests: focused weekly-report tests cover gate combinations, near-pass ranking, family counts, stages, missing metrics, and empty limits; the full suite must remain green. Acceptance: the report completes against production in under 30 seconds, counts reconcile with completed rows, no missing metric is treated as evidence, the dashboard remains read-only and responsive, and live trading remains disabled. Rollback: revert the weekly-report field and tests; historical JSON artifacts remain valid because the addition is backward-compatible.

## Adaptive-mutation outcome analytics — 2026-08-21

Existing implementation: adaptive children already carry deterministic provenance containing generator version, parent experiment, generation, mutated parameter, multiplier, and parent validation score. Versioned generation reports already retain created and duplicate counts. Candidate generation and robustness gates were not changed.

Evidence: 25 retained generation reports recorded 1,156 attempts, 522 creations, and 634 duplicates, a 54.84% duplicate fraction. The registry contains 572 completed adaptive children; 50 predate or otherwise fall outside the retained creation history and are reported as unmatched rather than silently reconciled. Of 534 children with both parent and child scores, 87 improved (16.29%) and the median score delta was -0.3307. No adaptive child passed all gates; 248 were one-gate near-passes. Target-distance mutations had the highest observed improvement rate among adequately sampled parameters at 32.73% (18/55), followed by stop distance at 25.61% (21/82), but these correlated, adaptively selected trials are not independent evidence of out-of-sample benefit.

Change: `AdaptiveSearch.analyze()` reuses completed registry rows and retained generation JSON to write cumulative outcomes into the existing read-only `adaptive.json`. Results include attempted/created/duplicate reconciliation, pending and unmatched counts, comparable-score coverage, improvement and near-pass rates, median score delta, and breakdowns by family, parameter, multiplier, and generation. The `adaptive-analytics` CLI command refreshes the artifact without creating scenarios or reading protected holdout data.

Expected benefit: exhausted or degrading mutation directions are visible before more search budget is spent, while promising directions remain hypotheses subject to multiple-testing controls. Risk: missing early history, correlated children, reused parents, and validation-score selection can overstate improvement. Tests: deterministic fixtures cover improvement, regression, duplicate reconciliation, missing history, near-passes, grouping, and atomic artifact update. Acceptance: production analysis completes in under 30 seconds, every completed mutation is either comparable or explicitly missing a score pair, history mismatches remain explicit, no gate is relaxed, and no new scenario is registered. Rollback: remove the CLI action and analytics field; existing generation reports and child provenance remain unchanged.

## Multiple-testing and selection-bias analytics — 2026-08-21

Existing implementation: the weekly report warned about family-wise false positives, tournament validation stored scores and four aligned walk-forward fold results for candidates reaching robust validation, and protected holdout access remained gated behind a full validation pass. It did not calculate a selection-adjusted threshold, score distribution, PBO, FDR input coverage, stability coverage, or stored holdout usage.

Evidence: the first production report analyzed 51,824 completed variants, of which 51,786 had scores. The best score was 3.5251 versus median -38.612, interquartile range -58.214 to -26.154, and worst decile -82.200. At nominal alpha 0.05, the Bonferroni threshold is 9.648e-7 and the unadjusted family-wise false-positive probability rounds to 1.0. The largest strictly aligned cohort contains 150 strategies with four walk-forward folds; combinatorially symmetric validation across its six half-fold splits estimated PBO at 1.0 because every in-sample winner ranked below the out-of-sample median. This is a severe warning for that cohort, not a universal probability for all 51,824 variants. Zero valid null-hypothesis p-values, zero parameter-neighbor surfaces, and zero stored protected-holdout evaluations were present. The holdout count is consistent with no candidate passing all validation gates.

Change: the existing `multiple_testing` weekly artifact now reports variant and family counts, Bonferroni alpha, full score distribution, Benjamini-Hochberg results only when valid p-values exist, aligned-fold CSCV/PBO only when a compatible matrix exists, parameter-stability coverage, and stored holdout usage. The report never opens the protected partition and does not alter ranking, gates, promotion, or scenario execution.

Expected benefit: isolated best scores can no longer be presented without the tested-variant population and selection warning, while absent FDR/stability evidence remains visible. Risk: the current PBO estimate has only six fold splits, uses net profit within an already selected 150-strategy cohort, and correlated variants violate independence assumptions behind simple multiplicity thresholds. Tests: deterministic fixtures cover quantiles, Bonferroni, BH discoveries, aligned-fold PBO, and unavailable controls. Acceptance: all counts reconcile, PBO excludes unaligned folds, FDR never runs without valid p-values, no holdout data is read, report runtime stays under 30 seconds, and existing gates remain unchanged. Rollback: revert the additive weekly fields and tests; previously written JSON remains readable by the dashboard.

## Artifact-retention measurement — 2026-08-21

Existing implementation: result bundles record a retention decision, deterministic audit sampling is implemented, ordinary development rejects are compact by default, and the prior digest-locked compaction removed historical ledgers only after a dry run and reconciliation. The remaining gap was a repeatable read-only measurement of policy labels versus files actually present.

Evidence: a remote scan found 32,503 valid result bundles and zero invalid JSON files. The 18,344 `compact_development_reject` bundles occupy 48,168,777 bytes, average approximately 2,626 bytes, and retain zero detailed files. All 189 `deterministic_audit_sample` bundles retain both detailed files (378 files total), occupy 207,409,817 bytes, and average approximately 1,097,406 bytes. There are 2,782 legacy-unclassified bundles with 52 detailed files. The historical `validation_candidate` class contains 11,188 bundles and only 208 detail files; 11,084 still declare detailed retention in their immutable result JSON after the separately journaled historical compaction removed those files. This is a metadata-age mismatch, not newly observed data loss. Remote root usage was 26.3% with approximately 77.4 GB free.

Change: the existing operations CLI now provides `operations artifact-retention-inventory --root PATH`. It reads result bundles and files without mutation, groups scenario count, total and average bytes, detailed scenario/file count, declared policy, missing declared detail, unexpected detail, invalid JSON, missing result bundles, and disk usage. It does not compact, reconcile, or update registry state.

Expected benefit: bytes per scenario and policy drift can be measured at every scale checkpoint, and audit/candidate protection can be proven before any future compaction plan. Risk: immutable legacy bundle declarations do not incorporate later registry reconciliation, so mismatch counts require the compaction journal for interpretation; concurrent workers can also add a small number of results during a scan. Tests: fixtures cover compact, complete detailed, and declared-detail-missing classes. Acceptance: compact rejects have no detailed files, every current audit sample has both files, invalid JSON is zero, disk remains below warning threshold, and the command performs no writes. Rollback: remove the additive CLI action and inventory helper; no artifact or registry rollback is needed because the operation is read-only.

## Portfolio and regime research — 2026-08-21

Existing implementation: `PortfolioResearch` already selected one artifact-backed leader per family, used only the validation partition, assigned causal expanding-threshold trend/volatility/session regimes, and reported trade outcomes by regime. It combined normalized equity levels with equal weights and reported average component exposure. There was no chronological weight-fit boundary, return accounting, alternative weighting benchmark, correlation/effective-bet diagnostic, best-individual/no-trade baseline, or leave-one-out attribution.

Evidence: only two diverse-family leaders currently have detailed local artifacts: momentum experiment 18824 and mean-reversion experiment 14761. Weights were fitted on validation observations from 2026-03-24 23:44 UTC through 2026-05-07 17:35 UTC and evaluated on the later validation segment through 2026-06-05 09:04 UTC. The default equal-weight portfolio returned 0.0988%, with annualized volatility 0.266%, maximum drawdown 0.0544%, and 95% one-minute Expected Shortfall -0.00117%. Combined gross-exposure estimate was 0.166. Effective number of bets was 1.0, and the best individual returned 0.1908%, so the mixture did not improve return over the best individual. Inverse-volatility and correlation-aware fits both assigned all weight to the only nonzero-volatility fit series and produced no measured diversification benefit. These two selected validation histories are too few for a robust mixture conclusion; turnover, simultaneous position direction, tail dependence, and locked holdout mixture performance remain **not yet verified**.

Change: aligned strategy equity is now converted to returns before aggregation. Equal weight remains the default and rollback benchmark; inverse-volatility and correlation-penalized inverse-volatility are long-only research comparisons fitted only on the first 60% of aligned validation history. The later 40% reports each method's weights, return/volatility/drawdown/Expected Shortfall, combined gross exposure, fit correlation matrix, effective number of bets, and leave-one-strategy-out marginal effects. Best-individual, all-individual, and no-trade baselines are included. Fit/evaluation timestamps and `holdout_used: false` make the chronological contract explicit. Existing causal regime diagnostics are preserved; regime-based activation was not added because the available evidence cannot support it.

Expected benefit: mixture claims can now be rejected when they merely average correlated equity, hide concentration, or lose to a simple baseline. Risk: zero-volatility fit histories can concentrate inverse-volatility weights; sparse, asynchronously inactive strategies can make zero-return correlation estimates misleading; component exposure summaries cannot prove netted concurrent exposure. Therefore alternative weights are reporting-only and equal weight remains the default. Tests: seven focused tests cover causal regimes, drawdown, nonnegative normalized weights, future-append invariance, weighted-return accounting, perfect-correlation effective bets, leave-one-out/no-trade output, and validation-only dataset access. Acceptance: weights use only the declared fit interval, evaluation follows it chronologically, protected holdout is never read, all methods are compared on identical rows, no strategy is promoted, and the full suite plus `git diff --check` pass. Rollback: revert the portfolio module and focused tests; the additive JSON report can be discarded, and no registry, scenario, gate, coordinator, or dashboard state requires rollback.

## ML governance and drift controls — 2026-08-21

Existing implementation: `GradientBoostingResearch` already used ten causal price features, a fixed five-bar direction label, chronological train/validation/test splits, seeded histogram gradient boosting, probability-threshold abstention, and the cost-aware event backtester. `WalkForwardMLCampaign` already used anchored folds, train-fitted regime transforms, deterministic seeded ensemble members, and out-of-fold predictions. Optional larger backends were adapters rather than required infrastructure. Neither path can submit orders. Missing report evidence included a simple probability baseline, calibration error, feature drift, model/feature/data versions, retraining and fallback declarations, and explicit governance for repeatedly consumed test segments.

Evidence: the production gradient-boosting run used 347,496 training rows, 115,832 validation rows, and 115,832 later test rows. Validation ROC AUC was 0.5190 and log loss 0.69267 versus 0.69301 for the train-prevalence baseline, but validation drift was degraded: ATR PSI 2.697 and one/five/fifteen-minute return PSI 0.230/0.241/0.232 exceeded the 0.20 limit. On the later test segment, ROC AUC was 0.5151 while log loss 0.69379 was worse than the 0.69362 baseline; ATR PSI remained degraded at 1.340. Only 1.24% of rows generated an active signal, producing 1,139 trades, net P&L -303.13 after configured costs, profit factor 0.697, expectancy -0.266, and maximum drawdown 0.319%. The current classifier therefore fails both economic and drift/baseline criteria. This does not establish that all ML uses lack value; spread/slippage, anomaly, regime, and volatility targets remain **not yet verified**.

Change: both existing ML report paths now include deterministic Brier score and expected calibration error, a train-prevalence classification baseline, and feature-level Population Stability Index fitted only on training distributions. Low-cardinality features use categorical PSI. A versioned model card records target and label construction, prediction-time features, model/feature/data fingerprints, seed, calibration status, manual retraining policy, drift limit, threshold abstention, no-trade fallback, and live-trading status. Walk-forward folds carry the same baseline and drift evidence. `research_gate_passed` requires improvement over the simple log-loss baseline, acceptable drift, and the existing economic criteria. `passed` is always false and `promotion_eligible` is false because these commands repeatedly consume their evaluation segments; a separately governed locked holdout would be required for promotion.

Expected benefit: a complex classifier can no longer appear acceptable solely from ROC AUC above 0.5 while losing after costs, underperforming a constant baseline, or operating under feature drift. Risk: PSI depends on the reference window and binning and is a monitoring signal rather than a causal explanation; the constant baseline does not replace linear/logistic or simple technical baselines; the current dataset fingerprint is a canonical in-report hash rather than the tournament manifest version. Tests: eight focused tests cover causal features, future-append invariance, reproducibility, calibration, numeric and categorical drift, deterministic core model adapters, train-only regime transforms, research-only model-card gating, and fold-level baseline/drift output. Acceptance: no report is promotion eligible, fallback is no-trade, every evaluated segment includes baseline/calibration/drift evidence, train-fitted bins and transforms never use future rows, production evidence rejects the current model, the full suite passes, and live trading remains disabled. Rollback: revert `ml.py`, `ml_campaign.py`, and the focused tests; delete additive research JSON if desired. No tournament registry, coordinator, dashboard, scenario, protected-holdout, or execution state changes require rollback.

## Dependence-aware bootstrap validation — 2026-08-21

Existing implementation: robust validation already used deterministic seeded resampling of completed trade net P&L, gated candidates on loss probability and fifth-percentile net P&L, and retained every bootstrap result. The implementation sampled individual trades IID, so clustered wins and losses were broken apart. It also stored the fifth percentile of a signed currency drawdown under `p95_max_drawdown`, making both percentile direction and units ambiguous.

Evidence: on retained mean-reversion experiment 14761 with 2,956 trades and 500 deterministic paths, IID resampling estimated loss probability 31.8%, fifth-percentile net P&L -281.11, and 95th-percentile drawdown loss 523.33 account-currency units. Five-trade circular blocks estimated 30.2%, -335.94, and 541.86 respectively, exposing a materially worse lower P&L tail and drawdown once local trade dependence was retained. Both methods reject the candidate. A six-trade momentum artifact produced unstable differences and remains ineligible under the configured minimum-trade gate; it is not evidence for block-length selection. The optimal dependence horizon across families remains **not yet verified**.

Change: the existing bootstrap function now performs a seeded, vectorized circular moving-block bootstrap with configurable block length, default five. `ValidationConfig` and `TournamentGates` both record this parameter. Reports add method, seed, effective block length, `account_currency` units, explicit signed `p05_drawdown_currency`, and positive `p95_drawdown_loss_currency`. The legacy `p95_max_drawdown` field remains as a backward-compatible signed alias. Existing loss-probability and fifth-percentile-net-P&L gate names and thresholds are unchanged. Vectorized block construction completes two 500-path comparisons over 2,956 trades in approximately 0.10 seconds on the primary host.

Expected benefit: robustness gates retain short-run loss clustering instead of assuming independent trades, while tail direction and units are auditable. Risk: a fixed five-trade block can understate or overstate dependence for different holding periods, sessions, and regimes; circular wrapping introduces one artificial boundary adjacency; previously stored IID reports remain historically valid but are not directly comparable without their method metadata. Tests: focused fixtures cover seed reproducibility, invalid configuration, currency/tail aliases, clustered-sequence sensitivity, and tournament propagation. Acceptance: every new robust report identifies its resampling contract, block paths are deterministic, clustered fixtures differ from IID, existing gate consumers remain compatible, runtime is bounded, the full suite passes, and no historical registry row is rewritten. Rollback: set block length to one for IID-equivalent behavior or revert the validation and tournament-runner changes; additive report fields can be ignored and no market data, artifacts, or prior decisions are mutated.

Deployment evidence: commit `860cbe4` was pushed, the coordinator drained cleanly at zero active leases after 4,093 session completions and zero failures, then restarted and resumed at 16 configured workers. During the post-restart canary, CockroachDB emitted one `ReadWithinUncertaintyIntervalError` under its inherited serializable transaction isolation. The coordinator loop recovered and completed 32 new scenarios with zero scenario failures, but status correctly remained `error` for the last loop exception. Inspection confirmed the registry adapter had no explicit isolation contract. The follow-up sets PostgreSQL connections to configurable `DATABASE_TRANSACTION_ISOLATION`, default `read_committed`; the existing row-locking claim transaction and uniqueness constraints remain in place. A live `SHOW transaction_isolation` returned `read committed`. This is intended to let Cockroach retry statements and avoid uncertainty errors; sustained absence of transaction retries after service reload remains **not yet verified**. Risk: read-committed multi-statement analytics can observe newer rows between statements, which is acceptable for dashboard summaries but must not replace explicit locking in ownership or promotion transactions. Rollback: set `DATABASE_TRANSACTION_ISOLATION=serializable` and restart the coordinator; no schema or data rollback is required.

## Execution-cost and loss-source attribution — 2026-08-21

Existing implementation: the event-driven engine already charges half-spread plus slippage on both entry and exit fills and commission on both sides. Every retained detailed ledger contains fill-adjusted gross P&L, total commission, and net P&L, while all scenarios retain compact metrics. The weekly report already measured whether attribution fields existed but did not produce them or classify observed losses.

Evidence: a deterministic flat-price 100-ounce fixture with a 0.20 spread, 0.05 slippage, and 3.50 commission per lot per side produces zero pre-cost P&L, 30.00 implicit spread/slippage cost, 7.00 commission, and -37.00 net P&L. The exact accounting identity is `net_profit = gross_profit - total_cost`, subject only to floating-point tolerance. Existing historical scenarios lack these additive compact fields and are left missing; their costs are not inferred. At milestone start, the live registry held 543,396 scenarios, with 55,707 completed, 487,680 queued, nine running, and no promoted champion. The remote session had zero scenario failures and 16 configured workers.

Change: every newly executed partition now stores pre-cost aggregate P&L, implicit execution cost, commission cost, total cost, cost-to-positive-pre-cost-profit ratio, two-sided XAU notional turnover, worst-five-percent trade Expected Shortfall in account currency, and the share of positive net P&L contributed by the best 10% of winning trades. This remains a compact metric dictionary and does not retain additional ledgers. Weekly analytics classifies a negative result as `no_genuine_signal` only when measured pre-cost P&L is non-positive, or `signal_consumed_by_execution_costs` only when pre-cost P&L is positive and net P&L is negative. Rows without direct gross evidence are `insufficient_evidence`; non-losing rows are explicitly separated. Regime, position-sizing, drift, turnover-excess, tail-causality, data-quality, and infrastructure classifications remain **not yet verified** rather than being guessed.

Expected benefit: future trials can distinguish absent edge from cost-consumed edge without loading full ledgers, quantify result-storage coverage, and prioritize simplification or turnover reduction using measured evidence. The additive fields flow through the existing local and distributed result contracts without schema migration or API breakage. Risk: trade-level Expected Shortfall is not portfolio return Expected Shortfall; turnover is account-currency notional rather than a normalized annual rate; top-decile winner concentration can be unstable for small trade counts; fixed configured costs are a model, not proof of realized broker costs. Tests: focused deterministic accounting, reconciliation, tail, turnover, concentration, missing-evidence, and classification tests pass, followed by the full 124-test suite and `git diff --check`. Acceptance: new remote canary results contain the fields, pre-cost P&L minus costs reconciles to net P&L, historical missing values remain missing, zero gross is not reported as a negative floating-point residue, the coordinator returns to 16 healthy workers with zero canary failures, and no gate or live-trading behavior changes. Rollback: revert the additive engine metrics, weekly classifier, and tests; old and newly written JSON remain readable because consumers ignore unknown fields, and no database migration or historical rewrite is involved.

Deployment evidence: commit `e557d84` was pushed, the coordinator drained at zero active leases after 1,088 session completions and zero failures, the engine was synced to the secondary, and only the coordinator was restarted. The first canary returned 16 fresh completions and zero failures with the new compact fields. Mean-reversion experiment `1203305350172934145` measured validation pre-cost P&L 253.24, total cost 3,089.46, and net P&L -2,836.22, directly supporting `signal_consumed_by_execution_costs`; experiment `1203305350123159553` measured pre-cost P&L -179.23 before 3,458.40 costs, supporting `no_genuine_signal`. Both failed existing gates and neither was promoted. The reported remote commit was `e557d84fbac12f0a03e97585fe55aba4deb1432c`.

## Parameter-stability surfaces — 2026-08-21

Existing implementation: deterministic scenario parameters, family, formula, dataset version, and validation scores were already retained for every completed trial. Validation could calculate explicitly supplied neighbor candidates one at a time, and the multiple-testing report exposed zero stored stability coverage, but no tournament-wide surface reused the completed grid or detected isolated optima.

Evidence: a read-only production analysis over 56,181 scored experiments completed in 23.6 seconds. Exact surfaces require the same dataset, strategy family, formula, and every categorical and numeric parameter except the single varied numeric dimension. Under that contract, 55,613 experiments have at least one comparable neighbor and 53,261 have a two-sided neighbor; 99,581 parameter surfaces contain at least two values. At declared tolerance `max(0.10, 10% of absolute score)`, zero experiments are stable across every comparable dimension. There are 389 experiments with at least one two-sided isolated peak (393 experiment/dimension comparisons). This is validation evidence only and does not make any candidate holdout eligible.

Change: the existing weekly report now builds deterministic one-dimensional parameter surfaces from completed trials without registering or rerunning scenarios. It reports scored/comparable/two-sided coverage, surface count, candidates stable across all comparable dimensions, unique isolated-peak experiments, isolated comparisons, and a bounded shortlist ranked by validation score with exact neighbor values and scores. Categorical values, including direction, remain part of the fixed signature and cannot be crossed accidentally. Duplicate observations at the same parameter value are reduced by their median score. No interpolation, gate relaxation, search-space mutation, or protected-holdout access occurs.

Expected benefit: isolated best scores and narrow parameter dependence become explicit using work already paid for, while missing neighbors remain measurable before further search is authorized. Risk: one-dimensional slices do not capture interaction surfaces, irregular spacing is not distance-normalized, median duplicate reduction can conceal provenance differences, validation scores are correlated and selection-biased, and the tolerance is a reporting policy rather than a statistical confidence interval. Tests: fixtures prove exact numeric adjacency, nested-parameter handling, categorical and formula isolation, two-sided peak detection, and bounded output; the full 125-test suite and `git diff --check` pass. Acceptance: runtime remains under 30 seconds at the present completed scale, every comparison changes exactly one numeric parameter, top peaks include both neighbor values and scores, no scenario or holdout read is triggered, and the weekly JSON remains backward-compatible. Rollback: remove the additive `parameter_stability` report and helper; generated weekly JSON can be discarded and no registry, result, service, or dataset state needs rollback.

## Scaling checkpoint and operational projection — 2026-08-21

Existing implementation: the remote coordinator already uses 16 bounded workers, leases with ownership and retries, stage-duration histograms, resource telemetry, graceful drain/resume, and a resumable registry. The operations CLI exposed health and artifact inventory but did not combine the live session measurements with registry progress into explicit 50k/100k/250k/500k checkpoints or a measured bottleneck/ETA.

Evidence: `operations scaling-checkpoint` read the live registry and `reports/tournament/distributed/status.json` without mutation. At 2026-08-21 09:17 UTC it reported 543,396 total scenarios: 56,521 completed, 486,868 queued, seven running, zero terminal failures, 22 retry attempts across 22 scenarios, and zero duplicate fingerprints. The current session throughput was 2,546.12 scenarios/hour, median total duration 6.49 seconds, p95 12.77 seconds, with compute median 5.18 seconds, dispatch median 0.67 seconds, and import median 0.08 seconds. Remote CPU p95 was 100.0%, memory 11.5%, disk 26.4%, and observed transfer rates were approximately 3.3 KB/s receive and 42.8 KB/s transmit. The measured bottleneck is secondary compute saturation; database-write and network saturation are **not yet verified**. The 50,000 checkpoint is reached; 100,000, 250,000, and 500,000 remain pending. At the observed rate, 443,479 remaining scenarios project to 174.2 hours. A one-day completion would require 18,478 scenarios/hour, 7.26 times the observed rate.

Change: `OperationsManager.scaling_checkpoint()` and `operations scaling-checkpoint` now report registry counts, terminal/retry/duplicate rates, checkpoint status, measured stage durations, CPU/memory/disk/network telemetry, current bottleneck classification, current ETA, and the throughput multiplier required for a configurable 24-hour target. The report preserves all existing concurrency and queue behavior; it is an operational measurement, not an automatic scale-up. Cost remains **not yet verified** because cloud billing and secondary-host pricing are not available in the execution environment.

Expected benefit: every scale checkpoint has a reproducible measurement contract, and saturation decisions can be based on observed CPU and stage data rather than blind concurrency increases. Risk: throughput varies by strategy family, cache state, SSH latency, and coordinator session; the projection is therefore refreshed evidence, not a capacity guarantee. Retry count is scenario-level and may undercount transient attempts not persisted by a crashed coordinator; duplicate fingerprints are registry-level uniqueness evidence, not semantic equivalence. Tests: an isolated registry/status fixture verifies checkpoint transitions, failure/retry accounting, duplicate calculation, compute bottleneck selection, and ETA; the full 125-test suite and `git diff --check` pass. Acceptance: the command performs no writes, current worker count remains 16, 50k is marked reached, later checkpoints remain pending, projected time and required throughput reconcile arithmetically, and no service restart is required. Rollback: remove the additive operations command and test; no registry, queue, worker, or result state changes.
