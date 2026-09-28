# Operator-authorized activation and panel reset — 2026-09-28

The operator requested activation of the merged code and a panel reset. Deployed
application revision: `72e18ee` (PR #24). Before stopping, the cycle was idle,
there were no running shell jobs, and the paper account was flat at $100,000.

Stopped paper and the agent, then used the supported atomic session reset.
Verified pre-reset backup: `backups/local-state/20260928T023825Z`.
Reset cleared paper decisions, transcript, jobs, cycles and harness memory;
source, credentials and research/market-data files were preserved.

Explicitly started paper and restarted the agent and dashboard. New run:
`agent_5764ff40f7dd`, started 2026-09-28 02:38:44 UTC (10:38 Singapore).
Paper-only mode remains in effect. No broker order execution was enabled.
The Datadog-hosted system prompt was not changed by this deployment; its
synchronization remains a separate operator configuration step.

Validation: full suite 490 passed, one skipped, one existing protobuf deprecation
warning. The fresh store had one run and session_start as its first transcript
event. Local health initially returned OK, no alerts and database integrity OK.

At 02:39 UTC the new heartbeat included capability status OK and memory status OK
with zero open drafts. Datadog returned its first response and the harness started
its shell action. Market refresh and the independent monitor were OK; local health
had no alerts. Optional graphify and rg were reported unavailable in the service
PATH with fallback guidance. This verifies new runner adoption, not strategy
profitability or a paper fill. No trades had occurred at verification.
