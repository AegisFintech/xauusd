# Graph Report - xauusd-db-release  (2026-10-24)

## Corpus Check
- 201 files · ~200,868 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .service 9, (none) 7, .timer 3)

## Summary
- 3807 nodes · 10632 edges · 183 communities (156 shown, 27 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 557 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4601ff18`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_ctrader_auth.py
- test_autonomous_harness.py
- main
- dashboard.py
- test_bits_runner.py
- ExperimentRegistry
- InMemoryCTraderDemoStore
- ConfirmedBreakoutCanarySource
- MemoryRegistry
- test_bits_capabilities.py
- CTraderDemoAdapter
- test_ml.py
- bits.py
- PaperTrading
- ImprovementLedger
- research_program.py
- SQLitePaperTradingStore
- Any
- test_agent_loop.py
- firecrawl_research.py
- RemoteComputeBridge
- test_agent_view.py
- StrategySpec
- SecretFilter
- XAUUSD discovery, incident, quantitative, and scaling audit
- create_app
- CTraderAuthError
- OpenAICompatiblePlanner
- state_backup.py
- test_demo_execution.py
- test_oauth.py
- CodexResearchClient
- EngineeringManager
- test_lab.py
- setup
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- test_tournament_data.py
- ShadowTradingReadiness
- cli.py
- BitsStore
- test_strategy_proposals.py
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
- canonical_json
- core.py
- restart_policy
- TournamentRunner
- ExecutionConfig
- ContinuousAgentRunner
- synthetic_bars
- PaperToCTraderDemoCoordinator
- CTraderDemoStore
- atomic_write_json
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
- test_data.py
- opencode.json
- EngineConfig
- .__init__
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- fetch_source
- AgentTools
- memory_registry.py
- test_agent_daily.py
- test_cli.py
- .write_notes
- ResearchHarness
- PaperTradingEngine
- closed_bar
- CTraderVolumeConversion
- LiveBarFeed
- LabStore
- pytest
- bits_capabilities.py
- test_bits_research.py
- ._note
- SQLiteAgentTranscriptStore
- LiveFeedConfig
- test_bits_memory_drafts.py
- .run
- lab_strategy.py
- test_ctrader_demo.py
- test_weekly_report.py
- agent_controller
- bounded_process
- ExperimentSpec
- test_dashboard.py
- atomic_write_text
- BitsError
- types
- BitsMemory
- lab_tools.py
- Any
- bits_memory.py
- pandas
- write_status
- data_heal
- portfolio_research.py
- .send
- file_lock
- test_lab_dashboard.py
- trendbars_to_frame
- evidence_refs
- README.md
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- NotesRejected
- _datetime
- Persistent open-ended Codex agent
- bits_runner.py
- test_offline.py
- Codex autonomous trading lab
- Datadog Bits connection
- Harness cleanup and improvement checklist — 2026-10-24
- _bars
- test_bits.py
- test_session_reset.py
- api_status
- CockroachAgentTranscriptStore
- DataConfig
- InMemoryHarnessStore
- attach_routes
- harness-outcomes-plan-2026-10-23.md
- ShadowStore
- Research and measured self-improvement implementation plan
- RecordingPostgres
- run
- timestamp
- CockroachHarnessStore
- TournamentDataset
- HistoricalDataStore
- transition
- _download_with_retry
- AgentTranscriptStore
- shell_environment
- Research program and measured improvement
- StateTransaction
- sklearn_base
- tarfile
- minimal_manifest
- ._discover_account
- graphify reference: extra exports and benchmark
- test_service_like_shell_runs_documented_examples_without_profile
- build_parser
- test_lab_retention.py
- Database maintenance and seven-day log rotation
- paper_from_env
- test_demo_automation_paper_only_skips_broker_dependencies
- live
- export
- test_sandbox_tests_return_bounded_feedback_and_clean_environment
- _command_failure
- state_db_path
- tool_state
- test_in_memory_reconcile_is_scoped_to_the_caller_family
- demo_feed_environment

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `MemoryRegistry` - 89 edges
3. `setup()` - 81 edges
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
- `Research continuity and output retrieval` --references--> `weekly_bars()`  [INFERRED]
  docs/legacy-project-history.md → xauusd/session_calendar.py
- `Clean lease-drained saturation benchmark — 2026-08-20` --references--> `completed()`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → tests/test_adaptive_search.py

## Import Cycles
- None detected.

## Communities (183 total, 27 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.07
Nodes (36): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC (+28 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.29
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "main"
Cohesion: 0.08
Nodes (26): test_bits_notes_only_does_not_repeat_history(), test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_status_reports_paper_only_flag(), test_state_integrity_backup_restore_round_trip(), test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path() (+18 more)

### Community 3 - "dashboard.py"
Cohesion: 0.12
Nodes (32): asyncio, fastapi_security, get, HTTPBasicCredentials, plotly_graph_objects, secrets, test_dashboard_registry_requires_database_url_and_never_passes_a_path(), authenticate() (+24 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.09
Nodes (32): _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted., `monitor_error` used to be assigned and then read by nothing at all. (+24 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.18
Nodes (5): ExperimentStatus, ExperimentRegistry, Any, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool.

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.16
Nodes (21): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+13 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.10
Nodes (16): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_postgres_connection_uses_configured_read_committed() (+8 more)

### Community 9 - "test_bits_capabilities.py"
Cohesion: 0.20
Nodes (22): R2 — P1: capability discovery failure must remain visible, fake_tool(), The shell-job environment is discoverable from the environment jobs really get., Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_invalid_declared_directories_are_configuration_errors_not_missing_tools(), test_manifest_never_includes_environment_values(), test_manifest_publishes_a_bounded_repository_search() (+14 more)

### Community 10 - "CTraderDemoAdapter"
Cohesion: 0.16
Nodes (13): test_open_api_transport_fails_reconciliation_on_an_error_reply(), event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending() (+5 more)

### Community 11 - "test_ml.py"
Cohesion: 0.12
Nodes (25): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined() (+17 more)

### Community 12 - "bits.py"
Cohesion: 0.17
Nodes (14): 2. Publish the Datadog workflow message stream (required for the thinking panel), agent_messages(), _collect_messages(), message_fingerprint(), Any, Datadog workflow transport and the strict, correlated xauusd/1 boundary., Validate the agent's self-questioning about its own decision. This is the bot…, Flatten a message content value to plain text, whatever shape it arrives in.… (+6 more)

### Community 13 - "PaperTrading"
Cohesion: 0.09
Nodes (51): test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_once_reports_a_refused_restart(), test_paper_start_overrides_operator_stop(), test_paper_stop_persists_kill_switch(), test_snapshot_projects_current_agent_and_archived_jobs(), test_shadow_and_paper_share_target_prices_and_flatten_reversals(), test_shadow_risk_monitor_sees_intraminute_loss_and_keeps_stop() (+43 more)

### Community 14 - "ImprovementLedger"
Cohesion: 0.13
Nodes (18): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+10 more)

### Community 15 - "research_program.py"
Cohesion: 0.12
Nodes (33): plan(), test_compact_context_pages_full_design_without_truncating_evidence(), test_completed_findings_accumulate_lessons_without_recounting(), test_discovery_insights_require_real_retrieval_and_do_not_claim_availability(), test_family_rejections_drive_pivot_without_resetting_learning(), test_open_plan_capacity_and_variant_budgets_are_bounded(), test_plan_and_source_retention_keep_compact_provenance_and_lifetime_counts(), test_plan_is_immutable_deduplicated_and_cannot_close_without_findings() (+25 more)

### Community 16 - "SQLitePaperTradingStore"
Cohesion: 0.15
Nodes (10): Connection, Row, test_sqlite_integrity_check_detects_corruption(), test_sqlite_paper_store_integrity_check_reports_ok(), _connect(), _now(), Any, Close the caller's own interrupted runs left 'running' by a killed process.… (+2 more)

### Community 17 - "Any"
Cohesion: 0.14
Nodes (18): build_reconcile_request(), CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded() (+10 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.10
Nodes (40): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), A ticking agent must not be served as stopped. The engine's startup reconcile…, refresh_config(), refresh_runner() (+32 more)

### Community 19 - "firecrawl_research.py"
Cohesion: 0.15
Nodes (18): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+10 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (23): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+15 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.06
Nodes (33): _feed(), _harness_client(), paper_trading(), fixture, parametrize, A non-SQLite transcript store must not take the panel down., The exact 2026-10-08 outage: bar_write_failed, session open, no alert. The…, A feed that is alive and healthy but no longer persisting bars. (+25 more)

### Community 22 - "StrategySpec"
Cohesion: 0.12
Nodes (30): An empty training window must fail loudly, not look like a negative result., The embargo must reach the report, not just the helper. `walk_forward_splits`…, The negative path was never asserted, which is why several real defects…, A 30-bar rolling feature reaches across the split boundary. The last…, test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_chronological_splits_are_ordered_and_disjoint() (+22 more)

### Community 23 - "SecretFilter"
Cohesion: 0.08
Nodes (29): action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes…, A failed preview is observability, and observability must not break the job., A post-spawn exception must not strand the row as `running` forever. `state`… (+21 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "create_app"
Cohesion: 0.09
Nodes (26): frame(), read(), agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., create_app(), data_update_status(), harness(), health() (+18 more)

### Community 26 - "CTraderAuthError"
Cohesion: 0.14
Nodes (19): test_data_update_does_not_retry_auth_errors(), unauthorized(), downloader_config(), validate() is no longer a one-time check performed only by from_env(). The…, test_download_does_not_retry_non_token_auth_error(), fake_fetch(), test_download_does_not_retry_without_a_refresh_token(), test_download_refreshes_once_then_retries_in_a_fresh_process() (+11 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.24
Nodes (10): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError (+2 more)

### Community 28 - "state_backup.py"
Cohesion: 0.21
Nodes (20): decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+12 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.15
Nodes (21): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+13 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.06
Nodes (47): PathLike, Market Data & Authentication, FakeResponse, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent… (+39 more)

### Community 31 - "CodexResearchClient"
Cohesion: 0.20
Nodes (9): Step 7d - MCP server (only if --mcp flag), test_harness_pins_luna_on_new_and_resumed_calls(), test_resumes_exact_thread_and_enables_native_compaction(), test_session_telemetry_tracks_native_compaction_incrementally(), test_thread_id_persisted_before_next_turn(), CodexResearchClient, Path, Read only numeric usage and native compaction markers, never raw content. The… (+1 more)

### Community 32 - "EngineeringManager"
Cohesion: 0.25
Nodes (8): _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker., _safe()

### Community 33 - "test_lab.py"
Cohesion: 0.12
Nodes (29): parametrize, qualified_candidate(), quote(), test_codex_contract_rejects_unknown_fields_and_overlarge_requests(), test_durable_job_recovery_never_replays(), test_event_and_memory_storage_is_bounded(), test_evidence_relations_are_checked_beyond_digest(), test_forward_coverage_rejects_short_observation_despite_fixed_deadline() (+21 more)

### Community 34 - "setup"
Cohesion: 0.17
Nodes (22): test_compaction_also_refuses_deactivating_or_unverified_units(), test_compaction_refuses_a_running_database_service(), test_legacy_row_count_pruning_preserves_unknown_jobs(), test_offline_compaction_reclaims_pages_without_changing_account_or_learning(), test_old_run_logs_expire_but_active_runs_survive(), test_old_trade_using_monitor_prefix_and_unknown_jobs_never_expire(), test_seven_day_rotation_preserves_learning_active_work_and_trade_keys(), test_terminal_job_output_expires_but_identity_and_references_survive() (+14 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.12
Nodes (15): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+7 more)

### Community 37 - "test_tournament_data.py"
Cohesion: 0.09
Nodes (29): dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version…, A freeze killed mid-write must not hang the next one, nor quietly pass., A backtester or cost change must invalidate stored results. Both were hardcoded…, test_a_version_directory_with_no_manifest_fails_loudly() (+21 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 39 - "cli.py"
Cohesion: 0.11
Nodes (38): base64, collections, concurrent_futures, csv, dataclasses, datetime, dotenv, gzip (+30 more)

### Community 40 - "BitsStore"
Cohesion: 0.12
Nodes (12): Operations, 5. Restart the live view so the new observability is visible, memory(), fixture, memory(), fixture, BitsStore, Uses the same connection selected for the application's transcript store. (+4 more)

### Community 41 - "test_strategy_proposals.py"
Cohesion: 0.10
Nodes (13): Portfolio and regime research — 2026-08-21, test_portfolio_run_reads_validation_only(), test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), PortfolioResearch, Path (+5 more)

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 49 - "test_retention.py"
Cohesion: 0.08
Nodes (51): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(), archive(), _local_backups() (+43 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.06
Nodes (36): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+28 more)

### Community 51 - "InMemoryAgentTranscriptStore"
Cohesion: 0.07
Nodes (17): The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., `limit` alone does not bound a response. A shell-job step carries a captured…, The health endpoint is the observability surface; it must not raise. An…, The monitor's status string alone was never enough. A monitor that died after…, test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_alerts_on_a_stale_or_dead_position_monitor(), test_health_names_the_paths_a_retrieval_loop_keeps_reading() (+9 more)

### Community 52 - "test_automation.py"
Cohesion: 0.09
Nodes (31): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+23 more)

### Community 53 - "test_ctrader_reconciliation.py"
Cohesion: 0.21
Nodes (13): copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+5 more)

### Community 54 - "canonical_json"
Cohesion: 0.07
Nodes (32): test_account_only_reset_preserves_research_and_stop(), Explicit operator-only, flat paper account rebase; no research reset., rebase(), handler(), args_timeout(), NormalizedDecision, Any, Evaluate paper risk first; broker submission only happens behind all gates. (+24 more)

### Community 55 - "core.py"
Cohesion: 0.31
Nodes (7): test_backtest(), campaign(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 56 - "restart_policy"
Cohesion: 0.14
Nodes (14): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+6 more)

### Community 57 - "TournamentRunner"
Cohesion: 0.15
Nodes (12): Dependence-aware bootstrap validation — 2026-08-21, setup_runner(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition(), _finite(), Path (+4 more)

### Community 58 - "ExecutionConfig"
Cohesion: 0.15
Nodes (26): main(), bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,…, Zero is a real value; a metric that cannot be computed must say so. Reporting… (+18 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.15
Nodes (14): Event, test_redact_bounds_untrusted_content(), _assistant_step(), ContinuousAgentRunner, Any, BaseException, Family-scoped mirror of the SQL stores: never close another family's run., Display-friendly assistant step: parsed action plus the model's plain-English… (+6 more)

### Community 60 - "synthetic_bars"
Cohesion: 0.18
Nodes (19): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+11 more)

### Community 61 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.12
Nodes (14): The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise., The 2026-10-05 sequence: a fresh engine, no halt anywhere, still no trade., Signals, Store, test_a_halt_from_another_process_still_stops_a_running_engine(), test_engine_does_nothing_when_the_signal_is_flat(), test_engine_refuses_to_evaluate_a_strategy_with_no_recorded_validation() (+6 more)

### Community 62 - "CTraderDemoStore"
Cohesion: 0.14
Nodes (3): CTraderDemoStore, CTraderTransport, Protocol

### Community 63 - "atomic_write_json"
Cohesion: 0.15
Nodes (20): ctrader_open_api_messages_openapimessages_pb2, sqlite3, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_feed_matches_account_and_symbol_before_recording(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time() (+12 more)

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

### Community 72 - "BitsAgentRunner"
Cohesion: 0.11
Nodes (13): error_details(), excerpt(), BaseException, Payload-free classification of an exception for events and heartbeats.…, guidance_revision(), BitsAgentRunner, Any, Retrieval-loop evidence for the heartbeat, which this file writes every tick. A… (+5 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.12
Nodes (25): Delivery order after this merge, Merge review — 2026-09-25, baseline `cba22b2`, R1 — P0: do not lose pending findings when memory is rewritten, R3 — P1: make experiment continuity work with the deployed backend, Runtime adoption is still pending, at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from… (+17 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.08
Nodes (43): errno, demo_env(), frame(), minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.…, `data update` starts from the newest bar, so a hole in the middle is permanent.… (+35 more)

### Community 77 - "EngineConfig"
Cohesion: 0.15
Nodes (12): An oversized proposal must be visibly refused, not silently trimmed. Clamping…, test_engine_cannot_exceed_max_position(), test_engine_config_rejects_unbounded_values(), test_engine_does_not_clamp_an_oversized_proposal(), test_engine_status_reports_the_running_process_not_a_phantom(), _build_engine(), engine_controller(), Construct the deterministic engine from the same stores the agent uses. (+4 more)

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
Nodes (34): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, A restart re-proposes the same decision for the same bar, and the store's…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case. (+26 more)

### Community 82 - "fetch_source"
Cohesion: 0.09
Nodes (10): HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), xauusd, NoRedirect, _excerpt_text(), fetch_source() (+2 more)

### Community 83 - "AgentTools"
Cohesion: 0.16
Nodes (19): Store, test_dependency_install_requires_pins(), test_dependency_install_targets_scratch_only(), test_domain_configuration(), test_fetch_rejects_private_dns(), test_market_observe_excludes_frozen_and_forming_bars(), test_market_observe_without_frozen_boundary_reveals_no_history(), test_remote_job_identity_is_action_derived() (+11 more)

### Community 86 - "test_agent_daily.py"
Cohesion: 0.24
Nodes (5): test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal(), utc_day()

### Community 87 - "test_cli.py"
Cohesion: 0.20
Nodes (19): DemoTransport, _isolated_bits_state(), no_broker(), _run_cli(), stopped_demo_adapter(), test_bits_capabilities_check_and_stored_manifest(), test_bits_capabilities_direct_discovery_exception_still_exits_nonzero(), test_bits_capabilities_stored_check_rejects_a_stale_manifest() (+11 more)

### Community 88 - ".write_notes"
Cohesion: 0.22
Nodes (10): apply(), apply(), _close(), notes_digest(), _now(), One locked transaction over the notes and the drafts; any failure rolls back…, Replace the notes atomically, closing only the drafts named in ``resolves``.…, CLI write path: unparseable input is retained as text when it is safe to keep. (+2 more)

### Community 89 - "ResearchHarness"
Cohesion: 0.07
Nodes (26): Harness maintenance — 2026-10-24, test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_explicit_evidence_pages_and_source_excerpts_survive_context_compaction(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory() (+18 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.16
Nodes (12): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+4 more)

### Community 91 - "closed_bar"
Cohesion: 0.20
Nodes (6): test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 92 - "CTraderVolumeConversion"
Cohesion: 0.12
Nodes (14): test_demo_factory_binds_authoritative_paper_exposure(), test_volume_policy_from_metadata(), _ctrader_demo_adapter(), expected_volume(), _demo_automation_start(), _paper_to_demo_coordinator(), Explicit operator override for the demo execution kill switch; paper and the…, CTraderVolumeConversion (+6 more)

### Community 93 - "LiveBarFeed"
Cohesion: 0.12
Nodes (37): config(), credentials(), FakeClient, FakeStore, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test…, The status file holds only the latest state, and these services write no… (+29 more)

### Community 94 - "LabStore"
Cohesion: 0.17
Nodes (7): test_snapshot_expiry_deletes_backend_rows(), run(), LabStore, save(), add(), add(), save()

### Community 95 - "pytest"
Cohesion: 0.09
Nodes (21): ImportError, importlib, pytest, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 96 - "bits_capabilities.py"
Cohesion: 0.14
Nodes (20): platform, shlex, cli_prefix(), data_access(), _error_code(), _fallback(), observed_view(), operations() (+12 more)

### Community 97 - "test_bits_research.py"
Cohesion: 0.12
Nodes (24): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+16 more)

### Community 98 - "._note"
Cohesion: 0.08
Nodes (24): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), heartbeat(), on_connected(), on_disconnected(), on_message(), tick(), confirmed() (+16 more)

### Community 99 - "SQLiteAgentTranscriptStore"
Cohesion: 0.09
Nodes (30): The deterministic engine writes to the same `agent_runs` table. Taking the…, test_status_and_health_select_the_agent_run_not_a_newer_engine_run(), decision(), parametrize, Validation must not reject a real account, including a running one., The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is., The owner of a run is the only authority on whether it is live. (+22 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.12
Nodes (17): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+9 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.16
Nodes (26): skipif, notes(), open_drafts(), R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject(), test_concurrent_writers_with_the_same_base_cannot_both_win(), writer() (+18 more)

### Community 102 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 103 - "lab_strategy.py"
Cohesion: 0.16
Nodes (25): operator, bars(), parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate() (+17 more)

### Community 104 - "test_ctrader_demo.py"
Cohesion: 0.08
Nodes (35): adapter(), FakeClient, ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call() (+27 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.16
Nodes (20): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+12 more)

### Community 106 - "agent_controller"
Cohesion: 0.10
Nodes (21): parametrize, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An…, test_agent_config_rejects_non_finite_limits(), test_demo_automation_requires_explicit_positive_volume(), _positive_float(), LocalHistoricalMarketDataSource, Expose the final persisted, normalized M1 bar as a market observation., agent_controller() (+13 more)

### Community 107 - "bounded_process"
Cohesion: 0.13
Nodes (11): test_process_timeout_and_output_bound(), test_process_workspace_limit_stops_writer(), test_process_workspace_symlink_is_rejected(), test_successful_shell_cannot_leave_background_writer(), test_codex_environment_does_not_inherit_broker_credentials(), test_permission_profile_restricts_tools_to_training_workspace(), bounded_process(), Drain to disk with a hard runtime and output bound, killing the process group. (+3 more)

### Community 108 - "ExperimentSpec"
Cohesion: 0.27
Nodes (13): E. Current 50,000-scenario architecture and benchmark, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix(), ExperimentSpec, from_strategy(), candidate_specs() (+5 more)

### Community 109 - "test_dashboard.py"
Cohesion: 0.19
Nodes (9): setup_files(), test_dashboard_reads_latest_run_and_equity(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature(), test_status_remains_readable_without_generated_tournament_dataset(), test_system_metrics_calculate_network_rate(), test_system_metrics_include_capacity_network_and_services() (+1 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.14
Nodes (22): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+14 more)

### Community 111 - "BitsError"
Cohesion: 0.09
Nodes (24): Delivery and operational boundaries, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit, P1 — Persist reproducible experiments and separate live signals, P1 — Separate monitoring cadence from meaningful agent reviews (+16 more)

### Community 112 - "types"
Cohesion: 0.32
Nodes (5): test_failed_worker_schedule_rolls_back_without_retry(), test_research_advisories_do_not_disable_safe_software_releases(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), types, release_healthy()

### Community 113 - "BitsMemory"
Cohesion: 0.35
Nodes (4): BitsMemory, _note_sources(), _notes_base(), A specific next task for unresolved drafts; not a new research cycle.

### Community 114 - "lab_tools.py"
Cohesion: 0.18
Nodes (23): ast, generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused() (+15 more)

### Community 115 - "Any"
Cohesion: 0.15
Nodes (5): HarnessStore, Any, Protocol, RuntimeError, ToolExecutionError

### Community 116 - "bits_memory.py"
Cohesion: 0.19
Nodes (20): _age_seconds(), apply(), _brief(), _check_categories(), _check_entry(), check_notes(), _empty_drafts(), _is_current_notes() (+12 more)

### Community 117 - "pandas"
Cohesion: 0.18
Nodes (16): argparse, numpy, pandas, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., sklearn_metrics (+8 more)

### Community 118 - "write_status"
Cohesion: 0.26
Nodes (14): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), bits_alerts() (+6 more)

### Community 119 - "data_heal"
Cohesion: 0.24
Nodes (12): _heal_args(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _store_with_windows(), test_data_heal_defers_a_window_that_does_not_fit_the_budget(), test_data_heal_downloads_an_interior_window(), test_data_heal_dry_run_never_contacts_the_broker() (+4 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.30
Nodes (16): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal(), aligned_returns(), classify_regimes() (+8 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "file_lock"
Cohesion: 0.18
Nodes (16): The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker(), test_file_lock_times_out_instead_of_waiting_forever() (+8 more)

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.11
Nodes (8): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), test_statistics_counts_retained_evidence_without_claiming_success(), _age(), Counts only bounded retained evidence; never infer remote execution success., retained_statistics()

### Community 124 - "trendbars_to_frame"
Cohesion: 0.09
Nodes (18): 10. Related documents, 1. What was built and why, 3. Enable the live data feed, 4. Enable the deterministic engine, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback, 9. Recovering the market-data store (+10 more)

### Community 125 - "evidence_refs"
Cohesion: 0.60
Nodes (5): evidence_refs(), add(), ordered(), walk(), Evidence references named by a (possibly malformed) payload: bounded, safe,…

### Community 126 - "README.md"
Cohesion: 0.15
Nodes (8): Bits agent instructions, Autonomous Agent, Legacy Datadog planner operations, Delivery Stages, Historical delivery and deployment notes, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval, Research notes (`bits-memory`, schema `xauusd.notes/1`)

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.10
Nodes (21): Active Codex agent, Architecture, Aurum — Codex Autonomous Trading Lab, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+13 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.14
Nodes (14): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, Database retention — 2026-10-24, graphify, Local agent handoff — completed 2026-09-24 (+6 more)

### Community 132 - "NotesRejected"
Cohesion: 0.18
Nodes (10): _check_draft_ids(), issue(), NotesRejected, parse_notes_input(), One payload-free validation problem. ``retry`` says what makes a retry useful., Structured rejection of a notes payload; it never carries the payload., Strictly parse CLI input; malformed JSON is reported by line and column only., bits_memory_command() (+2 more)

### Community 133 - "_datetime"
Cohesion: 0.09
Nodes (41): Engineering, functools, threading, _archive(), Independent exploratory paper accounts; never a promotion or broker path., tick(), canary_signal_tool(), handler() (+33 more)

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.18
Nodes (10): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Research continuity and maintenance — 2026-10-24 (+2 more)

### Community 135 - "bits_runner.py"
Cohesion: 0.10
Nodes (28): contextlib, fcntl, html, html_parser, ipaddress, re, Two-invocation, no-trading smoke test of Bits -> shell -> Bits. Run from the…, selectors (+20 more)

### Community 136 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.18
Nodes (10): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Operating model, Research activity chat — 2026-10-23, Research and automatic deployment (+2 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "Harness cleanup and improvement checklist — 2026-10-24"
Cohesion: 0.40
Nodes (4): Audit findings, Broker smoke shutdown follow-up, Harness cleanup and improvement checklist — 2026-10-24, Verification and deployment log

### Community 140 - "_bars"
Cohesion: 0.16
Nodes (13): _bars(), Three valid, non-overlapping minutes, shifted so writers never collide., A shared temporary name lets two writers interleave into one inode. That is how…, Read-merge-swap has to be exclusive, and a wedged writer must not be skipped.…, The invariant the corruption broke: every writer's bars survive, and it reads., One value must not cost the whole frame. `data update` runs four times a day on…, test_concurrent_writers_leave_a_readable_complete_store(), append() (+5 more)

### Community 141 - "test_bits.py"
Cohesion: 0.33
Nodes (15): envelope(), interrogation(), parametrize, shell_action(), test_bare_string_evidence_is_one_reference(), test_errors_carry_stable_codes_and_only_safe_text(), test_interrogation_is_durable_and_optional(), test_interrogation_stream_stays_bounded() (+7 more)

### Community 142 - "test_session_reset.py"
Cohesion: 0.24
Nodes (11): seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), AgentAlreadyRunning, AgentLock, Single process per container; the lock is runtime coordination, not state., bits_recover(), lab_controller() (+3 more)

### Community 143 - "api_status"
Cohesion: 0.34
Nodes (14): adaptive_status(), api_status(), codex_status(), distributed_status(), live_snapshot(), portfolio_status(), proposal_status(), Path (+6 more)

### Community 144 - "CockroachAgentTranscriptStore"
Cohesion: 0.19
Nodes (4): CockroachAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row; see the SQLite store.

### Community 145 - "DataConfig"
Cohesion: 0.18
Nodes (14): pyarrow_parquet, An interior hole is a smaller problem than a refresh reported as failed. The…, test_update_reports_a_failed_heal_without_failing_the_update(), test_dashboard_uses_metadata_and_bounded_tail_not_store_read(), DataConfig, chart(), _data(), chart_bars() (+6 more)

### Community 147 - "attach_routes"
Cohesion: 0.24
Nodes (9): FastAPI, fastapi_responses, inspect, attach_routes(), lab_chart(), lab_events(), lab_snapshot(), resolve() (+1 more)

### Community 149 - "ShadowStore"
Cohesion: 0.19
Nodes (12): test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), test_probation_after_outage_rejects_profitable_but_stale_observations(), retire() (+4 more)

### Community 150 - "Research and measured self-improvement implementation plan"
Cohesion: 0.25
Nodes (7): Acceptance criteria, Delivery checklist, Deployment procedure, Final verification and deployment, Implementation evidence so far, Objective and boundaries, Research and measured self-improvement implementation plan

### Community 151 - "RecordingPostgres"
Cohesion: 0.20
Nodes (3): PostgresLikeTranscript, psycopg-like connection: one implicit transaction per block, committed or…, RecordingPostgres

### Community 153 - "timestamp"
Cohesion: 0.12
Nodes (29): test_improvement_cannot_claim_old_release_as_new_work(), test_inspection_and_failed_remote_work_are_not_progress(), test_outcome_requires_existing_successful_evidence_and_deduplicates(), test_measured_bottleneck_seeds_one_backlog_item_and_preserves_baseline(), test_missing_baseline_cannot_be_claimed_and_inference_history_is_bounded(), test_observed_regression_cannot_be_labeled_improved(), test_recent_metric_window_does_not_bias_toward_retained_old_unknowns(), test_release_success_does_not_imply_measured_improvement() (+21 more)

### Community 155 - "TournamentDataset"
Cohesion: 0.28
Nodes (6): frame_digest(), DataFrame, Path, Wait for a concurrent freeze of the same version to publish its manifest.…, Hash canonical timestamps, schema, and values independent of Parquet bytes., TournamentDataset

### Community 156 - "HistoricalDataStore"
Cohesion: 0.09
Nodes (18): Historical deployment state — verified 2026-10-05, Interpreter guard for subcommands, test_store_rejects_invalid_ohlc(), test_store_roundtrip(), CTraderHistoricalAdapter, HistoricalDataStore, DataFrame, Path (+10 more)

### Community 157 - "transition"
Cohesion: 0.33
Nodes (6): test_counter_update_rolls_back_with_owning_state_transaction(), test_counters_survive_detail_eviction_and_ignore_duplicate_updates(), Small transactional counters; detailed evidence may expire independently., Called inside the transaction that writes the owning row., snapshot(), transition()

### Community 158 - "_download_with_retry"
Cohesion: 0.18
Nodes (9): Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., test_data_update_reraises_the_first_transient_failure(), test_data_update_retries_transient_failures(), _download_attempt_subprocess(), _download_with_retry(), Any, One single-shot ``data download`` in a fresh interpreter; returns its result. A… (+1 more)

### Community 160 - "shell_environment"
Cohesion: 0.20
Nodes (9): Datadog Bits operations, test_shell_environment_keeps_the_latest_refreshed_tokens(), test_shell_path_prepends_service_interpreter_and_declared_directories(), _in_virtualenv(), _prepare(), The environment every Bits shell job runs with., Deterministic search PATH: service virtualenv, declared extras, then inherited…, shell_environment() (+1 more)

### Community 161 - "Research program and measured improvement"
Cohesion: 0.25
Nodes (7): Decision cycle, Discovery and sources, Improvement measurement, Preregistration and execution, Release readiness and visibility, Research program and measured improvement, Storage and limitations

### Community 162 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 165 - "minimal_manifest"
Cohesion: 0.22
Nodes (9): test_failed_discovery_is_explicit_in_every_view(), test_observed_missing_executables_are_bounded_and_counted(), minimal_manifest(), _now(), Bounded, persistent record of executables a real job could not find., Tools that were not probed: availability is unknown, never implicitly healthy., Used when discovery itself fails: diagnostics must never block the agent, nor…, record_observed() (+1 more)

### Community 166 - "._discover_account"
Cohesion: 0.21
Nodes (11): app_failed(), account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), The broker client, created once. Injected through ``client_factory`` so the… (+3 more)

### Community 167 - "graphify reference: extra exports and benchmark"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 168 - "test_service_like_shell_runs_documented_examples_without_profile"
Cohesion: 0.29
Nodes (7): parametrize, Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, test_missing_executables_are_detected_from_shell_messages(), test_service_like_shell_runs_documented_examples_without_profile(), wait(), missing_executables(), Names bash (or /usr/bin/env) reported as not found in a completed job's stderr.

### Community 169 - "build_parser"
Cohesion: 0.18
Nodes (11): ArgumentParser, Bits shell environment (`bits-capabilities`), test_every_published_operation_is_a_real_cli_command(), Without this the command exists but nothing runs it, so a hole still sits for…, test_the_heal_command_is_in_the_cli_grammar(), test_update_can_heal_and_the_timer_does(), test_the_raw_retention_command_is_in_the_cli_grammar(), test_the_rebuild_command_is_in_the_cli_grammar() (+3 more)

### Community 170 - "test_lab_retention.py"
Cohesion: 0.60
Nodes (5): store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics()

### Community 171 - "Database maintenance and seven-day log rotation"
Cohesion: 0.40
Nodes (4): Database maintenance and seven-day log rotation, Initial deployment, One-time physical compaction, Scheduled behavior

### Community 172 - "paper_from_env"
Cohesion: 0.40
Nodes (5): test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store(), paper_from_env(), _positive_env_float(), Single paper-trading entry point shared by the CLI and the live view.

### Community 175 - "live"
Cohesion: 0.40
Nodes (5): middleware, Request, live(), events(), request_log()

### Community 176 - "export"
Cohesion: 0.50
Nodes (3): graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), export()

### Community 178 - "_command_failure"
Cohesion: 0.50
Nodes (4): bits_job_page(), _command_failure(), Exception, Classified, payload-free failure: exception text and arguments are never echoed.

### Community 180 - "tool_state"
Cohesion: 0.67
Nodes (3): tool_view(), available, missing or unknown; manifests from the previous release lack an…, tool_state()

## Knowledge Gaps
- **194 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+189 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1172 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `main`, `ConfirmedBreakoutCanarySource`, `bits_runner.py`, `test_ml.py`, `test_session_reset.py`, `DataConfig`, `test_agent_loop.py`, `StrategySpec`, `CTraderAuthError`, `TournamentDataset`, `test_lab.py`, `setup`, `cli.py`, `test_retention.py`, `test_automation.py`, `ExecutionConfig`, `atomic_write_json`, `test_data.py`, `EngineConfig`, `AgentTools`, `test_cli.py`, `LiveBarFeed`, `bits_capabilities.py`, `LiveFeedConfig`, `agent_controller`, `trendbars_to_frame`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `SQLiteAgentTranscriptStore` connect `SQLiteAgentTranscriptStore` to `main`, `test_bits_runner.py`, `_datetime`, `bits_runner.py`, `test_bits_capabilities.py`, `PaperTrading`, `test_session_reset.py`, `SQLitePaperTradingStore`, `test_agent_view.py`, `SecretFilter`, `create_app`, `test_lab.py`, `setup`, `test_service_like_shell_runs_documented_examples_without_profile`, `BitsStore`, `test_lab_retention.py`, `state_db_path`, `canonical_json`, `test_bits_memory.py`, `test_cli.py`, `LabStore`, `test_bits_memory_drafts.py`, `atomic_write_text`, `BitsError`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `_datetime`, `test_session_reset.py`, `test_agent_loop.py`, `test_agent_view.py`, `create_app`, `state_backup.py`, `test_demo_execution.py`, `test_lab.py`, `setup`, `cli.py`, `paper_from_env`, `test_demo_automation_paper_only_skips_broker_dependencies`, `test_demo_runner.py`, `InMemoryAgentTranscriptStore`, `canonical_json`, `restart_policy`, `ContinuousAgentRunner`, `PaperToCTraderDemoCoordinator`, `.__init__`, `test_engine_loop.py`, `test_cli.py`, `ResearchHarness`, `PaperTradingEngine`, `CTraderVolumeConversion`, `SQLiteAgentTranscriptStore`, `agent_controller`, `data_heal`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `xauusd-research` to the rest of the system?**
  _194 weakly-connected nodes found - possible documentation gaps or missing edges._