# Local handoff audit — 2026-09-24

Scope: merged baseline `35d9ccf`, issues #12 and #13. Deployment remains paused.
No services started, enabled or restarted; no broker requests, recovery operations,
account resets or kill-switch changes were performed during this audit.

## Local validation and deployment

- Full real-environment suite: **388 passed**, one existing protobuf datetime
  deprecation warning, 20.15 seconds. FastAPI/dashboard, psycopg, actual parquet,
  Twisted and virtual-environment checks ran successfully. No test fixes needed.
- `paper status` loads New York timezone data successfully. Persisted state remains
  stopped with reason `operator`, cash/equity $100,000, zero position/trades, and
  boolean `market_open`. No dependency installation was needed.
- The configured backend is local with `state/xauusd_local.db`. The demo template
  previously allowed writes only to `reports/`; its repository copy now also allows
  `state/`. It is **not installed on this host**, so no host unit was changed.
- Agent, live-view and state-backup service/timer templates exactly match the host.
  Data-update service/timer were copied from the host without credentials; these
  new templates exactly match. All host units and timers remain disabled/inactive.
- README's claim that only a demo template exists is corrected. There are now seven
  repository unit files. Graphify was rebuilt for the merged code.

Host-only legacy units (retained, not deleted or installed elsewhere):

- `xauusd-backup.service`, `xauusd-backup.timer`
- `xauusd-dashboard.service`
- `xauusd-remote-coordinator.service`
- `xauusd-research.service`, `xauusd-research.timer`
- `xauusd-scaling-checkpoint.service`, `xauusd-scaling-checkpoint.timer`
- `xauusd-tournament.service`
- `xauusd-weekly-report.service`, `xauusd-weekly-report.timer`

Before future enablement, review custom storage paths and runtime credentials
against each unit's write permissions. This audit changes repository templates
only; it does not authorize activation or change shell privileges.
