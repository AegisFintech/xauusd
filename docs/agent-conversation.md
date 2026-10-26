# Codex permissions and conversation visibility

The operator authorized full-access advisor execution on 2026-10-26. The active
launcher uses `codex exec --yolo`, retaining the configured persistent thread,
`gpt-6-luna`, low reasoning effort and 80,000-token native auto-compaction setting.
`approval_policy="never"` remains explicit. The advisor no longer uses the lab
filesystem/domain permission profile. Its privileges are the systemd service's OS
privileges, including filesystem/network access. A stripped child environment is
not credential isolation when the filesystem is accessible. No trading privilege,
account start/reset/recovery, risk change or protected-data access is authorized.
The existing explicit analysis/dependency tools still use their own sandbox.

Research has a **Conversation & application prompts** panel, and live activity
links to the corresponding retained exchange. The panel includes:

- Application workspace instructions, prompt, actual input brief and response schema.
- Public commentary and the validated structured assistant response.
- Native command/search/tool events, harness tool arguments and returned results.
- Persistent-session connection and emitted compaction events.

This is application-level visibility, not access to provider-internal instructions
or private model reasoning. The input records show the context actually sent for
that turn, including bounded historical context; native session compaction retains
its separate telemetry. Session/turn IDs correlate events; the first input in a new
thread can have an empty session ID until its subsequent connection event.
Capture begins at deployment. Earlier full prompts cannot be reconstructed.
Upstream tools and the Codex transport retain their existing runtime/output limits;
a retained result cannot restore bytes a tool never returned.

## Display and storage

Application input/instructions load in 2,000-character pages, public assistant text
in 1,500-character pages, and tool exchanges in 3,000-character pages. Next page
replaces the visible text. Content is rendered with textContent in a bounded scroll
area. An explicit attachment download retrieves one complete retained record.
Activity remains compact and chat auto-follow is unchanged. Refresh conversation
loads the newest 50 metadata rows; Load older records follows a stable cursor.

Bodies are filtered for credentials **before** hashing, storage or preview slicing.
Content-addressed bodies deduplicate unchanged instructions. Conversation tables
share the authoritative transcript backend, work with SQLite/Cockroach SQL, and
are included in whole-database backups. Limits are seven UTC days, 2,000 entries
and 20 MB of unique body content, whichever removes a record first. A single body
is capped at two million characters with an explicit capture_truncated marker.
Count/size eviction can therefore shorten the seven-day window. Hourly database
maintenance and every append prune records and orphaned bodies. Research findings,
job identities, unknown-action evidence, account state and trade controls are not
part of that pruning.

The browser routes are GET-only:

- `/api/lab/conversation?limit=50&before=CURSOR`: metadata, no full bodies.
- `/api/lab/conversation/ID?offset=0&limit=3000`: bounded character page (max 12,000).
- `/api/lab/conversation/ID/download`: plain-text attachment, never HTML.

The visibility/permission change does not resolve historical uncertain actions or
prove improved research productivity. Reconciliation must establish side effects
before any retry, and repair completion still requires reproduced failures,
tested releases and measured results.

## Verification

The release passed 941 tests with one existing skip. All eight new regression
tests fail against the prior release. Browser verification covers desktop/mobile
layout, inert untrusted text, bounded page navigation and full-record downloads.
The permission test checks the real launcher retains --yolo, persistent resumption
and compaction, while the original explicit-tool sandbox test remains unchanged.
