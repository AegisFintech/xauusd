"""Fail-closed cTrader Open API execution boundary for verified demo accounts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import hashlib
import json
import math
import os
import threading
from typing import Any, Callable, Protocol

from .ctrader_auth import DEMO_HOST, demo_accounts, is_error, resolve_symbol

KILL_SWITCH = "KILL_SWITCH"
DUPLICATE_REQUEST = "DUPLICATE_REQUEST"
# The broker answered the order with an error: nothing was executed.
BROKER_REJECTED = "BROKER_REJECTED"
# The transport failed or timed out after sending: the order may or may not have executed.
OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"


class CTraderDemoSafetyError(RuntimeError):
    """A configuration, recovery, or execution condition that must fail closed."""


@dataclass(frozen=True)
class CTraderDemoOpenApiConfig:
    """Credentials and target for an explicitly-invoked demo Open API session."""
    client_id: str
    client_secret: str
    access_token: str
    account_id: int | None = None
    host: str = DEMO_HOST
    port: int = 5035
    symbol: str = "XAUUSD"
    timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> "CTraderDemoOpenApiConfig":
        values = {
            "client_id": os.getenv("CTRADER_CLIENT_ID"),
            "client_secret": os.getenv("CTRADER_CLIENT_SECRET"),
            "access_token": os.getenv("CTRADER_ACCESS_TOKEN"),
        }
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise CTraderDemoSafetyError(f"missing cTrader Open API settings: {', '.join(missing)}")
        try:
            config = cls(
                client_id=str(values["client_id"]), client_secret=str(values["client_secret"]),
                access_token=str(values["access_token"]), account_id=int(os.environ["CTRADER_CTID_TRADER_ACCOUNT_ID"])
                if os.getenv("CTRADER_CTID_TRADER_ACCOUNT_ID") else None,
                host=os.getenv("CTRADER_OPEN_API_HOST", DEMO_HOST),
                port=int(os.getenv("CTRADER_OPEN_API_PORT", "5035")),
                symbol=os.getenv("CTRADER_SYMBOL", "XAUUSD"),
                timeout_seconds=float(os.getenv("CTRADER_OPEN_API_TIMEOUT_SECONDS", "30")),
            )
        except ValueError as exc:
            raise CTraderDemoSafetyError("invalid cTrader Open API numeric setting") from exc
        config.validate()
        return config

    def validate(self) -> None:
        if os.getenv("CTRADER_DEMO_ONLY") != "true":
            raise CTraderDemoSafetyError("CTRADER_DEMO_ONLY=true is required")
        if self.host != DEMO_HOST:
            raise CTraderDemoSafetyError("cTrader execution is restricted to demo.ctraderapi.com")
        if self.symbol != "XAUUSD" or self.port <= 0 or (self.account_id is not None and self.account_id <= 0):
            raise CTraderDemoSafetyError("a positive configured account (when supplied), port, and XAUUSD symbol are required")
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise CTraderDemoSafetyError("cTrader timeout must be finite and positive")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True)
class CTraderDemoAccount:
    account_id: int
    symbol_id: int
    account_type: str = "DEMO"
    symbol: str = "XAUUSD"
    host: str = DEMO_HOST

    def validate(self) -> None:
        if self.host != DEMO_HOST:
            raise CTraderDemoSafetyError("cTrader execution is restricted to demo.ctraderapi.com")
        if self.account_type != "DEMO":
            raise CTraderDemoSafetyError("cTrader account type must be DEMO")
        if self.symbol != "XAUUSD":
            raise CTraderDemoSafetyError("cTrader execution supports only XAUUSD")
        if (not isinstance(self.account_id, int) or isinstance(self.account_id, bool) or self.account_id <= 0 or
                not isinstance(self.symbol_id, int) or isinstance(self.symbol_id, bool) or self.symbol_id <= 0):
            raise CTraderDemoSafetyError("positive integer account_id and symbol_id are required")


@dataclass(frozen=True)
class CTraderSymbolMetadata:
    """Read-only broker price/volume constraints for the configured demo symbol."""
    symbol: str
    symbol_id: int
    digits: int
    lot_size: float
    min_volume: int
    max_volume: int
    step_volume: int

    def validate(self) -> None:
        if self.symbol != "XAUUSD":
            raise CTraderDemoSafetyError("cTrader symbols metadata is restricted to XAUUSD")
        if (self.digits <= 0 or self.lot_size <= 0 or self.min_volume <= 0 or self.max_volume <= 0 or
                self.step_volume <= 0 or self.min_volume > self.max_volume):
            raise CTraderDemoSafetyError("cTrader returned invalid symbol volume constraints")


@dataclass(frozen=True)
class CTraderOrder:
    request_id: str
    side: str
    volume: int

    def validate(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id is required")
        if self.side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if not isinstance(self.volume, int) or isinstance(self.volume, bool) or self.volume <= 0:
            raise ValueError("volume must be a positive integer cTrader volume in cents")


class CTraderTransport(Protocol):
    def send(self, request: Any, timeout_seconds: float) -> Any: ...


class CTraderDemoOpenApiTransport:
    """Synchronous, bounded cTrader demo transport.

    Construction and import are inert. ``discover`` or ``send`` is the explicit network
    boundary; both validate the demo-only environment before a client is constructed.
    ``client_factory``, ``reactor``, and ``extract`` make the protocol boundary testable.
    """
    def __init__(self, config: CTraderDemoOpenApiConfig, *, client_factory: Callable[..., Any] | None = None,
                 reactor: Any | None = None, extract: Callable[[Any], Any] | None = None,
                 message_types: dict[str, Any] | None = None):
        config.validate()
        self.config, self._client_factory, self._reactor, self._extract = config, client_factory, reactor, extract
        self._message_types = message_types
        self._client: Any | None = None
        self._account: CTraderDemoAccount | None = None
        self._symbol_metadata: CTraderSymbolMetadata | None = None
        self._reactor_thread: threading.Thread | None = None
        self._service_started = False

    @classmethod
    def from_env(cls, **kwargs: Any) -> "CTraderDemoOpenApiTransport":
        return cls(CTraderDemoOpenApiConfig.from_env(), **kwargs)

    def discover(self) -> CTraderDemoAccount:
        self._ensure_authenticated()
        assert self._account is not None
        return self._account

    def send(self, request: Any, timeout_seconds: float) -> Any:
        if not isinstance(timeout_seconds, (int, float)) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and positive")
        self._ensure_authenticated()
        response = self._request(request, float(timeout_seconds))
        return self._normalize(request, response)

    def symbol_metadata(self) -> CTraderSymbolMetadata:
        """Read-only broker volume/price metadata for the resolved demo symbol."""
        self._ensure_authenticated()
        assert self._account is not None
        if self._symbol_metadata is not None:
            return self._symbol_metadata
        messages = self._messages()
        response = self._extract_message(self._request(messages["ProtoOASymbolByIdReq"](
            ctidTraderAccountId=self._account.account_id, symbolId=[self._account.symbol_id]),
            self.config.timeout_seconds))
        self._raise_for_error(response, "symbol detail")
        symbols = self._values(response, "symbol")
        if not symbols:
            raise CTraderDemoSafetyError("cTrader returned no XAUUSD symbol detail")
        symbol = symbols[0]
        self._symbol_metadata = CTraderSymbolMetadata(
            symbol=self.config.symbol,
            symbol_id=self._account.symbol_id,
            digits=self._as_positive_int(symbol, "digits"),
            lot_size=self._as_number(symbol, "lotSize"),
            min_volume=self._as_positive_int(symbol, "minVolume"),
            max_volume=self._as_positive_int(symbol, "maxVolume"),
            step_volume=self._as_positive_int(symbol, "stepVolume"),
        )
        return self._symbol_metadata

    @staticmethod
    def _as_positive_int(value: Any, name: str) -> int:
        raw = CTraderDemoOpenApiTransport._field(value, name)
        if not isinstance(raw, int) or isinstance(raw, bool) or raw <= 0:
            raise CTraderDemoSafetyError(f"cTrader returned invalid positive integer {name}")
        return raw

    @staticmethod
    def _as_number(value: Any, name: str) -> float:
        raw = CTraderDemoOpenApiTransport._field(value, name)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool) or not math.isfinite(float(raw)):
            raise CTraderDemoSafetyError(f"cTrader returned invalid numeric {name}")
        return float(raw)

    def _ensure_authenticated(self) -> None:
        self.config.validate()  # Re-check immediately before the client/network boundary.
        if self._account is not None:
            return
        client = self._connect()
        messages = self._messages()
        self._request(messages["ProtoOAApplicationAuthReq"](
            clientId=self.config.client_id, clientSecret=self.config.client_secret), self.config.timeout_seconds)
        if self.config.account_id is None:
            accounts = self._extract_message(self._request(messages["ProtoOAGetAccountListByAccessTokenReq"](
                accessToken=self.config.access_token), self.config.timeout_seconds))
            self._raise_for_error(accounts, "account list")
            account = self._find_account(accounts)
            account_id = self._field(account, "ctidTraderAccountId")
        else:
            # A configured demo account id bypasses the account-list request, which can require
            # a token scope that is unnecessary for direct account authorization.
            account_id = self.config.account_id
        self._request(messages["ProtoOAAccountAuthReq"](
            ctidTraderAccountId=account_id, accessToken=self.config.access_token), self.config.timeout_seconds)
        symbols = self._extract_message(self._request(messages["ProtoOASymbolsListReq"](
            ctidTraderAccountId=account_id, includeArchivedSymbols=False), self.config.timeout_seconds))
        self._raise_for_error(symbols, "symbol list")
        symbol_id = self._find_symbol_id(symbols)
        self._account = CTraderDemoAccount(account_id, symbol_id, account_type="DEMO", symbol=self.config.symbol,
                                           host=self.config.host)
        self._account.validate()

    def _connect(self) -> Any:
        if self._client is not None:
            return self._client
        self.config.validate()
        if self._client_factory is None:
            from ctrader_open_api import Client, TcpProtocol
            self._client_factory = lambda host, port: Client(host, port, TcpProtocol)
        self._client = self._client_factory(self.config.host, self.config.port)
        return self._client

    def _messages(self) -> dict[str, Any]:
        if self._message_types is not None:
            return self._message_types
        try:
            from ctrader_open_api.messages.OpenApiMessages_pb2 import (
                ProtoOAAccountAuthReq, ProtoOAApplicationAuthReq, ProtoOAGetAccountListByAccessTokenReq,
                ProtoOASymbolsListReq, ProtoOASymbolByIdReq,
            )
        except ModuleNotFoundError as exc:
            raise CTraderDemoSafetyError("ctrader-open-api is required for demo transport") from exc
        return {name: value for name, value in locals().items() if name.startswith("Proto")}

    def _request(self, request: Any, timeout_seconds: float) -> Any:
        client = self._connect()
        result: dict[str, Any] = {}
        completed = threading.Event()

        def succeeded(value: Any) -> None:
            result["value"] = value
            completed.set()

        def failed(failure: Any) -> None:
            result["error"] = failure
            completed.set()

        # ctrader-open-api uses Twisted's process-global, non-restartable reactor.
        # Keep it alive in one daemon thread so explicit calls can be made sequentially.
        reactor = self._get_reactor()
        self._ensure_reactor_running(reactor)

        def issue() -> None:
            try:
                if not self._service_started:
                    client.startService()
                    self._service_started = True
                client.send(request, responseTimeoutInSeconds=timeout_seconds).addCallbacks(succeeded, failed)
            except Exception as exc:
                failed(exc)

        reactor.callFromThread(issue)
        if not completed.wait(timeout_seconds):
            failed(TimeoutError("cTrader request timed out"))
        if "error" in result:
            failure = result["error"]
            if isinstance(failure, BaseException):
                raise failure
            message = failure.getErrorMessage() if hasattr(failure, "getErrorMessage") else "cTrader request failed"
            raise RuntimeError(message)
        if "value" not in result:
            raise TimeoutError("cTrader request timed out")
        return result["value"]

    def _get_reactor(self) -> Any:
        if self._reactor is None:
            from twisted.internet import reactor
            self._reactor = reactor
        return self._reactor

    def _ensure_reactor_running(self, reactor: Any) -> None:
        if getattr(reactor, "running", False):
            return
        if self._reactor_thread is not None:
            raise CTraderDemoSafetyError("cTrader reactor failed to start")
        ready = threading.Event()

        def run() -> None:
            reactor.callWhenRunning(ready.set)
            reactor.run(installSignalHandlers=False)

        self._reactor_thread = threading.Thread(target=run, name="ctrader-demo-reactor", daemon=True)
        self._reactor_thread.start()
        if not ready.wait(self.config.timeout_seconds):
            raise CTraderDemoSafetyError("cTrader reactor failed to start")

    def _extract_message(self, response: Any) -> Any:
        if self._extract is not None:
            return self._extract(response)
        from ctrader_open_api import Protobuf
        return Protobuf.extract(response)

    @staticmethod
    def _error_fields(message: Any) -> tuple[str, str] | None:
        """Return ``(code, description)`` for a cTrader error message, else None."""
        return is_error(message)

    @staticmethod
    def _raise_for_error(message: Any, context: str) -> None:
        fields = CTraderDemoOpenApiTransport._error_fields(message)
        if fields is not None:
            code, description = fields
            raise CTraderDemoSafetyError(f"cTrader {context} error {code}: {description}")

    @staticmethod
    def _values(message: Any, name: str) -> list[Any]:
        return list(message.get(name, []) if isinstance(message, dict) else getattr(message, name, []))

    @staticmethod
    def _field(value: Any, name: str, default: Any = None) -> Any:
        return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)

    def _find_account(self, response: Any) -> Any:
        accounts = demo_accounts(self._values(response, "ctidTraderAccount"))
        if self.config.account_id is not None:
            selected = next((account for account in accounts if self._field(account, "ctidTraderAccountId") == self.config.account_id), None)
            if selected is None:
                raise CTraderDemoSafetyError("configured cTrader account was not authorized as a demo account")
            return selected
        if len(accounts) != 1:
            raise CTraderDemoSafetyError("automatic discovery requires exactly one authorized demo account")
        return accounts[0]

    def _find_symbol_id(self, response: Any) -> int:
        resolved = resolve_symbol(self._values(response, "symbol"), self.config.symbol)
        if resolved is None:
            raise CTraderDemoSafetyError("XAUUSD is unavailable for the configured cTrader account")
        symbol_id, _ = resolved
        return symbol_id

    def _normalize(self, request: Any, response: Any) -> dict[str, Any]:
        request_type = request.get("type") if isinstance(request, dict) else type(request).__name__
        message = self._extract_message(response)
        if request_type == "ProtoOAReconcileReq":
            assert self._account is not None
            # An error reply must fail reconciliation, never pass as an empty (clean) broker state.
            self._raise_for_error(message, "reconcile")
            outcomes = {}
            for order in self._values(message, "order"):
                request_id = self._field(order, "clientOrderId")
                if isinstance(request_id, str) and request_id:
                    outcomes[request_id] = {"accepted": True, "request_id": request_id,
                                            "response": self._order_receipt(order)}
            return {"account_id": self._account.account_id, "is_demo": True, "symbol": self._account.symbol,
                    "symbol_id": self._account.symbol_id, "request_outcomes": outcomes}
        return self._order_receipt(message)

    def _order_receipt(self, message: Any) -> dict[str, Any]:
        order = self._field(message, "order", message)
        position = self._field(message, "position", None)
        receipt = {"status": type(message).__name__}
        error = self._error_fields(message)
        if error is not None:
            # Order errors arrive as ordinary reply messages, not transport failures.
            receipt["error_code"] = error[0]
        order_id = self._field(order, "orderId")
        position_id = self._field(position, "positionId") if position is not None else None
        if isinstance(order_id, int): receipt["order_id"] = order_id
        if isinstance(position_id, int): receipt["position_id"] = position_id
        return receipt


class CTraderDemoStore(Protocol):
    def initialize(self) -> None: ...
    def start(self, reason: str) -> None: ...
    def stop(self, reason: str) -> None: ...
    def state(self) -> dict[str, Any]: ...
    def mark_reconciled(self, details: dict[str, Any]) -> None: ...
    def reserve(self, request_id: str, request: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]: ...
    def pending_request_ids(self) -> list[str]: ...
    def request_records(self) -> dict[str, dict[str, Any]]: ...
    def finish(self, request_id: str, outcome: dict[str, Any]) -> None: ...
    def audit(self, event: str, payload: dict[str, Any]) -> None: ...


def _initial_state() -> dict[str, Any]:
    return {"stopped": True, "kill_switch_reason": "missing_state", "reconciled": False}


class InMemoryCTraderDemoStore:
    """Test double only; production execution state belongs in CockroachDB."""
    def __init__(self):
        self._state: dict[str, Any] | None = None
        self.requests: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []

    def initialize(self) -> None:
        if self._state is None:
            self._state = _initial_state()

    def stop(self, reason: str) -> None:
        self.initialize(); self._state.update(stopped=True, kill_switch_reason=reason, reconciled=False)

    def start(self, reason: str) -> None:
        self.initialize(); self._state.update(stopped=False, kill_switch_reason=reason)

    def state(self) -> dict[str, Any]:
        self.initialize(); return json.loads(_canonical_json(self._state))

    def mark_reconciled(self, details: dict[str, Any]) -> None:
        self.initialize(); self._state.update(reconciled=True, reconciliation=details)

    def reserve(self, request_id: str, request: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
        existing = self.requests.get(request_id)
        if existing is not None:
            return False, json.loads(_canonical_json(existing.get("outcome"))) if "outcome" in existing else None
        self.requests[request_id] = {"request": request, "status": "pending"}
        self.audit("request_reserved", {"request_id": request_id})
        return True, None

    def finish(self, request_id: str, outcome: dict[str, Any]) -> None:
        self.requests[request_id].update(status="completed", outcome=outcome)
        self.audit("request_finished", {"request_id": request_id, "accepted": outcome["accepted"]})

    def request_records(self) -> dict[str, dict[str, Any]]:
        return json.loads(_canonical_json(self.requests))

    def pending_request_ids(self) -> list[str]:
        return [request_id for request_id, value in self.requests.items() if value["status"] == "pending"]

    def audit(self, event: str, payload: dict[str, Any]) -> None:
        self.events.append({"occurred_at": _now(), "event": event, "payload": payload})


class CockroachCTraderDemoStore:
    """Authoritative persistent execution state, idempotency, and audit store."""
    def __init__(self, database_url: str | None = None, initialize: bool = True):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is required for cTrader demo execution state")
        if initialize:
            self.initialize()

    def connect(self):
        from .experiment_registry import PostgresConnection
        return PostgresConnection(self.database_url)

    def initialize(self) -> None:
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS ctrader_demo_state (state_key TEXT PRIMARY KEY, state_json TEXT NOT NULL, updated_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS ctrader_demo_requests (request_id TEXT PRIMARY KEY, request_json TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','completed')), outcome_json TEXT, created_at TEXT NOT NULL, finished_at TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS ctrader_demo_audit (id BIGSERIAL PRIMARY KEY, occurred_at TEXT NOT NULL, event TEXT NOT NULL, payload_json TEXT NOT NULL)")

    def _state(self, db: Any) -> dict[str, Any]:
        row = db.execute("SELECT state_json FROM ctrader_demo_state WHERE state_key='primary' FOR UPDATE").fetchone()
        if row is None:
            state = _initial_state()
            db.execute("INSERT INTO ctrader_demo_state(state_key,state_json,updated_at) VALUES('primary',?,?)", (_canonical_json(state), _now()))
            return state
        try:
            state = json.loads(row["state_json"])
            if not isinstance(state, dict) or not {"stopped", "reconciled"} <= state.keys():
                raise ValueError("invalid execution state")
            return state
        except (TypeError, ValueError, json.JSONDecodeError):
            state = _initial_state(); state["kill_switch_reason"] = "corrupt_state"; self._save(db, state); return state

    @staticmethod
    def _save(db: Any, state: dict[str, Any]) -> None:
        db.execute("UPDATE ctrader_demo_state SET state_json=?,updated_at=? WHERE state_key='primary'", (_canonical_json(state), _now()))

    @staticmethod
    def _audit(db: Any, event: str, payload: dict[str, Any]) -> None:
        db.execute("INSERT INTO ctrader_demo_audit(occurred_at,event,payload_json) VALUES(?,?,?)", (_now(), event, _canonical_json(payload)))

    def stop(self, reason: str) -> None:
        with self.connect() as db:
            state = self._state(db); state.update(stopped=True, kill_switch_reason=reason, reconciled=False); self._save(db, state); self._audit(db, "kill_switch", {"reason": reason})

    def start(self, reason: str) -> None:
        with self.connect() as db:
            state = self._state(db)
            if not state.get("reconciled"):
                raise CTraderDemoSafetyError("successful reconciliation is required before starting execution")
            state.update(stopped=False, kill_switch_reason=reason); self._save(db, state); self._audit(db, "execution_started", {"reason": reason})

    def state(self) -> dict[str, Any]:
        with self.connect() as db:
            return self._state(db)

    def mark_reconciled(self, details: dict[str, Any]) -> None:
        with self.connect() as db:
            state = self._state(db); state.update(reconciled=True, reconciliation=details); self._save(db, state); self._audit(db, "reconciled", details)

    def reserve(self, request_id: str, request: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
        with self.connect() as db:
            cursor = db.execute("INSERT INTO ctrader_demo_requests(request_id,request_json,status,created_at) VALUES(?,?,?,?) ON CONFLICT (request_id) DO NOTHING", (request_id, _canonical_json(request), "pending", _now()))
            if cursor.rowcount == 1:
                self._audit(db, "request_reserved", {"request_id": request_id})
                return True, None
            row = db.execute("SELECT outcome_json FROM ctrader_demo_requests WHERE request_id=?", (request_id,)).fetchone()
            return False, json.loads(row["outcome_json"]) if row and row["outcome_json"] else None

    def finish(self, request_id: str, outcome: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("UPDATE ctrader_demo_requests SET status='completed',outcome_json=?,finished_at=? WHERE request_id=?", (_canonical_json(outcome), _now(), request_id))
            self._audit(db, "request_finished", {"request_id": request_id, "accepted": outcome["accepted"]})

    def request_records(self) -> dict[str, dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute("SELECT request_id,request_json,status,outcome_json FROM ctrader_demo_requests").fetchall()
            return {row["request_id"]: {"request": json.loads(row["request_json"]), "status": row["status"],
                    "outcome": json.loads(row["outcome_json"]) if row["outcome_json"] else None} for row in rows}

    def pending_request_ids(self) -> list[str]:
        with self.connect() as db:
            rows = db.execute("SELECT request_id FROM ctrader_demo_requests WHERE status='pending' ORDER BY created_at").fetchall()
            return [row["request_id"] for row in rows]

    def audit(self, event: str, payload: dict[str, Any]) -> None:
        with self.connect() as db:
            self._audit(db, event, payload)


class CTraderDemoAdapter:
    """Executes only persisted, reconciled XAUUSD demo-order proposals."""
    def __init__(self, account: CTraderDemoAccount, store: CTraderDemoStore, transport: CTraderTransport, timeout_seconds: float = 30.0):
        self.account, self.store, self.transport, self.timeout_seconds = account, store, transport, timeout_seconds
        self.store.initialize()
        try:
            self._validate_boundary()
        except CTraderDemoSafetyError as exc:
            self.store.stop("invalid_execution_boundary")
            self.store.audit("boundary_rejected", {"reason": str(exc)})
            raise

    def _validate_boundary(self) -> None:
        if os.getenv("CTRADER_DEMO_ONLY") != "true":
            raise CTraderDemoSafetyError("CTRADER_DEMO_ONLY=true is required")
        self.account.validate()
        if not isinstance(self.timeout_seconds, (int, float)) or not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be finite and positive")

    def start(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("start reason is required")
        self._validate_boundary()
        state = self.store.state()
        if not state.get("reconciled"):
            raise CTraderDemoSafetyError("successful reconciliation is required before starting execution")
        # Starting is deliberately separate from recovery and must be operator initiated.
        self.store.start(reason)

    def stop(self, reason: str) -> None:
        if not reason.strip():
            raise ValueError("stop reason is required")
        self.store.stop(reason)

    def state(self) -> dict[str, Any]:
        """Persisted execution kill switch, consulted by the shared restart policy."""
        return self.store.state()

    def reconcile_after_restart(self) -> bool:
        """Verify broker account identity before an operator may start execution."""
        try:
            response = self.transport.send(build_reconcile_request(self.account.account_id), self.timeout_seconds)
            details = _reconciliation_details(response)
            if (details["account_id"] != self.account.account_id or not details["is_demo"] or
                    details["symbol"] != self.account.symbol or details["symbol_id"] != self.account.symbol_id):
                raise CTraderDemoSafetyError("broker reconciliation did not verify the configured demo account and XAUUSD symbol")
            pending = self.store.pending_request_ids()
            records = self.store.request_records()
            mapping = {}
            for request_id, record in records.items():
                # Pre-migration records used the original ID verbatim. Never rewrite history.
                broker_id = record["request"].get("broker_client_order_id", request_id)
                if broker_id in mapping:
                    raise CTraderDemoSafetyError("ambiguous broker request identity")
                mapping[broker_id] = request_id
            outcomes = {mapping.get(key, key): dict(value, request_id=mapping.get(key, key))
                        for key, value in details["request_outcomes"].items()}
            if set(pending) - set(outcomes):
                raise CTraderDemoSafetyError("broker reconciliation did not resolve every pending request")
            for request_id in pending:
                self.store.finish(request_id, outcomes[request_id])
            self.store.mark_reconciled(details)
            return True
        except Exception as exc:
            self.store.stop("reconciliation_failed")
            self.store.audit("reconciliation_failed", {"error_type": type(exc).__name__})
            return False

    def execute(self, order: CTraderOrder) -> dict[str, Any]:
        order.validate(); self._validate_boundary()
        if self.store.state().get("stopped", True):
            return {"accepted": False, "reason": KILL_SWITCH, "request_id": order.request_id}
        request_data = {"account_id": self.account.account_id, "symbol": self.account.symbol, "symbol_id": self.account.symbol_id, "side": order.side, "volume": order.volume,
                        "broker_client_order_id": broker_client_order_id(order.request_id)}
        reserved, prior = self.store.reserve(order.request_id, request_data)
        if not reserved:
            return prior or {"accepted": False, "reason": DUPLICATE_REQUEST, "request_id": order.request_id}
        try:
            response = self.transport.send(build_new_order_request(self.account, order), self.timeout_seconds)
        except Exception as exc:
            # The order may have reached the broker, so this is not a rejection. Stop with a
            # reason the restart policy never auto-resumes: an operator must check broker
            # exposure before an explicit `demo-automation start`.
            outcome = {"accepted": False, "reason": OUTCOME_UNKNOWN, "request_id": order.request_id,
                       "error_type": type(exc).__name__}
            self.store.stop("transport_failure")
        else:
            receipt = _safe_response(response)
            if receipt.get("error_code"):
                outcome = {"accepted": False, "reason": BROKER_REJECTED, "request_id": order.request_id,
                           "response": receipt}
            else:
                outcome = {"accepted": True, "request_id": order.request_id, "response": receipt}
        self.store.finish(order.request_id, outcome)
        return outcome


def broker_client_order_id(request_id: str) -> str:
    """Stable, ASCII broker ID; retain the full internal ID in the request store."""
    if len(request_id) <= 50 and request_id.isascii():
        return request_id
    digest = base64.urlsafe_b64encode(hashlib.sha256(request_id.encode()).digest()).decode().rstrip("=")
    return "xau_" + digest


def build_new_order_request(account: CTraderDemoAccount, order: CTraderOrder) -> Any:
    """Construct the actual Open API market-order protobuf without opening a connection."""
    account.validate(); order.validate()
    try:
        from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOANewOrderReq
        from ctrader_open_api.messages.OpenApiModelMessages_pb2 import ProtoOAOrderType, ProtoOATradeSide
    except ModuleNotFoundError:
        return {"type": "ProtoOANewOrderReq", "ctidTraderAccountId": account.account_id,
                "symbolId": account.symbol_id, "orderType": "MARKET", "tradeSide": order.side,
                "volume": order.volume, "clientOrderId": broker_client_order_id(order.request_id), "label": "xauusd-demo"}
    return ProtoOANewOrderReq(ctidTraderAccountId=account.account_id, symbolId=account.symbol_id,
                              orderType=ProtoOAOrderType.MARKET, tradeSide=ProtoOATradeSide.Value(order.side),
                              volume=order.volume, clientOrderId=broker_client_order_id(order.request_id), label="xauusd-demo")


def build_reconcile_request(account_id: int) -> Any:
    try:
        from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOAReconcileReq
    except ModuleNotFoundError:
        return {"type": "ProtoOAReconcileReq", "ctidTraderAccountId": account_id}
    return ProtoOAReconcileReq(ctidTraderAccountId=account_id)


def _safe_response(response: Any) -> dict[str, Any]:
    """Persist a minimal non-secret receipt, not arbitrary transport objects."""
    if isinstance(response, dict):
        return {key: value for key, value in response.items()
                if key in {"order_id", "position_id", "status", "error_code"}}
    return {"status": type(response).__name__}


def _reconciliation_details(response: Any) -> dict[str, Any]:
    if not isinstance(response, dict):
        raise CTraderDemoSafetyError("reconciliation response must be structured")
    account_id = response.get("account_id")
    is_demo = response.get("is_demo")
    symbol = response.get("symbol")
    symbol_id = response.get("symbol_id")
    if (not isinstance(account_id, int) or not isinstance(is_demo, bool) or
            not isinstance(symbol, str) or not isinstance(symbol_id, int)):
        raise CTraderDemoSafetyError("reconciliation response lacks verified account or symbol identity")
    outcomes = response.get("request_outcomes", {})
    if not isinstance(outcomes, dict) or any(not isinstance(key, str) or not isinstance(value, dict) for key, value in outcomes.items()):
        raise CTraderDemoSafetyError("reconciliation request outcomes must be structured")
    return {"account_id": account_id, "is_demo": is_demo, "symbol": symbol,
            "symbol_id": symbol_id, "request_outcomes": outcomes}
