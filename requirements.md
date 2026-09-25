# Requirements: reliable research-to-paper-trade workflow

Prepared 2026-09-25 from the running local state store, stored shell requests/results,
local health/paper APIs, and the implementation. This is a coding handoff, not
permission to change risk rules, reset state, resume/restart services, or enable
broker orders. Implement changes separately from deployment. Preserve user data,
credentials, arbitrary shell access, demo-only restrictions, and operator stops.

## Merge review — 2026-09-25, baseline `cba22b2`

This revision supersedes the original priority list below. The original incident
and evidence IDs remain for reproduction, not as claims about the merged code.
Reviewed all 21 changed files, implementation paths and added tests. No application
code was changed during this review.

| Requirement area | Verified merged implementation | Remaining work |
| --- | --- | --- |
| Memory input/error handling | Canonical, compatibility and versioned forms; validation without state access; stdin/file input; safe structured rejection; versions/digests; SQLite atomic rollback | Pending-draft lifecycle and backend/concurrency acceptance below |
| Research recovery | Safe bounded pending payload, repair instruction after two rejections, health alert | Pending findings can still be discarded by unrelated successful writes; recovery is prompt guidance, not proof of repair |
| Shell environment | Shared environment builder, virtualenv PATH, optional extra paths, manifest, missing-command history/fallbacks | Discovery-failure visibility and deployment-check correctness below |
| Diagnostics | Classified tick/transport/validation errors, memory and missing-executable health alerts | Candidate/no-trade view, decision counts and scheduling explanations remain open |
| Reproducibility and live signal | Guidance improved; no experiment implementation changes | Entire original experiment/current-signal work remains open |
| Research decisions and scheduling | Existing strict action contract and one-hour clamp retained | Entire original decision-state and scheduling work remains open |

Do not rebuild the completed memory schema, CLI, environment builder or error
classification. Extend them and retain their regression tests.

### Runtime adoption is still pending

At approximately 09:21 UTC, the running agent still had run ID
`agent_1b340894c95d`, started September 24 07:05 UTC. Its heartbeat had neither
`memory` nor `capabilities`, and the live store had no capabilities manifest. It
was unstopped and waiting, with seven cycles without updated notes. Therefore
pulling the merge did not activate the new long-running runner code. Newly spawned
CLI processes can load the new files, so this is potentially a mixed-version
runtime; do not call it fully deployed.

An operator-authorized rollout must inspect active workflows/jobs first, preserve
uncertain-side-effect recovery rules, coordinate agent and view versions, and
verify new heartbeat fields plus a stored service-environment manifest. Never
blindly restart an active shell job or clear a stop. Updating
`docs/bits-system-prompt.md` does not update the Datadog agent configuration; the
operator must synchronize it separately. This task authorizes review and
requirements updates, not those operational actions.

### R1 — P0: do not lose pending findings when memory is rewritten

Confirmed in a temporary SQLite store using the merged code:

1. Save valid notes A.
2. Reject draft B containing new evidence and an invalid sources field.
3. Write the unchanged valid notes A again.
4. The result is `unchanged`, but `pending_notes` is deleted and the recovery alert
   clears. B's unpersisted evidence is lost from the pending record.

Cause: `BitsMemory.write_notes` unconditionally deletes `pending_notes` on every
successful write, including an unchanged write. A later rejected safe payload
also overwrites the previously retained payload, even if it concerns a different
finding.

Required: give pending drafts bounded durable identities and a base notes
version/digest. Resolving or explicitly superseding a draft must reference that
identity; arbitrary successful writes must not silently acknowledge it. Preserve
unresolved evidence references when replacing a draft. Keep bounded storage with
an explicit overflow/supersession policy and no secret retention. Update schema,
CLI, prompt and documentation together. Do not introduce a trading stop.

Acceptance: unchanged-write reproduction retains B; unrelated write retains B;
explicit corrected resolution clears only B; multiple failed drafts have documented
bounded behavior; interrupted resolution rolls back notes and pending state
atomically. Add stale-version/concurrent-writer tests. Validate the transaction
contract for the supported Cockroach backend before claiming database parity;
existing local rollback tests alone are insufficient.

### R2 — P1: capability discovery failure must remain visible

Confirmed with the merged `minimal_manifest('os_error')` fallback:
`prompt_view` omits its error code; `heartbeat_view` reports empty missing lists;
and the CLI check accepts a returned fallback manifest because it checks only
`required_missing`. The same issue applies to `--stored --check` when the runner
has persisted that fallback. The runner's exception fallback itself is useful and
must remain nonblocking.

Required: publish explicit discovery status (`ok`, `partial`, `failed`) and safe
error code in stored, prompt and heartbeat views. A failed/unknown manifest must
not pass a deployment check. Represent unprobed tools as unknown rather than
implicitly healthy. Include probe time and staleness in stored checks; report
invalid declared extra directories and CLI/data discovery failures separately
from missing optional tools. Keep research and risk monitoring running when
optional discovery fails; do not weaken stop rules or shell permissions.

Acceptance: inject discovery failure, persist fallback, then `--stored --check`
returns nonzero and health/context explain the failure. A real direct discovery
exception already exits nonzero and must continue to do so. Test partial discovery,
stale stored manifests, repaired tools and an optional absent tool with a working
fallback. Optional absence alone must not become a trading stop.

### R3 — P1: make experiment continuity work with the deployed backend

The original experiment requirements remain open. Additional implementation
constraint: `ExperimentRegistry` currently requires Cockroach `DATABASE_URL`,
whereas this deployment uses local SQLite. Reuse its schema/concepts with an
explicit local-capable adapter or another justified backend-compatible record
store; do not make optional database credentials a new dependency for local Bits
research. Test both backend contracts and preserve immutable artifact references.

Prioritize exact producer/data identities and current-signal timestamps before
expanding strategy searches. A fixed memory writer does not resolve contradictory
backtests, stale targets, or a weekly rule's lack of a current signal.

### Delivery order after this merge

1. R1 pending-draft preservation, then R2 honest discovery status/checks.
2. Original reproducibility/current-signal requirements plus R3 local backend support.
3. Original candidate decision state and isolated proposal-to-paper-fill tests.
4. Original requested/effective scheduling and human no-trade dashboard requirements.
5. Operator-authorized adoption, prompt synchronization and runtime acceptance.

Implementation status after this list (pending review; nothing deployed):

- R1 implemented: rejected writes become bounded `xauusd.drafts/1` drafts with durable IDs, base
  version/digest and evidence references; only `write --resolves` or `supersede --reason` closes one.
  `--base-version` rejects stale writes; overflow evicts the oldest draft into an explicit closed record;
  the legacy single pending record migrates. Tests cover the unchanged/unrelated-write reproductions,
  single-draft resolution, bounded overflow, interrupted-resolution rollback, stale bases, concurrent
  writers, and a psycopg-style transaction contract. An opt-in test (`XAUUSD_TEST_DATABASE_URL`) exists
  for a disposable Cockroach/Postgres database but has not been run, so database parity is not claimed.
- R2 implemented: manifests carry `status` ok/partial/failed with safe section error codes, `unknown`
  tool states, configuration errors and probe age; failed, partial, unknown, misconfigured or stale
  (stored, over 45 minutes) manifests fail `--check`; alerts never stop trading.
- Step 2 started: `xauusd.session_calendar.weekly_bars` provides New York session weeks with explicit
  completion status. The experiment registry, producer/input identities, live-signal separation and
  R3 local backend remain open.

Validation: 88 focused tests and the full 453-test suite passed; one existing
protobuf deprecation warning remains. `git diff --check` passed. Two additional
isolated probes reproduced R1 and R2 without touching live application state.
`graphify update .` refreshed the local graph for the merged code (2,210 nodes,
6,208 edges). Existing generated graph changes were preserved separately from
this requirements-only commit. No live Cockroach integration was exercised.
No workflow submissions, broker orders, note repairs, resets or service restarts
were performed by this review.

## Original incident evidence (pre-merge snapshot)

Snapshot at approximately 08:28 UTC (16:28 Asia/Shanghai), covering the session
started 2026-09-24 07:05 UTC, run `agent_1b340894c95d`:

- Agent is running, paper is unstopped, market is open, data refresh is successful,
  database integrity is OK. Paper cash/equity is $100,000, position is zero, no fills.
- There were 282 recorded agent responses, 61 completed cycles, and 221 shell jobs:
  178 succeeded and 43 failed. These are snapshot counts; the session continues.
- All 1,155 recorded paper decision results at that snapshot were monitor `ok`
  results, not trade fills or rejected trade proposals. No stored shell command
  invoked `agent-tool propose_trade`. Zero trades originate upstream of the gates.
- Datadog is returning decisions and the demo-host data downloader is working.
  This is not evidence of a current Datadog outage or cTrader order rejection.
  cTrader order execution is disabled by paper-only mode; no broker connectivity
  test for placing orders was performed in this review.
- The agent has tested many strategy families and declined them for weak,
  inconsistent, or cost-sensitive results. Some nonzero signals were explicitly
  rejected on research grounds. Other assessments reused historical flat targets.
  We have not independently validated every generated backtest or profitability claim.
- The current candidate is a weekly exhaustion-reversal rule with no current
  signal. Its latest reproduction disagrees with prior research (34 versus 30
  historical signals), and its performance is concentrated. Staying flat is valid.
- There are avoidable operational loops: 24 of the 43 failed jobs contain memory
  commands; eight failures report missing executables. Those categories overlap.
  Health reports six completed cycles without changed notes. Twenty-two early
  tick errors (07:07–07:12 UTC on September 24) record only `BitsError`, preventing
  retrospective identification of their exact causes. They are not current errors.

## Evidence anchors

Use the active transcript backend and `bits-job` to inspect these records. Do not
copy raw environment values or credentials into artifacts.

| Evidence | Finding |
| --- | --- |
| Job `c5ea68176942459881c9409618ac2936` | Memory payload wrapped in `notes`; CLI returns only `BitsError`. Extracted inner notes validate and are 2,571 canonical JSON characters, below the 4,000 limit. Shape is the problem for this job, not size. |
| Job `155490f0b9a44c698adfde8f8a310c56` | Memory retry fails because bare `python` is unavailable. |
| Job `1f83db0ba58841a8b5ec6de3833bf714` | `graphify` unavailable in the service shell. |
| Job `be11a2fe9b8a43ef8b6613cecb0e4df2` | `rg` unavailable in the service shell. |
| Job `91be334e3abb4a4fa0996a960c2a2297` | EMA reproduction differs by one turnover event and $2.80/oz in fold one. |
| Job `53e4380f3e2e4b01b772a46da08601b5` | Weekly reproduction: 34 versus expected 30 signals, latest signal zero, threshold 237.25; 50 trades, net 312.78 at 2.40 cost versus -47.22 at 9.60 cost, in generated report units. These are research output, not realized account P&L. |
| Transcript 14425, 14433, 14441 | Failed memory update, failed retry, final wait. Retry draft uses threshold 182.98 instead of latest output's 237.25. |
| Transcript 13876 and 14441 | Agent requests October 2 00:02 UTC and September 27 22:05 UTC respectively as a weekly review; scheduler instead caps waits at one hour. |
| `bits_state.working_notes` at snapshot | Last updated September 25 01:02 UTC, retaining earlier results despite subsequent contradictory reproduction. |

## Implemented baseline — memory writes and actionable errors (R1 remains)

Relevant: `xauusd/bits_memory.py`, `xauusd/cli.py`, `xauusd/bits_runner.py`,
`docs/bits-system-prompt.md`, associated tests.

1. Define one published, versioned memory input schema. Current CLI passes input
   directly to `write_notes`, which requires exactly `findings`, `hypotheses`,
   `rejected_approaches`, `open_questions`, and `next_steps`. Support the observed
   single `notes` wrapper as an explicit compatibility form or reject it with an
   actionable schema error. Reject ambiguous mixed shapes. Keep strict validation.
2. Include full executable command examples in runtime guidance:
   `.venv/bin/python -m xauusd.cli bits-memory ...`. Do not imply a standalone
   `bits-memory` executable exists. Publish note limits and source-reference rules.
3. Return safe structured errors with stable code, field path, expected shape,
   actual/maximum character count where relevant, and retryability. Do not expose
   arbitrary exception strings, payloads or subprocess arguments containing secrets.
   Preserve a classified error code in tick events instead of only the class name.
4. Add a validation-only memory command with no state mutation; successful writes
   return a version/digest and can be read back. Failed writes retain old notes.
5. Keep pending findings and their evidence references recoverable until a write
   succeeds. Repeated failures should trigger a specific repair task and alert,
   not another whole research cycle or a false claim that memory is uninstalled.

Acceptance: tests for raw and wrapped payloads, malformed fields, oversize notes,
secret rejection, atomic preservation, readback, and useful safe error output.
Reproduce the observed wrapper failure in an isolated store; never modify live
notes as a test. No silent truncation or unbounded memory expansion.

## Implemented baseline — service environment discovery (R2 remains)

Relevant: `xauusd/bits_jobs.py`, runner guidance, `deploy/systemd/`, documentation.

1. Provide a safe capability manifest from the same environment used by shell
   jobs: working directory, absolute Python/CLI path, availability/path/version
   of graphify and rg, supported CLI operations, data schema/access entry point.
   Do not dump environment variables. Interactive shell availability is insufficient.
2. Declare and validate required executable paths during deployment. Use absolute
   paths or an explicit service PATH. Keep both systemd copies aligned when an
   operator authorizes deployment; do not restart services for this handoff.
3. Guidance must use the verified interpreter and real data APIs. If an optional
   search tool is unavailable, provide a documented fallback and retain that fact
   across cycles. Keep arbitrary shell execution; no new command allow-list.

Acceptance: restricted-PATH subprocess tests matching service execution, including
missing tools; discovery and supported examples work without shell profile setup.

## P1 — Persist reproducible experiments and separate live signals

Relevant: existing experiment registry/data/backtest interfaces, generated research
scripts and report schema, Bits guidance and history.

1. Save an experiment's actual producer script before execution and register its
   ID, code hash, parameters, input snapshot/hash and cutoff, timezone/session
   boundaries, fold boundaries, costs and units, execution lag, and result path.
   Reuse existing registry infrastructure where possible. Avoid reconstructing
   implementation from narrative summaries or many pages of old commands.
2. Standardize report schema, including no-eligible-candidate outcomes and JSON
   serialization of numerical values. Compile generated Python before expensive
   runs. Preserve failures and partial artifacts with explicit completion status.
3. Reconcile the documented EMA and weekly discrepancies using frozen input
   snapshots and exact producer scripts. Preserve both conflicting records; mark
   unresolved results unverified rather than silently replacing the reference.
4. Separate historical fold-ending position, terminal backtest liquidation, and
   current live target. A historical `ending_target=0` must not become a current
   signal merely because it appears in a recent report. Live evaluation must record
   strategy version, input cutoff, observed time, signal validity and entry window.
5. Weekly aggregation must explicitly handle completed versus partial weeks and
   actual trading sessions/timezones. A pandas weekly label alone does not prove
   a week completed. Resolve threshold differences (182.98 versus 237.25) using
   source evidence; do not choose the number that supports a preferred decision.
6. Track reused holdouts and search attempts. Further variants on a previously
   examined holdout cannot be presented as independent untouched evidence.

Acceptance: deterministic fixture reproductions, fold-boundary accounting tests,
partial-week and DST/session tests, and a test where a historical flat endpoint
coexists with a nonzero current signal. Latest reports must link to executable
producers and immutable input identities. No claim that these repairs create an edge.

## P1 — Make research decisions and the path to a proposal explicit

1. Persist candidate states such as researching, rejected, needs-reproduction,
   forward-observation, and eligible-for-paper-evaluation. Record concrete evidence,
   missing checks, entry/invalidation/exit rules, sizing assumptions, and next task.
   Define evidence criteria before testing; do not invent new hurdles every cycle.
   Any thresholds that change risk-gate semantics need separate operator approval.
2. Each completed decision must distinguish `no_signal`, `strategy_unqualified`,
   `research_error`, `stale_data`, `market_closed`, `operator_stopped`, and
   `gate_rejected`, with source-linked facts. Extend the strict JSON contract only
   with synchronized prompt, validator and compatibility tests.
3. Research failure should resume the specific unfinished task. Retrieval should
   retain original job ID/cursor and expose small structured result summaries so
   output paging does not repeatedly exhaust the four-action cycle budget.
4. When a qualified, timely signal exists, use the existing `propose_trade`
   interface and record its authoritative outcome. A synthetic end-to-end test
   should demonstrate proposal, gate, paper fill, monitoring and closing through
   existing interfaces in isolated state. Do not place a live test trade.
5. No trade quota, forced BUY/SELL, weakening evidence to create activity, clearing
   stops, or bypassing gates. No-trade can be a correct completed decision. Forward
   shadow observations may gather evidence without changing paper or broker state.

Acceptance: tests distinguish no proposal from gate rejection and fill; an eligible
fixture reaches the paper interface exactly once, while invalid/stale/closed/stopped
fixtures remain blocked. Progress can mean a completed rejection or resolved defect,
not merely rewritten notes or a trade.

## P1 — Separate monitoring cadence from meaningful agent reviews

Relevant: `xauusd/bits_runner.py` scheduling, market calendar, health/live view.

1. Persist requested review time, effective review time, and reason for any clamp.
   Existing one-hour cap explains hourly reassessment of a weekly candidate.
2. Keep the independent account/risk monitor and freshness checks running. Avoid
   repeating expensive unchanged research merely because a periodic review occurs.
   Give the agent the wait condition and whether relevant evidence changed.
3. Compute strategy entry/review windows using its explicit session specification,
   consistent with the existing New York market calendar. Do not accept a prose
   claim that an arbitrary timestamp is the next weekly open.
4. A future scheduling-policy change must retain timely open-position supervision
   and operator-stop behavior; document it separately from risk-gate changes.

Acceptance: fake-clock tests for hourly clamp visibility, unchanged weekly waits,
new evidence, market reopen, DST and open-position monitoring. No indefinite sleep
that hides a pending job or unresolved position.

## P1 — Show humans why there are no trades

Relevant: `xauusd/agent_view.py`, health/status and transcript presentation.

1. Display execution mode (paper versus demo), account state, current candidate,
   whether it is qualified, latest signal/time, exact no-trade reason, next useful
   task, requested/effective review time and last successful research update.
2. Separately count monitor marks, proposals, gate rejections, paper fills and
   broker sends. The current paper-decisions table contains monitor results; its
   row count is not a count of trading decisions or trades.
3. Display memory-write failures, missing executables, reproduction mismatches and
   pending persistence explicitly. A healthy heartbeat does not mean research is
   progressing. Deduplicate routine cooldown/unchanged-tick noise in the human view.
4. Preserve expandable command/result/JSON details, source links and audit history.
   A cooldown skip must not look like a downloader failure simply because `ok=false`.

Acceptance: UI/API fixtures for this exact running-flat-research-blocked scenario,
no signal, failed memory write, gate rejection and actual paper fill. Plain-language
summaries must agree with authoritative state and verified results.

## Delivery and operational boundaries

Follow the updated delivery order above. The two original P0 sections now describe
implemented baselines to preserve; R1 and R2 describe their remaining gaps. Track milestones in GitHub,
update README/AGENTS/prompt documentation where behavior changes, run focused tests
and `.venv/bin/python -m pytest tests -q -p no:cacheprovider`, run `git diff --check`,
and run `graphify update .` after code changes. Commit and push each milestone.

This document does not authorize recovery commands, reset/restore, service restarts,
changing shell permissions or risk gates, or enabling demo broker orders. Preserve
current runtime state. Issue #19 (history-backed uncertain broker-order recovery)
remains a separate prerequisite for reliable future demo execution, not the reason
this paper session has no trades. The objective is reliable, explainable decisions
and execution when justified, not a promise of profitability or immediate trades.
