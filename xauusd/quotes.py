"""Bounded, two-sided demo spot observations, independent from application state.

Wire units and optional fields: https://help.ctrader.com/open-api/messages/#protoaspotevent
Bid/ask are unsigned integers in 1/100000 price units. A one-sided update
never refreshes either side of the persisted quote. Latest snapshots and history
are sampled at most once per receipt second; history retains at most seven days.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sqlite3

from .atomic import atomic_write_json, file_lock

MAX_HISTORY_ROWS = 604800
RETENTION_SECONDS = 7 * 86400
QUOTE_PATH = 'reports/quote_status.json'
HISTORY_PATH = 'data/quotes.sqlite'


def _present(payload, field):
    has = getattr(payload, 'HasField', None)
    if callable(has):
        try:
            return has(field)
        except (ValueError, TypeError):
            return False
    return hasattr(payload, field) and getattr(payload, field) is not None


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _datetime(value):
    moment = datetime.fromisoformat(value)
    if moment.tzinfo is None:
        raise ValueError('naive quote time')
    return moment.astimezone(timezone.utc)


def read_quote(path=None):
    """Return a validated observation, or an empty object on missing/corrupt data.

    Freshness is deliberately not inferred here: consumers must check both source
    and receipt times against their injected clock before using a quote.
    """
    try:
        value = json.loads(Path(path or os.getenv('QUOTE_STATUS_PATH', QUOTE_PATH)).read_text())
        if not isinstance(value, dict) or value.get('symbol') != 'XAUUSD' or value.get('source') != 'ctrader_demo':
            return {}
        bid, ask, spread = (value.get(k) for k in ('bid', 'ask', 'spread'))
        if not all(_finite(v) for v in (bid, ask, spread)) or bid <= 0 or ask < bid:
            return {}
        if not math.isclose(spread, ask-bid, abs_tol=1e-8):
            return {}
        _datetime(value['received_at'])
        if value.get('observed_at') is not None:
            _datetime(value['observed_at'])
        return value
    except (OSError, ValueError, TypeError, KeyError, OverflowError):
        return {}


def record_spot(payload, symbol_id, now, *, path=None, history_path=None):
    """Persist one complete quote. Return None for invalid/partial/older frames.

    The caller must match the authenticated demo account before invoking this
    decoder. No broker connection or trading side effect exists in this module.
    """
    if not _present(payload, 'symbolId') or getattr(payload, 'symbolId') != symbol_id:
        return None
    if not all(_present(payload, k) for k in ('bid', 'ask')):
        return None
    bid, ask = payload.bid, payload.ask
    if not all(_finite(v) and v > 0 and float(v).is_integer() for v in (bid, ask)) or ask < bid:
        return None
    if not isinstance(now, datetime) or now.tzinfo is None:
        return None
    received = now.astimezone(timezone.utc)
    observed = None
    if _present(payload, 'timestamp'):
        timestamp = payload.timestamp
        if not _finite(timestamp) or timestamp <= 0:
            return None
        try:
            observed = datetime.fromtimestamp(timestamp/1000, timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
        # Clock skew must not turn a future frame into fresh execution evidence.
        if observed > received:
            return None
    quote = {'bid': bid/100000, 'ask': ask/100000, 'spread': (ask-bid)/100000,
             'observed_at': observed.isoformat() if observed else None,
             'received_at': received.isoformat(), 'symbol': 'XAUUSD', 'source': 'ctrader_demo'}
    target = Path(path or os.getenv('QUOTE_STATUS_PATH', QUOTE_PATH))
    history = Path(history_path or os.getenv('QUOTE_HISTORY_PATH', HISTORY_PATH))
    with file_lock(target):
        previous = read_quote(target)
        if previous:
            prior_receipt = _datetime(previous['received_at'])
            if int(received.timestamp()) <= int(prior_receipt.timestamp()):
                return None
            prior_source = previous.get('observed_at')
            if observed and prior_source and observed <= _datetime(prior_source):
                return None
        history.parent.mkdir(parents=True, exist_ok=True)
        second = int(received.timestamp())
        # Distinct seconds plus the time window give a hard bound without a
        # full-table COUNT/OFFSET scan on every incoming frame.
        cutoff = second - min(MAX_HISTORY_ROWS, RETENTION_SECONDS) + 1
        with sqlite3.connect(history, timeout=2) as db:
            db.execute('CREATE TABLE IF NOT EXISTS quotes (received_second INTEGER PRIMARY KEY, '
                       'observed_at TEXT, received_at TEXT NOT NULL, bid REAL NOT NULL, '
                       'ask REAL NOT NULL, spread REAL NOT NULL)')
            db.execute('INSERT OR IGNORE INTO quotes VALUES (?,?,?,?,?,?)',
                       (second, quote['observed_at'], quote['received_at'], quote['bid'], quote['ask'], quote['spread']))
            db.execute('DELETE FROM quotes WHERE received_second < ? OR received_second > ?', (cutoff, second))
        atomic_write_json(target, quote)
    return quote
