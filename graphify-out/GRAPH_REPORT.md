# Graph Report - xauusd-cleanup-release  (2026-10-24)

## Corpus Check
- 192 files · ~193,458 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .service 8, (none) 7, .timer 2)

## Summary
- 3692 nodes · 10276 edges · 159 communities (136 shown, 23 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 540 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5228adc4`
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
- bits_capabilities.py
- CTraderDemoOpenApiTransport
- ml_campaign.py
- json
- PaperTrading
- self_improve.py
- bits_memory.py
- SQLitePaperTradingStore
- Any
- test_agent_loop.py
- FirecrawlResearchClient
- RemoteComputeBridge
- test_agent_view.py
- test_validation.py
- SecretFilter
- XAUUSD discovery, incident, quantitative, and scaling audit
- run
- CTraderAuthError
- OpenAICompatiblePlanner
- state_backup.py
- test_demo_execution.py
- persist_tokens_env
- TournamentDataset
- ExperimentSpec
- test_lab.py
- agent_advisor.py
- What You Must Do When Invoked
- Feasibility: replace the planner LLM endpoint with a Datadog Bits AI agent
- synthetic_bars
- ShadowTradingReadiness
- build_features
- Operator runbook: engine, live feed, and the visible harness
- bits_jobs.py
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
- Any
- DemoAutomationRunner
- Operations
- CTraderHistoricalAdapter
- ExecutionConfig
- ContinuousAgentRunner
- Requirements: reliable research-to-paper-trade workflow
- CodexResearchClient
- BitsStore
- test_oauth.py
- ctrader_demo.py
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
- oauth.py
- BitsMemory
- canonical_json
- CodexImprovementWorkflow
- test_engine_loop.py
- test_bits_capabilities.py
- AgentTools
- MemoryConnection
- lab_api.py
- main
- NotesRejected
- AgentAdvisor
- PaperTradingEngine
- .stop
- cli.py
- LiveBarFeed
- LabStore
- PostgresConnection
- data_heal
- bits_runner.py
- ._note
- SQLiteAgentTranscriptStore
- LiveFeedConfig
- test_bits_memory_drafts.py
- .run
- lab_strategy.py
- test_ctrader_lifecycle.py
- test_weekly_report.py
- Any
- HistoricalDataStore
- atomic_write_json
- Local audit — 2026-09-24
- atomic_write_text
- BitsError
- _registry_schema_valid
- ._discover_account
- lab_tools.py
- lab_sources.py
- RecordingPostgres
- test_session_reset.py
- write_status
- read_quote
- portfolio_research.py
- .send
- pytest
- test_lab_dashboard.py
- weekly_report.py
- evidence_refs
- README.md
- Aurum — Codex Autonomous Trading Lab
- activation-2026-09-28.md
- harness_page.py
- traceback
- Repository Operating Rules
- PaperDecision
- run
- Persistent open-ended Codex agent
- fetch_source
- test_offline.py
- Codex autonomous trading lab
- Datadog Bits connection
- Harness cleanup and improvement checklist — 2026-10-24
- InMemoryHarnessStore
- Merge review — 2026-09-25, baseline `cba22b2`
- ._subscribe
- test_lab_retention.py
- PaperTradingStore
- engine_decision_id
- _run_family
- StateTransaction
- harness-outcomes-plan-2026-10-23.md
- demo_feed_environment
- lab.py
- index
- setup
- CockroachHarnessStore
- trendbars_to_frame
- paper_trading.py
- _datetime
- sklearn_base
- tarfile

## God Nodes (most connected - your core abstractions)
1. `PaperTrading` - 114 edges
2. `MemoryRegistry` - 89 edges
3. `HistoricalDataStore` - 80 edges
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

## Communities (159 total, 23 thin omitted)

### Community 0 - "test_ctrader_auth.py"
Cohesion: 0.12
Nodes (25): account(), An unclassified account is not a demo account. ``isLive`` is a proto3 optional…, The discriminator has to work on the actual SDK message, not just dicts., test_demo_accounts_empty_when_all_live(), test_demo_accounts_excludes_a_dict_without_the_flag(), test_demo_accounts_keeps_only_accounts_the_broker_classified_as_demo(), test_demo_accounts_reads_explicit_presence_on_a_real_protobuf_account(), test_is_error_extracts_code_and_description() (+17 more)

### Community 1 - "test_autonomous_harness.py"
Cohesion: 0.35
Nodes (14): planner_action(), transport(), planner_actions(), test_final_response_completes_without_executing_a_tool(), test_harness_executes_only_registered_tool_and_persists_audit_events(), test_invalid_tool_output_retries_then_fails_with_audited_attempts(), test_optional_display_only_reason_is_accepted_and_string_checked(), test_tool_result_is_evidence_for_the_next_bounded_planner_turn() (+6 more)

### Community 2 - "OperationsManager"
Cohesion: 0.09
Nodes (19): test_artifact_retention_inventory_reports_policy_and_file_mismatches(), test_backup_preserves_scaling_checkpoints_with_integrity_manifest(), test_backup_uses_cockroach_logical_snapshot_and_manifest(), test_backup_verification_detects_auxiliary_corruption_and_unsafe_path(), test_backup_verification_fails_closed_on_checkpoint_corruption_and_unsafe_path(), test_capacity_plan_fails_closed_without_measurement_and_validates_inputs(), test_capacity_plan_rounds_up_with_efficiency_and_optional_cost(), test_checkpoint_capture_is_atomic_and_first_observation_is_immutable() (+11 more)

### Community 3 - "dashboard.py"
Cohesion: 0.06
Nodes (63): asyncio, fastapi_security, get, HTTPBasicCredentials, middleware, graphify reference: transcribe video and audio, Step 2.5 - Transcribe video / audio files (only if video files detected), plotly_graph_objects (+55 more)

### Community 4 - "test_bits_runner.py"
Cohesion: 0.08
Nodes (34): test_bootstrap_delivery_is_remembered_and_revision_changes_invalidate(), _looping_agent(), MissingToolPlanner, Planner, A `running` job past the executor ceiling is dead, not alive. The worker thread…, The staleness check must not stop the runner polling a live command., The risk monitor cannot fail silently behind a healthy heartbeat., A transient failure must not persist a stop that was never warranted. (+26 more)

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
Cohesion: 0.11
Nodes (15): MemoryRegistry, Small behavioral registry double; production always uses CockroachDB., spec(), test_champion_history_is_atomic_and_requires_improvement(), test_claim_is_priority_ordered_and_failure_is_recorded(), test_fingerprint_is_canonical_and_ignores_commit(), test_leaderboard_orders_validation_score(), test_registration_rejects_duplicate_identity() (+7 more)

### Community 9 - "bits_capabilities.py"
Cohesion: 0.07
Nodes (39): ArgumentParser, platform, shlex, test_shell_environment_keeps_the_latest_refreshed_tokens(), test_shell_path_prepends_service_interpreter_and_declared_directories(), test_the_heal_command_is_in_the_cli_grammar(), test_the_raw_retention_command_is_in_the_cli_grammar(), test_the_rebuild_command_is_in_the_cli_grammar() (+31 more)

### Community 10 - "CTraderDemoOpenApiTransport"
Cohesion: 0.11
Nodes (22): FakeClient, ImmediateDeferred, Message, test_configured_account_id_bypasses_account_list_scope(), test_host_and_environment_rejections_are_fail_closed(), test_open_api_transport_discovers_demo_account_and_normalizes_reconciliation(), test_open_api_transport_fails_reconciliation_on_an_error_reply(), test_open_api_transport_reads_symbol_volume_metadata() (+14 more)

### Community 11 - "ml_campaign.py"
Cohesion: 0.06
Nodes (46): ML governance and drift controls — 2026-08-21, HistGradientBoostingClassifier, ImportError, importlib, ndarray, sklearn_cluster, sklearn_ensemble, sklearn_metrics (+38 more)

### Community 12 - "json"
Cohesion: 0.11
Nodes (37): argparse, collections, concurrent_futures, csv, dataclasses, datetime, gzip, hashlib (+29 more)

### Community 13 - "PaperTrading"
Cohesion: 0.09
Nodes (52): No loop, and a heartbeat written by the previous release, are both silent., test_health_stays_quiet_when_no_path_repeats(), test_job_endpoint_pages_a_shell_capture(), test_agent_controller_refuses_on_corrupt_state(), test_agent_resume_refused_after_operator_stop_writes_status(), test_demo_automation_once_reports_a_refused_restart(), test_paper_start_overrides_operator_stop(), test_paper_stop_persists_kill_switch() (+44 more)

### Community 14 - "self_improve.py"
Cohesion: 0.13
Nodes (20): base64, CompletedProcess, _patch(), Ledger + money-gate tests for the self-improvement proposal store. Written…, test_core_trading_patch_is_flagged_needs_operator_gate(), test_ledger_rejects_duplicate_title_tuple(), test_ledger_submit_reopen_integrity(), apply_proposal() (+12 more)

### Community 15 - "bits_memory.py"
Cohesion: 0.17
Nodes (22): _age_seconds(), apply(), _brief(), _check_categories(), _check_entry(), check_notes(), _close(), _empty_drafts() (+14 more)

### Community 16 - "SQLitePaperTradingStore"
Cohesion: 0.22
Nodes (11): Connection, test_sqlite_integrity_check_detects_corruption(), test_sqlite_paper_store_integrity_check_reports_ok(), Explicit operator-only, flat paper account rebase; no research reset., rebase(), _connect(), Any, Minimal local SQLite state stores for paper trading and the agent transcript.… (+3 more)

### Community 17 - "Any"
Cohesion: 0.09
Nodes (17): build_reconcile_request(), failed(), issue(), failed(), issue(), observe(), succeeded(), CTraderDemoSafetyError (+9 more)

### Community 18 - "test_agent_loop.py"
Cohesion: 0.09
Nodes (45): agent_runner(), fresh_paper(), fresh_source(), market_store(), paper_only_coordinator(), parametrize, A ticking agent must not be served as stopped. The engine's startup reconcile…, `nan <= 0` and `inf <= 0` are both False, so the original check passed them. An… (+37 more)

### Community 19 - "FirecrawlResearchClient"
Cohesion: 0.14
Nodes (16): client(), parametrize, test_firecrawl_only_fetches_allow_listed_https_sources_and_records_provenance(), test_firecrawl_rejects_unscoped_or_sensitive_source_urls(), test_firecrawl_star_domain_allow_allows_any_https_source(), test_firecrawl_star_domain_still_rejects_insecure_or_credential_urls(), test_firecrawl_tool_marks_content_as_untrusted_and_applies_content_limit(), FirecrawlConfig (+8 more)

### Community 20 - "RemoteComputeBridge"
Cohesion: 0.10
Nodes (23): P0/P1 implementation updates — 2026-08-20, setup(), test_artifact_retention_keeps_candidates_and_deterministic_audits(), test_compute_job_is_fingerprinted_and_never_reads_holdout(), test_compute_job_rejects_wrong_dataset(), test_control_plane_refills_at_ten_percent(), test_coordinator_drain_flag_is_reversible(), test_readiness_degrades_for_unsynchronized_or_drifted_clock() (+15 more)

### Community 21 - "test_agent_view.py"
Cohesion: 0.06
Nodes (31): _feed(), _harness_client(), paper_trading(), fixture, parametrize, A non-SQLite transcript store must not take the panel down., The exact 2026-10-08 outage: bar_write_failed, session open, no alert. The…, A feed that is alive and healthy but no longer persisting bars. (+23 more)

### Community 22 - "test_validation.py"
Cohesion: 0.10
Nodes (31): Dependence-aware bootstrap validation — 2026-08-21, An empty training window must fail loudly, not look like a negative result., The embargo must reach the report, not just the helper. `walk_forward_splits`…, The negative path was never asserted, which is why several real defects…, A 30-bar rolling feature reaches across the split boundary. The last…, test_block_bootstrap_preserves_clustered_sequence_effect(), test_bootstrap_is_seeded_and_reports_loss_probability(), test_bootstrap_rejects_invalid_configuration() (+23 more)

### Community 23 - "SecretFilter"
Cohesion: 0.08
Nodes (30): action(), jobs(), fixture, bits_jobs grew without limit: 313 rows held 1.7 MB in two days. One row per…, A 20-minute backtest must not look like a hung harness. The record is written…, A preview is scrubbed exactly like the stored record. A partial publish writes…, A failed preview is observability, and observability must not break the job., A post-spawn exception must not strand the row as `running` forever. `state`… (+22 more)

### Community 24 - "XAUUSD discovery, incident, quantitative, and scaling audit"
Cohesion: 0.04
Nodes (47): A. What was actually inspected, Artifact-retention measurement — 2026-08-21, Automatic immutable scaling checkpoints — 2026-08-21, Automatic scaling-checkpoint acceptance — 2026-08-21, B. Existing architecture and data flow, C. Existing features that should be preserved, Checkpoint progress review — 2026-08-22, Compact artifact retention — 2026-08-20 (+39 more)

### Community 26 - "CTraderAuthError"
Cohesion: 0.08
Nodes (31): The reported cause is the real one, not the last attempt's wrapper., test_data_update_does_not_retry_auth_errors(), unauthorized(), test_data_update_reraises_the_first_transient_failure(), demo_env(), downloader_config(), validate() is no longer a one-time check performed only by from_env(). The…, test_data_config_from_env_account_optionally_discovered() (+23 more)

### Community 27 - "OpenAICompatiblePlanner"
Cohesion: 0.24
Nodes (10): 3. Where the planner is wired today (confirmed), 8. Prototype gate and test plan (execute BEFORE any cutover), test_planner_from_env_configures_model_and_timeout(), test_planner_from_env_rejects_a_non_positive_timeout(), _check_reason(), OpenAICompatiblePlanner, parse_action(), PlannerResponseError (+2 more)

### Community 28 - "state_backup.py"
Cohesion: 0.17
Nodes (21): decision(), seeded_db(), test_backup_keeps_validating_wal_writes(), test_backup_refuses_corrupt_source(), test_backup_restore_round_trip_preserves_state(), test_restore_can_explicitly_preserve_a_running_account(), test_restore_refuses_garbage_archive(), test_restore_refuses_sha256_tampering() (+13 more)

### Community 29 - "test_demo_execution.py"
Cohesion: 0.14
Nodes (24): coordinator(), decision(), DemoAdapterDouble, policy(), Replies in call order: the reconciliation first, then the order., SequencedTransport, test_adapter_store_audits_the_broker_outcome(), test_broker_error_reply_stops_both_switches_and_restart_keeps_them_stopped() (+16 more)

### Community 30 - "persist_tokens_env"
Cohesion: 0.12
Nodes (19): PathLike, cTrader does not always return a new refresh token. Dropping the stored one…, A crash mid-write must not destroy the other credentials. ``write_text``…, An ``export KEY=`` line must not survive alongside the rewritten key. Otherwise…, The last assignment is the one that loaded, so it is the one rewritten., The rewrite must hold a lock for the whole read-modify-write. Two independent…, Smoke test: concurrent writers never produce an unparseable env file., test_persist_tokens_appends_missing_key_and_sets_0600() (+11 more)

### Community 31 - "TournamentDataset"
Cohesion: 0.11
Nodes (15): setup_runner(), test_adaptive_generations_wait_for_completion_interval(), test_continuous_worker_records_idle_heartbeat(), test_failure_is_durable(), test_legacy_flat_parameters_are_reconstructed(), test_robust_validation_adds_walk_forward_and_bootstrap(), test_worker_completes_and_writes_artifacts_without_test_partition(), Path (+7 more)

### Community 32 - "ExperimentSpec"
Cohesion: 0.14
Nodes (22): E. Current 50,000-scenario architecture and benchmark, dotenv, psycopg, random, main(), test_catalog_is_deterministic_and_valid(), test_catalog_seeding_is_batched_and_duplicate_safe(), test_replenishment_scans_past_existing_prefix() (+14 more)

### Community 33 - "test_lab.py"
Cohesion: 0.12
Nodes (31): parametrize, qualified_candidate(), quote(), test_codex_contract_rejects_unknown_fields_and_overlarge_requests(), test_codex_environment_does_not_inherit_broker_credentials(), test_evidence_relations_are_checked_beyond_digest(), test_forward_coverage_rejects_short_observation_despite_fixed_deadline(), test_forward_coverage_uses_new_york_market_minutes_and_accepts_complete_week() (+23 more)

### Community 34 - "agent_advisor.py"
Cohesion: 0.15
Nodes (22): functools, test_experimental_account_is_separate_and_bounded(), test_experimental_tick_fills_once_and_refuses_stale_quotes(), test_retire_flat_frees_capacity_and_keeps_review(), test_retirement_does_not_hide_open_exposure(), test_retiring_uses_gates_and_archives_only_after_flat(), feed(), threading (+14 more)

### Community 35 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (23): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Part A - Structural extraction for code files, Part B - Semantic extraction (parallel subagents) (+15 more)

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
Cohesion: 0.12
Nodes (21): test_all_baseline_signals_are_aligned_and_bounded(), test_breakout_channel_excludes_current_bar(), test_features_do_not_change_when_future_bars_are_appended(), test_novel_signal_formulas_are_causal(), test_dynamic_parameters_change_signal(), test_quantitative_families_are_causal_and_generate_scenarios(), test_session_momentum_warmup_is_flat_not_an_integer_cast_error(), build_features() (+13 more)

### Community 40 - "Operator runbook: engine, live feed, and the visible harness"
Cohesion: 0.25
Nodes (7): 10. Related documents, 4. Enable the deterministic engine, 6. Resume the agent (only after the feed and engine are verified), 7. Verifying the whole loop, 8. Refusal and rollback, Engine control, Operator runbook: engine, live feed, and the visible harness

### Community 41 - "bits_jobs.py"
Cohesion: 0.14
Nodes (21): ast, contextlib, fcntl, ipaddress, re, selectors, signal, subprocess (+13 more)

### Community 42 - "._fetch"
Cohesion: 0.36
Nodes (15): account_ok(), account_or_discover(), app_ok(), auth_stop(), connected(), got_accounts(), got_page(), got_symbol() (+7 more)

### Community 43 - "AdaptiveSearch"
Cohesion: 0.16
Nodes (15): Adaptive-mutation outcome analytics — 2026-08-21, Clean lease-drained saturation benchmark — 2026-08-20, completed(), test_adaptive_analyze_updates_existing_report(), test_adaptive_generation_walks_past_duplicates(), test_adaptive_search_creates_bounded_lineage(), test_adaptive_search_preserves_family_exploration(), test_mutation_analytics_measures_improvement_and_duplicates() (+7 more)

### Community 49 - "test_retention.py"
Cohesion: 0.12
Nodes (39): test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(), archive(), _local_backups(), test_compaction_reads_compressed_raw_pages(), test_completed_logs_only_and_pins(), test_completed_workspace_reclaims_training_and_scripts_but_keeps_memory(), test_completed_workspace_with_nested_symlink_retained(), test_compress_existing_exact_target_and_deterministic_bytes() (+31 more)

### Community 50 - "test_demo_runner.py"
Cohesion: 0.11
Nodes (22): Adapter, DecisionSource, MarketSource, paper_only_runner(), Stateful demo lifecycle double: the kill switch persists like the real store., Pass an existing ``paper``/``adapter`` to simulate a process restart on…, runner(), status() (+14 more)

### Community 51 - "InMemoryAgentTranscriptStore"
Cohesion: 0.09
Nodes (15): The test double must mirror the SQL stores, or tests prove nothing., test_in_memory_reconcile_is_scoped_to_the_caller_family(), The 2026-10-05 loop reported only its symptom. 19 cycles re-fetched one…, `limit` alone does not bound a response. A shell-job step carries a captured…, The health endpoint is the observability surface; it must not raise. An…, The monitor's status string alone was never enough. A monitor that died after…, test_harness_endpoint_reports_engine_feed_and_cycle(), test_health_alerts_on_a_stale_or_dead_position_monitor() (+7 more)

### Community 52 - "test_automation.py"
Cohesion: 0.09
Nodes (29): _permissive_validation(), _pipeline_config(), An all-fail run must not promote `candidates[0]` anyway., A bare score with no provenance could be compared against anything., Ranking, validation and selection must use three disjoint partitions. The…, test_atomic_json_replaces_complete_document(), test_automated_attempt_records_failure(), test_champion_is_not_replaced_when_either_side_lacks_a_dataset_binding() (+21 more)

### Community 53 - "test_ctrader_reconciliation.py"
Cohesion: 0.21
Nodes (13): copy, parametrize, record(), snapshot(), test_filled_position_survives_adapter_restart(), send(), test_native_snapshot_preserves_positions_and_checks_account(), test_netting_partial_reduction_and_flattening() (+5 more)

### Community 54 - "Any"
Cohesion: 0.13
Nodes (12): Operating model, 1. What was built and why, CockroachPaperTradingStore, _corrupt_state(), _now(), transition(), transition(), Any (+4 more)

### Community 55 - "DemoAutomationRunner"
Cohesion: 0.13
Nodes (9): DemoAutomationRunner, DemoLifecycle, MarketDataSource, Any, Protocol, Reconcile first, then resume only the kill switches the restart policy allows.…, Apply the shared restart policy; return ``(switch, reason)`` when a stop must…, Read-only source for the latest executable market observation. (+1 more)

### Community 56 - "Operations"
Cohesion: 0.12
Nodes (13): Execution Boundary, Operations, 1. Current state (as recorded in the state store), 2. Side-effect audit (required before recovery), 3. Integrity pre-flight, 4. Recovery sequence, 5. Post-recovery verification, 6. Refusal and rollback (+5 more)

### Community 57 - "CTraderHistoricalAdapter"
Cohesion: 0.15
Nodes (9): Research notes (`bits-memory`, schema `xauusd.notes/1`), Interpreter guard for subcommands, stream(), events(), CTraderHistoricalAdapter, Path, The same wire page, whether plain or losslessly gzip-compressed., Import cTrader CSV exports into the normalized historical store. (+1 more)

### Community 58 - "ExecutionConfig"
Cohesion: 0.14
Nodes (28): main(), bars(), gapped_bars(), holding_signal(), no_costs(), A multi-day hold was modelled with zero carry. `max_holding_bars` reaches 240…, A no-loss strategy used to produce profit_factor inf. json.dumps(...,…, Zero is a real value; a metric that cannot be computed must say so. Reporting… (+20 more)

### Community 59 - "ContinuousAgentRunner"
Cohesion: 0.07
Nodes (19): Event, test_redact_bounds_untrusted_content(), AgentTranscriptStore, _assistant_step(), CockroachAgentTranscriptStore, ContinuousAgentRunner, Any, BaseException (+11 more)

### Community 60 - "Requirements: reliable research-to-paper-trade workflow"
Cohesion: 0.18
Nodes (10): Delivery and operational boundaries, Evidence anchors, Implemented baseline — memory writes and actionable errors (R1 remains), Implemented baseline — service environment discovery (R2 remains), Original incident evidence (pre-merge snapshot), P1 — Make research decisions and the path to a proposal explicit, P1 — Persist reproducible experiments and separate live signals, P1 — Separate monitoring cadence from meaningful agent reviews (+2 more)

### Community 61 - "CodexResearchClient"
Cohesion: 0.12
Nodes (16): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000) (+8 more)

### Community 62 - "BitsStore"
Cohesion: 0.14
Nodes (10): 5. Restart the live view so the new observability is visible, memory(), fixture, memory(), fixture, BitsStore, Uses the same connection selected for the application's transcript store., Read-modify-write several state keys atomically. SQLite connections run in… (+2 more)

### Community 63 - "test_oauth.py"
Cohesion: 0.17
Nodes (13): Market Data & Authentication, FakeResponse, response_json(), test_authorize_url_builds_documented_endpoint(), test_exchange_authorization_code_uses_code_and_redirect(), fake_urlopen(), test_http_failure_raises_oauth_error(), test_missing_access_token_raises() (+5 more)

### Community 64 - "ctrader_demo.py"
Cohesion: 0.09
Nodes (24): adapter(), test_broker_error_reply_is_recorded_as_a_rejection_not_a_fill(), test_broker_identity_collision_stops_before_submission(), test_duplicate_request_never_sends_a_second_transport_call(), test_long_decision_id_is_persisted_but_broker_id_fits(), test_reconcile_maps_persisted_broker_id_back_to_internal_id(), test_recovery_failure_kills_and_blocks_execution(), test_transport_failure_is_an_unknown_outcome_that_blocks_restart() (+16 more)

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
Nodes (16): error_details(), message_fingerprint(), BaseException, Payload-free classification of an exception for events and heartbeats.…, Stable digest of a message stream, used to persist each turn exactly once., BitsAgentRunner, Any, Retrieval-loop evidence for the heartbeat, which this file writes every tick. A… (+8 more)

### Community 73 - "test_session_calendar.py"
Cohesion: 0.16
Nodes (20): at(), parametrize, Session weeks follow New York time; completion is explicit, never inferred from…, Synthetic M1 bars stamped at bar open, only while the session gate is open., session_bars(), test_a_week_whose_data_stops_early_is_not_complete(), test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected(), test_pandas_weekly_labels_disagree_with_session_weeks() (+12 more)

### Community 74 - "Architecture and data-flow map"
Cohesion: 0.50
Nodes (3): Architecture and data-flow map, Component map, State and live UI

### Community 75 - "test_data.py"
Cohesion: 0.07
Nodes (47): errno, _bars(), minute_60(), _minute_bars(), one_bar_at(), The archive is the only rebuild path, so a plan must prove it loses no range.…, Three valid, non-overlapping minutes, shifted so writers never collide., `data update` starts from the newest bar, so a hole in the middle is permanent.… (+39 more)

### Community 77 - "oauth.py"
Cohesion: 0.16
Nodes (16): urllib_error, CTraderOAuthError, _env_key(), _env_lock(), guard(), _env_value(), exchange_authorization_code(), Path (+8 more)

### Community 78 - "BitsMemory"
Cohesion: 0.28
Nodes (4): BitsMemory, _note_sources(), _notes_base(), A specific next task for unresolved drafts; not a new research cycle.

### Community 79 - "canonical_json"
Cohesion: 0.15
Nodes (25): codes(), entry(), observed_wrapper_payload(), open_drafts(), Shape of job c5ea68176942459881c9409618ac2936: valid notes inside a single…, reply(), sample_notes(), test_history_size_and_excerpts_are_explicit() (+17 more)

### Community 80 - "CodexImprovementWorkflow"
Cohesion: 0.22
Nodes (9): repository(), test_codex_child_environment_uses_allowlist(), test_prepare_creates_detached_review_only_worktree(), test_prompt_has_explicit_safety_boundaries(), test_research_brief_is_redacted_and_aggregated(), CodexImprovementWorkflow, CodexWorkflowConfig, Path (+1 more)

### Community 81 - "test_engine_loop.py"
Cohesion: 0.06
Nodes (53): build(), Market hours are checked before freshness, as the agent does. On a weekend the…, Staleness is checked before a proposal exists, not after. The engine reads the…, Halting the engine is not a trading stop, and resuming is not a start., The engine is the trade path; a persistent failure must be loud., An oversized proposal must be visibly refused, not silently trimmed. Clamping…, The halt was the only thing between the engine and an unvalidated strategy. A…, Deterministic signal double: returns the same proposal until told otherwise. (+45 more)

### Community 82 - "test_bits_capabilities.py"
Cohesion: 0.11
Nodes (38): R2 — P1: capability discovery failure must remain visible, fake_tool(), parametrize, The shell-job environment is discoverable from the environment jobs really get., Matches service execution: bash -c, minimal PATH, no HOME profile, absolute CLI…, Recursive searches from the repository root overrun the 1200s shell ceiling.…, test_a_repaired_tool_clears_the_observed_missing_alert(), test_every_published_operation_is_a_real_cli_command() (+30 more)

### Community 83 - "AgentTools"
Cohesion: 0.10
Nodes (25): Store, test_dependency_install_requires_pins(), test_dependency_install_targets_scratch_only(), test_domain_configuration(), test_fetch_rejects_private_dns(), test_market_observe_excludes_frozen_and_forming_bars(), test_market_observe_without_frozen_boundary_reveals_no_history(), test_process_timeout_and_output_bound() (+17 more)

### Community 86 - "lab_api.py"
Cohesion: 0.13
Nodes (12): test_daily_snapshot_hides_yesterday_progress_and_jobs(), test_utc_daily_roll_preserves_memory_account_and_validation_budget(), test_read_only_lab_api_reports_actual_data_and_events(), UTC goal/display boundaries, independent of account and risk state., roll_daily_goal(), utc_day(), _age(), events() (+4 more)

### Community 87 - "main"
Cohesion: 0.09
Nodes (34): DemoTransport, _isolated_bits_state(), Each attempt is a separate process, so the retry is driven by a runner. In-…, Without this the command exists but nothing runs it, so a hole still sits for…, _run_cli(), stopped_demo_adapter(), test_bits_capabilities_check_and_stored_manifest(), test_bits_capabilities_direct_discovery_exception_still_exits_nonzero() (+26 more)

### Community 88 - "NotesRejected"
Cohesion: 0.13
Nodes (19): rejection(), apply(), apply(), _check_draft_ids(), issue(), NotesRejected, _now(), parse_notes_input() (+11 more)

### Community 89 - "AgentAdvisor"
Cohesion: 0.10
Nodes (21): Harness maintenance — 2026-10-24, test_advisor_contract_rejects_extra_actions_and_nonobject_arguments(), test_advisor_executes_tools_then_feeds_actual_results_and_persists_agenda(), run_turn(), test_compact_context_preserves_account_controls_and_retrievable_evidence(), test_final_structured_turn_is_not_repeated_as_public_commentary(), test_new_session_does_not_reinstate_archived_brief_memory(), run_turn() (+13 more)

### Community 90 - "PaperTradingEngine"
Cohesion: 0.09
Nodes (18): EngineDecision, EngineStore, MarketSource, PaperTradingEngine, Any, Protocol, One bar's outcome, as recorded for the live view., Evaluate a deterministic strategy on the feed and pass it through the gates. (+10 more)

### Community 92 - "cli.py"
Cohesion: 0.06
Nodes (48): test_volume_policy_from_metadata(), typing, agent_transcript_store_from_env(), Transcript store for the configured backend (local SQLite by default)., Validate the small, explicit JSON-schema subset used for tool boundaries., _validate_json(), Deterministic local-data sources for the demo automation canary., agent_controller() (+40 more)

### Community 93 - "LiveBarFeed"
Cohesion: 0.12
Nodes (37): config(), credentials(), FakeClient, FakeStore, Losing the log must never cost the data it describes., A cTrader client double: answers each request synchronously., A default that points into reports/ is a production file waiting to be test…, The status file holds only the latest state, and these services write no… (+29 more)

### Community 94 - "LabStore"
Cohesion: 0.18
Nodes (7): test_snapshot_expiry_deletes_backend_rows(), LabStore, save(), add(), add(), save(), Expire old price-mark results, never actual trade idempotency keys. Monitor…

### Community 95 - "PostgresConnection"
Cohesion: 0.23
Nodes (3): test_postgres_connection_uses_configured_read_committed(), PostgresConnection, CockroachSourceStore

### Community 96 - "data_heal"
Cohesion: 0.20
Nodes (14): _heal_args(), no_broker(), The 2026-10-12 feed restart lost 17 minutes no tail-only update could reach., Deferred, not dropped: a bounded timer job must still report what it skipped., An open minute in which nothing quoted has no bar, so it can never be filled.…, _store_with_windows(), test_data_heal_defers_a_window_that_does_not_fit_the_budget(), test_data_heal_downloads_an_interior_window() (+6 more)

### Community 97 - "bits_runner.py"
Cohesion: 0.11
Nodes (29): A cycle runs several steps; the window counts cycles, not commands., The evidence has to reach the model, not just the store., Observation has to be conservative, or the evidence is noise. A token counts…, 19 cycles re-read one 7,271-byte file and nothing could say which file.…, Store, test_command_paths_keeps_only_existing_scoped_files(), test_context_publishes_repeated_paths_with_an_instruction(), test_market_windows_use_observed_data_and_handle_missing_source() (+21 more)

### Community 98 - "._note"
Cohesion: 0.08
Nodes (21): 3. Enable the live data feed, test_a_closed_bar_is_the_only_bar_that_may_be_persisted(), test_an_inconsistent_decoded_bar_is_refused(), _bar_is_usable(), closed_bar(), heartbeat(), on_disconnected(), on_message() (+13 more)

### Community 99 - "SQLiteAgentTranscriptStore"
Cohesion: 0.07
Nodes (35): Row, The deterministic engine writes to the same `agent_runs` table. Taking the…, test_status_and_health_select_the_agent_run_not_a_newer_engine_run(), decision(), parametrize, Validation must not reject a real account, including a running one., The agent and the engine share one `agent_runs` table. An engine start ran an…, Nothing is provably an orphan when the caller does not say who it is. (+27 more)

### Community 100 - "LiveFeedConfig"
Cohesion: 0.11
Nodes (18): test_feed_config_rejects_a_nonsense_port_or_empty_symbol(), test_feed_refuses_any_host_but_the_pinned_demo_host(), test_session_phase_reports_the_new_york_break_and_the_weekend(), _feed_health(), Whatever the live feed last recorded, or that it has never run. Never raises:…, data_feed_controller(), Live M1 bar feed. Separate process on purpose: Twisted's reactor is global and…, _heartbeat_phase() (+10 more)

### Community 101 - "test_bits_memory_drafts.py"
Cohesion: 0.15
Nodes (25): skipif, notes(), open_drafts(), PostgresLikeTranscript, R1: rejected memory writes keep durable draft identities until explicitly…, Opt-in: exercises the Cockroach/Postgres path. Never point it at a live store:…, reject(), test_concurrent_writers_with_the_same_base_cannot_both_win() (+17 more)

### Community 102 - ".run"
Cohesion: 0.21
Nodes (10): _cagr(), close(), commission(), fill_price(), _profit_factor(), DataFrame, Series, Gross profit over gross loss, or ``None`` when it is undefined. ``None`` covers… (+2 more)

### Community 103 - "lab_strategy.py"
Cohesion: 0.17
Nodes (24): operator, bars(), parametrize, test_expression_is_causal_and_bounded(), test_expression_rejects_future_and_unbounded_code(), test_frozen_partition_and_embargo_never_exposes_holdout(), test_nonfinite_signal_fails_closed(), test_validation_never_promotes_empty_or_forged_candidate() (+16 more)

### Community 104 - "test_ctrader_lifecycle.py"
Cohesion: 0.20
Nodes (10): Client, event(), parametrize, Broker-free lifecycle sequences: the first correlated response is not…, Reactor, setup(), test_acceptance_then_partial_then_fill(), test_incomplete_or_invalid_execution_stays_pending() (+2 more)

### Community 105 - "test_weekly_report.py"
Cohesion: 0.33
Nodes (10): row(), test_gate_analytics_counts_failures_near_passes_and_coverage(), test_gate_analytics_handles_development_and_missing_gate_evidence(), test_loss_source_classification_requires_direct_cost_evidence(), test_parameter_stability_compares_only_matching_numeric_neighbors(), test_selection_bias_computes_bh_and_aligned_fold_pbo(), test_selection_bias_reports_score_distribution_and_missing_controls(), classify_loss_source() (+2 more)

### Community 106 - "Any"
Cohesion: 0.15
Nodes (5): HarnessStore, Any, Protocol, RuntimeError, ToolExecutionError

### Community 107 - "HistoricalDataStore"
Cohesion: 0.11
Nodes (25): pyarrow_parquet, A store whose newest bar is fresh and which contains a real, cost-aware edge. A…, _seed_store(), An interior hole is a smaller problem than a refresh reported as failed. The…, test_update_reports_a_failed_heal_without_failing_the_update(), frame(), test_positions_matches_get_indexer(), test_positions_requires_a_sorted_unique_index() (+17 more)

### Community 108 - "atomic_write_json"
Cohesion: 0.21
Nodes (11): _dependency_only(), _eligible(), EngineeringManager, _hash(), _protected(), Path, Fail closed on interrupted installs; leave installed releases to worker., _safe() (+3 more)

### Community 109 - "Local audit — 2026-09-24"
Cohesion: 0.14
Nodes (12): Broker order IDs — follow-up #14, cTrader SDK and protocol review (no broker connection), Demo-only host boundary, Follow-up implementation (supersedes the original blocker list), Local audit — 2026-09-24, Local validation and deployment, Operator-authorized paper resumption — 2026-09-24, Operator-requested fresh session — 2026-09-24 07:05 UTC (+4 more)

### Community 110 - "atomic_write_text"
Cohesion: 0.11
Nodes (23): fixture, parametrize, setup(), Store, test_added_conftest_cannot_skip_original_tests(), test_changed_files_rechecked_before_health_success(), test_dependencies_may_change_but_build_configuration_cannot(), test_failed_tests_never_install() (+15 more)

### Community 111 - "BitsError"
Cohesion: 0.08
Nodes (44): 2. Publish the Datadog workflow message stream (required for the thinking panel), main(), call(), Two-invocation, no-trading smoke test of Bits -> shell -> Bits. Run from the…, envelope(), interrogation(), parametrize, boom() (+36 more)

### Community 112 - "_registry_schema_valid"
Cohesion: 0.21
Nodes (12): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal, test_registry_validation_streams_rows_and_rejects_non_array_tables(), Validate logical snapshot JSON in bounded memory (8 MiB per row). Snapshots…, _registry_schema_valid() (+4 more)

### Community 113 - "._discover_account"
Cohesion: 0.21
Nodes (11): app_failed(), account_ok(), fail(), got_accounts(), got_symbols(), transport_failed(), use_account(), The broker client, created once. Injected through ``client_factory`` so the… (+3 more)

### Community 114 - "lab_tools.py"
Cohesion: 0.19
Nodes (22): generated(), test_child_environment_does_not_pass_credentials(), test_corrupt_or_traversal_library_never_seeds(), test_failed_tests_never_publish(), test_file_count_and_library_symlink_refuse(), test_library_cap_and_corrupt_objects_never_seed(), test_passed_tools_are_immutable_and_reused(), test_symlinks_and_size_limit_refuse_execution() (+14 more)

### Community 115 - "lab_sources.py"
Cohesion: 0.13
Nodes (12): html, html_parser, HTMLParser, test_content_region_and_fallback(), test_explicit_main_excludes_long_navigation_and_active_content(), urllib_parse, urllib_request, xauusd (+4 more)

### Community 117 - "test_session_reset.py"
Cohesion: 0.32
Nodes (8): seeded(), test_reset_clears_session_atomically_and_keeps_verified_backup(), test_reset_refuses_active_agent_and_unstopped_paper(), AgentAlreadyRunning, AgentLock, Single process per container; the lock is runtime coordination, not state., Explicit operator reset of a stopped local paper session, after backup., reset_paper_session()

### Community 118 - "write_status"
Cohesion: 0.22
Nodes (15): test_bits_alerts_name_missing_executables(), test_bits_alerts_name_repeated_memory_failures(), test_bits_alerts_name_unresolved_memory_drafts(), test_read_status_missing_or_corrupt_returns_none(), test_write_status_is_atomic_and_readable(), test_write_status_overwrites_and_records_timestamp(), agent_status_path(), bits_alerts() (+7 more)

### Community 119 - "read_quote"
Cohesion: 0.18
Nodes (17): ctrader_open_api_messages_openapimessages_pb2, sqlite3, parametrize, test_corrupt_quote_is_unavailable_not_trusted(), test_feed_matches_account_and_symbol_before_recording(), test_invalid_quotes_do_not_persist(), test_optional_proto_presence_never_combines_sides(), test_real_protobuf_two_sided_prices_and_source_time() (+9 more)

### Community 120 - "portfolio_research.py"
Cohesion: 0.19
Nodes (19): test_effective_bets_detect_perfect_correlation(), test_equity_metrics_measure_portfolio_drawdown(), test_leave_one_out_and_no_trade_metrics(), test_portfolio_run_reads_validation_only(), test_portfolio_uses_weighted_returns_and_alignment(), test_regime_labels_are_causal_and_complete(), test_weights_are_long_only_normalized_and_causal(), aligned_returns() (+11 more)

### Community 121 - ".send"
Cohesion: 0.25
Nodes (5): account_list(), envelope(), FakeDeferred, Wrap a real response proto the way the SDK hands it to a callback., symbol_list()

### Community 122 - "pytest"
Cohesion: 0.16
Nodes (17): pytest, The durable-write primitives every writer in this repository shares., Two holders must never be inside the section at once. `flock` is per open file…, A wedged writer has to fail loudly, not hang a trading loop., test_atomic_write_replaces_the_target_and_leaves_no_temporary(), test_file_lock_creates_a_missing_parent_directory(), test_file_lock_is_exclusive_between_holders(), worker() (+9 more)

### Community 123 - "test_lab_dashboard.py"
Cohesion: 0.12
Nodes (10): fastapi_testclient, client(), test_query_bounds_and_timeframes(), test_read_only_routes_and_snapshot(), test_statistics_counts_retained_evidence_without_claiming_success(), attach_routes(), lab_chart(), lab_events() (+2 more)

### Community 124 - "weekly_report.py"
Cohesion: 0.22
Nodes (8): Gate-failure and near-pass analytics — 2026-08-21, itertools, statistics, test_weekly_report_tracks_throughput_families_and_multiple_testing(), _flatten_parameters(), parameter_stability_analytics(), _quantile(), WeeklyTournamentReport

### Community 125 - "evidence_refs"
Cohesion: 0.60
Nodes (5): evidence_refs(), add(), ordered(), walk(), Evidence references named by a (possibly malformed) payload: bounded, safe,…

### Community 126 - "README.md"
Cohesion: 0.14
Nodes (8): Bits agent instructions, Autonomous Agent, Legacy Datadog planner operations, Bits shell environment (`bits-capabilities`), Delivery Stages, Historical delivery and deployment notes, Operator pause for overhaul — 2026-09-24, Research continuity and output retrieval

### Community 127 - "Aurum — Codex Autonomous Trading Lab"
Cohesion: 0.11
Nodes (19): Active Codex agent, Architecture, Aurum — Codex Autonomous Trading Lab, Codex efficiency — 2026-10-23, Configuration, Current Status, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23 (+11 more)

### Community 131 - "Repository Operating Rules"
Cohesion: 0.15
Nodes (13): Autonomous Harness, Codex deployment — verified 2026-10-21, Codex efficiency — 2026-10-23, Dashboard navigation — 2026-10-23, Dashboard statistics — 2026-10-23, Datadog Bits operations, graphify, Local agent handoff — completed 2026-09-24 (+5 more)

### Community 132 - "PaperDecision"
Cohesion: 0.29
Nodes (6): test_paper_endpoint_reflects_accepted_fill(), Any, Evaluate paper risk first; broker submission only happens behind all gates., Broker-free validation of the paper pipeline; no adapter, volume, or kill-…, Use the adapter's persistent audit store when the concrete adapter exposes it., PaperDecision

### Community 133 - "run"
Cohesion: 0.29
Nodes (4): test_failed_worker_schedule_rolls_back_without_retry(), test_worker_requires_new_healthy_heartbeat_before_acceptance(), release_healthy(), run()

### Community 134 - "Persistent open-ended Codex agent"
Cohesion: 0.18
Nodes (10): Dashboard and controls, Decision loop, Engineering releases, Evidence-driven lifecycle — 2026-10-23, Persistent Codex and experimental paper accounts (2026-10-22), Persistent open-ended Codex agent, Purpose and authority, Research continuity and maintenance — 2026-10-24 (+2 more)

### Community 135 - "fetch_source"
Cohesion: 0.18
Nodes (3): test_fetch_keeps_raw_digest_and_bounds(), NoRedirect, fetch_source()

### Community 136 - "test_offline.py"
Cohesion: 0.21
Nodes (13): test_offline_transitions_are_aligned_and_terminal(), test_sequence_windows_never_include_future_rows(), test_torch_adapter_explains_missing_extra(), build_offline_transitions(), build_sequence_dataset(), OfflineTransitions, DataFrame, Series (+5 more)

### Community 137 - "Codex autonomous trading lab"
Cohesion: 0.22
Nodes (9): Codex autonomous trading lab, Codex efficiency — 2026-10-23, Commands, Configuration, Dashboard navigation — 2026-10-23, Research activity chat — 2026-10-23, Research and automatic deployment, Storage and retention (+1 more)

### Community 138 - "Datadog Bits connection"
Cohesion: 0.29
Nodes (7): Configuration, Datadog Bits connection, Deployment validation — 2026-09-23, History and readable activity, Research continuity and output retrieval, Runtime and recovery, Verified transport and remaining integration

### Community 139 - "Harness cleanup and improvement checklist — 2026-10-24"
Cohesion: 0.40
Nodes (4): Audit findings, Broker smoke shutdown follow-up, Harness cleanup and improvement checklist — 2026-10-24, Verification and deployment log

### Community 141 - "Merge review — 2026-09-25, baseline `cba22b2`"
Cohesion: 0.40
Nodes (5): Delivery order after this merge, Merge review — 2026-09-25, baseline `cba22b2`, R1 — P0: do not lose pending findings when memory is rewritten, R3 — P1: make experiment continuity work with the deployed backend, Runtime adoption is still pending

### Community 142 - "._subscribe"
Cohesion: 0.31
Nodes (8): on_connected(), tick(), confirmed(), guard(), send_spots(), send_trendbars(), Subscribe to live M1 trendbars for the discovered account and symbol. Runs…, Re-subscribe on a cadence so a silently dropped stream recovers.…

### Community 143 - "test_lab_retention.py"
Cohesion: 0.60
Nodes (5): store_at(), test_candidate_bound_preserves_qualified_and_compact_history_is_bounded(), test_dataset_retention_keeps_twelve_current_and_protected_refs(), test_malformed_dataset_refs_and_pins_keep_archives(), test_shadow_retention_keeps_live_state_and_compacts_final_metrics()

### Community 145 - "engine_decision_id"
Cohesion: 0.50
Nodes (4): A restart re-proposes the same decision for the same bar, and the store's…, test_engine_decision_id_is_derived_from_the_bar(), engine_decision_id(), Durable identity for one engine decision. Derived from the bar, not from a…

### Community 146 - "_run_family"
Cohesion: 0.50
Nodes (3): Family-scoped mirror of the SQL stores: never close another family's run., The run family a run_id belongs to: ``agent_`` or ``engine_``. The agent and…, _run_family()

### Community 147 - "StateTransaction"
Cohesion: 0.25
Nodes (3): Serialize read-modify-write transactions that name the same key. SQLite's BEGIN…, bits_state access bound to one open connection/transaction., StateTransaction

### Community 150 - "lab.py"
Cohesion: 0.16
Nodes (13): schedule_verification(), quote_valid(), One shared, cost-aware target execution path for prospective and paper runs., A prospective simulation account; never selects or replaces real state., ShadowStore, target_decision(), _open_minutes(), paper_tick() (+5 more)

### Community 151 - "index"
Cohesion: 0.67
Nodes (3): frame(), read(), index()

### Community 153 - "setup"
Cohesion: 0.15
Nodes (19): test_account_only_reset_preserves_research_and_stop(), test_improvement_cannot_claim_old_release_as_new_work(), test_inspection_and_failed_remote_work_are_not_progress(), test_outcome_requires_existing_successful_evidence_and_deduplicates(), setup(), test_counter_update_rolls_back_with_owning_state_transaction(), test_counters_survive_detail_eviction_and_ignore_duplicate_updates(), test_durable_job_recovery_never_replays() (+11 more)

### Community 156 - "trendbars_to_frame"
Cohesion: 0.09
Nodes (17): Historical deployment state — verified 2026-10-05, 9. Recovering the market-data store, OSError, test_trendbar_delta_decoding(), Any, DataFrame, Contiguous runs of market-open minutes the store does not have. `validate`…, Replace the store with `bars`, merged into whatever is already there. One… (+9 more)

### Community 158 - "paper_trading.py"
Cohesion: 0.10
Nodes (28): FastAPI, fastapi_responses, inspect, create_app(), data_update_status(), harness(), health(), job_output() (+20 more)

### Community 159 - "_datetime"
Cohesion: 0.17
Nodes (21): Engineering, canary_signal_tool(), handler(), _decision_id(), _mock_market_for_read(), paper_state_tool(), _positive_float(), handler() (+13 more)

## Knowledge Gaps
- **175 isolated node(s):** `$schema`, `plugin`, `xauusd-research`, `research-cron.sh script`, `start.sh script` (+170 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1140 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LiveBarFeed` connect `LiveBarFeed` to `._note`, `LiveFeedConfig`, `HistoricalDataStore`, `json`, `._subscribe`, `._discover_account`, `read_quote`, `CTraderAuthError`, `.stop`, `cli.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `PaperTrading` connect `PaperTrading` to `test_bits_runner.py`, `PaperDecision`, `test_agent_loop.py`, `test_agent_view.py`, `lab.py`, `setup`, `state_backup.py`, `test_demo_execution.py`, `paper_trading.py`, `_datetime`, `test_lab.py`, `agent_advisor.py`, `test_demo_runner.py`, `InMemoryAgentTranscriptStore`, `Any`, `Operations`, `ContinuousAgentRunner`, `test_engine_loop.py`, `main`, `PaperTradingEngine`, `cli.py`, `data_heal`, `SQLiteAgentTranscriptStore`, `test_session_reset.py`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `SQLiteAgentTranscriptStore` connect `SQLiteAgentTranscriptStore` to `test_bits_runner.py`, `PaperTrading`, `test_lab_retention.py`, `SQLitePaperTradingStore`, `test_agent_view.py`, `SecretFilter`, `setup`, `state_backup.py`, `_datetime`, `test_lab.py`, `Operations`, `BitsStore`, `canonical_json`, `test_bits_capabilities.py`, `main`, `cli.py`, `LabStore`, `test_bits_memory_drafts.py`, `atomic_write_text`, `BitsError`, `test_session_reset.py`, `test_lab_dashboard.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `PaperTrading` (e.g. with `paper_trading()` and `test_sqlite_paper_store_rejects_mistyped_fields()`) actually correct?**
  _`PaperTrading` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MemoryRegistry` (e.g. with `test_dashboard_reads_latest_run_and_equity()` and `test_health_is_public_but_api_can_require_auth()`) actually correct?**
  _`MemoryRegistry` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `HistoricalDataStore` (e.g. with `AgentTools` and `DailyResearchPipeline`) actually correct?**
  _`HistoricalDataStore` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `ExperimentRegistry` (e.g. with `R3 — P1: make experiment continuity work with the deployed backend` and `AdaptiveSearch`) actually correct?**
  _`ExperimentRegistry` has 12 INFERRED edges - model-reasoned connections that need verification._