from datetime import datetime, timedelta, timezone
import sqlite3
from types import SimpleNamespace

import pytest
from ctrader_open_api.messages.OpenApiMessages_pb2 import ProtoOASpotEvent

NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)


def test_real_protobuf_two_sided_prices_and_source_time(tmp_path):
    from xauusd.quotes import record_spot, read_quote
    event = ProtoOASpotEvent(ctidTraderAccountId=1, symbolId=2, bid=270000000, ask=270025000,
                             timestamp=int((NOW-timedelta(seconds=2)).timestamp()*1000))
    path = tmp_path/'quote.json'
    result = record_spot(event, 2, NOW, path=path, history_path=tmp_path/'quotes.db')
    assert result['bid'] == 2700
    assert result['ask'] == 2700.25
    assert result['spread'] == .25
    assert result['observed_at'] != result['received_at']
    assert read_quote(path) == result


def test_optional_proto_presence_never_combines_sides(tmp_path):
    from xauusd.quotes import record_spot, read_quote
    path = tmp_path/'quote.json'
    kwargs = {'path': path, 'history_path': tmp_path/'quotes.db'}
    first = ProtoOASpotEvent(ctidTraderAccountId=1, symbolId=2, bid=270000000, ask=270025000)
    record_spot(first, 2, NOW, **kwargs)
    assert record_spot(ProtoOASpotEvent(ctidTraderAccountId=1, symbolId=2, bid=270010000), 2,
                       NOW+timedelta(seconds=5), **kwargs) is None
    assert read_quote(path)['received_at'] == NOW.isoformat()
    assert read_quote(path)['observed_at'] is None


@pytest.mark.parametrize('bid,ask', [(0, 100), (101, 100), (float('nan'), 200), (100, float('inf')), (True, 100)])
def test_invalid_quotes_do_not_persist(tmp_path, bid, ask):
    from xauusd.quotes import record_spot
    payload = SimpleNamespace(symbolId=2, bid=bid, ask=ask)
    assert record_spot(payload, 2, NOW, path=tmp_path/'q', history_path=tmp_path/'db') is None
    assert not (tmp_path/'q').exists()


def test_wrong_symbol_and_out_of_order_quote_refused(tmp_path):
    from xauusd.quotes import record_spot, read_quote
    kwargs = {'path': tmp_path/'q', 'history_path': tmp_path/'db'}
    event = SimpleNamespace(symbolId=2, bid=270000000, ask=270025000, timestamp=int(NOW.timestamp()*1000))
    assert record_spot(event, 3, NOW, **kwargs) is None
    record_spot(event, 2, NOW, **kwargs)
    event.timestamp -= 5000
    assert record_spot(event, 2, NOW+timedelta(seconds=1), **kwargs) is None
    assert read_quote(kwargs['path'])['received_at'] == NOW.isoformat()


def test_sample_once_second_history_retention_and_hard_bound(tmp_path, monkeypatch):
    from xauusd import quotes
    monkeypatch.setattr(quotes, 'MAX_HISTORY_ROWS', 3)
    kwargs = {'path': tmp_path/'q', 'history_path': tmp_path/'db'}
    event = SimpleNamespace(symbolId=2, bid=270000000, ask=270025000)
    for i in range(6):
        quotes.record_spot(event, 2, NOW+timedelta(seconds=i), **kwargs)
    quotes.record_spot(event, 2, NOW+timedelta(seconds=5,microseconds=500000), **kwargs)
    with sqlite3.connect(kwargs['history_path']) as db:
        assert db.execute('select count(*) from quotes').fetchone()[0] == 3
    quotes.record_spot(event, 2, NOW+timedelta(days=8), **kwargs)
    with sqlite3.connect(kwargs['history_path']) as db:
        assert db.execute('select count(*) from quotes').fetchone()[0] == 1


def test_corrupt_quote_is_unavailable_not_trusted(tmp_path):
    from xauusd.quotes import read_quote
    path = tmp_path/'q'
    path.write_text('{"bid": 12}')
    assert read_quote(path) == {}


def test_feed_matches_account_and_symbol_before_recording(monkeypatch):
    from xauusd import quotes
    from xauusd.live_feed import LiveBarFeed
    calls = []
    monkeypatch.setattr(quotes, 'record_spot', lambda *args: calls.append(args))
    feed = LiveBarFeed.__new__(LiveBarFeed)
    feed._discovered = {'account_id': 1, 'symbol_id': 2}
    feed.now = lambda: NOW
    feed._note = lambda *args: None
    feed._record_quote(ProtoOASpotEvent(ctidTraderAccountId=9, symbolId=2, bid=100, ask=200))
    feed._record_quote(ProtoOASpotEvent(ctidTraderAccountId=1, symbolId=9, bid=100, ask=200))
    assert not calls
    feed._record_quote(ProtoOASpotEvent(ctidTraderAccountId=1, symbolId=2, bid=100, ask=200))
    assert len(calls) == 1
    assert calls[0][1:] == (2, NOW)
