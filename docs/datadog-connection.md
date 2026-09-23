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

These settings are preparatory; the current trading planner still uses `OPENAI_*`.
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
round trip. A production adapter, durable action handling, and execution/result
feedback loop still need implementation.

This API path can carry server-initiated requests and results without a public
shell HTTP endpoint. Model availability, credit coverage, sustained JSON contract
fidelity, and continuous trading integration were not established by this test.
