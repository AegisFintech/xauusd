# Graph Report - xauusd-dashboard-release  (2026-10-23)

## Corpus Check
- 181 files · ~189,496 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .service 8, (none) 7, .timer 2)

## Summary
- 3630 nodes · 10145 edges · 164 communities (144 shown, 20 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 536 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f42cac68`
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
- agent_loop.py
- MemoryRegistry
- pytest
- test_ctrader_demo.py
- ExecutionConfig
- ._signal
- PaperTrading
- ImprovementLedger
- CockroachAgentTranscriptStore
- test_session_reset.py
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- test_validation.py
- test_bits_jobs.py
- XAUUSD discovery, incident, quantitative, and scaling audit
- run
- DataConfig
- OpenAICompatiblePlanner
- state_backup.py
- test_demo_execution.py
- test_oauth.py
- TournamentDataset
- test_search_space.py
- test_lab.py
- memory_registry.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- synthetic_bars
- ShadowTradingReadiness
- build_features
- InMemoryAgentTranscriptStore
- engine_loop.py
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
- PaperDecision
- CTraderVolumeConversion
- restart_policy
- create_app
- DemoLifecycle
- ContinuousAgentRunner
- SQLiteAgentTranscriptStore
- verify_result_parity.py
- EngineConfig
- _registry_schema_valid
- CTraderOpenApiConfig
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
- agent_controller
- cli.py
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- bits_capabilities.py
- AgentTools
- lab_api.py
- agent_experiments.py
- test_cli.py
- BitsMemory
- test_agent_advisor.py
- PaperTradingEngine
- test_bits_capabilities.py
- HistoricalDataStore
- test_live_feed.py
- .run
- PostgresConnection
- Signals
- bits_runner.py
- ._note
- test_local_state.py
- LiveFeedConfig
- test_bits_memory_drafts.py
- BitsStore
- _datetime
- CTraderDemoStore
- test_weekly_report.py
- Any
- canonical_json
- file_lock
- bits_memory.py
- atomic_write_text
- BitsError
- LabStore
- ._discover_account
- promote_tools
- fetch_source
- closed_bar
- .write_notes
- DemoAutomationRunner
- read_quote
- portfolio_research.py
- .send
- EngineeringManager
- test_lab_dashboard.py
- data_heal
- evidence_refs
- Local audit — 2026-09-24
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- test_dashboard.py
- test_agent_release_worker.py
- Persistent open-ended Codex agent
- /graphify
- _bars
- Codex autonomous trading lab
- Datadog Bits connection
- weekly_bars
- StoreCorruptError
- .path
- ResearchHarness
- Merge review — 2026-09-25, baseline `cba22b2`
- atomic_write_json
- Step 3 - Extract entities and relationships
- PaperToCTraderDemoCoordinator
- SecretFilter
- harness-outcomes-plan-2026-10-23.md
- demo_feed_environment
- _download_with_retry
- DemoRunnerConfig
- InMemoryHarnessStore
- RecordingPostgres
- CockroachHarnessStore
- StateTransaction
- CTraderHistoricalAdapter
- cTrader SDK and protocol review (no broker connection)
- PaperTradingStore
- test_lab_retention.py
- ._authenticate
- .capture_scaling_checkpoints
- WeeklyTournamentReport
- _command_failure

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `MemoryRegistry` - 89 edges
3. `HistoricalDataStore` - 76 edges
4. `ExperimentRegistry` - 76 edges
5. `SQLiteAgentTranscriptStore` - 72 edges
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
- `Order lifecycle and errors — follow-up #15` --references--> `is_error()`  [INFERRED]
  docs/local-handoff-audit-2026-09-24.md → xauusd/ctrader_auth.py
- `R3 — P1: make experiment continuity work with the deployed backend` --references--> `ExperimentRegistry`  [INFERRED]
  requirements.md → xauusd/experiment_registry.py
- `Portfolio and regime research — 2026-08-21` --references--> `PortfolioResearch`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → xauusd/portfolio_research.py

## Import Cycles
- None detected.

## Communities (164 total, 20 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.13
Nodes (20): account(), An unclassified account is not a demo account. ``isLive`` is a proto3 optional…, The discriminator has to work on the actual SDK message, not just dicts., test_demo_accounts_empty_when_all_live(), test_demo_accounts_excludes_a_dict_without_the_flag(), test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo(), test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account(), test_is_error_extracts_code_and_description() (+12 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.29
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "main"
Cohesion: 0.08
Nodes (24): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+16 more)

### Community 3 - "dashboard.py"
Cohesion: 0.07
Nodes (59): asyncio, FastAPI, fastapi_responses, fastapi_security, get, HTTPBasicCredentials, inspect, middleware (+51 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.08
Nodes (34): test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted. (+26 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.15
Nodes (7): ExperimentStatus, Path, ExperimentRegistry, Any, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool., Path

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "agent_loop.py"
Cohesion: 0.12
Nodes (33): test_canary_signal_tool_returns_side(), append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once() (+25 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.10
Nodes (16): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+8 more)

### Community 9 - "pytest"
Cohesion: 0.06
Nodes (35): ImportError, importlib, pytest, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing (+27 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.09
Nodes (36): adapter(), FakeClient, ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_configured_account_id_bypasses_account_list_scope(), test_duplicate_request_never_sends_a_second_transport_call() (+28 more)

### Community 11 - "ExecutionConfig"
Cohesion: 0.07
Nodes (63): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, numpy, pandas, sklearn_metrics, socket, main() (+55 more)

### Community 12 - "._signal"
Cohesion: 0.33
Nodes (5): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), Durable identity for one engine decision. Derived from the bar, not from a…, Ask the deterministic strategy for a direction, and size it here. The strategy…

### Community 13 - "PaperTrading"
Cohesion: 0.08
Nodes (52): test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_surfaces_a_monitor_error(), test_job_endpoint_pages_a_shell_capture(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_once_reports_a_refused_restart(), test_demo_automation_paper_only_skips_broker_dependencies(), test_paper_start_overrides_operator_stop() (+44 more)

### Community 14 - "ImprovementLedger"
Cohesion: 0.13
Nodes (18): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+10 more)

### Community 15 - "CockroachAgentTranscriptStore"
Cohesion: 0.19
Nodes (6): CockroachAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row; see the SQLite store., The run family a run_id belongs to: ``agent_`` or ``engine_``. The agent and…, _run_family()

### Community 16 - "test_session_reset.py"
Cohesion: 0.25
Nodes (10): seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), AgentAlreadyRunning, AgentLock, Single process per container; the lock is runtime coordination, not state., bits_recover(), Explicit operator acknowledgement after reconciling uncertain side effects. (+2 more)

### Community 17 - "Any"
Cohesion: 0.17
Nodes (12): CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded(), Any (+4 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.11
Nodes (36): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), A ticking agent must not be served as stopped. The engine's startup reconcile…, refresh_config(), refresh_runner() (+28 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.15
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (23): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+15 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.05
Nodes (39): _feed(), _harness_client(), paper_trading(), fixture, parametrize, The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., The health endpoint is the observability surface; it must not raise. An… (+31 more)

### Community 22 - "test_validation.py"
Cohesion: 0.10
Nodes (31): Dependence-aware bootstrap validation — 2026-08-21, An empty training window must fail loudly, not look like a negative result., The embargo must reach the report, not just the helper. `walk_forward_splits`…, The negative path was never asserted, which is why several real defects…, A 30-bar rolling feature reaches across the split boundary. The last…, test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration() (+23 more)

### Community 23 - "test_bits_jobs.py"
Cohesion: 0.09
Nodes (27): action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes…, A failed preview is observability, and observability must not break the job., A post-spawn exception must not strand the row as `running` forever. `state`… (+19 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (45): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20, Complete auxiliary backup integrity — 2026-08-21 (+37 more)

### Community 26 - "DataConfig"
Cohesion: 0.14
Nodes (21): test_data_update_does_not_retry_auth_errors(), unauthorized(), demo_env(), downloader_config(), validate() is no longer a one-time check performed only by from_env(). The…, test_download_does_not_retry_non_token_auth_error(), fake_fetch(), test_download_does_not_retry_without_a_refresh_token() (+13 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.24
Nodes (10): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError (+2 more)

### Community 28 - "state_backup.py"
Cohesion: 0.19
Nodes (21): decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+13 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.15
Nodes (21): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+13 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.06
Nodes (44): PathLike, Market Data & Authentication, FakeResponse, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent… (+36 more)

### Community 31 - "TournamentDataset"
Cohesion: 0.11
Nodes (15): setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition(), Path (+7 more)

### Community 32 - "test_search_space.py"
Cohesion: 0.25
Nodes (14): E. Current 50,000-scenario architecture and benchmark, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix(), from_strategy() (+6 more)

### Community 33 - "test_lab.py"
Cohesion: 0.12
Nodes (37): test_account_only_reset_preserves_research_and_stop(), test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), parametrize, qualified_candidate(), quote(), setup(), bars() (+29 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.18
Nodes (11): Step 0 - GitHub repos and multi-path merge (only if a URL or several paths), Step 1 - Ensure graphify is installed, Step 2.5 - Video and audio (only if video files detected), Step 2 - Detect files, Step 4.5 - Graph health check (read-only integrity gate), Step 4 - Build graph, cluster, analyze, generate outputs, Step 5 - Label communities, Step 6 - Generate Obsidian vault (opt-in) + HTML (+3 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.12
Nodes (15): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+7 more)

### Community 37 - "synthetic_bars"
Cohesion: 0.08
Nodes (37): test_backtest(), dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version…, A freeze killed mid-write must not hang the next one, nor quietly pass., A backtester or cost change must invalidate stored results. Both were hardcoded… (+29 more)

### Community 38 - "ShadowTradingReadiness"
Cohesion: 0.16
Nodes (11): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), Path (+3 more)

### Community 39 - "build_features"
Cohesion: 0.10
Nodes (27): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error(), test_novel_formulas_generate_valid_signals() (+19 more)

### Community 40 - "InMemoryAgentTranscriptStore"
Cohesion: 0.09
Nodes (10): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), `limit` alone does not bound a response. A shell-job step carries a captured…, test_steps_response_is_bounded_by_a_byte_budget(), test_base_runner_records_codes_for_planner_and_tick_errors(), boom(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store. (+2 more)

### Community 41 - "engine_loop.py"
Cohesion: 0.15
Nodes (6): EngineStore, MarketSource, Protocol, Deterministic paper-trading engine: the trade decision path, with no LLM on it.…, The narrow slice of the durable store the engine needs., TranscriptSink

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.19
Nodes (14): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+6 more)

### Community 49 - "test_retention.py"
Cohesion: 0.12
Nodes (39): archive(), _local_backups(), test_compaction_preserves_rebuild_revision_winner(), test_compaction_reads_compressed_raw_pages(), test_completed_logs_only_and_pins(), test_completed_workspace_reclaims_training_and_scripts_but_keeps_memory(), test_completed_workspace_with_nested_symlink_retained(), test_compress_existing_exact_target_and_deterministic_bytes() (+31 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.13
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 51 - "test_ctrader_lifecycle.py"
Cohesion: 0.22
Nodes (10): Client, event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending() (+2 more)

### Community 52 - "test_automation.py"
Cohesion: 0.08
Nodes (32): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+24 more)

### Community 53 - "CTraderDemoSafetyError"
Cohesion: 0.10
Nodes (22): copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+14 more)

### Community 54 - "PaperDecision"
Cohesion: 0.14
Nodes (9): test_paper_endpoint_reflects_accepted_fill(), CockroachPaperTradingStore, _now(), PaperDecision, transition(), transition(), Any, CockroachDB is the authoritative state and idempotency store in production. (+1 more)

### Community 55 - "CTraderVolumeConversion"
Cohesion: 0.12
Nodes (11): test_demo_factory_binds_authoritative_paper_exposure(), test_volume_policy_from_metadata(), _ctrader_demo_adapter(), expected_volume(), CTraderVolumeConversion, CTraderVolumePolicy, DemoExecutor, Protocol (+3 more)

### Community 56 - "restart_policy"
Cohesion: 0.14
Nodes (14): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+6 more)

### Community 57 - "create_app"
Cohesion: 0.08
Nodes (38): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), read(), agent_status_path() (+30 more)

### Community 58 - "DemoLifecycle"
Cohesion: 0.15
Nodes (6): DecisionSource, DemoLifecycle, MarketDataSource, Protocol, Read-only source for the latest executable market observation., Read-only strategy proposal source; ``None`` means no proposed action.

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.10
Nodes (15): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, BaseException, Protocol (+7 more)

### Community 60 - "SQLiteAgentTranscriptStore"
Cohesion: 0.15
Nodes (9): Row, The deterministic engine writes to the same `agent_runs` table. Taking the…, test_status_and_health_select_the_agent_run_not_a_newer_engine_run(), _now(), Local SQLite replacement for the CockroachDB agent transcript store., Bound transcript growth. Nothing else ever deleted from this table. The…, Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row, and only that row. A run's owner is the… (+1 more)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "EngineConfig"
Cohesion: 0.20
Nodes (9): test_engine_config_rejects_unbounded_values(), test_engine_status_reports_the_running_process_not_a_phantom(), _build_engine(), engine_controller(), Construct the deterministic engine from the same stores the agent uses., Operator and supervisor control for the deterministic trade engine., EngineConfig, _float_env() (+1 more)

### Community 63 - "_registry_schema_valid"
Cohesion: 0.21
Nodes (12): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_registry_validation_streams_rows_and_rejects_non_array_tables(), Validate logical snapshot JSON in bounded memory (8 MiB per row). Snapshots…, _registry_schema_valid() (+4 more)

### Community 64 - "CTraderOpenApiConfig"
Cohesion: 0.14
Nodes (11): test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag(), test_trendbar_delta_decoding(), CTraderOpenApiConfig, Any, Every archived raw page as ``(first_minute, last_minute, path)``, sorted. The…, Which archived pages a minimal cover makes redundant. Deletes nothing. The… (+3 more)

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
Nodes (13): error_details(), message_fingerprint(), BaseException, Payload-free classification of an exception for events and heartbeats.…, Stable digest of a message stream, used to persist each turn exactly once., BitsAgentRunner, Any, Retrieval-loop evidence for the heartbeat, which this file writes every tick. A… (+5 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.27
Nodes (12): at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from…, Synthetic M1 bars stamped at bar open, only while the session gate is open., session_bars(), test_a_week_whose_data_stops_early_is_not_complete(), test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected(), test_pandas_weekly_labels_disagree_with_session_weeks() (+4 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.12
Nodes (30): errno, minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.…, `data update` starts from the newest bar, so a hole in the middle is permanent.…, A weekend is not data loss; counting it as such hides the gaps that matter., The path the CLI takes: no frame passed in. (+22 more)

### Community 77 - "agent_controller"
Cohesion: 0.12
Nodes (18): parametrize, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An…, test_agent_config_rejects_non_finite_limits(), _positive_float(), agent_controller(), _agent_data_refresh_source(), _agent_status_path(), _agent_status_view() (+10 more)

### Community 78 - "cli.py"
Cohesion: 0.06
Nodes (75): ast, base64, collections, concurrent_futures, contextlib, csv, dataclasses, datetime (+67 more)

### Community 79 - "test_bits_memory.py"
Cohesion: 0.16
Nodes (24): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection(), reply(), sample_notes() (+16 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.08
Nodes (40): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., An oversized proposal must be visibly refused, not silently trimmed. Clamping…, The halt was the only thing between the engine and an unvalidated strategy. A…, Re-read every tick, like the halt: a cached answer fails silently until restart. (+32 more)

### Community 82 - "bits_capabilities.py"
Cohesion: 0.07
Nodes (40): Datadog Bits operations, ArgumentParser, platform, shlex, test_shell_environment_keeps_the_latest_refreshed_tokens(), test_shell_path_prepends_service_interpreter_and_declared_directories(), test_the_heal_command_is_in_the_cli_grammar(), test_the_raw_retention_command_is_in_the_cli_grammar() (+32 more)

### Community 83 - "AgentTools"
Cohesion: 0.05
Nodes (46): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000) (+38 more)

### Community 84 - "lab_api.py"
Cohesion: 0.20
Nodes (9): test_read_only_lab_api_reports_actual_data_and_events(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal(), utc_day(), chart(), _data(), events(), Read-only dashboard projections, bounded by rows and bytes. (+1 more)

### Community 86 - "agent_experiments.py"
Cohesion: 0.13
Nodes (25): functools, test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), test_improvement_cannot_claim_old_release_as_new_work() (+17 more)

### Community 87 - "test_cli.py"
Cohesion: 0.14
Nodes (24): DemoTransport, _isolated_bits_state(), Without this the command exists but nothing runs it, so a hole still sits for…, An interior hole is a smaller problem than a refresh reported as failed. The…, _run_cli(), stopped_demo_adapter(), test_bits_capabilities_check_and_stored_manifest(), test_bits_capabilities_direct_discovery_exception_still_exits_nonzero() (+16 more)

### Community 88 - "BitsMemory"
Cohesion: 0.24
Nodes (6): BitsMemory, apply(), _note_sources(), _notes_base(), Deliberately close one draft without saving it; the notes are not touched., A specific next task for unresolved drafts; not a new research cycle.

### Community 89 - "test_agent_advisor.py"
Cohesion: 0.12
Nodes (17): test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory(), run_turn(), test_pre_job_research_failure_is_loud_and_preserves_trading_state() (+9 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.16
Nodes (12): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+4 more)

### Community 91 - "test_bits_capabilities.py"
Cohesion: 0.11
Nodes (38): R2 — P1: capability discovery failure must remain visible, fake_tool(), parametrize, The shell-job environment is discoverable from the environment jobs really get., Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_every_published_operation_is_a_real_cli_command() (+30 more)

### Community 92 - "HistoricalDataStore"
Cohesion: 0.13
Nodes (13): Historical deployment state — verified 2026-10-05, frame(), test_positions_matches_get_indexer(), test_positions_requires_a_sorted_unique_index(), test_positions_resolves_an_anchor_sweep_in_one_pass(), test_store_rejects_invalid_ohlc(), test_store_roundtrip(), HistoricalDataStore (+5 more)

### Community 93 - "test_live_feed.py"
Cohesion: 0.13
Nodes (35): config(), credentials(), FakeClient, FakeStore, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test…, The status file holds only the latest state, and these services write no… (+27 more)

### Community 94 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 95 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 96 - "Signals"
Cohesion: 0.19
Nodes (7): Deterministic signal double: returns the same proposal until told otherwise., Signals, Source, Store, test_a_halt_from_another_process_still_stops_a_running_engine(), test_halt_stops_proposals_and_persists_the_reason(), test_resume_takes_effect_on_a_running_engine_without_a_restart()

### Community 97 - "bits_runner.py"
Cohesion: 0.10
Nodes (28): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction(), test_market_windows_use_observed_data_and_handle_missing_source() (+20 more)

### Community 98 - "._note"
Cohesion: 0.10
Nodes (21): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), on_connected(), on_disconnected(), on_message(), tick(), confirmed(), guard() (+13 more)

### Community 99 - "test_local_state.py"
Cohesion: 0.07
Nodes (34): decision(), parametrize, Validation must not reject a real account, including a running one., The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is., The owner of a run is the only authority on whether it is live., The transcript had no DELETE anywhere and gained a row per heartbeat. 14,350…, Pruning must not delete content a connected reader has not displayed yet. The… (+26 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.11
Nodes (18): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+10 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.18
Nodes (24): skipif, notes(), open_drafts(), R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject(), test_concurrent_writers_with_the_same_base_cannot_both_win(), writer() (+16 more)

### Community 102 - "BitsStore"
Cohesion: 0.17
Nodes (8): Operations, 5. Restart the live view so the new observability is visible, test_bits_notes_only_does_not_repeat_history(), BitsStore, Uses the same connection selected for the application's transcript store., Read-modify-write several state keys atomically. SQLite connections run in…, Drop the oldest terminal job records. Nothing else ever deleted from this…, Row counts and stored bytes, so unbounded growth is visible.

### Community 103 - "_datetime"
Cohesion: 0.11
Nodes (39): Engineering, operator, parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate() (+31 more)

### Community 104 - "CTraderDemoStore"
Cohesion: 0.14
Nodes (3): CTraderDemoStore, CTraderTransport, Protocol

### Community 105 - "test_weekly_report.py"
Cohesion: 0.19
Nodes (16): row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors(), test_selection_bias_computes_bh_and_aligned_fold_pbo(), test_selection_bias_reports_score_distribution_and_missing_controls(), update() (+8 more)

### Community 106 - "Any"
Cohesion: 0.15
Nodes (5): HarnessStore, Any, Protocol, RuntimeError, ToolExecutionError

### Community 107 - "canonical_json"
Cohesion: 0.21
Nodes (13): Connection, Explicit operator-only, flat paper account rebase; no research reset., rebase(), canonical_json(), _connect(), Any, Minimal local SQLite state stores for paper trading and the agent transcript.…, Local SQLite replacement for the CockroachDB paper trading store. (+5 more)

### Community 108 - "file_lock"
Cohesion: 0.15
Nodes (17): The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker(), test_file_lock_times_out_instead_of_waiting_forever() (+9 more)

### Community 109 - "bits_memory.py"
Cohesion: 0.14
Nodes (24): _age_seconds(), _check_categories(), _check_draft_ids(), _check_entry(), check_notes(), _is_current_notes(), issue(), _key_path() (+16 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.11
Nodes (23): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+15 more)

### Community 111 - "BitsError"
Cohesion: 0.05
Nodes (59): 10. Related documents, 1. What was built and why, 2. Publish the Datadog workflow message stream (required for the thinking panel), 4. Enable the deterministic engine, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback, Engine control (+51 more)

### Community 112 - "LabStore"
Cohesion: 0.19
Nodes (5): test_snapshot_expiry_deletes_backend_rows(), LabStore, add(), save(), Expire old price-mark results, never actual trade idempotency keys. Monitor…

### Community 113 - "._discover_account"
Cohesion: 0.57
Nodes (7): account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), Resolve the demo account and XAUUSD symbol id, then ``done``. Asynchronous,…

### Community 114 - "promote_tools"
Cohesion: 0.19
Nodes (21): generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused(), test_symlinks_and_size_limit_refuse_execution() (+13 more)

### Community 115 - "fetch_source"
Cohesion: 0.10
Nodes (10): HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), xauusd, NoRedirect, _excerpt_text(), fetch_source() (+2 more)

### Community 116 - "closed_bar"
Cohesion: 0.18
Nodes (7): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 117 - ".write_notes"
Cohesion: 0.18
Nodes (15): Implemented baseline — memory writes and actionable errors (R1 remains), apply(), apply(), _brief(), _close(), _empty_drafts(), load_drafts(), _merge_refs() (+7 more)

### Community 118 - "DemoAutomationRunner"
Cohesion: 0.26
Nodes (5): DemoAutomationRunner, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 119 - "read_quote"
Cohesion: 0.18
Nodes (17): ctrader_open_api_messages_openapimessages_pb2, sqlite3, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_feed_matches_account_and_symbol_before_recording(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time() (+9 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.19
Nodes (19): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal(), aligned_returns() (+11 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "EngineeringManager"
Cohesion: 0.25
Nodes (8): _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker., _safe()

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.14
Nodes (10): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), test_snapshot_projects_current_agent_and_archived_jobs(), attach_routes(), lab_chart(), lab_events() (+2 more)

### Community 124 - "data_heal"
Cohesion: 0.20
Nodes (14): _heal_args(), no_broker(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _store_with_windows(), test_data_heal_defers_a_window_that_does_not_fit_the_budget(), test_data_heal_downloads_an_interior_window() (+6 more)

### Community 125 - "evidence_refs"
Cohesion: 0.38
Nodes (7): evidence_refs(), add(), ordered(), walk(), _legacy_draft(), Evidence references named by a (possibly malformed) payload: bounded, safe,…, The single pending record written by the previous release, as one open draft.

### Community 126 - "Local audit — 2026-09-24"
Cohesion: 0.22
Nodes (7): Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC, Planner latency (read-only), Recommended next work

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.13
Nodes (15): Architecture, Aurum — Codex Autonomous Trading Lab, Autonomous Agent, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Demo Automation (+7 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.20
Nodes (10): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, graphify, Local agent handoff — completed 2026-09-24, Open-agent extension — 2026-10-21, Purpose (+2 more)

### Community 132 - "test_dashboard.py"
Cohesion: 0.23
Nodes (8): setup_files(), test_dashboard_reads_latest_run_and_equity(), test_dashboard_registry_requires_database_url_and_never_passes_a_path(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature(), test_status_remains_readable_without_generated_tournament_dataset(), test_tournament_equity_and_leaderboard()

### Community 133 - "test_agent_release_worker.py"
Cohesion: 0.38
Nodes (4): test_failed_worker_schedule_rolls_back_without_retry(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), release_healthy(), schedule_verification()

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.22
Nodes (9): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Tools and compute (+1 more)

### Community 135 - "/graphify"
Cohesion: 0.22
Nodes (8): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Usage, What graphify is for

### Community 136 - "_bars"
Cohesion: 0.18
Nodes (12): _bars(), Three valid, non-overlapping minutes, shifted so writers never collide., A shared temporary name lets two writers interleave into one inode. That is how…, Read-merge-swap has to be exclusive, and a wedged writer must not be skipped.…, The invariant the corruption broke: every writer's bars survive, and it reads., One value must not cost the whole frame. `data update` runs four times a day on…, test_concurrent_writers_leave_a_readable_complete_store(), append() (+4 more)

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.14
Nodes (10): Bits agent instructions, Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Operating model, Research and automatic deployment (+2 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "weekly_bars"
Cohesion: 0.25
Nodes (8): timedelta, DataFrame, DatetimeIndex, New York trading-week boundaries for research aggregation (never a trading…, Naive New York wall time of each timestamp's session-week open (vectorized…, Aggregate UTC bar-open-stamped M1 OHLCV bars into New York session weeks.…, _week_open_wall(), weekly_bars()

### Community 140 - "StoreCorruptError"
Cohesion: 0.17
Nodes (11): 9. Recovering the market-data store, OSError, `error_type: OSError` with `error_code: null` was undiagnosable. That is all…, test_a_corrupt_store_is_reported_as_corrupt_not_as_a_bare_oserror(), test_classify_store_error_names_a_full_disk_and_refuses_to_guess(), classify_store_error(), BaseException, The newest bar in the store, reading the index column only. `data update` needs… (+3 more)

### Community 141 - ".path"
Cohesion: 0.29
Nodes (6): Interpreter guard for subcommands, Bits shell environment (`bits-capabilities`), Delivery Stages, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval, Research notes (`bits-memory`, schema `xauusd.notes/1`)

### Community 142 - "ResearchHarness"
Cohesion: 0.16
Nodes (6): A prospective simulation account; never selects or replaces real state., ShadowStore, _open_minutes(), Observation opportunities under the shared New York market session., Observe prospective fills at actual fresh quotes through the same gates., ResearchHarness

### Community 143 - "Merge review — 2026-09-25, baseline `cba22b2`"
Cohesion: 0.40
Nodes (5): Delivery order after this merge, Merge review — 2026-09-25, baseline `cba22b2`, R1 — P0: do not lose pending findings when memory is rewritten, R3 — P1: make experiment continuity work with the deployed backend, Runtime adoption is still pending

### Community 144 - "atomic_write_json"
Cohesion: 0.40
Nodes (4): atomic_write_json(), Any, Serialise ``payload`` as JSON and replace ``target`` atomically. ``allow_nan``…, Append a state transition to a bounded event log. The status file holds only…

### Community 145 - "Step 3 - Extract entities and relationships"
Cohesion: 0.50
Nodes (4): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 3 - Extract entities and relationships

### Community 146 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.26
Nodes (8): NormalizedDecision, PaperToCTraderDemoCoordinator, Any, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it., Strategy proposal expressed in configured paper-trading quantity units., Runs paper risk first; execution lifecycle remains explicitly operator…

### Community 147 - "SecretFilter"
Cohesion: 0.20
Nodes (6): memory(), fixture, memory(), fixture, Suppress whole values, not partial/redacted credentials. Not a shell sandbox., SecretFilter

### Community 150 - "_download_with_retry"
Cohesion: 0.18
Nodes (9): Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., test_data_update_reraises_the_first_transient_failure(), test_data_update_retries_transient_failures(), _download_attempt_subprocess(), _download_with_retry(), Any, One single-shot ``data download`` in a fresh interpreter; returns its result. A… (+1 more)

### Community 151 - "DemoRunnerConfig"
Cohesion: 0.25
Nodes (8): test_demo_automation_start_in_paper_only_mode_contacts_no_broker(), test_environment_config_is_disabled_unless_explicitly_true(), demo_automation(), _demo_automation_start(), _demo_automation_status(), Explicit operator override for the demo execution kill switch; paper and the…, Run the explicitly enabled local-data paper-to-demo canary., DemoRunnerConfig

### Community 153 - "RecordingPostgres"
Cohesion: 0.20
Nodes (3): PostgresLikeTranscript, psycopg-like connection: one implicit transaction per block, committed or…, RecordingPostgres

### Community 155 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 156 - "CTraderHistoricalAdapter"
Cohesion: 0.25
Nodes (5): CTraderHistoricalAdapter, Path, The same wire page, whether plain or losslessly gzip-compressed., Import cTrader CSV exports into the normalized historical store., read_raw_page()

### Community 157 - "cTrader SDK and protocol review (no broker connection)"
Cohesion: 0.29
Nodes (5): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Order lifecycle and errors — follow-up #15, Position reconciliation — follow-up #16

### Community 159 - "test_lab_retention.py"
Cohesion: 0.60
Nodes (5): store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics()

### Community 160 - "._authenticate"
Cohesion: 0.33
Nodes (3): app_failed(), Authenticate the application, then resolve the demo account and symbol.…, Application auth, which the broker requires before any token request. Sending…

### Community 162 - "WeeklyTournamentReport"
Cohesion: 0.50
Nodes (3): Gate-failure and near-pass analytics — 2026-08-21, test_weekly_report_tracks_throughput_families_and_multiple_testing(), WeeklyTournamentReport

### Community 163 - "_command_failure"
Cohesion: 0.50
Nodes (4): bits_job_page(), _command_failure(), Exception, Classified, payload-free failure: exception text and arguments are never echoed.

## Knowledge Gaps
- **164 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+159 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1116 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `main`, `agent_loop.py`, `ExecutionConfig`, `StoreCorruptError`, `.path`, `test_agent_loop.py`, `test_validation.py`, `DataConfig`, `CTraderHistoricalAdapter`, `TournamentDataset`, `test_retention.py`, `test_automation.py`, `EngineConfig`, `CTraderOpenApiConfig`, `test_data.py`, `agent_controller`, `cli.py`, `bits_capabilities.py`, `AgentTools`, `lab_api.py`, `test_cli.py`, `test_live_feed.py`, `LiveFeedConfig`, `read_quote`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `main`, `test_bits_runner.py`, `agent_loop.py`, `ResearchHarness`, `test_session_reset.py`, `test_agent_loop.py`, `PaperToCTraderDemoCoordinator`, `test_agent_view.py`, `state_backup.py`, `test_demo_execution.py`, `PaperTradingStore`, `test_lab.py`, `InMemoryAgentTranscriptStore`, `engine_loop.py`, `test_demo_runner.py`, `PaperDecision`, `CTraderVolumeConversion`, `restart_policy`, `create_app`, `ContinuousAgentRunner`, `agent_controller`, `cli.py`, `test_engine_loop.py`, `agent_experiments.py`, `test_cli.py`, `PaperTradingEngine`, `test_local_state.py`, `_datetime`, `test_lab_dashboard.py`, `data_heal`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `LiveBarFeed` connect `test_live_feed.py` to `CTraderOpenApiConfig`, `._authenticate`, `._note`, `LiveFeedConfig`, `cli.py`, `atomic_write_json`, `._discover_account`, `closed_bar`, `read_quote`, `DataConfig`, `HistoricalDataStore`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ExperimentRegistry` (e.g. with `R3 — P1: make experiment continuity work with the deployed backend` and `AdaptiveSearch`) actually correct?**
  _`ExperimentRegistry` has 12 INFERRED edges - model-reasoned connections that need verification._