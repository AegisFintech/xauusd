# Database maintenance and seven-day log rotation

Authoritative state remains on the configured backend. This deployment uses local
SQLite at STATE_DB_PATH. Market Parquet, native Codex session files, credentials,
quotes and recovery archives are outside this rotation policy.

## Scheduled behavior

xauusd-db-maintenance.timer runs hourly with a short randomized delay and a missed
run catch-up. The oneshot service executes `.venv/bin/python -m
xauusd.database_retention`, writes no console log, and persists a safe status at
reports/db_retention_status.json. Storage shows this status and the last full
compaction; failures are health alerts, never silent account restart/recovery.

Expire operational entries older than seven days UTC, with existing shorter caps
still in force: transcript bodies (including old bodies within long-running runs),
completed run metadata without retained transcript, Lab activity events, completed
job/tool logs, equity display marks, inference samples and monitor-only decisions.
Preserve monotonic event IDs, current working context and cumulative metrics.

Learning/lessons, sources/insights, experiment plans, candidate/qualification
records, findings, improvement measurements, account/stop state, real trade
idempotency, unresolved/running jobs and evidence referenced by durable state do
not expire here. Existing purpose-specific bounded retention remains authoritative.
Explicit transcript/step references are preserved; malformed durable state aborts
rotation rather than deleting evidence it cannot understand.

Terminal legacy shell outputs expire only when their age is known and no learning
or working-state reference pins them. Keep request/job/action identity, outcome,
exit code and output digest; mark output_expired and leave stdout/stderr empty.
A replay returns the existing record, never re-executes it. Older jobs lacking any
timestamp get retention_observed_at on their first scan and a full seven-day grace
period. New claims/completions record timestamps. Unknown jobs never rotate, and
legacy row-count pruning now excludes unknown rows.

Scans and deletions use up to 500 ordinary rows or 50 output-bearing jobs per batch with bounded work per invocation. A durable
job scan cursor prevents starvation when the table grows. Indexes support age
queries. SQLite optimize, passive checkpoint and incremental vacuum are safe
online; a busy checkpoint can leave reusable WAL capacity until a later run.

## One-time physical compaction

Deleting records frees reusable SQLite pages without necessarily shrinking its
file. Full compaction is operator maintenance, not a scheduled trading action:

1. Check no automatic engineering install or server tool side effect is pending.
2. Record paper controls and learning digests; stop xauusd-agent, xauusd-engine and
   xauusd-agent-view services. Keep feed/data acquisition independent.
3. Run `.venv/bin/python -m xauusd.database_retention --compact`.
4. Require quick_check=ok before/after. The operation converts the local file to
   incremental auto-vacuum, compacts it and checkpoints WAL. It refuses if any of
   the three known database services are active and does not change account state.
5. Restart the same services, verify unchanged stops/exposure/session/engine halt,
   compare protected learning digests, and check health and read-only Storage.

Never use state reset/restore, paper start or engine resume for maintenance. Full
VACUUM can need temporary disk space and a write lock; do not run it on an active
trading database. The hourly unit never passes --compact.

## Initial deployment

The audit found about 64 MB allocated, with roughly 45 MB already free inside the
file, 874 legacy shell jobs and about 29,500 monitor marks. Actual measurements and
post-compaction checks are recorded below after deployment. Learning is preserved;
there is no requirement to archive expired raw logs and grow disk usage elsewhere.

Initial optimization reclaimed **43,671,552 bytes**: primary file 63,700,992 ->
20,029,440 bytes. quick_check passed before/after. Hash comparison verified exact
preservation of learning namespaces, job identity/request/outcome, unknown actions,
full paper state and persistent session. Six old run summaries expired; 866 undated
unreferenced legacy jobs began their seven-day grace period. No raw output of unknown
age was falsely claimed old. Primary database services were restarted afterward.

Verification: complete suite **921 passed, 1 skipped**; installed focused checks
passed. The hourly timer is enabled/active and its oneshot ran successfully online.
Read-only Storage reports retention_days=7 and the compaction result. All installed
unit copies match deploy/systemd. Account/session continuity and the persistent
engine halt were verified after restart. The running database can grow normally
between maintenance runs; reusable/free pages are managed incrementally.
