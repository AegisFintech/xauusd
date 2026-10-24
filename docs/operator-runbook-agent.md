# Persistent open-ended Codex agent

## Purpose and authority

The operator authorizes an evolving research and engineering agenda with a 100% net daily return aspiration. This is a research goal, not an achieved return, guarantee or reason to change risk limits. Execution remains paper-only. Existing demo pins, persistent stops, account/recovery restrictions and deterministic qualification remain authoritative.

## Decision loop

The existing agent unit uses Codex as its core advisor. Each bounded session receives its own durable agenda, compact memory, actual account/monitor state, experiment history and tool catalog. Codex can use native coding tools in a credential-free snapshot and return strict server tool calls. Actual sanitized results return on the next inference turn. Up to four turns run per session; subsequent sessions continue from persisted findings. A fresh session boundary archives prior narrative without resetting accounts, validation history or trade evidence. No operator reply is required.

The agent chooses between market observation, source discovery, new analysis methods, data/tool work, remote experiments, application engineering and strategy proposals. It is not required to propose a strategy every cycle. Changed commentary alone does not count as experimental progress; repeated unchanged evidence produces a review alert. Pre-job and inference failures are persisted and surfaced by health, while the independent paper monitor keeps its own cadence.

## Tools and compute

- market_observe: current two-sided quotes and bounded new closed M1 bars strictly after the frozen dataset end. Protected historical partitions are never exposed through this tool.
- source_search: public web leads with retrieval time and digest, marked untrusted; no result quality claim.
- source_domain/source_fetch: configure research domains and retrieve bounded HTTPS text with provenance. Private/non-global DNS targets are refused.
- analysis: arbitrary research commands in the credential-free local workspace, with runtime/output/disk limits and descendant cleanup.
- dependency_install: pinned binary PyPI wheels installed into scratch dependencies only; no unpinned transitive resolution or production environment changes. Analysis imports these through workspace PYTHONPATH.
- tc02_inspect/tc02_run/tc02_job_status: inspect the SSH worker and run isolated bounded experiments. Upload only selected scratch artifacts. Dedicated remote job control directories contain durable action-derived IDs; model code sees only work/, not host /root or /opt. Failed/unknown SSH outcomes never trigger automatic resubmission. action_reconcile retrieves recorded status without executing again.
- engineering_check/engineering_deploy: inspect proposed application changes, run the complete unchanged original test suite plus added tests, install a successful release, restart independently and verify health or roll back.

Each action intent persists before execution. Known returned failures are different from uncertain side effects. Action IDs deduplicate requests; uncertain fingerprints block blind replay under a new ID. In-flight/unknown records are retained. Read-only calls remain usable for diagnosis. Public output is bounded and sanitized; private model reasoning is neither promised nor displayed.

The verified tc02 worker has 16 CPUs, about 32 GB RAM and about 16 GB temporary disk free at inspection. Connectivity and source availability vary; measure each experiment. Existing /opt/xauusd is untouched. Remote commands use Bubblewrap filesystem isolation, clean environment, a 1200-second ceiling, 100 MB monitored workspace, bounded uploads/results, and completed scratch retention of ten jobs/seven days.

## Engineering releases

Current source/tests/docs are copied into project/; credentials, .git, data, state, reports and runtime environment are not copied. Original tests and the control kernel are immutable to automatic releases. Protected gate/auth/state dependency closure is derived from source imports. Research/application/UI modules and new methods may change; the protected kernel is not unrestricted self-rewriting.

Tests run in Bubblewrap with private network/PID/filesystem namespaces and loopback, no host credentials, no external networking. A trusted completion marker verifies pytest actually returned after all original modules were collected and tests finished; an early os._exit(0) is not success. Failed checks return bounded actionable output. Live hashes are checked again after tests; changed operator files refuse deployment. Installation intent and before-images persist before replacement; a three-release bounded journal supports rollback.

xauusd-release-verify.service independently restarts agent/view and requires a new healthy heartbeat and three consecutive healthy samples. Failure rolls back only matching installed files and restarts restored services. Conflicting operator edits are preserved and reported. Agent ExecStartPre recovers an interrupted install before loading application code, and ExecStartPost schedules pending health verification. Neither path starts paper, enables broker execution or clears the old engine halt.

Production dependency environment rollout is deliberately unavailable: dependency declarations cannot silently pass tests against old installed versions. Such changes return dependency_environment_unavailable. The agent can install research dependencies in scratch and vendor appropriate research code, while production runtime migrations remain a capability gap.

## Dashboard and controls

http://127.0.0.1:8100/ displays the 100% aspiration separately from measured paper daily return, current agenda/public assessment, tools/results, tc02 status and engineering releases. Prior activity/jobs appear as archived context; trade history remains intact. All browser routes remain read-only. /legacy preserves the earlier transcript view. /api/health reports monitor, feed, research and storage failures.

Use the existing lab status, paper status, engine status and data commands. Account starts/resets/restores/recovery and risk changes remain operator-only. Do not clear a halt to create activity. For chronological validation and seven-day observed-forward requirements, see operator-runbook-codex.md.

## UTC daily view and compute preference

The main clock is UTC. At 00:00 UTC, a fresh daily goal/progress view begins: current activity, completed jobs, visible fills and equity marks are scoped to that day. A running job may carry across midnight and remains visible. Compact research memory, account/trade audit, active positions, persistent stops, qualification evidence and per-dataset validation budgets are never reset by this display rollover. Seven compact goal-day summaries are retained. The actual paper daily-loss baseline still follows the existing UTC policy; its first new-day mark cannot forgive carried losses.

The advisor is directed to use tc02 for heavy backtesting/compute, staging scripts and permitted training data through tc02_run. This server owns orchestration, live monitoring and lightweight checks; independent final strategy qualification remains authoritative locally. If remote compute is unavailable, diagnose or defer heavy work instead of silently overloading the trading server. Market-session checks continue using America/New_York and daylight saving; the dashboard displays their results in UTC.

### Persistent Codex and experimental paper accounts (2026-10-22)

Advisor calls persist the exact Codex thread ID in the authoritative state store
and resume it across turns, research workspaces, process restarts and UTC days.
Native Codex compaction is configured at 80,000 context tokens. Fresh workspace
instructions and account/tool evidence are reread each turn; compact research
memory remains a recovery layer. Failed calls are not silently retried against a
new thread. Compaction is context based, not a daily reset.

The advisor may start up to four independent $1,000 experimental paper accounts
using `experiment_start`. They use fresh bid/ask quotes, causal expressions and
the existing deterministic paper gates. Fills and results are labelled unvalidated
and never satisfy promotion evidence. No broker adapter or engine-resume path is
added. Heavy exploratory work remains assigned to tc02. Blocked optional sources
must not monopolize the research loop; two failed approaches should be parked
while a different measurable hypothesis is tested.

`account_rebase.rebase` is operator-only, supports local SQLite, requires flat
exposure, and atomically resets only the paper ledger/baselines/idempotency and
its displayed equity history. It preserves research, the current kill switch,
and all risk configuration. Quiesce every paper writer before using it. The
operator requested $1,000 and explicitly declined a backup for this test reset.


## Evidence-driven lifecycle — 2026-10-23

The advisor has experiment_review and experiment_retire. Retirement archives a flat
account immediately; an open account becomes retiring and the monitor requests a
zero target through unchanged quote, hours, freshness and risk gates. A refused
close leaves exposure visible and occupies its slot. Archives retain the last 40
accounts; active accounts remain bounded at four. No broker adapter is added.

research_record accepts a hypothesis, verdict, conclusion and successful durable
analysis/tc02 call_id. It retains the evidence and digest, deduplicates by call,
and labels the conclusion unvalidated. The agent's interpretation is not an
independent validation result. Latest 100 conclusions are retained.
improvement_record retains up to 60 backlog items with problem/change/acceptance.
A verified item requires an engineering release newer than its creation baseline;
that verifies deployment, not the model's acceptance claim or profitability.

Stagnation tracks recorded research outcomes, retirement and verified releases.
Changing source searches, capability inspections, prose or scratch scripts does
not reset it. Alerts never stop trading or force orders.

Each workspace receives research_runner.py, a dependency-free fixed-rule baseline
runner for tc02. Export only train.parquet as timestamp/open/close CSV; upload CSV
and runner using the existing durable tc02_run capability. Parameters are chosen
before execution. Results report one-ounce price P/L, costs, chronological thirds,
best-two sensitivity and excluded gaps; they are not account returns or final
qualification. Unknown remote outcomes still require reconciliation, never replay.
The dashboard leads with completed evidence and shows lifecycle states/backlog.

## Research continuity and maintenance — 2026-10-24

Use research_lookup (optional family/id) before repeating a hypothesis. Supply
research_record experiment metadata with family, dataset_version, actual
code_sha256, parameters, costs, finite-or-null metrics, failure_reason and a
parent finding ID or null. Results remain unvalidated claims. Equivalent retained
identities deduplicate even under a new call ID. evidence_read can retrieve
finding-backed output after the original tool detail expires.

Statistics have separate retained-detail and since-installation scopes. Daily
aggregates retain 90 days; cumulative counters persist independently of logs.
CPU seconds measure remote child processes; wall seconds measure job duration.
Neither establishes full-server utilization or historical backtest totals.

At the unresolved-action ceiling, status/reconciliation/evidence/lookup stay
available. A not_found job remains unknown and cannot replay. The October 24
inspection found all twelve older unknown remote IDs missing; their outcomes
remain unproven. New worker retention expires payloads while keeping compact
status and idempotency metadata. This does not authorize Bits recovery or any
account start/reset.

Feed heartbeat updates every 60 seconds even on weekends. It preserves errors
and last-bar time; it cannot make stale prices tradable. Dashboard market reads
use metadata and bounded batch aggregation, with file-identity cache invalidation.
Generated Graphify snapshots retain three newest and seven days; pins, unknown
files and symlinks preserve a directory. Completed workspaces retain the existing
seven-day policy; active/uncertain work and recovery artifacts are preserved.
