# Research program and measured improvement

## Decision cycle

The persistent Luna advisor receives a compact research program and observed
bottlenecks on every turn. Successful recent tool results carry across bounded
cycle boundaries. The full retained plan/source/insight/measurement is paged through
research_program; omitted design text is explicitly a summary, not lost evidence.

Six topics broaden the agenda: macro (rates/dollar), events, positioning,
liquidity/execution, research methods/data quality, and price/volume behavior.
Topic counters and compact family lessons survive daily display rollovers.
Three recorded rejections in a family recommend a different explanation; the
advisor may revisit with a justified changed design. Recommendations do not
confer trading privileges. Available results take priority over another experiment;
stagnation recommends new source discovery, and every fourth cycle with backlog
recommends measured improvement review. The advisor still owns the actual question.

## Discovery and sources

source_search produces untrusted leads. source_fetch uses existing configured
HTTPS domain and public-address checks. Successful server retrieval records URL,
retrieval time, digest, call ID and bounded excerpt, returning source_records IDs.
research_insight accepts topic, question, finding, next_test and 1–5 retrieved
source_ids; search leads alone cannot support an interpretation. The insight
retains compact provenance even after a source ledger entry expires.

No retrieval timestamp establishes historical publication or availability. These
are advisor interpretations, not verified facts or qualification inputs. A
point-in-time dataset needs its own documented availability checks; missing data
should block that plan and lead to another question. Source text cannot expand
permissions, disable controls, or become executable instructions.

## Preregistration and execution

research_plan requires topic, family, question, hypothesis, baseline,
dataset_version (current frozen cohort), data_requirements, source_ids (may be
empty), costs (finite nonnegative values), success_criteria, max_variants (1–12),
parent_id (plan ID or null), and change_reason. Designs are immutable; equivalent
identities return the existing plan. Modified experiments need a new linked plan.
These plans describe research; criteria are not replacements for qualification.

New server analysis/tc02_run calls require plan_id and variant_id. Native coding
and small checks retain the existing workspace sandbox; this registry is not an
OS-level restriction on native Codex execution. The server
reserves the variant transactionally before execution, stores the actual command
arguments digest, and strips planning fields before invoking the existing tool.
Unknown command fingerprints still block replay even under a different plan ID.
Reservations and unknown results are never silently removed or replayed.

After interpreting a successful result, research_record must include experiment
metadata matching its plan's family and dataset_version. It binds the finding to
the plan and updates compact family lessons. research_plan_close accepts id,
state (completed/blocked/abandoned), reason. Completion requires a finding;
reserved/running/unknown variants prevent closing. Read status/evidence instead.
No code path here calls account recovery/start/reset or resumes the engine.

## Improvement measurement

Inference duration, success and briefing bytes are measured server-side, with
120 retained samples and cumulative totals. Tool durations accompany durable
call records and aggregate counters. Recent metric windows sort by observation
time so old retained unknown jobs do not masquerade as the latest activity.

improvement_review identifies observed retrieval/inspection overhead and seeds a
single planned backlog item per measured bottleneck, preserving existing items.
improvement_record optionally names metric: tool_failure_rate,
evidence_read_share, tool_seconds, inference_seconds. The first record freezes a
baseline; repeating it cannot replace the baseline. tool_failure_rate is the
share of requests without confirmed success, including uncertain requests; it is
not a count of failed backtests. Duration/share comparisons may reflect workload
mix; they are observational, not causal evidence.

A distinct independently verified software release is needed before post-release
measurement. The advisor must mark the specific implemented improvement verified
through improvement_record; an unrelated verified release cannot satisfy the link.
The current engineering_release identity is supplied in every advisor context. At least ten samples in each window and a 10% observed change are
required. States distinguish awaiting_verified_release, awaiting_linked_verified_improvement, collecting_samples,
insufficient_baseline, improved, regressed, no_measurable_change and superseded.
A verified release is still separate from measured productivity and trading
performance. A regression calls for a normal tested corrective release; it does
not authorize untested rollback or protected-control changes.

## Release readiness and visibility

/api/health keeps all research warnings and overall degradation visible. Its
release_readiness separately includes operational alerts: account/stop, state,
monitor, feed/data, storage, agent errors and engineering recovery still block a
release. Only specifically classified research stagnation and isolated research
job uncertainty are advisory to software release verification. Unknown engineering
side effects and legacy Bits recovery problems remain operational blockers.
The worker still requires a new running Codex process, fresh heartbeat and live
healthy monitor. Research warnings cannot make stale data tradable.

Research shows topics, recommended next work, plans, source interpretations,
bottlenecks and measured improvement states. Statistics shows measured duration,
metric samples, cumulative counters and explicitly scoped retained counts. All
browser endpoints remain GET-only.

## Storage and limitations

Keep at most 80 terminal plans plus 20 open plans (a new plan reserves space),
100 sources, 100 insights, 64 family summaries with cumulative topic rollups,
120 inference samples and 60 improvement measurements. Open plans refuse further
capacity rather than evict unresolved work. Compact provenance is copied into
plans/insights before source expiration. No full OHLC history or raw web pages
are added to memory. Cumulative counters do not infer history before installation.

The integration test uses a simulated advisor and tool responses to demonstrate
loop behavior, not financial success. Actual runtime adoption is monitored after
deployment. New before/after measurements and prospective strategy windows may
remain pending until sufficient real observations exist.
