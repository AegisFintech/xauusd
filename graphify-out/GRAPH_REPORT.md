# Graph Report - xauusd  (2026-09-23)

## Corpus Check
- 119 files · ~85,912 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 6, .service 4, .example 1)

## Summary
- 1920 nodes · 5402 edges · 93 communities (75 shown, 18 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 295 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd26b7d7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_bits_runner.py
- test_autonomous_harness.py
- OperationsManager
- dashboard.py
- ConfirmedBreakoutCanarySource
- ExperimentRegistry
- CockroachCTraderDemoStore
- firecrawl_research.py
- MemoryRegistry
- ml_models.py
- test_ctrader_demo.py
- ExecutionConfig
- main
- PaperTrading
- self_improve.py
- _paper_to_demo_coordinator
- ml_campaign.py
- Any
- test_agent_loop.py
- portfolio_research.py
- autonomous_harness.py
- test_agent_view.py
- agent_loop.py
- ShadowTradingReadiness
- XAUUSD discovery, incident, quantitative, and scaling audit
- cli.py
- test_demo_runner.py
- canonical_json
- SQLiteAgentTranscriptStore
- test_demo_execution.py
- test_oauth.py
- TournamentDataset
- test_search_space.py
- synthetic_bars
- memory_registry.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- test_strategy_proposals.py
- ToolExecutionError
- HistoricalDataStore
- local_state.py
- SecretFilter
- test_ctrader_auth.py
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- BitsError
- SQLitePaperTradingStore
- pytest
- test_automation.py
- BitsAgentRunner
- ctrader_demo.py
- .execute
- test_validation.py
- .from_env
- Adapter
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- verify_result_parity.py
- test_offline.py
- graphify reference: query, path, explain
- Repository Operating Rules
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- InMemoryCTraderDemoStore
- DemoAutomationRunner
- datetime
- Architecture and data-flow map
- InMemoryHarnessStore
- opencode.json
- DemoRunnerConfig
- agent_view.py
- read_status
- CodexImprovementWorkflow
- test_health_uses_configured_cockroach_registry
- core.py
- CockroachHarnessStore
- DemoLifecycle
- HarnessStore
- PaperTradingStore
- _download_with_retry
- .run
- RemoteComputeBridge
- step_display

## God Nodes (most connected - your core abstractions)
1. `MemoryRegistry` - 88 edges
2. `ExperimentRegistry` - 75 edges
3. `PaperTrading` - 75 edges
4. `main()` - 57 edges
5. `XAUUSD discovery, incident, quantitative, and scaling audit` - 54 edges
6. `canonical_json()` - 45 edges
7. `HistoricalDataStore` - 44 edges
8. `InMemoryPaperTradingStore` - 44 edges
9. `BitsError` - 41 edges
10. `synthetic_bars()` - 40 edges

## Surprising Connections (you probably didn't know these)
- `12. Status of evidence` --references--> `OpenAICompatiblePlanner`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → xauusd/autonomous_harness.py
- `Clean lease-drained saturation benchmark — 2026-08-20` --references--> `completed()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → tests/test_adaptive_search.py
- `8. Prototype gate and test plan (execute BEFORE any cutover)` --references--> `tool()`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → tests/test_autonomous_harness.py
- `Engineering` --references--> `agent_transcript_store_from_env()`  [INFERRED]
  AGENTS.md → xauusd/agent_loop.py
- `P0/P1 implementation updates — 2026-08-20` --references--> `failure_code()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → xauusd/distributed_compute.py

## Import Cycles
- None detected.

## Communities (93 total, 18 thin omitted)

### Community 0 - "test_bits_runner.py"
Cohesion: 0.12
Nodes (17): Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_market_windows_use_observed_data_and_handle_missing_source(), test_nested_output_page_preserves_original_cursor_without_skipping_text(), test_research_progress_is_idempotent_and_resets_only_on_changed_notes(), Planner, runner(), test_complete_action_feedback_cycle() (+9 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.31
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "OperationsManager"
Cohesion: 0.12
Nodes (19): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+11 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (63): asyncio, fastapi_security, fastapi_testclient, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected) (+55 more)

### Community 4 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.15
Nodes (22): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+14 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.08
Nodes (26): Gate-failure and near-pass analytics — 2026-08-21, ExperimentStatus, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence() (+18 more)

### Community 6 - "CockroachCTraderDemoStore"
Cohesion: 0.41
Nodes (4): _canonical_json(), CockroachCTraderDemoStore, _now(), Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "firecrawl_research.py"
Cohesion: 0.09
Nodes (21): test_postgres_connection_uses_configured_read_committed(), client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit() (+13 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "ml_models.py"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.10
Nodes (26): adapter(), FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation() (+18 more)

### Community 11 - "ExecutionConfig"
Cohesion: 0.19
Nodes (17): main(), bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path(), test_compact_attribution_metrics_reconcile_and_measure_concentration(), test_signal_executes_at_next_open_without_lookahead(), test_spread_slippage_and_commission_are_charged_both_sides(), test_stop_wins_ambiguous_intrabar_path() (+9 more)

### Community 12 - "main"
Cohesion: 0.16
Nodes (15): test_agent_transcript_backend_selection_defaults_to_local(), agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., agent_controller(), _agent_data_refresh_source(), _agent_status_path(), _agent_status_view(), bits_recover() (+7 more)

### Community 13 - "PaperTrading"
Cohesion: 0.10
Nodes (39): paper_trading(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_bits_notes_only_does_not_repeat_history(), test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_paper_only_skips_broker_dependencies(), test_demo_automation_requires_explicit_positive_volume(), test_demo_automation_status_reports_paper_only_flag() (+31 more)

### Community 14 - "self_improve.py"
Cohesion: 0.13
Nodes (20): base64, CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal() (+12 more)

### Community 15 - "_paper_to_demo_coordinator"
Cohesion: 0.15
Nodes (9): test_volume_policy_from_metadata(), _paper_to_demo_coordinator(), CTraderVolumeConversion, CTraderVolumePolicy, DemoExecutor, Protocol, Explicit conversion from paper quantity units to cTrader volume-in-cents units., Broker-declared volume constraints; a volume failing any rule must be rejected… (+1 more)

### Community 16 - "ml_campaign.py"
Cohesion: 0.13
Nodes (26): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, sklearn_metrics, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future() (+18 more)

### Community 17 - "Any"
Cohesion: 0.18
Nodes (8): CTraderDemoOpenApiTransport, failed(), issue(), succeeded(), Any, Synchronous, bounded cTrader demo transport. Construction and import are inert.…, Read-only broker volume/price metadata for the resolved demo symbol., Return ``(code, description)`` for a cTrader error message, else None.

### Community 18 - "test_agent_loop.py"
Cohesion: 0.09
Nodes (37): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), refresh_config(), refresh_runner(), ScriptedPlanner (+29 more)

### Community 19 - "portfolio_research.py"
Cohesion: 0.17
Nodes (22): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), read(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete() (+14 more)

### Community 20 - "autonomous_harness.py"
Cohesion: 0.19
Nodes (13): concurrent_futures, 3. Where the planner is wired today (confirmed), 6. Safety and repository-rule compliance (unchanged), 8. Prototype gate and test plan (execute BEFORE any cutover), ValueError, _check_reason(), OpenAICompatiblePlanner, parse_action() (+5 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.12
Nodes (7): test_age_seconds_parses_timezone_aware_timestamps(), test_health_degrades_when_ticks_never_reach_the_planner(), test_health_does_not_alert_below_the_stale_tick_threshold(), test_paper_endpoint_reflects_accepted_fill(), _write_heartbeat(), urllib, _age_seconds()

### Community 22 - "agent_loop.py"
Cohesion: 0.11
Nodes (33): math, typing, build_agent_registry(), canary_signal_tool(), handler(), _decision_id(), paper_state_tool(), _positive_float() (+25 more)

### Community 23 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (11): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), Path (+3 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "cli.py"
Cohesion: 0.24
Nodes (17): collections, dataclasses, hashlib, json, logging, numpy, os, pandas (+9 more)

### Community 26 - "test_demo_runner.py"
Cohesion: 0.27
Nodes (10): DecisionSource, MarketSource, paper_only_runner(), runner(), test_cycle_failure_stops_after_configured_consecutive_failures(), test_disabled_config_does_not_reconcile_or_start(), test_paper_only_start_skips_broker_reconciliation_and_runs_cycle(), test_stale_market_data_and_no_decision_do_not_execute() (+2 more)

### Community 27 - "canonical_json"
Cohesion: 0.13
Nodes (15): canonical_json(), CockroachPaperTradingStore, _default_state(), market_is_open(), _now(), PaperDecision, transition(), transition() (+7 more)

### Community 28 - "SQLiteAgentTranscriptStore"
Cohesion: 0.22
Nodes (5): Row, _now(), Local SQLite replacement for the CockroachDB agent transcript store., Close interrupted runs left 'running' by a killed process., SQLiteAgentTranscriptStore

### Community 29 - "test_demo_execution.py"
Cohesion: 0.20
Nodes (18): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches(), test_duplicate_decision_cannot_produce_another_broker_request() (+10 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.05
Nodes (47): Bits agent instructions, Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration (+39 more)

### Community 31 - "TournamentDataset"
Cohesion: 0.11
Nodes (19): dataset(), test_content_change_creates_new_version(), test_frozen_dataset_is_reproducible_and_partitioned(), test_partitions_read_exact_manifest_counts(), test_tampering_is_detected(), setup_runner(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed() (+11 more)

### Community 32 - "test_search_space.py"
Cohesion: 0.23
Nodes (15): E. Current 50,000-scenario architecture and benchmark, dotenv, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix() (+7 more)

### Community 33 - "synthetic_bars"
Cohesion: 0.13
Nodes (24): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+16 more)

### Community 34 - "memory_registry.py"
Cohesion: 0.18
Nodes (3): copy, MemoryConnection, MemoryCursor

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.06
Nodes (27): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+19 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.20
Nodes (9): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 9. Cost and latency tradeoffs (+1 more)

### Community 37 - "test_strategy_proposals.py"
Cohesion: 0.16
Nodes (8): test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), novel_proposals(), Proposal, ProposalEngine, ContinuousTournamentWorker

### Community 39 - "HistoricalDataStore"
Cohesion: 0.09
Nodes (33): test_data_update_does_not_retry_auth_errors(), download(), demo_env(), downloader_config(), minute_60(), one_bar_at(), test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host() (+25 more)

### Community 40 - "local_state.py"
Cohesion: 0.16
Nodes (23): gzip, sqlite3, decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_refuses_garbage_archive() (+15 more)

### Community 41 - "SecretFilter"
Cohesion: 0.16
Nodes (12): memory(), fixture, reply(), test_history_size_and_excerpts_are_explicit(), test_memory_retains_recent_exchanges_and_source_linked_digest(), test_notes_preserve_structured_claims_and_reject_oversize(), Suppress whole values, not partial/redacted credentials. Not a shell sandbox., SecretFilter (+4 more)

### Community 42 - "test_ctrader_auth.py"
Cohesion: 0.12
Nodes (33): account(), test_demo_accounts_empty_when_all_live(), test_demo_accounts_filters_live_and_missing_flag(), test_is_error_extracts_code_and_description(), test_is_error_none_when_clear(), test_resolve_symbol_falls_back_to_first_match(), test_resolve_symbol_prefers_enabled_match(), test_resolve_symbol_rejects_invalid_id() (+25 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 49 - "BitsError"
Cohesion: 0.17
Nodes (20): main(), call(), envelope(), parametrize, shell_action(), test_refuses_invalid_envelopes(), test_refuses_invalid_shell_limits(), test_strict_json_and_arbitrary_command() (+12 more)

### Community 50 - "SQLitePaperTradingStore"
Cohesion: 0.13
Nodes (21): Connection, decision(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store(), test_sqlite_integrity_check_detects_corruption(), test_sqlite_paper_store_corrupt_state_fails_closed(), test_sqlite_paper_store_integrity_check_reports_ok(), test_sqlite_paper_store_kill_switch_persists_and_fails_closed() (+13 more)

### Community 51 - "pytest"
Cohesion: 0.18
Nodes (12): pytest, action(), jobs(), fixture, test_cancel_process_after_output_streams_close(), test_execution_idempotency_and_conflict(), test_interrupted_job_never_replayed(), test_secret_output_is_not_persisted() (+4 more)

### Community 52 - "test_automation.py"
Cohesion: 0.14
Nodes (17): test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_html_report_contains_candidates(), test_registry_only_promotes_passing_better_candidate(), test_run_lock_rejects_overlap(), test_weekly_comparison_collects_archived_runs(), append_jsonl(), atomic_json() (+9 more)

### Community 54 - "ctrader_demo.py"
Cohesion: 0.09
Nodes (13): build_new_order_request(), build_reconcile_request(), CTraderDemoAdapter, CTraderDemoStore, CTraderTransport, Protocol, Fail-closed cTrader Open API execution boundary for verified demo accounts., Executes only persisted, reconciled XAUUSD demo-order proposals. (+5 more)

### Community 55 - ".execute"
Cohesion: 0.39
Nodes (5): Any, datetime, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it.

### Community 56 - "test_validation.py"
Cohesion: 0.14
Nodes (19): Dependence-aware bootstrap validation — 2026-08-21, test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_parameter_neighbors_change_one_value(), test_validator_writes_report_and_does_not_promote_weak_strategy(), validate_strategy(), bootstrap_trade_paths() (+11 more)

### Community 57 - ".from_env"
Cohesion: 0.29
Nodes (6): 7.1 Code — one relaxation (small, tested), 7.2 Deploy — one systemd unit (mirror rule applies), 7.3 Config/docs, 7. Required changes (tracked, not yet implemented), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout()

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.08
Nodes (15): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), CockroachAgentTranscriptStore, ContinuousAgentRunner, Any, Protocol (+7 more)

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 64 - "Repository Operating Rules"
Cohesion: 0.18
Nodes (9): Autonomous Harness, Datadog Bits operations, Engineering, Execution Boundary, graphify, Operations, Purpose, Repository Operating Rules (+1 more)

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

### Community 71 - "InMemoryCTraderDemoStore"
Cohesion: 0.18
Nodes (3): _initial_state(), InMemoryCTraderDemoStore, Test double only; production execution state belongs in CockroachDB.

### Community 72 - "DemoAutomationRunner"
Cohesion: 0.30
Nodes (4): DemoAutomationRunner, Any, Poll injected sources only after explicit enablement and reconciliation., Reconcile first, then make the explicitly enabled paper/demo pair runnable.

### Community 73 - "datetime"
Cohesion: 0.11
Nodes (23): contextlib, datetime, fcntl, re, Two-invocation, no-trading smoke test of Bits -> shell -> Bits. Run from the…, selectors, signal, sys (+15 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 77 - "DemoRunnerConfig"
Cohesion: 0.33
Nodes (6): test_environment_config_is_disabled_unless_explicitly_true(), demo_automation(), _demo_automation_status(), Run the explicitly enabled local-data paper-to-demo canary., DemoRunnerConfig, datetime

### Community 78 - "agent_view.py"
Cohesion: 0.21
Nodes (12): FastAPI, fastapi_responses, fixture, server(), create_app(), data_update_status(), health(), paper_endpoint() (+4 more)

### Community 79 - "read_status"
Cohesion: 0.35
Nodes (10): test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), Any, Path, Atomic on-disk heartbeat for the continuous agent. The agent writes no…, Persist one heartbeat atomically (temp file + fsync + rename). (+2 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 82 - "core.py"
Cohesion: 0.27
Nodes (8): test_backtest(), campaign(), event_backtest(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 84 - "DemoLifecycle"
Cohesion: 0.22
Nodes (4): DemoLifecycle, MarketDataSource, Protocol, Read-only source for the latest executable market observation.

### Community 88 - "_download_with_retry"
Cohesion: 0.33
Nodes (4): test_data_update_retries_transient_failures(), _download_with_retry(), Any, Transient-failure retry around a scheduled data download; auth errors are…

### Community 89 - ".run"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

### Community 90 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (21): P0/P1 implementation updates — 2026-08-20, Exception, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible() (+13 more)

### Community 94 - "step_display"
Cohesion: 0.33
Nodes (6): test_bits_decisions_show_summary_instead_of_protocol_json(), test_shell_command_and_output_are_not_in_collapsed_text(), steps(), Any, Presentation only: never turns an assessment into a confirmed execution., step_display()

## Knowledge Gaps
- **119 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+114 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 536 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `Repository Operating Rules`, `local_state.py`, `datetime`, `canonical_json`, `main`, `agent_view.py`, `_paper_to_demo_coordinator`, `test_agent_loop.py`, `SQLitePaperTradingStore`, `test_agent_view.py`, `agent_loop.py`, `PaperTradingStore`, `cli.py`, `test_demo_runner.py`, `ContinuousAgentRunner`, `test_demo_execution.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `MemoryRegistry` connect `MemoryRegistry` to `test_search_space.py`, `memory_registry.py`, `dashboard.py`, `OperationsManager`, `test_strategy_proposals.py`, `ExperimentRegistry`, `AdaptiveSearch`, `CodexImprovementWorkflow`, `ShadowTradingReadiness`, `RemoteComputeBridge`, `TournamentDataset`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `What You Must Do When Invoked`, `ConfirmedBreakoutCanarySource`, `ExecutionConfig`, `main`, `PaperTrading`, `ml_campaign.py`, `test_agent_loop.py`, `core.py`, `agent_loop.py`, `test_validation.py`, `cli.py`, `TournamentDataset`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `build_agent_registry()`) actually correct?**
  _`PaperTrading` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `main()` (e.g. with `CTraderAuthError` and `CTraderOpenApiConfig`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._