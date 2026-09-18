from datetime import timezone

import pandas as pd

from xauusd.canary_strategy import ConfirmedBreakoutCanarySource, LocalHistoricalMarketDataSource
from xauusd.data import DataConfig, HistoricalDataStore
from xauusd.demo_runner import MarketData


def store_with_bars(tmp_path):
    index = pd.date_range("2026-09-17 10:00", periods=80, freq="min", tz="UTC")
    bars = pd.DataFrame({"open": range(100, 180), "high": range(101, 181), "low": range(99, 179),
                         "close": range(100, 180), "volume": [1] * 80}, index=index)
    store = HistoricalDataStore(DataConfig(processed_dir=tmp_path))
    store.write(bars)
    return store


def test_local_historical_market_source_reads_final_close_and_utc_time(tmp_path):
    store = store_with_bars(tmp_path)

    observation = LocalHistoricalMarketDataSource(store).read()

    assert observation.price == 179.0
    assert observation.observed_at == store.read().index[-1].to_pydatetime()
    assert observation.observed_at.tzinfo == timezone.utc


def test_canary_ignores_neutral_and_persistent_signals(tmp_path):
    store = store_with_bars(tmp_path)
    market = MarketData(179.0, store.read().index[-1].to_pydatetime())

    for signals in ([0, 0], [1, 1]):
        source = ConfirmedBreakoutCanarySource(
            store, 0.5,
            signal_generator=lambda features, spec, signals=signals: pd.Series(signals, index=features.index[-2:]),
        )
        assert source.read(market) is None


def test_canary_transition_has_stable_identity_and_side(tmp_path):
    store = store_with_bars(tmp_path)
    market = MarketData(179.0, store.read().index[-1].to_pydatetime())
    generator = lambda features, spec: pd.Series([0, -1], index=features.index[-2:])

    first = ConfirmedBreakoutCanarySource(store, 2, signal_generator=generator).read(market)
    second = ConfirmedBreakoutCanarySource(store, 2, signal_generator=generator).read(market)

    assert first is not None
    assert first.side == "SELL"
    assert first.decision_id == second.decision_id
    assert first.market_data_at == store.read().index[-1].to_pydatetime()
