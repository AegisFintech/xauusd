# Graph Report - xauusd  (2026-09-24)

## Corpus Check
- 121 files · ~91,209 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 6, .service 5, .timer 2)

## Summary
- 2011 nodes · 5658 edges · 99 communities (82 shown, 17 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 311 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f39c828e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_ctrader_auth.py
- test_autonomous_harness.py
- OperationsManager
- dashboard.py
- DemoRunnerConfig
- ExperimentRegistry
- InMemoryCTraderDemoStore
- FirecrawlResearchClient
- MemoryRegistry
- pytest
- test_ctrader_demo.py
- test_ml.py
- cli.py
- PaperTrading
- ImprovementLedger
- DemoAutomationRunner
- test_dashboard.py
- Any
- test_agent_loop.py
- portfolio_research.py
- .from_env
- test_agent_view.py
- read_status
- test_ctrader_lifecycle.py
- XAUUSD discovery, incident, quantitative, and scaling audit
- agent_loop.py
- test_demo_runner.py
- OpenAICompatiblePlanner
- SQLiteAgentTranscriptStore
- test_demo_execution.py
- test_oauth.py
- TournamentRunner
- ExperimentSpec
- synthetic_bars
- memory_registry.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- Backtester
- ShadowTradingReadiness
- test_data.py
- ctrader_demo.py
- create_app
- Datadog Bits connection
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- BitsError
- test_validation.py
- CockroachPaperTradingStore
- automation.py
- test_tournament_runner.py
- PaperDecision
- PaperToCTraderDemoCoordinator
- Repository Operating Rules
- canonical_json
- is_error
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- verify_result_parity.py
- mutation_analytics
- graphify reference: query, path, explain
- ._fetch
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- test_experiment_registry.py
- PortfolioResearch
- ToolSpec
- Architecture and data-flow map
- InMemoryHarnessStore
- opencode.json
- test_cli.py
- CTraderDemoAdapter
- bits_runner.py
- CodexImprovementWorkflow
- Local handoff audit — 2026-09-24
- cTrader SDK and protocol review (no broker connection)
- CockroachHarnessStore
- market_is_open
- HarnessStore
- ExecutionConfig
- .__init__
- PaperTradingStore
- RemoteComputeBridge
- test_health_uses_configured_cockroach_registry
- HistoricalDataStore
- CTraderOpenApiDownloader
- .run
- TournamentDataset
- ProposalEngine
- SecretFilter
- SequencedTransport

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
- `Execution Boundary` --references--> `restart_policy()`  [INFERRED]
  AGENTS.md → xauusd/paper_trading.py
- `Portfolio and regime research — 2026-08-21` --references--> `PortfolioResearch`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → xauusd/portfolio_research.py
- `Clean lease-drained saturation benchmark — 2026-08-20` --references--> `completed()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → tests/test_adaptive_search.py

## Import Cycles
- None detected.

## Communities (99 total, 17 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.23
Nodes (11): account(), test_demo_accounts_empty_when_all_live(), test_demo_accounts_filters_live_and_missing_flag(), test_resolve_symbol_falls_back_to_first_match(), test_resolve_symbol_prefers_enabled_match(), test_resolve_symbol_rejects_invalid_id(), test_resolve_symbol_returns_none_when_absent(), demo_accounts() (+3 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.38
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "OperationsManager"
Cohesion: 0.12
Nodes (18): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+10 more)

### Community 3 - "dashboard.py"
Cohesion: 0.08
Nodes (58): asyncio, FastAPI, fastapi_responses, fastapi_security, get, HTTPBasicCredentials, logging, middleware (+50 more)

### Community 4 - "DemoRunnerConfig"
Cohesion: 0.19
Nodes (8): test_environment_config_is_disabled_unless_explicitly_true(), DecisionSource, DemoRunnerConfig, MarketDataSource, datetime, Protocol, Read-only source for the latest executable market observation., Read-only strategy proposal source; ``None`` means no proposed action.

### Community 5 - "ExperimentRegistry"
Cohesion: 0.07
Nodes (30): Gate-failure and near-pass analytics — 2026-08-21, ExperimentStatus, itertools, statistics, test_bits_notes_only_does_not_repeat_history(), row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence() (+22 more)

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "FirecrawlResearchClient"
Cohesion: 0.14
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.13
Nodes (4): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., test_catalog_seeding_is_batched_and_duplicate_safe(), test_proposal_engine_is_duplicate_safe_and_records_provenance()

### Community 9 - "pytest"
Cohesion: 0.06
Nodes (34): ImportError, importlib, pytest, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing (+26 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.11
Nodes (23): FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(), test_open_api_transport_fails_reconciliation_on_an_error_reply(), test_open_api_transport_reads_symbol_volume_metadata() (+15 more)

### Community 11 - "test_ml.py"
Cohesion: 0.12
Nodes (24): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined() (+16 more)

### Community 12 - "cli.py"
Cohesion: 0.11
Nodes (33): Engineering, agent_transcript_store_from_env(), _positive_float(), Transcript store for the configured backend (local SQLite by default)., Validate the small, explicit JSON-schema subset used for tool boundaries., _validate_json(), agent_controller(), _agent_status_path() (+25 more)

### Community 13 - "PaperTrading"
Cohesion: 0.18
Nodes (24): decision(), parametrize, test_corrupt_memory_state_fails_closed(), test_default_gate_accepts_the_newest_closed_m1_bar(), test_duplicate_decision_returns_persisted_outcome_without_second_fill(), test_gate_accepts_the_winter_hour_after_21_utc_and_refuses_the_real_break(), test_gate_returns_market_closed_outside_trading_hours(), test_market_closed_precedes_stale_data() (+16 more)

### Community 14 - "ImprovementLedger"
Cohesion: 0.13
Nodes (18): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+10 more)

### Community 15 - "DemoAutomationRunner"
Cohesion: 0.17
Nodes (6): DemoAutomationRunner, DemoLifecycle, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 16 - "test_dashboard.py"
Cohesion: 0.24
Nodes (8): fastapi_testclient, setup_files(), test_dashboard_reads_latest_run_and_equity(), test_dashboard_registry_requires_database_url_and_never_passes_a_path(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature(), test_tournament_equity_and_leaderboard()

### Community 17 - "Any"
Cohesion: 0.17
Nodes (12): CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded(), Any (+4 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.05
Nodes (72): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), refresh_config(), refresh_runner(), ScriptedPlanner (+64 more)

### Community 19 - "portfolio_research.py"
Cohesion: 0.30
Nodes (16): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal(), aligned_returns(), classify_regimes() (+8 more)

### Community 20 - ".from_env"
Cohesion: 0.29
Nodes (6): 7.1 Code — one relaxation (small, tested), 7.2 Deploy — one systemd unit (mirror rule applies), 7.3 Config/docs, 7. Required changes (tracked, not yet implemented), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout()

### Community 21 - "test_agent_view.py"
Cohesion: 0.09
Nodes (15): paper_trading(), fixture, server(), test_age_seconds_parses_timezone_aware_timestamps(), test_bits_decisions_show_summary_instead_of_protocol_json(), test_health_degrades_when_ticks_never_reach_the_planner(), test_health_does_not_alert_below_the_stale_tick_threshold(), test_paper_endpoint_reflects_accepted_fill() (+7 more)

### Community 22 - "read_status"
Cohesion: 0.35
Nodes (10): test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), Any, Path, Atomic on-disk heartbeat for the continuous agent. The agent writes no…, Persist one heartbeat atomically (temp file + fsync + rename). (+2 more)

### Community 23 - "test_ctrader_lifecycle.py"
Cohesion: 0.10
Nodes (28): adapter(), test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_duplicate_request_never_sends_a_second_transport_call(), test_long_decision_id_is_persisted_but_broker_id_fits(), test_reconcile_maps_persisted_broker_id_back_to_internal_id(), test_recovery_failure_kills_and_blocks_execution(), test_transport_failure_is_an_unknown_outcome_that_blocks_restart(), test_unresolved_pre_crash_request_fails_recovery_closed() (+20 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (47): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+39 more)

### Community 25 - "agent_loop.py"
Cohesion: 0.20
Nodes (20): collections, concurrent_futures, dataclasses, datetime, hashlib, json, math, os (+12 more)

### Community 26 - "test_demo_runner.py"
Cohesion: 0.13
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.30
Nodes (9): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), ValueError, _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError, Any (+1 more)

### Community 28 - "SQLiteAgentTranscriptStore"
Cohesion: 0.06
Nodes (50): Connection, gzip, Row, sqlite3, decision(), test_agent_transcript_backend_selection_defaults_to_local(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store() (+42 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.19
Nodes (19): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches() (+11 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.06
Nodes (42): PathLike, Architecture, Autonomous Agent, Configuration, Current Status, Delivery Stages, Demo Automation, Demo Automation Service (+34 more)

### Community 31 - "TournamentRunner"
Cohesion: 0.22
Nodes (6): _atomic_json(), compute_job(), _finite(), Path, Consume deterministic experiments without reading the holdout test set., TournamentRunner

### Community 32 - "ExperimentSpec"
Cohesion: 0.23
Nodes (14): E. Current 50,000-scenario architecture and benchmark, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_replenishment_scans_past_existing_prefix(), ExperimentSpec, from_strategy() (+6 more)

### Community 33 - "synthetic_bars"
Cohesion: 0.16
Nodes (21): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error(), test_novel_formulas_generate_valid_signals() (+13 more)

### Community 34 - "memory_registry.py"
Cohesion: 0.18
Nodes (3): copy, MemoryConnection, MemoryCursor

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (25): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+17 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.15
Nodes (11): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+3 more)

### Community 37 - "Backtester"
Cohesion: 0.29
Nodes (7): test_backtest(), campaign(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (11): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), Path (+3 more)

### Community 39 - "test_data.py"
Cohesion: 0.12
Nodes (24): test_data_update_does_not_retry_auth_errors(), download(), test_data_update_retries_transient_failures(), demo_env(), downloader_config(), minute_60(), one_bar_at(), test_data_config_from_env_account_optionally_discovered() (+16 more)

### Community 40 - "ctrader_demo.py"
Cohesion: 0.10
Nodes (20): base64, contextlib, dotenv, fcntl, re, Two-invocation, no-trading smoke test of Bits -> shell -> Bits. Run from the…, selectors, signal (+12 more)

### Community 41 - "create_app"
Cohesion: 0.27
Nodes (10): create_app(), data_update_status(), health(), paper_endpoint(), paper_or_default(), _paper_risk_config_from_env(), paper_from_env(), _positive_env_float() (+2 more)

### Community 42 - "Datadog Bits connection"
Cohesion: 0.20
Nodes (8): Bits agent instructions, Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 43 - "AdaptiveSearch"
Cohesion: 0.29
Nodes (11): Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_semantic_identity_ignores_provenance(), test_small_adaptive_batch_round_robins_families() (+3 more)

### Community 49 - "BitsError"
Cohesion: 0.06
Nodes (42): main(), call(), envelope(), action(), jobs(), fixture, test_cancel_process_after_output_streams_close(), test_execution_idempotency_and_conflict() (+34 more)

### Community 50 - "test_validation.py"
Cohesion: 0.16
Nodes (17): test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_parameter_neighbors_change_one_value(), test_validator_writes_report_and_does_not_promote_weak_strategy(), bootstrap_trade_paths(), chronological_split(), parameter_neighbors() (+9 more)

### Community 51 - "CockroachPaperTradingStore"
Cohesion: 0.35
Nodes (3): CockroachPaperTradingStore, _now(), CockroachDB is the authoritative state and idempotency store in production.

### Community 52 - "automation.py"
Cohesion: 0.14
Nodes (20): test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_html_report_contains_candidates(), test_registry_only_promotes_passing_better_candidate(), test_run_lock_rejects_overlap(), test_weekly_comparison_collects_archived_runs(), traceback, append_jsonl() (+12 more)

### Community 53 - "test_tournament_runner.py"
Cohesion: 0.29
Nodes (8): Dependence-aware bootstrap validation — 2026-08-21, setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition(), TournamentGates

### Community 54 - "PaperDecision"
Cohesion: 0.24
Nodes (6): PaperDecision, transition(), transition(), Any, datetime, Mark fresh observations and persist risk stops without an AI or order call.

### Community 55 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.10
Nodes (18): test_volume_policy_from_metadata(), CTraderVolumeConversion, CTraderVolumePolicy, DemoExecutor, NormalizedDecision, PaperToCTraderDemoCoordinator, Any, datetime (+10 more)

### Community 56 - "Repository Operating Rules"
Cohesion: 0.20
Nodes (9): Autonomous Harness, Datadog Bits operations, Execution Boundary, graphify, Local agent handoff — completed 2026-09-24, Operations, Purpose, Repository Operating Rules (+1 more)

### Community 57 - "canonical_json"
Cohesion: 0.31
Nodes (6): canonical_json(), Minimal local SQLite state stores for paper trading and the agent transcript.…, _default_state(), Deterministic, database-backed paper trading. This module has no broker…, Explicit operator reset of a stopped local paper session, after backup., zoneinfo

### Community 58 - "is_error"
Cohesion: 0.28
Nodes (8): test_is_error_extracts_code_and_description(), test_is_error_none_when_clear(), test_real_protobuf_error_types_with_empty_codes(), _field(), is_error(), Any, Shared, pure cTrader Open API account and symbol selection helpers. Used by…, Return ``(code, description)`` when a cTrader message carries an error, else…

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.06
Nodes (21): Event, test_redact_bounds_untrusted_content(), test_postgres_connection_uses_configured_read_committed(), AgentTranscriptStore, _assistant_step(), CockroachAgentTranscriptStore, ContinuousAgentRunner, _decision_id() (+13 more)

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "mutation_analytics"
Cohesion: 0.33
Nodes (3): Adaptive-mutation outcome analytics — 2026-08-21, test_mutation_analytics_measures_improvement_and_duplicates(), mutation_analytics()

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 64 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

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

### Community 72 - "PortfolioResearch"
Cohesion: 0.14
Nodes (7): test_portfolio_run_reads_validation_only(), read(), test_continuous_worker_records_idle_heartbeat(), index(), PortfolioResearch, Path, ContinuousTournamentWorker

### Community 73 - "ToolSpec"
Cohesion: 0.31
Nodes (3): RuntimeError, ToolExecutionError, ToolSpec

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 77 - "test_cli.py"
Cohesion: 0.12
Nodes (19): DemoTransport, no_broker(), stopped_demo_adapter(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_once_reports_a_refused_restart(), test_demo_automation_paper_only_skips_broker_dependencies() (+11 more)

### Community 78 - "CTraderDemoAdapter"
Cohesion: 0.09
Nodes (9): build_reconcile_request(), CTraderDemoAdapter, CTraderDemoStore, CTraderTransport, Protocol, Executes only persisted, reconciled XAUUSD demo-order proposals., Persisted execution kill switch, consulted by the shared restart policy., Verify broker account identity before an operator may start execution. (+1 more)

### Community 79 - "bits_runner.py"
Cohesion: 0.12
Nodes (19): memory(), fixture, reply(), test_history_size_and_excerpts_are_explicit(), test_memory_retains_recent_exchanges_and_source_linked_digest(), test_notes_preserve_structured_claims_and_reject_oversize(), Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate() (+11 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "Local handoff audit — 2026-09-24"
Cohesion: 0.29
Nodes (5): Follow-up implementation, Local handoff audit — 2026-09-24, Local validation and deployment, Planner latency (read-only), Recommended next work

### Community 82 - "cTrader SDK and protocol review (no broker connection)"
Cohesion: 0.29
Nodes (5): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Order lifecycle and errors — follow-up #15, Position reconciliation — follow-up #16

### Community 84 - "market_is_open"
Cohesion: 0.33
Nodes (6): test_market_is_open_across_both_us_daylight_saving_transitions(), test_market_is_open_follows_the_new_york_close_in_us_standard_time(), utc(), market_is_open(), Computed, display-only paper results for the live view., XAUUSD spot session: Sunday 18:00 to Friday 17:00 New York time, break…

### Community 87 - "ExecutionConfig"
Cohesion: 0.22
Nodes (18): numpy, pandas, sklearn_metrics, main(), Secret-free deterministic parity fixture for the runtime container., bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path() (+10 more)

### Community 90 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (21): P0/P1 implementation updates — 2026-08-20, Exception, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible() (+13 more)

### Community 92 - "HistoricalDataStore"
Cohesion: 0.18
Nodes (9): test_store_rejects_invalid_ohlc(), test_store_roundtrip(), _agent_data_refresh_source(), Bound data refresh for a stale agent tick. Runs the one-shot downloader in a…, CTraderHistoricalAdapter, HistoricalDataStore, DataFrame, Local OHLCV store. The adapter accepts historical exports only; no execution… (+1 more)

### Community 93 - "CTraderOpenApiDownloader"
Cohesion: 0.23
Nodes (8): test_trendbar_delta_decoding(), Timestamp, CTraderOpenApiDownloader, Any, datetime, Decode cTrader's low-plus-delta trendbar representation., Read-only cTrader Open API client for symbols and historical trendbars., trendbars_to_frame()

### Community 94 - ".run"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

### Community 95 - "TournamentDataset"
Cohesion: 0.20
Nodes (10): dataset(), test_content_change_creates_new_version(), test_frozen_dataset_is_reproducible_and_partitioned(), test_partitions_read_exact_manifest_counts(), test_tampering_is_detected(), frame_digest(), DataFrame, Hash canonical timestamps, schema, and values independent of Parquet bytes. (+2 more)

### Community 96 - "ProposalEngine"
Cohesion: 0.53
Nodes (4): test_proposal_catalog_eventually_exhausts(), novel_proposals(), Proposal, ProposalEngine

## Knowledge Gaps
- **127 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+122 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 566 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `synthetic_bars`, `What You Must Do When Invoked`, `test_data.py`, `cli.py`, `test_agent_loop.py`, `automation.py`, `agent_loop.py`, `TournamentDataset`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `MemoryRegistry` connect `MemoryRegistry` to `ExperimentSpec`, `synthetic_bars`, `memory_registry.py`, `OperationsManager`, `ProposalEngine`, `ExperimentRegistry`, `ShadowTradingReadiness`, `test_experiment_registry.py`, `AdaptiveSearch`, `CodexImprovementWorkflow`, `test_dashboard.py`, `test_tournament_runner.py`, `RemoteComputeBridge`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `ExperimentRegistry` connect `ExperimentRegistry` to `ExperimentSpec`, `synthetic_bars`, `OperationsManager`, `dashboard.py`, `ProposalEngine`, `ShadowTradingReadiness`, `test_experiment_registry.py`, `PortfolioResearch`, `AdaptiveSearch`, `cli.py`, `CodexImprovementWorkflow`, `portfolio_research.py`, `test_tournament_runner.py`, `.__init__`, `agent_loop.py`, `RemoteComputeBridge`, `TournamentRunner`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_maybe_resume_preserves_every_persisted_stop_except_fresh_state()`) actually correct?**
  _`PaperTrading` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `main()` (e.g. with `CTraderAuthError` and `CTraderOpenApiConfig`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._