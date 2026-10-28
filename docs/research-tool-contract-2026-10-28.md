# Research tool contract repair — 28 October 2026

Integration prerequisite [scalping-bot#405](https://github.com/AegisFintech/scalping-bot/issues/405),
part of [xauusd#22](https://github.com/AegisFintech/xauusd/issues/22) and the
[one-bot integration plan](https://github.com/AegisFintech/scalping-bot/issues/398).
This is an upstream research-only repair before selective import into scalping-bot.
It does not introduce another broker executor or complete all historical #22 work.

## Trigger and change

The retained runtime review observed calls to `research_execution`,
`research_recovery` and `tool_results`, which are brief fields rather than tools,
and `research_plan` calls with an incorrect shape. The static response schema
previously accepted every string as a tool name; malformed plans returned only a
code. More tokens or a synthetic finding cannot resolve this interface defect.

The actual Codex response schema now restricts names to the current advertised
catalog; its reply validator checks the same list. A missing catalog allows no
calls. Brief fields are explicitly labelled data. Existing programmatic tests
and compatibility callers can still validate a generic turn, while the production
Codex path always uses the bounded schema and validator together.

`PLAN_INPUT_SCHEMA` is the shared source of the plan's thirteen required keys
and is included in the actual advisor context. Existing semantic checks, immutable
plan identity, budgets, source requirements and reservation transactions remain.
Shape errors return known required/missing keys, allowed topics and an unexpected
field count, never supplied values or unknown field names. Invalid non-string
or unhashable topics reject safely. Earlier review prose described fourteen keys;
the actual code has thirteen, now checked directly against its schema.

The prompt tells the advisor to interpret the exact retained result with
`research_record` and await its successful receipt before closing the plan.
Existing provenance, source-availability, negative finding and no-replay rules
remain. The patch never invents an interpretation or automatically records one.
Persistent threads, model, compaction, account state, engine halt, permissions,
unknown jobs, protected data and trading gates are unchanged.

## Verification

Base: `35854ce652eb6541760c553f9176fbf5bae223fa`. Three new regressions failed
against the original source (missing name enum, missing actionable plan fields,
missing schema in real context); the existing-identity characterization passed.
With the repair, the focused tool/advisor/evidence/program/completion/learning
suites passed **64 tests**. Full isolated suite:

```sh
PYTHONDONTWRITEBYTECODE=1 /root/xauusd/.venv/bin/python -m pytest tests -q -p no:cacheprovider
```

**978 passed, 1 skipped, 1 upstream protobuf deprecation warning**, 46.63 seconds.
The unavailable optional database-backend test is not claimed verified. Tests ran
in `/root/xauusd-worktrees/issue405`, not the running source. Standards and Spec
reviews reported no blocking finding. Diff/secret checks and Graphify precede
commit/push. No provider call, broker command, live-state edit or deployment was
performed by these tests. Deployment and fresh autonomous findings are separate
acceptance; until observed, stagnation and learning success are not declared fixed.

Rollback restores the previous research source only after normal shutdown and
preserves every new claim, finding, plan, thread and unknown execution. No state
migration/reset or unknown-job resubmission is required by this source change.
