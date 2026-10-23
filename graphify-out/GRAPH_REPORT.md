# Graph Report - xauusd-luna-release  (2026-10-23)

## Corpus Check
- 181 files · ~188,947 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .service 8, (none) 7, .timer 2)

## Summary
- 3626 nodes · 10141 edges · 150 communities (130 shown, 20 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 536 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `113abb6d`
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
- ml_models.py
- test_ctrader_demo.py
- pandas
- engine_decision_id
- PaperTrading
- self_improve.py
- CockroachAgentTranscriptStore
- PaperDecision
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- test_validation.py
- SQLiteAgentTranscriptStore
- XAUUSD discovery, incident, quantitative, and scaling audit
- cli.py
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
- test_ctrader_reconciliation.py
- Any
- PaperToCTraderDemoCoordinator
- restart_policy
- create_app
- NormalizedDecision
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- verify_result_parity.py
- EngineConfig
- _registry_schema_valid
- ExecutionConfig
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
- data.py
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- bits_capabilities.py
- AgentTools
- _datetime
- agent_experiments.py
- main
- read_status
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
- pytest
- LiveFeedConfig
- test_bits_memory_drafts.py
- BitsStore
- lab.py
- ctrader_demo.py
- test_weekly_report.py
- lab_codex.py
- canonical_json
- file_lock
- bits_memory.py
- atomic_write_text
- BitsError
- LabStore
- _error_code
- lab_tools.py
- fetch_source
- Operator runbook: engine, live feed, and the visible harness
- Requirements: reliable research-to-paper-trade workflow
- DemoAutomationRunner
- read_quote
- portfolio_research.py
- .send
- EngineeringManager
- test_lab_dashboard.py
- test_offline.py
- evidence_refs
- Local audit — 2026-09-24
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- AgentTranscriptStore
- types
- Persistent open-ended Codex agent
- /graphify
- build_parser
- Codex autonomous trading lab
- Datadog Bits connection
- session_calendar.py
- README.md
- .path
- ShadowStore
- Merge review — 2026-09-25, baseline `cba22b2`
- atomic_write_json
- Step 3 - Extract entities and relationships
- test_sandbox_tests_return_bounded_feedback_and_clean_environment
- SequencedTransport
- harness-outcomes-plan-2026-10-23.md
- demo_feed_environment

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
- `Original incident evidence (pre-merge snapshot)` --references--> `BitsError`  [INFERRED]
  requirements.md → xauusd/bits.py
- `Order lifecycle and errors — follow-up #15` --references--> `is_error()`  [INFERRED]
  docs/local-handoff-audit-2026-09-24.md → xauusd/ctrader_auth.py
- `R3 — P1: make experiment continuity work with the deployed backend` --references--> `ExperimentRegistry`  [INFERRED]
  requirements.md → xauusd/experiment_registry.py

## Import Cycles
- None detected.

## Communities (150 total, 20 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.12
Nodes (25): account(), An unclassified account is not a demo account. ``isLive`` is a proto3 optional…, The discriminator has to work on the actual SDK message, not just dicts., test_demo_accounts_empty_when_all_live(), test_demo_accounts_excludes_a_dict_without_the_flag(), test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo(), test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account(), test_is_error_extracts_code_and_description() (+17 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.13
Nodes (21): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_planner_from_env_configures_model_and_timeout() (+13 more)

### Community 2 - "OperationsManager"
Cohesion: 0.09
Nodes (20): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+12 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (67): asyncio, FastAPI, fastapi_responses, fastapi_security, get, HTTPBasicCredentials, inspect, middleware (+59 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.08
Nodes (34): _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted., `monitor_error` used to be assigned and then read by nothing at all. (+26 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.16
Nodes (6): ExperimentStatus, ExperimentRegistry, Any, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool., Path

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (6): _canonical_json(), CockroachCTraderDemoStore, InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.16
Nodes (20): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+12 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "ml_models.py"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.08
Nodes (35): test_demo_factory_binds_authoritative_paper_exposure(), adapter(), FakeClient, ImmediateDeferred, Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_configured_account_id_bypasses_account_list_scope() (+27 more)

### Community 11 - "pandas"
Cohesion: 0.10
Nodes (34): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, numpy, pandas, sklearn_metrics, Secret-free deterministic parity fixture for the runtime container., test_appending_future_does_not_change_existing_ml_features() (+26 more)

### Community 12 - "engine_decision_id"
Cohesion: 0.50
Nodes (4): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), Durable identity for one engine decision. Derived from the bar, not from a…

### Community 13 - "PaperTrading"
Cohesion: 0.08
Nodes (55): paper_trading(), test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_surfaces_a_monitor_error(), test_job_endpoint_pages_a_shell_capture(), test_base_runner_records_codes_for_planner_and_tick_errors(), boom(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status() (+47 more)

### Community 14 - "self_improve.py"
Cohesion: 0.13
Nodes (20): base64, CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal() (+12 more)

### Community 15 - "CockroachAgentTranscriptStore"
Cohesion: 0.14
Nodes (7): CockroachAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row; see the SQLite store., Family-scoped mirror of the SQL stores: never close another family's run., The run family a run_id belongs to: ``agent_`` or ``engine_``. The agent and…, _run_family()

### Community 16 - "PaperDecision"
Cohesion: 0.30
Nodes (9): test_paper_endpoint_reflects_accepted_fill(), seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), AgentAlreadyRunning, AgentLock, Single process per container; the lock is runtime coordination, not state., PaperDecision (+1 more)

### Community 17 - "Any"
Cohesion: 0.15
Nodes (17): request(), CTraderDemoOpenApiTransport, failed(), issue(), failed(), issue(), observe(), succeeded() (+9 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.09
Nodes (48): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), parametrize, A ticking agent must not be served as stopped. The engine's startup reconcile…, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An… (+40 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.15
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (23): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+15 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.05
Nodes (42): _feed(), _harness_client(), fixture, parametrize, The deterministic engine writes to the same `agent_runs` table. Taking the…, The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., The health endpoint is the observability surface; it must not raise. An… (+34 more)

### Community 22 - "test_validation.py"
Cohesion: 0.09
Nodes (32): Dependence-aware bootstrap validation — 2026-08-21, An empty training window must fail loudly, not look like a negative result., The embargo must reach the report, not just the helper. `walk_forward_splits`…, The negative path was never asserted, which is why several real defects…, A 30-bar rolling feature reaches across the split boundary. The last…, test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration() (+24 more)

### Community 23 - "SQLiteAgentTranscriptStore"
Cohesion: 0.07
Nodes (38): Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, test_service_like_shell_runs_documented_examples_without_profile(), action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes… (+30 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (47): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+39 more)

### Community 25 - "cli.py"
Cohesion: 0.14
Nodes (26): collections, concurrent_futures, csv, dataclasses, datetime, hashlib, json, math (+18 more)

### Community 26 - "DataConfig"
Cohesion: 0.07
Nodes (36): Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., An interior hole is a smaller problem than a refresh reported as failed. The…, test_data_update_does_not_retry_auth_errors(), unauthorized(), test_data_update_reraises_the_first_transient_failure(), test_data_update_retries_transient_failures(), test_update_reports_a_failed_heal_without_failing_the_update() (+28 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.15
Nodes (11): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), _check_reason(), HarnessStore, OpenAICompatiblePlanner, parse_action(), PlannerResponseError, Any (+3 more)

### Community 28 - "state_backup.py"
Cohesion: 0.15
Nodes (23): gzip, sqlite3, decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account() (+15 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.19
Nodes (19): coordinator(), decision(), DemoAdapterDouble, policy(), test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped(), test_broker_error_stops_paper_and_demo_kill_switches(), test_broker_rejection_stops_paper_and_demo_kill_switches() (+11 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.06
Nodes (47): PathLike, Market Data & Authentication, FakeResponse, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent… (+39 more)

### Community 31 - "TournamentDataset"
Cohesion: 0.09
Nodes (18): test_portfolio_run_reads_validation_only(), setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition() (+10 more)

### Community 32 - "test_search_space.py"
Cohesion: 0.23
Nodes (15): E. Current 50,000-scenario architecture and benchmark, dotenv, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix() (+7 more)

### Community 33 - "test_lab.py"
Cohesion: 0.10
Nodes (42): test_account_only_reset_preserves_research_and_stop(), test_pre_job_research_failure_is_loud_and_preserves_trading_state(), test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), parametrize, qualified_candidate(), quote(), setup() (+34 more)

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
Nodes (12): ChampionRegistry, Dataset, test_emergency_stop_forces_flat_signal(), test_empty_data_is_recorded_as_flat(), test_invalid_risk_limits_are_rejected(), test_readiness_never_enables_execution(), test_shadow_is_hard_blocked_without_champion(), DataFrame (+4 more)

### Community 39 - "build_features"
Cohesion: 0.09
Nodes (27): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error(), test_novel_formulas_generate_valid_signals() (+19 more)

### Community 40 - "InMemoryAgentTranscriptStore"
Cohesion: 0.13
Nodes (7): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), `limit` alone does not bound a response. A shell-job step carries a captured…, test_steps_response_is_bounded_by_a_byte_budget(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store., Mirror of the SQLite retention so both backends behave the same.

### Community 41 - ".__init__"
Cohesion: 0.15
Nodes (5): EngineStore, MarketSource, Protocol, The narrow slice of the durable store the engine needs., TranscriptSink

### Community 42 - "._fetch"
Cohesion: 0.41
Nodes (13): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+5 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 49 - "test_retention.py"
Cohesion: 0.12
Nodes (39): archive(), _local_backups(), test_compaction_preserves_rebuild_revision_winner(), test_compaction_reads_compressed_raw_pages(), test_completed_logs_only_and_pins(), test_completed_workspace_reclaims_training_and_scripts_but_keeps_memory(), test_completed_workspace_with_nested_symlink_retained(), test_compress_existing_exact_target_and_deterministic_bytes() (+31 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.14
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 51 - "test_ctrader_lifecycle.py"
Cohesion: 0.22
Nodes (10): Client, event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending() (+2 more)

### Community 52 - "test_automation.py"
Cohesion: 0.09
Nodes (30): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+22 more)

### Community 53 - "test_ctrader_reconciliation.py"
Cohesion: 0.21
Nodes (13): copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+5 more)

### Community 54 - "Any"
Cohesion: 0.12
Nodes (9): CockroachPaperTradingStore, _now(), transition(), transition(), PaperTradingStore, Any, Protocol, CockroachDB is the authoritative state and idempotency store in production. (+1 more)

### Community 55 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.11
Nodes (15): test_volume_policy_from_metadata(), _paper_to_demo_coordinator(), CTraderVolumeConversion, CTraderVolumePolicy, DemoExecutor, PaperToCTraderDemoCoordinator, Any, Protocol (+7 more)

### Community 56 - "restart_policy"
Cohesion: 0.14
Nodes (14): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+6 more)

### Community 57 - "create_app"
Cohesion: 0.11
Nodes (21): frame(), read(), create_app(), data_update_status(), harness(), health(), index(), job_output() (+13 more)

### Community 58 - "NormalizedDecision"
Cohesion: 0.15
Nodes (11): test_environment_config_is_disabled_unless_explicitly_true(), _decision_id(), handler(), NormalizedDecision, Strategy proposal expressed in configured paper-trading quantity units., DecisionSource, DemoRunnerConfig, MarketDataSource (+3 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.16
Nodes (13): Event, test_redact_bounds_untrusted_content(), _assistant_step(), ContinuousAgentRunner, Any, BaseException, Display-friendly assistant step: parsed action plus the model's plain-English…, Transcript-friendly view: keep structures, bound untrusted string lengths. (+5 more)

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.25
Nodes (7): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "EngineConfig"
Cohesion: 0.18
Nodes (10): test_engine_config_rejects_unbounded_values(), test_engine_status_reports_the_running_process_not_a_phantom(), test_halt_stops_proposals_and_persists_the_reason(), _build_engine(), engine_controller(), Construct the deterministic engine from the same stores the agent uses., Operator and supervisor control for the deterministic trade engine., EngineConfig (+2 more)

### Community 63 - "_registry_schema_valid"
Cohesion: 0.21
Nodes (12): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_registry_validation_streams_rows_and_rejects_non_array_tables(), Validate logical snapshot JSON in bounded memory (8 MiB per row). Snapshots…, _registry_schema_valid() (+4 more)

### Community 64 - "ExecutionConfig"
Cohesion: 0.14
Nodes (28): main(), bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,…, Zero is a real value; a metric that cannot be computed must say so. Reporting… (+20 more)

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
Nodes (64): date, pandas_tseries_holiday, _cot_csv(), _prereg(), The preregistered CFTC study: point-in-time discipline, session weeks, fail-…, 15:30 New York is 20:30 UTC in winter and 19:30 UTC under daylight time. The…, The fail-closed check the artifact claims, verified instead of asserted. Taking…, Excluding 2023 and 2025 wholesale means some flows span a gap; report how many.… (+56 more)

### Community 72 - "BitsAgentRunner"
Cohesion: 0.10
Nodes (15): missing_executables(), Names bash (or /usr/bin/env) reported as not found in a completed job's stderr., error_details(), message_fingerprint(), BaseException, Payload-free classification of an exception for events and heartbeats.…, Stable digest of a message stream, used to persist each turn exactly once., BitsAgentRunner (+7 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.25
Nodes (14): at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from…, Synthetic M1 bars stamped at bar open, only while the session gate is open., session_bars(), test_a_week_whose_data_stops_early_is_not_complete(), test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected(), test_pandas_weekly_labels_disagree_with_session_weeks() (+6 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.07
Nodes (51): errno, _bars(), frame(), minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.…, Three valid, non-overlapping minutes, shifted so writers never collide. (+43 more)

### Community 77 - "agent_controller"
Cohesion: 0.12
Nodes (14): test_demo_automation_requires_explicit_positive_volume(), agent_controller(), _agent_data_refresh_source(), _agent_status_path(), _agent_status_view(), _canary_source(), expected_volume(), _demo_automation_runner() (+6 more)

### Community 78 - "data.py"
Cohesion: 0.11
Nodes (29): ast, contextlib, fcntl, html, html_parser, ipaddress, logging, os (+21 more)

### Community 79 - "test_bits_memory.py"
Cohesion: 0.16
Nodes (23): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection(), reply(), sample_notes() (+15 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.10
Nodes (35): build(), Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., An oversized proposal must be visibly refused, not silently trimmed. Clamping…, The halt was the only thing between the engine and an unvalidated strategy. A…, Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case., The hash stops a later edit to the artifact redefining what was granted. (+27 more)

### Community 82 - "bits_capabilities.py"
Cohesion: 0.08
Nodes (36): Datadog Bits operations, platform, Bits shell environment (`bits-capabilities`), shlex, test_shell_environment_keeps_the_latest_refreshed_tokens(), test_shell_path_prepends_service_interpreter_and_declared_directories(), cli_commands(), cli_prefix() (+28 more)

### Community 83 - "AgentTools"
Cohesion: 0.11
Nodes (25): Store, test_dependency_install_requires_pins(), test_dependency_install_targets_scratch_only(), test_domain_configuration(), test_fetch_rejects_private_dns(), test_market_observe_excludes_frozen_and_forming_bars(), test_market_observe_without_frozen_boundary_reveals_no_history(), test_process_timeout_and_output_bound() (+17 more)

### Community 84 - "_datetime"
Cohesion: 0.14
Nodes (25): Engineering, threading, canary_signal_tool(), handler(), read_market_tool(), handler(), chart(), _data() (+17 more)

### Community 86 - "agent_experiments.py"
Cohesion: 0.14
Nodes (25): functools, test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), test_improvement_cannot_claim_old_release_as_new_work() (+17 more)

### Community 87 - "main"
Cohesion: 0.08
Nodes (44): DemoTransport, _heal_args(), _isolated_bits_state(), no_broker(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _run_cli() (+36 more)

### Community 88 - "read_status"
Cohesion: 0.26
Nodes (12): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), bits_alerts() (+4 more)

### Community 89 - "test_agent_advisor.py"
Cohesion: 0.10
Nodes (20): test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory(), run_turn(), test_running_calls_become_unknown_without_execution() (+12 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.14
Nodes (13): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+5 more)

### Community 91 - "test_bits_capabilities.py"
Cohesion: 0.12
Nodes (33): R2 — P1: capability discovery failure must remain visible, fake_tool(), parametrize, The shell-job environment is discoverable from the environment jobs really get., Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_every_published_operation_is_a_real_cli_command(), test_failed_discovery_is_explicit_in_every_view() (+25 more)

### Community 92 - "HistoricalDataStore"
Cohesion: 0.07
Nodes (28): Historical deployment state — verified 2026-10-05, 9. Recovering the market-data store, OSError, test_store_rejects_invalid_ohlc(), test_store_roundtrip(), test_trendbar_delta_decoding(), stream(), events() (+20 more)

### Community 93 - "test_live_feed.py"
Cohesion: 0.13
Nodes (35): config(), credentials(), FakeClient, FakeStore, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test…, The status file holds only the latest state, and these services write no… (+27 more)

### Community 94 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 95 - "PostgresConnection"
Cohesion: 0.14
Nodes (5): test_postgres_connection_uses_configured_read_committed(), CockroachHarnessStore, _now(), PostgresConnection, CockroachSourceStore

### Community 96 - "Signals"
Cohesion: 0.13
Nodes (11): Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Deterministic signal double: returns the same proposal until told otherwise., Signals, Source, Store, test_a_halt_from_another_process_still_stops_a_running_engine(), test_daily_loss_gate_still_applies_to_the_engine() (+3 more)

### Community 97 - "bits_runner.py"
Cohesion: 0.10
Nodes (28): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+20 more)

### Community 98 - "._note"
Cohesion: 0.10
Nodes (22): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), on_connected(), on_disconnected(), on_message(), tick(), confirmed(), guard() (+14 more)

### Community 99 - "pytest"
Cohesion: 0.07
Nodes (33): pytest, decision(), parametrize, Validation must not reject a real account, including a running one., The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is., The owner of a run is the only authority on whether it is live., The transcript had no DELETE anywhere and gained a row per heartbeat. 14,350… (+25 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.12
Nodes (17): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+9 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.08
Nodes (32): skipif, notes(), open_drafts(), PostgresLikeTranscript, R1: rejected memory writes keep durable draft identities until explicitly…, psycopg-like connection: one implicit transaction per block, committed or…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, RecordingPostgres (+24 more)

### Community 102 - "BitsStore"
Cohesion: 0.09
Nodes (17): Operations, test_agent_transcript_backend_selection_defaults_to_local(), agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., BitsStore, Uses the same connection selected for the application's transcript store., Read-modify-write several state keys atomically. SQLite connections run in…, Drop the oldest terminal job records. Nothing else ever deleted from this… (+9 more)

### Community 103 - "lab.py"
Cohesion: 0.16
Nodes (27): io, operator, parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate() (+19 more)

### Community 104 - "ctrader_demo.py"
Cohesion: 0.08
Nodes (13): test_open_api_transport_fails_reconciliation_on_an_error_reply(), build_reconcile_request(), CTraderDemoAdapter, CTraderDemoStore, CTraderTransport, _initial_state(), Protocol, Fail-closed cTrader Open API execution boundary for verified demo accounts. (+5 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.18
Nodes (18): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+10 more)

### Community 106 - "lab_codex.py"
Cohesion: 0.13
Nodes (17): Step 7d - MCP server (only if --mcp flag), test_harness_pins_luna_on_new_and_resumed_calls(), test_resumes_exact_thread_and_enables_native_compaction(), test_session_telemetry_tracks_native_compaction_incrementally(), test_thread_id_persisted_before_next_turn(), validate_turn(), Validate the small, explicit JSON-schema subset used for tool boundaries., _validate_json() (+9 more)

### Community 107 - "canonical_json"
Cohesion: 0.11
Nodes (19): Connection, Row, Explicit operator-only, flat paper account rebase; no research reset., rebase(), canonical_json(), _connect(), _now(), Any (+11 more)

### Community 108 - "file_lock"
Cohesion: 0.18
Nodes (16): The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker(), test_file_lock_times_out_instead_of_waiting_forever() (+8 more)

### Community 109 - "bits_memory.py"
Cohesion: 0.08
Nodes (44): _age_seconds(), BitsMemory, apply(), apply(), apply(), _brief(), _check_categories(), _check_draft_ids() (+36 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.14
Nodes (22): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+14 more)

### Community 111 - "BitsError"
Cohesion: 0.10
Nodes (39): 2. Publish the Datadog workflow message stream (required for the thinking panel), main(), call(), envelope(), interrogation(), parametrize, shell_action(), test_bare_string_evidence_is_one_reference() (+31 more)

### Community 112 - "LabStore"
Cohesion: 0.14
Nodes (12): test_snapshot_expiry_deletes_backend_rows(), store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics(), LabStore, save() (+4 more)

### Community 113 - "_error_code"
Cohesion: 0.23
Nodes (12): _error_code(), Return the cTrader error code for an error message, or None when unset., app_failed(), account_ok(), fail(), got_accounts(), got_symbols(), transport_failed() (+4 more)

### Community 114 - "lab_tools.py"
Cohesion: 0.19
Nodes (22): generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused(), test_symlinks_and_size_limit_refuse_execution() (+14 more)

### Community 115 - "fetch_source"
Cohesion: 0.09
Nodes (10): HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), test_fetch_keeps_raw_digest_and_bounds(), xauusd, NoRedirect, _excerpt_text(), fetch_source() (+2 more)

### Community 116 - "Operator runbook: engine, live feed, and the visible harness"
Cohesion: 0.10
Nodes (16): 10. Related documents, 1. What was built and why, 3. Enable the live data feed, 4. Enable the deterministic engine, 5. Restart the live view so the new observability is visible, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback (+8 more)

### Community 117 - "Requirements: reliable research-to-paper-trade workflow"
Cohesion: 0.18
Nodes (10): Delivery and operational boundaries, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit, P1 — Persist reproducible experiments and separate live signals, P1 — Separate monitoring cadence from meaningful agent reviews (+2 more)

### Community 118 - "DemoAutomationRunner"
Cohesion: 0.17
Nodes (6): DemoAutomationRunner, DemoLifecycle, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 119 - "read_quote"
Cohesion: 0.19
Nodes (16): ctrader_open_api_messages_openapimessages_pb2, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_feed_matches_account_and_symbol_before_recording(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time(), test_sample_once_second_history_retention_and_hard_bound() (+8 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.30
Nodes (16): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal(), aligned_returns(), classify_regimes() (+8 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "EngineeringManager"
Cohesion: 0.25
Nodes (8): _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker., _safe()

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.16
Nodes (9): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), attach_routes(), lab_chart(), lab_events(), lab_snapshot() (+1 more)

### Community 124 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 125 - "evidence_refs"
Cohesion: 0.38
Nodes (7): evidence_refs(), add(), ordered(), walk(), _legacy_draft(), Evidence references named by a (possibly malformed) payload: bounded, safe,…, The single pending record written by the previous release, as one open draft.

### Community 126 - "Local audit — 2026-09-24"
Cohesion: 0.14
Nodes (12): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC (+4 more)

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.14
Nodes (14): Architecture, Aurum — Codex Autonomous Trading Lab, Autonomous Agent, Codex efficiency — 2026-10-23, Configuration, Current Status, Demo Automation, Demo Automation Service (+6 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.18
Nodes (9): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, graphify, Local agent handoff — completed 2026-09-24, Open-agent extension — 2026-10-21, Purpose, Repository Operating Rules (+1 more)

### Community 133 - "types"
Cohesion: 0.24
Nodes (6): test_failed_worker_schedule_rolls_back_without_retry(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), types, release_healthy(), run(), schedule_verification()

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.22
Nodes (9): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Tools and compute (+1 more)

### Community 135 - "/graphify"
Cohesion: 0.22
Nodes (8): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Usage, What graphify is for

### Community 136 - "build_parser"
Cohesion: 0.25
Nodes (8): ArgumentParser, Without this the command exists but nothing runs it, so a hole still sits for…, test_the_heal_command_is_in_the_cli_grammar(), test_update_can_heal_and_the_timer_does(), test_the_raw_retention_command_is_in_the_cli_grammar(), test_the_rebuild_command_is_in_the_cli_grammar(), build_parser(), The complete CLI grammar; also used to publish supported operations.

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.25
Nodes (8): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Operating model, Research and automatic deployment, Storage and retention, Visibility

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "session_calendar.py"
Cohesion: 0.29
Nodes (6): DatetimeIndex, New York trading-week boundaries for research aggregation (never a trading…, The session week containing ``moment``; the weekend gap belongs to the week…, Naive New York wall time of each timestamp's session-week open (vectorized…, week_bounds(), _week_open_wall()

### Community 141 - ".path"
Cohesion: 0.33
Nodes (5): Interpreter guard for subcommands, Delivery Stages, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval, Research notes (`bits-memory`, schema `xauusd.notes/1`)

### Community 143 - "Merge review — 2026-09-25, baseline `cba22b2`"
Cohesion: 0.40
Nodes (5): Delivery order after this merge, Merge review — 2026-09-25, baseline `cba22b2`, R1 — P0: do not lose pending findings when memory is rewritten, R3 — P1: make experiment continuity work with the deployed backend, Runtime adoption is still pending

### Community 144 - "atomic_write_json"
Cohesion: 0.40
Nodes (4): atomic_write_json(), Any, Serialise ``payload`` as JSON and replace ``target`` atomically. ``allow_nan``…, Append a state transition to a bounded event log. The status file holds only…

### Community 145 - "Step 3 - Extract entities and relationships"
Cohesion: 0.50
Nodes (4): Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents), Part C - Merge AST + semantic into final extraction, Step 3 - Extract entities and relationships

## Knowledge Gaps
- **161 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+156 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1112 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `ConfirmedBreakoutCanarySource`, `pandas`, `.path`, `test_agent_loop.py`, `test_validation.py`, `cli.py`, `DataConfig`, `TournamentDataset`, `test_retention.py`, `test_automation.py`, `EngineConfig`, `ExecutionConfig`, `test_data.py`, `agent_controller`, `data.py`, `bits_capabilities.py`, `AgentTools`, `_datetime`, `main`, `test_live_feed.py`, `LiveFeedConfig`, `read_quote`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `PaperDecision`, `test_agent_loop.py`, `test_agent_view.py`, `cli.py`, `state_backup.py`, `test_demo_execution.py`, `test_lab.py`, `.__init__`, `test_demo_runner.py`, `Any`, `PaperToCTraderDemoCoordinator`, `restart_policy`, `create_app`, `ContinuousAgentRunner`, `agent_controller`, `test_engine_loop.py`, `_datetime`, `agent_experiments.py`, `main`, `PaperTradingEngine`, `Signals`, `pytest`, `lab.py`, `canonical_json`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `SQLiteAgentTranscriptStore` connect `SQLiteAgentTranscriptStore` to `test_bits_runner.py`, `PaperTrading`, `PaperDecision`, `test_agent_view.py`, `cli.py`, `state_backup.py`, `test_lab.py`, `data.py`, `test_bits_memory.py`, `main`, `test_bits_capabilities.py`, `pytest`, `test_bits_memory_drafts.py`, `BitsStore`, `canonical_json`, `atomic_write_text`, `BitsError`, `LabStore`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ExperimentRegistry` (e.g. with `R3 — P1: make experiment continuity work with the deployed backend` and `AdaptiveSearch`) actually correct?**
  _`ExperimentRegistry` has 12 INFERRED edges - model-reasoned connections that need verification._