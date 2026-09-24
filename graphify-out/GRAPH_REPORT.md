# Graph Report - xauusd  (2026-09-24)

## Corpus Check
- 122 files · ~92,689 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 6, .service 5, .timer 2)

## Summary
- 2030 nodes · 5720 edges · 96 communities (79 shown, 17 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 317 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4e1104bc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_ctrader_auth.py
- test_autonomous_harness.py
- OperationsManager
- dashboard.py
- test_bits_runner.py
- ExperimentRegistry
- InMemoryCTraderDemoStore
- test_canary_strategy.py
- MemoryRegistry
- ml_models.py
- test_ctrader_demo.py
- ExecutionConfig
- demo_runner.py
- PaperTrading
- self_improve.py
- CockroachAgentTranscriptStore
- datetime
- Any
- test_agent_loop.py
- firecrawl_research.py
- RemoteComputeBridge
- test_agent_view.py
- test_validation.py
- test_bits_jobs.py
- XAUUSD discovery, incident, quantitative, and scaling audit
- cli.py
- test_demo_runner.py
- OpenAICompatiblePlanner
- SQLiteAgentTranscriptStore
- test_demo_execution.py
- test_oauth.py
- TournamentRunner
- test_search_space.py
- synthetic_bars
- memory_registry.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- core.py
- ShadowTradingReadiness
- CTraderAuthError
- InMemoryAgentTranscriptStore
- test_offline.py
- ._fetch
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- BitsError
- DemoAutomationRunner
- test_ctrader_lifecycle.py
- automation.py
- ctrader_demo.py
- canonical_json
- PaperToCTraderDemoCoordinator
- restart_policy
- agent_view.py
- autonomous_harness.py
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- verify_result_parity.py
- /graphify
- graphify reference: query, path, explain
- EventDrivenBacktester
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- test_experiment_registry.py
- BitsAgentRunner
- XAUUSD Autonomous Research and Demo Harness
- Architecture and data-flow map
- test_data.py
- opencode.json
- agent_controller
- CTraderDemoStore
- pytest
- CodexImprovementWorkflow
- ToolSpec
- SequencedTransport
- CockroachHarnessStore
- agent_loop.py
- HarnessStore
- main
- read_status
- PaperTradingStore
- test_health_uses_configured_cockroach_registry
- HistoricalDataStore
- CTraderOpenApiDownloader
- .run
- PostgresConnection
- portfolio_research.py

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
- `Order lifecycle and errors — follow-up #15` --references--> `is_error()`  [INFERRED]
  docs/local-handoff-audit-2026-09-24.md → xauusd/ctrader_auth.py
- `Execution Boundary` --references--> `restart_policy()`  [INFERRED]
  AGENTS.md → xauusd/paper_trading.py
- `Clean lease-drained saturation benchmark — 2026-08-20` --references--> `completed()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → tests/test_adaptive_search.py
- `8. Prototype gate and test plan (execute BEFORE any cutover)` --references--> `tool()`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → tests/test_autonomous_harness.py

## Import Cycles
- None detected.

## Communities (96 total, 17 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.16
Nodes (19): account(), test_demo_accounts_empty_when_all_live(), test_demo_accounts_filters_live_and_missing_flag(), test_is_error_extracts_code_and_description(), test_is_error_none_when_clear(), test_resolve_symbol_falls_back_to_first_match(), test_resolve_symbol_prefers_enabled_match(), test_resolve_symbol_rejects_invalid_id() (+11 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.19
Nodes (16): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+8 more)

### Community 2 - "OperationsManager"
Cohesion: 0.11
Nodes (20): test_research_brief_is_redacted_and_aggregated(), test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost() (+12 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (64): asyncio, fastapi_responses, fastapi_security, fastapi_testclient, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio (+56 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.12
Nodes (18): Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_market_windows_use_observed_data_and_handle_missing_source(), test_nested_output_page_preserves_original_cursor_without_skipping_text(), test_research_progress_is_idempotent_and_resets_only_on_changed_notes(), Planner, runner(), test_complete_action_feedback_cycle() (+10 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.08
Nodes (27): Gate-failure and near-pass analytics — 2026-08-21, ExperimentStatus, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence() (+19 more)

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "test_canary_strategy.py"
Cohesion: 0.34
Nodes (12): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+4 more)

### Community 9 - "ml_models.py"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.09
Nodes (33): adapter(), FakeClient, ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call() (+25 more)

### Community 11 - "ExecutionConfig"
Cohesion: 0.14
Nodes (27): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, sklearn_metrics, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future() (+19 more)

### Community 12 - "demo_runner.py"
Cohesion: 0.12
Nodes (12): test_environment_config_is_disabled_unless_explicitly_true(), NormalizedDecision, Strategy proposal expressed in configured paper-trading quantity units., DecisionSource, DemoLifecycle, DemoRunnerConfig, MarketDataSource, datetime (+4 more)

### Community 13 - "PaperTrading"
Cohesion: 0.16
Nodes (27): decision(), parametrize, test_corrupt_memory_state_fails_closed(), test_default_gate_accepts_the_newest_closed_m1_bar(), test_duplicate_decision_returns_persisted_outcome_without_second_fill(), test_gate_accepts_the_winter_hour_after_21_utc_and_refuses_the_real_break(), test_gate_returns_market_closed_outside_trading_hours(), test_market_closed_precedes_stale_data() (+19 more)

### Community 14 - "self_improve.py"
Cohesion: 0.13
Nodes (20): base64, CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal() (+12 more)

### Community 15 - "CockroachAgentTranscriptStore"
Cohesion: 0.19
Nodes (5): CockroachAgentTranscriptStore, _decision_id(), handler(), datetime, Production transcript store; the database is authoritative agent state.

### Community 16 - "datetime"
Cohesion: 0.12
Nodes (21): datetime, fcntl, selectors, signal, seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), threading (+13 more)

### Community 17 - "Any"
Cohesion: 0.17
Nodes (12): CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded(), Any (+4 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.17
Nodes (28): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), refresh_config(), stale_market_store(), test_assistant_steps_carry_parsed_action_and_human_reason() (+20 more)

### Community 19 - "firecrawl_research.py"
Cohesion: 0.15
Nodes (18): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+10 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.06
Nodes (32): P0/P1 implementation updates — 2026-08-20, Exception, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible() (+24 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.09
Nodes (16): paper_trading(), fixture, server(), test_age_seconds_parses_timezone_aware_timestamps(), test_bits_decisions_show_summary_instead_of_protocol_json(), test_health_degrades_when_ticks_never_reach_the_planner(), test_health_does_not_alert_below_the_stale_tick_threshold(), test_paper_endpoint_reflects_accepted_fill() (+8 more)

### Community 22 - "test_validation.py"
Cohesion: 0.15
Nodes (18): Dependence-aware bootstrap validation — 2026-08-21, test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_parameter_neighbors_change_one_value(), validate_strategy(), bootstrap_trade_paths(), chronological_split() (+10 more)

### Community 23 - "test_bits_jobs.py"
Cohesion: 0.22
Nodes (10): action(), jobs(), fixture, test_cancel_process_after_output_streams_close(), test_execution_idempotency_and_conflict(), test_interrupted_job_never_replayed(), test_secret_output_is_not_persisted(), test_timeout_and_output_bound() (+2 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "cli.py"
Cohesion: 0.21
Nodes (20): collections, dataclasses, hashlib, json, logging, math, numpy, os (+12 more)

### Community 26 - "test_demo_runner.py"
Cohesion: 0.14
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.30
Nodes (6): 3. Where the planner is wired today (confirmed), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), OpenAICompatiblePlanner, Any, Return the model's raw response content and the parsed allow-listed action. Raw…

### Community 28 - "SQLiteAgentTranscriptStore"
Cohesion: 0.07
Nodes (43): Connection, gzip, Row, sqlite3, decision(), test_agent_transcript_backend_selection_defaults_to_local(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store() (+35 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.19
Nodes (19): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches() (+11 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.10
Nodes (28): PathLike, Market Data & Authentication, FakeResponse, response_json(), test_authorize_url_builds_documented_endpoint(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error() (+20 more)

### Community 31 - "TournamentRunner"
Cohesion: 0.11
Nodes (15): setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition(), _atomic_json() (+7 more)

### Community 32 - "test_search_space.py"
Cohesion: 0.25
Nodes (14): E. Current 50,000-scenario architecture and benchmark, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix(), from_strategy() (+6 more)

### Community 33 - "synthetic_bars"
Cohesion: 0.12
Nodes (28): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+20 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.14
Nodes (13): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 7.1 Code — one relaxation (small, tested) (+5 more)

### Community 37 - "core.py"
Cohesion: 0.27
Nodes (8): test_backtest(), campaign(), event_backtest(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (11): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), Path (+3 more)

### Community 39 - "CTraderAuthError"
Cohesion: 0.14
Nodes (19): test_data_update_does_not_retry_auth_errors(), download(), test_data_update_retries_transient_failures(), downloader_config(), minute_60(), one_bar_at(), test_download_does_not_retry_non_token_auth_error(), fake_fetch() (+11 more)

### Community 40 - "InMemoryAgentTranscriptStore"
Cohesion: 0.11
Nodes (9): refresh_runner(), ScriptedPlanner, test_runner_records_failed_refresh_and_gates_planner(), test_runner_refreshes_stale_data_and_records_step(), refresh(), test_runner_respects_refresh_cooldown(), test_runner_skips_refresh_when_disabled(), InMemoryAgentTranscriptStore (+1 more)

### Community 41 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.19
Nodes (14): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+6 more)

### Community 49 - "BitsError"
Cohesion: 0.12
Nodes (27): dotenv, main(), call(), Two-invocation, no-trading smoke test of Bits -> shell -> Bits. Run from the…, sys, tempfile, envelope(), parametrize (+19 more)

### Community 50 - "DemoAutomationRunner"
Cohesion: 0.26
Nodes (5): DemoAutomationRunner, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 51 - "test_ctrader_lifecycle.py"
Cohesion: 0.21
Nodes (11): Client, event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending() (+3 more)

### Community 52 - "automation.py"
Cohesion: 0.12
Nodes (23): test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_html_report_contains_candidates(), test_registry_only_promotes_passing_better_candidate(), test_run_lock_rejects_overlap(), test_weekly_comparison_collects_archived_runs(), traceback, append_jsonl() (+15 more)

### Community 53 - "ctrader_demo.py"
Cohesion: 0.09
Nodes (26): contextlib, copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account() (+18 more)

### Community 54 - "canonical_json"
Cohesion: 0.10
Nodes (20): test_market_data_age_clamps_a_still_forming_bar_to_zero(), test_market_data_age_counts_from_bar_close_not_bar_open(), canonical_json(), CockroachPaperTradingStore, _default_state(), market_data_age_seconds(), market_is_open(), _now() (+12 more)

### Community 55 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.12
Nodes (14): test_volume_policy_from_metadata(), CTraderVolumePolicy, DemoExecutor, PaperToCTraderDemoCoordinator, Any, datetime, Protocol, Coordinates accepted paper decisions with explicitly started cTrader demo… (+6 more)

### Community 56 - "restart_policy"
Cohesion: 0.33
Nodes (5): Operations, test_restart_policy_is_an_allowlist_that_fails_closed(), Resume after an unattended restart only when :func:`restart_policy` allows it.…, Classify a persisted kill switch for an unattended restart. ``"running"``: not…, restart_policy()

### Community 57 - "agent_view.py"
Cohesion: 0.18
Nodes (16): Engineering, FastAPI, agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., create_app(), data_update_status(), health(), paper_endpoint() (+8 more)

### Community 58 - "autonomous_harness.py"
Cohesion: 0.21
Nodes (12): concurrent_futures, 6. Safety and repository-rule compliance (unchanged), 8. Prototype gate and test plan (execute BEFORE any cutover), re, ValueError, _check_reason(), parse_action(), PlannerResponseError (+4 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.11
Nodes (13): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, Protocol, Display-friendly assistant step: parsed action plus the model's plain-English… (+5 more)

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "/graphify"
Cohesion: 0.12
Nodes (12): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Usage (+4 more)

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 64 - "EventDrivenBacktester"
Cohesion: 0.35
Nodes (11): main(), bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path(), test_compact_attribution_metrics_reconcile_and_measure_concentration(), test_signal_executes_at_next_open_without_lookahead(), test_spread_slippage_and_commission_are_charged_both_sides(), test_stop_wins_ambiguous_intrabar_path() (+3 more)

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
Cohesion: 0.26
Nodes (13): spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity(), test_registry_requires_cockroach_database_url(), test_remote_error_can_requeue_owned_experiment() (+5 more)

### Community 73 - "XAUUSD Autonomous Research and Demo Harness"
Cohesion: 0.04
Nodes (40): Autonomous Harness, Datadog Bits operations, Execution Boundary, graphify, Local agent handoff — completed 2026-09-24, Purpose, Repository Operating Rules, Bits agent instructions (+32 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.30
Nodes (9): demo_env(), test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag(), test_trendbar_delta_decoding(), CTraderOpenApiConfig, Any, Decode cTrader's low-plus-delta trendbar representation. (+1 more)

### Community 77 - "agent_controller"
Cohesion: 0.11
Nodes (19): test_demo_factory_binds_authoritative_paper_exposure(), _positive_float(), agent_controller(), _agent_data_refresh_source(), _agent_status_path(), _agent_status_view(), agent_tool(), _ctrader_demo_adapter() (+11 more)

### Community 78 - "CTraderDemoStore"
Cohesion: 0.14
Nodes (3): CTraderDemoStore, CTraderTransport, Protocol

### Community 79 - "pytest"
Cohesion: 0.15
Nodes (13): pytest, memory(), fixture, reply(), test_history_size_and_excerpts_are_explicit(), test_memory_retains_recent_exchanges_and_source_linked_digest(), test_notes_preserve_structured_claims_and_reject_oversize(), Suppress whole values, not partial/redacted credentials. Not a shell sandbox. (+5 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.24
Nodes (8): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), CodexImprovementWorkflow, CodexWorkflowConfig, Path, Create review-only Codex candidates in disposable detached worktrees.

### Community 81 - "ToolSpec"
Cohesion: 0.31
Nodes (3): RuntimeError, ToolExecutionError, ToolSpec

### Community 84 - "agent_loop.py"
Cohesion: 0.14
Nodes (19): test_canary_signal_tool_returns_side(), build_agent_registry(), canary_signal_tool(), handler(), _mock_market_for_read(), paper_state_tool(), Continuous single-agent XAUUSD paper trading loop with a live, visible thinking…, read_market_tool() (+11 more)

### Community 87 - "main"
Cohesion: 0.11
Nodes (26): DemoTransport, no_broker(), stopped_demo_adapter(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_bits_notes_only_does_not_repeat_history(), test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_once_reports_a_refused_restart() (+18 more)

### Community 88 - "read_status"
Cohesion: 0.35
Nodes (10): test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), Any, Path, Atomic on-disk heartbeat for the continuous agent. The agent writes no…, Persist one heartbeat atomically (temp file + fsync + rename). (+2 more)

### Community 92 - "HistoricalDataStore"
Cohesion: 0.31
Nodes (5): test_store_rejects_invalid_ohlc(), test_store_roundtrip(), HistoricalDataStore, DataFrame, Local OHLCV store. The adapter accepts historical exports only; no execution…

### Community 93 - "CTraderOpenApiDownloader"
Cohesion: 0.29
Nodes (4): Timestamp, CTraderOpenApiDownloader, datetime, Read-only cTrader Open API client for symbols and historical trendbars.

### Community 94 - ".run"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

### Community 95 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 96 - "portfolio_research.py"
Cohesion: 0.19
Nodes (21): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), read(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete() (+13 more)

## Knowledge Gaps
- **128 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+123 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 569 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MemoryRegistry` connect `MemoryRegistry` to `test_search_space.py`, `synthetic_bars`, `OperationsManager`, `memory_registry.py`, `dashboard.py`, `ExperimentRegistry`, `ShadowTradingReadiness`, `test_experiment_registry.py`, `AdaptiveSearch`, `CodexImprovementWorkflow`, `RemoteComputeBridge`, `TournamentRunner`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `ExperimentRegistry` connect `ExperimentRegistry` to `test_search_space.py`, `synthetic_bars`, `OperationsManager`, `dashboard.py`, `portfolio_research.py`, `ShadowTradingReadiness`, `test_experiment_registry.py`, `AdaptiveSearch`, `CodexImprovementWorkflow`, `RemoteComputeBridge`, `main`, `cli.py`, `TournamentRunner`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `PaperTradingStore`, `restart_policy`, `test_bits_runner.py`, `agent_controller`, `datetime`, `test_agent_loop.py`, `agent_loop.py`, `test_agent_view.py`, `PaperToCTraderDemoCoordinator`, `main`, `canonical_json`, `agent_view.py`, `test_demo_runner.py`, `ContinuousAgentRunner`, `SQLiteAgentTranscriptStore`, `test_demo_execution.py`, `cli.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_maybe_resume_preserves_every_persisted_stop_except_fresh_state()`) actually correct?**
  _`PaperTrading` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `main()` (e.g. with `CTraderAuthError` and `CTraderOpenApiConfig`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._