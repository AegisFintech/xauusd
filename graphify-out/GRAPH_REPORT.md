# Graph Report - xauusd  (2026-09-18)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1308 nodes · 3818 edges · 49 communities (41 shown, 8 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 168 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `14b9a9cf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48

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
- `test_result_root_is_not_created_per_scenario()` --uses--> `RemoteComputeBridge`  [INFERRED]
  tests/test_distributed_compute.py → xauusd/distributed_compute.py
- `test_store_rejects_invalid_ohlc()` --calls--> `HistoricalDataStore`  [EXTRACTED]
  tests/test_data.py → xauusd/data.py
- `test_store_roundtrip()` --calls--> `HistoricalDataStore`  [EXTRACTED]
  tests/test_data.py → xauusd/data.py
- `MarketSource` --uses--> `MarketData`  [INFERRED]
  tests/test_demo_runner.py → xauusd/demo_runner.py
- `test_host_and_environment_rejections_are_fail_closed()` --uses--> `CTraderDemoSafetyError`  [INFERRED]
  tests/test_ctrader_demo.py → xauusd/ctrader_demo.py

## Import Cycles
- None detected.

## Communities (49 total, 8 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (40): FastAPI, fastapi_responses, fixture, paper_trading(), server(), test_paper_endpoint_reflects_accepted_fill(), decision(), test_corrupt_memory_state_fails_closed() (+32 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (36): concurrent_futures, re, planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts() (+28 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (42): dotenv, gzip, psycopg, random, main(), sys, test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_paper_only_skips_broker_dependencies() (+34 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (61): asyncio, fastapi_security, fastapi_testclient, get, HTTPBasicCredentials, middleware, plotly_graph_objects, Request (+53 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (41): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches(), test_duplicate_decision_cannot_produce_another_broker_request() (+33 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (21): ExperimentStatus, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates(), test_semantic_identity_ignores_provenance() (+13 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (25): Adapter, DecisionSource, MarketSource, paper_only_runner(), runner(), test_cycle_failure_stops_after_configured_consecutive_failures(), test_disabled_config_does_not_reconcile_or_start(), test_environment_config_is_disabled_unless_explicitly_true() (+17 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (22): parametrize, test_postgres_connection_uses_configured_read_committed(), client(), test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit() (+14 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (26): pytest, test_store_rejects_invalid_ohlc(), test_store_roundtrip(), test_trendbar_delta_decoding(), Timestamp, types, CTraderHistoricalAdapter, CTraderOpenApiDownloader (+18 more)

### Community 10 - "Community 10"
Cohesion: 0.10
Nodes (23): adapter(), FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation() (+15 more)

### Community 11 - "Community 11"
Cohesion: 0.10
Nodes (20): Exception, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+12 more)

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (25): main(), bars(), no_costs(), test_array_loop_is_deterministic_on_randomized_path(), test_compact_attribution_metrics_reconcile_and_measure_concentration(), test_signal_executes_at_next_open_without_lookahead(), test_spread_slippage_and_commission_are_charged_both_sides(), test_stop_wins_ambiguous_intrabar_path() (+17 more)

### Community 13 - "Community 13"
Cohesion: 0.14
Nodes (25): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error(), test_novel_formulas_generate_valid_signals() (+17 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 15 - "Community 15"
Cohesion: 0.23
Nodes (19): base64, collections, dataclasses, datetime, hashlib, json, logging, math (+11 more)

### Community 16 - "Community 16"
Cohesion: 0.13
Nodes (24): HistGradientBoostingClassifier, ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined(), ml_research() (+16 more)

### Community 17 - "Community 17"
Cohesion: 0.18
Nodes (8): CTraderDemoOpenApiTransport, failed(), issue(), succeeded(), Any, Synchronous, bounded cTrader demo transport. Construction and import are inert.…, Read-only broker volume/price metadata for the resolved demo symbol., Return ``(code, description)`` for a cTrader error message, else None.

### Community 18 - "Community 18"
Cohesion: 0.17
Nodes (24): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), ScriptedPlanner, test_assistant_steps_carry_parsed_action_and_human_reason(), test_assistant_steps_without_reason_remain_well_formed() (+16 more)

### Community 19 - "Community 19"
Cohesion: 0.17
Nodes (18): numpy, pandas, sklearn_metrics, Secret-free deterministic parity fixture for the runtime container., test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_parameter_neighbors_change_one_value() (+10 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (18): test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_html_report_contains_candidates(), test_registry_only_promotes_passing_better_candidate(), test_run_lock_rejects_overlap(), test_weekly_comparison_collects_archived_runs(), traceback, append_jsonl() (+10 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (11): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), test_continuous_worker_records_idle_heartbeat(), CodexImprovementWorkflow, CodexWorkflowConfig (+3 more)

### Community 22 - "Community 22"
Cohesion: 0.18
Nodes (21): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), read(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal() (+13 more)

### Community 23 - "Community 23"
Cohesion: 0.14
Nodes (13): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), test_adaptive_generations_wait_for_completion_interval() (+5 more)

### Community 24 - "Community 24"
Cohesion: 0.12
Nodes (11): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, Protocol, Display-friendly assistant step: parsed action plus the model's plain-English… (+3 more)

### Community 25 - "Community 25"
Cohesion: 0.18
Nodes (18): itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors(), test_selection_bias_computes_bh_and_aligned_fold_pbo() (+10 more)

### Community 26 - "Community 26"
Cohesion: 0.15
Nodes (16): store_with_bars(), test_canary_ignores_neutral_and_persistent_signals(), test_canary_transition_has_stable_identity_and_side(), test_local_historical_market_source_reads_final_close_and_utc_time(), handler(), _mock_market_for_read(), ConfirmedBreakoutCanarySource, LocalHistoricalMarketDataSource (+8 more)

### Community 27 - "Community 27"
Cohesion: 0.20
Nodes (10): dataset(), test_content_change_creates_new_version(), test_frozen_dataset_is_reproducible_and_partitioned(), test_partitions_read_exact_manifest_counts(), test_tampering_is_detected(), frame_digest(), DataFrame, Hash canonical timestamps, schema, and values independent of Parquet bytes. (+2 more)

### Community 28 - "Community 28"
Cohesion: 0.21
Nodes (6): _atomic_json(), compute_job(), _finite(), Path, Consume deterministic experiments without reading the holdout test set., TournamentRunner

### Community 29 - "Community 29"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 30 - "Community 30"
Cohesion: 0.17
Nodes (11): build_new_order_request(), build_reconcile_request(), CTraderDemoSafetyError, RuntimeError, Fail-closed cTrader Open API execution boundary for verified demo accounts., A configuration, recovery, or execution condition that must fail closed., Verify broker account identity before an operator may start execution., Construct the actual Open API market-order protobuf without opening a… (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.41
Nodes (4): _canonical_json(), CockroachCTraderDemoStore, _now(), Authoritative persistent execution state, idempotency, and audit store.

### Community 32 - "Community 32"
Cohesion: 0.18
Nodes (3): _initial_state(), InMemoryCTraderDemoStore, Test double only; production execution state belongs in CockroachDB.

### Community 33 - "Community 33"
Cohesion: 0.15
Nodes (3): CTraderDemoStore, CTraderTransport, Protocol

### Community 34 - "Community 34"
Cohesion: 0.18
Nodes (3): copy, MemoryConnection, MemoryCursor

### Community 35 - "Community 35"
Cohesion: 0.20
Nodes (8): test_demo_automation_requires_explicit_positive_volume(), _positive_float(), agent_controller(), _agent_status_view(), _demo_automation_runner(), _paper_from_env(), _positive_env_float(), Single continuously trading AI agent with a visible thinking process.

### Community 36 - "Community 36"
Cohesion: 0.31
Nodes (7): test_backtest(), campaign(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 39 - "Community 39"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 40 - "Community 40"
Cohesion: 0.46
Nodes (6): setup_runner(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition(), TournamentGates

### Community 41 - "Community 41"
Cohesion: 0.39
Nodes (6): close(), commission(), fill_price(), DataFrame, Series, Trade

### Community 42 - "Community 42"
Cohesion: 0.40
Nodes (5): threading, _decision_id(), handler(), datetime, Continuous single-agent XAUUSD paper trading loop with a live, visible thinking…

## Knowledge Gaps
- **3 isolated node(s):** `research-cron.sh script`, `start.sh script`, `xauusd-research`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 309 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExperimentRegistry` connect `Community 5` to `Community 2`, `Community 3`, `Community 8`, `Community 40`, `Community 11`, `Community 13`, `Community 15`, `Community 21`, `Community 22`, `Community 23`, `Community 25`, `Community 28`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `OperationsManager` connect `Community 2` to `Community 3`, `Community 5`, `Community 15`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `MemoryRegistry` connect `Community 8` to `Community 34`, `Community 3`, `Community 2`, `Community 5`, `Community 40`, `Community 11`, `Community 13`, `Community 21`, `Community 23`, `Community 25`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `ExperimentRegistry` (e.g. with `AdaptiveSearch` and `CodexImprovementWorkflow`) actually correct?**
  _`ExperimentRegistry` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `build_agent_registry()`) actually correct?**
  _`PaperTrading` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `RemoteComputeBridge` (e.g. with `test_result_root_is_not_created_per_scenario()` and `tournament_equity()`) actually correct?**
  _`RemoteComputeBridge` has 9 INFERRED edges - model-reasoned connections that need verification._