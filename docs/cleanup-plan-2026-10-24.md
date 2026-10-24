# Harness cleanup and improvement checklist — 2026-10-24

- [x] Review graph, source, working tree, live APIs and storage without changing trading controls.
- [x] Preserve recovery/status tools at the unresolved-action ceiling; investigate existing tc02 IDs without resubmission.
- [x] Separate feed process heartbeat from closed-bar freshness; verify against the demo host.
- [x] Add structured, evidence-linked hypothesis records and equivalent-experiment detection.
- [x] Add durable daily/cumulative operational counters and measured remote resource usage.
- [x] Display unresolved-action age/blockers and clearly scoped statistics.
- [x] Profile and bound dashboard historical data reads and resampling.
- [x] Review existing source cleanup and audit optional legacy entry points before deleting anything.
- [x] Bound generated Graphify/workspace clutter; preserve active/referenced evidence and recovery data.
- [x] Separate active Codex setup from legacy planner documentation and extract cohesive large-module responsibilities.
- [x] Run regression/focused/full tests, Graphify and diff checks; deploy, verify, commit and push.

No account start/reset/recovery, broker execution, engine resumption or risk changes are part of this work.

## Audit findings

- All twelve inspected unknown tc02 IDs returned not_found. No request was
  resubmitted and no unknown outcome was classified as success or failure.
  Historical remote cleanup deleted entire directories after ten completed jobs;
  the updated worker preserves compact terminal metadata when output expires.
- Source cleanup incorporates the existing reviewed helper/import deletions across
  ten modules. Repository references to the removed symbols were checked.
- Optional ML, tournament, distributed compute, legacy dashboard and Datadog code
  still has CLI/import references. No whole module/service was proven unused;
  these entry points are retained instead of breaking supported commands.
- Extracted dashboard market projection, transactional statistics and generated
  snapshot retention into cohesive modules. Avoided a wholesale CLI rewrite.
- Workspace inventory: approximately 1.7 GB, with completed verification snapshots
  among the largest entries. The seven-day/pin/completion retention remains in
  force; recent and unclassified research was not deleted for appearances.
- Regenerable Graphify caches are removed from the index and ignored. Current
  graph outputs remain tracked; old recognized snapshots use conservative pruning.
- Sample configuration now selects Codex and includes the previously pending
  Codex/quote settings. Runtime credentials and risk settings are untouched.
- Dashboard profiling on 2,413,939 bars: full read 0.3223 s; coverage 0.0018 s;
  M1/1000 cold 0.0894 s, cached 0.0006 s; D1/1000 cold 1.8224 s. These are single
  local measurements, not a performance SLA.
- One existing API test's injected full-frame reader was replaced with a real
  temporary Parquet store matching the new interface; assertions remain intact.

## Verification and deployment log

- Regression failures were observed before the corresponding recovery, heartbeat,
  structured-record, statistics, market-projection and graph-retention fixes.
- Desktop/mobile renderer checks passed, including unresolved ages, durable-counter
  sections, one visible panel, text-only untrusted output and no horizontal overflow.
- tc02 durable-status smoke passed. A one-second workload exposed supervisor-only
  CPU accounting; measuring inside the sandbox then returned 1.010103 CPU seconds
  over 1.101571 wall seconds. Metrics unavailable after forced termination remain
  null rather than a fabricated zero. This measures child workload CPU, not host
  utilization. The smoke itself is maintenance, not a profitable backtest.
- Initial full-suite failure identified an outdated market-reader test fixture;
  its assertions were preserved and it now uses a real temporary Parquet store.

- Final complete suite: **891 passed, 1 skipped**, with the existing protobuf
  deprecation warning. Deployed focused checks: **59 passed**. Diff checks passed.
- Deployed agent/view/feed/engine units are active. All nine installed unit files
  are byte-identical to deploy/systemd; demo-automation remains undeployed.
- Persistent Codex thread ID was preserved. Main paper cash, exposure and
  persistent stop state are unchanged; deterministic engine remains halted.
- Idle weekend heartbeat advanced without changing last-bar time. The prior
  stale-feed alert cleared. Health remains degraded for twelve unknown remote
  research outcomes and stagnant research; neither was hidden or cleared.
- Recognized generated graph snapshots reclaimed **41,259,684 bytes**, with no
  deletion errors. Research data, active work and recovery backups were preserved.
- Current and archived README links were checked. Graphify updated with local AST
  extraction; no semantic-label API call was required. Unrelated pre-existing
  OpenCode deletions, research reports and untracked design notes remain untouched.

### Broker smoke shutdown follow-up

The initial 180-second real-demo smoke subscribed successfully and retained healthy
heartbeats through the closed session. At exactly its scheduled end, the disconnect
callback incorrectly recorded transport_error. A regression test now distinguishes
planned shutdown from actual loss; the callback reports stopped only when the stop
event is set. Unexpected disconnect errors/reconnect behavior remain intact.

Follow-up verification: **892 passed, 1 skipped** in the complete suite and
31 focused feed tests passed. A fresh real-demo `data-feed once` invocation
with a 15-second verification bound subscribed successfully and returned
`stopped`, no error, zero bars (weekend closed). The production smoke bound
remains 180 seconds. No gate, account, or reconnect semantics changed.
