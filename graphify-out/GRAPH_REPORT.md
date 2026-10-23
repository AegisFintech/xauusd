# Graph Report - xauusd-statistics-release  (2026-10-23)

## Corpus Check
- 181 files · ~190,372 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .service 8, (none) 7, .timer 2)

## Summary
- 3642 nodes · 10161 edges · 162 communities (139 shown, 23 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 536 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `02da3d8e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_ctrader_auth.py
- test_autonomous_harness.py
- OperationsManager
- dashboard.py
- test_bits_runner.py
- ExperimentRegistry
- .db
- ConfirmedBreakoutCanarySource
- MemoryRegistry
- ml_models.py
- test_ctrader_demo.py
- test_ml.py
- cli.py
- PaperTrading
- ImprovementLedger
- CockroachAgentTranscriptStore
- test_session_reset.py
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- pandas
- BitsStore
- XAUUSD discovery, incident, quantitative, and scaling audit
- run
- CTraderAuthError
- OpenAICompatiblePlanner
- PaperDecision
- test_demo_execution.py
- persist_tokens_env
- TournamentDataset
- ExperimentSpec
- test_lab.py
- memory_registry.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- synthetic_bars
- ShadowTradingReadiness
- build_features
- InMemoryAgentTranscriptStore
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
- test_ctrader_lifecycle.py
- test_automation.py
- CTraderDemoSafetyError
- Any
- CTraderVolumeConversion
- paper_from_env
- create_app
- ExecutionConfig
- ContinuousAgentRunner
- atomic_write_json
- verify_result_parity.py
- EngineConfig
- _registry_schema_valid
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
- test_bits.py
- data_heal
- canonical_json
- CodexImprovementWorkflow
- test_engine_loop.py
- test_bits_capabilities.py
- AgentTools
- LiveFeedUnavailable
- setup
- main
- bits_memory.py
- test_agent_advisor.py
- PaperTradingEngine
- .persist_bar
- HistoricalDataStore
- test_live_feed.py
- .run
- PostgresConnection
- PaperToCTraderDemoCoordinator
- test_bits_research.py
- ._note
- SQLiteAgentTranscriptStore
- LiveFeedConfig
- test_bits_memory_drafts.py
- _download_with_retry
- lab.py
- CodexResearchClient
- test_weekly_report.py
- HarnessStore
- agent_loop.py
- file_lock
- child_environment
- atomic_write_text
- BitsError
- LabStore
- ._discover_account
- lab_tools.py
- fetch_source
- bounded_process
- build_parser
- write_status
- pytest
- portfolio_research.py
- .send
- EngineeringManager
- test_lab_dashboard.py
- test_oauth.py
- evidence_refs
- Local audit — 2026-09-24
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- .execute
- types
- Persistent open-ended Codex agent
- /graphify
- test_offline.py
- Codex autonomous trading lab
- Datadog Bits connection
- README.md
- StoreCorruptError
- _looping_agent
- ResearchHarness
- test_lab_retention.py
- TournamentRunner
- engine_decision_id
- harness-outcomes-plan-2026-10-23.md
- demo_feed_environment
- _datetime
- InMemoryHarnessStore
- RecordingPostgres
- CockroachHarnessStore
- trendbars_to_frame
- cTrader SDK and protocol review (no broker connection)
- core.py
- _validate_json
- graphify reference: extra exports and benchmark
- demo_accounts
- FakeResponse
- _rewritten_env
- test_sandbox_tests_return_bounded_feedback_and_clean_environment
- .__init__

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `MemoryRegistry` - 89 edges
3. `HistoricalDataStore` - 76 edges
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
- `Order lifecycle and errors — follow-up #15` --references--> `is_error()`  [INFERRED]
  docs/local-handoff-audit-2026-09-24.md → xauusd/ctrader_auth.py
- `R3 — P1: make experiment continuity work with the deployed backend` --references--> `ExperimentRegistry`  [INFERRED]
  requirements.md → xauusd/experiment_registry.py

## Import Cycles
- None detected.

## Communities (162 total, 23 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.20
Nodes (13): test_is_error_extracts_code_and_description(), test_is_error_none_when_clear(), test_resolve_symbol_falls_back_to_first_match(), test_resolve_symbol_prefers_enabled_match(), test_resolve_symbol_rejects_invalid_id(), test_resolve_symbol_returns_none_when_absent(), test_real_protobuf_error_types_with_empty_codes(), _field() (+5 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.29
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "OperationsManager"
Cohesion: 0.09
Nodes (19): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+11 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (63): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), plotly_graph_objects (+55 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.11
Nodes (24): MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted., runner(), test_a_recent_running_job_is_still_polled() (+16 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.16
Nodes (6): ExperimentStatus, ExperimentRegistry, Any, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool., Path

### Community 6 - ".db"
Cohesion: 0.13
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.18
Nodes (20): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+12 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.10
Nodes (16): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+8 more)

### Community 9 - "ml_models.py"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.09
Nodes (32): adapter(), FakeClient, ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call() (+24 more)

### Community 11 - "test_ml.py"
Cohesion: 0.12
Nodes (25): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined() (+17 more)

### Community 12 - "cli.py"
Cohesion: 0.07
Nodes (70): base64, collections, concurrent_futures, contextlib, csv, dataclasses, datetime, dotenv (+62 more)

### Community 13 - "PaperTrading"
Cohesion: 0.07
Nodes (58): paper_trading(), The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., The monitor's status string alone was never enough. A monitor that died after…, test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_alerts_on_a_stale_or_dead_position_monitor(), test_health_names_the_paths_a_retrieval_loop_keeps_reading(), test_health_stays_quiet_when_no_path_repeats() (+50 more)

### Community 14 - "ImprovementLedger"
Cohesion: 0.13
Nodes (18): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+10 more)

### Community 15 - "CockroachAgentTranscriptStore"
Cohesion: 0.23
Nodes (4): CockroachAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row; see the SQLite store.

### Community 16 - "test_session_reset.py"
Cohesion: 0.32
Nodes (8): seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), AgentAlreadyRunning, AgentLock, Single process per container; the lock is runtime coordination, not state., Explicit operator reset of a stopped local paper session, after backup., reset_paper_session()

### Community 17 - "Any"
Cohesion: 0.16
Nodes (14): test_transport_submission_and_polling(), request(), CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe() (+6 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.11
Nodes (38): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), A ticking agent must not be served as stopped. The engine's startup reconcile…, refresh_config(), refresh_runner() (+30 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.15
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (22): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+14 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.05
Nodes (35): _feed(), _harness_client(), parametrize, The deterministic engine writes to the same `agent_runs` table. Taking the…, `limit` alone does not bound a response. A shell-job step carries a captured…, The health endpoint is the observability surface; it must not raise. An…, A non-SQLite transcript store must not take the panel down., The exact 2026-10-08 outage: bar_write_failed, session open, no alert. The… (+27 more)

### Community 22 - "pandas"
Cohesion: 0.10
Nodes (39): numpy, pandas, sklearn_metrics, An empty training window must fail loudly, not look like a negative result., The embargo must reach the report, not just the helper. `walk_forward_splits`…, The negative path was never asserted, which is why several real defects…, A 30-bar rolling feature reaches across the split boundary. The last…, test_block_bootstrap_preserves_clustered_sequence_effect() (+31 more)

### Community 23 - "BitsStore"
Cohesion: 0.07
Nodes (40): Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, test_service_like_shell_runs_documented_examples_without_profile(), action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes… (+32 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (47): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+39 more)

### Community 26 - "CTraderAuthError"
Cohesion: 0.11
Nodes (24): test_data_update_does_not_retry_auth_errors(), unauthorized(), demo_env(), downloader_config(), validate() is no longer a one-time check performed only by from_env(). The…, test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag() (+16 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.22
Nodes (11): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError (+3 more)

### Community 28 - "PaperDecision"
Cohesion: 0.18
Nodes (21): decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+13 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.12
Nodes (25): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+17 more)

### Community 30 - "persist_tokens_env"
Cohesion: 0.11
Nodes (22): PathLike, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent…, Smoke test: concurrent writers never produce an unparseable env file., test_persist_tokens_appends_missing_key_and_sets_0600() (+14 more)

### Community 31 - "TournamentDataset"
Cohesion: 0.08
Nodes (19): Dependence-aware bootstrap validation — 2026-08-21, test_portfolio_run_reads_validation_only(), setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap() (+11 more)

### Community 32 - "ExperimentSpec"
Cohesion: 0.26
Nodes (12): E. Current 50,000-scenario architecture and benchmark, main(), test_catalog_is_deterministic_and_valid(), test_replenishment_scans_past_existing_prefix(), ExperimentSpec, from_strategy(), candidate_specs(), catalog_size() (+4 more)

### Community 33 - "test_lab.py"
Cohesion: 0.14
Nodes (31): parametrize, qualified_candidate(), quote(), test_codex_contract_rejects_unknown_fields_and_overlarge_requests(), test_evidence_relations_are_checked_beyond_digest(), test_forward_coverage_rejects_short_observation_despite_fixed_deadline(), test_forward_coverage_uses_new_york_market_minutes_and_accepts_complete_week(), test_forward_window_is_scored_once_then_rejected() (+23 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.12
Nodes (15): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+7 more)

### Community 37 - "synthetic_bars"
Cohesion: 0.10
Nodes (30): dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version…, A freeze killed mid-write must not hang the next one, nor quietly pass., A backtester or cost change must invalidate stored results. Both were hardcoded…, test_a_version_directory_with_no_manifest_fails_loudly() (+22 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 39 - "build_features"
Cohesion: 0.14
Nodes (21): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error(), test_novel_formulas_generate_valid_signals() (+13 more)

### Community 40 - "InMemoryAgentTranscriptStore"
Cohesion: 0.09
Nodes (10): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), test_base_runner_records_codes_for_planner_and_tick_errors(), boom(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store., Mirror of the SQLite retention so both backends behave the same., Family-scoped mirror of the SQL stores: never close another family's run. (+2 more)

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
Cohesion: 0.17
Nodes (22): archive(), _local_backups(), test_compaction_preserves_rebuild_revision_winner(), test_compaction_reads_compressed_raw_pages(), test_completed_logs_only_and_pins(), test_completed_workspace_reclaims_training_and_scripts_but_keeps_memory(), test_completed_workspace_with_nested_symlink_retained(), test_compress_existing_exact_target_and_deterministic_bytes() (+14 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.06
Nodes (33): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+25 more)

### Community 51 - "test_ctrader_lifecycle.py"
Cohesion: 0.21
Nodes (11): Client, event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending() (+3 more)

### Community 52 - "test_automation.py"
Cohesion: 0.08
Nodes (32): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+24 more)

### Community 53 - "CTraderDemoSafetyError"
Cohesion: 0.13
Nodes (19): copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+11 more)

### Community 54 - "Any"
Cohesion: 0.09
Nodes (16): Execution Boundary, Operating model, 1. What was built and why, CockroachPaperTradingStore, _corrupt_state(), _default_state(), _now(), transition() (+8 more)

### Community 55 - "CTraderVolumeConversion"
Cohesion: 0.17
Nodes (7): test_demo_factory_binds_authoritative_paper_exposure(), _ctrader_demo_adapter(), expected_volume(), CTraderVolumeConversion, DemoExecutor, Protocol, Explicit conversion from paper quantity units to cTrader volume-in-cents units.

### Community 56 - "paper_from_env"
Cohesion: 0.09
Nodes (21): Operations, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+13 more)

### Community 57 - "create_app"
Cohesion: 0.08
Nodes (28): fixture, server(), frame(), read(), create_app(), data_update_status(), harness(), health() (+20 more)

### Community 58 - "ExecutionConfig"
Cohesion: 0.13
Nodes (29): main(), Secret-free deterministic parity fixture for the runtime container., bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,… (+21 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.10
Nodes (15): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, BaseException, Protocol (+7 more)

### Community 60 - "atomic_write_json"
Cohesion: 0.17
Nodes (25): atomic_write_bytes(), atomic_write_json(), _fsync_directory(), Any, Path, Replace ``target`` with ``payload`` atomically and durably., Serialise ``payload`` as JSON and replace ``target`` atomically. ``allow_nan``…, Persist a rename. Best effort: not every filesystem allows opening a dir. (+17 more)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "EngineConfig"
Cohesion: 0.15
Nodes (12): An oversized proposal must be visibly refused, not silently trimmed. Clamping…, test_engine_config_rejects_unbounded_values(), test_engine_does_not_clamp_an_oversized_proposal(), test_engine_status_reports_the_running_process_not_a_phantom(), _build_engine(), engine_controller(), _paper_to_demo_coordinator(), Construct the deterministic engine from the same stores the agent uses. (+4 more)

### Community 63 - "_registry_schema_valid"
Cohesion: 0.21
Nodes (12): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_registry_validation_streams_rows_and_rejects_non_array_tables(), Validate logical snapshot JSON in bounded memory (8 MiB per row). Snapshots…, _registry_schema_valid() (+4 more)

### Community 64 - "CTraderDemoAdapter"
Cohesion: 0.09
Nodes (8): CTraderDemoAdapter, CTraderDemoStore, CTraderTransport, Protocol, Executes only persisted, reconciled XAUUSD demo-order proposals., Persisted execution kill switch, consulted by the shared restart policy., Persist a minimal non-secret receipt, not arbitrary transport objects., _safe_response()

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
Nodes (63): date, pandas_tseries_holiday, _cot_csv(), _prereg(), The preregistered CFTC study: point-in-time discipline, session weeks, fail-…, 15:30 New York is 20:30 UTC in winter and 19:30 UTC under daylight time. The…, The fail-closed check the artifact claims, verified instead of asserted. Taking…, Excluding 2023 and 2025 wholesale means some flows span a gap; report how many.… (+55 more)

### Community 72 - "bits_runner.py"
Cohesion: 0.09
Nodes (23): error_details(), excerpt(), result_for_prompt(), message_fingerprint(), BaseException, Payload-free classification of an exception for events and heartbeats.…, Stable digest of a message stream, used to persist each turn exactly once., fills_since() (+15 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.08
Nodes (33): Delivery and operational boundaries, Delivery order after this merge, Implemented baseline — service environment discovery (R2 remains), Merge review — 2026-09-25, baseline `cba22b2`, Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit, P1 — Persist reproducible experiments and separate live signals, P1 — Separate monitoring cadence from meaningful agent reviews (+25 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.07
Nodes (51): errno, _bars(), frame(), minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.…, Three valid, non-overlapping minutes, shifted so writers never collide. (+43 more)

### Community 77 - "test_bits.py"
Cohesion: 0.18
Nodes (21): 10. Related documents, 2. Publish the Datadog workflow message stream (required for the thinking panel), 4. Enable the deterministic engine, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback, Engine control, Operator runbook: engine, live feed, and the visible harness (+13 more)

### Community 78 - "data_heal"
Cohesion: 0.24
Nodes (12): _heal_args(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _store_with_windows(), test_data_heal_defers_a_window_that_does_not_fit_the_budget(), test_data_heal_downloads_an_interior_window(), test_data_heal_dry_run_never_contacts_the_broker() (+4 more)

### Community 79 - "canonical_json"
Cohesion: 0.15
Nodes (24): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection(), reply(), sample_notes() (+16 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.10
Nodes (35): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case., The hash stops a later edit to the artifact redefining what was granted. (+27 more)

### Community 82 - "test_bits_capabilities.py"
Cohesion: 0.06
Nodes (72): platform, R2 — P1: capability discovery failure must remain visible, fake_tool(), parametrize, The shell-job environment is discoverable from the environment jobs really get., Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_every_published_operation_is_a_real_cli_command() (+64 more)

### Community 83 - "AgentTools"
Cohesion: 0.18
Nodes (18): Store, test_dependency_install_requires_pins(), test_dependency_install_targets_scratch_only(), test_domain_configuration(), test_fetch_rejects_private_dns(), test_market_observe_excludes_frozen_and_forming_bars(), test_market_observe_without_frozen_boundary_reveals_no_history(), test_remote_job_identity_is_action_derived() (+10 more)

### Community 84 - "LiveFeedUnavailable"
Cohesion: 0.15
Nodes (9): app_failed(), check(), LiveFeedConfigError, LiveFeedUnavailable, RuntimeError, ValueError, A refused configuration, carrying a stable code. Subclasses ``ValueError``…, Application auth, which the broker requires before any token request. Sending… (+1 more)

### Community 86 - "setup"
Cohesion: 0.13
Nodes (28): test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), test_improvement_cannot_claim_old_release_as_new_work(), test_inspection_and_failed_remote_work_are_not_progress() (+20 more)

### Community 87 - "main"
Cohesion: 0.12
Nodes (28): DemoTransport, _isolated_bits_state(), no_broker(), An interior hole is a smaller problem than a refresh reported as failed. The…, _run_cli(), stopped_demo_adapter(), test_bits_capabilities_check_and_stored_manifest(), test_bits_capabilities_direct_discovery_exception_still_exits_nonzero() (+20 more)

### Community 88 - "bits_memory.py"
Cohesion: 0.08
Nodes (45): Implemented baseline — memory writes and actionable errors (R1 remains), _age_seconds(), BitsMemory, apply(), apply(), apply(), _brief(), _check_categories() (+37 more)

### Community 89 - "test_agent_advisor.py"
Cohesion: 0.12
Nodes (18): test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory(), run_turn(), test_pre_job_research_failure_is_loud_and_preserves_trading_state() (+10 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.14
Nodes (13): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+5 more)

### Community 91 - ".persist_bar"
Cohesion: 0.18
Nodes (8): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Append one closed bar to the shared store. Goes through…, Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 92 - "HistoricalDataStore"
Cohesion: 0.08
Nodes (27): Historical deployment state — verified 2026-10-05, parametrize, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An…, test_agent_config_rejects_non_finite_limits(), test_demo_automation_requires_explicit_positive_volume(), test_store_rejects_invalid_ohlc(), test_store_roundtrip(), _positive_float() (+19 more)

### Community 93 - "test_live_feed.py"
Cohesion: 0.13
Nodes (35): config(), credentials(), FakeClient, FakeStore, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test…, The status file holds only the latest state, and these services write no… (+27 more)

### Community 94 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 95 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 96 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.15
Nodes (12): The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise., Signals, Source, Store, test_a_halt_from_another_process_still_stops_a_running_engine(), test_daily_loss_gate_still_applies_to_the_engine(), test_engine_refuses_to_evaluate_a_strategy_with_no_recorded_validation() (+4 more)

### Community 97 - "test_bits_research.py"
Cohesion: 0.11
Nodes (24): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+16 more)

### Community 98 - "._note"
Cohesion: 0.10
Nodes (20): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), on_connected(), on_disconnected(), on_message(), tick(), confirmed(), guard() (+12 more)

### Community 99 - "SQLiteAgentTranscriptStore"
Cohesion: 0.06
Nodes (44): Connection, Row, test_account_only_reset_preserves_research_and_stop(), decision(), parametrize, Validation must not reject a real account, including a running one., The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is. (+36 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.19
Nodes (11): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+3 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.10
Nodes (30): skipif, notes(), open_drafts(), R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject(), test_concurrent_writers_with_the_same_base_cannot_both_win(), writer() (+22 more)

### Community 102 - "_download_with_retry"
Cohesion: 0.18
Nodes (9): Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., test_data_update_reraises_the_first_transient_failure(), test_data_update_retries_transient_failures(), _download_attempt_subprocess(), _download_with_retry(), Any, One single-shot ``data download`` in a fresh interpreter; returns its result. A… (+1 more)

### Community 103 - "lab.py"
Cohesion: 0.14
Nodes (28): functools, operator, bars(), parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed() (+20 more)

### Community 104 - "CodexResearchClient"
Cohesion: 0.20
Nodes (9): Step 7d - MCP server (only if --mcp flag), test_harness_pins_luna_on_new_and_resumed_calls(), test_resumes_exact_thread_and_enables_native_compaction(), test_session_telemetry_tracks_native_compaction_incrementally(), test_thread_id_persisted_before_next_turn(), CodexResearchClient, Path, Read only numeric usage and native compaction markers, never raw content. The… (+1 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.17
Nodes (19): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+11 more)

### Community 107 - "agent_loop.py"
Cohesion: 0.14
Nodes (19): build_agent_registry(), canary_signal_tool(), _decision_id(), paper_state_tool(), propose_trade_tool(), handler(), Continuous single-agent XAUUSD paper trading loop with a live, visible thinking…, read_market_tool() (+11 more)

### Community 108 - "file_lock"
Cohesion: 0.20
Nodes (12): The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker(), test_file_lock_times_out_instead_of_waiting_forever() (+4 more)

### Community 109 - "child_environment"
Cohesion: 0.28
Nodes (5): test_codex_environment_does_not_inherit_broker_credentials(), test_permission_profile_restricts_tools_to_training_workspace(), child_environment(), permission_arguments(), Deny reads outside the supplied training workspace and Python runtime. These…

### Community 110 - "atomic_write_text"
Cohesion: 0.14
Nodes (22): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+14 more)

### Community 111 - "BitsError"
Cohesion: 0.09
Nodes (26): Evidence anchors, main(), call(), test_http_and_workflow_failures_are_classified(), test_workflow_agent_identity_is_verified(), agent_messages(), BitsClient, BitsError (+18 more)

### Community 112 - "LabStore"
Cohesion: 0.16
Nodes (8): 5. Restart the live view so the new observability is visible, Row counts and stored bytes, so unbounded growth is visible., LabStore, save(), add(), add(), save(), Expire old price-mark results, never actual trade idempotency keys. Monitor…

### Community 113 - "._discover_account"
Cohesion: 0.40
Nodes (8): account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), Authenticate the application, then resolve the demo account and symbol.…, Resolve the demo account and XAUUSD symbol id, then ``done``. Asynchronous,…

### Community 114 - "lab_tools.py"
Cohesion: 0.18
Nodes (23): ast, generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused() (+15 more)

### Community 115 - "fetch_source"
Cohesion: 0.10
Nodes (10): HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), xauusd, NoRedirect, _excerpt_text(), fetch_source() (+2 more)

### Community 116 - "bounded_process"
Cohesion: 0.20
Nodes (6): test_process_timeout_and_output_bound(), test_process_workspace_limit_stops_writer(), test_process_workspace_symlink_is_rejected(), test_successful_shell_cannot_leave_background_writer(), bounded_process(), Drain to disk with a hard runtime and output bound, killing the process group.

### Community 117 - "build_parser"
Cohesion: 0.25
Nodes (8): ArgumentParser, Without this the command exists but nothing runs it, so a hole still sits for…, test_the_heal_command_is_in_the_cli_grammar(), test_update_can_heal_and_the_timer_does(), test_the_raw_retention_command_is_in_the_cli_grammar(), test_the_rebuild_command_is_in_the_cli_grammar(), build_parser(), The complete CLI grammar; also used to publish supported operations.

### Community 118 - "write_status"
Cohesion: 0.22
Nodes (14): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), `monitor_error` used to be assigned and then read by nothing at all., test_monitor_error_and_liveness_are_reported_in_the_heartbeat() (+6 more)

### Community 119 - "pytest"
Cohesion: 0.20
Nodes (16): ctrader_open_api_messages_openapimessages_pb2, pytest, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_feed_matches_account_and_symbol_before_recording(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time() (+8 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.30
Nodes (16): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal(), aligned_returns(), classify_regimes() (+8 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "EngineeringManager"
Cohesion: 0.25
Nodes (9): test_snapshot_expiry_deletes_backend_rows(), _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker. (+1 more)

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.08
Nodes (17): FastAPI, fastapi_responses, fastapi_testclient, inspect, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), test_snapshot_projects_current_agent_and_archived_jobs() (+9 more)

### Community 124 - "test_oauth.py"
Cohesion: 0.21
Nodes (16): response_json(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises(), test_refresh_access_token_returns_pair_with_browser_agent(), fake_urlopen(), test_rejected_grant_raises_oauth_error() (+8 more)

### Community 125 - "evidence_refs"
Cohesion: 0.60
Nodes (5): evidence_refs(), add(), ordered(), walk(), Evidence references named by a (possibly malformed) payload: bounded, safe,…

### Community 126 - "Local audit — 2026-09-24"
Cohesion: 0.22
Nodes (7): Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC, Planner latency (read-only), Recommended next work

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.10
Nodes (20): Architecture, Aurum — Codex Autonomous Trading Lab, Autonomous Agent, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+12 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.15
Nodes (13): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, Datadog Bits operations, graphify, Local agent handoff — completed 2026-09-24 (+5 more)

### Community 132 - ".execute"
Cohesion: 0.36
Nodes (4): Any, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it.

### Community 133 - "types"
Cohesion: 0.25
Nodes (5): test_failed_worker_schedule_rolls_back_without_retry(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), types, release_healthy(), run()

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.22
Nodes (9): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Tools and compute (+1 more)

### Community 135 - "/graphify"
Cohesion: 0.12
Nodes (14): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Usage (+6 more)

### Community 136 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.22
Nodes (9): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Research activity chat — 2026-10-23, Research and automatic deployment, Storage and retention (+1 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 140 - "StoreCorruptError"
Cohesion: 0.33
Nodes (5): 9. Recovering the market-data store, OSError, The newest bar in the store, reading the index column only. `data update` needs…, The store file exists but cannot be parsed. Raised instead of letting pyarrow's…, StoreCorruptError

### Community 141 - "_looping_agent"
Cohesion: 0.33
Nodes (6): _looping_agent(), An agent whose store already shows one file re-read for a whole window., The evidence reached the model's prompt and never reached the operator. On…, A research-progress signal is an alert; it must not stop or block anything. The…, test_heartbeat_publishes_compact_retrieval_loop_evidence(), test_retrieval_loop_evidence_never_gates_a_cycle()

### Community 142 - "ResearchHarness"
Cohesion: 0.15
Nodes (9): quote_valid(), One shared, cost-aware target execution path for prospective and paper runs., A prospective simulation account; never selects or replaces real state., ShadowStore, target_decision(), _open_minutes(), Observation opportunities under the shared New York market session., Observe prospective fills at actual fresh quotes through the same gates. (+1 more)

### Community 143 - "test_lab_retention.py"
Cohesion: 0.60
Nodes (5): store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics()

### Community 144 - "TournamentRunner"
Cohesion: 0.20
Nodes (6): _atomic_json(), _finite(), Path, Consume deterministic experiments without reading the holdout test set., Champion-selection statistic, or ``None`` when a component is undefined.…, TournamentRunner

### Community 145 - "engine_decision_id"
Cohesion: 0.50
Nodes (4): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), Durable identity for one engine decision. Derived from the bar, not from a…

### Community 150 - "_datetime"
Cohesion: 0.12
Nodes (21): Engineering, test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), test_read_only_lab_api_reports_actual_data_and_events(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal(), utc_day(), handler() (+13 more)

### Community 153 - "RecordingPostgres"
Cohesion: 0.20
Nodes (3): PostgresLikeTranscript, psycopg-like connection: one implicit transaction per block, committed or…, RecordingPostgres

### Community 156 - "trendbars_to_frame"
Cohesion: 0.13
Nodes (10): test_trendbar_delta_decoding(), CTraderHistoricalAdapter, Any, Path, Every archived raw page as ``(first_minute, last_minute, path)``, sorted. The…, Which archived pages a minimal cover makes redundant. Deletes nothing. The…, Rebuild the store offline from the archived raw page cache. The archive under…, Import cTrader CSV exports into the normalized historical store. (+2 more)

### Community 157 - "cTrader SDK and protocol review (no broker connection)"
Cohesion: 0.29
Nodes (5): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Order lifecycle and errors — follow-up #15, Position reconciliation — follow-up #16

### Community 158 - "core.py"
Cohesion: 0.31
Nodes (7): test_backtest(), campaign(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 159 - "_validate_json"
Cohesion: 0.33
Nodes (4): RuntimeError, Validate the small, explicit JSON-schema subset used for tool boundaries., ToolExecutionError, _validate_json()

### Community 162 - "graphify reference: extra exports and benchmark"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 163 - "demo_accounts"
Cohesion: 0.20
Nodes (11): account(), An unclassified account is not a demo account. ``isLive`` is a proto3 optional…, The discriminator has to work on the actual SDK message, not just dicts., test_demo_accounts_empty_when_all_live(), test_demo_accounts_excludes_a_dict_without_the_flag(), test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo(), test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account(), demo_accounts() (+3 more)

### Community 167 - "_rewritten_env"
Cohesion: 0.40
Nodes (5): _env_key(), _env_value(), Key name of an env assignment, tolerating a leading ``export`` and quotes.…, The whole env file with ``updates`` applied, preserving comments and order. A…, _rewritten_env()

## Knowledge Gaps
- **169 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+164 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1126 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `ConfirmedBreakoutCanarySource`, `/graphify`, `test_ml.py`, `cli.py`, `StoreCorruptError`, `ResearchHarness`, `test_agent_loop.py`, `pandas`, `_datetime`, `CTraderAuthError`, `trendbars_to_frame`, `TournamentDataset`, `test_retention.py`, `test_automation.py`, `ExecutionConfig`, `EngineConfig`, `test_data.py`, `test_bits_capabilities.py`, `AgentTools`, `LiveFeedUnavailable`, `main`, `test_live_feed.py`, `agent_loop.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `cli.py`, `ResearchHarness`, `test_session_reset.py`, `test_agent_loop.py`, `test_agent_view.py`, `_datetime`, `PaperDecision`, `test_demo_execution.py`, `test_lab.py`, `InMemoryAgentTranscriptStore`, `.__init__`, `test_demo_runner.py`, `Any`, `CTraderVolumeConversion`, `paper_from_env`, `create_app`, `ContinuousAgentRunner`, `EngineConfig`, `data_heal`, `test_engine_loop.py`, `setup`, `main`, `PaperTradingEngine`, `HistoricalDataStore`, `PaperToCTraderDemoCoordinator`, `SQLiteAgentTranscriptStore`, `lab.py`, `agent_loop.py`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `SQLiteAgentTranscriptStore` connect `SQLiteAgentTranscriptStore` to `test_lab.py`, `test_bits_runner.py`, `test_bits_memory_drafts.py`, `agent_loop.py`, `cli.py`, `PaperTrading`, `atomic_write_text`, `BitsError`, `canonical_json`, `test_lab_retention.py`, `test_bits_capabilities.py`, `test_session_reset.py`, `test_agent_view.py`, `main`, `BitsStore`, `setup`, `EngineeringManager`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ExperimentRegistry` (e.g. with `R3 — P1: make experiment continuity work with the deployed backend` and `AdaptiveSearch`) actually correct?**
  _`ExperimentRegistry` has 12 INFERRED edges - model-reasoned connections that need verification._