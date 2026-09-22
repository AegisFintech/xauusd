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


def transition_at(timestamp):
    """Signal generator emitting one SELL transition at an absolute bar time.

    The transition only exists once that bar is persisted: assigning to a label
    outside the index would silently append a phantom bar to the series.
    """
    stamp = pd.Timestamp(timestamp, tz="UTC")

    def generate(features, spec):
        values = pd.Series(0, index=features.index, dtype=int)
        if stamp in values.index:
            values.loc[stamp] = -1
        return values
    return generate


def append_bars(store, times):
    # Bars need a real range: build_features drops any row where high == low,
    # because body_fraction and range_ratio divide by it.
    index = pd.DatetimeIndex([pd.Timestamp(time, tz="UTC") for time in times], name="timestamp", tz="UTC")
    count = len(index)
    bars = pd.DataFrame({"open": [180.0] * count, "high": [181.0] * count, "low": [179.0] * count,
                         "close": [180.5] * count, "volume": [1] * count}, index=index)
    store.write(bars, merge=True)


def newest_market(store):
    return MarketData(200.0, store.read().index[-1].to_pydatetime())


def test_canary_cold_start_ignores_a_transition_it_never_observed(tmp_path):
    store = store_with_bars(tmp_path)  # 10:00 .. 11:19 UTC
    source = ConfirmedBreakoutCanarySource(store, 1, signal_generator=transition_at("2026-09-17 11:17"))

    assert source.read(newest_market(store)) is None


def test_canary_recovers_a_transition_on_a_bar_the_consumer_skipped(tmp_path):
    store = store_with_bars(tmp_path)
    source = ConfirmedBreakoutCanarySource(store, 1, signal_generator=transition_at("2026-09-17 11:20"))
    assert source.read(newest_market(store)) is None  # 11:20 not persisted yet

    append_bars(store, ["2026-09-17 11:20", "2026-09-17 11:21"])  # two bars arrive between reads

    decision = source.read(newest_market(store))

    # Reading only the newest bar would see 11:21 (no change) and lose the signal.
    assert decision is not None
    assert decision.side == "SELL"
    assert decision.market_data_at == pd.Timestamp("2026-09-17 11:20", tz="UTC").to_pydatetime()


def test_canary_drops_a_transition_beyond_the_backlog_bound(tmp_path):
    store = store_with_bars(tmp_path)
    source = ConfirmedBreakoutCanarySource(store, 1, signal_generator=transition_at("2026-09-17 11:20"))
    assert source.read(newest_market(store)) is None

    append_bars(store, ["2026-09-17 11:20", "2026-09-17 11:21", "2026-09-17 11:22"])

    assert source.read(newest_market(store)) is None


def test_canary_emits_each_transition_once(tmp_path):
    store = store_with_bars(tmp_path)
    source = ConfirmedBreakoutCanarySource(store, 1, signal_generator=transition_at("2026-09-17 11:20"))
    assert source.read(newest_market(store)) is None

    append_bars(store, ["2026-09-17 11:20"])

    assert source.read(newest_market(store)) is not None
    assert source.read(newest_market(store)) is None
