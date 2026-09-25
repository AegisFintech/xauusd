"""Datadog workflow transport and the strict, correlated xauusd/1 boundary."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
import os
import re
from urllib import request, error

PROTOCOL = "xauusd/1"
REGIONS = {"us1": "datadoghq.com", "us3": "us3.datadoghq.com",
           "us5": "us5.datadoghq.com", "eu": "datadoghq.eu",
           "ap1": "ap1.datadoghq.com", "ap2": "ap2.datadoghq.com",
           "uk1": "uk1.datadoghq.com"}
MAX_RESPONSE = 2_000_000


SAFE_CODE = re.compile(r"[a-z][a-z0-9_]{0,63}")


class BitsError(RuntimeError):
    """Safe diagnostic only: never includes response bodies or credentials.

    ``code`` is a stable, machine-readable classification that survives into
    tick events and heartbeats; the message stays a fixed, payload-free string.
    """

    def __init__(self, message: str = "", code: str | None = None):
        super().__init__(message)
        if not (isinstance(code, str) and SAFE_CODE.fullmatch(code)):
            code = re.sub(r"[^a-z0-9]+", "_", str(message).lower()).strip("_")[:64] or "bits_error"
            if not code[0].isalpha():
                code = "bits_" + code[:58]
        self.code = code


# Only classifications, never messages, are recorded for errors we do not own.
_GENERIC_ERROR_CODES = (("OperationalError", "database_operational_error"),
                        ("DatabaseError", "database_error"),
                        ("TimeoutError", "timeout"),
                        ("ConnectionError", "connection_error"),
                        ("OSError", "os_error"))


def error_details(exc: BaseException) -> dict:
    """Payload-free classification of an exception for events and heartbeats.

    BitsError messages are fixed strings by contract, so they may be shown.
    Other exception text can contain arbitrary data and is never included.
    """
    detail = {"error_type": type(exc).__name__}
    if isinstance(exc, BitsError):
        detail.update(error_code=exc.code, summary=str(exc))
        return detail
    names = {cls.__name__ for cls in type(exc).__mro__}
    detail["error_code"] = next((code for name, code in _GENERIC_ERROR_CODES if name in names), "unclassified")
    return detail


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise BitsError("duplicate JSON field", "duplicate_json_field")
            result[key] = value
        return result
    def invalid(_):
        raise BitsError("non-finite JSON value", "non_finite_json")
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    except (ValueError, TypeError):
        raise BitsError("invalid JSON", "invalid_json") from None


def validate_envelope(raw, cycle_id, message_id):
    obj = strict_json(raw)
    fields = {"protocol", "cycle_id", "reply_to", "status", "summary", "actions",
              "next_review_at", "blocker"}
    if not isinstance(obj, dict) or set(obj) != fields:
        raise BitsError("invalid envelope fields", "invalid_envelope_fields")
    if obj["protocol"] != PROTOCOL or obj["cycle_id"] != cycle_id or obj["reply_to"] != message_id:
        raise BitsError("response correlation mismatch", "correlation_mismatch")
    if obj["status"] not in ("action_required", "waiting", "blocked", "completed"):
        raise BitsError("invalid response status", "invalid_status")
    if not isinstance(obj["summary"], str) or len(obj["summary"]) > 16000:
        raise BitsError("invalid summary", "invalid_summary")
    if obj["blocker"] is not None and (not isinstance(obj["blocker"], str) or len(obj["blocker"]) > 4000):
        raise BitsError("invalid blocker", "invalid_blocker")
    if obj["status"] == "blocked" and not obj["blocker"]:
        raise BitsError("blocked response requires explanation", "blocked_without_blocker")
    actions = obj["actions"]
    if not isinstance(actions, list) or len(actions) > 1:
        raise BitsError("expected at most one action", "too_many_actions")
    if bool(actions) != (obj["status"] == "action_required"):
        raise BitsError("actions and status disagree", "actions_status_mismatch")
    for action in actions:
        validate_shell_action(action)
    if obj["next_review_at"] is not None:
        try:
            dt = datetime.fromisoformat(obj["next_review_at"].replace("Z", "+00:00"))
            if dt.utcoffset() != timezone.utc.utcoffset(dt):
                raise ValueError()
        except (TypeError, AttributeError, ValueError):
            raise BitsError("review time must be UTC ISO 8601", "invalid_review_time") from None
    return obj


def validate_shell_action(action):
    if not isinstance(action, dict) or set(action) != {"id", "type", "args"}:
        raise BitsError("invalid action fields", "invalid_action_fields")
    if not isinstance(action["id"], str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", action["id"]):
        raise BitsError("invalid action ID", "invalid_action_id")
    if action["type"] != "shell":
        raise BitsError("unsupported action type", "unsupported_action_type")
    args = action["args"]
    if not isinstance(args, dict) or set(args) != {"command", "cwd", "timeout_sec", "max_output_bytes"}:
        raise BitsError("invalid shell arguments", "invalid_shell_arguments")
    if not isinstance(args["command"], str) or not args["command"].strip() or len(args["command"]) > 65536 or "\0" in args["command"]:
        raise BitsError("invalid command", "invalid_command")
    if not isinstance(args["cwd"], str) or not os.path.isabs(args["cwd"]) or "\0" in args["cwd"]:
        raise BitsError("cwd must be absolute", "invalid_cwd")
    for name, upper in (("timeout_sec", 3600), ("max_output_bytes", 1048576)):
        if type(args[name]) is not int or not 1 <= args[name] <= upper:
            raise BitsError("invalid shell limit", "invalid_shell_limit")


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass
class BitsClient:
    site: str
    workflow_id: str
    api_key: str = field(repr=False)
    app_key: str = field(repr=False)
    timeout: float = 20

    def __post_init__(self):
        if self.site not in REGIONS.values():
            raise BitsError("unsupported Datadog site", "unsupported_site")
        if not re.fullmatch(r"[A-Za-z0-9-]{1,128}", self.workflow_id):
            raise BitsError("invalid workflow ID", "invalid_workflow_id")
        if not self.api_key or not self.app_key:
            raise BitsError("missing Datadog credentials", "missing_credentials")
        if not math.isfinite(self.timeout) or not 0 < self.timeout <= 60:
            raise BitsError("invalid Datadog timeout", "invalid_timeout")

    @classmethod
    def from_env(cls):
        region = os.getenv("DD_REGION", "us1").strip().lower()
        return cls(REGIONS.get(region, region), os.getenv("DD_BITS_WORKFLOW_ID", ""),
                   os.getenv("DD_API_KEY", ""), os.getenv("DD_APP_KEY", ""),
                   float(os.getenv("DD_HTTP_TIMEOUT_SECONDS", "20")))

    def _request(self, suffix="", payload=None):
        req = request.Request("https://api." + self.site + "/api/v2/workflows/" + self.workflow_id + suffix,
                              data=None if payload is None else json.dumps(payload, allow_nan=False).encode(),
                              headers={"DD-API-KEY": self.api_key, "DD-APPLICATION-KEY": self.app_key,
                                       "Content-Type": "application/json", "Accept": "application/json",
                                       "User-Agent": "xauusd-bits/1"})
        try:
            with request.build_opener(NoRedirect).open(req, timeout=self.timeout) as response:
                raw = response.read(MAX_RESPONSE + 1)
        except error.HTTPError as exc:
            status = exc.code if isinstance(exc.code, int) and 100 <= exc.code <= 599 else 0
            raise BitsError("Datadog HTTP " + str(status), "datadog_http_" + str(status)) from None
        except (OSError, error.URLError):
            raise BitsError("Datadog transport failed; submission outcome may be unknown",
                            "datadog_transport_failed") from None
        if len(raw) > MAX_RESPONSE:
            raise BitsError("Datadog response exceeds limit", "response_too_large")
        return strict_json(raw)

    def submit(self, invocation):
        # Never automatically retry POST: Datadog does not document an idempotency key.
        data = self._request("/instances", {"meta": {"payload": {"input": json.dumps(invocation, allow_nan=False)}}})
        instance = data.get("data", {}).get("id")
        if not isinstance(instance, str) or not re.fullmatch(r"[A-Za-z0-9-]{1,128}", instance):
            raise BitsError("missing workflow instance ID", "missing_instance_id")
        return instance

    def verify_agent(self, agent_id):
        """Pin the workflow to the configured agent before starting the service."""
        attrs = self._request().get("data", {}).get("attributes", {})
        spec = attrs.get("spec", {})
        steps = spec.get("steps", [])
        if not attrs.get("published") or len(steps) != 1:
            raise BitsError("expected published single-agent workflow", "workflow_not_single_agent")
        params = {p.get("name"): p.get("value") for p in steps[0].get("parameters", [])}
        if (steps[0].get("actionId") != "com.datadoghq.dd.bitsai.customagent.customAgentExecute" or
                not agent_id or params.get("customAgentId") != agent_id):
            raise BitsError("workflow agent does not match DD_AGENT_ID", "workflow_agent_mismatch")
        if not any(p.get("name") == "output" and p.get("value") for p in spec.get("outputSchema", {}).get("parameters", [])):
            raise BitsError("workflow output mapping is missing", "workflow_output_missing")

    def poll(self, instance, cycle_id, message_id):
        if not re.fullmatch(r"[A-Za-z0-9-]{1,128}", instance):
            raise BitsError("invalid workflow instance ID", "invalid_instance_id")
        data = self._request("/instances/" + instance)
        try:
            attrs = data["data"]["attributes"]
            state = attrs["instanceStatus"]["detailsKind"]
        except (KeyError, TypeError):
            raise BitsError("invalid workflow result", "invalid_workflow_result") from None
        if state in ("IN_PROGRESS", "RUNNING", "PENDING", "QUEUED"):
            return None
        if state != "SUCCEEDED":
            # The terminal state is a Datadog enum (for example FAILED or CANCELLED).
            kind = state.lower() if isinstance(state, str) and re.fullmatch(r"[A-Z_]{1,32}", state) else "unknown"
            raise BitsError("workflow did not succeed", "workflow_" + kind)
        return validate_envelope(attrs.get("outputs", {}).get("output"), cycle_id, message_id)
