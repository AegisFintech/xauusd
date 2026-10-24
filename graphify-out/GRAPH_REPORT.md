# Graph Report - xauusd-cleanup-release  (2026-10-24)

## Corpus Check
- 192 files · ~193,149 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .service 8, (none) 7, .timer 2)

## Summary
- 3688 nodes · 10267 edges · 158 communities (135 shown, 23 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 539 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f431a68c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_ctrader_auth.py
- test_autonomous_harness.py
- OperationsManager
- dashboard.py
- test_bits_runner.py
- ExperimentRegistry
- Any
- ConfirmedBreakoutCanarySource
- MemoryRegistry
- ml_models.py
- test_ctrader_demo.py
- ml_campaign.py
- json
- PaperTrading
- self_improve.py
- bits_memory.py
- SQLiteAgentTranscriptStore
- CTraderDemoOpenApiTransport
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- test_validation.py
- BitsStore
- XAUUSD discovery, incident, quantitative, and scaling audit
- run
- CTraderAuthError
- OpenAICompatiblePlanner
- SQLitePaperTradingStore
- test_demo_execution.py
- test_oauth.py
- test_tournament_runner.py
- test_search_space.py
- test_lab.py
- test_dashboard.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- synthetic_bars
- ShadowTradingReadiness
- build_features
- Operator runbook: engine, live feed, and the visible harness
- .__init__
- ._fetch
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- test_retention.py
- test_demo_runner.py
- InMemoryAgentTranscriptStore
- test_automation.py
- test_ctrader_reconciliation.py
- PaperDecision
- CockroachAgentTranscriptStore
- restart_policy
- step_display
- ExecutionConfig
- ContinuousAgentRunner
- Requirements: reliable research-to-paper-trade workflow
- verify_result_parity.py
- EngineConfig
- CTraderOAuthError
- CTraderDemoAdapter
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- test_cftc_research.py
- bits_runner.py
- test_session_calendar.py
- Architecture and data-flow map
- test_data.py
- opencode.json
- oauth.py
- BitsMemory
- canonical_json
- CodexImprovementWorkflow
- test_engine_loop.py
- test_bits_capabilities.py
- AgentTools
- memory_registry.py
- _feed
- test_cli.py
- .write_notes
- agent_advisor.py
- PaperTradingEngine
- .persist_bar
- cli.py
- test_live_feed.py
- TournamentDataset
- PostgresConnection
- Store
- test_bits_research.py
- ._note
- test_local_state.py
- LiveFeedConfig
- test_bits_memory_drafts.py
- .run
- lab_strategy.py
- core.py
- test_weekly_report.py
- HarnessStore
- DataConfig
- atomic_write_json
- attach_routes
- LabStore
- BitsError
- AgentTranscriptStore
- ._discover_account
- promote_tools
- agent_tools.py
- RecordingPostgres
- NormalizedDecision
- write_status
- read_quote
- portfolio_research.py
- .send
- pytest
- test_lab_dashboard.py
- test_strategy_proposals.py
- evidence_refs
- Delivery Stages
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- PaperToCTraderDemoCoordinator
- types
- Persistent open-ended Codex agent
- _MainContent
- test_offline.py
- Codex autonomous trading lab
- Datadog Bits connection
- README.md
- Planner
- Merge review — 2026-09-25, baseline `cba22b2`
- FakeResponse
- test_agent_config_rejects_non_finite_limits
- test_health_reports_degraded_when_the_state_store_is_unavailable
- test_engine_decision_id_is_derived_from_the_bar
- StateTransaction
- harness-outcomes-plan-2026-10-23.md
- demo_feed_environment
- _datetime
- .from_env
- test_lab_statistics.py
- CockroachHarnessStore
- HistoricalDataStore
- create_app
- ToolRegistry
- sklearn_base
- tarfile

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `MemoryRegistry` - 89 edges
3. `HistoricalDataStore` - 80 edges
4. `ExperimentRegistry` - 76 edges
5. `SQLiteAgentTranscriptStore` - 73 edges
6. `main()` - 71 edges
7. `_datetime()` - 67 edges
8. `BitsStore` - 66 edges
9. `InMemoryPaperTradingStore` - 65 edges
10. `canonical_json()` - 59 edges

## Surprising Connections (you probably didn't know these)
- `Persistent Codex and experimental paper accounts (2026-10-22)` --references--> `rebase()`  [INFERRED]
  docs/operator-runbook-agent.md → xauusd/account_rebase.py
- `12. Status of evidence` --references--> `OpenAICompatiblePlanner`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → xauusd/autonomous_harness.py
- `Original incident evidence (pre-merge snapshot)` --references--> `BitsError`  [INFERRED]
  requirements.md → xauusd/bits.py
- `R3 — P1: make experiment continuity work with the deployed backend` --references--> `ExperimentRegistry`  [INFERRED]
  requirements.md → xauusd/experiment_registry.py
- `Research continuity and output retrieval` --references--> `weekly_bars()`  [INFERRED]
  docs/legacy-project-history.md → xauusd/session_calendar.py

## Import Cycles
- None detected.

## Communities (158 total, 23 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.07
Nodes (37): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC (+29 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.21
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "OperationsManager"
Cohesion: 0.08
Nodes (22): Automatic immutable scaling checkpoints — 2026-08-21, Scaling checkpoint and operational projection — 2026-08-21, test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs() (+14 more)

### Community 3 - "dashboard.py"
Cohesion: 0.08
Nodes (55): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), plotly_graph_objects (+47 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.10
Nodes (29): _looping_agent(), A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted., `monitor_error` used to be assigned and then read by nothing at all., An agent whose store already shows one file re-read for a whole window., The evidence reached the model's prompt and never reached the operator. On… (+21 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.11
Nodes (7): ExperimentStatus, Read-modify-write several state keys atomically. SQLite connections run in…, ExperimentRegistry, Any, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool., Path

### Community 6 - "Any"
Cohesion: 0.11
Nodes (9): _canonical_json(), CockroachCTraderDemoStore, CTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Any, Test double only; production execution state belongs in CockroachDB. (+1 more)

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.16
Nodes (21): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+13 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "ml_models.py"
Cohesion: 0.09
Nodes (20): ImportError, importlib, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample(), test_core_model_adapters_and_ensemble_probabilities() (+12 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.08
Nodes (42): adapter(), FakeClient, ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call() (+34 more)

### Community 11 - "ml_campaign.py"
Cohesion: 0.13
Nodes (25): HistGradientBoostingClassifier, ndarray, sklearn_metrics, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined() (+17 more)

### Community 12 - "json"
Cohesion: 0.10
Nodes (46): base64, collections, concurrent_futures, csv, dataclasses, datetime, gzip, hashlib (+38 more)

### Community 13 - "PaperTrading"
Cohesion: 0.07
Nodes (61): paper_trading(), The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., The monitor's status string alone was never enough. A monitor that died after…, test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_alerts_on_a_stale_or_dead_position_monitor(), test_health_names_the_paths_a_retrieval_loop_keeps_reading(), test_health_stays_quiet_when_no_path_repeats() (+53 more)

### Community 14 - "self_improve.py"
Cohesion: 0.14
Nodes (19): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+11 more)

### Community 15 - "bits_memory.py"
Cohesion: 0.16
Nodes (18): _age_seconds(), _check_categories(), _check_draft_ids(), _check_entry(), check_notes(), _is_current_notes(), issue(), _key_path() (+10 more)

### Community 16 - "SQLiteAgentTranscriptStore"
Cohesion: 0.14
Nodes (11): Connection, Row, test_bits_notes_only_does_not_repeat_history(), _connect(), _now(), Any, Local SQLite replacement for the CockroachDB agent transcript store., Bound transcript growth. Nothing else ever deleted from this table. The… (+3 more)

### Community 17 - "CTraderDemoOpenApiTransport"
Cohesion: 0.13
Nodes (15): request(), CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded() (+7 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.10
Nodes (44): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), A ticking agent must not be served as stopped. The engine's startup reconcile…, refresh_config(), refresh_runner() (+36 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.14
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (23): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+15 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.09
Nodes (15): _harness_client(), The deterministic engine writes to the same `agent_runs` table. Taking the…, `limit` alone does not bound a response. A shell-job step carries a captured…, A non-SQLite transcript store must not take the panel down., test_age_seconds_parses_timezone_aware_timestamps(), test_harness_endpoint_degrades_without_a_sqlite_store(), test_harness_page_renders_and_is_read_only(), test_harness_page_subscribes_to_the_event_stream() (+7 more)

### Community 22 - "test_validation.py"
Cohesion: 0.13
Nodes (22): An empty training window must fail loudly, not look like a negative result., A 30-bar rolling feature reaches across the split boundary. The last…, test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_chronological_splits_are_ordered_and_disjoint(), test_parameter_neighbors_change_one_value(), test_validator_embargo_purges_the_training_tail() (+14 more)

### Community 23 - "BitsStore"
Cohesion: 0.07
Nodes (40): selectors, action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes…, A failed preview is observability, and observability must not break the job. (+32 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (45): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20, Complete auxiliary backup integrity — 2026-08-21 (+37 more)

### Community 26 - "CTraderAuthError"
Cohesion: 0.11
Nodes (24): test_data_update_does_not_retry_auth_errors(), unauthorized(), demo_env(), downloader_config(), validate() is no longer a one-time check performed only by from_env(). The…, test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag() (+16 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.33
Nodes (9): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError, Any, ValueError (+1 more)

### Community 28 - "SQLitePaperTradingStore"
Cohesion: 0.13
Nodes (30): sqlite3, seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source() (+22 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.11
Nodes (25): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+17 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.13
Nodes (22): PathLike, Market Data & Authentication, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent…, Smoke test: concurrent writers never produce an unparseable env file. (+14 more)

### Community 31 - "test_tournament_runner.py"
Cohesion: 0.12
Nodes (12): Dependence-aware bootstrap validation — 2026-08-21, test_dataset_manifest_records_the_derived_versions(), setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap() (+4 more)

### Community 32 - "test_search_space.py"
Cohesion: 0.25
Nodes (15): E. Current 50,000-scenario architecture and benchmark, dotenv, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix() (+7 more)

### Community 33 - "test_lab.py"
Cohesion: 0.08
Nodes (44): test_account_only_reset_preserves_research_and_stop(), test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), test_improvement_cannot_claim_old_release_as_new_work(), test_inspection_and_failed_remote_work_are_not_progress(), test_outcome_requires_existing_successful_evidence_and_deduplicates(), test_reconciliation_and_evidence_remain_available_at_unresolved_limit(), parametrize (+36 more)

### Community 34 - "test_dashboard.py"
Cohesion: 0.23
Nodes (8): setup_files(), test_dashboard_reads_latest_run_and_equity(), test_dashboard_registry_requires_database_url_and_never_passes_a_path(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature(), test_status_remains_readable_without_generated_tournament_dataset(), test_tournament_equity_and_leaderboard()

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.15
Nodes (11): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+3 more)

### Community 37 - "synthetic_bars"
Cohesion: 0.11
Nodes (28): dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version…, A freeze killed mid-write must not hang the next one, nor quietly pass., A backtester or cost change must invalidate stored results. Both were hardcoded…, test_a_version_directory_with_no_manifest_fails_loudly() (+20 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 39 - "build_features"
Cohesion: 0.12
Nodes (21): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+13 more)

### Community 40 - "Operator runbook: engine, live feed, and the visible harness"
Cohesion: 0.13
Nodes (12): Operations, 10. Related documents, 1. What was built and why, 4. Enable the deterministic engine, 5. Restart the live view so the new observability is visible, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback (+4 more)

### Community 41 - ".__init__"
Cohesion: 0.15
Nodes (5): EngineStore, MarketSource, Protocol, The narrow slice of the durable store the engine needs., TranscriptSink

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 49 - "test_retention.py"
Cohesion: 0.08
Nodes (52): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(), archive(), _local_backups() (+44 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.06
Nodes (33): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+25 more)

### Community 51 - "InMemoryAgentTranscriptStore"
Cohesion: 0.10
Nodes (9): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), test_runner_records_failed_refresh_and_gates_planner(), test_base_runner_records_codes_for_planner_and_tick_errors(), boom(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store., Mirror of the SQLite retention so both backends behave the same. (+1 more)

### Community 52 - "test_automation.py"
Cohesion: 0.08
Nodes (31): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+23 more)

### Community 53 - "test_ctrader_reconciliation.py"
Cohesion: 0.23
Nodes (12): parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening(), test_persistent_store_keeps_unknown_pending_and_preserves_fill_mapping() (+4 more)

### Community 54 - "PaperDecision"
Cohesion: 0.11
Nodes (11): CockroachPaperTradingStore, _now(), PaperDecision, transition(), transition(), PaperTradingStore, Any, Protocol (+3 more)

### Community 55 - "CockroachAgentTranscriptStore"
Cohesion: 0.19
Nodes (4): CockroachAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row; see the SQLite store.

### Community 56 - "restart_policy"
Cohesion: 0.13
Nodes (15): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+7 more)

### Community 57 - "step_display"
Cohesion: 0.12
Nodes (18): test_bits_decisions_show_summary_instead_of_protocol_json(), test_shell_command_and_output_are_not_in_collapsed_text(), harness(), steps(), stream(), events(), _engine_display_text(), _feed_alerts() (+10 more)

### Community 58 - "ExecutionConfig"
Cohesion: 0.11
Nodes (34): main(), bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,…, Zero is a real value; a metric that cannot be computed must say so. Reporting… (+26 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.16
Nodes (13): Event, test_redact_bounds_untrusted_content(), _assistant_step(), ContinuousAgentRunner, Any, BaseException, Display-friendly assistant step: parsed action plus the model's plain-English…, Transcript-friendly view: keep structures, bound untrusted string lengths. (+5 more)

### Community 60 - "Requirements: reliable research-to-paper-trade workflow"
Cohesion: 0.18
Nodes (10): Delivery and operational boundaries, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit, P1 — Persist reproducible experiments and separate live signals, P1 — Separate monitoring cadence from meaningful agent reviews (+2 more)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.39
Nodes (6): compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "EngineConfig"
Cohesion: 0.20
Nodes (7): test_engine_config_rejects_unbounded_values(), test_engine_status_reports_the_running_process_not_a_phantom(), engine_controller(), Operator and supervisor control for the deterministic trade engine., EngineConfig, _float_env(), Engine pacing and sizing. Every field is bounded and validated.

### Community 63 - "CTraderOAuthError"
Cohesion: 0.20
Nodes (14): response_json(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises(), test_refresh_access_token_returns_pair_with_browser_agent(), fake_urlopen(), test_rejected_grant_raises_oauth_error() (+6 more)

### Community 64 - "CTraderDemoAdapter"
Cohesion: 0.13
Nodes (10): build_reconcile_request(), CTraderDemoAdapter, CTraderTransport, Protocol, Executes only persisted, reconciled XAUUSD demo-order proposals., Persisted execution kill switch, consulted by the shared restart policy., Verify broker account identity before an operator may start execution., Persist a minimal non-secret receipt, not arbitrary transport objects. (+2 more)

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

### Community 71 - "test_cftc_research.py"
Cohesion: 0.08
Nodes (61): date, pandas_tseries_holiday, _cot_csv(), _prereg(), The preregistered CFTC study: point-in-time discipline, session weeks, fail-…, 15:30 New York is 20:30 UTC in winter and 19:30 UTC under daylight time. The…, The fail-closed check the artifact claims, verified instead of asserted. Taking…, Excluding 2023 and 2025 wholesale means some flows span a gap; report how many.… (+53 more)

### Community 72 - "bits_runner.py"
Cohesion: 0.09
Nodes (21): error_details(), AgentLock, Single process per container; the lock is runtime coordination, not state., excerpt(), result_for_prompt(), message_fingerprint(), BaseException, Payload-free classification of an exception for events and heartbeats.… (+13 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.16
Nodes (20): at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from…, Synthetic M1 bars stamped at bar open, only while the session gate is open., session_bars(), test_a_week_whose_data_stops_early_is_not_complete(), test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected(), test_pandas_weekly_labels_disagree_with_session_weeks() (+12 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.06
Nodes (59): ArgumentParser, errno, Without this the command exists but nothing runs it, so a hole still sits for…, test_the_heal_command_is_in_the_cli_grammar(), test_update_can_heal_and_the_timer_does(), _bars(), frame(), minute_60() (+51 more)

### Community 77 - "oauth.py"
Cohesion: 0.18
Nodes (13): contextlib, fcntl, urllib_error, _env_key(), _env_lock(), guard(), _env_value(), Path (+5 more)

### Community 78 - "BitsMemory"
Cohesion: 0.35
Nodes (4): BitsMemory, _note_sources(), _notes_base(), A specific next task for unresolved drafts; not a new research cycle.

### Community 79 - "canonical_json"
Cohesion: 0.17
Nodes (24): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection(), reply(), sample_notes() (+16 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.09
Nodes (37): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., An oversized proposal must be visibly refused, not silently trimmed. Clamping…, Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case. (+29 more)

### Community 82 - "test_bits_capabilities.py"
Cohesion: 0.06
Nodes (72): Datadog Bits operations, platform, R2 — P1: capability discovery failure must remain visible, shlex, fake_tool(), parametrize, The shell-job environment is discoverable from the environment jobs really get., Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI… (+64 more)

### Community 83 - "AgentTools"
Cohesion: 0.05
Nodes (44): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000) (+36 more)

### Community 84 - "memory_registry.py"
Cohesion: 0.18
Nodes (3): copy, MemoryConnection, MemoryCursor

### Community 86 - "_feed"
Cohesion: 0.15
Nodes (13): _feed(), parametrize, The exact 2026-10-08 outage: bar_write_failed, session open, no alert. The…, A feed that is alive and healthy but no longer persisting bars., No bars over a weekend is idle, not broken; alerting on it trains operators to…, A dead feed keeps reporting its last known state as healthy forever., The resubscribe cycle takes about two seconds and repeats every 900s. A health…, test_health_alerts_when_bars_go_stale_during_an_open_session() (+5 more)

### Community 87 - "test_cli.py"
Cohesion: 0.08
Nodes (40): DemoTransport, _heal_args(), _isolated_bits_state(), no_broker(), Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped. (+32 more)

### Community 88 - ".write_notes"
Cohesion: 0.16
Nodes (17): apply(), apply(), apply(), _brief(), _close(), _empty_drafts(), load_drafts(), _merge_refs() (+9 more)

### Community 89 - "agent_advisor.py"
Cohesion: 0.07
Nodes (36): Harness maintenance — 2026-10-24, test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory(), run_turn() (+28 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.14
Nodes (13): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+5 more)

### Community 91 - ".persist_bar"
Cohesion: 0.18
Nodes (8): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Append one closed bar to the shared store. Goes through…, Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 92 - "cli.py"
Cohesion: 0.06
Nodes (57): argparse, agent_transcript_store_from_env(), _positive_float(), Transcript store for the configured backend (local SQLite by default)., agent_controller(), _agent_data_refresh_source(), _agent_status_path(), _agent_status_view() (+49 more)

### Community 93 - "test_live_feed.py"
Cohesion: 0.13
Nodes (36): config(), credentials(), FakeClient, FakeStore, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test…, The status file holds only the latest state, and these services write no… (+28 more)

### Community 94 - "TournamentDataset"
Cohesion: 0.23
Nodes (7): Path, frame_digest(), DataFrame, Path, Wait for a concurrent freeze of the same version to publish its manifest.…, Hash canonical timestamps, schema, and values independent of Parquet bytes., TournamentDataset

### Community 95 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 96 - "Store"
Cohesion: 0.25
Nodes (4): The 2026-10-05 sequence: a fresh engine, no halt anywhere, still no trade., Store, test_a_halt_from_another_process_still_stops_a_running_engine(), test_the_gate_holds_with_no_halt_key_and_survives_a_restart()

### Community 97 - "test_bits_research.py"
Cohesion: 0.12
Nodes (24): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+16 more)

### Community 98 - "._note"
Cohesion: 0.10
Nodes (22): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), heartbeat(), on_connected(), on_disconnected(), on_message(), tick(), confirmed() (+14 more)

### Community 99 - "test_local_state.py"
Cohesion: 0.08
Nodes (28): decision(), parametrize, Validation must not reject a real account, including a running one., The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is., The owner of a run is the only authority on whether it is live., The transcript had no DELETE anywhere and gained a row per heartbeat. 14,350…, Pruning must not delete content a connected reader has not displayed yet. The… (+20 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.12
Nodes (17): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+9 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.17
Nodes (24): skipif, notes(), open_drafts(), R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject(), test_draft_references_are_validated_and_closed_drafts_are_not_reopened(), test_explicit_corrected_resolution_clears_only_the_named_draft() (+16 more)

### Community 102 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 103 - "lab_strategy.py"
Cohesion: 0.15
Nodes (27): operator, bars(), parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate() (+19 more)

### Community 104 - "core.py"
Cohesion: 0.31
Nodes (7): test_backtest(), campaign(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 105 - "test_weekly_report.py"
Cohesion: 0.18
Nodes (18): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+10 more)

### Community 107 - "DataConfig"
Cohesion: 0.23
Nodes (12): pyarrow_parquet, test_dashboard_uses_metadata_and_bounded_tail_not_store_read(), DataConfig, chart(), _data(), chart_bars(), coverage(), _file() (+4 more)

### Community 108 - "atomic_write_json"
Cohesion: 0.09
Nodes (31): ast, signal, Two holders must never be inside the section at once. `flock` is per open file…, test_file_lock_is_exclusive_between_holders(), worker(), test_codex_environment_does_not_inherit_broker_credentials(), tomllib, _dependency_only() (+23 more)

### Community 109 - "attach_routes"
Cohesion: 0.24
Nodes (9): FastAPI, fastapi_responses, inspect, attach_routes(), lab_chart(), lab_events(), lab_snapshot(), resolve() (+1 more)

### Community 110 - "LabStore"
Cohesion: 0.06
Nodes (36): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+28 more)

### Community 111 - "BitsError"
Cohesion: 0.09
Nodes (40): 2. Publish the Datadog workflow message stream (required for the thinking panel), main(), call(), Two-invocation, no-trading smoke test of Bits -> shell -> Bits. Run from the…, envelope(), interrogation(), parametrize, shell_action() (+32 more)

### Community 113 - "._discover_account"
Cohesion: 0.21
Nodes (11): app_failed(), account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), The broker client, created once. Injected through ``client_factory`` so the… (+3 more)

### Community 114 - "promote_tools"
Cohesion: 0.19
Nodes (21): generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused(), test_symlinks_and_size_limit_refuse_execution() (+13 more)

### Community 115 - "agent_tools.py"
Cohesion: 0.11
Nodes (14): html, html_parser, ipaddress, re, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), urllib_parse (+6 more)

### Community 116 - "RecordingPostgres"
Cohesion: 0.20
Nodes (3): PostgresLikeTranscript, psycopg-like connection: one implicit transaction per block, committed or…, RecordingPostgres

### Community 117 - "NormalizedDecision"
Cohesion: 0.22
Nodes (8): The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise., Signals, test_engine_refuses_to_evaluate_a_strategy_with_no_recorded_validation(), test_halt_stops_proposals_and_persists_the_reason(), handler(), NormalizedDecision, Strategy proposal expressed in configured paper-trading quantity units.

### Community 118 - "write_status"
Cohesion: 0.26
Nodes (14): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), bits_alerts() (+6 more)

### Community 119 - "read_quote"
Cohesion: 0.19
Nodes (16): ctrader_open_api_messages_openapimessages_pb2, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_feed_matches_account_and_symbol_before_recording(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time(), test_sample_once_second_history_retention_and_hard_bound() (+8 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.22
Nodes (19): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal() (+11 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "pytest"
Cohesion: 0.25
Nodes (7): pytest, The durable-write primitives every writer in this repository shares., A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_times_out_instead_of_waiting_forever(), test_lock_file_lives_beside_the_target_and_is_released()

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.12
Nodes (8): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), test_statistics_counts_retained_evidence_without_claiming_success(), _age(), Counts only bounded retained evidence; never infer remote execution success., retained_statistics()

### Community 124 - "test_strategy_proposals.py"
Cohesion: 0.43
Nodes (6): test_novel_formulas_generate_valid_signals(), test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), novel_proposals(), Proposal, ProposalEngine

### Community 125 - "evidence_refs"
Cohesion: 0.38
Nodes (7): evidence_refs(), add(), ordered(), walk(), _legacy_draft(), Evidence references named by a (possibly malformed) payload: bounded, safe,…, The single pending record written by the previous release, as one open draft.

### Community 126 - "Delivery Stages"
Cohesion: 0.25
Nodes (5): Bits shell environment (`bits-capabilities`), Delivery Stages, Historical delivery and deployment notes, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.11
Nodes (19): Active Codex agent, Architecture, Aurum — Codex Autonomous Trading Lab, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+11 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.13
Nodes (14): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, graphify, Historical deployment state — verified 2026-10-05, Local agent handoff — completed 2026-09-24 (+6 more)

### Community 132 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.19
Nodes (9): test_resume_takes_effect_on_a_running_engine_without_a_restart(), DemoExecutor, PaperToCTraderDemoCoordinator, Any, Protocol, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it. (+1 more)

### Community 133 - "types"
Cohesion: 0.33
Nodes (4): test_failed_worker_schedule_rolls_back_without_retry(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), types, release_healthy()

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.20
Nodes (10): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Research continuity and maintenance — 2026-10-24 (+2 more)

### Community 135 - "_MainContent"
Cohesion: 0.29
Nodes (3): HTMLParser, _MainContent, Prefer a publisher's explicit content region over repeated site menus.

### Community 136 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.20
Nodes (10): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Operating model, Research activity chat — 2026-10-23, Research and automatic deployment (+2 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "README.md"
Cohesion: 0.17
Nodes (6): Bits agent instructions, Audit findings, Harness cleanup and improvement checklist — 2026-10-24, Verification and deployment log, Autonomous Agent, Legacy Datadog planner operations

### Community 140 - "Planner"
Cohesion: 0.33
Nodes (3): MissingToolPlanner, Planner, test_missing_executables_are_retained_across_cycles_and_restarts()

### Community 141 - "Merge review — 2026-09-25, baseline `cba22b2`"
Cohesion: 0.40
Nodes (5): Delivery order after this merge, Merge review — 2026-09-25, baseline `cba22b2`, R1 — P0: do not lose pending findings when memory is rewritten, R3 — P1: make experiment continuity work with the deployed backend, Runtime adoption is still pending

### Community 143 - "test_agent_config_rejects_non_finite_limits"
Cohesion: 0.67
Nodes (3): parametrize, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An…, test_agent_config_rejects_non_finite_limits()

### Community 147 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 150 - "_datetime"
Cohesion: 0.07
Nodes (48): Engineering, functools, Explicit operator-only, flat paper account rebase; no research reset., rebase(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal(), utc_day(), _archive() (+40 more)

### Community 152 - ".from_env"
Cohesion: 0.29
Nodes (6): 7.1 Code — one relaxation (small, tested), 7.2 Deploy — one systemd unit (mirror rule applies), 7.3 Config/docs, 7. Required changes (tracked, not yet implemented), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout()

### Community 153 - "test_lab_statistics.py"
Cohesion: 0.33
Nodes (6): test_counter_update_rolls_back_with_owning_state_transaction(), test_counters_survive_detail_eviction_and_ignore_duplicate_updates(), Small transactional counters; detailed evidence may expire independently., Called inside the transaction that writes the owning row., snapshot(), transition()

### Community 156 - "HistoricalDataStore"
Cohesion: 0.08
Nodes (24): Research notes (`bits-memory`, schema `xauusd.notes/1`), 9. Recovering the market-data store, Interpreter guard for subcommands, OSError, test_store_rejects_invalid_ohlc(), test_store_roundtrip(), test_trendbar_delta_decoding(), CTraderHistoricalAdapter (+16 more)

### Community 158 - "create_app"
Cohesion: 0.12
Nodes (19): fixture, server(), frame(), test_invalid_backend_raises(), read(), create_app(), data_update_status(), health() (+11 more)

### Community 159 - "ToolRegistry"
Cohesion: 0.24
Nodes (5): RuntimeError, Immutable-in-practice allow-list. Only the application can register tools., ToolExecutionError, ToolRegistry, ToolSpec

## Knowledge Gaps
- **175 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+170 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1139 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LiveBarFeed` connect `test_live_feed.py` to `._note`, `LiveFeedConfig`, `DataConfig`, `json`, `atomic_write_json`, `HistoricalDataStore`, `._discover_account`, `read_quote`, `CTraderAuthError`, `.persist_bar`, `cli.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `Repository Operating Rules`, `ConfirmedBreakoutCanarySource`, `ml_campaign.py`, `json`, `test_agent_loop.py`, `CTraderAuthError`, `test_lab.py`, `test_retention.py`, `test_automation.py`, `ExecutionConfig`, `test_data.py`, `test_bits_capabilities.py`, `AgentTools`, `test_cli.py`, `cli.py`, `test_live_feed.py`, `TournamentDataset`, `LiveFeedConfig`, `DataConfig`, `agent_tools.py`, `read_quote`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `PaperToCTraderDemoCoordinator`, `json`, `test_health_reports_degraded_when_the_state_store_is_unavailable`, `test_agent_loop.py`, `test_agent_view.py`, `_datetime`, `SQLitePaperTradingStore`, `test_demo_execution.py`, `create_app`, `test_lab.py`, `.__init__`, `test_demo_runner.py`, `InMemoryAgentTranscriptStore`, `PaperDecision`, `restart_policy`, `ContinuousAgentRunner`, `test_engine_loop.py`, `test_cli.py`, `PaperTradingEngine`, `cli.py`, `test_local_state.py`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ExperimentRegistry` (e.g. with `R3 — P1: make experiment continuity work with the deployed backend` and `AdaptiveSearch`) actually correct?**
  _`ExperimentRegistry` has 12 INFERRED edges - model-reasoned connections that need verification._