# Historical delivery and deployment notes

Archived from the README on 2026-10-24. These entries describe earlier versions; current services, state and active runbooks are authoritative.

## Delivery Stages

1. Autonomous planning harness with persistent runs, tool controls, and audit records.
2. Firecrawl source ingestion with provenance and prompt-injection isolation.
3. Deterministic paper trading, risk gates, notifications, and restart recovery.
4. cTrader demo-only adapter, persistent idempotency, and sandbox integration tests.
5. Limited demo canary followed by continuous demo operation only after all gates pass.

See `AGENTS.md` for repository operating rules and `docs/ARCHITECTURE.md` for the existing research platform.


### Research continuity and output retrieval

Bits receives repository rules once per revision (delivery is acknowledged by a
successful correlated response), persistent research guidance, and descriptive
15/60/240-bar close summaries with actual window timestamps. These observations
are not trade signals or evidence of profitability. The agent should run concrete
cost-aware experiments and save source-linked notes before waiting on measurable
conditions. Arbitrary shell access and deterministic trading gates are unchanged.

Weekly research aggregates M1 bars with `xauusd.session_calendar.weekly_bars`,
which uses New York session weeks (Sunday 18:00 to Friday 17:00, so UTC
boundaries move with daylight time) and marks each week `complete`,
`in_progress`, `incomplete_data` or `partial_start`. It refuses bars after the
information cutoff. A pandas weekly label does not prove a week completed, and
holidays are not modelled, so early closes appear as incomplete weeks.

Stored-output pages are unwrapped before prompt compression, retaining the original
job ID and correct next offset. Follow that cursor instead of paging retrieval jobs.
The health dashboard flags three completed cycles without changed research notes.
This is a transparent progress proxy: no trade or unchanged notes alone does not
prove analytical failure. Updating only a note timestamp does not clear the count.

Use `bits-memory show --notes-only` to retrieve research notes without duplicating conversation history.

### Research notes (`bits-memory`, schema `xauusd.notes/1`)

There is no standalone `bits-memory` executable; always run it through the CLI:

```bash
.venv/bin/python -m xauusd.cli bits-memory schema             # published schema, limits, source rules
.venv/bin/python -m xauusd.cli bits-memory validate --input-file - <<'JSON'   # check only; no state is read or written
{"notes": {"findings": [], "hypotheses": [], "rejected_approaches": [], "open_questions": [], "next_steps": []}}
JSON
.venv/bin/python -m xauusd.cli bits-memory write --input-file notes.json      # or --input JSON
.venv/bin/python -m xauusd.cli bits-memory show --notes-only   # readback, with version and digest
.venv/bin/python -m xauusd.cli bits-memory pending [--draft ID] # rejected writes kept as drafts
.venv/bin/python -m xauusd.cli bits-memory write --resolves ID --base-version 3 --input-file notes.json
.venv/bin/python -m xauusd.cli bits-memory supersede --draft ID --reason 'replaced by a later reproduction'
```

Accepted inputs are the canonical object with exactly the five categories, the
versioned wrapper `{"schema":"xauusd.notes/1","notes":{...}}`, and the observed
`{"notes":{...}}` wrapper as a compatibility form. Mixed shapes, extra fields and
unknown schema versions are rejected. Each category holds at most 12
`{"text","sources"}` entries, and the canonical JSON is at most 4,000 characters;
nothing is truncated. A successful write returns `version` and a `sha256` digest
(identical content keeps its version). A rejection exits 2 and prints
`status: rejected` with a stable `code`, JSON `path`, `expected` shape, sizes and
`retryable`/`retry` guidance, never the payload or exception text; operational
failures exit 1 with a classified code. The stored notes stay unchanged.

A rejected write that supplied a payload becomes a pending draft (`xauusd.drafts/1`)
with a durable ID (`draft_` plus 12 hex characters), the base notes version and
digest, the latest error, the payload when it is safe and at most 12,000
characters, and its evidence references (anything under `sources`, up to 40).
Retrying the identical payload or naming the draft updates it; a replaced payload
keeps earlier unresolved references. Only `write --resolves ID` (in the same
transaction as the notes) or `supersede --draft ID --reason TEXT` closes a draft;
unrelated or unchanged writes never clear one, and the result lists drafts that
remain open. `--base-version` makes a write fail with `stale_base` when the notes
changed in between; resolving a draft whose base is older than the stored notes
requires it, so a resolution cannot overwrite notes saved meanwhile. At most five
drafts stay open: opening a sixth closes the oldest as `evicted_overflow`,
keeping its ID, last error and references but not its payload. The newest 20
closed records are kept. Sensitive payloads, references and reasons are never
retained. Drafts rejected twice, skipped by a later write, based on older notes,
unresolved for 30 minutes or migrated from the previous single pending record
give Bits a `repair_task` and raise a `memory drafts need repair` health alert;
none of this stops trading. Writes lock a sentinel row with `FOR UPDATE` on the
Postgres/Cockroach path and use `BEGIN IMMEDIATE` on SQLite; the Postgres path is
contract-tested offline, and `XAUUSD_TEST_DATABASE_URL` enables an opt-in test
against a disposable database. Tick errors record a classified `error_code`, a
safe summary and the cycle phase rather than only an exception class name.

### Bits shell environment (`bits-capabilities`)

Shell jobs run `/bin/bash -c` without a login profile, so interactive `PATH`
additions (pipx, cargo, rc files) do not apply. The harness builds one explicit
job environment: the service virtualenv's `bin` first (so `python` is the service
interpreter), then absolute directories declared in `BITS_SHELL_EXTRA_PATH`, then
the inherited service `PATH`. The capability manifest is computed from the same
function:

```bash
.venv/bin/python -m xauusd.cli bits-capabilities            # what a job started by this process would see
.venv/bin/python -m xauusd.cli bits-capabilities --stored   # the manifest recorded by the running agent
```

The manifest (`xauusd.capabilities/1`) lists the working directory, the absolute
interpreter and CLI prefix, the resulting `PATH`, availability, path and version
of `graphify`, `rg`, `git` and `grep` with documented fallbacks, supported CLI
operations as complete commands, and the M1 data entry point. It also publishes the
two measured bounds that keep a shell job inside the 1200-second ceiling:
`data.window_lookup` (resolve a batch of bar timestamps in one pass) and
`data.repository_search` (scope every recursive search to the directory that can
hold the target; never walk `data/`, `graphify-out/cache`, `backups/`, `build/`,
`.venv/` or `.git/` from the repository root). It includes no
environment variable values other than `PATH`. The agent refreshes it at start-up,
every 15 minutes, and when a job reports `command not found`. Observed missing
executables persist across cycles and restarts, appear in `context.capabilities`,
and raise a health alert until they resolve. An optional tool that is simply
absent is reported with its fallback, not alerted.

Every manifest states its discovery `status`: `ok`, `partial` (named sections
such as `cli_commands` or `data` failed, each with a safe `error_code`) or
`failed` (the whole probe raised; the agent stores a fallback manifest and keeps
researching and monitoring). Tools are `available`, `missing` or `unknown`;
unprobed tools are never implied healthy, and `version_state` distinguishes
`probed`, `probe_failed` and `not_probed`. Invalid `BITS_SHELL_EXTRA_PATH`
entries are reported as `configuration_errors`, separately from missing tools.
The same status, error codes and unknown tools appear in `context.capabilities`,
the heartbeat and `/api/health` alerts. The agent re-probes at least every 15
minutes while it runs. Output includes a `check` verdict: `--check` exits 1
unless the status is `ok`, no required executable is missing and no declared
configuration is invalid; with `--stored` the recorded manifest must also be at
most 45 minutes old (probe time and age are shown). A discovery exception exits 1.
None of these conditions stops trading.

Deployment validation is an operator step and restarts nothing. Run the check
under the unit's working directory and environment file, because an interactive
shell is not the service environment:

```bash
sudo systemd-run --pipe --wait --quiet -p WorkingDirectory=/root/xauusd \
  -p EnvironmentFile=/root/xauusd/.env \
  /root/xauusd/.venv/bin/python -m xauusd.cli bits-capabilities --check
```

`--check` exits 1 when a required executable (`/bin/bash` or the interpreter) is
missing. Declare extra tool directories with `BITS_SHELL_EXTRA_PATH` in `.env`;
the systemd unit files are unchanged.

Bits shell jobs use a server-enforced 1200-second (20-minute) execution timeout.
The tool-call audit and stored job request record the effective timeout. This is
separate from the Datadog workflow HTTP timeout. Existing recovery-stop behaviour
is unchanged; changing this limit does not clear a persistent stop.

### Operator pause for overhaul — 2026-09-24

The operator paused this deployment for work with another harness. Paper is
persistently stopped (`operator`); the agent, live view, data-update timer and
state-backup timer are stopped and disabled. No XAUUSD cron entries were found.
Credentials, datasets, existing backups and the unresolved timed-out job are
preserved. Resumption requires explicit operator action and reconciliation of
that job; changing the shell timeout does not replay it.

The [2026-09-24 handoff audit](local-handoff-audit-2026-09-24.md) records local validation and the subsequent broker fixes (#14–#16). Full-fill confirmation and position reconciliation are tested offline. Uncertain orders without terminal history remain blocked; no automatic replay is allowed. The operator authorized resuming the existing Datadog paper deployment on 2026-09-24; cTrader order execution remains disabled by paper-only mode.
