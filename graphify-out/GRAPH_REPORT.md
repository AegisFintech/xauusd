# Graph Report - xauusd-merge-all  (2026-10-23)

## Corpus Check
- 140 files · ~160,191 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: (none) 7, .service 7, .timer 2)

## Summary
- 3126 nodes · 8545 edges · 126 communities (110 shown, 16 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 479 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `63706bc7`
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
- CTraderDemoOpenApiTransport
- pandas
- ._signal
- PaperTrading
- self_improve.py
- CockroachAgentTranscriptStore
- test_session_reset.py
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- synthetic_bars
- test_bits_jobs.py
- XAUUSD discovery, incident, quantitative, and scaling audit
- cli.py
- CTraderAuthError
- OpenAICompatiblePlanner
- test_state_backup.py
- test_demo_execution.py
- test_oauth.py
- test_tournament_runner.py
- catalog_size
- data_heal
- memory_registry.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- TournamentDataset
- pytest
- CTraderOpenApiDownloader
- InMemoryAgentTranscriptStore
- .__init__
- ._fetch
- AdaptiveSearch
- research-cron.sh
- start.sh
- tests/__init__.py
- xauusd/__init__.py
- xauusd-research
- BitsClient
- test_demo_runner.py
- test_ctrader_lifecycle.py
- test_automation.py
- CTraderDemoSafetyError
- canonical_json
- CTraderVolumeConversion
- restart_policy
- agent_view.py
- NormalizedDecision
- ContinuousAgentRunner
- graphify reference: extra exports and benchmark
- verify_result_parity.py
- EngineConfig
- graphify reference: query, path, explain
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
- core.py
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- bits_capabilities.py
- CockroachHarnessStore
- agent_loop.py
- HarnessStore
- main
- read_status
- InMemoryHarnessStore
- PaperTradingEngine
- test_bits_capabilities.py
- HistoricalDataStore
- test_live_feed.py
- .run
- PostgresConnection
- Store
- bits_runner.py
- ._note
- paper_trading.py
- LiveFeedConfig
- test_bits_memory_drafts.py
- BitsStore
- bits_memory.py
- BitsMemory
- test_weekly_report.py
- ._authenticate
- SQLiteAgentTranscriptStore
- file_lock
- NotesRejected
- missing_executables
- BitsError
- ._discover_account
- closed_bar
- Operator runbook: engine, live feed, and the visible harness
- Requirements: reliable research-to-paper-trade workflow
- RecordingPostgres
- PaperToCTraderDemoCoordinator
- .send
- StateTransaction
- StoreCorruptError
- evidence_refs
- _command_failure
- activation-2026-09-28.md
- harness_page.py
- traceback

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 103 edges
2. `MemoryRegistry` - 89 edges
3. `ExperimentRegistry` - 76 edges
4. `main()` - 70 edges
5. `HistoricalDataStore` - 68 edges
6. `InMemoryPaperTradingStore` - 65 edges
7. `SQLiteAgentTranscriptStore` - 64 edges
8. `BitsStore` - 63 edges
9. `canonical_json()` - 57 edges
10. `BitsError` - 55 edges

## Surprising Connections (you probably didn't know these)
- `12. Status of evidence` --references--> `OpenAICompatiblePlanner`  [INFERRED]
  docs/feasibility-datadog-bits-agent.md → xauusd/autonomous_harness.py
- `Original incident evidence (pre-merge snapshot)` --references--> `BitsError`  [INFERRED]
  requirements.md → xauusd/bits.py
- `R3 — P1: make experiment continuity work with the deployed backend` --references--> `ExperimentRegistry`  [INFERRED]
  requirements.md → xauusd/experiment_registry.py
- `Portfolio and regime research — 2026-08-21` --references--> `PortfolioResearch`  [INFERRED]
  docs/DISCOVERY_AND_SCALING_AUDIT_2026-08-19.md → xauusd/portfolio_research.py
- `Delivery order after this merge` --references--> `weekly_bars()`  [INFERRED]
  requirements.md → xauusd/session_calendar.py

## Import Cycles
- None detected.

## Communities (126 total, 16 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.06
Nodes (44): Autonomous Harness, Branch consolidation — 2026-10-23, graphify, Local agent handoff — completed 2026-09-24, Purpose, Repository Operating Rules, Required update workflow, Broker order IDs — follow-up #14 (+36 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.23
Nodes (16): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+8 more)

### Community 2 - "OperationsManager"
Cohesion: 0.08
Nodes (22): Automatic immutable scaling checkpoints — 2026-08-21, Scaling checkpoint and operational projection — 2026-08-21, test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs() (+14 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (64): asyncio, fastapi_security, fastapi_testclient, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected) (+56 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.09
Nodes (32): _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted., `monitor_error` used to be assigned and then read by nothing at all. (+24 more)

### Community 5 - "ExperimentRegistry"
Cohesion: 0.16
Nodes (7): ExperimentStatus, ExperimentRegistry, Any, datetime, Recover claims left by a previous instance of the single system worker., Requeue leases from replaced instances of a named worker pool., Path

### Community 6 - "InMemoryCTraderDemoStore"
Cohesion: 0.15
Nodes (7): _canonical_json(), CockroachCTraderDemoStore, _initial_state(), InMemoryCTraderDemoStore, _now(), Test double only; production execution state belongs in CockroachDB., Authoritative persistent execution state, idempotency, and audit store.

### Community 7 - "ConfirmedBreakoutCanarySource"
Cohesion: 0.17
Nodes (21): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+13 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "ml_models.py"
Cohesion: 0.09
Nodes (21): ImportError, importlib, sklearn_base, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, sample() (+13 more)

### Community 10 - "CTraderDemoOpenApiTransport"
Cohesion: 0.12
Nodes (22): FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(), test_open_api_transport_fails_reconciliation_on_an_error_reply(), test_open_api_transport_reads_symbol_volume_metadata() (+14 more)

### Community 11 - "pandas"
Cohesion: 0.11
Nodes (29): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, numpy, pandas, sklearn_metrics, Secret-free deterministic parity fixture for the runtime container., test_appending_future_does_not_change_existing_ml_features() (+21 more)

### Community 12 - "._signal"
Cohesion: 0.33
Nodes (6): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), datetime, Durable identity for one engine decision. Derived from the bar, not from a…, Ask the deterministic strategy for a direction, and size it here. The strategy…

### Community 13 - "PaperTrading"
Cohesion: 0.08
Nodes (55): paper_trading(), The monitor's status string alone was never enough. A monitor that died after…, test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_alerts_on_a_stale_or_dead_position_monitor(), test_job_endpoint_pages_a_shell_capture(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_once_reports_a_refused_restart() (+47 more)

### Community 14 - "self_improve.py"
Cohesion: 0.13
Nodes (20): base64, CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal() (+12 more)

### Community 15 - "CockroachAgentTranscriptStore"
Cohesion: 0.23
Nodes (4): CockroachAgentTranscriptStore, Production transcript store; the database is authoritative agent state., Close the caller's own interrupted runs left 'running' by a killed process.…, Re-assert a live process's own run row; see the SQLite store.

### Community 16 - "test_session_reset.py"
Cohesion: 0.38
Nodes (7): seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), AgentAlreadyRunning, AgentLock, Single process per container; the lock is runtime coordination, not state., reset_paper_session()

### Community 17 - "Any"
Cohesion: 0.10
Nodes (12): Client, failed(), issue(), failed(), issue(), observe(), succeeded(), CTraderDemoStore (+4 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.11
Nodes (37): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), A ticking agent must not be served as stopped. The engine's startup reconcile…, refresh_config(), refresh_runner() (+29 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.15
Nodes (16): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), FirecrawlConfig (+8 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.09
Nodes (22): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+14 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.06
Nodes (25): _feed(), _harness_client(), The deterministic engine writes to the same `agent_runs` table. Taking the…, `limit` alone does not bound a response. A shell-job step carries a captured…, The health endpoint is the observability surface; it must not raise. An…, A non-SQLite transcript store must not take the panel down., The exact 2026-10-08 outage: bar_write_failed, session open, no alert. The…, A feed that is alive and healthy but no longer persisting bars. (+17 more)

### Community 22 - "synthetic_bars"
Cohesion: 0.08
Nodes (55): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_campaign_writes_reproducible_manifest(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error() (+47 more)

### Community 23 - "test_bits_jobs.py"
Cohesion: 0.09
Nodes (27): action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes…, A failed preview is observability, and observability must not break the job., A post-spawn exception must not strand the row as `running` forever. `state`… (+19 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (45): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20, Complete auxiliary backup integrity — 2026-08-21 (+37 more)

### Community 25 - "cli.py"
Cohesion: 0.08
Nodes (63): collections, concurrent_futures, contextlib, dataclasses, datetime, dotenv, fcntl, gzip (+55 more)

### Community 26 - "CTraderAuthError"
Cohesion: 0.12
Nodes (16): Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., test_data_update_does_not_retry_auth_errors(), unauthorized(), test_data_update_reraises_the_first_transient_failure(), test_data_update_retries_transient_failures(), fake_fetch(), fake_fetch() (+8 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.22
Nodes (11): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError (+3 more)

### Community 28 - "test_state_backup.py"
Cohesion: 0.23
Nodes (18): decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+10 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.15
Nodes (21): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+13 more)

### Community 30 - "test_oauth.py"
Cohesion: 0.06
Nodes (48): PathLike, Market Data & Authentication, FakeResponse, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent… (+40 more)

### Community 31 - "test_tournament_runner.py"
Cohesion: 0.11
Nodes (17): Dependence-aware bootstrap validation — 2026-08-21, test_novel_formulas_generate_valid_signals(), test_proposal_catalog_eventually_exhausts(), test_proposal_engine_is_duplicate_safe_and_records_provenance(), setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable() (+9 more)

### Community 32 - "catalog_size"
Cohesion: 0.29
Nodes (9): E. Current 50,000-scenario architecture and benchmark, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix(), candidate_specs(), catalog_size(), combinations() (+1 more)

### Community 33 - "data_heal"
Cohesion: 0.24
Nodes (12): _heal_args(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _store_with_windows(), test_data_heal_defers_a_window_that_does_not_fit_the_budget(), test_data_heal_downloads_an_interior_window(), test_data_heal_dry_run_never_contacts_the_broker() (+4 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

### Community 36 - "Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent"
Cohesion: 0.12
Nodes (15): 10. Alternatives and fallback, 11. Recommendation, 12. Status of evidence, 1. Context and goal, 2. Feasibility verdict, 4. Datadog capabilities relevant to this swap (confirmed from Datadog docs), 5. Target architecture, 6. Safety and repository-rule compliance (unchanged) (+7 more)

### Community 37 - "TournamentDataset"
Cohesion: 0.07
Nodes (36): dataset(), A shared temporary name lets two writers interleave into one inode. `create`…, `write_text` truncates before it writes, so a reader can see a partial file.…, The invariant the shared temporary broke: one complete pointer, and it…, Two freezes of one version write identical bytes; neither may fail. The version…, A freeze killed mid-write must not hang the next one, nor quietly pass., A backtester or cost change must invalidate stored results. Both were hardcoded…, test_a_version_directory_with_no_manifest_fails_loudly() (+28 more)

### Community 38 - "pytest"
Cohesion: 0.06
Nodes (45): pytest, test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only() (+37 more)

### Community 39 - "CTraderOpenApiDownloader"
Cohesion: 0.31
Nodes (5): CTraderOpenApiDownloader, datetime, Timestamp, Read-only cTrader Open API client for symbols and historical trendbars., Re-run the whole download in a fresh interpreter and return its result. A…

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

### Community 49 - "BitsClient"
Cohesion: 0.13
Nodes (14): main(), call(), agent_messages(), BitsClient, _collect_messages(), Any, Validate the agent's self-questioning about its own decision. This is the bot…, Flatten a message content value to plain text, whatever shape it arrives in.… (+6 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.06
Nodes (37): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+29 more)

### Community 51 - "test_ctrader_lifecycle.py"
Cohesion: 0.13
Nodes (25): adapter(), test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_duplicate_request_never_sends_a_second_transport_call(), test_long_decision_id_is_persisted_but_broker_id_fits(), test_reconcile_maps_persisted_broker_id_back_to_internal_id(), test_recovery_failure_kills_and_blocks_execution(), test_transport_failure_is_an_unknown_outcome_that_blocks_restart() (+17 more)

### Community 52 - "test_automation.py"
Cohesion: 0.08
Nodes (33): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, Ranking, validation and selection must use three disjoint partitions. The…, _seed_store(), test_atomic_json_replaces_complete_document() (+25 more)

### Community 53 - "CTraderDemoSafetyError"
Cohesion: 0.09
Nodes (24): copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+16 more)

### Community 54 - "canonical_json"
Cohesion: 0.10
Nodes (17): canonical_json(), CockroachPaperTradingStore, _corrupt_state(), _default_state(), _now(), PaperDecision, transition(), transition() (+9 more)

### Community 55 - "CTraderVolumeConversion"
Cohesion: 0.13
Nodes (12): test_demo_factory_binds_authoritative_paper_exposure(), test_volume_policy_from_metadata(), _ctrader_demo_adapter(), expected_volume(), _paper_to_demo_coordinator(), CTraderVolumeConversion, CTraderVolumePolicy, DemoExecutor (+4 more)

### Community 56 - "restart_policy"
Cohesion: 0.14
Nodes (14): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+6 more)

### Community 57 - "agent_view.py"
Cohesion: 0.09
Nodes (33): FastAPI, fastapi_responses, fixture, server(), test_age_seconds_parses_timezone_aware_timestamps(), test_bits_decisions_show_summary_instead_of_protocol_json(), test_shell_command_and_output_are_not_in_collapsed_text(), _age_seconds() (+25 more)

### Community 58 - "NormalizedDecision"
Cohesion: 0.20
Nodes (9): The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise., Signals, test_engine_refuses_to_evaluate_a_strategy_with_no_recorded_validation(), test_resume_takes_effect_on_a_running_engine_without_a_restart(), NormalizedDecision, Strategy proposal expressed in configured paper-trading quantity units., DecisionSource (+1 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.10
Nodes (15): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), ContinuousAgentRunner, Any, BaseException, Protocol (+7 more)

### Community 60 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 61 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 62 - "EngineConfig"
Cohesion: 0.20
Nodes (9): test_engine_config_rejects_unbounded_values(), test_engine_status_reports_the_running_process_not_a_phantom(), _build_engine(), engine_controller(), Construct the deterministic engine from the same stores the agent uses., Operator and supervisor control for the deterministic trade engine., EngineConfig, _float_env() (+1 more)

### Community 63 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 64 - "ExecutionConfig"
Cohesion: 0.10
Nodes (32): main(), bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,…, Zero is a real value; a metric that cannot be computed must say so. Reporting… (+24 more)

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
Cohesion: 0.12
Nodes (12): error_details(), BaseException, Payload-free classification of an exception for events and heartbeats.…, guidance_revision(), BitsAgentRunner, Any, Retrieval-loop evidence for the heartbeat, which this file writes every tick. A…, Manifest of the shell-job environment, persisted so its facts survive cycles… (+4 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.05
Nodes (47): Bits agent instructions, Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration (+39 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.06
Nodes (57): errno, _bars(), demo_env(), downloader_config(), frame(), minute_60(), _minute_bars(), one_bar_at() (+49 more)

### Community 77 - "agent_controller"
Cohesion: 0.09
Nodes (22): parametrize, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An…, test_agent_config_rejects_non_finite_limits(), test_demo_automation_requires_explicit_positive_volume(), test_agent_transcript_backend_selection_defaults_to_local(), agent_transcript_store_from_env(), _positive_float(), Transcript store for the configured backend (local SQLite by default). (+14 more)

### Community 78 - "core.py"
Cohesion: 0.31
Nodes (7): test_backtest(), campaign(), BacktestConfig, Backtester, features(), DataFrame, Series

### Community 79 - "test_bits_memory.py"
Cohesion: 0.18
Nodes (21): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection(), reply(), sample_notes() (+13 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.09
Nodes (38): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., An oversized proposal must be visibly refused, not silently trimmed. Clamping…, Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case. (+30 more)

### Community 82 - "bits_capabilities.py"
Cohesion: 0.07
Nodes (40): Datadog Bits operations, ArgumentParser, platform, shlex, test_shell_environment_keeps_the_latest_refreshed_tokens(), test_shell_path_prepends_service_interpreter_and_declared_directories(), test_the_heal_command_is_in_the_cli_grammar(), test_the_raw_retention_command_is_in_the_cli_grammar() (+32 more)

### Community 84 - "agent_loop.py"
Cohesion: 0.18
Nodes (24): Engineering, build_agent_registry(), canary_signal_tool(), handler(), _decision_id(), paper_state_tool(), propose_trade_tool(), handler() (+16 more)

### Community 87 - "main"
Cohesion: 0.10
Nodes (32): DemoTransport, _isolated_bits_state(), no_broker(), Without this the command exists but nothing runs it, so a hole still sits for…, An interior hole is a smaller problem than a refresh reported as failed. The…, _run_cli(), stopped_demo_adapter(), test_bits_capabilities_check_and_stored_manifest() (+24 more)

### Community 88 - "read_status"
Cohesion: 0.17
Nodes (19): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent. (+11 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.16
Nodes (12): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+4 more)

### Community 91 - "test_bits_capabilities.py"
Cohesion: 0.12
Nodes (35): R2 — P1: capability discovery failure must remain visible, fake_tool(), The shell-job environment is discoverable from the environment jobs really get., Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_every_published_operation_is_a_real_cli_command(), test_failed_discovery_is_explicit_in_every_view() (+27 more)

### Community 92 - "HistoricalDataStore"
Cohesion: 0.08
Nodes (21): Current deployment state — verified 2026-10-05, Interpreter guard for subcommands, Research notes (`bits-memory`, schema `xauusd.notes/1`), test_store_rejects_invalid_ohlc(), test_store_roundtrip(), test_trendbar_delta_decoding(), CTraderHistoricalAdapter, HistoricalDataStore (+13 more)

### Community 93 - "test_live_feed.py"
Cohesion: 0.13
Nodes (35): config(), credentials(), demo_feed_environment(), FakeClient, FakeStore, fixture, A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test… (+27 more)

### Community 94 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 95 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 96 - "Store"
Cohesion: 0.25
Nodes (4): The 2026-10-05 sequence: a fresh engine, no halt anywhere, still no trade., Store, test_halt_stops_proposals_and_persists_the_reason(), test_the_gate_holds_with_no_halt_key_and_survives_a_restart()

### Community 97 - "bits_runner.py"
Cohesion: 0.09
Nodes (31): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+23 more)

### Community 98 - "._note"
Cohesion: 0.10
Nodes (20): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), on_connected(), on_disconnected(), on_message(), tick(), confirmed(), guard() (+12 more)

### Community 99 - "paper_trading.py"
Cohesion: 0.12
Nodes (27): decision(), parametrize, Validation must not reject a real account, including a running one., A row that parses but cannot be evaluated is corruption, not an account. Before…, test_agent_start_leaves_a_running_engine_run_alone(), test_invalid_backend_raises(), test_paper_from_env_defaults_to_local_sqlite_store(), test_sqlite_integrity_check_detects_corruption() (+19 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.11
Nodes (18): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase(), check(), LiveFeedConfig (+10 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.12
Nodes (30): skipif, memory(), notes(), open_drafts(), fixture, R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject() (+22 more)

### Community 102 - "BitsStore"
Cohesion: 0.16
Nodes (9): Operations, memory(), fixture, job_output(), BitsStore, Uses the same connection selected for the application's transcript store., Read-modify-write several state keys atomically. SQLite connections run in…, Drop the oldest terminal job records. Nothing else ever deleted from this… (+1 more)

### Community 103 - "bits_memory.py"
Cohesion: 0.16
Nodes (24): _age_seconds(), apply(), _brief(), _check_categories(), _check_entry(), check_notes(), _close(), _empty_drafts() (+16 more)

### Community 104 - "BitsMemory"
Cohesion: 0.28
Nodes (4): BitsMemory, _note_sources(), _notes_base(), A specific next task for unresolved drafts; not a new research cycle.

### Community 105 - "test_weekly_report.py"
Cohesion: 0.17
Nodes (19): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+11 more)

### Community 106 - "._authenticate"
Cohesion: 0.33
Nodes (3): app_failed(), Authenticate the application, then resolve the demo account and symbol.…, Application auth, which the broker requires before any token request. Sending…

### Community 107 - "SQLiteAgentTranscriptStore"
Cohesion: 0.08
Nodes (22): Connection, Row, test_bits_notes_only_does_not_repeat_history(), The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is., The owner of a run is the only authority on whether it is live., The transcript had no DELETE anywhere and gained a row per heartbeat. 14,350…, Pruning must not delete content a connected reader has not displayed yet. The… (+14 more)

### Community 108 - "file_lock"
Cohesion: 0.18
Nodes (16): The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker(), test_file_lock_times_out_instead_of_waiting_forever() (+8 more)

### Community 109 - "NotesRejected"
Cohesion: 0.13
Nodes (18): apply(), apply(), _check_draft_ids(), issue(), NotesRejected, _now(), parse_notes_input(), One payload-free validation problem. ``retry`` says what makes a retry useful. (+10 more)

### Community 110 - "missing_executables"
Cohesion: 0.50
Nodes (4): parametrize, test_missing_executables_are_detected_from_shell_messages(), missing_executables(), Names bash (or /usr/bin/env) reported as not found in a completed job's stderr.

### Community 111 - "BitsError"
Cohesion: 0.15
Nodes (27): envelope(), interrogation(), parametrize, test_tick_errors_keep_a_classified_code_phase_and_safe_summary(), failing_poll(), shell_action(), test_bare_string_evidence_is_one_reference(), test_errors_carry_stable_codes_and_only_safe_text() (+19 more)

### Community 113 - "._discover_account"
Cohesion: 0.57
Nodes (7): account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), Resolve the demo account and XAUUSD symbol id, then ``done``. Asynchronous,…

### Community 115 - "closed_bar"
Cohesion: 0.18
Nodes (7): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 116 - "Operator runbook: engine, live feed, and the visible harness"
Cohesion: 0.18
Nodes (10): 10. Related documents, 1. What was built and why, 2. Publish the Datadog workflow message stream (required for the thinking panel), 4. Enable the deterministic engine, 5. Restart the live view so the new observability is visible, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback (+2 more)

### Community 117 - "Requirements: reliable research-to-paper-trade workflow"
Cohesion: 0.12
Nodes (15): Delivery and operational boundaries, Delivery order after this merge, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Merge review — 2026-09-25, baseline `cba22b2`, Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit (+7 more)

### Community 119 - "RecordingPostgres"
Cohesion: 0.20
Nodes (3): PostgresLikeTranscript, psycopg-like connection: one implicit transaction per block, committed or…, RecordingPostgres

### Community 120 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.33
Nodes (7): PaperToCTraderDemoCoordinator, Any, datetime, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it., Runs paper risk first; execution lifecycle remains explicitly operator…

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 123 - "StoreCorruptError"
Cohesion: 0.17
Nodes (11): 9. Recovering the market-data store, OSError, `error_type: OSError` with `error_code: null` was undiagnosable. That is all…, test_a_corrupt_store_is_reported_as_corrupt_not_as_a_bare_oserror(), test_classify_store_error_names_a_full_disk_and_refuses_to_guess(), classify_store_error(), BaseException, The newest bar in the store, reading the index column only. `data update` needs… (+3 more)

### Community 125 - "evidence_refs"
Cohesion: 0.60
Nodes (5): evidence_refs(), add(), ordered(), walk(), Evidence references named by a (possibly malformed) payload: bounded, safe,…

### Community 127 - "_command_failure"
Cohesion: 0.50
Nodes (4): bits_job_page(), _command_failure(), Exception, Classified, payload-free failure: exception text and arguments are never echoed.

## Knowledge Gaps
- **148 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+143 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 986 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `test_session_reset.py`, `test_agent_loop.py`, `test_agent_view.py`, `cli.py`, `test_state_backup.py`, `test_demo_execution.py`, `data_heal`, `InMemoryAgentTranscriptStore`, `.__init__`, `test_demo_runner.py`, `canonical_json`, `CTraderVolumeConversion`, `restart_policy`, `agent_view.py`, `ContinuousAgentRunner`, `agent_controller`, `test_engine_loop.py`, `agent_loop.py`, `main`, `read_status`, `PaperTradingEngine`, `paper_trading.py`, `PaperToCTraderDemoCoordinator`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `LiveBarFeed` connect `test_live_feed.py` to `._note`, `LiveFeedConfig`, `._authenticate`, `test_data.py`, `._discover_account`, `closed_bar`, `cli.py`, `HistoricalDataStore`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `ExecutionConfig`, `LiveFeedConfig`, `TournamentDataset`, `ConfirmedBreakoutCanarySource`, `test_data.py`, `pandas`, `agent_controller`, `test_agent_loop.py`, `bits_capabilities.py`, `test_automation.py`, `agent_loop.py`, `synthetic_bars`, `main`, `cli.py`, `StoreCorruptError`, `test_live_feed.py`, `EngineConfig`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ExperimentRegistry` (e.g. with `R3 — P1: make experiment continuity work with the deployed backend` and `AdaptiveSearch`) actually correct?**
  _`ExperimentRegistry` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `main()` (e.g. with `CTraderAuthError` and `CTraderOpenApiConfig`) actually correct?**
  _`main()` has 4 INFERRED edges - model-reasoned connections that need verification._