"""New York trading-week boundaries for research aggregation (never a trading gate).

The XAUUSD week opens Sunday 18:00 and closes Friday 17:00 New York time, the same
session that ``paper_trading.market_is_open`` enforces, so its UTC boundaries move
with US daylight time. A pandas weekly label (``resample('W')``) neither starts at
the session open nor proves that a week completed. ``weekly_bars`` assigns M1 bars
to session weeks and states for every week whether it is complete or partial.

Exchange holidays and early closes are not modelled: a week whose data stops early
is reported as ``incomplete_data``, never silently as complete.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

import pandas as pd

from .paper_trading import BAR_INTERVAL_SECONDS, NEW_YORK, NEW_YORK_CLOSE_HOUR, NEW_YORK_REOPEN_HOUR

WEEK_STATUSES = ("complete", "in_progress", "incomplete_data", "partial_start")
DEFAULT_EDGE_TOLERANCE = timedelta(minutes=10)
_BAR = pd.Timedelta(seconds=BAR_INTERVAL_SECONDS)
_OPEN_TO_CLOSE = pd.Timedelta(days=4, hours=NEW_YORK_CLOSE_HOUR + 24 - NEW_YORK_REOPEN_HOUR)  # Sun 18:00 -> Fri 17:00


def week_bounds(moment: datetime) -> dict:
    """The session week containing ``moment``; the weekend gap belongs to the week that just closed.

    Returns the week ID (the New York date of its Friday close) and UTC open, close and next open.
    """
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("moment must be timezone-aware")
    local = moment.astimezone(NEW_YORK)
    sunday = local.date() - timedelta(days=(local.weekday() + 1) % 7)
    if local < datetime.combine(sunday, time(NEW_YORK_REOPEN_HOUR), NEW_YORK):
        sunday -= timedelta(days=7)
    # 18:00 and 17:00 are never ambiguous New York wall times (DST changes at 02:00).
    opened = datetime.combine(sunday, time(NEW_YORK_REOPEN_HOUR), NEW_YORK)
    closed = datetime.combine(sunday + timedelta(days=5), time(NEW_YORK_CLOSE_HOUR), NEW_YORK)
    reopened = datetime.combine(sunday + timedelta(days=7), time(NEW_YORK_REOPEN_HOUR), NEW_YORK)
    return {"week_id": closed.date().isoformat(), "open": opened.astimezone(timezone.utc),
            "close": closed.astimezone(timezone.utc), "next_open": reopened.astimezone(timezone.utc)}


def _week_open_wall(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Naive New York wall time of each timestamp's session-week open (vectorized week_bounds)."""
    wall = index.tz_convert(NEW_YORK).tz_localize(None)
    sunday = wall.normalize() - pd.to_timedelta((wall.dayofweek + 1) % 7, unit="D")
    opened = sunday + pd.Timedelta(hours=NEW_YORK_REOPEN_HOUR)
    return pd.DatetimeIndex(opened.where(wall >= opened, opened - pd.Timedelta(days=7)))


def weekly_bars(bars: pd.DataFrame, as_of: datetime | None = None,
                tolerance: timedelta = DEFAULT_EDGE_TOLERANCE) -> pd.DataFrame:
    """Aggregate UTC bar-open-stamped M1 OHLCV bars into New York session weeks.

    ``as_of`` is the information cutoff (default: the close of the last bar). Bars after it
    are refused rather than silently used. Each week's ``status`` is ``complete``,
    ``in_progress`` (the cutoff precedes the Friday close), ``incomplete_data`` (the close
    has passed but data stops more than ``tolerance`` early) or ``partial_start`` (data
    begins more than ``tolerance`` after the Sunday open). Only complete weeks are safe
    inputs for rules that assume a finished week.
    """
    columns = ["week_open", "week_close", "first_bar", "last_bar", "bars",
               "open", "high", "low", "close", "volume", "status", "complete"]
    if bars.empty:
        return pd.DataFrame(columns=columns, index=pd.Index([], name="week_id"))
    index = pd.DatetimeIndex(bars.index)
    if index.tz is None:
        raise ValueError("bars need a timezone-aware (UTC) index")
    frame = bars.set_axis(index.tz_convert("UTC")).sort_index()
    index = pd.DatetimeIndex(frame.index)
    last_close = index.max() + _BAR
    cutoff = pd.Timestamp(as_of).tz_convert("UTC") if as_of is not None else last_close
    if last_close > cutoff:
        raise ValueError("bars extend beyond as_of; slice the input to the information cutoff first")
    opened_wall = _week_open_wall(index)
    groups = frame.assign(_opened=opened_wall.values).groupby("_opened", sort=True)
    weeks = groups.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), volume=("volume", "sum"), bars=("close", "size"))
    times = pd.Series(index, index=index).groupby(opened_wall.values)
    week_open_wall = pd.DatetimeIndex(weeks.index)
    weeks["week_open"] = week_open_wall.tz_localize(NEW_YORK).tz_convert("UTC")
    weeks["week_close"] = (week_open_wall + _OPEN_TO_CLOSE).tz_localize(NEW_YORK).tz_convert("UTC")
    weeks["first_bar"], weeks["last_bar"] = times.min(), times.max()  # aligned on the week key; tz kept
    edge = pd.Timedelta(tolerance)
    status = pd.Series("complete", index=weeks.index)
    status[weeks["first_bar"] > weeks["week_open"] + edge] = "partial_start"
    status[weeks["last_bar"] + _BAR < weeks["week_close"] - edge] = "incomplete_data"
    status[cutoff < weeks["week_close"]] = "in_progress"
    weeks["status"], weeks["complete"] = status, status == "complete"
    weeks.index = pd.Index((week_open_wall + _OPEN_TO_CLOSE).strftime("%Y-%m-%d"), name="week_id")
    return weeks[columns]
