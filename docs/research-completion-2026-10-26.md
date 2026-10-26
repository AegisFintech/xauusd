# Research completion and repair — 2026-10-26

The retained research program had one completed plan and fourteen blocked plans.
An implementation failure is not rejection of a market hypothesis. Original plans,
findings, unknown actions and account controls remain intact.

## Diagnosis and implementation

1. Inspect all blocked reasons and classify shared causes. `research_workflow`
   exposes data/schema, evidence/provenance, tool/environment, historical-source
   availability and experiment-implementation categories. Classification is a
   diagnostic of recorded reasons, not a new result or automatic resolution.
2. Supply the existing chronological training partition as `train.csv` with an
   explicit UTC timestamp and OHLCV, alongside its original indexed parquet.
   `training_schema.json` verifies ordered unique timezone-aware timestamps,
   finite positive prices, OHLC bounds and nonnegative volume; it reports gap
   count and exact CSV digest. The current cohort and its embargo are unchanged.
   Both bulky training copies are removed at cycle completion. Validation and
   holdout are never exported. Missing intervals remain missing.
3. Correct the reproduced feature defect: a return is unavailable whenever any
   interval in its full lookback is irregular. Tests cover two-minute and
   two-day gaps, the first eligible post-gap observation and prefix causality.
   This operator-authorized source correction does not open the module to
   automatic agent editing or alter execution gates.
4. Permit at most two running research plans. A successful computation on an
   open plan without a recorded finding blocks further compute reservations;
   retrieval, reconciliation, source investigation and repair remain available.
   The existing twenty-open-plan storage ceiling remains, so planned ideas can
   wait without running. Unknown variants still cannot close or replay.
5. Capture command and research-file SHA256 values before dispatch. Retain
   bounded result evidence and provenance in each plan variant, independently
   of the seven-day operational call ledger. Exact original call IDs work
   across workspaces; ambiguous suffix matching and synthetic IDs are refused.
   Older evidence is backfilled only when its exact call is still retained.
   Missing historical code or output is never reconstructed by guesswork.
6. `result_summary(call_id)` returns deterministic structured metrics, selected
   cost/chronological diagnostics, evidence digest and code/artifact hashes.
   It does not infer metrics from prose, rerun jobs or assert validation.
   New computation results include the summary in the next advisor brief;
   full bounded summary responses survive context compaction. Raw evidence
   remains pageable when needed. Dashboard/context plan summaries exclude raw
   evidence bodies; full records remain available through existing paging.
7. Permit one working improvement. The advisor follows reproduce → failing
   regression → fix → checks → deployment → linked release → measurement.
   Blocked repairs expose a concrete escalation with acceptance criteria;
   protected controls stay protected. Internet search must answer a specific
   research/data question and end in a test, interpretation or explicit park.
8. Overview and Research lead with completion counts, blockers, next completion
   step, verified release and measured-benefit status. Research chat follows the
   outcome summary and retains auto-follow, history and safe text rendering.

## Measurement and release handling

The existing retrieval-overhead baseline remains frozen (20 calls, share 0.75).
This update can be linked to that specific improvement after deployment has
been verified. It must collect at least ten real post-release calls before
reporting any measured benefit. Test fixtures and smoke requests do not count
as live productivity samples. Fewer calls alone do not establish better findings.

Operator deployments can record `research_operator_release` with verified state,
release ID, source/test evidence and the autonomous engineering release observed
at installation. Productivity samples use it only while that engineering base
is unchanged; a later autonomous release takes precedence. This bookkeeping
neither installs code nor changes the engineering rollback journal. Software
verification and productivity remain separate from trading qualification.

## Verification and limitations

New regression cases were observed failing before their fixes. Focused and full
suite checks and desktop/mobile browser checks cover completion ordering,
metrics, old-workspace evidence, bounded work, gaps and safe text rendering.
The operator audit is `reports/research_completion_audit_20261026.json` (runtime,
not committed). It measures the actual frozen training export and a dependency-
free tc02 baseline infrastructure smoke; this is not new strategy qualification.

Original blocked plans remain immutable historical records. Corrected studies
use a new plan with `parent_id`, a declared change and fresh variant; successful
old results may be interpreted from retained evidence without re-execution.
No profitable edge, daily return target or autonomous improvement is established
by this release. Pending live measurements stay explicitly pending.

### Measured pre-deployment audit

All fourteen blocked plans were reviewed: nine data/schema, three provenance,
and two environment failures. The actual training partition has 59,744 rows
and 44 irregular intervals; timestamps are present in its index. The prepared
CSV is 3,677,329 bytes. A real tc02 stdlib-only baseline smoke completed with
return code zero (0.141 CPU seconds, 0.200 worker wall seconds, excluding transfer
and SSH overhead). The baseline lost after both cost assumptions; it establishes
working infrastructure, not an edge. Original failed execution attempts are not
retroactively relabeled successful. The CSV copy was removed after the smoke.

Final source checks: 933 passed, one skipped (existing protobuf deprecation warning).
Desktop/mobile browser checks passed with inert untrusted text and no JS errors.
