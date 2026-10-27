# Graph Report - xauusd-evidence-release  (2026-10-27)

## Corpus Check
- 211 files · ~207,584 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: .service 9, (none) 7, .timer 3)

## Summary
- 3915 nodes · 10968 edges · 169 communities (148 shown, 21 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 571 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91084afc`
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
- cli.py
- ConversationStore
- CodexResearchClient
- PaperTrading
- ImprovementLedger
- research_program.py
- bits_capabilities.py
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- synthetic_bars
- test_bits_jobs.py
- XAUUSD discovery, incident, quantitative, and scaling audit
- lab_dashboard.py
- DataConfig
- OpenAICompatiblePlanner
- PaperDecision
- test_demo_execution.py
- InMemoryAgentTranscriptStore
- bars
- test_tournament_runner.py
- test_lab.py
- AdaptiveSearch
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- test_tournament_data.py
- ShadowTradingReadiness
- pathlib
- ._discover_account
- paper_trading.py
- ._fetch
- .record_rejection
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- test_retention.py
- test_demo_runner.py
- canonical_json
- test_automation.py
- CTraderDemoSafetyError
- Any
- CTraderDemoOpenApiTransport
- restart_policy
- DemoAutomationRunner
- test_ml.py
- ContinuousAgentRunner
- .connect
- test_lab_dashboard.py
- SecretFilter
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
- PaperToCTraderDemoCoordinator
- write_status
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- lab_sources.py
- AgentTools
- test_dashboard.py
- lab_market.py
- test_cli.py
- SQLitePaperTradingStore
- AgentAdvisor
- PaperTradingEngine
- closed_bar
- test_oauth.py
- LiveBarFeed
- setup
- ml_models.py
- LabStore
- test_bits_research.py
- ._note
- SQLiteAgentTranscriptStore
- LiveFeedConfig
- test_bits_memory_drafts.py
- .run
- CockroachAgentTranscriptStore
- test_ctrader_lifecycle.py
- test_weekly_report.py
- TournamentDataset
- bounded_process
- ExperimentSpec
- data_heal
- atomic_write_text
- BitsError
- core.py
- Local audit — 2026-09-24
- promote_tools
- CTraderVolumeConversion
- BitsMemory
- bits_memory_command
- graphify reference: extra exports and benchmark
- pandas
- portfolio_research.py
- .send
- StoreCorruptError
- build_parser
- DemoLifecycle
- ToolRegistry
- README.md
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- .__init__
- _datetime
- Persistent open-ended Codex agent
- main
- HarnessStore
- Codex autonomous trading lab
- Datadog Bits connection
- Harness cleanup and improvement checklist — 2026-10-24
- Requirements: reliable research-to-paper-trade workflow
- test_offline.py
- agent_controller
- CockroachHarnessStore
- transition
- agent_advisor.py
- research_runner.py
- .from_env
- harness-outcomes-plan-2026-10-23.md
- _MainContent
- Research and measured self-improvement implementation plan
- RecordingPostgres
- ExecutionConfig
- timestamp
- test_agent_daily.py
- engine_decision_id
- HistoricalDataStore
- engine_controller
- test_a_job_that_raises_is_recorded_as_failed_not_left_running
- test_lab_retention.py
- state_db_path
- Research program and measured improvement
- StateTransaction
- sklearn_base
- tarfile
- evidence_refs
- test_health_reports_degraded_when_the_state_store_is_unavailable
- Delivery Stages
- Research completion and repair — 2026-10-26

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `setup()` - 113 edges
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

## Communities (169 total, 21 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.12
Nodes (25): account(), An unclassified account is not a demo account. ``isLive`` is a proto3 optional…, The discriminator has to work on the actual SDK message, not just dicts., test_demo_accounts_empty_when_all_live(), test_demo_accounts_excludes_a_dict_without_the_flag(), test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo(), test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account(), test_is_error_extracts_code_and_description() (+17 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.17
Nodes (16): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+8 more)

### Community 2 - "OperationsManager"
Cohesion: 0.10
Nodes (19): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+11 more)

### Community 3 - "dashboard.py"
Cohesion: 0.09
Nodes (54): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), plotly_graph_objects (+46 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.09
Nodes (32): _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted., `monitor_error` used to be assigned and then read by nothing at all. (+24 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.05
Nodes (36): Operations, 5. Restart the live view so the new observability is visible, ExperimentStatus, frame(), read(), Path, create_app(), data_update_status() (+28 more)

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.16
Nodes (21): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+13 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.10
Nodes (16): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+8 more)

### Community 9 - "test_bits_capabilities.py"
Cohesion: 0.11
Nodes (37): R2 — P1: capability discovery failure must remain visible, fake_tool(), parametrize, The shell-job environment is discoverable from the environment jobs really get., Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_every_published_operation_is_a_real_cli_command() (+29 more)

### Community 10 - "cli.py"
Cohesion: 0.15
Nodes (27): collections, concurrent_futures, dataclasses, datetime, gzip, hashlib, io, json (+19 more)

### Community 11 - "ConversationStore"
Cohesion: 0.14
Nodes (14): test_capture_limit_is_explicit_and_remains_valid_json(), test_filters_before_capture_and_deduplicates_instruction_content(), test_large_exchange_is_retrievable_but_activity_stays_small(), test_read_only_paged_routes_and_inert_ui(), test_retention_limits_and_equal_timestamp_paging(), ConversationStore, attach_routes(), conversation_download() (+6 more)

### Community 12 - "CodexResearchClient"
Cohesion: 0.14
Nodes (14): Step 7d - MCP server (only if --mcp flag), test_full_access_launcher_preserves_session_and_compaction(), test_native_output_is_complete_and_private_reasoning_is_ignored(), test_harness_pins_luna_on_new_and_resumed_calls(), test_resumes_exact_thread_and_enables_native_compaction(), test_session_telemetry_tracks_native_compaction_incrementally(), test_thread_id_persisted_before_next_turn(), test_advisor_prompt_prioritizes_result_completion_over_generic_discovery() (+6 more)

### Community 13 - "PaperTrading"
Cohesion: 0.08
Nodes (53): test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_surfaces_a_monitor_error(), test_job_endpoint_pages_a_shell_capture(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_once_reports_a_refused_restart(), test_demo_automation_paper_only_skips_broker_dependencies(), test_paper_start_overrides_operator_stop() (+45 more)

### Community 14 - "ImprovementLedger"
Cohesion: 0.13
Nodes (18): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+10 more)

### Community 15 - "research_program.py"
Cohesion: 0.14
Nodes (34): test_blockers_are_classified_and_repair_has_priority(), test_completed_plan_legacy_evidence_is_backfilled_only_by_exact_id(), test_old_workspace_exact_evidence_can_be_recorded_after_log_rotation(), test_only_two_plans_may_execute_and_success_must_be_interpreted(), plan(), test_compact_context_pages_full_design_without_truncating_evidence(), test_completed_findings_accumulate_lessons_without_recounting(), test_discovery_insights_require_real_retrieval_and_do_not_claim_availability() (+26 more)

### Community 16 - "bits_capabilities.py"
Cohesion: 0.09
Nodes (34): Datadog Bits operations, platform, shlex, test_shell_environment_keeps_the_latest_refreshed_tokens(), test_shell_path_prepends_service_interpreter_and_declared_directories(), cli_prefix(), data_access(), _error_code() (+26 more)

### Community 17 - "Any"
Cohesion: 0.10
Nodes (12): Client, failed(), issue(), failed(), issue(), observe(), succeeded(), CTraderDemoStore (+4 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.10
Nodes (45): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), A ticking agent must not be served as stopped. The engine's startup reconcile…, refresh_config(), refresh_runner() (+37 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.14
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.08
Nodes (28): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+20 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.05
Nodes (39): _feed(), _harness_client(), paper_trading(), fixture, parametrize, The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., `limit` alone does not bound a response. A shell-job step carries a captured… (+31 more)

### Community 22 - "synthetic_bars"
Cohesion: 0.08
Nodes (49): parametrize, test_return_features_exclude_entire_gap_straddling_horizon(), test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios() (+41 more)

### Community 23 - "test_bits_jobs.py"
Cohesion: 0.20
Nodes (17): action(), bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes…, The executor enforces the ceiling, not only the caller that sets it. The…, test_a_job_never_exceeds_the_server_timeout_ceiling(), test_a_running_job_publishes_partial_output(), test_bits_jobs_prune_drops_old_terminal_rows_only() (+9 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (46): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+38 more)

### Community 25 - "lab_dashboard.py"
Cohesion: 0.40
Nodes (4): FastAPI, fastapi_responses, inspect, Read-only Codex research command centre; all market content is untrusted text.

### Community 26 - "DataConfig"
Cohesion: 0.11
Nodes (25): test_data_update_does_not_retry_auth_errors(), unauthorized(), downloader_config(), validate() is no longer a one-time check performed only by from_env(). The…, test_download_does_not_retry_non_token_auth_error(), fake_fetch(), test_download_does_not_retry_without_a_refresh_token(), test_download_refreshes_once_then_retries_in_a_fresh_process() (+17 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.33
Nodes (9): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError, Any, ValueError (+1 more)

### Community 28 - "PaperDecision"
Cohesion: 0.20
Nodes (20): test_paper_endpoint_reflects_accepted_fill(), decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive() (+12 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.12
Nodes (25): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+17 more)

### Community 30 - "InMemoryAgentTranscriptStore"
Cohesion: 0.11
Nodes (7): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), test_base_runner_records_codes_for_planner_and_tick_errors(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store., Mirror of the SQLite retention so both backends behave the same., Family-scoped mirror of the SQL stores: never close another family's run.

### Community 31 - "bars"
Cohesion: 0.17
Nodes (22): bars(), parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate(), test_dataset_advances_only_to_a_wholly_new_cohort() (+14 more)

### Community 32 - "test_tournament_runner.py"
Cohesion: 0.12
Nodes (15): Dependence-aware bootstrap validation — 2026-08-21, test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed() (+7 more)

### Community 33 - "test_lab.py"
Cohesion: 0.09
Nodes (40): parametrize, qualified_candidate(), quote(), test_codex_contract_rejects_unknown_fields_and_overlarge_requests(), test_evidence_relations_are_checked_beyond_digest(), test_forward_coverage_rejects_short_observation_despite_fixed_deadline(), test_forward_coverage_uses_new_york_market_minutes_and_accepts_complete_week(), test_forward_window_is_scored_once_then_rejected() (+32 more)

### Community 34 - "AdaptiveSearch"
Cohesion: 0.19
Nodes (14): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+6 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.15
Nodes (11): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+3 more)

### Community 37 - "test_tournament_data.py"
Cohesion: 0.09
Nodes (29): dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version…, A freeze killed mid-write must not hang the next one, nor quietly pass., A backtester or cost change must invalidate stored results. Both were hardcoded…, test_a_version_directory_with_no_manifest_fails_loudly() (+21 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 39 - "pathlib"
Cohesion: 0.07
Nodes (50): ast, base64, contextlib, dotenv, fcntl, ipaddress, pathlib, pytest (+42 more)

### Community 40 - "._discover_account"
Cohesion: 0.24
Nodes (10): app_failed(), account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), Authenticate the application, then resolve the demo account and symbol.… (+2 more)

### Community 41 - "paper_trading.py"
Cohesion: 0.10
Nodes (27): sqlite3, seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), Explicit operator-only, flat paper account rebase; no research reset., rebase(), FastAPI live view of the autonomous agent's visible thinking process., AgentAlreadyRunning (+19 more)

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - ".record_rejection"
Cohesion: 0.21
Nodes (14): apply(), apply(), apply(), _brief(), _close(), _empty_drafts(), load_drafts(), _merge_refs() (+6 more)

### Community 49 - "test_retention.py"
Cohesion: 0.08
Nodes (54): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(), archive(), _local_backups() (+46 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.11
Nodes (22): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+14 more)

### Community 51 - "canonical_json"
Cohesion: 0.19
Nodes (19): _check_categories(), _check_draft_ids(), _check_entry(), check_notes(), _is_current_notes(), issue(), _key_path(), _kind() (+11 more)

### Community 52 - "test_automation.py"
Cohesion: 0.09
Nodes (31): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+23 more)

### Community 53 - "CTraderDemoSafetyError"
Cohesion: 0.08
Nodes (28): stopped_demo_adapter(), test_host_and_environment_rejections_are_fail_closed(), Transport, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send() (+20 more)

### Community 54 - "Any"
Cohesion: 0.10
Nodes (11): Operating model, 1. What was built and why, CockroachPaperTradingStore, _now(), transition(), transition(), PaperTradingStore, Any (+3 more)

### Community 55 - "CTraderDemoOpenApiTransport"
Cohesion: 0.14
Nodes (19): FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(), test_open_api_transport_fails_reconciliation_on_an_error_reply(), test_open_api_transport_reads_symbol_volume_metadata(), test_open_api_transport_rejects_non_demo_before_constructing_client() (+11 more)

### Community 56 - "restart_policy"
Cohesion: 0.13
Nodes (15): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+7 more)

### Community 57 - "DemoAutomationRunner"
Cohesion: 0.26
Nodes (5): DemoAutomationRunner, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 58 - "test_ml.py"
Cohesion: 0.12
Nodes (25): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined() (+17 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.10
Nodes (15): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, BaseException, Protocol (+7 more)

### Community 60 - ".connect"
Cohesion: 0.19
Nodes (6): Connection, Row, _connect(), _now(), Any, Close the caller's own interrupted runs left 'running' by a killed process.…

### Community 61 - "test_lab_dashboard.py"
Cohesion: 0.11
Nodes (8): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), test_statistics_counts_retained_evidence_without_claiming_success(), _age(), Counts only bounded retained evidence; never infer remote execution success., retained_statistics()

### Community 62 - "SecretFilter"
Cohesion: 0.14
Nodes (10): jobs(), fixture, A failed preview is observability, and observability must not break the job., A thread registered but never started raises on join and aborted shutdown., test_publish_progress_failure_does_not_disturb_the_job(), test_shell_job_stop_does_not_raise_on_an_unstarted_worker(), Write a running job's partial output so a reader can watch it. The record keeps…, Suppress whole values, not partial/redacted credentials. Not a shell sandbox. (+2 more)

### Community 63 - "read_quote"
Cohesion: 0.21
Nodes (15): ctrader_open_api_messages_openapimessages_pb2, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time(), test_sample_once_second_history_retention_and_hard_bound(), test_wrong_symbol_and_out_of_order_quote_refused() (+7 more)

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
Cohesion: 0.11
Nodes (14): error_details(), excerpt(), BaseException, Payload-free classification of an exception for events and heartbeats.…, guidance_revision(), BitsAgentRunner, Any, Retrieval-loop evidence for the heartbeat, which this file writes every tick. A… (+6 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.16
Nodes (20): at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from…, Synthetic M1 bars stamped at bar open, only while the session gate is open., session_bars(), test_a_week_whose_data_stops_early_is_not_complete(), test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected(), test_pandas_weekly_labels_disagree_with_session_weeks() (+12 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.06
Nodes (53): errno, _bars(), demo_env(), frame(), minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.… (+45 more)

### Community 77 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.18
Nodes (11): handler(), NormalizedDecision, PaperToCTraderDemoCoordinator, Any, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it., Strategy proposal expressed in configured paper-trading quantity units. (+3 more)

### Community 78 - "write_status"
Cohesion: 0.24
Nodes (15): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), bits_alerts() (+7 more)

### Community 79 - "test_bits_memory.py"
Cohesion: 0.15
Nodes (25): codes(), entry(), memory(), observed_wrapper_payload(), open_drafts(), fixture, Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection() (+17 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.07
Nodes (50): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., An oversized proposal must be visibly refused, not silently trimmed. Clamping…, The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise. (+42 more)

### Community 82 - "lab_sources.py"
Cohesion: 0.12
Nodes (11): html, html_parser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), urllib_parse, urllib_request, NoRedirect (+3 more)

### Community 83 - "AgentTools"
Cohesion: 0.17
Nodes (18): Store, test_dependency_install_requires_pins(), test_dependency_install_targets_scratch_only(), test_domain_configuration(), test_fetch_rejects_private_dns(), test_market_observe_excludes_frozen_and_forming_bars(), test_market_observe_without_frozen_boundary_reveals_no_history(), test_remote_job_identity_is_action_derived() (+10 more)

### Community 84 - "test_dashboard.py"
Cohesion: 0.10
Nodes (11): copy, MemoryConnection, MemoryCursor, setup_files(), test_dashboard_reads_latest_run_and_equity(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature() (+3 more)

### Community 86 - "lab_market.py"
Cohesion: 0.24
Nodes (12): pyarrow_parquet, test_dashboard_uses_metadata_and_bounded_tail_not_store_read(), xauusd, chart(), _data(), chart_bars(), coverage(), _file() (+4 more)

### Community 87 - "test_cli.py"
Cohesion: 0.11
Nodes (26): DemoTransport, _isolated_bits_state(), no_broker(), Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., Without this the command exists but nothing runs it, so a hole still sits for…, An interior hole is a smaller problem than a refresh reported as failed. The…, _run_cli() (+18 more)

### Community 88 - "SQLitePaperTradingStore"
Cohesion: 0.15
Nodes (14): decision(), parametrize, Validation must not reject a real account, including a running one., A row that parses but cannot be evaluated is corruption, not an account. Before…, test_paper_from_env_defaults_to_local_sqlite_store(), test_sqlite_integrity_check_detects_corruption(), test_sqlite_paper_store_corrupt_state_fails_closed(), test_sqlite_paper_store_integrity_check_reports_ok() (+6 more)

### Community 89 - "AgentAdvisor"
Cohesion: 0.06
Nodes (39): Harness maintenance — 2026-10-24, test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_explicit_evidence_pages_and_source_excerpts_survive_context_compaction(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory() (+31 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.09
Nodes (18): EngineDecision, EngineStore, MarketSource, PaperTradingEngine, Any, Protocol, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates. (+10 more)

### Community 91 - "closed_bar"
Cohesion: 0.18
Nodes (7): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 92 - "test_oauth.py"
Cohesion: 0.06
Nodes (47): PathLike, Market Data & Authentication, FakeResponse, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent… (+39 more)

### Community 93 - "LiveBarFeed"
Cohesion: 0.11
Nodes (39): config(), credentials(), demo_feed_environment(), FakeClient, FakeStore, fixture, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously. (+31 more)

### Community 94 - "setup"
Cohesion: 0.12
Nodes (32): test_account_only_reset_preserves_research_and_stop(), test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), test_compaction_also_refuses_deactivating_or_unverified_units() (+24 more)

### Community 95 - "ml_models.py"
Cohesion: 0.09
Nodes (20): ImportError, importlib, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample(), test_core_model_adapters_and_ensemble_probabilities() (+12 more)

### Community 96 - "LabStore"
Cohesion: 0.18
Nodes (7): test_snapshot_expiry_deletes_backend_rows(), events(), LabStore, save(), add(), add(), save()

### Community 97 - "test_bits_research.py"
Cohesion: 0.11
Nodes (26): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+18 more)

### Community 98 - "._note"
Cohesion: 0.09
Nodes (24): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), heartbeat(), on_connected(), on_disconnected(), on_message(), tick(), confirmed() (+16 more)

### Community 99 - "SQLiteAgentTranscriptStore"
Cohesion: 0.12
Nodes (22): The deterministic engine writes to the same `agent_runs` table. Taking the…, test_status_and_health_select_the_agent_run_not_a_newer_engine_run(), The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is., The owner of a run is the only authority on whether it is live., The transcript had no DELETE anywhere and gained a row per heartbeat. 14,350…, Pruning must not delete content a connected reader has not displayed yet. The…, test_agent_start_leaves_a_running_engine_run_alone() (+14 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.12
Nodes (17): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+9 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.16
Nodes (26): skipif, notes(), open_drafts(), R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject(), test_concurrent_writers_with_the_same_base_cannot_both_win(), writer() (+18 more)

### Community 102 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 103 - "CockroachAgentTranscriptStore"
Cohesion: 0.23
Nodes (4): CockroachAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row; see the SQLite store.

### Community 104 - "test_ctrader_lifecycle.py"
Cohesion: 0.13
Nodes (24): adapter(), test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_duplicate_request_never_sends_a_second_transport_call(), test_long_decision_id_is_persisted_but_broker_id_fits(), test_reconcile_maps_persisted_broker_id_back_to_internal_id(), test_recovery_failure_kills_and_blocks_execution(), test_unresolved_pre_crash_request_fails_recovery_closed() (+16 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.17
Nodes (17): Gate-failure and near-pass analytics — 2026-08-21, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors(), test_selection_bias_computes_bh_and_aligned_fold_pbo(), test_selection_bias_reports_score_distribution_and_missing_controls() (+9 more)

### Community 106 - "TournamentDataset"
Cohesion: 0.23
Nodes (7): Path, frame_digest(), DataFrame, Path, Wait for a concurrent freeze of the same version to publish its manifest.…, Hash canonical timestamps, schema, and values independent of Parquet bytes., TournamentDataset

### Community 107 - "bounded_process"
Cohesion: 0.13
Nodes (11): test_process_timeout_and_output_bound(), test_process_workspace_limit_stops_writer(), test_process_workspace_symlink_is_rejected(), test_successful_shell_cannot_leave_background_writer(), test_codex_environment_does_not_inherit_broker_credentials(), test_permission_profile_restricts_tools_to_training_workspace(), bounded_process(), Drain to disk with a hard runtime and output bound, killing the process group. (+3 more)

### Community 108 - "ExperimentSpec"
Cohesion: 0.21
Nodes (15): E. Current 50,000-scenario architecture and benchmark, itertools, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_replenishment_scans_past_existing_prefix(), ExperimentSpec (+7 more)

### Community 109 - "data_heal"
Cohesion: 0.24
Nodes (12): _heal_args(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _store_with_windows(), test_data_heal_defers_a_window_that_does_not_fit_the_budget(), test_data_heal_downloads_an_interior_window(), test_data_heal_dry_run_never_contacts_the_broker() (+4 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.06
Nodes (36): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+28 more)

### Community 111 - "BitsError"
Cohesion: 0.07
Nodes (49): 10. Related documents, 2. Publish the Datadog workflow message stream (required for the thinking panel), 4. Enable the deterministic engine, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback, Engine control, Operator runbook: engine, live feed, and the visible harness (+41 more)

### Community 112 - "core.py"
Cohesion: 0.27
Nodes (8): test_backtest(), campaign(), event_backtest(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 113 - "Local audit — 2026-09-24"
Cohesion: 0.14
Nodes (12): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC (+4 more)

### Community 114 - "promote_tools"
Cohesion: 0.19
Nodes (21): generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused(), test_symlinks_and_size_limit_refuse_execution() (+13 more)

### Community 115 - "CTraderVolumeConversion"
Cohesion: 0.18
Nodes (6): _ctrader_demo_adapter(), expected_volume(), CTraderVolumeConversion, DemoExecutor, Protocol, Explicit conversion from paper quantity units to cTrader volume-in-cents units.

### Community 116 - "BitsMemory"
Cohesion: 0.21
Nodes (8): memory(), fixture, _age_seconds(), BitsMemory, _note_sources(), _notes_base(), A specific next task for unresolved drafts; not a new research cycle., repair_reasons()

### Community 117 - "bits_memory_command"
Cohesion: 0.22
Nodes (6): parse_notes_input(), Strictly parse CLI input; malformed JSON is reported by line and column only., CLI write path: unparseable input is retained as text when it is safe to keep., bits_memory_command(), Exit 0 on success, 2 for a rejected payload (fix and retry), 1 for an…, _read_notes_input()

### Community 118 - "graphify reference: extra exports and benchmark"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 119 - "pandas"
Cohesion: 0.17
Nodes (17): argparse, numpy, operator, pandas, compare(), main(), Path, Compare two or more compute-job result directories without mutating them. (+9 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.22
Nodes (19): Portfolio and regime research — 2026-08-21, test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal() (+11 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "StoreCorruptError"
Cohesion: 0.13
Nodes (11): 9. Recovering the market-data store, OSError, `error_type: OSError` with `error_code: null` was undiagnosable. That is all…, test_a_corrupt_store_is_reported_as_corrupt_not_as_a_bare_oserror(), test_classify_store_error_names_a_full_disk_and_refuses_to_guess(), classify_store_error(), BaseException, The newest bar in the store, reading the index column only. `data update` needs… (+3 more)

### Community 123 - "build_parser"
Cohesion: 0.25
Nodes (8): ArgumentParser, Bits shell environment (`bits-capabilities`), test_the_heal_command_is_in_the_cli_grammar(), test_the_raw_retention_command_is_in_the_cli_grammar(), test_the_rebuild_command_is_in_the_cli_grammar(), cli_commands(), build_parser(), The complete CLI grammar; also used to publish supported operations.

### Community 124 - "DemoLifecycle"
Cohesion: 0.20
Nodes (4): DemoLifecycle, MarketDataSource, Protocol, Read-only source for the latest executable market observation.

### Community 125 - "ToolRegistry"
Cohesion: 0.36
Nodes (3): Immutable-in-practice allow-list. Only the application can register tools., ToolRegistry, ToolSpec

### Community 126 - "README.md"
Cohesion: 0.13
Nodes (10): Codex permissions and conversation visibility, Display and storage, Verification, Bits agent instructions, Autonomous Agent, Legacy Datadog planner operations, Database maintenance and seven-day log rotation, Initial deployment (+2 more)

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.09
Nodes (22): Active Codex agent, Architecture, Aurum — Codex Autonomous Trading Lab, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+14 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.10
Nodes (20): Autonomous Harness, Bounded research recovery — 2026-10-26, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, Database retention — 2026-10-24, Evidence completion repair — 2026-10-27 (+12 more)

### Community 133 - "_datetime"
Cohesion: 0.09
Nodes (32): Engineering, functools, threading, UTC goal/display boundaries, independent of account and risk state., utc_day(), _archive(), Independent exploratory paper accounts; never a promotion or broker path., tick() (+24 more)

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.18
Nodes (10): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Research continuity and maintenance — 2026-10-24 (+2 more)

### Community 135 - "main"
Cohesion: 0.09
Nodes (21): test_bits_notes_only_does_not_repeat_history(), test_demo_automation_disabled_returns_status_without_constructing_clients(), test_demo_automation_start_keeps_the_switch_stopped_when_reconciliation_fails(), test_demo_automation_start_reconciles_then_clears_only_the_demo_switch(), test_demo_automation_status_reports_paper_only_flag(), test_state_integrity_backup_restore_round_trip(), bits_job_page(), cftc_point_in_time() (+13 more)

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

### Community 141 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 142 - "agent_controller"
Cohesion: 0.09
Nodes (27): parametrize, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An…, test_agent_config_rejects_non_finite_limits(), agent_transcript_store_from_env(), _positive_float(), Transcript store for the configured backend (local SQLite by default)., agent_controller(), _agent_data_refresh_source() (+19 more)

### Community 144 - "transition"
Cohesion: 0.33
Nodes (6): test_counter_update_rolls_back_with_owning_state_transaction(), test_counters_survive_detail_eviction_and_ignore_duplicate_updates(), Small transactional counters; detailed evidence may expire independently., Called inside the transaction that writes the owning row., snapshot(), transition()

### Community 145 - "agent_advisor.py"
Cohesion: 0.10
Nodes (30): test_improvement_cannot_claim_old_release_as_new_work(), test_inspection_and_failed_remote_work_are_not_progress(), test_outcome_requires_existing_successful_evidence_and_deduplicates(), test_improvement_has_one_working_slot_and_protected_fix_is_escalated(), test_operator_release_measurements_yield_to_next_autonomous_release(), test_plan_keeps_evidence_and_code_provenance_after_call_log_rotation(), test_training_export_preserves_utc_index_and_reports_gaps(), payload() (+22 more)

### Community 146 - "research_runner.py"
Cohesion: 0.33
Nodes (4): csv, test_runner_costs_gaps_and_undefined_metrics(), Dependency-free, training-only tc02 baseline runner. Prints evidence, never…, run()

### Community 147 - ".from_env"
Cohesion: 0.29
Nodes (6): 7.1 Code — one relaxation (small, tested), 7.2 Deploy — one systemd unit (mirror rule applies), 7.3 Config/docs, 7. Required changes (tracked, not yet implemented), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout()

### Community 149 - "_MainContent"
Cohesion: 0.29
Nodes (3): HTMLParser, _MainContent, Prefer a publisher's explicit content region over repeated site menus.

### Community 150 - "Research and measured self-improvement implementation plan"
Cohesion: 0.25
Nodes (7): Acceptance criteria, Delivery checklist, Deployment procedure, Final verification and deployment, Implementation evidence so far, Objective and boundaries, Research and measured self-improvement implementation plan

### Community 151 - "RecordingPostgres"
Cohesion: 0.20
Nodes (3): PostgresLikeTranscript, psycopg-like connection: one implicit transaction per block, committed or…, RecordingPostgres

### Community 152 - "ExecutionConfig"
Cohesion: 0.13
Nodes (28): main(), Secret-free deterministic parity fixture for the runtime container., bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,… (+20 more)

### Community 153 - "timestamp"
Cohesion: 0.08
Nodes (36): invoke(), test_blocked_historical_plan_cannot_preempt_current_completed_result(), test_large_experiment_review_is_success_and_has_decision_summary(), test_large_result_retains_final_page_across_restart(), execute(), test_pagination_does_not_recursively_page_other_pages(), test_recent_retrieval_regression_is_detected_despite_old_calls(), test_recurring_verified_bottleneck_reopens_repair_without_erasing_history() (+28 more)

### Community 154 - "test_agent_daily.py"
Cohesion: 0.33
Nodes (3): test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), roll_daily_goal()

### Community 155 - "engine_decision_id"
Cohesion: 0.50
Nodes (4): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), Durable identity for one engine decision. Derived from the bar, not from a…

### Community 156 - "HistoricalDataStore"
Cohesion: 0.10
Nodes (19): Interpreter guard for subcommands, stream(), events(), CTraderHistoricalAdapter, HistoricalDataStore, Any, DataFrame, Path (+11 more)

### Community 157 - "engine_controller"
Cohesion: 0.50
Nodes (3): test_engine_status_reports_the_running_process_not_a_phantom(), engine_controller(), Operator and supervisor control for the deterministic trade engine.

### Community 159 - "test_lab_retention.py"
Cohesion: 0.60
Nodes (5): store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics()

### Community 161 - "Research program and measured improvement"
Cohesion: 0.25
Nodes (7): Decision cycle, Discovery and sources, Improvement measurement, Preregistration and execution, Release readiness and visibility, Research program and measured improvement, Storage and limitations

### Community 162 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 165 - "evidence_refs"
Cohesion: 0.60
Nodes (5): evidence_refs(), add(), ordered(), walk(), Evidence references named by a (possibly malformed) payload: bounded, safe,…

### Community 169 - "Delivery Stages"
Cohesion: 0.25
Nodes (5): Delivery Stages, Historical delivery and deployment notes, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval, Research notes (`bits-memory`, schema `xauusd.notes/1`)

### Community 171 - "Research completion and repair — 2026-10-26"
Cohesion: 0.33
Nodes (5): Diagnosis and implementation, Measured pre-deployment audit, Measurement and release handling, Research completion and repair — 2026-10-26, Verification and limitations

## Knowledge Gaps
- **201 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+196 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1202 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `_datetime`, `ExperimentRegistry`, `main`, `cli.py`, `agent_controller`, `test_agent_loop.py`, `test_agent_view.py`, `PaperDecision`, `test_demo_execution.py`, `InMemoryAgentTranscriptStore`, `test_lab.py`, `test_health_reports_degraded_when_the_state_store_is_unavailable`, `paper_trading.py`, `test_demo_runner.py`, `Any`, `restart_policy`, `ContinuousAgentRunner`, `test_lab_dashboard.py`, `PaperToCTraderDemoCoordinator`, `test_engine_loop.py`, `test_cli.py`, `SQLitePaperTradingStore`, `PaperTradingEngine`, `setup`, `SQLiteAgentTranscriptStore`, `data_heal`, `CTraderVolumeConversion`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `Repository Operating Rules`, `ConfirmedBreakoutCanarySource`, `main`, `cli.py`, `agent_controller`, `bits_capabilities.py`, `test_agent_loop.py`, `synthetic_bars`, `DataConfig`, `bars`, `test_lab.py`, `pathlib`, `test_retention.py`, `test_automation.py`, `test_ml.py`, `read_quote`, `test_data.py`, `AgentTools`, `lab_market.py`, `test_cli.py`, `LiveBarFeed`, `LiveFeedConfig`, `TournamentDataset`, `core.py`, `pandas`, `StoreCorruptError`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `LiveBarFeed` connect `LiveBarFeed` to `._note`, `LiveFeedConfig`, `pathlib`, `._discover_account`, `cli.py`, `test_data.py`, `AgentAdvisor`, `DataConfig`, `closed_bar`, `HistoricalDataStore`, `read_quote`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `$schema`, `plugin`, `xauusd-research` to the rest of the system?**
  _201 weakly-connected nodes found - possible documentation gaps or missing edges._