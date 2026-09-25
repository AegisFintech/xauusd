# Requirements: reliable research-to-paper-trade workflow

Prepared 2026-09-25 from the running local state store, stored shell requests/results,
local health/paper APIs, and the implementation. This is a coding handoff, not
permission to change risk rules, reset state, resume/restart services, or enable
broker orders. Implement changes separately from deployment. Preserve user data,
credentials, arbitrary shell access, demo-only restrictions, and operator stops.

## What is actually happening

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

## P0 — Repair memory writes and actionable errors

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

## P0 — Make the service execution environment discoverable

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

Implement P0 first, then experiment continuity/current-signal correctness, decision
state, scheduling transparency, and dashboard reporting. Track milestones in GitHub,
update README/AGENTS/prompt documentation where behavior changes, run focused tests
and `.venv/bin/python -m pytest tests -q -p no:cacheprovider`, run `git diff --check`,
and run `graphify update .` after code changes. Commit and push each milestone.

This document does not authorize recovery commands, reset/restore, service restarts,
changing shell permissions or risk gates, or enabling demo broker orders. Preserve
current runtime state. Issue #19 (history-backed uncertain broker-order recovery)
remains a separate prerequisite for reliable future demo execution, not the reason
this paper session has no trades. The objective is reliable, explainable decisions
and execution when justified, not a promise of profitability or immediate trades.
