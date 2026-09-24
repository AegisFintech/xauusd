from copy import deepcopy
import sqlite3
from contextlib import contextmanager

import pytest

from xauusd.ctrader_demo import (CTraderDemoAccount, CTraderDemoAdapter, CTraderDemoOpenApiConfig,
    CTraderDemoOpenApiTransport, CTraderDemoSafetyError, CockroachCTraderDemoStore,
    InMemoryCTraderDemoStore, OUTCOME_UNKNOWN, verify_position_exposure)

ACCOUNT = CTraderDemoAccount(7, 99)


def record(side="BUY", volume=100, position_id=30, identifier="decision", deal_id=40):
    return {"status": "completed", "request": {"account_id": 7, "symbol_id": 99,
            "side": side, "volume": volume, "broker_client_order_id": identifier},
            "outcome": {"accepted": True, "request_id": identifier, "response": {
                "execution_type": 3, "filled_volume": volume, "position_id": position_id,
                "order_id": 20, "deal_id": deal_id, "broker_client_order_id": identifier}}}


def snapshot(volume=100):
    return {"account_id": 7, "is_demo": True, "symbol": "XAUUSD", "symbol_id": 99,
            "positions": ([{"position_id": 30, "symbol_id": 99, "volume": volume,
                            "side": 1, "position_status": 1}] if volume else []), "open_orders": []}


def test_filled_position_survives_adapter_restart(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    store = InMemoryCTraderDemoStore()
    store.requests["decision"] = record()
    class Transport:
        def send(self, request, timeout_seconds): return snapshot()
    adapter = CTraderDemoAdapter(ACCOUNT, store, Transport(), expected_volume_provider=lambda: 100)
    assert adapter.reconcile_after_restart()
    assert adapter.state()["stopped"]  # reconciliation itself cannot resume


def test_netting_partial_reduction_and_flattening():
    records = {"decision": record(), "sell": record("SELL", 40, identifier="sell", deal_id=41)}
    verify_position_exposure(ACCOUNT, records, snapshot(60), lambda: 60)
    records["close"] = record("SELL", 60, identifier="close", deal_id=42)
    verify_position_exposure(ACCOUNT, records, snapshot(0), lambda: 0)


@pytest.mark.parametrize("case", ["manual", "wrong_volume", "wrong_symbol", "missing_position",
    "paper_mismatch", "pending", "legacy_unknown", "unmapped_fill", "duplicate_position", "open_order"])
def test_unexplained_exposure_never_reconciles(case):
    records, broker, paper = {"decision": record()}, snapshot(), 100
    if case == "manual": records = {}
    if case == "wrong_volume": broker["positions"][0]["volume"] = 50
    if case == "wrong_symbol": broker["positions"][0]["symbol_id"] = 100
    if case == "missing_position": broker["positions"] = []
    if case == "paper_mismatch": paper = 50
    if case == "pending": records["decision"]["status"] = "pending"
    if case == "legacy_unknown": records["decision"]["outcome"] = {"accepted": False, "reason": OUTCOME_UNKNOWN}
    if case == "unmapped_fill": records["decision"]["outcome"]["response"].pop("position_id")
    if case == "duplicate_position": broker["positions"] *= 2
    if case == "open_order": broker["open_orders"] = [{"order_id": 20}]
    with pytest.raises(CTraderDemoSafetyError):
        verify_position_exposure(ACCOUNT, records, broker, lambda: paper)


def test_native_snapshot_preserves_positions_and_checks_account(monkeypatch):
    monkeypatch.setenv("CTRADER_DEMO_ONLY", "true")
    transport = CTraderDemoOpenApiTransport(CTraderDemoOpenApiConfig("id", "secret", "token", 7),
                                          extract=lambda x: x)
    transport._account = ACCOUNT
    message = {"ctidTraderAccountId": 7, "position": [{"positionId": 30, "positionStatus": 1,
               "tradeData": {"symbolId": 99, "tradeSide": 1, "volume": 100}}]}
    result = transport._normalize({"type": "ProtoOAReconcileReq"}, message)
    assert result["positions"] == snapshot()["positions"]
    message["ctidTraderAccountId"] = 8
    with pytest.raises(CTraderDemoSafetyError):
        transport._normalize({"type": "ProtoOAReconcileReq"}, message)


def test_persistent_store_keeps_unknown_pending_and_preserves_fill_mapping(tmp_path):
    # Run production store SQL with a local connection shim; no external DB or broker.
    class Store(CockroachCTraderDemoStore):
        @contextmanager
        def connect(self):
            db = sqlite3.connect(tmp_path / "store.db")
            db.row_factory = sqlite3.Row
            class Connection:
                def execute(self, sql, args=()):
                    return db.execute(sql.replace(" FOR UPDATE", "").replace("BIGSERIAL", "INTEGER"), args)
            try:
                yield Connection()
                db.commit()
            finally:
                db.close()
    store = Store("unused")
    value = record()
    assert store.reserve("decision", value["request"])[0]
    store.finish("decision", {"accepted": False, "reason": OUTCOME_UNKNOWN})
    restarted = Store("unused")
    assert restarted.pending_request_ids() == ["decision"]
    assert not restarted.reserve("decision", value["request"])[0]
    restarted.finish("decision", value["outcome"])
    assert restarted.request_records()["decision"] == value
    assert not restarted.pending_request_ids()
