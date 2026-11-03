"""Astronomical computations: phase events, illumination, moon age, tithi."""

from datetime import date, datetime, timedelta
from calendar import monthrange
from zoneinfo import ZoneInfo
from dataclasses import dataclass
from typing import List, Dict, Optional
import math
from skyfield import almanac
from . import config as cfg
from .sky import eph, ts


@dataclass
class PhaseEvent:
    """A lunar phase event (new moon or full moon).

    Attributes
    ----------
    kind : str
        One of "new", "full", "first_quarter" or "last_quarter".
    date : date
        The calendar date on which the event occurs (local time).
    dt : datetime
        The exact local datetime of the event.
    """
    kind: str
    date: date
    dt: datetime


def compute_phase_events_for_year(year: int):
    """Compute all new/full moon events for a given year.

    This includes events from the previous December and the following January
    to ensure proper waxing/waning context.

    Parameters
    ----------
    year : int
        The target year for which lunar phase events should be computed.

    Returns
    -------
    events : list of PhaseEvent
        All new/full moon events spanning the extended date range.
    by_month : dict[int, list[PhaseEvent]]
        A mapping of month → events occurring within that month of the target year.
    """
    # We need events from the previous December through next January
    t0 = ts.utc(year - 1, 12, 1)
    t1 = ts.utc(year + 1, 1, 31, 23, 59)

    times, phases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))


    events: List[PhaseEvent] = []
    quarters: List[PhaseEvent] = []
    for t, phase in zip(times, phases):
        utc_dt = t.utc_datetime().replace(tzinfo=ZoneInfo("UTC"))
        local_dt = utc_dt.astimezone(cfg.TZINFO)

        if phase in (1, 3):  # 1=first quarter, 3=last quarter
            kind = "first_quarter" if phase == 1 else "last_quarter"
            quarters.append(PhaseEvent(kind, local_dt.date(), local_dt))
            continue

        kind = "new" if phase == 0 else "full"
        events.append(PhaseEvent(kind, local_dt.date(), local_dt))

    events.sort(key=lambda e: e.date)
    quarters.sort(key=lambda e: e.dt)
    cfg.QUARTER_EVENTS_GLOBAL = quarters

    # Build month buckets ONLY for the target year
    by_month: Dict[int, List[PhaseEvent]] = {m: [] for m in range(1, 13)}
    for ev in events:
        if ev.date.year == year:
            by_month[ev.date.month].append(ev)

    return events, by_month


def assign_daily_phases(
    year: int,
    month: int,
    events: List[PhaseEvent],
    events_by_month: Dict[int, List[PhaseEvent]]
):
    """Assign a lunar phase label to each day of a month.

    The assigned phase is one of:
    - "New Moon"
    - "Full Moon"
    - "Waxing"
    - "Waning"

    True new/full moon dates are taken from the event list.
    Waxing/waning is inferred by examining the nearest surrounding events.

    Parameters
    ----------
    year : int
        The year of the target month.
    month : int
        The month (1–12) for which daily phases are assigned.
    events : list of PhaseEvent
        All phase events spanning the extended date range.
    events_by_month : dict[int, list[PhaseEvent]]
        Mapping of month → events occurring in that month of the target year.

    Returns
    -------
    dict[int, str]
        A mapping of day → phase label.
    """
    days = monthrange(year, month)[1]
    phases: Dict[int, Optional[str]] = {d: None for d in range(1, days + 1)}

    prev_m = month - 1 if month > 1 else 12
    next_m = month + 1 if month < 12 else 1

    # Gather events from adjacent months for context
    candidate: List[PhaseEvent] = []
    candidate += events_by_month.get(prev_m, [])
    candidate += events_by_month.get(month, [])
    candidate += events_by_month.get(next_m, [])

    # 1. TRUE phase dates
    true_new_days: set[int] = set()
    true_full_days: set[int] = set()

    for ev in candidate:
        if ev.date.year == year and ev.date.month == month:
            if ev.kind == "new":
                true_new_days.add(ev.date.day)
            else:
                true_full_days.add(ev.date.day)

    # 2. Mark New / Full
    for d in range(1, days + 1):
        if d in true_new_days:
            phases[d] = "New Moon"
        elif d in true_full_days:
            phases[d] = "Full Moon"

    # 3. Build context for waxing/waning
    month_start = date(year, month, 1)
    month_end = date(year, month, days)

    context = [
        e for e in events
        if month_start - timedelta(days=60) <= e.date <= month_end + timedelta(days=60)
    ]

    # 4. Assign waxing/waning
    for d in range(1, days + 1):
        if phases[d] is not None:
            continue

        current = date(year, month, d)

        before = [e for e in context if e.date <= current]
        after = [e for e in context if e.date > current]

        if not before:
            phases[d] = "Waxing"
            continue
        if not after:
            phases[d] = "Waning"
            continue

        last_ev = before[-1]
        next_ev = after[0]

        if last_ev.kind == "new" and next_ev.kind == "full":
            phases[d] = "Waxing"
        else:
            phases[d] = "Waning"

    return phases


def moon_rise_set_times(d: date):
    """
    Compute the Moon’s local rise and set times for a given calendar date.

    This helper determines when the Moon crosses the local horizon on the
    specified date, returning the times (in HH:MM 24‑hour format) converted
    into the active IANA timezone (`TZINFO`). If the Moon does not rise or
    set within the 00:00–23:59 interval of the given date, the corresponding
    return value is `None`.

    Notes
    -----
    The Moon does not necessarily rise and set once per calendar day.
    Because the Moon rises ~50 minutes later each day and its declination
    varies significantly, several natural situations can occur:

    • The Moon may rise late at night and the next rise occurs after
      midnight the following day, resulting in no rise event on the
      intervening date.

    • The Moon may remain above the horizon for more than 24 hours,
      producing a day with no rise or set.

    • The Moon may remain below the horizon for more than 24 hours,
      also producing a day with no rise or set.

    These cases are astronomically normal and are reflected by returning
    `None` for the missing event.

    Parameters
    ----------
    d : date
        The calendar date for which moonrise and moonset times should be
        computed.

    Returns
    -------
    tuple[str | None, str | None]
        A pair `(rise, set_)` where:
            rise : str or None
                Local moonrise time in "HH:MM" format, or None if no rise
                occurs on this date.
            set_ : str or None
                Local moonset time in "HH:MM" format, or None if no set
                occurs on this date.
    """
    t0 = ts.from_datetime(datetime(d.year, d.month, d.day, 0, 0, tzinfo=cfg.TZINFO))
    t1 = ts.from_datetime(datetime(d.year, d.month, d.day, 23, 59, tzinfo=cfg.TZINFO))

    f = almanac.risings_and_settings(eph, eph['moon'], cfg.OBSERVER)
    times, events = almanac.find_discrete(t0, t1, f)

    rise = None
    set_ = None

    for t, e in zip(times, events):
        local = t.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(cfg.TZINFO)
        if e == 1:   # rising
            rise = local.strftime("%H:%M")
        else:        # setting
            set_ = local.strftime("%H:%M")

    return rise, set_


def moon_illumination_percent(d: date):
    """Compute the moon's illumination percentage for a given date.

    If the date corresponds to an actual new/full moon event, the illumination
    may be computed at the exact event moment (if enabled). Otherwise, the
    illumination is computed at local midnight.

    Parameters
    ----------
    d : date
        The calendar date for which illumination should be computed.

    Returns
    -------
    tuple[str, float]
        event_time_str : str
            The local time of the lunar event (HH:MM), or an empty string if
            no event occurs on this date.
        illumination_percent : float
            The illumination percentage (0–100).
    """
    # Check if this day is a true full/new moon
    event = next((ev for ev in cfg.EVENTS_GLOBAL if ev.date == d), None)

    if event:
        if cfg.USE_EXACT_EVENT_ILLUMINATION:
            # Try exact illumination at the true event moment
            exact = illumination_exact_at_event(event)

            if exact is not None:
                illum = exact
            else:
                # Fallback: midnight illumination
                local_dt = datetime(d.year, d.month, d.day, 0, 0, tzinfo=cfg.TZINFO)
                t = ts.from_datetime(local_dt)
                angle = almanac.moon_phase(eph, t).radians
                illum = round((1 - math.cos(angle)) / 2 * 100, 2)
        else:
            # Standard mode: midnight illumination even for full/new moons
            local_dt = datetime(d.year, d.month, d.day, 0, 0, tzinfo=cfg.TZINFO)
            t = ts.from_datetime(local_dt)
            angle = almanac.moon_phase(eph, t).radians
            illum = round((1 - math.cos(angle)) / 2 * 100, 2)

        # Local time of the event in 24h format
        event_time_str = event.dt.strftime("%H:%M")
        return event_time_str, illum

    # Otherwise compute illumination at local midnight
    local_dt = datetime(d.year, d.month, d.day, 0, 0, tzinfo=cfg.TZINFO)
    t = ts.from_datetime(local_dt)
    angle = almanac.moon_phase(eph, t).radians
    illum = round((1 - math.cos(angle)) / 2 * 100, 2)

    return "", illum


def moon_phase_fraction(d: date) -> float:
    """Compute the fractional lunar phase for a given date.

    The returned value is normalized to the range [0, 1), where:
    - 0.0 corresponds to a new moon
    - 0.5 corresponds to a full moon

    Parameters
    ----------
    d : date
        The calendar date for which the phase fraction is computed.

    Returns
    -------
    float
        The fractional phase of the lunar cycle.
    """
    t = ts.from_datetime(datetime(d.year, d.month, d.day, 0, 0, tzinfo=cfg.TZINFO))
    angle = almanac.moon_phase(eph, t).radians
    return (angle % (2 * math.pi)) / (2 * math.pi)


def illumination_exact_at_event(ev: PhaseEvent) -> float | None:
    """Compute illumination at the exact moment of a new or full moon event.

    Parameters
    ----------
    ev : PhaseEvent
        The lunar event for which illumination should be computed.

    Returns
    -------
    float or None
        The illumination percentage (0–100) at the exact event moment,
        or None if the event time cannot be resolved.
    """
    # Search for the exact event time within a ±1 day window
    t0 = ts.utc(ev.date.year, ev.date.month, ev.date.day - 1)
    t1 = ts.utc(ev.date.year, ev.date.month, ev.date.day + 1)
    times, phases = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))

    for tt, p in zip(times, phases):
        if (ev.kind == "full" and p == 2) or (ev.kind == "new" and p == 0):
            angle = almanac.moon_phase(eph, tt).radians
            illum = (1 - math.cos(angle)) / 2
            return round(illum * 100, 2)

    return None


def illumination_trend_for_date(center_date: date, window: int = 3) -> list[float]:
    """
    Compute a short illumination trend centered on a given date.

    This helper returns illumination percentages for a symmetric window
    around the target date. For example, a window of 3 yields illumination
    values for the range:
        center_date - 3 days  →  center_date + 3 days
    producing 7 total samples.

    Parameters
    ----------
    center_date : date
        The calendar date around which the illumination trend is computed.
    window : int, optional
        Number of days before and after the center date to include.
        Default is 3.

    Returns
    -------
    list of float
        Illumination percentages (0–100) for each day in the window,
        ordered chronologically.
    """
    values: list[float] = []
    for offset in range(-window, window + 1):
        d = center_date + timedelta(days=offset)
        _, illum = moon_illumination_percent(d)
        values.append(illum)
    return values


SYNODIC_MONTH = 29.530588


def phase_name_for_date(d: date, frac: float) -> str:
    """Return the descriptive phase name (e.g. "Waxing Crescent") for a day.

    Exact event days (new, first quarter, full, last quarter) win over the
    fraction-based name, so the label always agrees with the event markers.
    """
    for ev in cfg.EVENTS_GLOBAL or []:
        if ev.date == d:
            return "New Moon" if ev.kind == "new" else "Full Moon"
    for ev in cfg.QUARTER_EVENTS_GLOBAL:
        if ev.date == d:
            return "First Quarter" if ev.kind == "first_quarter" else "Last Quarter"

    if frac < 0.25:
        return "Waxing Crescent"
    if frac < 0.5:
        return "Waxing Gibbous"
    if frac < 0.75:
        return "Waning Gibbous"
    return "Waning Crescent"


def moon_age_at(moment: datetime) -> float | None:
    """Days elapsed since the last new moon at the given local datetime."""
    previous = [ev for ev in cfg.EVENTS_GLOBAL or [] if ev.kind == "new" and ev.dt <= moment]
    if not previous:
        return None
    return (moment - previous[-1].dt).total_seconds() / 86400


def moon_age_days(d: date) -> float | None:
    """Days elapsed since the last new moon, measured at local noon of `d`."""
    age = moon_age_at(datetime(d.year, d.month, d.day, 12, 0, tzinfo=cfg.TZINFO))
    return None if age is None else round(age, 1)


def tithi_for_date(d: date) -> int:
    """Return the tithi (1-30) prevailing at local sunrise on `d`.

    A tithi is each 12 degrees of the Moon's elongation from the Sun. When
    the location is known the sunrise instant is used; otherwise 06:00.
    """
    when = None
    if cfg.OBSERVER is not None:
        t0 = ts.from_datetime(datetime(d.year, d.month, d.day, 0, 0, tzinfo=cfg.TZINFO))
        t1 = ts.from_datetime(datetime(d.year, d.month, d.day, 0, 0, tzinfo=cfg.TZINFO) + timedelta(days=1))
        times, events = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(eph, cfg.OBSERVER))
        for t, e in zip(times, events):
            if e == 1:           # sunrise
                when = t
                break
    if when is None:
        when = ts.from_datetime(datetime(d.year, d.month, d.day, 6, 0, tzinfo=cfg.TZINFO))

    degrees = almanac.moon_phase(eph, when).degrees % 360
    return int(degrees // 12) + 1
