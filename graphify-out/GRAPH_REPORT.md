# Graph Report - xauusd-conversation-release  (2026-10-26)

## Corpus Check
- 207 files · ~205,306 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .service 9, (none) 7, .timer 3)

## Summary
- 3870 nodes · 10835 edges · 158 communities (138 shown, 20 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 566 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ecc6d9a5`
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
- test_ctrader_lifecycle.py
- LabStore
- CodexResearchClient
- PaperTrading
- self_improve.py
- test_research_completion.py
- DemoAutomationRunner
- Any
- test_agent_loop.py
- firecrawl_research.py
- RemoteComputeBridge
- test_agent_view.py
- synthetic_bars
- BitsStore
- XAUUSD discovery, incident, quantitative, and scaling audit
- agent_view.py
- CTraderAuthError
- OpenAICompatiblePlanner
- paper_trading.py
- test_demo_execution.py
- persist_tokens_env
- Local audit — 2026-09-24
- HistoricalDataStore
- test_lab.py
- bounded_process
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- TournamentDataset
- ShadowTradingReadiness
- cli.py
- ._discover_account
- autonomous_harness.py
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
- ctrader_demo.py
- Any
- oauth.py
- restart_policy
- test_tournament_runner.py
- pandas
- ContinuousAgentRunner
- EngineConfig
- _registry_schema_valid
- core.py
- pytest
- PostgresConnection
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
- write_status
- .__init__
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- _MainContent
- AgentTools
- MemoryConnection
- lab_api.py
- test_cli.py
- PaperToCTraderDemoCoordinator
- AgentAdvisor
- PaperTradingEngine
- closed_bar
- CTraderVolumeConversion
- LiveBarFeed
- setup
- ml_models.py
- bits_capabilities.py
- test_bits_research.py
- ._note
- SQLiteAgentTranscriptStore
- live_feed.py
- SecretFilter
- .run
- _bars
- CTraderDemoOpenApiTransport
- test_weekly_report.py
- InMemoryHarnessStore
- EngineeringManager
- ExperimentSpec
- test_oauth.py
- atomic_write_text
- BitsError
- types
- Store
- lab_tools.py
- Any
- canonical_json
- verify_result_parity.py
- graphify reference: extra exports and benchmark
- Signals
- portfolio_research.py
- .send
- atomic_write_json
- test_lab_dashboard.py
- build_parser
- CTraderHistoricalAdapter
- README.md
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- CTraderOpenApiConfig
- _datetime
- Persistent open-ended Codex agent
- Operator runbook: engine, live feed, and the visible harness
- FakeResponse
- Codex autonomous trading lab
- Datadog Bits connection
- Harness cleanup and improvement checklist — 2026-10-24
- Requirements: reliable research-to-paper-trade workflow
- test_sandbox_tests_return_bounded_feedback_and_clean_environment
- agent_controller
- ExecutionConfig
- _download_with_retry
- harness-outcomes-plan-2026-10-23.md
- agent_experiments.py
- Research and measured self-improvement implementation plan
- agent_advisor.py
- CockroachHarnessStore
- trendbars_to_frame
- StoreCorruptError
- Research program and measured improvement
- StateTransaction
- sklearn_base
- tarfile
- /graphify
- Research completion and repair — 2026-10-26

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `setup()` - 96 edges
3. `MemoryRegistry` - 89 edges
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
- `Original incident evidence (pre-merge snapshot)` --references--> `BitsError`  [INFERRED]
  requirements.md → xauusd/bits.py
- `Order lifecycle and errors — follow-up #15` --references--> `is_error()`  [INFERRED]
  docs/local-handoff-audit-2026-09-24.md → xauusd/ctrader_auth.py
- `R3 — P1: make experiment continuity work with the deployed backend` --references--> `ExperimentRegistry`  [INFERRED]
  requirements.md → xauusd/experiment_registry.py

## Import Cycles
- None detected.

## Communities (158 total, 20 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.12
Nodes (25): account(), An unclassified account is not a demo account. ``isLive`` is a proto3 optional…, The discriminator has to work on the actual SDK message, not just dicts., test_demo_accounts_empty_when_all_live(), test_demo_accounts_excludes_a_dict_without_the_flag(), test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo(), test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account(), test_is_error_extracts_code_and_description() (+17 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.29
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "main"
Cohesion: 0.09
Nodes (21): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+13 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (64): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), plotly_graph_objects (+56 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.09
Nodes (32): _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted., `monitor_error` used to be assigned and then read by nothing at all. (+24 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.16
Nodes (6): ExperimentStatus, ExperimentRegistry, Any, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool., Path

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.18
Nodes (19): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+11 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.10
Nodes (16): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+8 more)

### Community 9 - "test_bits_capabilities.py"
Cohesion: 0.12
Nodes (34): R2 — P1: capability discovery failure must remain visible, fake_tool(), parametrize, The shell-job environment is discoverable from the environment jobs really get., Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_every_published_operation_is_a_real_cli_command(), test_failed_discovery_is_explicit_in_every_view() (+26 more)

### Community 10 - "test_ctrader_lifecycle.py"
Cohesion: 0.31
Nodes (10): event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending(), test_partial_fill_followed_by_rejection_requires_reconciliation() (+2 more)

### Community 11 - "LabStore"
Cohesion: 0.12
Nodes (12): test_snapshot_expiry_deletes_backend_rows(), store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics(), LabStore, save() (+4 more)

### Community 12 - "CodexResearchClient"
Cohesion: 0.16
Nodes (12): Step 7d - MCP server (only if --mcp flag), test_full_access_launcher_preserves_session_and_compaction(), test_native_output_is_complete_and_private_reasoning_is_ignored(), test_harness_pins_luna_on_new_and_resumed_calls(), test_resumes_exact_thread_and_enables_native_compaction(), test_session_telemetry_tracks_native_compaction_incrementally(), test_thread_id_persisted_before_next_turn(), CodexResearchClient (+4 more)

### Community 13 - "PaperTrading"
Cohesion: 0.07
Nodes (61): paper_trading(), The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., The monitor's status string alone was never enough. A monitor that died after…, test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_alerts_on_a_stale_or_dead_position_monitor(), test_health_names_the_paths_a_retrieval_loop_keeps_reading(), test_health_stays_quiet_when_no_path_repeats() (+53 more)

### Community 14 - "self_improve.py"
Cohesion: 0.13
Nodes (20): base64, CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal() (+12 more)

### Community 15 - "test_research_completion.py"
Cohesion: 0.10
Nodes (45): test_blockers_are_classified_and_repair_has_priority(), test_completed_plan_legacy_evidence_is_backfilled_only_by_exact_id(), test_improvement_has_one_working_slot_and_protected_fix_is_escalated(), test_old_workspace_exact_evidence_can_be_recorded_after_log_rotation(), test_only_two_plans_may_execute_and_success_must_be_interpreted(), test_plan_keeps_evidence_and_code_provenance_after_call_log_rotation(), test_result_summary_keeps_metrics_in_compacted_context(), test_training_export_preserves_utc_index_and_reports_gaps() (+37 more)

### Community 16 - "DemoAutomationRunner"
Cohesion: 0.17
Nodes (6): DemoAutomationRunner, DemoLifecycle, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 17 - "Any"
Cohesion: 0.08
Nodes (15): Client, failed(), issue(), failed(), issue(), observe(), succeeded(), CTraderDemoStore (+7 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.10
Nodes (42): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), A ticking agent must not be served as stopped. The engine's startup reconcile…, refresh_config(), refresh_runner() (+34 more)

### Community 19 - "firecrawl_research.py"
Cohesion: 0.15
Nodes (18): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+10 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (24): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+16 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.05
Nodes (39): _feed(), _harness_client(), fixture, parametrize, The deterministic engine writes to the same `agent_runs` table. Taking the…, `limit` alone does not bound a response. A shell-job step carries a captured…, The health endpoint is the observability surface; it must not raise. An…, A non-SQLite transcript store must not take the panel down. (+31 more)

### Community 22 - "synthetic_bars"
Cohesion: 0.07
Nodes (55): parametrize, test_return_features_exclude_entire_gap_straddling_horizon(), test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal() (+47 more)

### Community 23 - "BitsStore"
Cohesion: 0.06
Nodes (41): Operations, Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, test_service_like_shell_runs_documented_examples_without_profile(), action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written… (+33 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "agent_view.py"
Cohesion: 0.08
Nodes (33): FastAPI, fastapi_responses, inspect, test_agent_transcript_backend_selection_defaults_to_local(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store(), agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default). (+25 more)

### Community 26 - "CTraderAuthError"
Cohesion: 0.14
Nodes (20): test_data_update_does_not_retry_auth_errors(), unauthorized(), demo_env(), downloader_config(), validate() is no longer a one-time check performed only by from_env(). The…, test_download_does_not_retry_non_token_auth_error(), fake_fetch(), test_download_does_not_retry_without_a_refresh_token() (+12 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.33
Nodes (5): 3. Where the planner is wired today (confirmed), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), OpenAICompatiblePlanner, Return the model's raw response content and the parsed allow-listed action. Raw…

### Community 28 - "paper_trading.py"
Cohesion: 0.09
Nodes (44): math, test_account_only_reset_preserves_research_and_stop(), seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), decision(), seeded_db(), test_backup_keeps_validating_wal_writes() (+36 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.15
Nodes (21): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+13 more)

### Community 30 - "persist_tokens_env"
Cohesion: 0.12
Nodes (19): PathLike, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent…, Smoke test: concurrent writers never produce an unparseable env file., test_persist_tokens_appends_missing_key_and_sets_0600() (+11 more)

### Community 31 - "Local audit — 2026-09-24"
Cohesion: 0.11
Nodes (13): Historical delivery and deployment notes, Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24 (+5 more)

### Community 32 - "HistoricalDataStore"
Cohesion: 0.13
Nodes (21): pyarrow_parquet, A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, _seed_store(), test_dashboard_uses_metadata_and_bounded_tail_not_store_read(), test_read_only_lab_api_reports_actual_data_and_events(), test_compaction_preserves_rebuild_revision_winner(), _build_engine(), Construct the deterministic engine from the same stores the agent uses. (+13 more)

### Community 33 - "test_lab.py"
Cohesion: 0.06
Nodes (64): test_failed_worker_schedule_rolls_back_without_retry(), parametrize, qualified_candidate(), quote(), bars(), parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code() (+56 more)

### Community 34 - "bounded_process"
Cohesion: 0.13
Nodes (11): test_process_timeout_and_output_bound(), test_process_workspace_limit_stops_writer(), test_process_workspace_symlink_is_rejected(), test_successful_shell_cannot_leave_background_writer(), test_codex_environment_does_not_inherit_broker_credentials(), test_permission_profile_restricts_tools_to_training_workspace(), bounded_process(), Drain to disk with a hard runtime and output bound, killing the process group. (+3 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.13
Nodes (15): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 3 - Extract entities and relationships (+7 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.14
Nodes (13): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 7.1 Code — one relaxation (small, tested) (+5 more)

### Community 37 - "TournamentDataset"
Cohesion: 0.07
Nodes (36): dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version…, A freeze killed mid-write must not hang the next one, nor quietly pass., A backtester or cost change must invalidate stored results. Both were hardcoded…, test_a_version_directory_with_no_manifest_fails_loudly() (+28 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 39 - "cli.py"
Cohesion: 0.09
Nodes (44): collections, csv, datetime, dotenv, gzip, hashlib, html, html_parser (+36 more)

### Community 40 - "._discover_account"
Cohesion: 0.18
Nodes (13): app_failed(), account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), LiveFeedUnavailable (+5 more)

### Community 41 - "autonomous_harness.py"
Cohesion: 0.27
Nodes (9): concurrent_futures, 6. Safety and repository-rule compliance (unchanged), 8. Prototype gate and test plan (execute BEFORE any cutover), _check_reason(), parse_action(), PlannerResponseError, ValueError, Research-only autonomous harness primitives; this module has no broker or web… (+1 more)

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 49 - "test_retention.py"
Cohesion: 0.11
Nodes (41): test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(), archive(), _local_backups(), test_compaction_reads_compressed_raw_pages(), test_completed_logs_only_and_pins(), test_completed_workspace_reclaims_training_and_scripts_but_keeps_memory(), test_completed_workspace_with_nested_symlink_retained(), test_compress_existing_exact_target_and_deterministic_bytes() (+33 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.13
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 51 - "InMemoryAgentTranscriptStore"
Cohesion: 0.09
Nodes (10): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), test_base_runner_records_codes_for_planner_and_tick_errors(), boom(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store., Mirror of the SQLite retention so both backends behave the same., Family-scoped mirror of the SQL stores: never close another family's run. (+2 more)

### Community 52 - "test_automation.py"
Cohesion: 0.10
Nodes (24): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., Ranking, validation and selection must use three disjoint partitions. The…, test_atomic_json_replaces_complete_document(), test_champion_is_not_replaced_when_either_side_lacks_a_dataset_binding(), test_champion_never_promotes_a_candidate_with_no_score() (+16 more)

### Community 53 - "ctrader_demo.py"
Cohesion: 0.10
Nodes (26): test_symbol_metadata_and_volume_policy_validate_invariants(), parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+18 more)

### Community 54 - "Any"
Cohesion: 0.11
Nodes (11): Operating model, 1. What was built and why, CockroachPaperTradingStore, _now(), transition(), transition(), PaperTradingStore, Any (+3 more)

### Community 55 - "oauth.py"
Cohesion: 0.18
Nodes (13): contextlib, fcntl, urllib_error, _env_key(), _env_lock(), guard(), _env_value(), Path (+5 more)

### Community 56 - "restart_policy"
Cohesion: 0.14
Nodes (14): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+6 more)

### Community 57 - "test_tournament_runner.py"
Cohesion: 0.10
Nodes (16): Dependence-aware bootstrap validation — 2026-08-21, test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed() (+8 more)

### Community 58 - "pandas"
Cohesion: 0.07
Nodes (51): dataclasses, ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, numpy, operator, pandas, sklearn_metrics (+43 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.07
Nodes (19): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), CockroachAgentTranscriptStore, ContinuousAgentRunner, Any, BaseException (+11 more)

### Community 60 - "EngineConfig"
Cohesion: 0.17
Nodes (10): An oversized proposal must be visibly refused, not silently trimmed. Clamping…, test_engine_cannot_exceed_max_position(), test_engine_config_rejects_unbounded_values(), test_engine_does_not_clamp_an_oversized_proposal(), test_engine_status_reports_the_running_process_not_a_phantom(), test_halt_stops_proposals_and_persists_the_reason(), engine_controller(), Operator and supervisor control for the deterministic trade engine. (+2 more)

### Community 61 - "_registry_schema_valid"
Cohesion: 0.21
Nodes (12): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_registry_validation_streams_rows_and_rejects_non_array_tables(), Validate logical snapshot JSON in bounded memory (8 MiB per row). Snapshots…, _registry_schema_valid() (+4 more)

### Community 62 - "core.py"
Cohesion: 0.31
Nodes (7): test_backtest(), campaign(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 63 - "pytest"
Cohesion: 0.20
Nodes (17): ctrader_open_api_messages_openapimessages_pb2, pytest, sqlite3, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time() (+9 more)

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
Nodes (63): date, pandas_tseries_holiday, _cot_csv(), _prereg(), The preregistered CFTC study: point-in-time discipline, session weeks, fail-…, 15:30 New York is 20:30 UTC in winter and 19:30 UTC under daylight time. The…, The fail-closed check the artifact claims, verified instead of asserted. Taking…, Excluding 2023 and 2025 wholesale means some flows span a gap; report how many.… (+55 more)

### Community 72 - "bits_runner.py"
Cohesion: 0.08
Nodes (23): missing_executables(), Names bash (or /usr/bin/env) reported as not found in a completed job's stderr., error_details(), AgentLock, Single process per container; the lock is runtime coordination, not state., excerpt(), result_for_prompt(), message_fingerprint() (+15 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.16
Nodes (20): at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from…, Synthetic M1 bars stamped at bar open, only while the session gate is open., session_bars(), test_a_week_whose_data_stops_early_is_not_complete(), test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected(), test_pandas_weekly_labels_disagree_with_session_weeks() (+12 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.09
Nodes (39): errno, frame(), minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.…, `data update` starts from the newest bar, so a hole in the middle is permanent.…, A weekend is not data loss; counting it as such hides the gaps that matter. (+31 more)

### Community 77 - "write_status"
Cohesion: 0.24
Nodes (15): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), bits_alerts() (+7 more)

### Community 78 - ".__init__"
Cohesion: 0.15
Nodes (5): EngineStore, MarketSource, Protocol, The narrow slice of the durable store the engine needs., TranscriptSink

### Community 79 - "test_bits_memory.py"
Cohesion: 0.12
Nodes (30): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection(), reply(), sample_notes() (+22 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.10
Nodes (34): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, A restart re-proposes the same decision for the same bar, and the store's…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case. (+26 more)

### Community 82 - "_MainContent"
Cohesion: 0.12
Nodes (8): HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), xauusd, _excerpt_text(), _MainContent, Prefer a publisher's explicit content region over repeated site menus.

### Community 83 - "AgentTools"
Cohesion: 0.15
Nodes (19): Store, test_dependency_install_requires_pins(), test_dependency_install_targets_scratch_only(), test_domain_configuration(), test_fetch_rejects_private_dns(), test_market_observe_excludes_frozen_and_forming_bars(), test_market_observe_without_frozen_boundary_reveals_no_history(), test_remote_job_identity_is_action_derived() (+11 more)

### Community 86 - "lab_api.py"
Cohesion: 0.09
Nodes (20): test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), test_statistics_counts_retained_evidence_without_claiming_success(), test_counter_update_rolls_back_with_owning_state_transaction(), test_counters_survive_detail_eviction_and_ignore_duplicate_updates(), test_release_advisory_classification_never_hides_engineering_uncertainty(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal() (+12 more)

### Community 87 - "test_cli.py"
Cohesion: 0.10
Nodes (36): DemoTransport, _heal_args(), _isolated_bits_state(), no_broker(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, An interior hole is a smaller problem than a refresh reported as failed. The… (+28 more)

### Community 88 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.10
Nodes (21): test_environment_config_is_disabled_unless_explicitly_true(), handler(), demo_automation(), _demo_automation_start(), _demo_automation_status(), Explicit operator override for the demo execution kill switch; paper and the…, Run the explicitly enabled local-data paper-to-demo canary., NormalizedDecision (+13 more)

### Community 89 - "AgentAdvisor"
Cohesion: 0.07
Nodes (30): Harness maintenance — 2026-10-24, test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_explicit_evidence_pages_and_source_excerpts_survive_context_compaction(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory() (+22 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.14
Nodes (13): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+5 more)

### Community 91 - "closed_bar"
Cohesion: 0.18
Nodes (7): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 92 - "CTraderVolumeConversion"
Cohesion: 0.12
Nodes (12): test_demo_factory_binds_authoritative_paper_exposure(), test_volume_policy_from_metadata(), _ctrader_demo_adapter(), expected_volume(), _paper_to_demo_coordinator(), CTraderVolumeConversion, CTraderVolumePolicy, DemoExecutor (+4 more)

### Community 93 - "LiveBarFeed"
Cohesion: 0.11
Nodes (39): config(), credentials(), demo_feed_environment(), FakeClient, FakeStore, fixture, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously. (+31 more)

### Community 94 - "setup"
Cohesion: 0.07
Nodes (40): test_capture_limit_is_explicit_and_remains_valid_json(), test_filters_before_capture_and_deduplicates_instruction_content(), test_large_exchange_is_retrievable_but_activity_stays_small(), test_read_only_paged_routes_and_inert_ui(), test_real_child_boundary_records_exact_application_input_and_validated_reply(), test_retention_limits_and_equal_timestamp_paging(), test_compaction_also_refuses_deactivating_or_unverified_units(), test_compaction_refuses_a_running_database_service() (+32 more)

### Community 95 - "ml_models.py"
Cohesion: 0.09
Nodes (20): ImportError, importlib, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample(), test_core_model_adapters_and_ensemble_probabilities() (+12 more)

### Community 96 - "bits_capabilities.py"
Cohesion: 0.08
Nodes (35): Datadog Bits operations, Bits shell environment (`bits-capabilities`), platform, shlex, test_shell_environment_keeps_the_latest_refreshed_tokens(), test_shell_path_prepends_service_interpreter_and_declared_directories(), cli_commands(), cli_prefix() (+27 more)

### Community 97 - "test_bits_research.py"
Cohesion: 0.12
Nodes (24): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+16 more)

### Community 98 - "._note"
Cohesion: 0.09
Nodes (24): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), heartbeat(), on_connected(), on_disconnected(), on_message(), tick(), confirmed() (+16 more)

### Community 99 - "SQLiteAgentTranscriptStore"
Cohesion: 0.06
Nodes (36): Connection, Row, decision(), parametrize, Validation must not reject a real account, including a running one., The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is., The owner of a run is the only authority on whether it is live. (+28 more)

### Community 100 - "live_feed.py"
Cohesion: 0.14
Nodes (16): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+8 more)

### Community 101 - "SecretFilter"
Cohesion: 0.09
Nodes (33): skipif, memory(), notes(), open_drafts(), PostgresLikeTranscript, fixture, R1: rejected memory writes keep durable draft identities until explicitly…, psycopg-like connection: one implicit transaction per block, committed or… (+25 more)

### Community 102 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 103 - "_bars"
Cohesion: 0.22
Nodes (10): _bars(), Three valid, non-overlapping minutes, shifted so writers never collide., A shared temporary name lets two writers interleave into one inode. That is how…, The invariant the corruption broke: every writer's bars survive, and it reads., One value must not cost the whole frame. `data update` runs four times a day on…, test_concurrent_writers_leave_a_readable_complete_store(), append(), test_last_timestamp_reads_the_index_column_only() (+2 more)

### Community 104 - "CTraderDemoOpenApiTransport"
Cohesion: 0.10
Nodes (32): adapter(), FakeClient, ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call() (+24 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.16
Nodes (20): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+12 more)

### Community 107 - "EngineeringManager"
Cohesion: 0.25
Nodes (8): _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker., _safe()

### Community 108 - "ExperimentSpec"
Cohesion: 0.25
Nodes (14): E. Current 50,000-scenario architecture and benchmark, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_replenishment_scans_past_existing_prefix(), ExperimentSpec, from_strategy() (+6 more)

### Community 109 - "test_oauth.py"
Cohesion: 0.25
Nodes (14): response_json(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises(), test_refresh_access_token_returns_pair_with_browser_agent(), fake_urlopen(), test_rejected_grant_raises_oauth_error() (+6 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.14
Nodes (22): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+14 more)

### Community 111 - "BitsError"
Cohesion: 0.08
Nodes (43): main(), call(), envelope(), interrogation(), parametrize, test_tick_errors_keep_a_classified_code_phase_and_safe_summary(), failing_poll(), shell_action() (+35 more)

### Community 112 - "types"
Cohesion: 0.38
Nodes (5): test_research_advisories_do_not_disable_safe_software_releases(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), types, release_healthy(), run()

### Community 113 - "Store"
Cohesion: 0.22
Nodes (5): The 2026-10-05 sequence: a fresh engine, no halt anywhere, still no trade., Store, test_a_halt_from_another_process_still_stops_a_running_engine(), test_resume_clears_a_persisted_halt(), test_the_gate_holds_with_no_halt_key_and_survives_a_restart()

### Community 114 - "lab_tools.py"
Cohesion: 0.18
Nodes (23): ast, generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused() (+15 more)

### Community 115 - "Any"
Cohesion: 0.15
Nodes (5): HarnessStore, Any, Protocol, RuntimeError, ToolExecutionError

### Community 116 - "canonical_json"
Cohesion: 0.08
Nodes (45): _age_seconds(), BitsMemory, apply(), apply(), apply(), _brief(), _check_categories(), _check_draft_ids() (+37 more)

### Community 117 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 118 - "graphify reference: extra exports and benchmark"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 119 - "Signals"
Cohesion: 0.25
Nodes (6): The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise., Signals, test_engine_does_nothing_when_the_signal_is_flat(), test_engine_refuses_to_evaluate_a_strategy_with_no_recorded_validation(), test_resume_takes_effect_on_a_running_engine_without_a_restart()

### Community 120 - "portfolio_research.py"
Cohesion: 0.20
Nodes (20): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), read(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete() (+12 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "atomic_write_json"
Cohesion: 0.13
Nodes (21): The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker(), test_file_lock_times_out_instead_of_waiting_forever() (+13 more)

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.15
Nodes (4): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot()

### Community 124 - "build_parser"
Cohesion: 0.25
Nodes (8): ArgumentParser, Without this the command exists but nothing runs it, so a hole still sits for…, test_the_heal_command_is_in_the_cli_grammar(), test_update_can_heal_and_the_timer_does(), test_the_raw_retention_command_is_in_the_cli_grammar(), test_the_rebuild_command_is_in_the_cli_grammar(), build_parser(), The complete CLI grammar; also used to publish supported operations.

### Community 125 - "CTraderHistoricalAdapter"
Cohesion: 0.25
Nodes (5): CTraderHistoricalAdapter, Path, The same wire page, whether plain or losslessly gzip-compressed., Import cTrader CSV exports into the normalized historical store., read_raw_page()

### Community 126 - "README.md"
Cohesion: 0.13
Nodes (10): Codex permissions and conversation visibility, Display and storage, Verification, Bits agent instructions, Autonomous Agent, Legacy Datadog planner operations, Database maintenance and seven-day log rotation, Initial deployment (+2 more)

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.08
Nodes (25): Active Codex agent, Architecture, Aurum — Codex Autonomous Trading Lab, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+17 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.11
Nodes (18): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, Database retention — 2026-10-24, Full-access Codex and visible exchanges — 2026-10-26, graphify (+10 more)

### Community 132 - "CTraderOpenApiConfig"
Cohesion: 0.70
Nodes (4): test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag(), CTraderOpenApiConfig

### Community 133 - "_datetime"
Cohesion: 0.19
Nodes (21): Engineering, threading, canary_signal_tool(), handler(), _decision_id(), _mock_market_for_read(), Continuous single-agent XAUUSD paper trading loop with a live, visible thinking…, read_market_tool() (+13 more)

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.18
Nodes (10): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Research continuity and maintenance — 2026-10-24 (+2 more)

### Community 135 - "Operator runbook: engine, live feed, and the visible harness"
Cohesion: 0.20
Nodes (9): 10. Related documents, 2. Publish the Datadog workflow message stream (required for the thinking panel), 4. Enable the deterministic engine, 5. Restart the live view so the new observability is visible, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback, Engine control (+1 more)

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.22
Nodes (9): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Research activity chat — 2026-10-23, Research and automatic deployment, Storage and retention (+1 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "Harness cleanup and improvement checklist — 2026-10-24"
Cohesion: 0.40
Nodes (4): Audit findings, Broker smoke shutdown follow-up, Harness cleanup and improvement checklist — 2026-10-24, Verification and deployment log

### Community 140 - "Requirements: reliable research-to-paper-trade workflow"
Cohesion: 0.12
Nodes (15): Delivery and operational boundaries, Delivery order after this merge, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Merge review — 2026-09-25, baseline `cba22b2`, Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit (+7 more)

### Community 142 - "agent_controller"
Cohesion: 0.10
Nodes (20): parametrize, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An…, test_agent_config_rejects_non_finite_limits(), test_demo_automation_requires_explicit_positive_volume(), _positive_float(), agent_controller(), _agent_data_refresh_source(), _agent_status_path() (+12 more)

### Community 143 - "ExecutionConfig"
Cohesion: 0.14
Nodes (28): main(), bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,…, Zero is a real value; a metric that cannot be computed must say so. Reporting… (+20 more)

### Community 146 - "_download_with_retry"
Cohesion: 0.18
Nodes (9): Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., test_data_update_reraises_the_first_transient_failure(), test_data_update_retries_transient_failures(), _download_attempt_subprocess(), _download_with_retry(), Any, One single-shot ``data download`` in a fresh interpreter; returns its result. A… (+1 more)

### Community 149 - "agent_experiments.py"
Cohesion: 0.33
Nodes (12): test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), _archive(), Independent exploratory paper accounts; never a promotion or broker path. (+4 more)

### Community 150 - "Research and measured self-improvement implementation plan"
Cohesion: 0.25
Nodes (7): Acceptance criteria, Delivery checklist, Deployment procedure, Final verification and deployment, Implementation evidence so far, Objective and boundaries, Research and measured self-improvement implementation plan

### Community 153 - "agent_advisor.py"
Cohesion: 0.12
Nodes (34): copy, functools, test_improvement_cannot_claim_old_release_as_new_work(), test_inspection_and_failed_remote_work_are_not_progress(), test_outcome_requires_existing_successful_evidence_and_deduplicates(), test_operator_release_measurements_yield_to_next_autonomous_release(), test_measured_bottleneck_seeds_one_backlog_item_and_preserves_baseline(), test_missing_baseline_cannot_be_claimed_and_inference_history_is_bounded() (+26 more)

### Community 156 - "trendbars_to_frame"
Cohesion: 0.15
Nodes (10): test_trendbar_delta_decoding(), Any, DataFrame, Contiguous runs of market-open minutes the store does not have. `validate`…, Replace the store with `bars`, merged into whatever is already there. One…, Every archived raw page as ``(first_minute, last_minute, path)``, sorted. The…, Which archived pages a minimal cover makes redundant. Deletes nothing. The…, Rebuild the store offline from the archived raw page cache. The archive under… (+2 more)

### Community 158 - "StoreCorruptError"
Cohesion: 0.13
Nodes (11): 9. Recovering the market-data store, OSError, `error_type: OSError` with `error_code: null` was undiagnosable. That is all…, test_a_corrupt_store_is_reported_as_corrupt_not_as_a_bare_oserror(), test_classify_store_error_names_a_full_disk_and_refuses_to_guess(), classify_store_error(), BaseException, The newest bar in the store, reading the index column only. `data update` needs… (+3 more)

### Community 161 - "Research program and measured improvement"
Cohesion: 0.25
Nodes (7): Decision cycle, Discovery and sources, Improvement measurement, Preregistration and execution, Release readiness and visibility, Research program and measured improvement, Storage and limitations

### Community 162 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 169 - "/graphify"
Cohesion: 0.13
Nodes (13): Delivery Stages, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval, Research notes (`bits-memory`, schema `xauusd.notes/1`), For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only (+5 more)

### Community 171 - "Research completion and repair — 2026-10-26"
Cohesion: 0.33
Nodes (5): Diagnosis and implementation, Measured pre-deployment audit, Measurement and release handling, Research completion and repair — 2026-10-26, Verification and limitations

## Knowledge Gaps
- **199 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+194 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1189 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `_datetime`, `agent_controller`, `test_agent_loop.py`, `test_agent_view.py`, `agent_experiments.py`, `agent_view.py`, `paper_trading.py`, `test_demo_execution.py`, `test_lab.py`, `cli.py`, `test_demo_runner.py`, `InMemoryAgentTranscriptStore`, `Any`, `restart_policy`, `ContinuousAgentRunner`, `.__init__`, `test_engine_loop.py`, `test_cli.py`, `PaperToCTraderDemoCoordinator`, `PaperTradingEngine`, `CTraderVolumeConversion`, `setup`, `SQLiteAgentTranscriptStore`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `SQLiteAgentTranscriptStore` connect `SQLiteAgentTranscriptStore` to `test_bits_runner.py`, `_datetime`, `test_bits_capabilities.py`, `LabStore`, `PaperTrading`, `test_agent_view.py`, `BitsStore`, `agent_view.py`, `paper_trading.py`, `test_lab.py`, `cli.py`, `test_bits_memory.py`, `lab_api.py`, `test_cli.py`, `setup`, `SecretFilter`, `atomic_write_text`, `BitsError`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `main`, `Repository Operating Rules`, `ConfirmedBreakoutCanarySource`, `agent_controller`, `ExecutionConfig`, `test_agent_loop.py`, `synthetic_bars`, `CTraderAuthError`, `trendbars_to_frame`, `StoreCorruptError`, `test_lab.py`, `TournamentDataset`, `cli.py`, `/graphify`, `test_retention.py`, `test_automation.py`, `pandas`, `test_data.py`, `AgentTools`, `test_cli.py`, `LiveBarFeed`, `bits_capabilities.py`, `live_feed.py`, `CTraderHistoricalAdapter`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `xauusd-research` to the rest of the system?**
  _199 weakly-connected nodes found - possible documentation gaps or missing edges._