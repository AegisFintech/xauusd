# Datadog Bits connection

Credential smoke test on 2026-09-23:

- API key validation: HTTP 200, valid.
- API/application key pair validation: HTTP 200.
- Configured workflow read: HTTP 200; published with an API trigger.
- Its single `Run_Agent` step targets the configured `DD_AGENT_ID`.
- A connectivity-only invocation completed with workflow and step `SUCCEEDED`.
- After the operator mapped the agent final response to the workflow output,
  a second connectivity-only invocation succeeded and returned a 254-character
  JSON string in `outputs.output`.
- All nine contract checks passed: exact envelope fields, `xauusd/1` protocol,
  matching cycle ID and reply-to ID, completed status, empty actions, string
  summary, null review time, and null blocker. No Markdown stripping or other
  repair was needed. This verifies one no-action round trip, not arbitrary
  command execution or sustained contract reliability.

The test requested no tools, commands, trades, or configuration changes. The local
harness did not execute any model output or change the running planner.

## Configuration

Use the placeholders in `.env.example` (also available as `.env.sample`):

| Variable | Purpose |
| --- | --- |
| `DD_REGION` | Datadog site region, such as `us1`, `eu`, or `ap1` |
| `DD_API_KEY` | API key, sent only as the authentication header |
| `DD_APP_KEY` | Application key with workflow read and run permissions |
| `DD_AGENT_ID` | Custom Bits agent selected by the workflow |
| `DD_BITS_WORKFLOW_ID` | Published, API-triggered workflow ID |

Set `AGENT_PLANNER=datadog` to use these settings. The workflow identity is checked
against `DD_AGENT_ID` on startup. `DD_HTTP_TIMEOUT_SECONDS` defaults to 20 and
`DD_WORKFLOW_TIMEOUT_SECONDS` to 300. The active deployment no longer needs `OPENAI_*`.
Do not copy actual keys or identifiers into templates or documentation.

## Verified transport and remaining integration

Datadog documents [workflow execution](https://docs.datadoghq.com/api/latest/workflow-automation/execute-a-workflow/)
at `POST /api/v2/workflows/{workflow_id}/instances`, with a request shaped as:

```json
{"meta":{"payload":{"input":"serialized xauusd/1 invocation JSON"}}}
```

Poll `GET /api/v2/workflows/{workflow_id}/instances/{instance_id}` for completion.
The workflow accepts a STRING `input` used by its agent prompt. Its STRING `output`
is now mapped to the agent's final response. Read `outputs.output` from the
completed instance and validate it as the `xauusd/1` envelope before considering
any action. The connectivity test verified that invocation IDs survive this
round trip. The adapter, durable jobs and feedback loop are implemented in
`xauusd/bits.py`, `xauusd/bits_jobs.py`, and `xauusd/bits_runner.py`.

This API path can carry server-initiated requests and results without a public
shell HTTP endpoint. A subsequent live test requested `printf 42`, executed it
through the durable shell wrapper, and returned its successful result to Bits,
which acknowledged it with a valid completed envelope.

The operator reports **sol GPT-5.6** selected in the Datadog agent. This is an operator-reported setting, not a model
identity verified from API metadata. Credit eligibility and tariff remain
unverified; every decision/result exchange is a workflow execution.

## Runtime and recovery

The existing `xauusd-agent.service` owns the loop. It downloads initial data if
missing, refreshes stale observations, submits Bits context, polls the workflow,
runs one returned shell command, and feeds its persisted result into the next
invocation. A cycle has at most `AGENT_MAX_STEPS_PER_TICK` executed actions.
Responses with invalid JSON, mismatched IDs, unknown fields, or excessive limits
never reach execution. Workflow POSTs have no automatic retry. Pending workflow
IDs resume after restart; uncertain submissions or shell outcomes fail closed.

`bits_state` and `bits_jobs` live in the configured state database alongside the
paper account and transcript. Runtime output is bounded, explicitly marked when
truncated, and sensitive content is withheld. This filter is not protection from
an intentionally obfuscated command or credential exfiltration: the operator has
authorized unrestricted container shell access. Do not describe local risk gates
as tamper-proof under this permission model.

The independent paper monitor runs every five seconds. It marks fresh prices and
persists stops on daily-loss or drawdown breaches. It never liquidates positions.
Existing demo execution requires its separate verified-account/reconciliation
lifecycle; enabling Bits does not override it. The current deployment stays
paper-only.

After checking effects of an uncertain command, stop the agent and use
`bits-recover --reason ...`, then explicitly `paper start` and restart the service.
Completed commands are not replayed with the same cycle/action ID. Do not run
multiple agent hosts against one state store; the runtime lock is container-local.

See [the system prompt](bits-system-prompt.md) and the root README for commands.

## Deployment validation — 2026-09-23

- Full suite: 344 passed (one existing protobuf datetime deprecation warning).
- Live strict JSON submission/polling and workflow-agent identity checks passed.
- `scripts/bits_smoke.py` passed: Bits requested `printf 42`, the shell executed
  it, and Bits acknowledged the returned result. It uses a temporary database,
  does not trade, and consumes two workflow executions.
- The deployed service completed a real repository-inspection/result-feedback
  cycle, then scheduled a later review. No trade was forced for validation.
- Market-data refresh, independent paper monitoring, and `/api/health` were
  healthy with no alerts. The paper account was flat at verification time.
- Graceful restart preserved the scheduled review, marked the prior transcript
  run stopped, and started one new run. No automatic systemd restarts occurred.
- The deployed agent unit matches `deploy/systemd/xauusd-agent.service`.
- A verified SQLite backup was taken before deployment.

This validates operation and recovery, not profitability, future model behavior,
or broker fills. The deployed account remains paper-only. The previous historical
kill-switch reason can remain in state after an explicit start; the active stop
is determined by the current `stopped` boolean.
