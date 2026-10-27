# Graph Report - xauusd-evidence-release  (2026-10-27)

## Corpus Check
- 211 files · ~207,171 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .service 9, (none) 7, .timer 3)

## Summary
- 3913 nodes · 10961 edges · 166 communities (143 shown, 23 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 571 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3b331c48`
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
- test_ctrader_lifecycle.py
- setup
- CodexResearchClient
- PaperTrading
- self_improve.py
- test_research_completion.py
- atomic_write_json
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- StrategySpec
- SecretFilter
- XAUUSD discovery, incident, quantitative, and scaling audit
- agent_view.py
- DataConfig
- OpenAICompatiblePlanner
- state_backup.py
- test_demo_execution.py
- InMemoryAgentTranscriptStore
- lab.py
- test_tournament_runner.py
- test_lab.py
- AdaptiveSearch
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- synthetic_bars
- ShadowTradingReadiness
- datetime
- ._discover_account
- canonical_json
- ._fetch
- .write_notes
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- test_retention.py
- test_demo_runner.py
- bits_memory.py
- test_automation.py
- ctrader_demo.py
- PaperDecision
- serialized
- restart_policy
- DemoAutomationRunner
- ExecutionConfig
- ContinuousAgentRunner
- pytest
- test_lab_dashboard.py
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
- test_data.py
- opencode.json
- BitsStore
- write_status
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- fetch_source
- AgentTools
- MemoryConnection
- lab_api.py
- test_cli.py
- _registry_schema_valid
- AgentAdvisor
- PaperTradingEngine
- closed_bar
- test_oauth.py
- LiveBarFeed
- test_database_retention.py
- ml_models.py
- LabStore
- bits_runner.py
- ._note
- SQLiteAgentTranscriptStore
- live_feed.py
- test_bits_memory_drafts.py
- .run
- atomic.py
- test_ctrader_demo.py
- test_weekly_report.py
- TournamentDataset
- bounded_process
- ExperimentSpec
- persist_tokens_env
- atomic_write_text
- BitsError
- types
- Local audit — 2026-09-24
- lab_tools.py
- test_experiment_registry.py
- BitsMemory
- .__init__
- graphify reference: extra exports and benchmark
- json
- portfolio_research.py
- .send
- Operator runbook: engine, live feed, and the visible harness
- child_environment
- DecisionSource
- InMemoryHarnessStore
- README.md
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- .__init__
- _datetime
- Persistent open-ended Codex agent
- _demo_automation_runner
- HarnessStore
- Codex autonomous trading lab
- Datadog Bits connection
- Harness cleanup and improvement checklist — 2026-10-24
- Requirements: reliable research-to-paper-trade workflow
- test_offline.py
- cli.py
- CockroachHarnessStore
- transition
- test_evidence_completion.py
- _result_file
- database_retention.py
- harness-outcomes-plan-2026-10-23.md
- test_health_uses_configured_cockroach_registry
- Research and measured self-improvement implementation plan
- RecordingPostgres
- build_features
- agent_advisor.py
- FakeResponse
- engine_decision_id
- HistoricalDataStore
- engine_controller
- _validated_ledger
- Research program and measured improvement
- StateTransaction
- sklearn_base
- tarfile
- evidence_refs
- Delivery Stages
- Research completion and repair — 2026-10-26

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `setup()` - 112 edges
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

## Communities (166 total, 23 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.12
Nodes (25): account(), An unclassified account is not a demo account. ``isLive`` is a proto3 optional…, The discriminator has to work on the actual SDK message, not just dicts., test_demo_accounts_empty_when_all_live(), test_demo_accounts_excludes_a_dict_without_the_flag(), test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo(), test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account(), test_is_error_extracts_code_and_description() (+17 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.23
Nodes (16): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+8 more)

### Community 2 - "OperationsManager"
Cohesion: 0.12
Nodes (19): gzip, test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost() (+11 more)

### Community 3 - "dashboard.py"
Cohesion: 0.08
Nodes (55): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), plotly_graph_objects (+47 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.08
Nodes (33): test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted. (+25 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.16
Nodes (6): ExperimentStatus, ExperimentRegistry, Any, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool., Path

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.16
Nodes (20): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+12 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.10
Nodes (10): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., setup_files(), test_dashboard_reads_latest_run_and_equity(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature(), test_status_remains_readable_without_generated_tournament_dataset() (+2 more)

### Community 9 - "test_bits_capabilities.py"
Cohesion: 0.05
Nodes (81): Datadog Bits operations, ArgumentParser, Bits shell environment (`bits-capabilities`), platform, R2 — P1: capability discovery failure must remain visible, shlex, fake_tool(), parametrize (+73 more)

### Community 10 - "test_ctrader_lifecycle.py"
Cohesion: 0.22
Nodes (10): Client, event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending() (+2 more)

### Community 11 - "setup"
Cohesion: 0.10
Nodes (27): test_capture_limit_is_explicit_and_remains_valid_json(), test_filters_before_capture_and_deduplicates_instruction_content(), test_large_exchange_is_retrievable_but_activity_stays_small(), test_read_only_paged_routes_and_inert_ui(), test_real_child_boundary_records_exact_application_input_and_validated_reply(), test_retention_limits_and_equal_timestamp_paging(), test_improvement_cannot_claim_old_release_as_new_work(), test_inspection_and_failed_remote_work_are_not_progress() (+19 more)

### Community 12 - "CodexResearchClient"
Cohesion: 0.17
Nodes (12): test_full_access_launcher_preserves_session_and_compaction(), test_native_output_is_complete_and_private_reasoning_is_ignored(), test_harness_pins_luna_on_new_and_resumed_calls(), test_resumes_exact_thread_and_enables_native_compaction(), test_session_telemetry_tracks_native_compaction_incrementally(), test_thread_id_persisted_before_next_turn(), test_timeout_emits_safe_elapsed_diagnostics(), CodexResearchClient (+4 more)

### Community 13 - "PaperTrading"
Cohesion: 0.07
Nodes (63): paper_trading(), The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., The monitor's status string alone was never enough. A monitor that died after…, test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_alerts_on_a_stale_or_dead_position_monitor(), test_health_names_the_paths_a_retrieval_loop_keeps_reading(), test_health_stays_quiet_when_no_path_repeats() (+55 more)

### Community 14 - "self_improve.py"
Cohesion: 0.13
Nodes (20): base64, CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal() (+12 more)

### Community 15 - "test_research_completion.py"
Cohesion: 0.12
Nodes (36): test_blockers_are_classified_and_repair_has_priority(), test_completed_plan_legacy_evidence_is_backfilled_only_by_exact_id(), test_old_workspace_exact_evidence_can_be_recorded_after_log_rotation(), test_only_two_plans_may_execute_and_success_must_be_interpreted(), test_plan_keeps_evidence_and_code_provenance_after_call_log_rotation(), plan(), test_compact_context_pages_full_design_without_truncating_evidence(), test_completed_findings_accumulate_lessons_without_recounting() (+28 more)

### Community 16 - "atomic_write_json"
Cohesion: 0.20
Nodes (12): test_snapshot_expiry_deletes_backend_rows(), _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker. (+4 more)

### Community 17 - "Any"
Cohesion: 0.17
Nodes (12): CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded(), Any (+4 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.09
Nodes (43): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), parametrize, A ticking agent must not be served as stopped. The engine's startup reconcile…, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An… (+35 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.14
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.08
Nodes (28): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+20 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.06
Nodes (32): _feed(), _harness_client(), fixture, parametrize, The deterministic engine writes to the same `agent_runs` table. Taking the…, `limit` alone does not bound a response. A shell-job step carries a captured…, The health endpoint is the observability surface; it must not raise. An…, A non-SQLite transcript store must not take the panel down. (+24 more)

### Community 22 - "StrategySpec"
Cohesion: 0.11
Nodes (31): An empty training window must fail loudly, not look like a negative result., The embargo must reach the report, not just the helper. `walk_forward_splits`…, The negative path was never asserted, which is why several real defects…, A 30-bar rolling feature reaches across the split boundary. The last…, test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration(), test_chronological_splits_are_ordered_and_disjoint() (+23 more)

### Community 23 - "SecretFilter"
Cohesion: 0.08
Nodes (29): action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes…, A failed preview is observability, and observability must not break the job., A post-spawn exception must not strand the row as `running` forever. `state`… (+21 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (48): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+40 more)

### Community 25 - "agent_view.py"
Cohesion: 0.07
Nodes (39): Engineering, FastAPI, fastapi_responses, inspect, test_bits_decisions_show_summary_instead_of_protocol_json(), test_shell_command_and_output_are_not_in_collapsed_text(), frame(), read() (+31 more)

### Community 26 - "DataConfig"
Cohesion: 0.11
Nodes (25): test_data_update_does_not_retry_auth_errors(), unauthorized(), demo_env(), downloader_config(), validate() is no longer a one-time check performed only by from_env(). The…, test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag() (+17 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.22
Nodes (11): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError (+3 more)

### Community 28 - "state_backup.py"
Cohesion: 0.17
Nodes (21): decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+13 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.09
Nodes (30): test_host_and_environment_rejections_are_fail_closed(), coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome() (+22 more)

### Community 30 - "InMemoryAgentTranscriptStore"
Cohesion: 0.10
Nodes (9): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), test_base_runner_records_codes_for_planner_and_tick_errors(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store., Mirror of the SQLite retention so both backends behave the same., Family-scoped mirror of the SQL stores: never close another family's run., The run family a run_id belongs to: ``agent_`` or ``engine_``. The agent and… (+1 more)

### Community 31 - "lab.py"
Cohesion: 0.13
Nodes (32): functools, operator, parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate() (+24 more)

### Community 32 - "test_tournament_runner.py"
Cohesion: 0.17
Nodes (9): Dependence-aware bootstrap validation — 2026-08-21, setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition() (+1 more)

### Community 33 - "test_lab.py"
Cohesion: 0.12
Nodes (35): parametrize, qualified_candidate(), quote(), bars(), test_codex_contract_rejects_unknown_fields_and_overlarge_requests(), test_dataset_advances_only_to_a_wholly_new_cohort(), test_evidence_relations_are_checked_beyond_digest(), test_forward_coverage_rejects_short_observation_despite_fixed_deadline() (+27 more)

### Community 34 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.12
Nodes (15): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+7 more)

### Community 37 - "synthetic_bars"
Cohesion: 0.07
Nodes (38): logging, test_backtest(), dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version…, A freeze killed mid-write must not hang the next one, nor quietly pass. (+30 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 39 - "datetime"
Cohesion: 0.08
Nodes (35): concurrent_futures, csv, datetime, hashlib, html, html_parser, ipaddress, os (+27 more)

### Community 40 - "._discover_account"
Cohesion: 0.21
Nodes (11): app_failed(), account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), The broker client, created once. Injected through ``client_factory`` so the… (+3 more)

### Community 41 - "canonical_json"
Cohesion: 0.13
Nodes (24): Connection, test_account_only_reset_preserves_research_and_stop(), seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), Explicit operator-only, flat paper account rebase; no research reset., rebase(), AgentAlreadyRunning (+16 more)

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - ".write_notes"
Cohesion: 0.16
Nodes (17): apply(), apply(), apply(), _brief(), _close(), _empty_drafts(), load_drafts(), _merge_refs() (+9 more)

### Community 49 - "test_retention.py"
Cohesion: 0.12
Nodes (40): test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(), archive(), _local_backups(), test_compaction_preserves_rebuild_revision_winner(), test_compaction_reads_compressed_raw_pages(), test_completed_logs_only_and_pins(), test_completed_workspace_reclaims_training_and_scripts_but_keeps_memory(), test_completed_workspace_with_nested_symlink_retained() (+32 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.13
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 51 - "bits_memory.py"
Cohesion: 0.15
Nodes (19): _age_seconds(), _check_categories(), _check_draft_ids(), _check_entry(), check_notes(), _is_current_notes(), issue(), _key_path() (+11 more)

### Community 52 - "test_automation.py"
Cohesion: 0.09
Nodes (30): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+22 more)

### Community 53 - "ctrader_demo.py"
Cohesion: 0.08
Nodes (34): FakeClient, test_configured_account_id_bypasses_account_list_scope(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(), test_open_api_transport_fails_reconciliation_on_an_error_reply(), test_open_api_transport_reads_symbol_volume_metadata(), test_open_api_transport_rejects_non_demo_before_constructing_client(), test_open_api_transport_reports_an_order_error_reply_with_its_code(), test_open_api_transport_selects_the_only_authorized_demo_account() (+26 more)

### Community 54 - "PaperDecision"
Cohesion: 0.12
Nodes (10): CockroachPaperTradingStore, _now(), PaperDecision, transition(), transition(), PaperTradingStore, Any, Protocol (+2 more)

### Community 55 - "serialized"
Cohesion: 0.15
Nodes (16): test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), _archive(), Independent exploratory paper accounts; never a promotion or broker path. (+8 more)

### Community 56 - "restart_policy"
Cohesion: 0.13
Nodes (15): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+7 more)

### Community 57 - "DemoAutomationRunner"
Cohesion: 0.17
Nodes (6): DemoAutomationRunner, DemoLifecycle, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 58 - "ExecutionConfig"
Cohesion: 0.07
Nodes (49): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, main(), Secret-free deterministic parity fixture for the runtime container., bars(), gapped_bars(), holding_signal() (+41 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.07
Nodes (19): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), CockroachAgentTranscriptStore, ContinuousAgentRunner, Any, BaseException (+11 more)

### Community 60 - "pytest"
Cohesion: 0.14
Nodes (18): pytest, The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker() (+10 more)

### Community 61 - "test_lab_dashboard.py"
Cohesion: 0.10
Nodes (9): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), test_snapshot_projects_current_agent_and_archived_jobs(), test_statistics_counts_retained_evidence_without_claiming_success(), _age(), Counts only bounded retained evidence; never infer remote execution success. (+1 more)

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
Cohesion: 0.08
Nodes (61): date, pandas_tseries_holiday, _cot_csv(), _prereg(), The preregistered CFTC study: point-in-time discipline, session weeks, fail-…, 15:30 New York is 20:30 UTC in winter and 19:30 UTC under daylight time. The…, The fail-closed check the artifact claims, verified instead of asserted. Taking…, Excluding 2023 and 2025 wholesale means some flows span a gap; report how many.… (+53 more)

### Community 72 - "BitsAgentRunner"
Cohesion: 0.10
Nodes (16): test_nested_output_page_preserves_original_cursor_without_skipping_text(), error_details(), excerpt(), result_for_prompt(), BaseException, Payload-free classification of an exception for events and heartbeats.…, guidance_revision(), BitsAgentRunner (+8 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.16
Nodes (20): at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from…, Synthetic M1 bars stamped at bar open, only while the session gate is open., session_bars(), test_a_week_whose_data_stops_early_is_not_complete(), test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected(), test_pandas_weekly_labels_disagree_with_session_weeks() (+12 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.07
Nodes (51): errno, _bars(), frame(), minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.…, Three valid, non-overlapping minutes, shifted so writers never collide. (+43 more)

### Community 77 - "BitsStore"
Cohesion: 0.17
Nodes (8): Operations, test_bits_notes_only_does_not_repeat_history(), job_output(), BitsStore, Uses the same connection selected for the application's transcript store., Read-modify-write several state keys atomically. SQLite connections run in…, Drop the oldest terminal job records. Nothing else ever deleted from this…, Row counts and stored bytes, so unbounded growth is visible.

### Community 78 - "write_status"
Cohesion: 0.21
Nodes (14): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), run(), agent_status_path() (+6 more)

### Community 79 - "test_bits_memory.py"
Cohesion: 0.13
Nodes (27): codes(), entry(), memory(), observed_wrapper_payload(), open_drafts(), fixture, Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection() (+19 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.08
Nodes (40): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., An oversized proposal must be visibly refused, not silently trimmed. Clamping…, The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise. (+32 more)

### Community 82 - "fetch_source"
Cohesion: 0.09
Nodes (10): HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), xauusd, NoRedirect, _excerpt_text(), fetch_source() (+2 more)

### Community 83 - "AgentTools"
Cohesion: 0.17
Nodes (18): Store, test_dependency_install_requires_pins(), test_dependency_install_targets_scratch_only(), test_domain_configuration(), test_fetch_rejects_private_dns(), test_market_observe_excludes_frozen_and_forming_bars(), test_market_observe_without_frozen_boundary_reveals_no_history(), test_remote_job_identity_is_action_derived() (+10 more)

### Community 86 - "lab_api.py"
Cohesion: 0.12
Nodes (21): pyarrow_parquet, test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), test_dashboard_uses_metadata_and_bounded_tail_not_store_read(), test_release_advisory_classification_never_hides_engineering_uncertainty(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal(), utc_day() (+13 more)

### Community 87 - "test_cli.py"
Cohesion: 0.08
Nodes (40): DemoTransport, _heal_args(), _isolated_bits_state(), no_broker(), Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped. (+32 more)

### Community 88 - "_registry_schema_valid"
Cohesion: 0.21
Nodes (12): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_registry_validation_streams_rows_and_rejects_non_array_tables(), Validate logical snapshot JSON in bounded memory (8 MiB per row). Snapshots…, _registry_schema_valid() (+4 more)

### Community 89 - "AgentAdvisor"
Cohesion: 0.07
Nodes (34): Harness maintenance — 2026-10-24, test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_explicit_evidence_pages_and_source_excerpts_survive_context_compaction(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory() (+26 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.14
Nodes (13): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+5 more)

### Community 91 - "closed_bar"
Cohesion: 0.18
Nodes (7): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 92 - "test_oauth.py"
Cohesion: 0.20
Nodes (17): Market Data & Authentication, response_json(), test_authorize_url_builds_documented_endpoint(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises(), test_refresh_access_token_returns_pair_with_browser_agent() (+9 more)

### Community 93 - "LiveBarFeed"
Cohesion: 0.11
Nodes (39): config(), credentials(), demo_feed_environment(), FakeClient, FakeStore, fixture, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously. (+31 more)

### Community 94 - "test_database_retention.py"
Cohesion: 0.18
Nodes (15): test_compaction_also_refuses_deactivating_or_unverified_units(), test_compaction_refuses_a_running_database_service(), test_legacy_row_count_pruning_preserves_unknown_jobs(), test_offline_compaction_reclaims_pages_without_changing_account_or_learning(), test_old_run_logs_expire_but_active_runs_survive(), test_old_trade_using_monitor_prefix_and_unknown_jobs_never_expire(), test_seven_day_rotation_preserves_learning_active_work_and_trade_keys(), test_terminal_job_output_expires_but_identity_and_references_survive() (+7 more)

### Community 95 - "ml_models.py"
Cohesion: 0.09
Nodes (20): ImportError, importlib, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample(), test_core_model_adapters_and_ensemble_probabilities() (+12 more)

### Community 96 - "LabStore"
Cohesion: 0.21
Nodes (5): LabStore, save(), add(), add(), save()

### Community 97 - "bits_runner.py"
Cohesion: 0.11
Nodes (27): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction(), test_market_windows_use_observed_data_and_handle_missing_source() (+19 more)

### Community 98 - "._note"
Cohesion: 0.09
Nodes (22): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), heartbeat(), on_connected(), on_disconnected(), on_message(), tick(), confirmed() (+14 more)

### Community 99 - "SQLiteAgentTranscriptStore"
Cohesion: 0.06
Nodes (41): Row, store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics(), decision(), parametrize (+33 more)

### Community 100 - "live_feed.py"
Cohesion: 0.11
Nodes (20): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+12 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.16
Nodes (26): skipif, memory(), notes(), open_drafts(), fixture, R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject() (+18 more)

### Community 102 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 103 - "atomic.py"
Cohesion: 0.17
Nodes (14): contextlib, fcntl, urllib_error, Atomic durable-file writes. One implementation, used by every writer in the…, _env_key(), _env_lock(), guard(), _env_value() (+6 more)

### Community 104 - "test_ctrader_demo.py"
Cohesion: 0.13
Nodes (18): adapter(), ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_duplicate_request_never_sends_a_second_transport_call(), test_long_decision_id_is_persisted_but_broker_id_fits(), test_reconcile_maps_persisted_broker_id_back_to_internal_id() (+10 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.17
Nodes (19): itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors(), test_selection_bias_computes_bh_and_aligned_fold_pbo() (+11 more)

### Community 106 - "TournamentDataset"
Cohesion: 0.21
Nodes (7): Path, frame_digest(), DataFrame, Path, Wait for a concurrent freeze of the same version to publish its manifest.…, Hash canonical timestamps, schema, and values independent of Parquet bytes., TournamentDataset

### Community 107 - "bounded_process"
Cohesion: 0.20
Nodes (6): test_process_timeout_and_output_bound(), test_process_workspace_limit_stops_writer(), test_process_workspace_symlink_is_rejected(), test_successful_shell_cannot_leave_background_writer(), bounded_process(), Drain to disk with a hard runtime and output bound, killing the process group.

### Community 108 - "ExperimentSpec"
Cohesion: 0.23
Nodes (15): E. Current 50,000-scenario architecture and benchmark, dotenv, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_replenishment_scans_past_existing_prefix(), ExperimentSpec (+7 more)

### Community 109 - "persist_tokens_env"
Cohesion: 0.12
Nodes (19): PathLike, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent…, Smoke test: concurrent writers never produce an unparseable env file., test_persist_tokens_appends_missing_key_and_sets_0600() (+11 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.11
Nodes (23): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+15 more)

### Community 111 - "BitsError"
Cohesion: 0.10
Nodes (39): main(), call(), envelope(), interrogation(), parametrize, boom(), shell_action(), test_bare_string_evidence_is_one_reference() (+31 more)

### Community 112 - "types"
Cohesion: 0.32
Nodes (5): test_failed_worker_schedule_rolls_back_without_retry(), test_research_advisories_do_not_disable_safe_software_releases(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), types, release_healthy()

### Community 113 - "Local audit — 2026-09-24"
Cohesion: 0.14
Nodes (12): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC (+4 more)

### Community 114 - "lab_tools.py"
Cohesion: 0.18
Nodes (23): ast, generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused() (+15 more)

### Community 115 - "test_experiment_registry.py"
Cohesion: 0.26
Nodes (13): spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity(), test_registry_requires_cockroach_database_url(), test_remote_error_can_requeue_owned_experiment() (+5 more)

### Community 116 - "BitsMemory"
Cohesion: 0.28
Nodes (4): BitsMemory, _note_sources(), _notes_base(), A specific next task for unresolved drafts; not a new research cycle.

### Community 117 - ".__init__"
Cohesion: 0.15
Nodes (5): EngineStore, MarketSource, Protocol, The narrow slice of the durable store the engine needs., TranscriptSink

### Community 118 - "graphify reference: extra exports and benchmark"
Cohesion: 0.20
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 119 - "json"
Cohesion: 0.19
Nodes (20): collections, dataclasses, io, json, numpy, pandas, pathlib, compare() (+12 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.19
Nodes (19): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal(), aligned_returns() (+11 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "Operator runbook: engine, live feed, and the visible harness"
Cohesion: 0.17
Nodes (11): 10. Related documents, 1. What was built and why, 2. Publish the Datadog workflow message stream (required for the thinking panel), 4. Enable the deterministic engine, 5. Restart the live view so the new observability is visible, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback (+3 more)

### Community 123 - "child_environment"
Cohesion: 0.28
Nodes (5): test_codex_environment_does_not_inherit_broker_credentials(), test_permission_profile_restricts_tools_to_training_workspace(), child_environment(), permission_arguments(), Deny reads outside the supplied training workspace and Python runtime. These…

### Community 124 - "DecisionSource"
Cohesion: 0.29
Nodes (5): DecisionSource, MarketDataSource, Protocol, Read-only source for the latest executable market observation., Read-only strategy proposal source; ``None`` means no proposed action.

### Community 126 - "README.md"
Cohesion: 0.13
Nodes (10): Codex permissions and conversation visibility, Display and storage, Verification, Bits agent instructions, Autonomous Agent, Legacy Datadog planner operations, Database maintenance and seven-day log rotation, Initial deployment (+2 more)

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.09
Nodes (22): Active Codex agent, Architecture, Aurum — Codex Autonomous Trading Lab, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+14 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.11
Nodes (18): Autonomous Harness, Bounded research recovery — 2026-10-26, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, Database retention — 2026-10-24, Evidence completion repair — 2026-10-27 (+10 more)

### Community 133 - "_datetime"
Cohesion: 0.10
Nodes (35): math, threading, typing, build_agent_registry(), canary_signal_tool(), handler(), _decision_id(), _mock_market_for_read() (+27 more)

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.18
Nodes (10): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Research continuity and maintenance — 2026-10-24 (+2 more)

### Community 135 - "_demo_automation_runner"
Cohesion: 0.31
Nodes (7): test_demo_automation_requires_explicit_positive_volume(), test_environment_config_is_disabled_unless_explicitly_true(), demo_automation(), _demo_automation_runner(), _demo_automation_status(), Run the explicitly enabled local-data paper-to-demo canary., DemoRunnerConfig

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.20
Nodes (10): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Operating model, Research activity chat — 2026-10-23, Research and automatic deployment (+2 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "Harness cleanup and improvement checklist — 2026-10-24"
Cohesion: 0.40
Nodes (4): Audit findings, Broker smoke shutdown follow-up, Harness cleanup and improvement checklist — 2026-10-24, Verification and deployment log

### Community 140 - "Requirements: reliable research-to-paper-trade workflow"
Cohesion: 0.12
Nodes (15): Delivery and operational boundaries, Delivery order after this merge, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Merge review — 2026-09-25, baseline `cba22b2`, Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit (+7 more)

### Community 141 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 142 - "cli.py"
Cohesion: 0.06
Nodes (57): argparse, test_demo_factory_binds_authoritative_paper_exposure(), agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., Validate the small, explicit JSON-schema subset used for tool boundaries., _validate_json(), agent_controller(), _agent_data_refresh_source() (+49 more)

### Community 144 - "transition"
Cohesion: 0.33
Nodes (6): test_counter_update_rolls_back_with_owning_state_transaction(), test_counters_survive_detail_eviction_and_ignore_duplicate_updates(), Small transactional counters; detailed evidence may expire independently., Called inside the transaction that writes the owning row., snapshot(), transition()

### Community 145 - "test_evidence_completion.py"
Cohesion: 0.11
Nodes (21): test_dashboard_registry_requires_database_url_and_never_passes_a_path(), invoke(), test_large_experiment_review_is_success_and_has_decision_summary(), test_large_result_retains_final_page_across_restart(), test_pagination_does_not_recursively_page_other_pages(), test_recent_retrieval_regression_is_detected_despite_old_calls(), test_recurring_verified_bottleneck_reopens_repair_without_erasing_history(), test_stagnant_review_cannot_repeat_forever() (+13 more)

### Community 146 - "_result_file"
Cohesion: 0.25
Nodes (8): Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case., The hash stops a later edit to the artifact redefining what was granted., _result_file(), test_a_recorded_validation_lets_the_same_engine_trade_without_a_restart(), test_a_validation_for_another_strategy_does_not_authorise_this_one(), test_record_validation_refuses_a_result_that_did_not_pass(), test_record_validation_requires_a_reason_and_pins_the_result_hash()

### Community 147 - "database_retention.py"
Cohesion: 0.43
Nodes (7): _job_outputs(), moment(), _old(), Seven-day operational log retention; learning and execution controls survive., _references(), collect(), _transcripts()

### Community 150 - "Research and measured self-improvement implementation plan"
Cohesion: 0.25
Nodes (7): Acceptance criteria, Delivery checklist, Deployment procedure, Final verification and deployment, Implementation evidence so far, Objective and boundaries, Research and measured self-improvement implementation plan

### Community 151 - "RecordingPostgres"
Cohesion: 0.20
Nodes (3): PostgresLikeTranscript, psycopg-like connection: one implicit transaction per block, committed or…, RecordingPostgres

### Community 152 - "build_features"
Cohesion: 0.11
Nodes (24): parametrize, test_return_features_exclude_entire_gap_straddling_horizon(), test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal() (+16 more)

### Community 153 - "agent_advisor.py"
Cohesion: 0.11
Nodes (34): copy, test_operator_release_measurements_yield_to_next_autonomous_release(), test_measured_bottleneck_seeds_one_backlog_item_and_preserves_baseline(), test_missing_baseline_cannot_be_claimed_and_inference_history_is_bounded(), test_observed_regression_cannot_be_labeled_improved(), test_recent_metric_window_does_not_bias_toward_retained_old_unknowns(), test_release_success_does_not_imply_measured_improvement(), Persistent Codex agenda and durable tool-call/result reasoning loop. The model… (+26 more)

### Community 155 - "engine_decision_id"
Cohesion: 0.50
Nodes (4): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), Durable identity for one engine decision. Derived from the bar, not from a…

### Community 156 - "HistoricalDataStore"
Cohesion: 0.07
Nodes (24): Historical deployment state — verified 2026-10-05, Interpreter guard for subcommands, OSError, test_store_rejects_invalid_ohlc(), test_store_roundtrip(), test_trendbar_delta_decoding(), CTraderHistoricalAdapter, HistoricalDataStore (+16 more)

### Community 157 - "engine_controller"
Cohesion: 0.50
Nodes (3): test_engine_status_reports_the_running_process_not_a_phantom(), engine_controller(), Operator and supervisor control for the deterministic trade engine.

### Community 161 - "Research program and measured improvement"
Cohesion: 0.25
Nodes (7): Decision cycle, Discovery and sources, Improvement measurement, Preregistration and execution, Release readiness and visibility, Research program and measured improvement, Storage and limitations

### Community 162 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 165 - "evidence_refs"
Cohesion: 0.38
Nodes (7): evidence_refs(), add(), ordered(), walk(), _legacy_draft(), Evidence references named by a (possibly malformed) payload: bounded, safe,…, The single pending record written by the previous release, as one open draft.

### Community 169 - "Delivery Stages"
Cohesion: 0.25
Nodes (5): Delivery Stages, Historical delivery and deployment notes, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval, Research notes (`bits-memory`, schema `xauusd.notes/1`)

### Community 171 - "Research completion and repair — 2026-10-26"
Cohesion: 0.33
Nodes (5): Diagnosis and implementation, Measured pre-deployment audit, Measurement and release handling, Research completion and repair — 2026-10-26, Verification and limitations

## Knowledge Gaps
- **201 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1202 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `_datetime`, `setup`, `cli.py`, `test_agent_loop.py`, `test_agent_view.py`, `agent_view.py`, `state_backup.py`, `test_demo_execution.py`, `InMemoryAgentTranscriptStore`, `lab.py`, `test_lab.py`, `canonical_json`, `test_demo_runner.py`, `PaperDecision`, `serialized`, `restart_policy`, `ContinuousAgentRunner`, `test_lab_dashboard.py`, `test_engine_loop.py`, `test_cli.py`, `PaperTradingEngine`, `SQLiteAgentTranscriptStore`, `.__init__`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `_datetime`, `ConfirmedBreakoutCanarySource`, `_demo_automation_runner`, `test_bits_capabilities.py`, `cli.py`, `test_agent_loop.py`, `StrategySpec`, `DataConfig`, `test_lab.py`, `datetime`, `test_retention.py`, `test_automation.py`, `read_quote`, `test_data.py`, `AgentTools`, `lab_api.py`, `test_cli.py`, `LiveBarFeed`, `live_feed.py`, `TournamentDataset`, `json`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `setup()` connect `setup` to `LabStore`, `test_lab.py`, `agent_advisor.py`, `SQLiteAgentTranscriptStore`, `canonical_json`, `PaperTrading`, `test_research_completion.py`, `transition`, `test_evidence_completion.py`, `lab_api.py`, `serialized`, `AgentAdvisor`, `test_database_retention.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `xauusd-research` to the rest of the system?**
  _201 weakly-connected nodes found - possible documentation gaps or missing edges._