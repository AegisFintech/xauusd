"""Session weeks follow New York time; completion is explicit, never inferred from a pandas label."""
from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from xauusd.paper_trading import market_is_open
from xauusd.session_calendar import week_bounds, weekly_bars

UTC = timezone.utc


def at(text):
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def session_bars(start, end, skip=()):
    """Synthetic M1 bars stamped at bar open, only while the session gate is open."""
    minutes = pd.date_range(start, end, freq='min', inclusive='left', tz='UTC')
    minutes = [minute for minute in minutes if market_is_open(minute.to_pydatetime())
               and not any(lo <= minute < hi for lo, hi in skip)]
    index = pd.DatetimeIndex(minutes, name='timestamp')
    values = pd.Series(range(len(index)), index=index, dtype=float) + 2000
    return pd.DataFrame({'open': values, 'high': values + 1, 'low': values - 1, 'close': values + .5,
                         'volume': 1.0}, index=index)


@pytest.mark.parametrize('moment,week_id,opened,closed', [
    ('2026-09-23T10:00:00', '2026-09-25', '2026-09-20T22:00:00', '2026-09-25T21:00:00'),  # daylight time
    ('2026-12-02T10:00:00', '2026-12-04', '2026-11-29T23:00:00', '2026-12-04T22:00:00'),  # standard time
    ('2026-10-31T12:00:00', '2026-10-30', '2026-10-25T22:00:00', '2026-10-30T21:00:00'),  # weekend gap
    ('2026-11-01T22:59:00', '2026-10-30', '2026-10-25T22:00:00', '2026-10-30T21:00:00'),  # Sun 17:59 EST
    ('2026-11-01T23:00:00', '2026-11-06', '2026-11-01T23:00:00', '2026-11-06T22:00:00'),  # DST ended
    ('2027-03-14T22:00:00', '2027-03-19', '2027-03-14T22:00:00', '2027-03-19T21:00:00'),  # DST started
    ('2027-03-14T21:30:00', '2027-03-12', '2027-03-07T23:00:00', '2027-03-12T22:00:00'),
])
def test_week_bounds_follow_the_new_york_session(moment, week_id, opened, closed):
    bounds = week_bounds(at(moment))
    assert (bounds['week_id'], bounds['open'], bounds['close']) == (week_id, at(opened), at(closed))
    assert bounds['next_open'] - bounds['open'] in (timedelta(days=7), timedelta(days=7, hours=1),
                                                    timedelta(days=7, hours=-1))
    assert not market_is_open(bounds['close']) and market_is_open(bounds['open'])
    with pytest.raises(ValueError):
        week_bounds(datetime(2026, 9, 23, 10))


def test_weekly_bars_mark_complete_in_progress_and_partial_weeks():
    # Data starts Monday of the week closing 2026-10-23, spans the week that ends DST, and stops mid-week.
    bars = session_bars('2026-10-19T12:00', '2026-11-04T15:00')
    weeks = weekly_bars(bars)
    assert list(weeks.index) == ['2026-10-23', '2026-10-30', '2026-11-06']
    assert list(weeks['status']) == ['partial_start', 'complete', 'in_progress']
    assert list(weeks['complete']) == [False, True, False]
    dst_week = weeks.loc['2026-11-06']
    assert dst_week['week_open'] == pd.Timestamp('2026-11-01T23:00', tz='UTC')
    assert dst_week['week_close'] == pd.Timestamp('2026-11-06T22:00', tz='UTC')
    full = weeks.loc['2026-10-30']
    assert full['first_bar'] == pd.Timestamp('2026-10-25T22:00', tz='UTC')
    assert full['last_bar'] == pd.Timestamp('2026-10-30T20:59', tz='UTC')
    in_week = bars.loc['2026-10-25T22:00':'2026-10-30T20:59']
    assert full['bars'] == len(in_week) and full['open'] == in_week['open'].iloc[0]
    assert full['close'] == in_week['close'].iloc[-1] and full['high'] == in_week['high'].max()
    # Once the Friday close has passed the in-progress week completes; an explicit cutoff agrees.
    assert weekly_bars(session_bars('2026-10-25T21:00', '2026-11-07T00:00'))['status'].tolist() == ['complete', 'complete']
    assert weekly_bars(bars, as_of=at('2026-11-04T15:00:00'))['status'].iloc[-1] == 'in_progress'


def test_a_week_whose_data_stops_early_is_not_complete():
    bars = session_bars('2026-09-20T21:00', '2026-09-26T00:00', skip=[(at('2026-09-25T17:00:00'), at('2026-09-25T21:00:00'))])
    week = weekly_bars(bars, as_of=at('2026-09-26T00:00:00')).iloc[0]
    assert week['status'] == 'incomplete_data' and not week['complete']
    assert week['last_bar'] == pd.Timestamp('2026-09-25T16:59', tz='UTC')


def test_pandas_weekly_labels_disagree_with_session_weeks():
    bars = session_bars('2026-09-20T21:00', '2026-10-03T00:00')
    session = weekly_bars(bars)
    naive = bars['close'].resample('W-SUN').last()
    # Sunday-evening bars open the next session week but fall in the week *ending* that Sunday for pandas.
    assert len(naive) == 3 and len(session) == 2
    assert list(session['complete']) == [True, True]


def test_bars_after_the_cutoff_are_refused_and_naive_indexes_rejected():
    bars = session_bars('2026-09-21T12:00', '2026-09-21T13:00')
    with pytest.raises(ValueError, match='beyond as_of'):
        weekly_bars(bars, as_of=at('2026-09-21T12:30:00'))
    with pytest.raises(ValueError, match='timezone-aware'):
        weekly_bars(bars.tz_localize(None))
    assert weekly_bars(bars.iloc[:0]).empty
