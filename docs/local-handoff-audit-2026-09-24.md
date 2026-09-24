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

## Planner latency (read-only)

Read all persisted `agent_transcript` rows in ID order through SQLite `mode=ro`.
Match each `bits_submit.content_json.message_id` to the parsed assistant reply's
`reply_to`, including matches across process restarts. Subtract ISO timestamps;
use NumPy's default linear percentiles. The sample is post-reset history, not
all historic operation. This includes polling overhead and a deployment pause;
it is observed harness turnaround, not pure model inference time. The submit event
is written after the workflow POST returns, so initial POST latency is excluded.

| Metric | Result |
|---|---:|
| Matched replies | 120 |
| Unmatched replies / unanswered submissions | 0 / 0 |
| p50 | 11.17 seconds |
| p95 | 23.16 seconds |
| Maximum | 74.90 seconds |
| Replies / action replies over 180 seconds | 0 / 0 |
| `tick_end` with `action not executed: budget or response age limit` | 0 |

The 180-second submission-age action cutoff and 300-second workflow deadline still
permit a theoretically valid workflow reply to be discarded. This did not occur
in this sample. Separate future research-action age policy from trade freshness;
do not relax market-data freshness or replay uncertain actions. The 1200-second
shell execution deadline is a third, independent timer.

## cTrader SDK and protocol review (no broker connection)

Inspected installed `ctrader-open-api==0.9.2`, generated protobuf descriptors,
`Client.send`, `Client._received`, and repository transport/adapter code. Constructed
messages locally only; no authentication or order requests were sent.

### Order lifecycle and errors — follow-up #15

Execution events can represent acceptance or execution. Their required
`executionType` distinguishes outcomes; `errorCode` is optional. Error-response and
order-error messages require the error field, but protobuf required strings can
be empty. These schema facts do not prove production rejection events always
contain a nonempty code. [Official message reference](https://help.ctrader.com/open-api/messages/#protooaexecutionevent).

Local probes: `ProtoOAErrorRes(errorCode='')` and an account-qualified
`ProtoOAOrderErrorEvent(errorCode='')` both pass `IsInitialized()` while repository
`is_error()` returns no error. An initialized `ProtoOAExecutionEvent` with
`ORDER_REJECTED` and no error code also evades `is_error()`. These are schema-valid
counterexamples, not claims about observed broker traffic.

The installed SDK pops its response deferred on the first matching `clientMsgId`.
It does not wait for a fill or inspect execution type. Thus `send(new_order)` can
resolve on acceptance, fill, or error, depending on the first correlated reply;
there is no terminal-fill guarantee. The adapter strips execution type and marks
any receipt without an error code accepted. Improve explicit rejection handling,
partial/final-fill tracking and unknown-event handling before demo execution.
Acceptance must not be treated as proof of a filled position.

### Broker order IDs — follow-up #14

The documented `clientOrderId` limit is **50 characters**.
[Official new-order reference](https://help.ctrader.com/open-api/messages/#protooaneworderreq).

The repository's stable agent decision ID is a 64-character SHA256 hex digest,
passed unchanged into `CTraderOrder.request_id` and `clientOrderId`. The installed
protobuf has no max-length validator, so local serialization does not expose this
contract violation. This is a demo readiness blocker; actual broker rejection was
not tested. Preserve internal IDs and introduce a durable broker-ID mapping only
after designing migration and reconciliation. The scheme was not changed here.

### Position reconciliation — follow-up #16

Positions carry `positionId` and nested `tradeData`, including symbol, volume,
side, and optional label/comment. They do not carry `clientOrderId`; orders do.
[Official model reference](https://help.ctrader.com/open-api/model-messages/#protooaposition).

Installed descriptors confirm those fields. The current request uses the constant
label `xauusd-demo` and no request-specific comment. That label identifies the
application but cannot uniquely map an individual request. `_normalize` processes
only reconcile response orders and ignores positions; account/symbol checks alone
do not compare broker exposure with the paper position. Resolve positions with a
persistent order/deal/position mapping, accounting for partial fills and netting.
Label/comment can support correlation but are not sufficient proof by themselves.

### Demo-only host boundary

Official documentation says demo/live environments are separated and accounts
cannot be used on the opposite endpoint.
[Official endpoint documentation](https://help.ctrader.com/open-api/proxies-endpoints/).

This supports the intended demo-host boundary when a configured account skips
account-list discovery. It is documentation evidence, not a live negative-auth
probe. The installed SDK selects an endpoint; it does not independently establish
account type. Local code should explicitly validate authentication response type,
account identity and errors before assigning DEMO metadata, as defense in depth.
Do not test this by attempting to authorize a real-money account.

## Recommended next work

1. Resolve #14–#16 before any demo order. Keep the deployment paused until separately
   authorized; passing unit tests does not demonstrate broker readiness.
2. Improve research reliability: use known dataset paths, validated backtest
   interfaces and bounded output. Twenty-minute jobs remain subject to the existing
   fail-closed timeout rule. Any future recoverable-research policy needs a credible
   way to distinguish research effects from trading effects under arbitrary shell;
   an agent-provided label alone is not a reliable boundary.
3. Revisit workflow/action deadline mismatch with a targeted delayed-response test.
   No observed latency failure justifies raising trade freshness limits.
4. Keep the deprecated host units disabled. Before future deployment, validate
   custom state paths and note SQLite backup may need state-directory write access
   for WAL sidecars under its sandbox; this was not exercised by starting a service.

All six local handoff items are complete as audits/validation. Broker compatibility
issues remain explicitly tracked work, not silently repaired trading behaviour.
