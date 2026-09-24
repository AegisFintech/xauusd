# Graph Report - xauusd  (2026-09-24)

## Corpus Check
- 122 files · ~92,432 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 6, .service 5, .timer 2)

## Summary
- 2029 nodes · 5719 edges · 106 communities (83 shown, 23 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 317 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2b6c1d2a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ._fetch
- test_autonomous_harness.py
- OperationsManager
- dashboard.py
- test_bits_runner.py
- ExperimentRegistry
- InMemoryCTraderDemoStore
- ConfirmedBreakoutCanarySource
- MemoryRegistry
- pytest
- test_ctrader_demo.py
- ExecutionConfig
- _demo_automation_runner
- PaperTrading
- self_improve.py
- InMemoryAgentTranscriptStore
- local_state.py
- Any
- test_agent_loop.py
- firecrawl_research.py
- RemoteComputeBridge
- test_agent_view.py
- test_distributed_compute.py
- test_ctrader_lifecycle.py
- XAUUSD discovery, incident, quantitative, and scaling audit
- cli.py
- test_demo_runner.py
- OpenAICompatiblePlanner
- SQLiteAgentTranscriptStore
- test_demo_execution.py
- test_oauth.py
- TournamentRunner
- ExperimentSpec
- synthetic_bars
- MemoryConnection
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- core.py
- ShadowTradingReadiness
- CTraderAuthError
- test_bits_jobs.py
- bits_jobs.py
- Datadog Bits connection
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- BitsError
- DemoAutomationRunner
- autonomous_harness.py
- automation.py
- CTraderDemoSafetyError
- PaperDecision
- PaperToCTraderDemoCoordinator
- restart_policy
- test_session_reset.py
- test_bits_research.py
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- verify_result_parity.py
- CTraderHistoricalAdapter
- graphify reference: query, path, explain
- BitsAgentRunner
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- test_experiment_registry.py
- CTraderVolumeConversion
- XAUUSD Autonomous Research and Demo Harness
- Architecture and data-flow map
- InMemoryHarnessStore
- opencode.json
- main
- CTraderDemoStore
- bits_runner.py
- CodexImprovementWorkflow
- Local handoff audit — 2026-09-24
- DemoLifecycle
- CockroachHarnessStore
- agent_loop.py
- HarnessStore
- Adapter
- test_data.py
- PaperTradingStore
- TournamentDataset
- test_health_uses_configured_cockroach_registry
- HistoricalDataStore
- CTraderOpenApiDownloader
- .run
- PostgresConnection
- test_strategy_proposals.py
- paper_trading.py
- mutation_analytics
- persist_tokens_env
- FakeResponse
- test_continuous_worker_records_idle_heartbeat
- ToolExecutionError
- authorize_url
- test_data_update_retries_transient_failures
- .__init__

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
10. `CTraderDemoOpenApiTransport` - 41 edges

## Surprising Connections (you probably didn't know these)
- `12. Status of evidence` --references--> `OpenAICompatiblePlanner`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → xauusd/autonomous_harness.py
- `Portfolio and regime research — 2026-08-21` --references--> `PortfolioResearch`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → xauusd/portfolio_research.py
- `Clean lease-drained saturation benchmark — 2026-08-20` --references--> `completed()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → tests/test_adaptive_search.py
- `8. Prototype gate and test plan (execute BEFORE any cutover)` --references--> `tool()`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → tests/test_autonomous_harness.py
- `Engineering` --references--> `agent_transcript_store_from_env()`  [INFERRED]
  AGENTS.md → xauusd/agent_loop.py

## Import Cycles
- None detected.

## Communities (106 total, 23 thin omitted)

### Community 0 - "._fetch"
Cohesion: 0.09
Nodes (40): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Order lifecycle and errors — follow-up #15, Position reconciliation — follow-up #16, account(), test_demo_accounts_empty_when_all_live(), test_demo_accounts_filters_live_and_missing_flag() (+32 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.29
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "OperationsManager"
Cohesion: 0.12
Nodes (18): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+10 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (64): asyncio, fastapi_responses, fastapi_security, fastapi_testclient, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio (+56 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.22
Nodes (10): Planner, runner(), test_complete_action_feedback_cycle(), test_market_closed_and_stopped_never_submit(), test_monitor_stops_loss_without_planner_call(), test_pending_workflow_survives_restart(), test_second_process_refused_and_uncertain_submission_stops(), test_shell_timeout_is_twenty_minutes_even_when_agent_requests_two() (+2 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.07
Nodes (29): Gate-failure and near-pass analytics — 2026-08-21, ExperimentStatus, itertools, statistics, test_bits_notes_only_does_not_repeat_history(), row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence() (+21 more)

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.13
Nodes (9): stopped_demo_adapter(), test_demo_automation_start_reconciles_then_clears_only_the_demo_switch(), _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB. (+1 more)

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.16
Nodes (21): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+13 more)

### Community 9 - "pytest"
Cohesion: 0.06
Nodes (35): ImportError, importlib, pytest, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing (+27 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.12
Nodes (20): FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(), test_open_api_transport_fails_reconciliation_on_an_error_reply(), test_open_api_transport_reads_symbol_volume_metadata() (+12 more)

### Community 11 - "ExecutionConfig"
Cohesion: 0.11
Nodes (38): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, sklearn_metrics, main(), bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path() (+30 more)

### Community 12 - "_demo_automation_runner"
Cohesion: 0.22
Nodes (10): test_demo_automation_requires_explicit_positive_volume(), test_demo_automation_start_keeps_the_switch_stopped_when_reconciliation_fails(), test_environment_config_is_disabled_unless_explicitly_true(), demo_automation(), _demo_automation_runner(), _demo_automation_status(), _positive_env_float(), Run the explicitly enabled local-data paper-to-demo canary. (+2 more)

### Community 13 - "PaperTrading"
Cohesion: 0.09
Nodes (42): paper_trading(), DemoTransport, no_broker(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_once_reports_a_refused_restart(), test_demo_automation_paper_only_skips_broker_dependencies(), test_demo_automation_start_in_paper_only_mode_contacts_no_broker() (+34 more)

### Community 14 - "self_improve.py"
Cohesion: 0.13
Nodes (20): base64, CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal() (+12 more)

### Community 15 - "InMemoryAgentTranscriptStore"
Cohesion: 0.13
Nodes (4): CockroachAgentTranscriptStore, InMemoryAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Test double only; production state lives in the configured backend store.

### Community 16 - "local_state.py"
Cohesion: 0.16
Nodes (23): gzip, sqlite3, decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_refuses_garbage_archive() (+15 more)

### Community 17 - "Any"
Cohesion: 0.16
Nodes (13): request(), CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded() (+5 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.12
Nodes (35): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), refresh_config(), refresh_runner(), ScriptedPlanner (+27 more)

### Community 19 - "firecrawl_research.py"
Cohesion: 0.15
Nodes (18): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+10 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.17
Nodes (4): test_readiness_uses_most_constrained_mount(), Path, Primary-only SSH bridge. The secondary never opens the CockroachDB registry., RemoteComputeBridge

### Community 21 - "test_agent_view.py"
Cohesion: 0.05
Nodes (50): FastAPI, test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), fixture, server(), test_age_seconds_parses_timezone_aware_timestamps(), test_bits_decisions_show_summary_instead_of_protocol_json() (+42 more)

### Community 22 - "test_distributed_compute.py"
Cohesion: 0.15
Nodes (17): P0/P1 implementation updates — 2026-08-20, Exception, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible() (+9 more)

### Community 23 - "test_ctrader_lifecycle.py"
Cohesion: 0.11
Nodes (26): adapter(), test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_duplicate_request_never_sends_a_second_transport_call(), test_long_decision_id_is_persisted_but_broker_id_fits(), test_reconcile_maps_persisted_broker_id_back_to_internal_id(), test_recovery_failure_kills_and_blocks_execution(), test_transport_failure_is_an_unknown_outcome_that_blocks_restart() (+18 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (47): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+39 more)

### Community 25 - "cli.py"
Cohesion: 0.17
Nodes (26): collections, dataclasses, datetime, hashlib, json, logging, math, numpy (+18 more)

### Community 26 - "test_demo_runner.py"
Cohesion: 0.21
Nodes (17): DecisionSource, MarketSource, paper_only_runner(), Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status(), test_cycle_failure_stops_after_configured_consecutive_failures(), test_disabled_config_does_not_reconcile_or_start() (+9 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.27
Nodes (6): 3. Where the planner is wired today (confirmed), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), OpenAICompatiblePlanner, Any, Return the model's raw response content and the parsed allow-listed action. Raw…

### Community 28 - "SQLiteAgentTranscriptStore"
Cohesion: 0.15
Nodes (10): Connection, Row, test_sqlite_transcript_reconciles_running_orphans(), test_sqlite_transcript_store_round_trips_steps_and_runs(), _connect(), _now(), Any, Local SQLite replacement for the CockroachDB agent transcript store. (+2 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.15
Nodes (21): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+13 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.20
Nodes (18): response_json(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises(), test_refresh_access_token_returns_pair_with_browser_agent(), fake_urlopen(), test_rejected_grant_raises_oauth_error() (+10 more)

### Community 31 - "TournamentRunner"
Cohesion: 0.25
Nodes (6): _atomic_json(), compute_job(), _finite(), Path, Consume deterministic experiments without reading the holdout test set., TournamentRunner

### Community 32 - "ExperimentSpec"
Cohesion: 0.26
Nodes (13): E. Current 50,000-scenario architecture and benchmark, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix(), ExperimentSpec, from_strategy(), candidate_specs() (+5 more)

### Community 33 - "synthetic_bars"
Cohesion: 0.11
Nodes (35): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+27 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.14
Nodes (13): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 7.1 Code — one relaxation (small, tested) (+5 more)

### Community 37 - "core.py"
Cohesion: 0.27
Nodes (8): test_backtest(), campaign(), event_backtest(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 39 - "CTraderAuthError"
Cohesion: 0.17
Nodes (18): test_data_update_does_not_retry_auth_errors(), download(), downloader_config(), minute_60(), one_bar_at(), test_download_does_not_retry_non_token_auth_error(), fake_fetch(), test_download_retries_once_on_invalid_token() (+10 more)

### Community 40 - "test_bits_jobs.py"
Cohesion: 0.22
Nodes (10): action(), jobs(), fixture, test_cancel_process_after_output_streams_close(), test_execution_idempotency_and_conflict(), test_interrupted_job_never_replayed(), test_secret_output_is_not_persisted(), test_timeout_and_output_bound() (+2 more)

### Community 41 - "bits_jobs.py"
Cohesion: 0.13
Nodes (13): contextlib, dotenv, fcntl, re, Two-invocation, no-trading smoke test of Bits -> shell -> Bits. Run from the…, selectors, signal, sys (+5 more)

### Community 42 - "Datadog Bits connection"
Cohesion: 0.20
Nodes (8): Bits agent instructions, Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 43 - "AdaptiveSearch"
Cohesion: 0.29
Nodes (11): Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_semantic_identity_ignores_provenance(), test_small_adaptive_batch_round_robins_families() (+3 more)

### Community 49 - "BitsError"
Cohesion: 0.17
Nodes (20): main(), call(), envelope(), parametrize, shell_action(), test_refuses_invalid_envelopes(), test_refuses_invalid_shell_limits(), test_strict_json_and_arbitrary_command() (+12 more)

### Community 50 - "DemoAutomationRunner"
Cohesion: 0.26
Nodes (5): DemoAutomationRunner, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 51 - "autonomous_harness.py"
Cohesion: 0.23
Nodes (11): concurrent_futures, 6. Safety and repository-rule compliance (unchanged), 8. Prototype gate and test plan (execute BEFORE any cutover), ValueError, _check_reason(), parse_action(), PlannerResponseError, Research-only autonomous harness primitives; this module has no broker or web… (+3 more)

### Community 52 - "automation.py"
Cohesion: 0.10
Nodes (27): test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_html_report_contains_candidates(), test_registry_only_promotes_passing_better_candidate(), test_run_lock_rejects_overlap(), test_weekly_comparison_collects_archived_runs(), test_validator_writes_report_and_does_not_promote_weak_strategy(), traceback (+19 more)

### Community 53 - "CTraderDemoSafetyError"
Cohesion: 0.10
Nodes (22): copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+14 more)

### Community 54 - "PaperDecision"
Cohesion: 0.12
Nodes (15): test_market_data_age_clamps_a_still_forming_bar_to_zero(), test_market_data_age_counts_from_bar_close_not_bar_open(), handler(), CockroachPaperTradingStore, market_data_age_seconds(), _now(), PaperDecision, transition() (+7 more)

### Community 55 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.13
Nodes (16): test_volume_policy_from_metadata(), agent_tool(), _paper_to_demo_coordinator(), CLI bridge to the existing deterministic tools, for Bits shell requests., CTraderVolumePolicy, DemoExecutor, PaperToCTraderDemoCoordinator, Any (+8 more)

### Community 56 - "restart_policy"
Cohesion: 0.15
Nodes (13): Autonomous Harness, Datadog Bits operations, Engineering, Execution Boundary, graphify, Local agent handoff — completed 2026-09-24, Operations, Purpose (+5 more)

### Community 57 - "test_session_reset.py"
Cohesion: 0.29
Nodes (9): seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), AgentAlreadyRunning, AgentLock, Single process per container; the lock is runtime coordination, not state., _default_state(), Explicit operator reset of a stopped local paper session, after backup. (+1 more)

### Community 58 - "test_bits_research.py"
Cohesion: 0.22
Nodes (8): Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_market_windows_use_observed_data_and_handle_missing_source(), test_nested_output_page_preserves_original_cursor_without_skipping_text(), test_research_progress_is_idempotent_and_resets_only_on_changed_notes(), finish_research_cycle(), market_research(), Compact observations and persistent research-progress signals, never trade…

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.11
Nodes (13): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, Protocol, Display-friendly assistant step: parsed action plus the model's plain-English… (+5 more)

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "CTraderHistoricalAdapter"
Cohesion: 0.25
Nodes (4): Interpreter guard for subcommands, CTraderHistoricalAdapter, Path, Import cTrader CSV exports into the normalized historical store.

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

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

### Community 71 - "test_experiment_registry.py"
Cohesion: 0.22
Nodes (14): spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_postgres_connection_uses_configured_read_committed(), test_registration_rejects_duplicate_identity(), test_registry_requires_cockroach_database_url() (+6 more)

### Community 72 - "CTraderVolumeConversion"
Cohesion: 0.22
Nodes (7): test_demo_factory_binds_authoritative_paper_exposure(), _ctrader_demo_adapter(), expected_volume(), _demo_automation_start(), Explicit operator override for the demo execution kill switch; paper and the…, CTraderVolumeConversion, Explicit conversion from paper quantity units to cTrader volume-in-cents units.

### Community 73 - "XAUUSD Autonomous Research and Demo Harness"
Cohesion: 0.14
Nodes (14): Architecture, Autonomous Agent, Configuration, Current Status, Delivery Stages, Demo Automation, Demo Automation Service, Demo-Only Controls (+6 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 77 - "main"
Cohesion: 0.18
Nodes (15): test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_status_reports_paper_only_flag(), test_state_integrity_backup_restore_round_trip(), agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., agent_controller(), _agent_status_path(), _agent_status_view() (+7 more)

### Community 78 - "CTraderDemoStore"
Cohesion: 0.14
Nodes (3): CTraderDemoStore, CTraderTransport, Protocol

### Community 79 - "bits_runner.py"
Cohesion: 0.15
Nodes (14): memory(), fixture, reply(), test_history_size_and_excerpts_are_explicit(), test_memory_retains_recent_exchanges_and_source_linked_digest(), test_notes_preserve_structured_claims_and_reject_oversize(), uuid, Suppress whole values, not partial/redacted credentials. Not a shell sandbox. (+6 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "Local handoff audit — 2026-09-24"
Cohesion: 0.29
Nodes (5): Follow-up implementation (supersedes the original blocker list), Local handoff audit — 2026-09-24, Local validation and deployment, Planner latency (read-only), Recommended next work

### Community 82 - "DemoLifecycle"
Cohesion: 0.20
Nodes (4): DemoLifecycle, MarketDataSource, Protocol, Read-only source for the latest executable market observation.

### Community 84 - "agent_loop.py"
Cohesion: 0.17
Nodes (19): threading, build_agent_registry(), canary_signal_tool(), _decision_id(), paper_state_tool(), _positive_float(), propose_trade_tool(), handler() (+11 more)

### Community 87 - "Adapter"
Cohesion: 0.22
Nodes (3): Adapter, Stateful demo lifecycle double: the kill switch persists like the real store., test_restart_reconciles_an_already_running_demo_switch_without_restarting_it()

### Community 88 - "test_data.py"
Cohesion: 0.24
Nodes (11): demo_env(), test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag(), test_store_rejects_invalid_ohlc(), test_store_roundtrip(), test_trendbar_delta_decoding(), CTraderOpenApiConfig (+3 more)

### Community 90 - "TournamentDataset"
Cohesion: 0.14
Nodes (17): Dependence-aware bootstrap validation — 2026-08-21, dataset(), test_content_change_creates_new_version(), test_frozen_dataset_is_reproducible_and_partitioned(), test_partitions_read_exact_manifest_counts(), test_tampering_is_detected(), setup_runner(), test_failure_is_durable() (+9 more)

### Community 92 - "HistoricalDataStore"
Cohesion: 0.27
Nodes (5): _agent_data_refresh_source(), Bound data refresh for a stale agent tick. Runs the one-shot downloader in a…, HistoricalDataStore, DataFrame, Local OHLCV store. The adapter accepts historical exports only; no execution…

### Community 93 - "CTraderOpenApiDownloader"
Cohesion: 0.31
Nodes (4): Timestamp, CTraderOpenApiDownloader, datetime, Read-only cTrader Open API client for symbols and historical trendbars.

### Community 94 - ".run"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

### Community 96 - "test_strategy_proposals.py"
Cohesion: 0.17
Nodes (10): test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), test_adaptive_generations_wait_for_completion_interval(), PortfolioResearch, Path, novel_proposals(), Proposal, ProposalEngine (+2 more)

### Community 97 - "paper_trading.py"
Cohesion: 0.18
Nodes (17): decision(), test_agent_transcript_backend_selection_defaults_to_local(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store(), test_sqlite_integrity_check_detects_corruption(), test_sqlite_paper_store_corrupt_state_fails_closed(), test_sqlite_paper_store_integrity_check_reports_ok(), test_sqlite_paper_store_kill_switch_persists_and_fails_closed() (+9 more)

### Community 98 - "mutation_analytics"
Cohesion: 0.33
Nodes (3): Adaptive-mutation outcome analytics — 2026-08-21, test_mutation_analytics_measures_improvement_and_duplicates(), mutation_analytics()

### Community 99 - "persist_tokens_env"
Cohesion: 0.33
Nodes (6): PathLike, test_persist_tokens_appends_missing_key_and_sets_0600(), test_persist_tokens_rewrites_only_token_keys(), persist_tokens_env(), Path, Atomically rewrite only the token keys in the given env file (``0o600``).…

### Community 103 - "authorize_url"
Cohesion: 0.67
Nodes (3): Market Data & Authentication, test_authorize_url_builds_documented_endpoint(), authorize_url()

## Knowledge Gaps
- **127 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+122 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 568 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MemoryRegistry` connect `MemoryRegistry` to `ExperimentSpec`, `test_strategy_proposals.py`, `MemoryConnection`, `dashboard.py`, `OperationsManager`, `ExperimentRegistry`, `ShadowTradingReadiness`, `test_experiment_registry.py`, `AdaptiveSearch`, `CodexImprovementWorkflow`, `RemoteComputeBridge`, `test_distributed_compute.py`, `cli.py`, `TournamentDataset`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `ExperimentRegistry` connect `ExperimentRegistry` to `ExperimentSpec`, `test_strategy_proposals.py`, `OperationsManager`, `dashboard.py`, `ShadowTradingReadiness`, `test_experiment_registry.py`, `.__init__`, `AdaptiveSearch`, `main`, `CodexImprovementWorkflow`, `RemoteComputeBridge`, `test_distributed_compute.py`, `cli.py`, `TournamentDataset`, `TournamentRunner`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `PaperTradingStore`, `paper_trading.py`, `test_bits_runner.py`, `main`, `local_state.py`, `test_agent_loop.py`, `agent_loop.py`, `test_agent_view.py`, `PaperDecision`, `PaperToCTraderDemoCoordinator`, `restart_policy`, `test_session_reset.py`, `test_demo_runner.py`, `ContinuousAgentRunner`, `test_demo_execution.py`, `cli.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_maybe_resume_preserves_every_persisted_stop_except_fresh_state()`) actually correct?**
  _`PaperTrading` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `main()` (e.g. with `CTraderAuthError` and `CTraderOpenApiConfig`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._