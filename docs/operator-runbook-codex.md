# Codex autonomous trading lab

## Operating model

The existing `xauusd-agent.service` runs `agent run` with `AGENT_PLANNER=codex`.
This is one supervisor process, with a Codex research child per job. A separate
five-second loop marks the shared paper account and executes only qualified
strategy programs. The old `xauusd-engine.service` stays halted; the new lab has
its own paper strategy path through the same unchanged `PaperTrading.evaluate`
gates. The live feed, data-update timer and backup timer continue independently.
No cTrader execution adapter is constructed by the lab, irrespective of research
output. Browser routes are GET-only; charts and evidence filters are interactive,
but no browser surface starts, stops or places trades.

## Research and automatic deployment

1. Freeze the most recent 100,000 closed M1 rows once. The 60% training window is
   purged by 256 bars; the next 20% is validation; the final 20% is protected and
   is never evaluated for candidate selection. The frozen content hash is checked.
2. Give Codex only the training parquet, a bounded numeric sample, compact memory,
   previous expression identities and public sources. Its tools cannot read the
   live repository, credentials, protected partitions or application state. The
   child profile grants training-workspace writes and runtime-library reads.
   Auth stays in the Codex client transport, outside the tool sandbox. This does
   not change the legacy Bits arbitrary-shell permission model.
3. Codex can write research tools and behavioral tests. Sandbox pytest must pass,
   with network disabled, before immutable hash-addressed tools are reused. Such
   tests demonstrate software behavior, not profitability. Application changes may use the tested release path described in
   operator-runbook-agent.md; protected controls and their dependency closure
   cannot be automatically patched.
4. Candidates are bounded causal Python expressions, interpreted without eval or
   imports. Available OHLCV Series and rolling/lag/where arithmetic are documented
   in each workspace. EMA is a finite exponentially weighted rolling window;
   windows are at most 240. Positive lag only; no forward lookup. Live evaluation
   uses at most 8,192 rows. Direction is normalized to -1/0/1; size is fixed by the
   existing `ENGINE_QUANTITY`, never by the model.
5. Rank on train only. The best novel expression faces chronological validation
   with next-open execution, spread 0.30, slippage 0.05 and commission 3.50 per
   100-ounce lot per side. Flatten before reversing, no invented intrabar stops.
   Require 100 trades, positive expectancy/net profit, defined profit factor >=
   1.15, drawdown no worse than -10%, 75% positive chronological folds and a
   positive moving-block-bootstrap fifth percentile. Undefined metrics fail.
6. Historical pass starts a fixed seven-calendar-day prospective simulation.
   Observe fresh actual bid/ask quotes; source and receipt clocks must both be
   within five seconds. The shadow and deployed account use the same target
   decision function, side quotes, modeled slippage/commissions, and shared paper
   gates. Both monitors observe intraminute quote moves. Deduplicate orders per
   closed bar and flatten a reversal before another bar may enter the other side.
7. Require at least 99% of expected market-open minute observations, coverage near both window boundaries, and no material observation gap while exposed. Weekends and the New York daily break are excluded using the shared session function. Downtime cannot count as a completed forward test.
8. Score that forward window once, requiring 30 closed trades and the same
   financial gates, a flat account and no persistent shadow risk stop. Failure is
   terminal for that candidate, not retried until a lucky window passes. Qualified
   strategies auto-promote only while real paper is running and flat. Promotion,
   execution and forward finalization share a lock. Every trade rechecks pinned
   program/evidence identity. Existing manual/unowned exposure blocks lab orders.

Each frozen dataset has twenty research/validation attempts. After exhaustion,
Codex keeps investigating data and improving research tools, but does not keep
fishing the same validation period for a winner. The system never rolls the data
forward merely to bypass this budget. It also never uses the protected holdout
as a new comparison input. Once 100,000 newly observed closed bars exist strictly after the previous dataset
end, a new wholly disjoint cohort is frozen automatically. The old protected
holdout is not recycled. No profitable result is guaranteed.

The existing max-position, daily loss, drawdown, trade count, market hours,
freshness, duplicate and persistent-stop semantics are unchanged. In particular,
loss gates can refuse exits too; a stopped open position needs operator attention.
Returns of 10%/100% per day are aspirations, not targets that grant risk privileges.

## Visibility

`/` and `/lab`: local command centre, candlesticks with M1/M5/M15/H1/H4/D1 controls,
zoom and crosshair, equity curve, paper position/fills, candidate gates, jobs,
public commentary, command/file-change evidence and data/storage status.
`/legacy`: previous transcript view. `/api/health` includes lab and storage alerts.
`/api/lab`, `/api/lab/chart`, `/api/lab/events`: bounded read-only data projections.
Internal model reasoning is not promised or reconstructed. Commentary is the
agent's public explanation; account and deterministic evaluator records are facts.

## Commands

Use the service virtualenv prefix for every operation:

```sh
.venv/bin/python -m xauusd.cli lab status
.venv/bin/python -m xauusd.cli lab once
.venv/bin/python -m xauusd.cli lab retention
.venv/bin/python -m xauusd.cli lab prune
.venv/bin/python -m xauusd.cli lab compact-raw
.venv/bin/python -m xauusd.cli lab compact-raw-apply
.venv/bin/python -m xauusd.cli lab compress-raw
.venv/bin/python -m xauusd.cli lab compress-raw-apply
.venv/bin/python -m xauusd.cli paper status
```

`lab once` is a bounded research job and refuses while the running supervisor owns
AgentLock. It never starts paper or enables broker execution. `lab run` requires
`CTRADER_AUTOMATION_ENABLED=true`. Startup constructs/verifies Codex before the
shared restart policy; missing auth or uncertain legacy Bits jobs/workflows refuse
safely. An interrupted research job is marked interrupted, its workspace becomes
eligible for retention, and it is not blindly replayed. A fresh later job gets a
new durable identity. Account recovery commands remain operator-only.

## Configuration

Existing `.env` is retained. Set `AGENT_PLANNER=codex`; keep all demo-only and
paper-only settings. Optional defaults:

- `LAB_CODEX_TIMEOUT_SECONDS=600` (10..1200).
- `LAB_RESEARCH_SECONDS=300` (minimum 60; a pause after each bounded job).
- `LAB_RESEARCH_DOMAINS=gold.org,federalreserve.gov,bls.gov,cftc.gov,fred.stlouisfed.org`.
- `QUOTE_STATUS_PATH=reports/quote_status.json`.
- `QUOTE_HISTORY_PATH=data/quotes.sqlite`.

Codex must be installed and authenticated for the service user. Verified locally
with CLI 0.163.0. Research commands use an explicit virtualenv interpreter, rather
than relying on login-shell PATH. Named filesystem profiles and bubblewrap must
work; unsupported isolation does not silently fall back to unrestricted execution.
Configured public domains constrain command traffic through the Codex network
proxy; hosted web search is disabled. Retrieved sources retain URL, time, digest
and bounded untrusted excerpts. Large/binary responses and redirects are refused.
Additional providers/dependencies must be configured deliberately, without placing
credentials in prompts, sources, output or research files.

## Storage and retention

Authoritative lab metadata uses the selected transcript backend (`local` SQLite
or Cockroach), like paper. Bound live events to 300, jobs to 30 completed records,
equity to 10,080 minute marks, candidates to 100 plus active/observing references.
Compact memory is limited to two 4,000-character fields. Active, observing and qualified evidence is retained. Inactive prospective accounts are compacted to bounded final-metric summaries before their shadow namespaces are removed; the last twelve archived dataset cohorts plus referenced cohorts are preserved. No account reset is performed.

Research output is limited to 2 MB, one event to 8 KB, a job to 600 seconds by
default, and observed workspace usage to 50 MB with one-second checks. Completed
scratch artifacts expire after seven days; active/pinned/symlink-containing trees
are retained. Training copies are removed after each job. Tool files/tests have
per-file/total/count limits; immutable library storage is capped at 64 MiB and
512 objects/128 manifests. Full libraries refuse updates and preserve current tools.

Normalized historical candles, trade/idempotency state, active evidence and
the newest fourteen verified local-state backups plus the latest-pointer backup are preserved. Monitor-only idempotency rows older than seven days are pruned; actual trade decision IDs and paper state are retained. Old tournament backups expire
only after schema+gzip+hash verification and keeping the newest two valid copies.
Raw archives are compacted only when exact bar content and reconstruction metadata
exist in later retained pages. Stable replay ordering preserves revised values.
Lossless gzip compression verifies exact decompressed bytes before removing raw JSON originals; both formats are supported by recovery and future downloads. Malformed, pinned, symlinked and changed artifacts are retained. Plans and applied
outcomes are durable audit files. Full raw compaction scans are explicit commands;
ordinary retention runs daily off the risk-monitor thread.

Quote history samples at most once per second, retains seven days and at most
604,800 rows. Broker and receipt timestamps are separate; one-sided frames do not
refresh a two-sided quote. Raw quote history is not a complete tick tape and does
not prove live execution capacity or slippage. The broker SDK TLS limitation in
README still applies to this demo-only deployment.

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
