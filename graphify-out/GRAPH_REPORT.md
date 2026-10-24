# Graph Report - xauusd-research-release  (2026-10-24)

## Corpus Check
- 198 files · ~198,949 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .service 8, (none) 7, .timer 2)

## Summary
- 3776 nodes · 10539 edges · 177 communities (148 shown, 29 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 556 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `15da44fc`
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
- test_ctrader_demo.py
- test_ml.py
- _collect_messages
- PaperTrading
- ImprovementLedger
- research_program.py
- test_ml_models.py
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- canonical_json
- test_agent_view.py
- synthetic_bars
- SQLiteAgentTranscriptStore
- XAUUSD discovery, incident, quantitative, and scaling audit
- create_app
- CTraderAuthError
- OpenAICompatiblePlanner
- test_state_backup.py
- test_demo_execution.py
- persist_tokens_env
- .create
- EngineeringManager
- test_lab.py
- setup
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- test_tournament_data.py
- ShadowTradingReadiness
- ExperimentSpec
- BitsStore
- test_tournament_runner.py
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
- automation.py
- ctrader_demo.py
- _datetime
- cli.py
- restart_policy
- Delivery Stages
- ExecutionConfig
- ContinuousAgentRunner
- Requirements: reliable research-to-paper-trade workflow
- Signals
- DemoAutomationRunner
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
- EngineConfig
- .__init__
- test_bits_memory.py
- CodexImprovementWorkflow
- test_engine_loop.py
- Local audit — 2026-09-24
- AgentTools
- MemoryConnection
- lab_api.py
- test_cli.py
- bits_memory.py
- AgentAdvisor
- PaperTradingEngine
- closed_bar
- CTraderVolumeConversion
- LiveBarFeed
- LabStore
- ml_models.py
- _registry_schema_valid
- test_bits_research.py
- ._note
- SQLitePaperTradingStore
- LiveFeedConfig
- test_bits_memory_drafts.py
- .run
- bars
- CTraderDemoOpenApiTransport
- test_weekly_report.py
- agent_controller
- test_oauth.py
- HistoricalDataStore
- test_dashboard.py
- atomic_write_text
- BitsError
- types
- LiveFeedUnavailable
- atomic_write_bytes
- _MainContent
- fetch_source
- verify_result_parity.py
- write_status
- data_heal
- test_portfolio_research.py
- .send
- file_lock
- test_lab_dashboard.py
- Operator runbook: engine, live feed, and the visible harness
- evidence_refs
- README.md
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- CTraderHistoricalAdapter
- market_is_open
- Persistent open-ended Codex agent
- json
- pytest
- Codex autonomous trading lab
- Datadog Bits connection
- Harness cleanup and improvement checklist — 2026-10-24
- _env_lock
- HarnessStore
- .from_env
- CTraderOpenApiConfig
- ToolRegistry
- lab_market.py
- _feed
- attach_routes
- harness-outcomes-plan-2026-10-23.md
- demo_feed_environment
- Research and measured self-improvement implementation plan
- _download_with_retry
- run
- timestamp
- CockroachHarnessStore
- FakeResponse
- trendbars_to_frame
- DemoRunnerConfig
- step_display
- PaperToCTraderDemoCoordinator
- agent_transcript_store_from_env
- Research program and measured improvement
- stopped_demo_adapter
- sklearn_base
- tarfile
- decision
- ._discover_account
- PaperTradingStore
- mutation_analytics
- RegimeTransformer
- test_sandbox_tests_return_bounded_feedback_and_clean_environment
- engine_decision_id
- graphify reference: transcribe video and audio
- test_health_reports_degraded_when_the_state_store_is_unavailable
- test_update_reports_a_failed_heal_without_failing_the_update
- .__init__
- .integrity_check

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `MemoryRegistry` - 89 edges
3. `HistoricalDataStore` - 80 edges
4. `ExperimentRegistry` - 76 edges
5. `SQLiteAgentTranscriptStore` - 73 edges
6. `setup()` - 71 edges
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

## Communities (177 total, 29 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.12
Nodes (25): account(), An unclassified account is not a demo account. ``isLive`` is a proto3 optional…, The discriminator has to work on the actual SDK message, not just dicts., test_demo_accounts_empty_when_all_live(), test_demo_accounts_excludes_a_dict_without_the_flag(), test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo(), test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account(), test_is_error_extracts_code_and_description() (+17 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.17
Nodes (16): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+8 more)

### Community 2 - "OperationsManager"
Cohesion: 0.09
Nodes (21): Automatic immutable scaling checkpoints — 2026-08-21, Scaling checkpoint and operational projection — 2026-08-21, test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs() (+13 more)

### Community 3 - "dashboard.py"
Cohesion: 0.09
Nodes (52): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, plotly_graph_objects, Request, secrets (+44 more)

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
Cohesion: 0.16
Nodes (21): append_bars(), newest_market(), Signal generator emitting one SELL transition at an absolute bar time. The…, store_with_bars(), test_canary_cold_start_ignores_a_transition_it_never_observed(), test_canary_drops_a_transition_beyond_the_backlog_bound(), test_canary_emits_each_transition_once(), test_canary_ignores_neutral_and_persistent_signals() (+13 more)

### Community 8 - "MemoryRegistry"
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "test_bits_capabilities.py"
Cohesion: 0.05
Nodes (77): Datadog Bits operations, ArgumentParser, Bits shell environment (`bits-capabilities`), platform, R2 — P1: capability discovery failure must remain visible, shlex, fake_tool(), parametrize (+69 more)

### Community 10 - "test_ctrader_demo.py"
Cohesion: 0.12
Nodes (27): adapter(), Message, test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_duplicate_request_never_sends_a_second_transport_call(), test_host_and_environment_rejections_are_fail_closed(), test_long_decision_id_is_persisted_but_broker_id_fits(), test_reconcile_maps_persisted_broker_id_back_to_internal_id() (+19 more)

### Community 11 - "test_ml.py"
Cohesion: 0.12
Nodes (25): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ndarray, test_appending_future_does_not_change_existing_ml_features(), test_calibration_and_drift_diagnostics_are_deterministic(), test_gradient_boosting_report_is_reproducible(), test_supervised_features_are_causal_and_labels_use_future(), test_walk_forward_campaign_is_research_only_and_baselined() (+17 more)

### Community 12 - "_collect_messages"
Cohesion: 0.28
Nodes (9): agent_messages(), _collect_messages(), Any, Validate the agent's self-questioning about its own decision. This is the bot…, Flatten a message content value to plain text, whatever shape it arrives in.…, Walk a response fragment and pull out ``{role, content}`` records in order., Extract the intermediate agent message stream from a workflow response. Empty…, _text_of() (+1 more)

### Community 13 - "PaperTrading"
Cohesion: 0.09
Nodes (51): paper_trading(), The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, No loop, and a heartbeat written by the previous release, are both silent., The monitor's status string alone was never enough. A monitor that died after…, test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_alerts_on_a_stale_or_dead_position_monitor(), test_health_names_the_paths_a_retrieval_loop_keeps_reading(), test_health_stays_quiet_when_no_path_repeats() (+43 more)

### Community 14 - "ImprovementLedger"
Cohesion: 0.13
Nodes (18): CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal(), ImprovementLedger (+10 more)

### Community 15 - "research_program.py"
Cohesion: 0.10
Nodes (37): copy, turn(), plan(), test_compact_context_pages_full_design_without_truncating_evidence(), test_completed_findings_accumulate_lessons_without_recounting(), test_discovery_insights_require_real_retrieval_and_do_not_claim_availability(), test_family_rejections_drive_pivot_without_resetting_learning(), test_full_advisor_discovery_plan_compute_findings_loop_survives_cycle_boundary() (+29 more)

### Community 16 - "test_ml_models.py"
Cohesion: 0.27
Nodes (9): ImportError, sample(), test_core_model_adapters_and_ensemble_probabilities(), test_optional_backend_has_actionable_error_when_missing(), test_regime_transformer_is_fit_then_reused(), create_model(), OptionalDependencyError, ProbabilityEnsemble (+1 more)

### Community 17 - "Any"
Cohesion: 0.11
Nodes (11): failed(), issue(), failed(), issue(), observe(), succeeded(), CTraderDemoStore, Any (+3 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.08
Nodes (51): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), parametrize, A ticking agent must not be served as stopped. The engine's startup reconcile…, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An… (+43 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.14
Nodes (17): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), firecrawl_fetch_tool() (+9 more)

### Community 20 - "canonical_json"
Cohesion: 0.07
Nodes (34): collections, P0/P1 implementation updates — 2026-08-20, io, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent() (+26 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.09
Nodes (15): _harness_client(), The deterministic engine writes to the same `agent_runs` table. Taking the…, `limit` alone does not bound a response. A shell-job step carries a captured…, A non-SQLite transcript store must not take the panel down., test_age_seconds_parses_timezone_aware_timestamps(), test_harness_endpoint_degrades_without_a_sqlite_store(), test_harness_page_renders_and_is_read_only(), test_harness_page_subscribes_to_the_event_stream() (+7 more)

### Community 22 - "synthetic_bars"
Cohesion: 0.07
Nodes (61): ast, numpy, operator, pandas, sklearn_metrics, socket, Secret-free deterministic parity fixture for the runtime container., test_all_baseline_signals_are_aligned_and_bounded() (+53 more)

### Community 23 - "SQLiteAgentTranscriptStore"
Cohesion: 0.07
Nodes (38): main(), Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, test_service_like_shell_runs_documented_examples_without_profile(), action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written… (+30 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (45): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20, Complete auxiliary backup integrity — 2026-08-21 (+37 more)

### Community 25 - "create_app"
Cohesion: 0.19
Nodes (11): fixture, server(), create_app(), data_update_status(), health(), job_output(), paper_endpoint(), paper_or_default() (+3 more)

### Community 26 - "CTraderAuthError"
Cohesion: 0.16
Nodes (18): test_data_update_does_not_retry_auth_errors(), unauthorized(), demo_env(), downloader_config(), test_download_does_not_retry_non_token_auth_error(), fake_fetch(), test_download_does_not_retry_without_a_refresh_token(), test_download_refreshes_once_then_retries_in_a_fresh_process() (+10 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.33
Nodes (9): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError, Any, ValueError (+1 more)

### Community 28 - "test_state_backup.py"
Cohesion: 0.21
Nodes (19): decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+11 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.15
Nodes (21): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+13 more)

### Community 30 - "persist_tokens_env"
Cohesion: 0.12
Nodes (19): PathLike, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent…, Smoke test: concurrent writers never produce an unparseable env file., test_persist_tokens_appends_missing_key_and_sets_0600() (+11 more)

### Community 31 - ".create"
Cohesion: 0.23
Nodes (5): frame_digest(), DataFrame, Path, Wait for a concurrent freeze of the same version to publish its manifest.…, Hash canonical timestamps, schema, and values independent of Parquet bytes.

### Community 32 - "EngineeringManager"
Cohesion: 0.25
Nodes (8): _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker., _safe()

### Community 33 - "test_lab.py"
Cohesion: 0.09
Nodes (40): parametrize, qualified_candidate(), quote(), test_codex_contract_rejects_unknown_fields_and_overlarge_requests(), test_evidence_relations_are_checked_beyond_digest(), test_forward_coverage_rejects_short_observation_despite_fixed_deadline(), test_forward_coverage_uses_new_york_market_minutes_and_accepts_complete_week(), test_forward_window_is_scored_once_then_rejected() (+32 more)

### Community 34 - "setup"
Cohesion: 0.15
Nodes (25): test_account_only_reset_preserves_research_and_stop(), test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), test_improvement_cannot_claim_old_release_as_new_work() (+17 more)

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

### Community 39 - "ExperimentSpec"
Cohesion: 0.16
Nodes (20): E. Current 50,000-scenario architecture and benchmark, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix(), test_proposal_catalog_eventually_exhausts() (+12 more)

### Community 40 - "BitsStore"
Cohesion: 0.14
Nodes (10): Operations, 5. Restart the live view so the new observability is visible, test_job_endpoint_pages_a_shell_capture(), test_bits_notes_only_does_not_repeat_history(), BitsStore, Uses the same connection selected for the application's transcript store., Read-modify-write several state keys atomically. SQLite connections run in…, Drop the oldest terminal job records. Nothing else ever deleted from this… (+2 more)

### Community 41 - "test_tournament_runner.py"
Cohesion: 0.15
Nodes (10): Dependence-aware bootstrap validation — 2026-08-21, setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition() (+2 more)

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.29
Nodes (11): Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_semantic_identity_ignores_provenance(), test_small_adaptive_batch_round_robins_families() (+3 more)

### Community 49 - "test_retention.py"
Cohesion: 0.11
Nodes (41): test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(), archive(), _local_backups(), test_compaction_reads_compressed_raw_pages(), test_completed_logs_only_and_pins(), test_completed_workspace_reclaims_training_and_scripts_but_keeps_memory(), test_completed_workspace_with_nested_symlink_retained(), test_compress_existing_exact_target_and_deterministic_bytes() (+33 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.13
Nodes (20): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+12 more)

### Community 51 - "InMemoryAgentTranscriptStore"
Cohesion: 0.10
Nodes (8): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), test_base_runner_records_codes_for_planner_and_tick_errors(), boom(), InMemoryAgentTranscriptStore, Test double only; production state lives in the configured backend store., Mirror of the SQLite retention so both backends behave the same., Family-scoped mirror of the SQL stores: never close another family's run.

### Community 52 - "automation.py"
Cohesion: 0.10
Nodes (28): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., Ranking, validation and selection must use three disjoint partitions. The…, test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_champion_is_not_replaced_when_either_side_lacks_a_dataset_binding() (+20 more)

### Community 53 - "ctrader_demo.py"
Cohesion: 0.08
Nodes (30): test_symbol_metadata_and_volume_policy_validate_invariants(), parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+22 more)

### Community 54 - "_datetime"
Cohesion: 0.12
Nodes (14): test_observation_is_future_only_tolerates_one_bar_of_forming(), Expire old price-mark results, never actual trade idempotency keys. Monitor…, CockroachPaperTradingStore, _now(), observation_is_future(), PaperDecision, transition(), transition() (+6 more)

### Community 55 - "cli.py"
Cohesion: 0.17
Nodes (18): dotenv, logging, test_backtest(), campaign(), cftc_point_in_time(), daily_run(), event_backtest(), main() (+10 more)

### Community 56 - "restart_policy"
Cohesion: 0.14
Nodes (14): Execution Boundary, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback, 7. Related documents (+6 more)

### Community 57 - "Delivery Stages"
Cohesion: 0.25
Nodes (5): Delivery Stages, Historical delivery and deployment notes, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval, Research notes (`bits-memory`, schema `xauusd.notes/1`)

### Community 58 - "ExecutionConfig"
Cohesion: 0.14
Nodes (27): main(), bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,…, Zero is a real value; a metric that cannot be computed must say so. Reporting… (+19 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.07
Nodes (19): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), CockroachAgentTranscriptStore, ContinuousAgentRunner, Any, BaseException (+11 more)

### Community 60 - "Requirements: reliable research-to-paper-trade workflow"
Cohesion: 0.18
Nodes (10): Delivery and operational boundaries, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit, P1 — Persist reproducible experiments and separate live signals, P1 — Separate monitoring cadence from meaningful agent reviews (+2 more)

### Community 61 - "Signals"
Cohesion: 0.13
Nodes (11): The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise., The 2026-10-05 sequence: a fresh engine, no halt anywhere, still no trade., Signals, Store, test_engine_does_nothing_when_the_signal_is_flat(), test_engine_refuses_to_evaluate_a_strategy_with_no_recorded_validation(), test_halt_stops_proposals_and_persists_the_reason() (+3 more)

### Community 62 - "DemoAutomationRunner"
Cohesion: 0.17
Nodes (6): DemoAutomationRunner, DemoLifecycle, Any, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Poll injected sources only after explicit enablement and reconciliation.

### Community 63 - "read_quote"
Cohesion: 0.21
Nodes (16): ctrader_open_api_messages_openapimessages_pb2, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_feed_matches_account_and_symbol_before_recording(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time(), test_sample_once_second_history_retention_and_hard_bound() (+8 more)

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
Nodes (15): test_nested_output_page_preserves_original_cursor_without_skipping_text(), error_details(), excerpt(), result_for_prompt(), BaseException, Payload-free classification of an exception for events and heartbeats.…, guidance_revision(), BitsAgentRunner (+7 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.12
Nodes (25): Delivery order after this merge, Merge review — 2026-09-25, baseline `cba22b2`, R1 — P0: do not lose pending findings when memory is rewritten, R3 — P1: make experiment continuity work with the deployed backend, Runtime adoption is still pending, at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from… (+17 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.07
Nodes (48): errno, _bars(), minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.…, Three valid, non-overlapping minutes, shifted so writers never collide., `data update` starts from the newest bar, so a hole in the middle is permanent.… (+40 more)

### Community 77 - "EngineConfig"
Cohesion: 0.14
Nodes (11): An oversized proposal must be visibly refused, not silently trimmed. Clamping…, test_a_halt_from_another_process_still_stops_a_running_engine(), test_engine_cannot_exceed_max_position(), test_engine_config_rejects_unbounded_values(), test_engine_does_not_clamp_an_oversized_proposal(), test_engine_status_reports_the_running_process_not_a_phantom(), engine_controller(), Operator and supervisor control for the deterministic trade engine. (+3 more)

### Community 78 - ".__init__"
Cohesion: 0.15
Nodes (5): EngineStore, MarketSource, Protocol, The narrow slice of the durable store the engine needs., TranscriptSink

### Community 79 - "test_bits_memory.py"
Cohesion: 0.11
Nodes (28): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, rejection(), reply(), sample_notes() (+20 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.10
Nodes (32): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., Re-read every tick, like the halt: a cached answer fails silently until restart., All 26 research results so far are rejected, so this is the common case., The hash stops a later edit to the artifact redefining what was granted. (+24 more)

### Community 82 - "Local audit — 2026-09-24"
Cohesion: 0.14
Nodes (12): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC (+4 more)

### Community 83 - "AgentTools"
Cohesion: 0.05
Nodes (46): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000) (+38 more)

### Community 86 - "lab_api.py"
Cohesion: 0.10
Nodes (18): test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), test_counter_update_rolls_back_with_owning_state_transaction(), test_counters_survive_detail_eviction_and_ignore_duplicate_updates(), test_read_only_lab_api_reports_actual_data_and_events(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal(), utc_day() (+10 more)

### Community 87 - "test_cli.py"
Cohesion: 0.21
Nodes (19): _isolated_bits_state(), no_broker(), _run_cli(), test_bits_capabilities_check_and_stored_manifest(), test_bits_capabilities_direct_discovery_exception_still_exits_nonzero(), test_bits_capabilities_stored_check_rejects_a_stale_manifest(), test_bits_job_errors_are_structured(), test_bits_memory_cli_draft_lifecycle() (+11 more)

### Community 88 - "bits_memory.py"
Cohesion: 0.10
Nodes (37): _age_seconds(), BitsMemory, apply(), apply(), apply(), _brief(), _check_categories(), _check_draft_ids() (+29 more)

### Community 89 - "AgentAdvisor"
Cohesion: 0.08
Nodes (21): Harness maintenance — 2026-10-24, test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_explicit_evidence_pages_and_source_excerpts_survive_context_compaction(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory() (+13 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.14
Nodes (13): EngineDecision, PaperTradingEngine, Any, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates., Stop the engine. Operator-only at the CLI, and callable by the supervisor. This…, Clear a halt. Never clears a paper or demo execution kill switch., Whether a durable halt is in force, re-read from the store every tick. The… (+5 more)

### Community 91 - "closed_bar"
Cohesion: 0.18
Nodes (7): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), closed_bar(), True once an M1 bar stamped at ``bar_time`` is complete., Accept a live bar, writing only bars known to be closed. The stream carries the…, Write the held bar. ``persist_bar`` re-checks close, age and order., Drop the subscription so a restart cannot replay bars into the store. Best…

### Community 92 - "CTraderVolumeConversion"
Cohesion: 0.13
Nodes (10): test_volume_policy_from_metadata(), _ctrader_demo_adapter(), expected_volume(), CTraderVolumeConversion, CTraderVolumePolicy, DemoExecutor, Protocol, Explicit conversion from paper quantity units to cTrader volume-in-cents units. (+2 more)

### Community 93 - "LiveBarFeed"
Cohesion: 0.12
Nodes (37): config(), credentials(), FakeClient, FakeStore, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test…, The status file holds only the latest state, and these services write no… (+29 more)

### Community 94 - "LabStore"
Cohesion: 0.15
Nodes (10): test_snapshot_expiry_deletes_backend_rows(), store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics(), LabStore, add() (+2 more)

### Community 95 - "ml_models.py"
Cohesion: 0.15
Nodes (9): importlib, sklearn_cluster, sklearn_ensemble, sklearn_mixture, sklearn_preprocessing, OfflinePolicyAdapter, ProbabilityModel, Protocol (+1 more)

### Community 96 - "_registry_schema_valid"
Cohesion: 0.21
Nodes (12): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_registry_validation_streams_rows_and_rejects_non_array_tables(), Validate logical snapshot JSON in bounded memory (8 MiB per row). Snapshots…, _registry_schema_valid() (+4 more)

### Community 97 - "test_bits_research.py"
Cohesion: 0.13
Nodes (23): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction() (+15 more)

### Community 98 - "._note"
Cohesion: 0.08
Nodes (25): test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), heartbeat(), on_connected(), on_disconnected(), on_message(), tick(), confirmed() (+17 more)

### Community 99 - "SQLitePaperTradingStore"
Cohesion: 0.06
Nodes (35): Engineering, Connection, Row, parametrize, The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is., The owner of a run is the only authority on whether it is live., The transcript had no DELETE anywhere and gained a row per heartbeat. 14,350… (+27 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.21
Nodes (11): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+3 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.08
Nodes (32): skipif, notes(), open_drafts(), PostgresLikeTranscript, R1: rejected memory writes keep durable draft identities until explicitly…, psycopg-like connection: one implicit transaction per block, committed or…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, RecordingPostgres (+24 more)

### Community 102 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 103 - "bars"
Cohesion: 0.18
Nodes (22): bars(), parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate(), test_dataset_advances_only_to_a_wholly_new_cohort() (+14 more)

### Community 104 - "CTraderDemoOpenApiTransport"
Cohesion: 0.15
Nodes (15): FakeClient, ImmediateDeferred, test_configured_account_id_bypasses_account_list_scope(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(), test_open_api_transport_fails_reconciliation_on_an_error_reply(), test_open_api_transport_reads_symbol_volume_metadata(), test_open_api_transport_rejects_non_demo_before_constructing_client(), test_open_api_transport_reports_an_order_error_reply_with_its_code() (+7 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.14
Nodes (22): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors() (+14 more)

### Community 106 - "agent_controller"
Cohesion: 0.15
Nodes (14): agent_controller(), _agent_data_refresh_source(), _agent_status_path(), _agent_status_view(), _build_engine(), _canary_source(), _demo_automation_runner(), _paper_from_env() (+6 more)

### Community 107 - "test_oauth.py"
Cohesion: 0.23
Nodes (15): response_json(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises(), test_refresh_access_token_returns_pair_with_browser_agent(), fake_urlopen(), test_rejected_grant_raises_oauth_error() (+7 more)

### Community 108 - "HistoricalDataStore"
Cohesion: 0.14
Nodes (14): A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, _seed_store(), frame(), validate() is no longer a one-time check performed only by from_env(). The…, test_download_revalidates_the_execution_boundary_at_the_network_call(), test_positions_matches_get_indexer(), test_positions_requires_a_sorted_unique_index(), test_positions_resolves_an_anchor_sweep_in_one_pass() (+6 more)

### Community 109 - "test_dashboard.py"
Cohesion: 0.19
Nodes (9): setup_files(), test_dashboard_reads_latest_run_and_equity(), test_dashboard_registry_requires_database_url_and_never_passes_a_path(), test_export_blocks_path_traversal(), test_health_is_public_but_api_can_require_auth(), test_live_snapshot_contains_operations_and_experiment_signature(), test_status_remains_readable_without_generated_tournament_dataset(), test_system_metrics_calculate_network_rate() (+1 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.14
Nodes (22): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+14 more)

### Community 111 - "BitsError"
Cohesion: 0.12
Nodes (30): call(), envelope(), interrogation(), parametrize, test_tick_errors_keep_a_classified_code_phase_and_safe_summary(), failing_poll(), shell_action(), test_bare_string_evidence_is_one_reference() (+22 more)

### Community 112 - "types"
Cohesion: 0.32
Nodes (5): test_failed_worker_schedule_rolls_back_without_retry(), test_research_advisories_do_not_disable_safe_software_releases(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), types, release_healthy()

### Community 113 - "LiveFeedUnavailable"
Cohesion: 0.14
Nodes (9): app_failed(), LiveFeedConfigError, LiveFeedUnavailable, RuntimeError, ValueError, A refused configuration, carrying a stable code. Subclasses ``ValueError``…, Authenticate the application, then resolve the demo account and symbol.…, Application auth, which the broker requires before any token request. Sending… (+1 more)

### Community 114 - "atomic_write_bytes"
Cohesion: 0.18
Nodes (24): generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused(), test_symlinks_and_size_limit_refuse_execution() (+16 more)

### Community 115 - "_MainContent"
Cohesion: 0.18
Nodes (7): HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), xauusd, _excerpt_text(), _MainContent, Prefer a publisher's explicit content region over repeated site menus.

### Community 116 - "fetch_source"
Cohesion: 0.18
Nodes (3): test_fetch_keeps_raw_digest_and_bounds(), NoRedirect, fetch_source()

### Community 117 - "verify_result_parity.py"
Cohesion: 0.33
Nodes (7): argparse, compare(), main(), Path, Compare two or more compute-job result directories without mutating them., result(), test_result_parity_accepts_equal_bundles_and_rejects_metric_drift()

### Community 118 - "write_status"
Cohesion: 0.24
Nodes (15): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), bits_alerts() (+7 more)

### Community 119 - "data_heal"
Cohesion: 0.24
Nodes (12): _heal_args(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _store_with_windows(), test_data_heal_defers_a_window_that_does_not_fit_the_budget(), test_data_heal_downloads_an_interior_window(), test_data_heal_dry_run_never_contacts_the_broker() (+4 more)

### Community 120 - "test_portfolio_research.py"
Cohesion: 0.19
Nodes (19): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), read(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal() (+11 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "file_lock"
Cohesion: 0.15
Nodes (15): The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker(), test_file_lock_times_out_instead_of_waiting_forever() (+7 more)

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.14
Nodes (5): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), test_statistics_counts_retained_evidence_without_claiming_success()

### Community 124 - "Operator runbook: engine, live feed, and the visible harness"
Cohesion: 0.20
Nodes (9): 10. Related documents, 1. What was built and why, 2. Publish the Datadog workflow message stream (required for the thinking panel), 4. Enable the deterministic engine, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback, Engine control (+1 more)

### Community 125 - "evidence_refs"
Cohesion: 0.38
Nodes (7): evidence_refs(), add(), ordered(), walk(), _legacy_draft(), Evidence references named by a (possibly malformed) payload: bounded, safe,…, The single pending record written by the previous release, as one open draft.

### Community 126 - "README.md"
Cohesion: 0.25
Nodes (3): Bits agent instructions, Autonomous Agent, Legacy Datadog planner operations

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.09
Nodes (23): Active Codex agent, Architecture, Aurum — Codex Autonomous Trading Lab, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+15 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.15
Nodes (13): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, graphify, Local agent handoff — completed 2026-09-24, Open-agent extension — 2026-10-21 (+5 more)

### Community 132 - "CTraderHistoricalAdapter"
Cohesion: 0.14
Nodes (8): Interpreter guard for subcommands, CTraderHistoricalAdapter, Path, Every archived raw page as ``(first_minute, last_minute, path)``, sorted. The…, Which archived pages a minimal cover makes redundant. Deletes nothing. The…, The same wire page, whether plain or losslessly gzip-compressed., Import cTrader CSV exports into the normalized historical store., read_raw_page()

### Community 133 - "market_is_open"
Cohesion: 0.16
Nodes (13): test_market_data_age_clamps_a_still_forming_bar_to_zero(), test_market_data_age_counts_from_bar_close_not_bar_open(), test_market_is_open_across_both_us_daylight_saving_transitions(), test_market_is_open_follows_the_new_york_close_in_us_standard_time(), test_market_is_open_session_matrix(), utc(), _open_minutes(), Observation opportunities under the shared New York market session. (+5 more)

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.20
Nodes (10): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Research continuity and maintenance — 2026-10-24 (+2 more)

### Community 135 - "json"
Cohesion: 0.05
Nodes (83): base64, concurrent_futures, contextlib, csv, dataclasses, datetime, fcntl, gzip (+75 more)

### Community 136 - "pytest"
Cohesion: 0.19
Nodes (14): pytest, test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame (+6 more)

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.20
Nodes (10): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Operating model, Research activity chat — 2026-10-23, Research and automatic deployment (+2 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "Harness cleanup and improvement checklist — 2026-10-24"
Cohesion: 0.40
Nodes (4): Audit findings, Broker smoke shutdown follow-up, Harness cleanup and improvement checklist — 2026-10-24, Verification and deployment log

### Community 140 - "_env_lock"
Cohesion: 0.22
Nodes (9): _env_key(), _env_lock(), guard(), _env_value(), Path, Exclusive lock around a `.env` read-modify-write, in its own directory. The…, Key name of an env assignment, tolerating a leading ``export`` and quotes.…, The whole env file with ``updates`` applied, preserving comments and order. A… (+1 more)

### Community 142 - ".from_env"
Cohesion: 0.29
Nodes (6): 7.1 Code — one relaxation (small, tested), 7.2 Deploy — one systemd unit (mirror rule applies), 7.3 Config/docs, 7. Required changes (tracked, not yet implemented), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout()

### Community 143 - "CTraderOpenApiConfig"
Cohesion: 0.43
Nodes (4): test_data_config_from_env_account_optionally_discovered(), test_data_config_rejects_non_demo_host(), test_data_config_requires_demo_only_flag(), CTraderOpenApiConfig

### Community 144 - "ToolRegistry"
Cohesion: 0.36
Nodes (3): Immutable-in-practice allow-list. Only the application can register tools., ToolRegistry, ToolSpec

### Community 145 - "lab_market.py"
Cohesion: 0.27
Nodes (11): pyarrow_parquet, test_dashboard_uses_metadata_and_bounded_tail_not_store_read(), chart(), _data(), chart_bars(), coverage(), _file(), _index_name() (+3 more)

### Community 146 - "_feed"
Cohesion: 0.15
Nodes (13): _feed(), parametrize, The exact 2026-10-08 outage: bar_write_failed, session open, no alert. The…, A feed that is alive and healthy but no longer persisting bars., No bars over a weekend is idle, not broken; alerting on it trains operators to…, A dead feed keeps reporting its last known state as healthy forever., The resubscribe cycle takes about two seconds and repeats every 900s. A health…, test_health_alerts_when_bars_go_stale_during_an_open_session() (+5 more)

### Community 147 - "attach_routes"
Cohesion: 0.24
Nodes (9): FastAPI, fastapi_responses, inspect, attach_routes(), lab_chart(), lab_events(), lab_snapshot(), resolve() (+1 more)

### Community 150 - "Research and measured self-improvement implementation plan"
Cohesion: 0.25
Nodes (7): Acceptance criteria, Delivery checklist, Deployment procedure, Final verification and deployment, Implementation evidence so far, Objective and boundaries, Research and measured self-improvement implementation plan

### Community 151 - "_download_with_retry"
Cohesion: 0.18
Nodes (9): Each attempt is a separate process, so the retry is driven by a runner. In-…, The reported cause is the real one, not the last attempt's wrapper., test_data_update_reraises_the_first_transient_failure(), test_data_update_retries_transient_failures(), _download_attempt_subprocess(), _download_with_retry(), Any, One single-shot ``data download`` in a fresh interpreter; returns its result. A… (+1 more)

### Community 153 - "timestamp"
Cohesion: 0.20
Nodes (21): functools, test_measured_bottleneck_seeds_one_backlog_item_and_preserves_baseline(), test_missing_baseline_cannot_be_claimed_and_inference_history_is_bounded(), test_observed_regression_cannot_be_labeled_improved(), test_recent_metric_window_does_not_bias_toward_retained_old_unknowns(), test_release_success_does_not_imply_measured_improvement(), Persistent Codex agenda and durable tool-call/result reasoning loop. The model…, improvement() (+13 more)

### Community 156 - "trendbars_to_frame"
Cohesion: 0.11
Nodes (15): Historical deployment state — verified 2026-10-05, 9. Recovering the market-data store, OSError, test_trendbar_delta_decoding(), Any, DataFrame, Contiguous runs of market-open minutes the store does not have. `validate`…, Replace the store with `bars`, merged into whatever is already there. One… (+7 more)

### Community 157 - "DemoRunnerConfig"
Cohesion: 0.14
Nodes (13): test_demo_automation_start_in_paper_only_mode_contacts_no_broker(), test_environment_config_is_disabled_unless_explicitly_true(), demo_automation(), _demo_automation_start(), _demo_automation_status(), Explicit operator override for the demo execution kill switch; paper and the…, Run the explicitly enabled local-data paper-to-demo canary., DecisionSource (+5 more)

### Community 158 - "step_display"
Cohesion: 0.14
Nodes (16): test_bits_decisions_show_summary_instead_of_protocol_json(), test_shell_command_and_output_are_not_in_collapsed_text(), harness(), steps(), stream(), events(), _engine_display_text(), _feed_alerts() (+8 more)

### Community 159 - "PaperToCTraderDemoCoordinator"
Cohesion: 0.21
Nodes (10): _decision_id(), handler(), NormalizedDecision, PaperToCTraderDemoCoordinator, Any, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it. (+2 more)

### Community 160 - "agent_transcript_store_from_env"
Cohesion: 0.20
Nodes (10): test_agent_transcript_backend_selection_defaults_to_local(), agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., bits_job_page(), bits_recover(), _command_failure(), Exception, Classified, payload-free failure: exception text and arguments are never echoed. (+2 more)

### Community 161 - "Research program and measured improvement"
Cohesion: 0.25
Nodes (7): Decision cycle, Discovery and sources, Improvement measurement, Preregistration and execution, Release readiness and visibility, Research program and measured improvement, Storage and limitations

### Community 162 - "stopped_demo_adapter"
Cohesion: 0.21
Nodes (6): DemoTransport, Without this the command exists but nothing runs it, so a hole still sits for…, stopped_demo_adapter(), test_demo_automation_start_keeps_the_switch_stopped_when_reconciliation_fails(), test_demo_automation_start_reconciles_then_clears_only_the_demo_switch(), test_update_can_heal_and_the_timer_does()

### Community 165 - "decision"
Cohesion: 0.25
Nodes (8): decision(), Validation must not reject a real account, including a running one., A row that parses but cannot be evaluated is corruption, not an account. Before…, test_sqlite_paper_store_corrupt_state_fails_closed(), test_sqlite_paper_store_keeps_a_valid_state_untouched(), test_sqlite_paper_store_kill_switch_persists_and_fails_closed(), test_sqlite_paper_store_persists_state_and_decision_idempotency(), test_sqlite_paper_store_rejects_valid_json_with_missing_keys()

### Community 166 - "._discover_account"
Cohesion: 0.57
Nodes (7): account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), Resolve the demo account and XAUUSD symbol id, then ``done``. Asynchronous,…

### Community 168 - "mutation_analytics"
Cohesion: 0.33
Nodes (3): Adaptive-mutation outcome analytics — 2026-08-21, test_mutation_analytics_measures_improvement_and_duplicates(), mutation_analytics()

### Community 171 - "engine_decision_id"
Cohesion: 0.50
Nodes (4): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), Durable identity for one engine decision. Derived from the bar, not from a…

## Knowledge Gaps
- **189 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+184 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1165 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `HistoricalDataStore` connect `HistoricalDataStore` to `CTraderHistoricalAdapter`, `ConfirmedBreakoutCanarySource`, `json`, `test_bits_capabilities.py`, `test_ml.py`, `CTraderOpenApiConfig`, `lab_market.py`, `test_agent_loop.py`, `canonical_json`, `synthetic_bars`, `CTraderAuthError`, `trendbars_to_frame`, `.create`, `test_lab.py`, `test_update_reports_a_failed_heal_without_failing_the_update`, `test_retention.py`, `automation.py`, `cli.py`, `test_data.py`, `AgentTools`, `lab_api.py`, `test_cli.py`, `LiveBarFeed`, `agent_controller`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `market_is_open`, `json`, `test_agent_loop.py`, `test_agent_view.py`, `create_app`, `test_state_backup.py`, `test_demo_execution.py`, `PaperToCTraderDemoCoordinator`, `test_lab.py`, `setup`, `decision`, `PaperTradingStore`, `BitsStore`, `test_health_reports_degraded_when_the_state_store_is_unavailable`, `.integrity_check`, `test_demo_runner.py`, `InMemoryAgentTranscriptStore`, `_datetime`, `cli.py`, `restart_policy`, `ContinuousAgentRunner`, `.__init__`, `test_engine_loop.py`, `test_cli.py`, `PaperTradingEngine`, `CTraderVolumeConversion`, `SQLitePaperTradingStore`, `agent_controller`, `data_heal`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `LiveBarFeed` connect `LiveBarFeed` to `._note`, `LiveFeedConfig`, `._discover_account`, `json`, `HistoricalDataStore`, `CTraderOpenApiConfig`, `LiveFeedUnavailable`, `cli.py`, `closed_bar`, `read_quote`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ExperimentRegistry` (e.g. with `R3 — P1: make experiment continuity work with the deployed backend` and `AdaptiveSearch`) actually correct?**
  _`ExperimentRegistry` has 12 INFERRED edges - model-reasoned connections that need verification._