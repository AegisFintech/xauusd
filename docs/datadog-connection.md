# Datadog Bits connection

Credential smoke test on 2026-09-23:

- API key validation: HTTP 200, valid.
- API/application key pair validation: HTTP 200.
- Configured workflow read: HTTP 200; published with an API trigger.
- Its single `Run_Agent` step targets the configured `DD_AGENT_ID`.
- A connectivity-only invocation completed with workflow and step `SUCCEEDED`.
- Workflow `outputs.output` was an empty string. No JSON agent response was
  available through that output, so the planner round trip is not yet verified.

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

## Verified transport and remaining setup

Datadog documents [workflow execution](https://docs.datadoghq.com/api/latest/workflow-automation/execute-a-workflow/)
at `POST /api/v2/workflows/{workflow_id}/instances`, with a request shaped as:

```json
{"meta":{"payload":{"input":"serialized xauusd/1 invocation JSON"}}}
```

Poll `GET /api/v2/workflows/{workflow_id}/instances/{instance_id}` for completion.
The workflow accepts a STRING `input` used by its agent prompt. Its STRING `output`
currently has an empty value in the workflow definition. In Datadog's workflow
editor, map that output to the Run Agent action's actual reply field using the
output picker; do not guess a field path. Repeat the connectivity-only test and
verify that `outputs.output` contains the expected JSON envelope and invocation
IDs before integrating command execution.

This API path can carry server-initiated requests and results without a public
shell HTTP endpoint. Model availability, credit coverage, JSON contract fidelity,
and continuous trading integration were not established by this credential test.
