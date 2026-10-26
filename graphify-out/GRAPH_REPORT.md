# Graph Report - xauusd-completion-release  (2026-10-26)

## Corpus Check
- 204 files · ~203,265 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .service 9, (none) 7, .timer 3)

## Summary
- 3841 nodes · 10758 edges · 176 communities (150 shown, 26 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 564 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e74c5e90`
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
- ConfirmedBreakoutCanarySource
- MemoryRegistry
- test_bits_capabilities.py
- CTraderDemoAdapter
- ml_campaign.py
- demo_runner.py
- PaperTrading
- self_improve.py
- research_program.py
- DemoAutomationRunner
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- validation.py
- SecretFilter
- XAUUSD discovery, incident, quantitative, and scaling audit
- create_app
- test_data.py
- OpenAICompatiblePlanner
- PaperDecision
- test_demo_execution.py
- persist_tokens_env
- CodexResearchClient
- lab_api.py
- test_lab.py
- setup
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- synthetic_bars
- ShadowTradingReadiness
- json
- BitsStore
- ProposalEngine
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
- CTraderDemoSafetyError
- Any
- Backtester
- restart_policy
- TournamentRunner
- ExecutionConfig
- ContinuousAgentRunner
- canonical_json
- Store
- CTraderDemoStore
- read_quote
- PostgresConnection
- graphify.js
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- extraction-spec.md
- test_cftc_research.py
- BitsAgentRunner
- test_session_calendar.py
- Architecture and data-flow map
- _store
- opencode.json
- EngineConfig
- .__init__
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- lab_sources.py
- AgentTools
- memory_registry.py
- snapshot
- test_cli.py
- PaperToCTraderDemoCoordinator
- AgentAdvisor
- PaperTradingEngine
- closed_bar
- CTraderVolumePolicy
- LiveBarFeed
- LabStore
- ml_models.py
- bits_capabilities.py
- bits_runner.py
- ._note
- SQLiteAgentTranscriptStore
- LiveFeedConfig
- test_bits_memory_drafts.py
- .run
- lab_strategy.py
- test_ctrader_demo.py
- test_weekly_report.py
- lab.py
- EngineeringManager
- search_space.py
- test_oauth.py
- atomic_write_text
- BitsError
- run
- .record_rejection
- lab_tools.py
- Any
- bits_memory.py
- verify_result_parity.py
- test_dashboard.py
- test_data_heal_defers_a_window_that_does_not_fit_the_budget
- portfolio_research.py
- .send
- pytest
- test_lab_dashboard.py
- build_parser
- evidence_refs
- README.md
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- BitsMemory
- _datetime
- Persistent open-ended Codex agent
- Operator runbook: engine, live feed, and the visible harness
- test_offline.py
- Codex autonomous trading lab
- Datadog Bits connection
- Harness cleanup and improvement checklist — 2026-10-24
- Signals
- transition
- cli.py
- build_features
- CockroachAgentTranscriptStore
- parse_notes_input
- InMemoryHarnessStore
- Database maintenance and seven-day log rotation
- harness-outcomes-plan-2026-10-23.md
- serialized
- Research and measured self-improvement implementation plan
- RecordingPostgres
- run
- agent_advisor.py
- CockroachHarnessStore
- TournamentDataset
- HistoricalDataStore
- DemoRunnerConfig
- FakeResponse
- missing_executables
- test_large_overlapping_update_keeps_the_newest_values
- Research program and measured improvement
- StateTransaction
- sklearn_base
- tarfile
- SequencedTransport
- _error_code
- authorize_url
- test_persist_tokens_keeps_the_stored_refresh_token_when_none_is_returned
- Delivery Stages
- test_lab_retention.py
- Research completion and repair — 2026-10-26
- test_persist_tokens_rewrites_an_exported_assignment
- engine_decision_id
- test_persist_tokens_keeps_the_last_duplicate_assignment
- demo_feed_environment

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `MemoryRegistry` - 89 edges
3. `setup()` - 89 edges
4. `HistoricalDataStore` - 80 edges
5. `ExperimentRegistry` - 76 edges
6. `SQLiteAgentTranscriptStore` - 73 edges
7. `main()` - 71 edges
8. `_datetime()` - 67 edges
9. `BitsStore` - 66 edges
10. `InMemoryPaperTradingStore` - 65 edges

## Surprising Connections (you probably didn't know these)
- `Persistent Codex and experimental paper accounts (2026-10-22)` --references--> `rebase()`  [INFERRED]
  docs/operator-runbook-agent.md → xauusd/account_rebase.py
- `12. Status of evidence` --references--> `OpenAICompatiblePlanner`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → xauusd/autonomous_harness.py
- `R3 — P1: make experiment continuity work with the deployed backend` --references--> `ExperimentRegistry`  [INFERRED]
  requirements.md → xauusd/experiment_registry.py
- `Research completion — 2026-10-26` --references--> `result_summary()`  [INFERRED]
  AGENTS.md → xauusd/research_workflow.py
- `Research completion and repair — 2026-10-26` --references--> `result_summary()`  [INFERRED]
  README.md → xauusd/research_workflow.py

## Import Cycles
- None detected.

## Communities (176 total, 26 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.07
Nodes (37): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC (+29 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.29
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "OperationsManager"
Cohesion: 0.09
Nodes (20): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+12 more)

### Community 3 - "dashboard.py"
Cohesion: 0.08
Nodes (54): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), plotly_graph_objects (+46 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.09
Nodes (30): _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted., `monitor_error` used to be assigned and then read by nothing at all. (+22 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.18
Nodes (5): ExperimentStatus, ExperimentRegistry, Any, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool.

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.23
Nodes (16): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+8 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "test_bits_capabilities.py"
Cohesion: 0.13
Nodes (32): R2 — P1: capability discovery failure must remain visible, fake_tool(), The shell-job environment is discoverable from the environment jobs really get., Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_every_published_operation_is_a_real_cli_command(), test_failed_discovery_is_explicit_in_every_view(), test_invalid_declared_directories_are_configuration_errors_not_missing_tools() (+24 more)

### Community 10 - "CTraderDemoAdapter"
Cohesion: 0.15
Nodes (15): event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending(), test_partial_fill_followed_by_rejection_requires_reconciliation() (+7 more)

### Community 11 - "ml_campaign.py"
Cohesion: 0.15
Nodes (21): HistGradientBoostingClassifier, ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined(), EnsembleConfig (+13 more)

### Community 12 - "demo_runner.py"
Cohesion: 0.11
Nodes (13): _normalized_m1_bars(), DataFrame, NormalizedDecision, Coordinates accepted paper decisions with explicitly started cTrader demo…, Strategy proposal expressed in configured paper-trading quantity units., DecisionSource, DemoLifecycle, MarketData (+5 more)

### Community 13 - "PaperTrading"
Cohesion: 0.08
Nodes (52): test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_surfaces_a_monitor_error(), test_job_endpoint_pages_a_shell_capture(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_once_reports_a_refused_restart(), test_demo_automation_paper_only_skips_broker_dependencies(), test_paper_start_overrides_operator_stop() (+44 more)

### Community 14 - "self_improve.py"
Cohesion: 0.14
Nodes (19): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+11 more)

### Community 15 - "research_program.py"
Cohesion: 0.13
Nodes (34): test_blockers_are_classified_and_repair_has_priority(), test_completed_plan_legacy_evidence_is_backfilled_only_by_exact_id(), test_old_workspace_exact_evidence_can_be_recorded_after_log_rotation(), test_only_two_plans_may_execute_and_success_must_be_interpreted(), plan(), test_compact_context_pages_full_design_without_truncating_evidence(), test_completed_findings_accumulate_lessons_without_recounting(), test_discovery_insights_require_real_retrieval_and_do_not_claim_availability() (+26 more)

### Community 16 - "DemoAutomationRunner"
Cohesion: 0.26
Nodes (5): DemoAutomationRunner, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 17 - "Any"
Cohesion: 0.17
Nodes (12): CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded(), Any (+4 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.10
Nodes (40): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), parametrize, A ticking agent must not be served as stopped. The engine's startup reconcile…, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An… (+32 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.14
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (21): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+13 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.05
Nodes (42): _feed(), _harness_client(), paper_trading(), fixture, parametrize, The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., `limit` alone does not bound a response. A shell-job step carries a captured… (+34 more)

### Community 22 - "validation.py"
Cohesion: 0.09
Nodes (37): ML governance and drift controls — 2026-08-21, numpy, sklearn_metrics, An empty training window must fail loudly, not look like a negative result., The embargo must reach the report, not just the helper. `walk_forward_splits`…, The negative path was never asserted, which is why several real defects…, A 30-bar rolling feature reaches across the split boundary. The last…, test_block_bootstrap_preserves_clustered_sequence_effect() (+29 more)

### Community 23 - "SecretFilter"
Cohesion: 0.08
Nodes (31): Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, test_service_like_shell_runs_documented_examples_without_profile(), action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes… (+23 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "create_app"
Cohesion: 0.08
Nodes (36): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), bits_alerts() (+28 more)

### Community 26 - "test_data.py"
Cohesion: 0.11
Nodes (28): errno, test_data_update_does_not_retry_auth_errors(), unauthorized(), demo_env(), downloader_config(), minute_60(), one_bar_at(), validate() is no longer a one-time check performed only by from_env(). The… (+20 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.24
Nodes (10): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError (+2 more)

### Community 28 - "PaperDecision"
Cohesion: 0.16
Nodes (21): decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+13 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.19
Nodes (19): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches() (+11 more)

### Community 30 - "persist_tokens_env"
Cohesion: 0.12
Nodes (22): PathLike, A crash mid-write must not destroy the other credentials. ``write_text``…, The rewrite must hold a lock for the whole read-modify-write. Two independent…, Smoke test: concurrent writers never produce an unparseable env file., test_persist_tokens_appends_missing_key_and_sets_0600(), test_persist_tokens_leaves_a_valid_file_after_many_writers(), writer(), test_persist_tokens_never_truncates_the_file() (+14 more)

### Community 31 - "CodexResearchClient"
Cohesion: 0.12
Nodes (16): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000) (+8 more)

### Community 32 - "lab_api.py"
Cohesion: 0.14
Nodes (18): pyarrow_parquet, test_statistics_counts_retained_evidence_without_claiming_success(), test_dashboard_uses_metadata_and_bounded_tail_not_store_read(), read_status(), _age(), chart(), _data(), events() (+10 more)

### Community 33 - "test_lab.py"
Cohesion: 0.10
Nodes (39): parametrize, qualified_candidate(), quote(), bars(), test_codex_environment_does_not_inherit_broker_credentials(), test_evidence_relations_are_checked_beyond_digest(), test_forward_coverage_rejects_short_observation_despite_fixed_deadline(), test_forward_coverage_uses_new_york_market_minutes_and_accepts_complete_week() (+31 more)

### Community 34 - "setup"
Cohesion: 0.14
Nodes (25): test_account_only_reset_preserves_research_and_stop(), test_improvement_cannot_claim_old_release_as_new_work(), test_inspection_and_failed_remote_work_are_not_progress(), test_outcome_requires_existing_successful_evidence_and_deduplicates(), test_compaction_also_refuses_deactivating_or_unverified_units(), test_compaction_refuses_a_running_database_service(), test_legacy_row_count_pruning_preserves_unknown_jobs(), test_offline_compaction_reclaims_pages_without_changing_account_or_learning() (+17 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.12
Nodes (15): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+7 more)

### Community 37 - "synthetic_bars"
Cohesion: 0.07
Nodes (39): Dependence-aware bootstrap validation — 2026-08-21, parametrize, test_return_features_exclude_entire_gap_straddling_horizon(), dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version… (+31 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (11): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), Path (+3 more)

### Community 39 - "json"
Cohesion: 0.09
Nodes (48): base64, collections, concurrent_futures, contextlib, csv, dataclasses, datetime, fcntl (+40 more)

### Community 40 - "BitsStore"
Cohesion: 0.12
Nodes (13): Operations, 5. Restart the live view so the new observability is visible, memory(), fixture, memory(), fixture, test_bits_notes_only_does_not_repeat_history(), BitsStore (+5 more)

### Community 41 - "ProposalEngine"
Cohesion: 0.13
Nodes (9): test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), novel_proposals(), Proposal, ProposalEngine, Path (+1 more)

### Community 42 - "._fetch"
Cohesion: 0.41
Nodes (13): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+5 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 49 - "test_retention.py"
Cohesion: 0.08
Nodes (54): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(), archive(), _local_backups() (+46 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.14
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 51 - "InMemoryAgentTranscriptStore"
Cohesion: 0.09
Nodes (10): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), test_base_runner_records_codes_for_planner_and_tick_errors(), boom(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store., Mirror of the SQLite retention so both backends behave the same., Family-scoped mirror of the SQL stores: never close another family's run. (+2 more)

### Community 52 - "test_automation.py"
Cohesion: 0.09
Nodes (30): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+22 more)

### Community 53 - "CTraderDemoSafetyError"
Cohesion: 0.12
Nodes (19): copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+11 more)

### Community 54 - "Any"
Cohesion: 0.12
Nodes (9): CockroachPaperTradingStore, _now(), transition(), transition(), PaperTradingStore, Any, Protocol, CockroachDB is the authoritative state and idempotency store in production. (+1 more)

### Community 55 - "Backtester"
Cohesion: 0.29
Nodes (7): test_backtest(), campaign(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 56 - "restart_policy"
Cohesion: 0.14
Nodes (14): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+6 more)

### Community 57 - "TournamentRunner"
Cohesion: 0.21
Nodes (7): _atomic_json(), compute_job(), _finite(), Path, Consume deterministic experiments without reading the holdout test set., Champion-selection statistic, or ``None`` when a component is undefined.…, TournamentRunner

### Community 58 - "ExecutionConfig"
Cohesion: 0.14
Nodes (27): pandas, main(), Secret-free deterministic parity fixture for the runtime container., bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240… (+19 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.10
Nodes (15): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, BaseException, Protocol (+7 more)

### Community 60 - "canonical_json"
Cohesion: 0.16
Nodes (18): seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), Explicit operator-only, flat paper account rebase; no research reset., rebase(), AgentAlreadyRunning, AgentLock, Single process per container; the lock is runtime coordination, not state. (+10 more)

### Community 61 - "Store"
Cohesion: 0.22
Nodes (5): The 2026-10-05 sequence: a fresh engine, no halt anywhere, still no trade., Store, test_a_halt_from_another_process_still_stops_a_running_engine(), test_resume_clears_a_persisted_halt(), test_the_gate_holds_with_no_halt_key_and_survives_a_restart()

### Community 62 - "CTraderDemoStore"
Cohesion: 0.14
Nodes (3): CTraderDemoStore, CTraderTransport, Protocol

### Community 63 - "read_quote"
Cohesion: 0.20
Nodes (16): ctrader_open_api_messages_openapimessages_pb2, sqlite3, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time(), test_sample_once_second_history_retention_and_hard_bound() (+8 more)

### Community 64 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

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
Cohesion: 0.07
Nodes (62): date, pandas_tseries_holiday, _cot_csv(), _prereg(), The preregistered CFTC study: point-in-time discipline, session weeks, fail-…, 15:30 New York is 20:30 UTC in winter and 19:30 UTC under daylight time. The…, The fail-closed check the artifact claims, verified instead of asserted. Taking…, Excluding 2023 and 2025 wholesale means some flows span a gap; report how many.… (+54 more)

### Community 72 - "BitsAgentRunner"
Cohesion: 0.11
Nodes (13): error_details(), message_fingerprint(), BaseException, Payload-free classification of an exception for events and heartbeats.…, Stable digest of a message stream, used to persist each turn exactly once., BitsAgentRunner, Any, Retrieval-loop evidence for the heartbeat, which this file writes every tick. A… (+5 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.16
Nodes (20): at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from…, Synthetic M1 bars stamped at bar open, only while the session gate is open., session_bars(), test_a_week_whose_data_stops_early_is_not_complete(), test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected(), test_pandas_weekly_labels_disagree_with_session_weeks() (+12 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "_store"
Cohesion: 0.06
Nodes (43): _bars(), _minute_bars(), The archive is the only rebuild path, so a plan must prove it loses no range.…, Three valid, non-overlapping minutes, shifted so writers never collide., `data update` starts from the newest bar, so a hole in the middle is permanent.…, A weekend is not data loss; counting it as such hides the gaps that matter., The path the CLI takes: no frame passed in., A shared temporary name lets two writers interleave into one inode. That is how… (+35 more)

### Community 77 - "EngineConfig"
Cohesion: 0.14
Nodes (11): An oversized proposal must be visibly refused, not silently trimmed. Clamping…, test_engine_cannot_exceed_max_position(), test_engine_config_rejects_unbounded_values(), test_engine_does_not_clamp_an_oversized_proposal(), test_engine_status_reports_the_running_process_not_a_phantom(), test_resume_takes_effect_on_a_running_engine_without_a_restart(), engine_controller(), Operator and supervisor control for the deterministic trade engine. (+3 more)

### Community 78 - ".__init__"
Cohesion: 0.15
Nodes (5): EngineStore, MarketSource, Protocol, The narrow slice of the durable store the engine needs., TranscriptSink

### Community 79 - "test_bits_memory.py"
Cohesion: 0.16
Nodes (23): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection(), reply(), sample_notes() (+15 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.10
Nodes (32): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case., The hash stops a later edit to the artifact redefining what was granted. (+24 more)

### Community 82 - "lab_sources.py"
Cohesion: 0.10
Nodes (14): html, html_parser, HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), urllib_parse, urllib_request (+6 more)

### Community 83 - "AgentTools"
Cohesion: 0.09
Nodes (25): Store, test_dependency_install_requires_pins(), test_dependency_install_targets_scratch_only(), test_domain_configuration(), test_fetch_rejects_private_dns(), test_market_observe_excludes_frozen_and_forming_bars(), test_market_observe_without_frozen_boundary_reveals_no_history(), test_process_timeout_and_output_bound() (+17 more)

### Community 86 - "snapshot"
Cohesion: 0.19
Nodes (7): test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), test_release_advisory_classification_never_hides_engineering_uncertainty(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal(), utc_day(), snapshot()

### Community 87 - "test_cli.py"
Cohesion: 0.10
Nodes (30): DemoTransport, _isolated_bits_state(), no_broker(), Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., An interior hole is a smaller problem than a refresh reported as failed. The…, _run_cli(), stopped_demo_adapter() (+22 more)

### Community 88 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.21
Nodes (8): DemoExecutor, PaperToCTraderDemoCoordinator, Any, Protocol, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it., Runs paper risk first; execution lifecycle remains explicitly operator…

### Community 89 - "AgentAdvisor"
Cohesion: 0.06
Nodes (35): Harness maintenance — 2026-10-24, test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_explicit_evidence_pages_and_source_excerpts_survive_context_compaction(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory() (+27 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.14
Nodes (13): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+5 more)

### Community 91 - "closed_bar"
Cohesion: 0.18
Nodes (7): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 92 - "CTraderVolumePolicy"
Cohesion: 0.29
Nodes (4): test_volume_policy_from_metadata(), CTraderVolumePolicy, Broker-declared volume constraints; a volume failing any rule must be rejected…, Return a rejection reason when volume violates broker constraints, else None.

### Community 93 - "LiveBarFeed"
Cohesion: 0.12
Nodes (37): config(), credentials(), FakeClient, FakeStore, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test…, The status file holds only the latest state, and these services write no… (+29 more)

### Community 94 - "LabStore"
Cohesion: 0.17
Nodes (7): test_snapshot_expiry_deletes_backend_rows(), LabStore, save(), add(), add(), save(), Expire old price-mark results, never actual trade idempotency keys. Monitor…

### Community 95 - "ml_models.py"
Cohesion: 0.09
Nodes (20): ImportError, importlib, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample(), test_core_model_adapters_and_ensemble_probabilities() (+12 more)

### Community 96 - "bits_capabilities.py"
Cohesion: 0.09
Nodes (33): Datadog Bits operations, platform, shlex, test_shell_environment_keeps_the_latest_refreshed_tokens(), test_shell_path_prepends_service_interpreter_and_declared_directories(), cli_prefix(), data_access(), _error_code() (+25 more)

### Community 97 - "bits_runner.py"
Cohesion: 0.10
Nodes (31): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+23 more)

### Community 98 - "._note"
Cohesion: 0.09
Nodes (22): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), heartbeat(), on_connected(), on_disconnected(), on_message(), tick(), confirmed() (+14 more)

### Community 99 - "SQLiteAgentTranscriptStore"
Cohesion: 0.07
Nodes (43): Connection, Row, The deterministic engine writes to the same `agent_runs` table. Taking the…, test_status_and_health_select_the_agent_run_not_a_newer_engine_run(), decision(), parametrize, Validation must not reject a real account, including a running one., The agent and the engine share one `agent_runs` table. An engine start ran an… (+35 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.11
Nodes (18): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+10 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.18
Nodes (24): skipif, notes(), open_drafts(), R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject(), test_concurrent_writers_with_the_same_base_cannot_both_win(), writer() (+16 more)

### Community 102 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 103 - "lab_strategy.py"
Cohesion: 0.16
Nodes (24): operator, parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate(), test_dataset_advances_only_to_a_wholly_new_cohort() (+16 more)

### Community 104 - "test_ctrader_demo.py"
Cohesion: 0.09
Nodes (33): adapter(), FakeClient, ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call() (+25 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.16
Nodes (18): Gate-failure and near-pass analytics — 2026-08-21, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors(), test_selection_bias_computes_bh_and_aligned_fold_pbo(), test_selection_bias_reports_score_distribution_and_missing_controls() (+10 more)

### Community 106 - "lab.py"
Cohesion: 0.14
Nodes (18): functools, atomic_write_json(), Any, Serialise ``payload`` as JSON and replace ``target`` atomically. ``allow_nan``…, _job_outputs(), main(), moment(), _old() (+10 more)

### Community 107 - "EngineeringManager"
Cohesion: 0.25
Nodes (8): _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker., _safe()

### Community 108 - "search_space.py"
Cohesion: 0.20
Nodes (16): E. Current 50,000-scenario architecture and benchmark, dotenv, itertools, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe() (+8 more)

### Community 109 - "test_oauth.py"
Cohesion: 0.23
Nodes (15): response_json(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises(), test_refresh_access_token_returns_pair_with_browser_agent(), fake_urlopen(), test_rejected_grant_raises_oauth_error() (+7 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.11
Nodes (23): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+15 more)

### Community 111 - "BitsError"
Cohesion: 0.06
Nodes (58): 2. Publish the Datadog workflow message stream (required for the thinking panel), Delivery and operational boundaries, Delivery order after this merge, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Merge review — 2026-09-25, baseline `cba22b2`, Original incident evidence (pre-merge snapshot) (+50 more)

### Community 112 - "run"
Cohesion: 0.27
Nodes (6): test_failed_worker_schedule_rolls_back_without_retry(), test_research_advisories_do_not_disable_safe_software_releases(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), release_healthy(), run(), schedule_verification()

### Community 113 - ".record_rejection"
Cohesion: 0.21
Nodes (14): apply(), apply(), apply(), _brief(), _close(), _empty_drafts(), load_drafts(), _merge_refs() (+6 more)

### Community 114 - "lab_tools.py"
Cohesion: 0.14
Nodes (28): ast, selectors, generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed() (+20 more)

### Community 115 - "Any"
Cohesion: 0.15
Nodes (5): HarnessStore, Any, Protocol, RuntimeError, ToolExecutionError

### Community 116 - "bits_memory.py"
Cohesion: 0.19
Nodes (18): _check_categories(), _check_draft_ids(), _check_entry(), check_notes(), _is_current_notes(), issue(), _key_path(), _kind() (+10 more)

### Community 117 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 118 - "test_dashboard.py"
Cohesion: 0.23
Nodes (8): setup_files(), test_dashboard_reads_latest_run_and_equity(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature(), test_status_remains_readable_without_generated_tournament_dataset(), test_system_metrics_include_capacity_network_and_services(), test_tournament_equity_and_leaderboard()

### Community 119 - "test_data_heal_defers_a_window_that_does_not_fit_the_budget"
Cohesion: 0.26
Nodes (10): _heal_args(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _store_with_windows(), test_data_heal_defers_a_window_that_does_not_fit_the_budget(), test_data_heal_downloads_an_interior_window(), test_data_heal_dry_run_never_contacts_the_broker() (+2 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.22
Nodes (19): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal() (+11 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "pytest"
Cohesion: 0.18
Nodes (15): pytest, The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker() (+7 more)

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.10
Nodes (13): FastAPI, fastapi_responses, fastapi_testclient, inspect, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), attach_routes() (+5 more)

### Community 124 - "build_parser"
Cohesion: 0.20
Nodes (10): ArgumentParser, Bits shell environment (`bits-capabilities`), Without this the command exists but nothing runs it, so a hole still sits for…, test_the_heal_command_is_in_the_cli_grammar(), test_update_can_heal_and_the_timer_does(), test_the_raw_retention_command_is_in_the_cli_grammar(), test_the_rebuild_command_is_in_the_cli_grammar(), cli_commands() (+2 more)

### Community 125 - "evidence_refs"
Cohesion: 0.38
Nodes (7): evidence_refs(), add(), ordered(), walk(), _legacy_draft(), Evidence references named by a (possibly malformed) payload: bounded, safe,…, The single pending record written by the previous release, as one open draft.

### Community 126 - "README.md"
Cohesion: 0.25
Nodes (3): Bits agent instructions, Autonomous Agent, Legacy Datadog planner operations

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.09
Nodes (22): Active Codex agent, Architecture, Aurum — Codex Autonomous Trading Lab, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+14 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.13
Nodes (15): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, Database retention — 2026-10-24, graphify, Local agent handoff — completed 2026-09-24 (+7 more)

### Community 132 - "BitsMemory"
Cohesion: 0.24
Nodes (6): _age_seconds(), BitsMemory, _note_sources(), _notes_base(), A specific next task for unresolved drafts; not a new research cycle., repair_reasons()

### Community 133 - "_datetime"
Cohesion: 0.20
Nodes (23): Engineering, build_agent_registry(), canary_signal_tool(), handler(), _decision_id(), _mock_market_for_read(), paper_state_tool(), propose_trade_tool() (+15 more)

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.20
Nodes (10): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Research continuity and maintenance — 2026-10-24 (+2 more)

### Community 135 - "Operator runbook: engine, live feed, and the visible harness"
Cohesion: 0.22
Nodes (8): 10. Related documents, 1. What was built and why, 4. Enable the deterministic engine, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback, Engine control, Operator runbook: engine, live feed, and the visible harness

### Community 136 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.20
Nodes (10): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Operating model, Research activity chat — 2026-10-23, Research and automatic deployment (+2 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "Harness cleanup and improvement checklist — 2026-10-24"
Cohesion: 0.40
Nodes (4): Audit findings, Broker smoke shutdown follow-up, Harness cleanup and improvement checklist — 2026-10-24, Verification and deployment log

### Community 140 - "Signals"
Cohesion: 0.25
Nodes (6): The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise., Signals, test_engine_does_nothing_when_the_signal_is_flat(), test_engine_refuses_to_evaluate_a_strategy_with_no_recorded_validation(), test_halt_stops_proposals_and_persists_the_reason()

### Community 141 - "transition"
Cohesion: 0.33
Nodes (6): test_counter_update_rolls_back_with_owning_state_transaction(), test_counters_survive_detail_eviction_and_ignore_duplicate_updates(), Small transactional counters; detailed evidence may expire independently., Called inside the transaction that writes the owning row., snapshot(), transition()

### Community 142 - "cli.py"
Cohesion: 0.06
Nodes (59): agent_transcript_store_from_env(), _positive_float(), Transcript store for the configured backend (local SQLite by default)., agent_controller(), _agent_data_refresh_source(), _agent_status_path(), _agent_status_view(), agent_tool() (+51 more)

### Community 143 - "build_features"
Cohesion: 0.13
Nodes (23): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+15 more)

### Community 144 - "CockroachAgentTranscriptStore"
Cohesion: 0.23
Nodes (4): CockroachAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row; see the SQLite store.

### Community 145 - "parse_notes_input"
Cohesion: 0.33
Nodes (3): parse_notes_input(), Strictly parse CLI input; malformed JSON is reported by line and column only., CLI write path: unparseable input is retained as text when it is safe to keep.

### Community 147 - "Database maintenance and seven-day log rotation"
Cohesion: 0.40
Nodes (4): Database maintenance and seven-day log rotation, Initial deployment, One-time physical compaction, Scheduled behavior

### Community 149 - "serialized"
Cohesion: 0.16
Nodes (16): test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), _archive(), Independent exploratory paper accounts; never a promotion or broker path. (+8 more)

### Community 150 - "Research and measured self-improvement implementation plan"
Cohesion: 0.25
Nodes (7): Acceptance criteria, Delivery checklist, Deployment procedure, Final verification and deployment, Implementation evidence so far, Objective and boundaries, Research and measured self-improvement implementation plan

### Community 151 - "RecordingPostgres"
Cohesion: 0.20
Nodes (3): PostgresLikeTranscript, psycopg-like connection: one implicit transaction per block, committed or…, RecordingPostgres

### Community 153 - "agent_advisor.py"
Cohesion: 0.13
Nodes (30): test_improvement_has_one_working_slot_and_protected_fix_is_escalated(), test_operator_release_measurements_yield_to_next_autonomous_release(), test_plan_keeps_evidence_and_code_provenance_after_call_log_rotation(), test_training_export_preserves_utc_index_and_reports_gaps(), test_measured_bottleneck_seeds_one_backlog_item_and_preserves_baseline(), test_missing_baseline_cannot_be_claimed_and_inference_history_is_bounded(), test_observed_regression_cannot_be_labeled_improved(), test_recent_metric_window_does_not_bias_toward_retained_old_unknowns() (+22 more)

### Community 155 - "TournamentDataset"
Cohesion: 0.23
Nodes (7): Path, frame_digest(), DataFrame, Path, Wait for a concurrent freeze of the same version to publish its manifest.…, Hash canonical timestamps, schema, and values independent of Parquet bytes., TournamentDataset

### Community 156 - "HistoricalDataStore"
Cohesion: 0.06
Nodes (33): Historical deployment state — verified 2026-10-05, 9. Recovering the market-data store, Interpreter guard for subcommands, OSError, frame(), test_positions_matches_get_indexer(), test_positions_requires_a_sorted_unique_index(), test_positions_resolves_an_anchor_sweep_in_one_pass() (+25 more)

### Community 159 - "missing_executables"
Cohesion: 0.50
Nodes (4): parametrize, test_missing_executables_are_detected_from_shell_messages(), missing_executables(), Names bash (or /usr/bin/env) reported as not found in a completed job's stderr.

### Community 160 - "test_large_overlapping_update_keeps_the_newest_values"
Cohesion: 0.50
Nodes (4): test_large_overlapping_update_keeps_the_newest_values(), frame(), read(), index()

### Community 161 - "Research program and measured improvement"
Cohesion: 0.25
Nodes (7): Decision cycle, Discovery and sources, Improvement measurement, Preregistration and execution, Release readiness and visibility, Research program and measured improvement, Storage and limitations

### Community 162 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 166 - "_error_code"
Cohesion: 0.20
Nodes (13): _error_code(), Return the cTrader error code for an error message, or None when unset., app_failed(), account_ok(), fail(), got_accounts(), got_symbols(), transport_failed() (+5 more)

### Community 167 - "authorize_url"
Cohesion: 0.67
Nodes (3): Market Data & Authentication, test_authorize_url_builds_documented_endpoint(), authorize_url()

### Community 169 - "Delivery Stages"
Cohesion: 0.25
Nodes (5): Delivery Stages, Historical delivery and deployment notes, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval, Research notes (`bits-memory`, schema `xauusd.notes/1`)

### Community 170 - "test_lab_retention.py"
Cohesion: 0.60
Nodes (5): store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics()

### Community 171 - "Research completion and repair — 2026-10-26"
Cohesion: 0.33
Nodes (5): Diagnosis and implementation, Measured pre-deployment audit, Measurement and release handling, Research completion and repair — 2026-10-26, Verification and limitations

### Community 173 - "engine_decision_id"
Cohesion: 0.50
Nodes (4): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), Durable identity for one engine decision. Derived from the bar, not from a…

## Knowledge Gaps
- **196 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+191 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1181 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `_datetime`, `ConfirmedBreakoutCanarySource`, `demo_runner.py`, `cli.py`, `build_features`, `test_agent_loop.py`, `validation.py`, `test_data.py`, `TournamentDataset`, `lab_api.py`, `test_lab.py`, `json`, `test_retention.py`, `test_automation.py`, `read_quote`, `_store`, `AgentTools`, `test_cli.py`, `LiveBarFeed`, `bits_capabilities.py`, `LiveFeedConfig`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `_datetime`, `demo_runner.py`, `cli.py`, `test_agent_loop.py`, `test_agent_view.py`, `serialized`, `create_app`, `PaperDecision`, `test_demo_execution.py`, `test_lab.py`, `setup`, `json`, `test_demo_runner.py`, `InMemoryAgentTranscriptStore`, `Any`, `restart_policy`, `ContinuousAgentRunner`, `canonical_json`, `.__init__`, `test_engine_loop.py`, `test_cli.py`, `PaperToCTraderDemoCoordinator`, `PaperTradingEngine`, `SQLiteAgentTranscriptStore`, `lab.py`, `test_data_heal_defers_a_window_that_does_not_fit_the_budget`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `BitsStore` connect `BitsStore` to `bits_runner.py`, `test_bits_memory_drafts.py`, `json`, `BitsAgentRunner`, `test_bits_capabilities.py`, `lab.py`, `PaperTrading`, `cli.py`, `BitsError`, `test_bits_memory.py`, `test_agent_view.py`, `test_cli.py`, `SecretFilter`, `create_app`, `canonical_json`, `LabStore`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `xauusd-research` to the rest of the system?**
  _196 weakly-connected nodes found - possible documentation gaps or missing edges._