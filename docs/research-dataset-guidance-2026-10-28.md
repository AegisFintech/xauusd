# Frozen dataset guidance — scalper issue #405

A recent autonomous research-plan call supplied a dataset version different from
the active frozen manifest. The server correctly rejected it. The existing brief
already contains the manifest; the model may still choose an invalid value. A
retained sample of 28 plan calls included two such mismatch errors alongside older
shape/text errors; it spans releases and is not a measured post-change rate.

The catalog now exposes the current frozen SHA256 version as a `const` in a copied
plan-input schema, refreshed on each advisor turn. A stale-plan error returns that
validated digest as a correction hint. Non-SHA values are never echoed or made a
schema constant. Invalid non-object manifest metadata rejects plan creation; a
missing manifest retains historical behavior. Server checks remain authoritative:
no model input is substituted, no old plan is rewritten, and a dataset change
between turns still rejects the stale request. The next turn sees fresh metadata.

This change is research guidance only. It does not access the protected holdout,
reset a manifest or attempts, create a plan itself, force a provider or job call,
change accounts or enable a broker executor. The model's future behavior must be
observed independently; a passing fixture does not establish autonomous learning.

All eight new regression cases failed on the previous source; 38 focused tests
passed after the correction, including malformed metadata and a dataset change
between turns. The complete isolated suite passed 986 tests with one optional
PostgreSQL parity test skipped because a disposable database URL was unavailable:
`PYTHONDONTWRITEBYTECODE=1 /root/xauusd/.venv/bin/python -m pytest tests -q -p no:cacheprovider`.
A protobuf deprecation warning remains. Both independent code reviews found no
blocker; source delivery and actual autonomous completion are tracked separately
in scalper issue #405. That issue stays open until genuine fresh
result-to-finding-to-close evidence exists.

The staged-content secret scanner and an exact match against active sensitive
configuration values passed. The broader primary-repository scanner cannot scan
this existing upstream baseline unchanged: it treats an empty `DATABASE_URL` in
`.env.example` as a populated assignment across a newline and refuses the
pre-existing tracked `.env.sample` symlink. The example value is empty and does
not match the active database value. Neither baseline file was changed here.
