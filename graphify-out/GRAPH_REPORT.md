# Graph Report - xauusd  (2026-09-23)

## Corpus Check
- 111 files · ~80,029 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 6, .service 4, .example 1)

## Summary
- 1837 nodes · 5118 edges · 92 communities (78 shown, 14 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 275 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b20264e1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PaperTrading
- test_autonomous_harness.py
- main
- dashboard.py
- test_demo_execution.py
- ExperimentRegistry
- test_demo_runner.py
- firecrawl_research.py
- MemoryRegistry
- ml_models.py
- test_ctrader_demo.py
- RemoteComputeBridge
- pandas
- synthetic_bars
- self_improve.py
- test_weekly_report.py
- ExecutionConfig
- Any
- test_agent_loop.py
- paper_trading.py
- OpenAICompatiblePlanner
- test_agent_view.py
- TournamentDataset
- ShadowTradingReadiness
- XAUUSD discovery, incident, quantitative, and scaling audit
- cli.py
- ConfirmedBreakoutCanarySource
- test_offline.py
- CodexImprovementWorkflow
- PaperToCTraderDemoCoordinator
- test_oauth.py
- CockroachCTraderDemoStore
- ExperimentSpec
- test_local_state.py
- memory_registry.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- InMemoryAgentTranscriptStore
- ToolExecutionError
- core.py
- test_tournament_runner.py
- .run
- test_ctrader_auth.py
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- BitsError
- SQLiteAgentTranscriptStore
- agent_controller
- automation.py
- portfolio_research.py
- CTraderAuthError
- agent_loop.py
- TournamentRunner
- test_state_backup.py
- CTraderDemoStore
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- verify_result_parity.py
- /graphify
- graphify reference: query, path, explain
- Repository Operating Rules
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- ._fetch
- DemoAutomationRunner
- ctrader_demo.py
- Architecture and data-flow map
- test_health_uses_configured_cockroach_registry
- opencode.json
- autonomous_harness.py
- PostgresConnection
- EventDrivenBacktester
- test_data.py
- HistoricalDataStore
- CTraderOpenApiDownloader
- CockroachHarnessStore
- test_bits_runner.py
- HarnessStore
- DemoRunnerConfig
- test_tournament_data.py
- DemoLifecycle
- _atomic_json
- failure_code

## God Nodes (most connected - your core abstractions)
1. `MemoryRegistry` - 88 edges
2. `ExperimentRegistry` - 75 edges
3. `PaperTrading` - 72 edges
4. `XAUUSD discovery, incident, quantitative, and scaling audit` - 54 edges
5. `main()` - 51 edges
6. `HistoricalDataStore` - 44 edges
7. `InMemoryPaperTradingStore` - 44 edges
8. `synthetic_bars()` - 40 edges
9. `RemoteComputeBridge` - 40 edges
10. `canonical_json()` - 40 edges

## Surprising Connections (you probably didn't know these)
- `12. Status of evidence` --references--> `OpenAICompatiblePlanner`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → xauusd/autonomous_harness.py
- `Clean lease-drained saturation benchmark — 2026-08-20` --references--> `completed()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → tests/test_adaptive_search.py
- `8. Prototype gate and test plan (execute BEFORE any cutover)` --references--> `tool()`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → tests/test_autonomous_harness.py
- `Engineering` --references--> `agent_transcript_store_from_env()`  [INFERRED]
  AGENTS.md → xauusd/agent_loop.py
- `3. Where the planner is wired today (confirmed)` --references--> `parse_action()`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → xauusd/autonomous_harness.py

## Import Cycles
- None detected.

## Communities (92 total, 14 thin omitted)

### Community 0 - "PaperTrading"
Cohesion: 0.12
Nodes (32): test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_paper_only_skips_broker_dependencies(), test_demo_automation_requires_explicit_positive_volume(), test_paper_start_overrides_operator_stop(), test_paper_stop_persists_kill_switch(), decision(), test_corrupt_memory_state_fails_closed() (+24 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.17
Nodes (16): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+8 more)

### Community 2 - "main"
Cohesion: 0.10
Nodes (24): gzip, test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_status_reports_paper_only_flag(), test_state_integrity_backup_restore_round_trip(), test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path() (+16 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (63): asyncio, fastapi_security, fastapi_testclient, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected) (+55 more)

### Community 4 - "test_demo_execution.py"
Cohesion: 0.20
Nodes (18): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches(), test_duplicate_decision_cannot_produce_another_broker_request() (+10 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.12
Nodes (10): ExperimentStatus, BitsStore, Uses the same connection selected for the application's transcript store., canonical_json(), ExperimentRegistry, Any, datetime, Recover claims left by a previous instance of the single system worker. (+2 more)

### Community 6 - "test_demo_runner.py"
Cohesion: 0.17
Nodes (11): Adapter, DecisionSource, MarketSource, paper_only_runner(), runner(), test_cycle_failure_stops_after_configured_consecutive_failures(), test_disabled_config_does_not_reconcile_or_start(), test_paper_only_start_skips_broker_reconciliation_and_runs_cycle() (+3 more)

### Community 7 - "firecrawl_research.py"
Cohesion: 0.15
Nodes (18): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+10 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "ml_models.py"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.13
Nodes (20): adapter(), FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation() (+12 more)

### Community 11 - "RemoteComputeBridge"
Cohesion: 0.16
Nodes (17): setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock(), test_readiness_uses_most_constrained_mount() (+9 more)

### Community 12 - "pandas"
Cohesion: 0.14
Nodes (22): numpy, pandas, Secret-free deterministic parity fixture for the runtime container., test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_chronological_splits_are_ordered_and_disjoint(), test_parameter_neighbors_change_one_value() (+14 more)

### Community 13 - "synthetic_bars"
Cohesion: 0.13
Nodes (25): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+17 more)

### Community 14 - "self_improve.py"
Cohesion: 0.12
Nodes (22): base64, CompletedProcess, sys, tempfile, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple() (+14 more)

### Community 15 - "test_weekly_report.py"
Cohesion: 0.17
Nodes (19): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+11 more)

### Community 16 - "ExecutionConfig"
Cohesion: 0.14
Nodes (27): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, sklearn_metrics, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future() (+19 more)

### Community 17 - "Any"
Cohesion: 0.18
Nodes (8): CTraderDemoOpenApiTransport, failed(), issue(), succeeded(), Any, Synchronous, bounded cTrader demo transport. Construction and import are inert.…, Read-only broker volume/price metadata for the resolved demo symbol., Return ``(code, description)`` for a cTrader error message, else None.

### Community 18 - "test_agent_loop.py"
Cohesion: 0.12
Nodes (35): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), refresh_config(), refresh_runner(), ScriptedPlanner (+27 more)

### Community 19 - "paper_trading.py"
Cohesion: 0.11
Nodes (12): CockroachPaperTradingStore, _default_state(), _now(), PaperDecision, transition(), PaperTradingStore, Any, datetime (+4 more)

### Community 20 - "OpenAICompatiblePlanner"
Cohesion: 0.27
Nodes (6): 3. Where the planner is wired today (confirmed), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), OpenAICompatiblePlanner, Any, Return the model's raw response content and the parsed allow-listed action. Raw…

### Community 21 - "test_agent_view.py"
Cohesion: 0.07
Nodes (31): FastAPI, fastapi_responses, pytest, test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), paper_trading(), fixture (+23 more)

### Community 22 - "TournamentDataset"
Cohesion: 0.35
Nodes (4): frame_digest(), DataFrame, Hash canonical timestamps, schema, and values independent of Parquet bytes., TournamentDataset

### Community 23 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "cli.py"
Cohesion: 0.24
Nodes (18): collections, dataclasses, datetime, hashlib, json, logging, math, os (+10 more)

### Community 26 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.18
Nodes (20): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+12 more)

### Community 27 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 28 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 29 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.11
Nodes (17): test_volume_policy_from_metadata(), _paper_to_demo_coordinator(), CTraderVolumeConversion, CTraderVolumePolicy, DemoExecutor, PaperToCTraderDemoCoordinator, Any, datetime (+9 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.06
Nodes (41): Configuration, Datadog Bits connection, Verified transport and remaining integration, PathLike, Architecture, Autonomous Agent, Configuration, Current Status (+33 more)

### Community 31 - "CockroachCTraderDemoStore"
Cohesion: 0.16
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 32 - "ExperimentSpec"
Cohesion: 0.21
Nodes (16): E. Current 50,000-scenario architecture and benchmark, dotenv, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix() (+8 more)

### Community 33 - "test_local_state.py"
Cohesion: 0.20
Nodes (16): decision(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store(), test_sqlite_integrity_check_detects_corruption(), test_sqlite_paper_store_corrupt_state_fails_closed(), test_sqlite_paper_store_integrity_check_reports_ok(), test_sqlite_paper_store_kill_switch_persists_and_fails_closed(), test_sqlite_paper_store_persists_state_and_decision_idempotency() (+8 more)

### Community 34 - "memory_registry.py"
Cohesion: 0.18
Nodes (3): copy, MemoryConnection, MemoryCursor

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.14
Nodes (13): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 7.1 Code — one relaxation (small, tested) (+5 more)

### Community 37 - "InMemoryAgentTranscriptStore"
Cohesion: 0.13
Nodes (4): CockroachAgentTranscriptStore, InMemoryAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Test double only; production state lives in the configured backend store.

### Community 39 - "core.py"
Cohesion: 0.27
Nodes (8): test_backtest(), campaign(), event_backtest(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 40 - "test_tournament_runner.py"
Cohesion: 0.15
Nodes (10): Dependence-aware bootstrap validation — 2026-08-21, setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition() (+2 more)

### Community 41 - ".run"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

### Community 42 - "test_ctrader_auth.py"
Cohesion: 0.16
Nodes (19): account(), test_demo_accounts_empty_when_all_live(), test_demo_accounts_filters_live_and_missing_flag(), test_is_error_extracts_code_and_description(), test_is_error_none_when_clear(), test_resolve_symbol_falls_back_to_first_match(), test_resolve_symbol_prefers_enabled_match(), test_resolve_symbol_rejects_invalid_id() (+11 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 49 - "BitsError"
Cohesion: 0.07
Nodes (38): contextlib, re, selectors, signal, envelope(), action(), jobs(), fixture (+30 more)

### Community 50 - "SQLiteAgentTranscriptStore"
Cohesion: 0.14
Nodes (10): Connection, Row, _connect(), _now(), Any, datetime, Minimal local SQLite state stores for paper trading and the agent transcript.…, Local SQLite replacement for the CockroachDB agent transcript store. (+2 more)

### Community 51 - "agent_controller"
Cohesion: 0.13
Nodes (18): test_agent_transcript_backend_selection_defaults_to_local(), agent_transcript_store_from_env(), _positive_float(), Transcript store for the configured backend (local SQLite by default)., LocalHistoricalMarketDataSource, Expose the final persisted, normalized M1 bar as a market observation., agent_controller(), _agent_data_refresh_source() (+10 more)

### Community 52 - "automation.py"
Cohesion: 0.12
Nodes (23): test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_html_report_contains_candidates(), test_registry_only_promotes_passing_better_candidate(), test_run_lock_rejects_overlap(), test_weekly_comparison_collects_archived_runs(), traceback, append_jsonl() (+15 more)

### Community 53 - "portfolio_research.py"
Cohesion: 0.19
Nodes (20): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal() (+12 more)

### Community 54 - "CTraderAuthError"
Cohesion: 0.14
Nodes (19): test_data_update_does_not_retry_auth_errors(), download(), test_data_update_retries_transient_failures(), downloader_config(), minute_60(), one_bar_at(), test_download_does_not_retry_non_token_auth_error(), fake_fetch() (+11 more)

### Community 55 - "agent_loop.py"
Cohesion: 0.17
Nodes (20): threading, build_agent_registry(), canary_signal_tool(), handler(), _decision_id(), _mock_market_for_read(), paper_state_tool(), propose_trade_tool() (+12 more)

### Community 56 - "TournamentRunner"
Cohesion: 0.26
Nodes (4): _finite(), Path, Consume deterministic experiments without reading the holdout test set., TournamentRunner

### Community 57 - "test_state_backup.py"
Cohesion: 0.19
Nodes (20): sqlite3, decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+12 more)

### Community 58 - "CTraderDemoStore"
Cohesion: 0.15
Nodes (3): CTraderDemoStore, CTraderTransport, Protocol

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.11
Nodes (15): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, Protocol, Display-friendly assistant step: parsed action plus the model's plain-English… (+7 more)

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

### Community 64 - "Repository Operating Rules"
Cohesion: 0.20
Nodes (8): Autonomous Harness, Engineering, Execution Boundary, graphify, Operations, Purpose, Repository Operating Rules, Auto-resume on a benign restart; fail closed on persisted trouble. A paper…

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

### Community 71 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 72 - "DemoAutomationRunner"
Cohesion: 0.30
Nodes (4): DemoAutomationRunner, Any, Poll injected sources only after explicit enablement and reconciliation., Reconcile first, then make the explicitly enabled paper/demo pair runnable.

### Community 73 - "ctrader_demo.py"
Cohesion: 0.11
Nodes (16): test_symbol_metadata_and_volume_policy_validate_invariants(), build_new_order_request(), build_reconcile_request(), CTraderDemoAdapter, CTraderDemoSafetyError, CTraderSymbolMetadata, RuntimeError, Fail-closed cTrader Open API execution boundary for verified demo accounts. (+8 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 77 - "autonomous_harness.py"
Cohesion: 0.23
Nodes (11): concurrent_futures, 6. Safety and repository-rule compliance (unchanged), 8. Prototype gate and test plan (execute BEFORE any cutover), ValueError, _check_reason(), parse_action(), PlannerResponseError, Research-only autonomous harness primitives; this module has no broker or web… (+3 more)

### Community 78 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 79 - "EventDrivenBacktester"
Cohesion: 0.35
Nodes (11): main(), bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path(), test_compact_attribution_metrics_reconcile_and_measure_concentration(), test_signal_executes_at_next_open_without_lookahead(), test_spread_slippage_and_commission_are_charged_both_sides(), test_stop_wins_ambiguous_intrabar_path() (+3 more)

### Community 80 - "test_data.py"
Cohesion: 0.30
Nodes (9): demo_env(), test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag(), test_trendbar_delta_decoding(), CTraderOpenApiConfig, Any, Decode cTrader's low-plus-delta trendbar representation. (+1 more)

### Community 81 - "HistoricalDataStore"
Cohesion: 0.31
Nodes (5): test_store_rejects_invalid_ohlc(), test_store_roundtrip(), HistoricalDataStore, DataFrame, Local OHLCV store. The adapter accepts historical exports only; no execution…

### Community 82 - "CTraderOpenApiDownloader"
Cohesion: 0.29
Nodes (4): Timestamp, CTraderOpenApiDownloader, datetime, Read-only cTrader Open API client for symbols and historical trendbars.

### Community 84 - "test_bits_runner.py"
Cohesion: 0.33
Nodes (5): Planner, runner(), test_complete_action_feedback_cycle(), test_market_closed_and_stopped_never_submit(), test_pending_workflow_survives_restart()

### Community 87 - "DemoRunnerConfig"
Cohesion: 0.33
Nodes (6): test_environment_config_is_disabled_unless_explicitly_true(), demo_automation(), _demo_automation_status(), Run the explicitly enabled local-data paper-to-demo canary., DemoRunnerConfig, datetime

### Community 88 - "test_tournament_data.py"
Cohesion: 0.36
Nodes (6): dataset(), test_content_change_creates_new_version(), test_frozen_dataset_is_reproducible_and_partitioned(), test_partitions_read_exact_manifest_counts(), test_tampering_is_detected(), TournamentDataConfig

### Community 89 - "DemoLifecycle"
Cohesion: 0.22
Nodes (4): DemoLifecycle, MarketDataSource, Protocol, Read-only source for the latest executable market observation.

### Community 91 - "failure_code"
Cohesion: 0.29
Nodes (4): P0/P1 implementation updates — 2026-08-20, Exception, test_remote_failure_codes_are_structured(), failure_code()

## Knowledge Gaps
- **113 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+108 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 513 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExperimentRegistry` connect `ExperimentRegistry` to `ExperimentSpec`, `main`, `dashboard.py`, `TournamentRunner`, `MemoryRegistry`, `test_tournament_runner.py`, `RemoteComputeBridge`, `AdaptiveSearch`, `synthetic_bars`, `test_weekly_report.py`, `portfolio_research.py`, `TournamentDataset`, `ShadowTradingReadiness`, `XAUUSD discovery, incident, quantitative, and scaling audit`, `cli.py`, `_atomic_json`, `CodexImprovementWorkflow`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `XAUUSD discovery, incident, quantitative, and scaling audit` connect `XAUUSD discovery, incident, quantitative, and scaling audit` to `ExperimentSpec`, `test_tournament_runner.py`, `AdaptiveSearch`, `test_weekly_report.py`, `ExecutionConfig`, `portfolio_research.py`, `failure_code`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `Repository Operating Rules`, `test_local_state.py`, `main`, `test_demo_execution.py`, `test_demo_runner.py`, `test_agent_loop.py`, `agent_controller`, `test_bits_runner.py`, `test_agent_view.py`, `paper_trading.py`, `agent_loop.py`, `test_state_backup.py`, `ContinuousAgentRunner`, `PaperToCTraderDemoCoordinator`, `cli.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `build_agent_registry()`) actually correct?**
  _`PaperTrading` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `xauusd-research` to the rest of the system?**
  _113 weakly-connected nodes found - possible documentation gaps or missing edges._