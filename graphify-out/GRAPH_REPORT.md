# Graph Report - xauusd  (2026-09-20)

## Corpus Check
- 101 files · ~71,678 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 6, .service 3, .example 1)

## Summary
- 1680 nodes · 4658 edges · 77 communities (64 shown, 13 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 218 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `56b1aafa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PaperTrading
- autonomous_harness.py
- OperationsManager
- dashboard.py
- test_demo_execution.py
- ExperimentRegistry
- test_demo_runner.py
- firecrawl_research.py
- MemoryRegistry
- HistoricalDataStore
- test_ctrader_demo.py
- RemoteComputeBridge
- ExecutionConfig
- synthetic_bars
- pytest
- DemoLifecycle
- ml_campaign.py
- Any
- test_agent_loop.py
- validation.py
- cli.py
- CodexImprovementWorkflow
- portfolio_research.py
- ShadowTradingReadiness
- XAUUSD discovery, incident, quantitative, and scaling audit
- PaperToCTraderDemoCoordinator
- ConfirmedBreakoutCanarySource
- TournamentDataset
- TournamentRunner
- What You Must Do When Invoked
- test_oauth.py
- CockroachCTraderDemoStore
- InMemoryCTraderDemoStore
- ctrader_demo.py
- memory_registry.py
- main
- core.py
- CockroachAgentTranscriptStore
- InMemoryAgentTranscriptStore
- pandas
- test_tournament_runner.py
- .run
- test_ctrader_auth.py
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- test_agent_view.py
- DemoAutomationRunner
- SQLiteAgentTranscriptStore
- automation.py
- Repository Operating Rules
- test_state_backup.py
- test_search_space.py
- paper_trading.py
- agent_loop.py
- _paper_to_demo_coordinator
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- DemoRunnerConfig
- test_tournament_data.py
- graphify reference: query, path, explain
- Any
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- _atomic_json
- failure_code
- test_health_uses_configured_cockroach_registry
- Architecture and data-flow map
- opencode.json

## God Nodes (most connected - your core abstractions)
1. `MemoryRegistry` - 88 edges
2. `ExperimentRegistry` - 75 edges
3. `PaperTrading` - 69 edges
4. `XAUUSD discovery, incident, quantitative, and scaling audit` - 54 edges
5. `main()` - 50 edges
6. `HistoricalDataStore` - 43 edges
7. `InMemoryPaperTradingStore` - 41 edges
8. `synthetic_bars()` - 40 edges
9. `RemoteComputeBridge` - 40 edges
10. `ExecutionConfig` - 39 edges

## Surprising Connections (you probably didn't know these)
- `Clean lease-drained saturation benchmark — 2026-08-20` --references--> `completed()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → tests/test_adaptive_search.py
- `Engineering` --references--> `agent_transcript_store_from_env()`  [INFERRED]
  AGENTS.md → xauusd/agent_loop.py
- `P0/P1 implementation updates — 2026-08-20` --references--> `failure_code()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → xauusd/distributed_compute.py
- `Engineering` --references--> `paper_from_env()`  [INFERRED]
  AGENTS.md → xauusd/paper_trading.py
- `Operations` --references--> `paper_from_env()`  [INFERRED]
  AGENTS.md → xauusd/paper_trading.py

## Import Cycles
- None detected.

## Communities (77 total, 13 thin omitted)

### Community 0 - "PaperTrading"
Cohesion: 0.13
Nodes (30): sys, paper_trading(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_paper_only_skips_broker_dependencies(), test_paper_start_overrides_operator_stop(), test_paper_stop_persists_kill_switch(), decision() (+22 more)

### Community 1 - "autonomous_harness.py"
Cohesion: 0.06
Nodes (36): concurrent_futures, re, planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts() (+28 more)

### Community 2 - "OperationsManager"
Cohesion: 0.11
Nodes (20): gzip, test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost() (+12 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (63): asyncio, fastapi_security, fastapi_testclient, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected) (+55 more)

### Community 4 - "test_demo_execution.py"
Cohesion: 0.20
Nodes (18): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches(), test_duplicate_decision_cannot_produce_another_broker_request() (+10 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.07
Nodes (31): Gate-failure and near-pass analytics — 2026-08-21, ExperimentStatus, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence() (+23 more)

### Community 6 - "test_demo_runner.py"
Cohesion: 0.18
Nodes (11): Adapter, DecisionSource, MarketSource, paper_only_runner(), runner(), test_cycle_failure_stops_after_configured_consecutive_failures(), test_disabled_config_does_not_reconcile_or_start(), test_paper_only_start_skips_broker_reconciliation_and_runs_cycle() (+3 more)

### Community 7 - "firecrawl_research.py"
Cohesion: 0.09
Nodes (21): parametrize, test_postgres_connection_uses_configured_read_committed(), client(), test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit() (+13 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "HistoricalDataStore"
Cohesion: 0.06
Nodes (44): Interpreter guard for subcommands, test_data_update_does_not_retry_auth_errors(), download(), test_data_update_retries_transient_failures(), demo_env(), downloader_config(), minute_60(), one_bar_at() (+36 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.10
Nodes (26): adapter(), FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation() (+18 more)

### Community 11 - "RemoteComputeBridge"
Cohesion: 0.16
Nodes (17): setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock(), test_readiness_uses_most_constrained_mount() (+9 more)

### Community 12 - "ExecutionConfig"
Cohesion: 0.14
Nodes (22): main(), Secret-free deterministic parity fixture for the runtime container., bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path(), test_compact_attribution_metrics_reconcile_and_measure_concentration(), test_signal_executes_at_next_open_without_lookahead(), test_spread_slippage_and_commission_are_charged_both_sides() (+14 more)

### Community 13 - "synthetic_bars"
Cohesion: 0.14
Nodes (26): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+18 more)

### Community 14 - "pytest"
Cohesion: 0.06
Nodes (35): ImportError, importlib, pytest, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing (+27 more)

### Community 15 - "DemoLifecycle"
Cohesion: 0.22
Nodes (4): DemoLifecycle, MarketDataSource, Protocol, Read-only source for the latest executable market observation.

### Community 16 - "ml_campaign.py"
Cohesion: 0.13
Nodes (27): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, numpy, sklearn_metrics, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible() (+19 more)

### Community 17 - "Any"
Cohesion: 0.18
Nodes (8): CTraderDemoOpenApiTransport, failed(), issue(), succeeded(), Any, Synchronous, bounded cTrader demo transport. Construction and import are inert.…, Read-only broker volume/price metadata for the resolved demo symbol., Return ``(code, description)`` for a cTrader error message, else None.

### Community 18 - "test_agent_loop.py"
Cohesion: 0.12
Nodes (31): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), refresh_config(), refresh_runner(), ScriptedPlanner (+23 more)

### Community 19 - "validation.py"
Cohesion: 0.20
Nodes (14): test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_parameter_neighbors_change_one_value(), bootstrap_trade_paths(), chronological_split(), parameter_neighbors(), DataFrame (+6 more)

### Community 20 - "cli.py"
Cohesion: 0.22
Nodes (20): base64, collections, dataclasses, datetime, hashlib, json, logging, math (+12 more)

### Community 21 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 22 - "portfolio_research.py"
Cohesion: 0.17
Nodes (22): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), read(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete() (+14 more)

### Community 23 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.14
Nodes (14): DemoExecutor, NormalizedDecision, PaperToCTraderDemoCoordinator, Any, datetime, Protocol, Coordinates accepted paper decisions with explicitly started cTrader demo…, Evaluate paper risk first; broker submission only happens behind all gates. (+6 more)

### Community 26 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.17
Nodes (15): store_with_bars(), test_canary_ignores_neutral_and_persistent_signals(), test_canary_transition_has_stable_identity_and_side(), test_local_historical_market_source_reads_final_close_and_utc_time(), handler(), _mock_market_for_read(), ConfirmedBreakoutCanarySource, LocalHistoricalMarketDataSource (+7 more)

### Community 27 - "TournamentDataset"
Cohesion: 0.40
Nodes (4): frame_digest(), DataFrame, Hash canonical timestamps, schema, and values independent of Parquet bytes., TournamentDataset

### Community 28 - "TournamentRunner"
Cohesion: 0.25
Nodes (4): _finite(), Path, Consume deterministic experiments without reading the holdout test set., TournamentRunner

### Community 29 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.07
Nodes (38): PathLike, Architecture, Autonomous Agent, Configuration, Current Status, Delivery Stages, Demo Automation, Demo Automation Service (+30 more)

### Community 31 - "CockroachCTraderDemoStore"
Cohesion: 0.41
Nodes (4): _canonical_json(), CockroachCTraderDemoStore, _now(), Authoritative persistent execution state, idempotency, and audit store.

### Community 32 - "InMemoryCTraderDemoStore"
Cohesion: 0.18
Nodes (3): _initial_state(), InMemoryCTraderDemoStore, Test double only; production execution state belongs in CockroachDB.

### Community 33 - "ctrader_demo.py"
Cohesion: 0.09
Nodes (13): build_new_order_request(), build_reconcile_request(), CTraderDemoAdapter, CTraderDemoStore, CTraderTransport, Protocol, Fail-closed cTrader Open API execution boundary for verified demo accounts., Executes only persisted, reconciled XAUUSD demo-order proposals. (+5 more)

### Community 34 - "memory_registry.py"
Cohesion: 0.18
Nodes (3): copy, MemoryConnection, MemoryCursor

### Community 35 - "main"
Cohesion: 0.15
Nodes (17): test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_requires_explicit_positive_volume(), test_demo_automation_status_reports_paper_only_flag(), test_state_integrity_backup_restore_round_trip(), test_agent_transcript_backend_selection_defaults_to_local(), agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., agent_controller() (+9 more)

### Community 36 - "core.py"
Cohesion: 0.27
Nodes (8): test_backtest(), campaign(), event_backtest(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 39 - "pandas"
Cohesion: 0.31
Nodes (8): argparse, pandas, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 40 - "test_tournament_runner.py"
Cohesion: 0.15
Nodes (10): Dependence-aware bootstrap validation — 2026-08-21, setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition() (+2 more)

### Community 41 - ".run"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

### Community 42 - "test_ctrader_auth.py"
Cohesion: 0.12
Nodes (34): account(), test_demo_accounts_empty_when_all_live(), test_demo_accounts_filters_live_and_missing_flag(), test_is_error_extracts_code_and_description(), test_is_error_none_when_clear(), test_resolve_symbol_falls_back_to_first_match(), test_resolve_symbol_prefers_enabled_match(), test_resolve_symbol_rejects_invalid_id() (+26 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.19
Nodes (14): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+6 more)

### Community 49 - "test_agent_view.py"
Cohesion: 0.08
Nodes (23): FastAPI, fastapi_responses, fixture, test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), server(), test_age_seconds_parses_timezone_aware_timestamps() (+15 more)

### Community 50 - "DemoAutomationRunner"
Cohesion: 0.30
Nodes (4): DemoAutomationRunner, Any, Poll injected sources only after explicit enablement and reconciliation., Reconcile first, then make the explicitly enabled paper/demo pair runnable.

### Community 51 - "SQLiteAgentTranscriptStore"
Cohesion: 0.15
Nodes (10): Connection, Row, test_sqlite_transcript_reconciles_running_orphans(), test_sqlite_transcript_store_round_trips_steps_and_runs(), _connect(), _now(), Any, Local SQLite replacement for the CockroachDB agent transcript store. (+2 more)

### Community 52 - "automation.py"
Cohesion: 0.15
Nodes (18): test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_html_report_contains_candidates(), test_registry_only_promotes_passing_better_candidate(), test_run_lock_rejects_overlap(), test_weekly_comparison_collects_archived_runs(), traceback, append_jsonl() (+10 more)

### Community 53 - "Repository Operating Rules"
Cohesion: 0.20
Nodes (8): Autonomous Harness, Engineering, Execution Boundary, graphify, Operations, Purpose, Repository Operating Rules, Auto-resume on a benign restart; fail closed on persisted trouble. A paper…

### Community 54 - "test_state_backup.py"
Cohesion: 0.17
Nodes (22): sqlite3, decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+14 more)

### Community 55 - "test_search_space.py"
Cohesion: 0.23
Nodes (15): E. Current 50,000-scenario architecture and benchmark, dotenv, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix() (+7 more)

### Community 56 - "paper_trading.py"
Cohesion: 0.20
Nodes (16): decision(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store(), test_sqlite_integrity_check_detects_corruption(), test_sqlite_paper_store_corrupt_state_fails_closed(), test_sqlite_paper_store_integrity_check_reports_ok(), test_sqlite_paper_store_kill_switch_persists_and_fails_closed(), test_sqlite_paper_store_persists_state_and_decision_idempotency() (+8 more)

### Community 57 - "agent_loop.py"
Cohesion: 0.24
Nodes (13): threading, build_agent_registry(), canary_signal_tool(), _decision_id(), paper_state_tool(), _positive_float(), propose_trade_tool(), handler() (+5 more)

### Community 58 - "_paper_to_demo_coordinator"
Cohesion: 0.21
Nodes (7): test_volume_policy_from_metadata(), _paper_to_demo_coordinator(), CTraderVolumeConversion, CTraderVolumePolicy, Explicit conversion from paper quantity units to cTrader volume-in-cents units., Broker-declared volume constraints; a volume failing any rule must be rejected…, Return a rejection reason when volume violates broker constraints, else None.

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.11
Nodes (13): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, Protocol, Display-friendly assistant step: parsed action plus the model's plain-English… (+5 more)

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "DemoRunnerConfig"
Cohesion: 0.33
Nodes (6): test_environment_config_is_disabled_unless_explicitly_true(), demo_automation(), _demo_automation_status(), Run the explicitly enabled local-data paper-to-demo canary., DemoRunnerConfig, datetime

### Community 62 - "test_tournament_data.py"
Cohesion: 0.36
Nodes (6): dataset(), test_content_change_creates_new_version(), test_frozen_dataset_is_reproducible_and_partitioned(), test_partitions_read_exact_manifest_counts(), test_tampering_is_detected(), TournamentDataConfig

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 64 - "Any"
Cohesion: 0.14
Nodes (10): _default_state(), market_is_open(), PaperDecision, transition(), PaperTradingStore, Any, datetime, Protocol (+2 more)

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

### Community 72 - "failure_code"
Cohesion: 0.29
Nodes (4): P0/P1 implementation updates — 2026-08-20, Exception, test_remote_failure_codes_are_structured(), failure_code()

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

## Knowledge Gaps
- **102 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 472 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `main`, `core.py`, `ExecutionConfig`, `ml_campaign.py`, `test_agent_loop.py`, `cli.py`, `automation.py`, `ConfirmedBreakoutCanarySource`, `TournamentDataset`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `Any`, `main`, `test_demo_execution.py`, `test_demo_runner.py`, `test_agent_view.py`, `test_agent_loop.py`, `cli.py`, `Repository Operating Rules`, `test_state_backup.py`, `paper_trading.py`, `agent_loop.py`, `_paper_to_demo_coordinator`, `ContinuousAgentRunner`, `PaperToCTraderDemoCoordinator`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `ExperimentRegistry` connect `ExperimentRegistry` to `OperationsManager`, `main`, `dashboard.py`, `_atomic_json`, `MemoryRegistry`, `test_tournament_runner.py`, `RemoteComputeBridge`, `AdaptiveSearch`, `synthetic_bars`, `ShadowTradingReadiness`, `CodexImprovementWorkflow`, `cli.py`, `test_search_space.py`, `XAUUSD discovery, incident, quantitative, and scaling audit`, `portfolio_research.py`, `TournamentRunner`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `build_agent_registry()`) actually correct?**
  _`PaperTrading` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `main()` (e.g. with `CTraderAuthError` and `CTraderOpenApiConfig`) actually correct?**
  _`main()` has 3 INFERRED edges - model-reasoned connections that need verification._