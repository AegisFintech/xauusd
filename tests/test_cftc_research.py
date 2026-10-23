"""The preregistered CFTC study: point-in-time discipline, session weeks, fail-closed writes."""
import json
from datetime import date

import pandas as pd
import pytest

from xauusd.cftc_research import (ACCEPTANCE_MINIMUM_TRADES, AS_OF_COLUMN, CftcStudyConfig,
                                  MIN_COMPLETE_WEEK_BARS, NC_LONG_COLUMN, NC_SHORT_COLUMN,
                                  OPEN_INTEREST_COLUMN, build_signals, build_trades,
                                  complete_weeks, derive_release, enumerate_observations,
                                  load_observations, run, weekly_session_bars, week_key)


def _tuesdays(count, start=date(2020, 1, 7)):
    return [(pd.Timestamp(start) + pd.Timedelta(weeks=step)).date() for step in range(count)]


def _cot_csv(tmp_path, as_of_dates):
    frame = pd.DataFrame({
        AS_OF_COLUMN: [value.isoformat() for value in as_of_dates],
        OPEN_INTEREST_COLUMN: [1000 + step for step in range(len(as_of_dates))],
        NC_LONG_COLUMN: [100 + step * 3 for step in range(len(as_of_dates))],
        NC_SHORT_COLUMN: [50 + step for step in range(len(as_of_dates))],
    })
    path = tmp_path / "cot.csv"
    frame.to_csv(path, index=False)
    return path


def _week_of_bars(start="2020-01-05 18:00", periods=7000, unit="us"):
    """One complete session week: Sunday 18:00 ET open through Friday.

    Microsecond resolution is the default here on purpose -- that is what the real
    store's index carries, and assuming nanoseconds is a silent-failure bug.
    """
    index = pd.date_range(start, periods=periods, freq="min", tz="America/New_York").as_unit(unit)
    return pd.Series(range(periods), index=index, dtype="float64", name="close")


def test_a_release_friday_that_is_a_federal_holiday_is_unverifiable():
    """2022-11-11 was Veterans Day, so the CFTC was closed and the release moved.

    No captured source states where it moved to, so it must be excluded rather than
    assumed -- which is what the fail-closed check demands.
    """
    release, basis = derive_release(date(2022, 11, 8))

    assert release == date(2022, 11, 11)
    assert basis == "unverifiable_federal_holiday"


def test_an_ordinary_tuesday_releases_on_the_following_friday():
    release, basis = derive_release(date(2021, 3, 9))

    assert (release, basis) == (date(2021, 3, 12), "official_rule_friday")


def test_a_dated_special_announcement_overrides_the_friday_rule():
    """Juneteenth 2021 moved the Friday 6/18 release to Monday 6/21."""
    release, basis = derive_release(date(2021, 6, 15))

    assert (release, basis) == (date(2021, 6, 21), "special_announcement")


def test_the_shutdown_catchup_range_is_excluded_even_though_its_release_year_is_not_2025(tmp_path):
    """The leak the year-based exclusion misses.

    The preregistration excludes release year 2025, but the appropriations-lapse
    backlog ran into January 2026, so an as-of 2025-12-30 observation releases
    2026-01-02 and would slip through. The assessment states a bare Friday rule is
    wrong for every report from 2025-10-03 to 2026-01-16; admitting one would be
    exactly the look-ahead the amendment exists to prevent.
    """
    path = _cot_csv(tmp_path, [date(2025, 12, 30)])
    config = CftcStudyConfig(cot_csv=path, store_path=tmp_path / "unused.parquet")
    enumeration = enumerate_observations(load_observations(config))

    row = enumeration["excluded"][0]
    assert row["release"] == "2026-01-02"
    assert "unverifiable_shutdown_catchup_2025-10-03_to_2026-01-16" in row["exclusion_reasons"]
    assert row["available_at"] is None
    assert enumeration["eligible"] == []


def test_excluded_observations_never_carry_an_availability_timestamp(tmp_path):
    """An availability stamp is what lets an observation reach a threshold."""
    dates = _tuesdays(60) + [date(2022, 11, 8), date(2023, 3, 7), date(2025, 12, 30)]
    path = _cot_csv(tmp_path, sorted(dates))
    config = CftcStudyConfig(cot_csv=path, store_path=tmp_path / "unused.parquet")
    enumeration = enumerate_observations(load_observations(config))

    assert all(row["available_at"] for row in enumeration["eligible"])
    assert all(row["available_at"] is None for row in enumeration["excluded"])
    reasons = {row["release"]: row["exclusion_reasons"] for row in enumeration["excluded"]}
    assert "unverifiable_federal_holiday" in reasons["2022-11-11"]
    assert "prereg_excluded_release_year_2023" in reasons["2023-03-10"]
    assert "unverifiable_shutdown_catchup_2025-10-03_to_2026-01-16" in reasons["2026-01-02"]
    # The 60-Tuesday series contains its own holiday Fridays, which is the point:
    # they are excluded by derivation, not by a remembered count.
    assert "unverifiable_federal_holiday" in reasons["2020-12-25"]


def test_availability_resolves_dst_per_date(tmp_path):
    """15:30 New York is 20:30 UTC in winter and 19:30 UTC under daylight time.

    The offset has to be derived per date; hard-coding either one puts every
    observation an hour early or an hour late for half the sample.
    """
    path = _cot_csv(tmp_path, [date(2020, 1, 7), date(2020, 7, 7)])
    config = CftcStudyConfig(cot_csv=path, store_path=tmp_path / "unused.parquet")
    by_release = {row["release"]: row["available_at"]
                  for row in enumerate_observations(load_observations(config))["eligible"]}

    assert by_release["2020-01-10"].endswith("-05:00")
    assert by_release["2020-07-10"].endswith("-04:00")
    assert pd.Timestamp(by_release["2020-01-10"]).hour == 15
    assert pd.Timestamp(by_release["2020-07-10"]).hour == 15


def test_signals_need_fifty_two_priors_and_order_by_availability(tmp_path):
    dates = _tuesdays(60)
    path = _cot_csv(tmp_path, dates)
    config = CftcStudyConfig(cot_csv=path, store_path=tmp_path / "unused.parquet")
    observations = load_observations(config)
    enumeration = enumerate_observations(observations)

    signals, past_warmup, _ = build_signals(enumeration["eligible"], observations)

    assert past_warmup == len(enumeration["eligible"]) - 52
    # Every signal must come from an observation that had 52 eligible priors.
    assert all(signal["as_of"] >= dates[52].isoformat() for signal in signals)
    assert [signal["available_at"] for signal in signals] == sorted(
        signal["available_at"] for signal in signals)


def test_an_excluded_observation_cannot_change_any_signal(tmp_path):
    """The fail-closed check the artifact claims, verified instead of asserted.

    Taking the first difference over the full series lets an excluded observation's
    net position leak into the flow of the eligible observation that follows it. The
    only place that can happen is an excluded observation with an eligible successor,
    so that is the one poisoned here: corrupting it must change nothing.
    """
    dates = _tuesdays(170, start=date(2022, 1, 4))   # spans 2023, which is excluded wholesale
    clean = _cot_csv(tmp_path, dates)
    config = CftcStudyConfig(cot_csv=clean, store_path=tmp_path / "unused.parquet")
    observations = load_observations(config)
    enumeration = enumerate_observations(observations)
    baseline = build_signals(enumeration["eligible"], observations)

    excluded_dates = {row["as_of"] for row in enumeration["excluded"]}
    ordered = sorted(value.isoformat() for value in observations["as_of"])
    target = next((previous for previous, current in zip(ordered, ordered[1:])
                   if previous in excluded_dates and current not in excluded_dates), None)
    assert target, "the fixture must contain an excluded observation before an eligible one"

    frame = pd.read_csv(clean)
    row = frame.index[frame[AS_OF_COLUMN] == target][0]
    frame.loc[row, NC_LONG_COLUMN] = 999_999
    frame.loc[row, NC_SHORT_COLUMN] = 0
    poisoned = tmp_path / "poisoned.csv"
    frame.to_csv(poisoned, index=False)
    contaminated_observations = load_observations(
        CftcStudyConfig(cot_csv=poisoned, store_path=tmp_path / "unused.parquet"))

    contaminated = build_signals(enumerate_observations(contaminated_observations)["eligible"],
                                 contaminated_observations)

    assert contaminated == baseline


def test_flow_gaps_left_by_exclusions_are_counted_not_hidden(tmp_path):
    """Excluding 2023 and 2025 wholesale means some flows span a gap; report how many.

    A difference across an excluded year is not a one-week flow, so the count is
    measured and published as a limitation rather than left implicit in a number.
    """
    path = _cot_csv(tmp_path, _tuesdays(170, start=date(2022, 1, 4)))
    config = CftcStudyConfig(cot_csv=path, store_path=tmp_path / "unused.parquet")
    observations = load_observations(config)
    enumeration = enumerate_observations(observations)

    _, past_warmup, gap_spanning = build_signals(enumeration["eligible"], observations)

    assert enumeration["summary"]["excluded"] > 0
    assert gap_spanning > 0
    assert past_warmup == len(enumeration["eligible"]) - 52


def test_microsecond_index_does_not_collapse_session_weeks():
    """`asi8` returns the index's own unit; `pd.to_datetime` assumes nanoseconds.

    The real store's index is microsecond-resolution, so trusting nanoseconds put
    every bar in 1969 and made every session week look like it opened on a
    Wednesday. That reported `complete_session_weeks: 0` instead of raising.
    """
    weeks = weekly_session_bars(_week_of_bars(unit="us"))

    assert len(weeks) == 1
    row = weeks.iloc[0]
    assert row["first_weekday"] == 6, "a session week opens on Sunday"
    assert row["last_weekday"] == 4, "and closes on Friday"
    assert row["first_ts"].year == 2020
    assert row["bars"] == 7000


def test_complete_weeks_rejects_a_partial_week():
    stub = _week_of_bars(periods=1200)  # under a day
    weeks = weekly_session_bars(stub)

    assert len(weeks) == 1
    assert weeks.iloc[0]["bars"] < MIN_COMPLETE_WEEK_BARS
    assert complete_weeks(weeks).empty


def test_week_key_puts_friday_afternoon_and_sunday_evening_in_the_same_week():
    friday = pd.Timestamp("2020-01-10 16:00", tz="America/New_York")
    sunday_open = pd.Timestamp("2020-01-05 18:30", tz="America/New_York")
    before_open = pd.Timestamp("2020-01-05 17:00", tz="America/New_York")

    assert week_key(friday) == week_key(sunday_open) == pd.Timestamp("2020-01-05")
    # Sunday before the 18:00 open still belongs to the previous session week.
    assert week_key(before_open) == pd.Timestamp("2019-12-29")


def test_trades_skip_a_signal_with_no_following_complete_week():
    weeks = weekly_session_bars(_week_of_bars())
    complete = complete_weeks(weeks)
    signals = [{"as_of": "2020-01-07", "side": "long", "scaled_flow": 1.0, "upper": 0.0,
                "lower": 0.0, "available_at": "2020-01-10T20:30:00-05:00"}]

    assert build_trades(signals, complete) == []


def _prereg(tmp_path, evidence_sha="0" * 64):
    evidence = tmp_path / "evidence.json"
    evidence.write_text("{}")
    path = tmp_path / "prereg.json"
    path.write_text(json.dumps({
        "title": "test study", "hypothesis": "h", "status": "preregistered_not_tested",
        "acceptance": "a", "invalidation": "i", "trade_permission": "None.",
        "signal_definition": "s", "entry_exit": "e",
        "point_in_time_amendment": {"availability_rule": "r", "registered_at_utc": "2026-01-01T00:00:00+00:00"},
        "point_in_time_evidence": [{"path": str(evidence), "sha256": evidence_sha}],
    }))
    return path


def test_run_refuses_to_write_when_evidence_no_longer_matches(tmp_path):
    """A result file that fails its own checks is worse than no file: it looks like evidence."""
    store = tmp_path / "bars.parquet"
    _week_of_bars().to_frame().to_parquet(store)
    config = CftcStudyConfig(cot_csv=_cot_csv(tmp_path, _tuesdays(60)), store_path=store,
                             prereg_path=_prereg(tmp_path), output_dir=tmp_path)

    with pytest.raises(ValueError, match="evidence mismatch"):
        run(config, write=True)

    assert list(tmp_path.glob("*result*.json")) == []


def test_run_writes_a_rejection_without_computing_returns(tmp_path):
    """Sixty observations cannot reach the 100-trade minimum, and that alone rejects.

    No expectancy is computed, so there is no number to over-fit against -- which is
    what `costs_and_validation` forbids after results are observed.
    """
    store = tmp_path / "bars.parquet"
    _week_of_bars().to_frame().to_parquet(store)
    evidence = tmp_path / "evidence.json"
    evidence.write_text("{}")
    import hashlib
    config = CftcStudyConfig(
        cot_csv=_cot_csv(tmp_path, _tuesdays(60)), store_path=store,
        prereg_path=_prereg(tmp_path, hashlib.sha256(b"{}").hexdigest()), output_dir=tmp_path)

    result = run(config, write=True)

    assert result["verdict"] == "rejected_insufficient_complete_trades"
    assert result["passes_validation"] is False
    assert result["execution"]["complete_trades"] < ACCEPTANCE_MINIMUM_TRADES
    assert result["results_usd_per_oz"] is None
    assert result["results_not_computed_because"]
    assert all(check is True for check in result["fail_closed_checks"].values())
    written = list(tmp_path.glob("*result*.json"))
    assert len(written) == 1
    assert json.loads(written[0].read_text())["verdict"] == result["verdict"]
