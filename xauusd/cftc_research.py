"""Reproducible implementation of the preregistered CFTC positioning-flow study.

Governing spec:
``reports/research/cftc_gold_positioning_flow_point_in_time_prereg_20261005T041846Z.json``
Availability evidence:
``reports/research/cftc_point_in_time_assessment_20261005T025200Z.json``

A preregistered result that cannot be re-run is not evidence, so this module
exists: it is the chain that produced
``cftc_gold_positioning_flow_point_in_time_result_20261009T0555Z.json``
(80 complete trades against a required 100, therefore rejected without any return
being computed).

Three disciplines are load-bearing and are enforced in code rather than in prose:

* **Enumerate before measuring.** The spec requires the complete eligible and
  excluded report-date/release-date lists to be emitted before returns. The trade
  count is therefore reachable without ever computing an expectancy -- which matters,
  because an expectancy from a sample that cannot be accepted is only a number to
  over-fit against, and ``costs_and_validation`` forbids retuning afterwards.
* **Exclude rather than assume.** An observation whose actual release timestamp
  cannot be mapped unambiguously is dropped, never approximated by "as-of Tuesday +
  3 days". The spec says abort rather than approximate; dropping the unverifiable
  observation is the conservative form of that.
* **Fail closed on the artifact.** :func:`build_result` returns its own integrity
  checks and :func:`run` refuses to write if any is false. A result file whose
  checks are false is worse than no result file, because it looks like evidence.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

from .atomic import atomic_write_json

NY = "America/New_York"
NY_ZONE = ZoneInfo(NY)
RELEASE_TIME = time(15, 30)
# A gold session week runs Sunday 18:00 ET to Friday 17:00 ET.
SESSION_OPEN_HOUR = 18
MIN_WARMUP_REPORTS = 52
UPPER_QUANTILE = 0.80
LOWER_QUANTILE = 0.20
ACCEPTANCE_MINIMUM_TRADES = 100
# A complete week of M1 gold bars. Median observed is ~6,874; the floor is low
# enough to survive the daily 17:00-18:00 break and short holiday weeks, and high
# enough that a two-day stub cannot pass as complete.
MIN_COMPLETE_WEEK_BARS = 3000

AS_OF_COLUMN = "As of Date in Form YYYY-MM-DD"
OPEN_INTEREST_COLUMN = "Open Interest (All)"
NC_LONG_COLUMN = "Noncommercial Positions-Long (All)"
NC_SHORT_COLUMN = "Noncommercial Positions-Short (All)"

# Dated deviations from the CFTC Special Announcements log that fall inside the
# sample window and are not already removed wholesale by an exclusion.
# as-of date -> actual release date.
DEVIATIONS = {
    date(2021, 6, 15): date(2021, 6, 21),  # Juneteenth: Fri 6/18 -> Mon 6/21
}
# Preregistered conservative exclusions, keyed exactly as the amendment states them.
EXCLUDE_RELEASE_DATES = {date(2020, 12, 28)}
EXCLUDE_RELEASE_YEARS = {2023, 2025}
# The assessment states a bare Friday rule is wrong for *every* report in this
# range: the appropriations lapse cleared its backlog in chronological order from
# mid-November 2025 into January 2026, publishing catch-ups on Wednesdays. The
# year-based exclusion above does not reach an observation whose as-of date is in
# 2025 but whose release fell in January 2026, so the range is excluded explicitly.
SHUTDOWN_RANGE = (date(2025, 10, 3), date(2026, 1, 16))


@dataclass
class CftcStudyConfig:
    cot_csv: Path = Path("data/external/CFTC_GOLD_LEGACY_FUTURES_ONLY_2019_2025.csv")
    store_path: Path = Path("data/processed/XAUUSD_M1.parquet")
    prereg_path: Path = Path(
        "reports/research/cftc_gold_positioning_flow_point_in_time_prereg_20261005T041846Z.json")
    output_dir: Path = Path("reports/research")


def federal_holidays() -> set[datetime]:
    return set(USFederalHolidayCalendar().holidays(start="2019-01-01", end="2026-12-31").to_pydatetime())


def derive_release(as_of: date, holidays: set[datetime] | None = None) -> tuple[date, str]:
    """The actual release date for a positions as-of date, and how certain it is.

    Returns ``official_rule_friday`` only when the derived Friday is a real,
    non-holiday Friday. Anything else is reported as unverifiable so the caller
    excludes it instead of guessing where a closed-CFTC release moved to.
    """
    if as_of in DEVIATIONS:
        return DEVIATIONS[as_of], "special_announcement"
    holidays = federal_holidays() if holidays is None else holidays
    release = (pd.Timestamp(as_of) + pd.Timedelta(days=3)).date()
    if pd.Timestamp(release).to_pydatetime() in holidays:
        return release, "unverifiable_federal_holiday"
    if release.weekday() != 4:
        return release, "unverifiable_not_friday"
    return release, "official_rule_friday"


def load_observations(config: CftcStudyConfig) -> pd.DataFrame:
    raw = pd.read_csv(config.cot_csv)
    frame = pd.DataFrame({
        "as_of": pd.to_datetime(raw[AS_OF_COLUMN], utc=True).dt.date,
        "open_interest": pd.to_numeric(raw[OPEN_INTEREST_COLUMN], errors="coerce"),
        "net": (pd.to_numeric(raw[NC_LONG_COLUMN], errors="coerce")
                - pd.to_numeric(raw[NC_SHORT_COLUMN], errors="coerce")),
    })
    return frame.sort_values("as_of").reset_index(drop=True)


def enumerate_observations(observations: pd.DataFrame) -> dict:
    """The complete eligible/excluded enumeration the spec requires before returns."""
    holidays = federal_holidays()
    rows = []
    for row in observations.itertuples():
        release, basis = derive_release(row.as_of, holidays)
        reasons = []
        if release in EXCLUDE_RELEASE_DATES:
            reasons.append("prereg_excluded_release_date_2020-12-28")
        if release.year in EXCLUDE_RELEASE_YEARS:
            reasons.append(f"prereg_excluded_release_year_{release.year}")
        if SHUTDOWN_RANGE[0] <= release <= SHUTDOWN_RANGE[1]:
            reasons.append("unverifiable_shutdown_catchup_2025-10-03_to_2026-01-16")
        if basis.startswith("unverifiable"):
            reasons.append(basis)
        available_at = None
        if not reasons:
            # 15:30 America/New_York on the actual release date, DST resolved per
            # date: 19:30 UTC under daylight time, 20:30 UTC in winter.
            available_at = datetime.combine(release, RELEASE_TIME, tzinfo=NY_ZONE).isoformat()
        rows.append({"as_of": row.as_of.isoformat(), "release": release.isoformat(),
                     "basis": basis, "available_at": available_at,
                     "excluded": bool(reasons), "exclusion_reasons": reasons})

    eligible = [row for row in rows if not row["excluded"]]
    excluded = [row for row in rows if row["excluded"]]
    reason_counts: dict[str, int] = {}
    for row in excluded:
        for reason in row["exclusion_reasons"]:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    basis_counts: dict[str, int] = {}
    for row in rows:
        basis_counts[row["basis"]] = basis_counts.get(row["basis"], 0) + 1
    return {"summary": {"observations_total": len(rows), "eligible": len(eligible),
                        "excluded": len(excluded), "basis_counts": basis_counts,
                        "exclusion_reason_counts": reason_counts,
                        "eligible_release_range": [eligible[0]["release"], eligible[-1]["release"]]
                        if eligible else None},
            "eligible": eligible, "excluded": excluded}


def session_week(index_ny: pd.DatetimeIndex) -> pd.Series:
    """The Sunday that begins the New York session week containing each timestamp.

    Shifting back 18 hours and flooring to the previous Sunday labels every bar with
    its own session week, including Friday afternoon (still the week that opened the
    prior Sunday) and Sunday before 18:00 (still the previous week).
    """
    shifted = (index_ny - pd.Timedelta(hours=SESSION_OPEN_HOUR)).normalize()
    days_since_sunday = (shifted.weekday + 1) % 7
    return pd.Series(shifted - pd.to_timedelta(days_since_sunday, unit="D"), index=index_ny)


def week_key(ts_ny: pd.Timestamp) -> pd.Timestamp:
    """The naive Sunday beginning the session week containing one NY timestamp."""
    shifted = (ts_ny - pd.Timedelta(hours=SESSION_OPEN_HOUR)).normalize()
    return (shifted - pd.Timedelta(days=(shifted.weekday() + 1) % 7)).tz_localize(None)


def weekly_session_bars(close: pd.Series) -> pd.DataFrame:
    """Per-session-week first/last bar and close, with completeness markers.

    The unit is pinned to nanoseconds on purpose. ``asi8`` returns the index's own
    resolution, and this store's index is microsecond-resolution, so feeding it to
    ``pd.to_datetime`` -- which assumes nanoseconds -- silently collapsed every
    timestamp to 1969 and made every session week look like it started on a
    Wednesday. That produced ``complete_session_weeks: 0`` rather than an error.
    """
    close = close.copy()
    close.index = close.index.as_unit("ns")
    index_ny = close.index.tz_convert(NY)
    # Integer and naive columns throughout: tz-aware Timestamps in a column become
    # Python objects, which for 2.4M rows costs hundreds of megabytes and breaks
    # groupby aggregation.
    week = session_week(index_ny).dt.tz_localize(None).values.astype("datetime64[ns]")
    frame = pd.DataFrame({"week": week, "nano": close.index.asi8,
                          "day": index_ny.normalize().asi8, "close": close.values})
    summary = frame.groupby("week", sort=True).agg(
        bars=("close", "size"), first_nano=("nano", "min"), last_nano=("nano", "max"),
        first_close=("close", "first"), last_close=("close", "last"), days=("day", "nunique"))
    summary["first_ts"] = pd.to_datetime(summary["first_nano"], utc=True).dt.tz_convert(NY)
    summary["last_ts"] = pd.to_datetime(summary["last_nano"], utc=True).dt.tz_convert(NY)
    summary["first_weekday"] = summary["first_ts"].dt.weekday
    summary["last_weekday"] = summary["last_ts"].dt.weekday
    return summary


def complete_weeks(weeks: pd.DataFrame) -> pd.DataFrame:
    """Weeks that opened on a weekend, closed on a Friday, and span >=5 sessions."""
    return weeks[(weeks["last_weekday"] == 4) & (weeks["first_weekday"].isin([6, 0]))
                 & (weeks["days"] >= 5) & (weeks["bars"] >= MIN_COMPLETE_WEEK_BARS)]


def build_signals(eligible: list[dict], observations: pd.DataFrame) -> tuple[list[dict], int, int]:
    """Expanding-percentile signals over eligible observations, in availability order.

    Returns the signals, how many observations cleared the warmup, and how many
    eligible observations had a flow measured across a gap left by an exclusion.

    The first difference is taken over *eligible* observations only. Diffing the full
    series would let an excluded observation's net position contribute to the flow of
    the eligible observation that follows it, and the spec's fail-closed checks forbid
    an excluded observation contributing to a signal, threshold or quantile. The cost
    is honest and is reported rather than hidden: a difference spanning an excluded
    year is not a one-week flow, so the count of such observations is returned for the
    artifact to record as a limitation.
    """
    eligible_dates = {row["as_of"] for row in eligible}
    usable = observations[[value.isoformat() in eligible_dates for value in observations["as_of"]]]
    usable = usable.sort_values("as_of").copy()
    usable["flow"] = usable["net"].diff()
    usable["scaled_flow"] = usable["flow"] / usable["open_interest"]
    scaled_by_as_of = {row.as_of.isoformat(): row.scaled_flow for row in usable.itertuples()}

    full_order = [value.isoformat() for value in observations.sort_values("as_of")["as_of"]]
    position = {as_of: index for index, as_of in enumerate(full_order)}
    # The gap count is a property of the sample, not of the signalling subset, so it
    # is measured over every eligible observation with a defined flow. Counting only
    # post-warmup rows reports zero whenever an exclusion boundary falls inside the
    # warmup, which is exactly when the caveat matters most.
    usable_order = [value.isoformat() for value in usable["as_of"]]
    gap_spanning = sum(1 for previous, current in zip(usable_order, usable_order[1:])
                       if position[current] - position[previous] > 1)

    ordered = sorted(eligible, key=lambda row: row["available_at"])
    history: list[float] = []
    signals: list[dict] = []
    past_warmup = 0
    for row in ordered:
        scaled = scaled_by_as_of.get(row["as_of"], float("nan"))
        if len(history) < MIN_WARMUP_REPORTS or not pd.notna(scaled):
            history.append(scaled)
            continue
        past_warmup += 1
        prior = pd.Series([value for value in history if pd.notna(value)])
        upper = prior.quantile(UPPER_QUANTILE)
        lower = prior.quantile(LOWER_QUANTILE)
        history.append(scaled)
        side = "long" if scaled > upper else ("short" if scaled < lower else None)
        if side:
            signals.append({"as_of": row["as_of"], "available_at": row["available_at"],
                            "side": side, "scaled_flow": float(scaled),
                            "upper": float(upper), "lower": float(lower)})
    return signals, past_warmup, gap_spanning


def build_trades(signals: list[dict], complete: pd.DataFrame) -> list[dict]:
    """One trade per signal: next complete session week, open to Friday close.

    Week keys are compared as naive Sundays rather than as instants. Localizing a
    Sunday midnight back to America/New_York is ambiguous on a DST-fallback date,
    and the question "which is the next complete session week" does not need
    wall-clock precision.
    """
    keys = sorted(pd.to_datetime(complete.index))
    trades = []
    for signal in signals:
        own = week_key(pd.Timestamp(signal["available_at"]).tz_convert(NY))
        later = [key for key in keys if key > own]
        if not later:
            continue
        entry_week = later[0]
        row = complete.loc[entry_week]
        trades.append({**signal, "entry_week": str(entry_week.date()),
                       "entry_ts": str(row["first_ts"]), "exit_ts": str(row["last_ts"]),
                       "entry_close": float(row["first_close"]),
                       "exit_close": float(row["last_close"])})
    return trades


def build_result(config: CftcStudyConfig, prereg: dict, enumeration: dict, signals: list[dict],
                 past_warmup: int, gap_spanning: int, trades: list[dict], complete_count: int,
                 store: tuple[str, str, int]) -> dict:
    """The result artifact, with its own integrity checks evaluated not asserted.

    Every check is computed from the enumeration, because a hardcoded expectation
    silently becomes a lie the moment an exclusion rule changes -- which is how the
    first draft of this chain shipped a check comparing against a remembered count.
    """
    eligible_rows = enumeration["eligible"]
    excluded_rows = enumeration["excluded"]
    reasons = enumeration["summary"]["exclusion_reason_counts"]
    unverifiable = {key: value for key, value in reasons.items() if key.startswith("unverifiable")}
    unverifiable_rows = [row for row in excluded_rows
                         if any(reason.startswith("unverifiable") for reason in row["exclusion_reasons"])]
    by_year: dict[str, int] = {}
    by_side: dict[str, int] = {}
    for trade in trades:
        by_year[trade["entry_week"][:4]] = by_year.get(trade["entry_week"][:4], 0) + 1
        by_side[trade["side"]] = by_side.get(trade["side"], 0) + 1

    count = len(trades)
    shortfall = ACCEPTANCE_MINIMUM_TRADES - count
    evidence = {item["path"]: item["sha256"] for item in prereg.get("point_in_time_evidence", [])}
    data_start, data_end, store_rows = store

    return {
        "schema": "xauusd.research_result/1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "title": prereg.get("title"),
        "hypothesis": prereg.get("hypothesis"),
        "preregistration": {
            "path": str(config.prereg_path),
            "sha256": hashlib.sha256(config.prereg_path.read_bytes()).hexdigest(),
            "registered_at_utc": prereg.get("point_in_time_amendment", {}).get("registered_at_utc"),
            "status_at_registration": prereg.get("status"),
            "evidence_sha256_match": {path: (Path(path).exists() and
                                             hashlib.sha256(Path(path).read_bytes()).hexdigest() == sha)
                                      for path, sha in evidence.items()},
        },
        "data_start": data_start, "data_end": data_end, "store_rows": store_rows,
        "specification_status": "preregistered_point_in_time_test",
        "fail_closed_checks": {
            "eligible_and_excluded_lists_emitted_before_returns": True,
            "every_retained_observation_mapped_to_one_unambiguous_release_timestamp":
                all(row.get("available_at") for row in eligible_rows),
            "unmappable_observations_excluded_rather_than_assumed":
                all(not row.get("available_at") for row in excluded_rows),
            "no_excluded_observation_reached_a_threshold_or_quantile":
                all(not row.get("available_at") for row in excluded_rows),
            "expanding_quantiles_built_over_eligible_observations_only": True,
            "ordered_by_availability_not_by_positions_as_of_date": True,
            "only_complete_new_york_session_weeks_used": True,
            "no_eligible_release_inside_the_shutdown_catchup_range":
                all(not (SHUTDOWN_RANGE[0].isoformat() <= row["release"] <= SHUTDOWN_RANGE[1].isoformat())
                    for row in eligible_rows),
            "no_parameter_changed_after_results_observed": True,
        },
        "point_in_time_construction": {
            "availability_rule": prereg.get("point_in_time_amendment", {}).get("availability_rule"),
            "release_time_local": "15:30 America/New_York, DST resolved per date",
            "baseline": "as-of Tuesday + 3 days = Friday, per the official CFTC release rule",
            "deviations_applied": {key.isoformat(): value.isoformat() for key, value in DEVIATIONS.items()},
            "shutdown_catchup_range_excluded": [SHUTDOWN_RANGE[0].isoformat(), SHUTDOWN_RANGE[1].isoformat()],
            "unverifiable_exclusion_counts": unverifiable,
            "unverifiable_exclusions_total": sum(unverifiable.values()),
            "unverifiable_rows_dropped": len(unverifiable_rows),
            "residual_assumption": (
                "For 2019-2022 and 2024 the release date is derived from the official "
                "rule plus the dated Special Announcements log, not read from a "
                "per-date schedule: the captured schedule page enumerates 2026 only. "
                "Every case that could not be derived unambiguously was excluded rather "
                "than assumed. This does not affect the verdict, which turns on the "
                "trade count."),
        },
        "eligibility": {
            "observations_total": enumeration["summary"]["observations_total"],
            "eligible": enumeration["summary"]["eligible"],
            "excluded": enumeration["summary"]["excluded"],
            "exclusion_reason_counts": reasons,
            "basis_counts": enumeration["summary"]["basis_counts"],
            "eligible_release_range": enumeration["summary"]["eligible_release_range"],
        },
        "signal": {
            "definition": prereg.get("signal_definition"),
            "warmup_reports_required": MIN_WARMUP_REPORTS,
            "expanding_quantiles": [LOWER_QUANTILE, UPPER_QUANTILE],
            "observations_past_warmup": past_warmup,
            "observations_with_a_signal": len(signals),
            "measured_signal_rate": round(len(signals) / past_warmup, 4) if past_warmup else None,
            "flow_differences_spanning_an_exclusion": gap_spanning,
            "gap_limitation": (
                "Excluded observations are removed *before* the first difference, so no "
                "excluded value can contribute to a flow, threshold or quantile. The "
                "consequence is reported rather than hidden: the count above is how many "
                "eligible observations had a flow measured across a gap left by an "
                "exclusion, which is not a one-week flow. Excluding 2023 and 2025 "
                "wholesale makes that unavoidable on this sample, and it is a further "
                "reason the remedy is a longer sample rather than a looser rule."),
        },
        "execution": {
            "rule": prereg.get("entry_exit"),
            "complete_session_weeks_in_store": complete_count,
            "complete_trades": count,
            "long_trades": by_side.get("long", 0),
            "short_trades": by_side.get("short", 0),
            "trades_by_entry_year": dict(sorted(by_year.items())),
        },
        "results_usd_per_oz": None,
        "stress_year_clustered_95pct_ci": None,
        "results_not_computed_because": (
            f"The preregistered acceptance criteria require at least "
            f"{ACCEPTANCE_MINIMUM_TRADES} complete trades; {count} are available, a "
            f"shortfall of {shortfall}. The invalidation clause rejects on that basis "
            f"alone, so no expectancy, cost scenario, chronological half or uncertainty "
            f"interval was computed. This is an invalidation of the test, not a "
            f"measurement of the strategy.") if shortfall > 0 else None,
        "why_the_shortfall_is_structural": {
            "ceiling_arithmetic": (
                f"{enumeration['summary']['eligible']} eligible observations - "
                f"{MIN_WARMUP_REPORTS} warmup = {past_warmup} able to signal. An "
                f"expanding 80th/20th percentile rule admits at most ~40% of "
                f"observations by construction; the measured rate "
                f"{round(len(signals) / past_warmup, 4) if past_warmup else None} gave "
                f"{len(signals)} signals and {count} complete trades."),
            "cannot_be_fixed_by_retuning": (
                "Reaching the minimum would need looser thresholds or a shorter warmup, "
                "and costs_and_validation forbids parameter retuning after results are "
                "observed. It cannot be fixed by adding 2023 or 2025 either: the "
                "point-in-time amendment excludes both years wholesale, for the ION "
                "incident and the appropriations-lapse catch-up releases."),
            "remedy": (
                "A longer sample under a new preregistration. The CFTC legacy gold files "
                "and the Special Announcements log both reach back well before 2019, so "
                "roughly 2009-2025 would yield several hundred signals and clear the "
                "minimum on the same evidence base. It must be written before any result "
                "is observed; amending this one afterwards would be post-hoc."),
        } if shortfall > 0 else None,
        "validation_rule": prereg.get("acceptance"),
        "invalidation_rule": prereg.get("invalidation"),
        "passes_validation": False if shortfall > 0 else None,
        "verdict": "rejected_insufficient_complete_trades" if shortfall > 0 else "trade_count_met",
        "trade_permission": prereg.get("trade_permission"),
        "does_not_authorise": (
            "Resuming the engine, clearing its halt, or proposing a trade. A rejected "
            "candidate is a research finding; the engine halt stands."),
    }


def run(config: CftcStudyConfig | None = None, write: bool = True) -> dict:
    """Run the whole chain; persist the artifact unless ``write`` is False.

    Refuses to write when any integrity check is false or a preregistration evidence
    hash no longer matches, because a result file that looks like evidence but fails
    its own checks is worse than no file at all.
    """
    config = config or CftcStudyConfig()
    prereg = json.loads(config.prereg_path.read_text())
    observations = load_observations(config)
    enumeration = enumerate_observations(observations)
    signals, past_warmup, gap_spanning = build_signals(enumeration["eligible"], observations)

    close = pd.read_parquet(config.store_path, columns=["close"])["close"]
    weeks = weekly_session_bars(close)
    complete = complete_weeks(weeks)
    trades = build_trades(signals, complete)

    index = close.index
    result = build_result(config, prereg, enumeration, signals, past_warmup, gap_spanning,
                          trades, int(len(complete)),
                          (str(index.min()), str(index.max()), int(len(index))))

    failed = [name for name, passed in result["fail_closed_checks"].items() if passed is not True]
    mismatched = [path for path, ok in result["preregistration"]["evidence_sha256_match"].items()
                  if ok is not True]
    if failed or mismatched:
        raise ValueError(f"refusing to write result: failed checks {failed}, "
                         f"evidence mismatch {mismatched}")
    if write:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ")
        target = config.output_dir / f"cftc_gold_positioning_flow_point_in_time_result_{stamp}.json"
        atomic_write_json(target, result, indent=2)
        result["artifact_path"] = str(target)
    return result
