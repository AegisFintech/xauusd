# Aurum — Codex Autonomous Trading Lab

An auditable XAUUSD research system being extended with an autonomous AI harness and cTrader **demo-account-only** automation. It uses reproducible historical research, deterministic risk controls, and persistent operational state. It makes no profitability claim.

## Current Status

The primary local dashboard is an interactive, read-only trading command centre
at `http://127.0.0.1:8100/`; the previous transcript view remains at `/legacy`.
Codex is the core advisor of a persistent agent loop: it owns an evolving agenda,
requests tools, receives actual results on the next turn, writes research and
application code, searches for new sources/methods, and dispatches isolated
experiments to `tc02`. The dashboard separates the **100% daily return aspiration**
from measured account returns and separates new activity from archived context.

Successful application changes can deploy automatically after isolated complete
suite verification, optimistic source checks, and restart health checks with
rollback. Original tests and the control kernel remain protected. Research
packages install in scratch; production dependency migrations remain unavailable.
Strategies still require independent cost-aware chronological validation and a
fixed seven-day observed-forward test before **paper-only** promotion.

The engine halt, paper kill switches, demo host pins and account restrictions
remain authoritative. See [the open-agent runbook](docs/operator-runbook-agent.md)
and [strategy qualification](docs/operator-runbook-codex.md).

The active Codex advisor runs with operator-authorized `--yolo` full service OS
access. In **Research → Conversation & application prompts**, new application
inputs, public replies and tool exchanges have short, expandable pages and explicit
record downloads. Conversation storage rotates after seven days with a 20 MB /
2,000-entry ceiling; unchanged instruction bodies deduplicate. Existing trading
controls remain authoritative. See [permissions and visibility](docs/agent-conversation.md).

## Architecture

```text
current market + account + memory + capabilities
                      |
                 Codex advisor <--------- actual tool results
                      |                           ^
               durable tool calls ----------------+
                      |
         sources / analysis / tc02 / engineering
                      |
           tested changes -> deploy / health / rollback

strategy proposals -> independent validation + forward observation
                   -> unchanged risk gates -> paper trading
```

The legacy Datadog Bits planner remains an alternative. Its operator-authorized
arbitrary shell permission model is unchanged; it is not the active Codex path.

## Demo-Only Controls

The cTrader demo adapter requires all of the following before it can send a request:

- `CTRADER_DEMO_ONLY=true`
- cTrader host exactly `demo.ctraderapi.com`
- verified demo account metadata and the configured XAUUSD symbol. The account list is
  the only response that states whether an account is live, so an account the broker
  never classified is treated as **not** demo. A configured
  `CTRADER_CTID_TRADER_ACCOUNT_ID` skips that request when the token scope cannot
  answer it; that account then reports `is_demo: false` in reconciliation details
  rather than claiming a verification that never happened.
- successful account and pending-order reconciliation after restart; only a fresh (never-stopped) execution switch starts automatically, every persisted stop needs `demo-automation start --reason ...`
- fresh market data and a healthy state store
- a clear persistent kill switch
- deterministic risk and idempotency checks

On uncertainty, restart recovery failure, data staleness, or API failure, the system will stop and alert rather than act. A broker error reply is recorded as `BROKER_REJECTED`. A transport failure or timeout after sending is recorded as `OUTCOME_UNKNOWN`, because the order may still have executed. Either one stops paper (`broker_execution_failed`) and demo execution, and neither switch resumes on its own. Check the account's broker positions before restarting.

### Known accepted limitation: broker TLS is encrypted but not authenticated

The `ctrader-open-api` SDK builds its endpoint as Twisted's `ssl:` URI, which creates a
bare `SSL.Context` with `verify_mode=CERT_NONE` and `check_hostname=False`. Only the
`tls:` URI (`optionsForClientTLS`, hostname + platform trust root) verifies. The
endpoint string is hardcoded inside the vendor package, so this repository cannot
influence it without replacing the SDK's client construction.

Consequence: the `client_secret` and all order traffic travel over an encrypted but
unauthenticated channel, so a network-level attacker who can intercept could capture
the app secret and forge order or fill replies, defeating the fail-closed order
lifecycle below. This is accepted for the demo-only deployment, where the blast radius
is a demo account. It is **not** acceptable for a real-money account, and it must be
resolved by constructing the client over a verified endpoint before any live trading
is considered.

## Configuration

Credentials belong in `.env` with mode `0600`; never commit them. Current historical-data settings and the demo-only assertion are documented in `.env.example`.

`.env.sample` links to `.env.example`. For the current harness select `AGENT_PLANNER=codex`; the sample also documents optional legacy settings. Set `AGENT_PLANNER=datadog` and the `DD_*` settings to use the Bits workflow. See
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
.venv/bin/python -m xauusd.cli data rebuild --cutoff 2019-12-01   # recover from the raw archive
.venv/bin/python -m xauusd.cli data raw-retention                 # report archive redundancy
.venv/bin/python -m xauusd.cli data heal --days 7                 # fill interior gaps
```

Credentials are an **OAuth2 token pair** (`CTRADER_ACCESS_TOKEN`, `CTRADER_REFRESH_TOKEN`) minted once through the cTrader ID granting-access flow (`xauusd.oauth.authorize_url` → `/apps/token`). With `CTRADER_CTID_TRADER_ACCOUNT_ID` left empty, both the data downloader and the demo execution adapter auto-discover the demo account and its XAUUSD symbol from the token (`ProtoOAGetAccountListByAccessTokenReq`); set the explicit id to pin a specific account (legacy leaf-token mode). On a `CH_ACCESS_TOKEN_INVALID`, `data update/download` refresh via `grant_type=refresh_token` once and atomically rewrite only the two token keys in `.env` (`0o600`) — nothing is ever logged. Both paths require `CTRADER_DEMO_ONLY=true`.

Every `data update/download` run records `reports/data_update_status.json` (`state: ok | auth_error | failed`, `error_code`, `recorded_at`, `end`), surfaced by the live view at `/api/data-update`, so timer failures are loud instead of silent `exit-code` entries. `error_code` is `store_corrupt` when the parquet exists but cannot be parsed and `disk_full` on `ENOSPC`; anything else stays `null` rather than guessing, and exception text is never persisted because it can carry a token inside a URL. The `xauusd-data-update.timer` re-enables scheduled 6-hourly refreshes.

`data/raw/ctrader/XAUUSD/M1/` archives every page the downloader fetches, so `data rebuild` reconstructs the store offline with no broker access — the recovery path when the store is unreadable. It quarantines an unparseable file to `<name>.corrupt-<UTC stamp>` rather than overwriting the evidence of how it broke, streams pages in chunks because the archive is heavily redundant (34M bar records for 2.4M unique minutes), and requires `--cutoff` when the store cannot be read: the archive reaches back to 2014, years before the store's 2019-12-01 start, and growing the store backwards changes the dataset version. Rebuilding 2.4M bars from 6,806 pages measured 45 minutes. **Never purge `data/raw/`** — it is the only rebuild path.

`data raw-retention` reports how much of that archive is redundant and deletes nothing. Measured on 2026-10-09: 7,155 pages / 4.67 GB, of which a minimal cover needs 826 pages / 530 MB — 8.66× redundancy and 4.14 GB reclaimable with the full bar range preserved (`cover_preserves_the_full_range: true`), computed in 1.7 s from the page filenames. Applying it is an operator decision, and it costs the overlap: a minimal cover keeps no second copy of any minute, so one corrupt surviving page would be unrecoverable. The cover is also computed from the ranges in the filenames, not from the bars themselves.

`data update` computes its start from the newest bar, so it can only extend the tail — an interior hole is permanent. A feed restart on 2026-10-12 lost 16 minutes that four daily updates could not reach, and they stayed missing until `data heal` existed. Heal finds market-open minutes the store does not have, using the same New York session logic as every other freshness decision, and downloads only those windows, bounded by `--days` and `--max-minutes` so it is safe on a timer; windows that do not fit the budget are reported as deferred rather than dropped. It also reports `unfilled_minutes` per window, because the broker has no bar for a minute in which nothing quoted: measured live, every window that survived a heal sat on the 21:00–22:00 UTC daily-break boundary and was unfillable rather than lost.

`xauusd-data-update.timer` runs `data update --heal`, bounded to 3 days back and 120 missing minutes per run, so a hole closes on the next scheduled refresh instead of waiting for someone to notice it. A heal failure is reported inside the result and never fails the refresh itself: the store is still current, and the status file drives the live view's data-update alert, so letting heal trouble mask a good download would cry wolf four times a day.

The feed also keeps a bounded transition log at `reports/data_feed_events.json` — the last 200 state changes plus a `dropped` count. The status file holds only the latest state and these services write no journald logs, so a feed that crashed and was restarted by systemd previously left no trace at all: the 2026-10-12 outage was datable only by correlating a hole in the store against `ExecMainStartTimestamp`. Only transitions are recorded, not bars, and a failing event log is logged and ignored — losing the log must never cost the data it describes.

## Active Codex agent

The deployed planner is `AGENT_PLANNER=codex`. It uses a persistent Codex thread,
structured server tools, isolated tc02 research, an independent paper monitor,
and tested application releases. See [the active agent runbook](docs/operator-runbook-agent.md)
and [qualification and paper operation](docs/operator-runbook-codex.md).

```bash
.venv/bin/python -m xauusd.cli agent status
.venv/bin/python -m xauusd.cli paper status
.venv/bin/python -m xauusd.cli state integrity
```

Do not run another `agent run` or `agent once` beside the service. `/` and `/lab`
serve the current read-only dashboard; `/legacy` serves the older transcript view.
The feed, view, agent and halted deterministic engine are separate processes.
A closed market does not stop research. No strategy currently has an established
profitable edge, and visible activity does not establish one.

Datadog settings and recovery procedures belong to the [optional legacy planner](docs/legacy-datadog-planner.md).
Account start/reset/recovery and risk changes remain operator-only.

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

## Historical implementations

Earlier delivery stages and deployment findings are preserved in
[project history](docs/legacy-project-history.md). Optional tournament/ML tools,
Datadog planning and older dashboard entry points remain available; they are not
started by the Codex deployment. Their import, CLI and service references must be
audited before removal.

## Local Python environment

Create the environment on each host; never commit `.venv` or a link to another
host’s temporary directory. Python bytecode is generated locally and ignored.

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest tests -q -p no:cacheprovider
```

Rebuilding the environment does not authorize starting paused services.

## Required update workflow

For every project update, refresh Graphify with `graphify update .`, update
`README.md` and `AGENTS.md` to reflect the change, run the required checks,
and commit and push the update. Keep credentials, runtime state, generated
market data, and unrelated existing changes out of commits. Report any failed
check or push explicitly.

## Codex efficiency — 2026-10-23

The research/advisor child explicitly pins `gpt-6-luna` with low reasoning effort,
including `exec resume` calls. It retains the same persisted Codex thread ID and
80,000-token automatic compaction trigger. No account, risk, strategy validation,
or execution privileges change with the model. Local user model defaults are ignored.

Per-turn briefs project repeated account histories and result bodies into concise
summaries. Current account, risk limits, constraints and unresolved-action records
are preserved. Training bars remain in `train.parquet`; large retained tool results
have evidence references. `evidence_read` accepts `call_id`, zero-based `offset`,
and `limit` (1–4000 characters); follow `next_offset` until null. It never executes
the original action. Preview text is not complete evidence. Existing tool-output
retention limits still apply; an unavailable or previously truncated result must
not be treated as fully observed.

The `codex_usage` field of `/api/lab` and the dashboard's
Codex efficiency block expose the observed model, latest input/cached/output token
counts, brief size and native session compaction count/timestamps. Counters are
read incrementally from the local session log with a persisted byte cursor; raw
session content is never returned or copied into state. Missing telemetry displays
unavailable rather than zero. Cumulative usage and compactions include the session's
previous model, so they do not establish savings from Luna or identify a bill.
The compaction threshold is a context trigger, not a time schedule. Keep the
operating prompt focused on one measurable task, reusable commands, compact results
and evidence references; evaluate retries and completed findings alongside tokens.

Committed branch history was consolidated into `main` on 2026-10-23. Updates
are published to `main`; unrelated local cleanup and runtime data remain outside
this release. The previously deployed harness modules and their integration tests
are included as prerequisites for the Luna efficiency update.

## Dashboard navigation — 2026-10-23

The read-only dashboard now has four keyboard-accessible tabs. Overview keeps
account metrics visible and shows the current task/blocker, market and equity
charts, latest three findings, running/recently failed jobs, and main-account
positions. Experiments compares independent unvalidated accounts and their
retirement reasons, with detailed records collapsed. Research contains the full
agenda, findings, candidate pipeline and activity stream. System contains Codex
usage/compaction, tool/release diagnostics, data, storage and full job history.
Measured account results take priority over the smaller aspiration label.
Arrow keys, Home and End navigate tabs; hidden charts redraw on returning to
Overview. Browser surfaces remain GET-only and issue no operator commands.


## Research activity chat — 2026-10-23

Research opens with the read-only live agent activity chat. Messages run oldest to newest, with Codex, tool and harness labels and expandable evidence. Auto-follow pauses when the reader scrolls up; Jump to latest resumes it. Refreshes preserve expanded evidence and do not rebuild an unchanged feed. Existing filters and UTC-day archival remain in place.


## Dashboard statistics — 2026-10-23

The read-only Statistics tab refreshes with the dashboard and consolidates retained research verdicts, research sessions, qualification outcomes, experiments, improvement states, tool calls and tc02 request outcomes. Completed remote calls count as successful only with an explicit successful result. It also shows cumulative persistent-thread Codex usage and cached share, latest-call usage, compactions, current paper/UTC daily metrics, data freshness, storage, release status and risk limits. Retained counts are not lifetime totals; remote CPU-hours, utilization and lifetime backtest totals remain unavailable. No execution or risk controls change.

## Harness maintenance — 2026-10-24

Research outcomes optionally carry family, dataset/code identity, parameters,
costs, finite metrics, failure reason and parent finding. `research_lookup`
retrieves retained summaries; equivalent experiment identities deduplicate.
These are advisor claims backed by tool output, not strategy qualification.

Statistics now include atomic cumulative counters since installation and 90 UTC
daily aggregates. They survive detailed-log pruning; earlier lifetime counts are
unknown. tc02 reports measured child CPU seconds and wall seconds for new jobs,
not whole-server utilization. Unknown outcomes retain IDs, ages and inspection
blockers. Inspection and reconciliation remain available at the action limit.
Remote output retention keeps compact job status/idempotency metadata.

The feed persists a 60-second process heartbeat even when the market is closed,
without clearing failures or refreshing the last market bar. Dashboard coverage
uses Parquet metadata; charts stream bounded batches and cache compact aggregates.
Regenerable Graphify caches and dated snapshots are ignored by Git; retention
keeps the latest three snapshots and any from the last seven days, and preserves
pins, unknown files, active research and recovery archives.

See the [cleanup checklist and findings](docs/cleanup-plan-2026-10-24.md).

A planned feed shutdown (including the bounded demo-host smoke test) records
`stopped` without a transport error. Unexpected disconnects retain their failure
status and the existing continuous reconnect behavior.

## Research and measured self-improvement — 2026-10-24

The Luna advisor now receives a six-topic research program, source-backed insights,
compact failure lessons and measured bottlenecks. New research compute requires an
immutable plan and a durably reserved variant; results and plans survive cycle
boundaries. Search leads, retrieved evidence and advisor interpretations remain
separate, with source provenance and no assumption of historical availability.

Observed overhead can seed an improvement task and measured baseline. A later
verified release is compared using at least ten samples per window; deployment,
measured productivity and profitable trading are distinct milestones. Research
warnings stay visible while software release readiness separately checks operational
health. All trading controls, the engine halt and the persistent Luna session remain
unchanged. See the [research program runbook](docs/operator-runbook-research-program.md)
and [implementation plan](docs/research-program-plan-2026-10-24.md).

Explicit bounded evidence pages and fetched source excerpts reach the advisor
intact; context compaction does not turn a requested page into another preview.
Large unsolicited results still use previews and durable retrieval references.

## Database retention — 2026-10-24

Operational database logs use a rolling **seven-day UTC retention** window,
checked hourly by `xauusd-db-maintenance.timer`. Expire old transcript/event/job
log bodies and monitor marks; preserve learning, referenced evidence, active and
unknown work, account state, stops and trade idempotency. Expired terminal shell
output becomes an explicit digest-marked tombstone; job/request identity remains.
Older undated jobs get a seven-day first-observed grace period, never an invented
creation date. Existing shorter row/byte caps still apply.

Maintenance uses bounded transactions, indexes, passive WAL checkpoints and
incremental vacuum after initial conversion. The scheduled service never runs a
blocking full VACUUM. One-time `python -m xauusd.database_retention --compact`
requires the agent, engine and view to be stopped, checks integrity before/after,
and never starts accounts or clears the engine halt. The read-only Storage view
shows maintenance and compaction results. See
[database maintenance](docs/operator-runbook-database.md).

### Research completion and repair — 2026-10-26

The harness now prioritizes completed evidence over activity: two running plans,
one working repair, and recorded findings before further computation. Workspaces
include an audited UTC-timestamped training CSV; multi-bar return features exclude
entire gap-straddling lookbacks. Exact cross-workspace evidence and research-file
hashes survive call-log rotation in bounded plan records. `result_summary` supplies
compact structured metrics before raw paging. Overview and Research lead with
outcomes, shared blocker categories, repair escalations and measured-benefit state;
the live chat follows. Productivity still needs real post-release samples.
See [implementation and verification](docs/research-completion-2026-10-26.md).

Research recovery now bounds missing remote-job investigations to two recorded
`not_found` checks. Investigated outcomes remain unknown and non-replayable;
only dependent plans are parked, freeing independent research slots. Research
shows actual stagnation cycles, pending checks and historical unknown counts.

Research completion repair (2026-10-27): tool-call evidence now retains complete
JSON up to 256 KiB instead of storing a 14,000-character fragment. Larger results
fail explicitly and require a bounded artifact summary. Experiment reviews report
success explicitly and expose compact account decision fields. Recent bottlenecks
use the same 20-call window as metrics; recurring verified issues reopen planned
repairs without erasing release history. Each advisor turn receives a durable
research stage (interpret result, repair, or independent experiment). Full paper
slots do not block independent research. These changes do not qualify a strategy
or change any trading controls.

The tc02 upload uses SSH compression and reports payload size, elapsed transport
time and timeout/exit status without retaining transport output. A transport
failure remains uncertain and is never retried automatically. The operator's
2026-10-27 full-training smoke timed out before a remote job record was found;
compression targets that transfer overhead without changing job identities.

Advisor prompts prioritize one concrete stage action, interpreting completed results
before general discovery. Project inspection is requested only for a specific
repair; the JSON tool contract is stated explicitly to avoid shell-based API discovery.

Current result interpretation now receives exact-call metrics/provenance and plan
identity directly. Historical blocked plans cannot preempt it. Context keeps four
recent tool results plus explicit older references and compact plan identities;
full immutable records remain available from the state store.

The current stage and its explicit server metrics are also embedded in the actual
Codex prompt, avoiding dependence on partial shell reads of a large brief. An
unvalidated research summary does not imply that its measured fields are absent.

### Measurable learning loop — 2026-10-27

See [the implementation checklist](docs/learning-loop-plan-2026-10-27.md).
Experimental paper accounts collect bounded prospective midpoint/net/cost
attribution and receive seven-day evidence-linked reviews. Legacy entry quotes
are never reconstructed. A paired training runner compares one frozen change on
the same data/costs with data, config and code hashes. Operator/autonomous call,
finding and cycle provenance feeds separate software/research/trading scorecards
in Research and Statistics. Historical provenance stays unknown; operator checks
and software releases do not establish autonomous strategy discovery or profit.
