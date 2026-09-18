# Graph Report - xauusd  (2026-09-18)

## Corpus Check
- 91 files · ~64,179 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 6, .service 2, .example 1)

## Summary
- 1381 nodes · 3883 edges · 71 communities (59 shown, 12 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 171 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3a553530`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PaperTrading
- ToolRegistry
- OperationsManager
- dashboard.py
- test_demo_execution.py
- ExperimentRegistry
- test_demo_runner.py
- FirecrawlResearchClient
- MemoryRegistry
- pytest
- test_ctrader_demo.py
- RemoteComputeBridge
- EventDrivenBacktester
- build_features
- ml_models.py
- demo_runner.py
- test_ml.py
- Any
- test_agent_loop.py
- test_validation.py
- agent_loop.py
- CodexImprovementWorkflow
- portfolio_research.py
- ShadowTradingReadiness
- ContinuousAgentRunner
- PaperToCTraderDemoCoordinator
- ConfirmedBreakoutCanarySource
- TournamentDataset
- TournamentRunner
- What You Must Do When Invoked
- CTraderDemoSafetyError
- CockroachCTraderDemoStore
- InMemoryCTraderDemoStore
- CTraderDemoStore
- memory_registry.py
- cli.py
- synthetic_bars
- CockroachAgentTranscriptStore
- InMemoryAgentTranscriptStore
- verify_result_parity.py
- test_tournament_runner.py
- .run
- HistoricalDataStore
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- create_app
- DemoAutomationRunner
- test_dashboard.py
- test_experiment_registry.py
- paper_from_env
- ExecutionConfig
- PostgresConnection
- CockroachHarnessStore
- CockroachPaperTradingStore
- test_strategy_proposals.py
- Any
- graphify reference: extra exports and benchmark
- test_cli.py
- pandas
- graphify reference: query, path, explain
- PaperTradingStore
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md

## God Nodes (most connected - your core abstractions)
1. `MemoryRegistry` - 88 edges
2. `ExperimentRegistry` - 75 edges
3. `PaperTrading` - 46 edges
4. `RemoteComputeBridge` - 40 edges
5. `synthetic_bars()` - 40 edges
6. `ExecutionConfig` - 39 edges
7. `HistoricalDataStore` - 38 edges
8. `StrategySpec` - 38 edges
9. `build_features()` - 38 edges
10. `OperationsManager` - 37 edges

## Surprising Connections (you probably didn't know these)
- `Operations` --references--> `paper_from_env()`  [INFERRED]
  AGENTS.md → xauusd/paper_trading.py
- `Step 2.5 - Transcribe video / audio files (only if video files detected)` --references--> `export()`  [INFERRED]
  .opencode/skills/graphify/references/transcribe.md → xauusd/dashboard.py
- `test_paper_endpoint_reflects_accepted_fill()` --calls--> `PaperDecision`  [EXTRACTED]
  tests/test_agent_view.py → xauusd/paper_trading.py
- `test_result_root_is_not_created_per_scenario()` --uses--> `RemoteComputeBridge`  [INFERRED]
  tests/test_distributed_compute.py → xauusd/distributed_compute.py
- `test_store_rejects_invalid_ohlc()` --calls--> `HistoricalDataStore`  [EXTRACTED]
  tests/test_data.py → xauusd/data.py

## Import Cycles
- None detected.

## Communities (71 total, 12 thin omitted)

### Community 0 - "PaperTrading"
Cohesion: 0.13
Nodes (18): paper_trading(), decision(), test_corrupt_memory_state_fails_closed(), test_duplicate_decision_returns_persisted_outcome_without_second_fill(), test_missing_state_defaults_to_stopped_and_requires_explicit_start(), test_position_freshness_and_daily_loss_gates_are_deterministic(), test_simulated_ledger_realizes_profit_when_position_is_closed(), test_summary_includes_equity_pnl_drawdown_and_recent_fills() (+10 more)

### Community 1 - "ToolRegistry"
Cohesion: 0.08
Nodes (30): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+22 more)

### Community 2 - "OperationsManager"
Cohesion: 0.08
Nodes (22): gzip, test_research_brief_is_redacted_and_aggregated(), test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs() (+14 more)

### Community 3 - "dashboard.py"
Cohesion: 0.09
Nodes (54): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), plotly_graph_objects (+46 more)

### Community 4 - "test_demo_execution.py"
Cohesion: 0.17
Nodes (20): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches(), test_duplicate_decision_cannot_produce_another_broker_request() (+12 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.09
Nodes (23): ExperimentStatus, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors(), test_selection_bias_computes_bh_and_aligned_fold_pbo(), test_selection_bias_reports_score_distribution_and_missing_controls() (+15 more)

### Community 6 - "test_demo_runner.py"
Cohesion: 0.17
Nodes (12): Adapter, DecisionSource, MarketSource, paper_only_runner(), runner(), test_cycle_failure_stops_after_configured_consecutive_failures(), test_disabled_config_does_not_reconcile_or_start(), test_paper_only_start_skips_broker_reconciliation_and_runs_cycle() (+4 more)

### Community 7 - "FirecrawlResearchClient"
Cohesion: 0.14
Nodes (17): parametrize, client(), test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 9 - "pytest"
Cohesion: 0.08
Nodes (35): pytest, test_store_rejects_invalid_ohlc(), test_store_roundtrip(), test_trendbar_delta_decoding(), test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), Timestamp (+27 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.09
Nodes (25): adapter(), FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation() (+17 more)

### Community 11 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (22): Exception, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+14 more)

### Community 12 - "EventDrivenBacktester"
Cohesion: 0.29
Nodes (12): main(), Secret-free deterministic parity fixture for the runtime container., bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path(), test_compact_attribution_metrics_reconcile_and_measure_concentration(), test_signal_executes_at_next_open_without_lookahead(), test_spread_slippage_and_commission_are_charged_both_sides() (+4 more)

### Community 13 - "build_features"
Cohesion: 0.13
Nodes (29): itertools, main(), test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_catalog_is_deterministic_and_valid() (+21 more)

### Community 14 - "ml_models.py"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 15 - "demo_runner.py"
Cohesion: 0.13
Nodes (11): tempfile, test_environment_config_is_disabled_unless_explicitly_true(), DecisionSource, DemoLifecycle, DemoRunnerConfig, MarketDataSource, datetime, Protocol (+3 more)

### Community 16 - "test_ml.py"
Cohesion: 0.17
Nodes (19): ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined(), EnsembleConfig, DataFrame, Path (+11 more)

### Community 17 - "Any"
Cohesion: 0.18
Nodes (8): CTraderDemoOpenApiTransport, failed(), issue(), succeeded(), Any, Synchronous, bounded cTrader demo transport. Construction and import are inert.…, Read-only broker volume/price metadata for the resolved demo symbol., Return ``(code, description)`` for a cTrader error message, else None.

### Community 18 - "test_agent_loop.py"
Cohesion: 0.17
Nodes (24): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), ScriptedPlanner, test_assistant_steps_carry_parsed_action_and_human_reason(), test_assistant_steps_without_reason_remain_well_formed() (+16 more)

### Community 19 - "test_validation.py"
Cohesion: 0.18
Nodes (16): test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_chronological_splits_are_ordered_and_disjoint(), test_parameter_neighbors_change_one_value(), test_walk_forward_never_trains_on_future(), bootstrap_trade_paths(), chronological_split() (+8 more)

### Community 20 - "agent_loop.py"
Cohesion: 0.06
Nodes (53): base64, collections, concurrent_futures, dataclasses, datetime, hashlib, json, math (+45 more)

### Community 21 - "CodexImprovementWorkflow"
Cohesion: 0.24
Nodes (8): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), CodexImprovementWorkflow, CodexWorkflowConfig, Path, Create review-only Codex candidates in disposable detached worktrees.

### Community 22 - "portfolio_research.py"
Cohesion: 0.20
Nodes (19): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal(), aligned_returns() (+11 more)

### Community 23 - "ShadowTradingReadiness"
Cohesion: 0.14
Nodes (13): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), test_adaptive_generations_wait_for_completion_interval() (+5 more)

### Community 24 - "ContinuousAgentRunner"
Cohesion: 0.21
Nodes (8): Event, test_redact_bounds_untrusted_content(), _assistant_step(), ContinuousAgentRunner, Display-friendly assistant step: parsed action plus the model's plain-English…, Transcript-friendly view: keep structures, bound untrusted string lengths., Drives one planner per tick; every action and outcome becomes a visible…, _redact_for_transcript()

### Community 25 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.11
Nodes (17): test_volume_policy_from_metadata(), CTraderVolumePolicy, DemoExecutor, NormalizedDecision, PaperToCTraderDemoCoordinator, Any, datetime, Protocol (+9 more)

### Community 26 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.12
Nodes (16): store_with_bars(), test_canary_ignores_neutral_and_persistent_signals(), test_canary_transition_has_stable_identity_and_side(), test_local_historical_market_source_reads_final_close_and_utc_time(), handler(), _mock_market_for_read(), ConfirmedBreakoutCanaryConfig, ConfirmedBreakoutCanarySource (+8 more)

### Community 27 - "TournamentDataset"
Cohesion: 0.35
Nodes (4): frame_digest(), DataFrame, Hash canonical timestamps, schema, and values independent of Parquet bytes., TournamentDataset

### Community 28 - "TournamentRunner"
Cohesion: 0.25
Nodes (4): _finite(), Path, Consume deterministic experiments without reading the holdout test set., TournamentRunner

### Community 29 - "What You Must Do When Invoked"
Cohesion: 0.07
Nodes (25): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+17 more)

### Community 30 - "CTraderDemoSafetyError"
Cohesion: 0.18
Nodes (10): build_reconcile_request(), CTraderDemoAdapter, CTraderDemoSafetyError, RuntimeError, A configuration, recovery, or execution condition that must fail closed., Executes only persisted, reconciled XAUUSD demo-order proposals., Verify broker account identity before an operator may start execution., Persist a minimal non-secret receipt, not arbitrary transport objects. (+2 more)

### Community 31 - "CockroachCTraderDemoStore"
Cohesion: 0.41
Nodes (4): _canonical_json(), CockroachCTraderDemoStore, _now(), Authoritative persistent execution state, idempotency, and audit store.

### Community 32 - "InMemoryCTraderDemoStore"
Cohesion: 0.18
Nodes (3): _initial_state(), InMemoryCTraderDemoStore, Test double only; production execution state belongs in CockroachDB.

### Community 33 - "CTraderDemoStore"
Cohesion: 0.15
Nodes (3): CTraderDemoStore, CTraderTransport, Protocol

### Community 34 - "memory_registry.py"
Cohesion: 0.18
Nodes (3): copy, MemoryConnection, MemoryCursor

### Community 35 - "cli.py"
Cohesion: 0.22
Nodes (13): dotenv, _positive_float(), agent_controller(), _agent_status_view(), demo_automation(), _demo_automation_runner(), _demo_automation_status(), _paper_from_env() (+5 more)

### Community 36 - "synthetic_bars"
Cohesion: 0.19
Nodes (15): logging, test_backtest(), dataset(), test_content_change_creates_new_version(), test_frozen_dataset_is_reproducible_and_partitioned(), test_partitions_read_exact_manifest_counts(), test_tampering_is_detected(), campaign() (+7 more)

### Community 39 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 40 - "test_tournament_runner.py"
Cohesion: 0.23
Nodes (7): setup_runner(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition(), TournamentGates

### Community 41 - ".run"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

### Community 42 - "HistoricalDataStore"
Cohesion: 0.14
Nodes (17): DailyResearchPipeline, datetime, daily_run(), event_backtest(), main(), ml_research(), ml_walk_forward(), research_campaign() (+9 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.19
Nodes (13): completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates(), test_semantic_identity_ignores_provenance(), test_small_adaptive_batch_round_robins_families() (+5 more)

### Community 49 - "create_app"
Cohesion: 0.15
Nodes (10): FastAPI, fastapi_responses, fixture, server(), read(), create_app(), index(), paper_endpoint() (+2 more)

### Community 50 - "DemoAutomationRunner"
Cohesion: 0.30
Nodes (4): DemoAutomationRunner, Any, Poll injected sources only after explicit enablement and reconciliation., Reconcile first, then make the explicitly enabled paper/demo pair runnable.

### Community 51 - "test_dashboard.py"
Cohesion: 0.20
Nodes (9): fastapi_testclient, setup_files(), test_dashboard_reads_latest_run_and_equity(), test_dashboard_registry_requires_database_url_and_never_passes_a_path(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature(), test_system_metrics_calculate_network_rate() (+1 more)

### Community 52 - "test_experiment_registry.py"
Cohesion: 0.26
Nodes (13): spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity(), test_registry_requires_cockroach_database_url(), test_remote_error_can_requeue_owned_experiment() (+5 more)

### Community 53 - "paper_from_env"
Cohesion: 0.17
Nodes (11): Autonomous Harness, Engineering, Execution Boundary, graphify, Operations, Purpose, Repository Operating Rules, _paper_risk_config_from_env() (+3 more)

### Community 54 - "ExecutionConfig"
Cohesion: 0.23
Nodes (6): HistGradientBoostingClassifier, test_gradient_boosting_report_is_reproducible(), test_validator_writes_report_and_does_not_promote_weak_strategy(), ExecutionConfig, GradientBoostingResearch, ValidationConfig

### Community 55 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 57 - "CockroachPaperTradingStore"
Cohesion: 0.35
Nodes (3): CockroachPaperTradingStore, _now(), CockroachDB is the authoritative state and idempotency store in production.

### Community 58 - "test_strategy_proposals.py"
Cohesion: 0.31
Nodes (6): test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), novel_proposals(), Proposal, ProposalEngine, ContinuousTournamentWorker

### Community 59 - "Any"
Cohesion: 0.22
Nodes (3): AgentTranscriptStore, Any, Protocol

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "test_cli.py"
Cohesion: 0.22
Nodes (6): sys, test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_paper_only_skips_broker_dependencies(), test_demo_automation_requires_explicit_positive_volume(), test_demo_automation_status_reports_paper_only_flag(), xauusd

### Community 62 - "pandas"
Cohesion: 0.75
Nodes (3): numpy, pandas, sklearn_metrics

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

## Knowledge Gaps
- **47 isolated node(s):** `Usage`, `What graphify is for`, `Step 0 - GitHub repos and multi-path merge (only if a URL or several paths)`, `Step 1 - Ensure graphify is installed`, `Step 2 - Detect files` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 367 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExperimentRegistry` connect `ExperimentRegistry` to `OperationsManager`, `cli.py`, `dashboard.py`, `test_tournament_runner.py`, `HistoricalDataStore`, `RemoteComputeBridge`, `AdaptiveSearch`, `build_features`, `test_experiment_registry.py`, `CodexImprovementWorkflow`, `agent_loop.py`, `ShadowTradingReadiness`, `portfolio_research.py`, `test_strategy_proposals.py`, `TournamentRunner`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `CTraderDemoOpenApiTransport` connect `Any` to `test_ctrader_demo.py`, `cli.py`, `agent_loop.py`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `cli.py`, `pytest`, `test_agent_loop.py`, `agent_loop.py`, `ConfirmedBreakoutCanarySource`, `TournamentDataset`, `What You Must Do When Invoked`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `build_agent_registry()`) actually correct?**
  _`PaperTrading` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `RemoteComputeBridge` (e.g. with `test_result_root_is_not_created_per_scenario()` and `tournament_equity()`) actually correct?**
  _`RemoteComputeBridge` has 9 INFERRED edges - model-reasoned connections that need verification._