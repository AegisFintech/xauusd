# Graph Report - xauusd  (2026-09-24)

## Corpus Check
- 120 files · ~90,088 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 6, .service 5, .timer 2)

## Summary
- 1980 nodes · 5557 edges · 94 communities (75 shown, 19 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 303 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5681960f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CockroachAgentTranscriptStore
- test_autonomous_harness.py
- OperationsManager
- dashboard.py
- ConfirmedBreakoutCanarySource
- ExperimentRegistry
- CockroachCTraderDemoStore
- firecrawl_research.py
- MemoryRegistry
- ml_models.py
- CTraderDemoOpenApiTransport
- test_ml.py
- agent_controller
- PaperTrading
- ImprovementLedger
- DemoAutomationRunner
- paper_trading.py
- Any
- test_agent_loop.py
- TournamentDataset
- OpenAICompatiblePlanner
- test_agent_view.py
- agent_loop.py
- CTraderDemoAdapter
- XAUUSD discovery, incident, quantitative, and scaling audit
- cli.py
- test_demo_runner.py
- PostgresConnection
- local_state.py
- test_demo_execution.py
- test_oauth.py
- TournamentRunner
- test_search_space.py
- synthetic_bars
- MemoryConnection
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- main
- ShadowTradingReadiness
- HistoricalDataStore
- SQLiteAgentTranscriptStore
- test_weekly_report.py
- ctrader_demo.py
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- BitsError
- test_offline.py
- CTraderDemoSafetyError
- test_automation.py
- CTraderOAuthError
- PaperDecision
- NormalizedDecision
- PaperToCTraderDemoCoordinator
- InMemoryCTraderDemoStore
- DemoLifecycle
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- verify_result_parity.py
- restart_policy
- graphify reference: query, path, explain
- XAUUSD Autonomous Research and Demo Harness
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- InMemoryAgentTranscriptStore
- .read
- PaperTradingStore
- Architecture and data-flow map
- InMemoryHarnessStore
- opencode.json
- _demo_automation_runner
- AgentTranscriptStore
- bits_runner.py
- CodexImprovementWorkflow
- cTrader SDK and protocol review (no broker connection)
- core.py
- CockroachHarnessStore
- Datadog Bits connection
- HarnessStore
- ExecutionConfig
- memory_registry.py
- .from_env
- RemoteComputeBridge
- README.md
- FakeResponse
- .run

## God Nodes (most connected - your core abstractions)
1. `MemoryRegistry` - 88 edges
2. `PaperTrading` - 78 edges
3. `ExperimentRegistry` - 75 edges
4. `main()` - 60 edges
5. `XAUUSD discovery, incident, quantitative, and scaling audit` - 54 edges
6. `InMemoryPaperTradingStore` - 47 edges
7. `canonical_json()` - 45 edges
8. `HistoricalDataStore` - 44 edges
9. `BitsError` - 41 edges
10. `synthetic_bars()` - 40 edges

## Surprising Connections (you probably didn't know these)
- `12. Status of evidence` --references--> `OpenAICompatiblePlanner`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → xauusd/autonomous_harness.py
- `Order lifecycle and errors — follow-up #15` --references--> `is_error()`  [INFERRED]
  docs/local-handoff-audit-2026-09-24.md → xauusd/ctrader_auth.py
- `Clean lease-drained saturation benchmark — 2026-08-20` --references--> `completed()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → tests/test_adaptive_search.py
- `8. Prototype gate and test plan (execute BEFORE any cutover)` --references--> `tool()`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → tests/test_autonomous_harness.py
- `Engineering` --references--> `agent_transcript_store_from_env()`  [INFERRED]
  AGENTS.md → xauusd/agent_loop.py

## Import Cycles
- None detected.

## Communities (94 total, 19 thin omitted)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.22
Nodes (16): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+8 more)

### Community 2 - "OperationsManager"
Cohesion: 0.09
Nodes (21): gzip, test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost() (+13 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (63): asyncio, fastapi_security, fastapi_testclient, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected) (+55 more)

### Community 4 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.32
Nodes (15): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+7 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.11
Nodes (11): ExperimentStatus, Path, BitsStore, Uses the same connection selected for the application's transcript store., canonical_json(), ExperimentRegistry, Any, datetime (+3 more)

### Community 6 - "CockroachCTraderDemoStore"
Cohesion: 0.41
Nodes (4): _canonical_json(), CockroachCTraderDemoStore, _now(), Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "firecrawl_research.py"
Cohesion: 0.15
Nodes (18): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+10 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.10
Nodes (16): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., test_readiness_degrades_for_unsynchronized_or_drifted_clock(), spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score() (+8 more)

### Community 9 - "ml_models.py"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 10 - "CTraderDemoOpenApiTransport"
Cohesion: 0.16
Nodes (17): FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(), test_open_api_transport_fails_reconciliation_on_an_error_reply(), test_open_api_transport_reads_symbol_volume_metadata(), test_open_api_transport_rejects_non_demo_before_constructing_client() (+9 more)

### Community 11 - "test_ml.py"
Cohesion: 0.13
Nodes (25): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined() (+17 more)

### Community 12 - "agent_controller"
Cohesion: 0.14
Nodes (14): test_agent_transcript_backend_selection_defaults_to_local(), agent_transcript_store_from_env(), _positive_float(), Transcript store for the configured backend (local SQLite by default)., agent_controller(), _agent_data_refresh_source(), _agent_status_path(), _agent_status_view() (+6 more)

### Community 13 - "PaperTrading"
Cohesion: 0.13
Nodes (32): paper_trading(), test_non_paper_only_requires_adapter_and_volume(), test_paper_only_runs_without_adapter_or_volume_and_never_stops_switches(), decision(), parametrize, test_corrupt_memory_state_fails_closed(), test_default_gate_accepts_the_newest_closed_m1_bar(), test_duplicate_decision_returns_persisted_outcome_without_second_fill() (+24 more)

### Community 14 - "ImprovementLedger"
Cohesion: 0.13
Nodes (18): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+10 more)

### Community 15 - "DemoAutomationRunner"
Cohesion: 0.26
Nodes (5): DemoAutomationRunner, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 16 - "paper_trading.py"
Cohesion: 0.17
Nodes (18): decision(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store(), test_sqlite_integrity_check_detects_corruption(), test_sqlite_paper_store_corrupt_state_fails_closed(), test_sqlite_paper_store_integrity_check_reports_ok(), test_sqlite_paper_store_kill_switch_persists_and_fails_closed(), test_sqlite_paper_store_persists_state_and_decision_idempotency() (+10 more)

### Community 17 - "Any"
Cohesion: 0.11
Nodes (8): failed(), issue(), succeeded(), CTraderDemoStore, CTraderTransport, Any, Protocol, Return ``(code, description)`` for a cTrader error message, else None.

### Community 18 - "test_agent_loop.py"
Cohesion: 0.11
Nodes (40): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), refresh_config(), refresh_runner(), ScriptedPlanner (+32 more)

### Community 19 - "TournamentDataset"
Cohesion: 0.09
Nodes (32): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), read(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete() (+24 more)

### Community 20 - "OpenAICompatiblePlanner"
Cohesion: 0.27
Nodes (9): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), ValueError, _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError, Any (+1 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.07
Nodes (33): FastAPI, fastapi_responses, test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), fixture, server(), test_age_seconds_parses_timezone_aware_timestamps() (+25 more)

### Community 22 - "agent_loop.py"
Cohesion: 0.21
Nodes (15): build_agent_registry(), canary_signal_tool(), handler(), _decision_id(), _mock_market_for_read(), paper_state_tool(), handler(), Continuous single-agent XAUUSD paper trading loop with a live, visible thinking… (+7 more)

### Community 23 - "CTraderDemoAdapter"
Cohesion: 0.09
Nodes (18): adapter(), test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_duplicate_request_never_sends_a_second_transport_call(), test_host_and_environment_rejections_are_fail_closed(), test_recovery_failure_kills_and_blocks_execution(), test_transport_failure_is_an_unknown_outcome_that_blocks_restart(), test_unresolved_pre_crash_request_fails_recovery_closed(), Transport (+10 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "cli.py"
Cohesion: 0.10
Nodes (39): base64, collections, concurrent_futures, contextlib, dataclasses, datetime, dotenv, fcntl (+31 more)

### Community 26 - "test_demo_runner.py"
Cohesion: 0.13
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 27 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 28 - "local_state.py"
Cohesion: 0.12
Nodes (31): sqlite3, seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source() (+23 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.11
Nodes (26): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+18 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.20
Nodes (13): PathLike, Market Data & Authentication, test_authorize_url_builds_documented_endpoint(), test_persist_tokens_appends_missing_key_and_sets_0600(), test_persist_tokens_rewrites_only_token_keys(), urllib_error, urllib_parse, urllib_request (+5 more)

### Community 31 - "TournamentRunner"
Cohesion: 0.10
Nodes (14): Dependence-aware bootstrap validation — 2026-08-21, setup_runner(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition(), _atomic_json() (+6 more)

### Community 32 - "test_search_space.py"
Cohesion: 0.25
Nodes (14): E. Current 50,000-scenario architecture and benchmark, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix(), from_strategy() (+6 more)

### Community 33 - "synthetic_bars"
Cohesion: 0.12
Nodes (33): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error(), test_novel_formulas_generate_valid_signals() (+25 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.15
Nodes (11): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+3 more)

### Community 37 - "main"
Cohesion: 0.12
Nodes (22): DemoTransport, no_broker(), stopped_demo_adapter(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_bits_notes_only_does_not_repeat_history(), test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_once_reports_a_refused_restart() (+14 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.14
Nodes (13): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), test_adaptive_generations_wait_for_completion_interval() (+5 more)

### Community 39 - "HistoricalDataStore"
Cohesion: 0.05
Nodes (57): Interpreter guard for subcommands, test_data_update_does_not_retry_auth_errors(), download(), test_data_update_retries_transient_failures(), demo_env(), downloader_config(), minute_60(), one_bar_at() (+49 more)

### Community 40 - "SQLiteAgentTranscriptStore"
Cohesion: 0.16
Nodes (8): Connection, Row, _connect(), _now(), Any, Local SQLite replacement for the CockroachDB agent transcript store., Close interrupted runs left 'running' by a killed process., SQLiteAgentTranscriptStore

### Community 41 - "test_weekly_report.py"
Cohesion: 0.17
Nodes (19): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+11 more)

### Community 42 - "ctrader_demo.py"
Cohesion: 0.15
Nodes (20): account(), test_demo_accounts_empty_when_all_live(), test_demo_accounts_filters_live_and_missing_flag(), test_is_error_extracts_code_and_description(), test_is_error_none_when_clear(), test_resolve_symbol_falls_back_to_first_match(), test_resolve_symbol_prefers_enabled_match(), test_resolve_symbol_rejects_invalid_id() (+12 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.19
Nodes (14): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+6 more)

### Community 49 - "BitsError"
Cohesion: 0.06
Nodes (42): main(), call(), envelope(), action(), jobs(), fixture, test_cancel_process_after_output_streams_close(), test_execution_idempotency_and_conflict() (+34 more)

### Community 50 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 51 - "CTraderDemoSafetyError"
Cohesion: 0.14
Nodes (10): test_symbol_metadata_and_volume_policy_validate_invariants(), CTraderDemoAccount, CTraderDemoSafetyError, CTraderSymbolMetadata, RuntimeError, Read-only broker price/volume constraints for the configured demo symbol., Read-only broker volume/price metadata for the resolved demo symbol., A configuration, recovery, or execution condition that must fail closed. (+2 more)

### Community 52 - "test_automation.py"
Cohesion: 0.14
Nodes (17): test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_html_report_contains_candidates(), test_registry_only_promotes_passing_better_candidate(), test_run_lock_rejects_overlap(), test_weekly_comparison_collects_archived_runs(), append_jsonl(), atomic_json() (+9 more)

### Community 53 - "CTraderOAuthError"
Cohesion: 0.20
Nodes (14): response_json(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises(), test_refresh_access_token_returns_pair_with_browser_agent(), fake_urlopen(), test_rejected_grant_raises_oauth_error() (+6 more)

### Community 54 - "PaperDecision"
Cohesion: 0.15
Nodes (10): CockroachPaperTradingStore, _now(), PaperDecision, transition(), transition(), Any, datetime, CockroachDB is the authoritative state and idempotency store in production. (+2 more)

### Community 55 - "NormalizedDecision"
Cohesion: 0.23
Nodes (9): NormalizedDecision, Any, datetime, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it., Strategy proposal expressed in configured paper-trading quantity units., DecisionSource (+1 more)

### Community 56 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.16
Nodes (13): pytest, Planner, runner(), test_complete_action_feedback_cycle(), test_market_closed_and_stopped_never_submit(), test_monitor_stops_loss_without_planner_call(), test_pending_workflow_survives_restart(), test_second_process_refused_and_uncertain_submission_stops() (+5 more)

### Community 57 - "InMemoryCTraderDemoStore"
Cohesion: 0.18
Nodes (3): _initial_state(), InMemoryCTraderDemoStore, Test double only; production execution state belongs in CockroachDB.

### Community 58 - "DemoLifecycle"
Cohesion: 0.20
Nodes (4): DemoLifecycle, MarketDataSource, Protocol, Read-only source for the latest executable market observation.

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.16
Nodes (14): Event, test_redact_bounds_untrusted_content(), _assistant_step(), ContinuousAgentRunner, Any, datetime, Display-friendly assistant step: parsed action plus the model's plain-English…, Transcript-friendly view: keep structures, bound untrusted string lengths. (+6 more)

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "restart_policy"
Cohesion: 0.15
Nodes (13): Autonomous Harness, Datadog Bits operations, Engineering, Execution Boundary, graphify, Local agent handoff — completed 2026-09-24, Operations, Purpose (+5 more)

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 64 - "XAUUSD Autonomous Research and Demo Harness"
Cohesion: 0.14
Nodes (14): Architecture, Autonomous Agent, Configuration, Current Status, Delivery Stages, Demo Automation, Demo Automation Service, Demo-Only Controls (+6 more)

### Community 65 - "graphify.js"
Cohesion: 0.40
Nodes (3): IMPORTANT: keep the reminder string free of backticks and $(...) constructs., ref_fs, ref_path

### Community 66 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 67 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 68 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 72 - ".read"
Cohesion: 0.20
Nodes (6): ConfirmedBreakoutCanaryConfig, _normalized_m1_bars(), DataFrame, datetime, Series, Most recent transition among the bars not yet observed, or None. Inspecting…

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 77 - "_demo_automation_runner"
Cohesion: 0.20
Nodes (11): test_demo_automation_requires_explicit_positive_volume(), test_environment_config_is_disabled_unless_explicitly_true(), demo_automation(), _demo_automation_runner(), _demo_automation_start(), _demo_automation_status(), _positive_env_float(), Explicit operator override for the demo execution kill switch; paper and the… (+3 more)

### Community 79 - "bits_runner.py"
Cohesion: 0.18
Nodes (12): Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_market_windows_use_observed_data_and_handle_missing_source(), test_nested_output_page_preserves_original_cursor_without_skipping_text(), test_research_progress_is_idempotent_and_resets_only_on_changed_notes(), types, excerpt(), Bounded, source-linked memory. Current account state always outranks notes. (+4 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "cTrader SDK and protocol review (no broker connection)"
Cohesion: 0.22
Nodes (9): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Local handoff audit — 2026-09-24, Local validation and deployment, Order lifecycle and errors — follow-up #15, Planner latency (read-only), Position reconciliation — follow-up #16 (+1 more)

### Community 82 - "core.py"
Cohesion: 0.27
Nodes (8): test_backtest(), campaign(), event_backtest(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 84 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 87 - "ExecutionConfig"
Cohesion: 0.15
Nodes (25): numpy, pandas, sklearn_metrics, main(), Secret-free deterministic parity fixture for the runtime container., bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path() (+17 more)

### Community 88 - "memory_registry.py"
Cohesion: 0.36
Nodes (6): copy, test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), novel_proposals(), Proposal, ProposalEngine

### Community 89 - ".from_env"
Cohesion: 0.29
Nodes (6): 7.1 Code — one relaxation (small, tested), 7.2 Deploy — one systemd unit (mirror rule applies), 7.3 Config/docs, 7. Required changes (tracked, not yet implemented), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout()

### Community 90 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (21): P0/P1 implementation updates — 2026-08-20, Exception, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible() (+13 more)

### Community 94 - ".run"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

## Knowledge Gaps
- **126 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+121 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 556 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaperTrading` connect `PaperTrading` to `main`, `PaperTradingStore`, `agent_controller`, `paper_trading.py`, `test_agent_loop.py`, `test_agent_view.py`, `agent_loop.py`, `PaperDecision`, `PaperToCTraderDemoCoordinator`, `cli.py`, `test_demo_runner.py`, `ContinuousAgentRunner`, `local_state.py`, `test_demo_execution.py`, `restart_policy`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `MemoryRegistry` connect `MemoryRegistry` to `test_search_space.py`, `MemoryConnection`, `dashboard.py`, `OperationsManager`, `ShadowTradingReadiness`, `test_weekly_report.py`, `AdaptiveSearch`, `CodexImprovementWorkflow`, `memory_registry.py`, `RemoteComputeBridge`, `TournamentRunner`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `ExperimentRegistry` connect `ExperimentRegistry` to `test_search_space.py`, `OperationsManager`, `dashboard.py`, `main`, `ShadowTradingReadiness`, `MemoryRegistry`, `test_weekly_report.py`, `AdaptiveSearch`, `CodexImprovementWorkflow`, `TournamentDataset`, `memory_registry.py`, `cli.py`, `RemoteComputeBridge`, `XAUUSD discovery, incident, quantitative, and scaling audit`, `TournamentRunner`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_maybe_resume_preserves_every_persisted_stop_except_fresh_state()`) actually correct?**
  _`PaperTrading` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `main()` (e.g. with `CTraderAuthError` and `CTraderOpenApiConfig`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._