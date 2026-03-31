"""
Lunar Calendar Generator
Copyright (c) 2026 Valerio Fuoglio

Tools for computing lunar phases, illumination, and rendering SVG moon icons.
This module includes:
- PhaseEvent dataclass
- Lunar event computation
- Daily phase assignment
- Illumination and phase fraction utilities
- SVG moon rendering

Licensed under the MIT License.
See LICENSE file for details.
"""

from datetime import date, datetime, timedelta
from calendar import monthrange
from zoneinfo import ZoneInfo
from dataclasses import dataclass
import math
from typing import List, Dict, Optional


from skyfield.api import load
from skyfield import almanac

import math

# ----------------------------------------
# CONFIG
# ----------------------------------------

"""
Configuration variables controlling NoctiCycle’s behavior.

These settings define the target year, location, timezone, rendering options,
and astronomical calculation modes used throughout the lunar calendar
generation process.

Attributes
----------
YEAR : int
    The calendar year for which the lunar calendar is generated.

CITY : str
    Human‑readable name of the selected location. Used for display in the
    generated HTML output.

TZ : str
    IANA timezone identifier for the chosen location
    (e.g., "America/Halifax"). Determines how lunar events are converted
    from UTC to local time.

TZINFO : ZoneInfo
    Parsed timezone object derived from `TZ`. Used for all local datetime
    conversions.

SHOW_LUMINANCE : bool
    If True, each calendar day displays the Moon’s illumination percentage.

SHOW_EVENT_TIME : bool
    If True, the exact local time of new/full moon events is shown on the
    corresponding day.

USE_EXACT_EVENT_ILLUMINATION : bool
    If True, illumination on true new/full moon days is computed at the
    exact event moment. If False, illumination is always computed at local
    midnight.

COSMETICS_MODE : bool
    Enables optional visual adjustments to the SVG moon rendering. This
    affects appearance only, not astronomical accuracy.

ts : skyfield.api.TimeScale
    Global timescale object used for all astronomical computations.

eph : skyfield.api.Loader
    Ephemeris data (DE421) used to compute lunar positions and phases.

EVENTS_GLOBAL : list[PhaseEvent] or None
    Cached list of lunar events for the active year. Populated by
    `compute_phase_events_for_year()` and used by illumination helpers.
"""


YEAR: int = 2026
CITY: str = "New York"
TZ: str = "America/New_York"
TZINFO = ZoneInfo(TZ)

SHOW_LUMINANCE: bool = True
SHOW_EVENT_TIME: bool = True

USE_EXACT_EVENT_ILLUMINATION: bool = True

COSMETICS_MODE: bool = True

ts = load.timescale()
eph = load("de421.bsp")

EVENTS_GLOBAL = None


# ----------------------------------------
# PHASE EVENTS (for bands + names)
# ----------------------------------------


@dataclass
class PhaseEvent:
    """A lunar phase event (new moon or full moon).

    Attributes
    ----------
    kind : str
        Either "new" or "full".
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
    for t, phase in zip(times, phases):
        if phase not in (0, 2):  # 0=new, 2=full
            continue

        utc_dt = t.utc_datetime().replace(tzinfo=ZoneInfo("UTC"))
        local_dt = utc_dt.astimezone(TZINFO)
        kind = "new" if phase == 0 else "full"

        events.append(PhaseEvent(kind, local_dt.date(), local_dt))

    events.sort(key=lambda e: e.date)

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



# ----------------------------------------
# ILLUMINATION + LUNATION
# ----------------------------------------
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
    event = next((ev for ev in EVENTS_GLOBAL if ev.date == d), None)

    if event:
        if USE_EXACT_EVENT_ILLUMINATION:
            # Try exact illumination at the true event moment
            exact = illumination_exact_at_event(event)

            if exact is not None:
                illum = exact
            else:
                # Fallback: midnight illumination
                local_dt = datetime(d.year, d.month, d.day, 0, 0, tzinfo=TZINFO)
                t = ts.from_datetime(local_dt)
                angle = almanac.moon_phase(eph, t).radians
                illum = round((1 - math.cos(angle)) / 2 * 100, 2)
        else:
            # Standard mode: midnight illumination even for full/new moons
            local_dt = datetime(d.year, d.month, d.day, 0, 0, tzinfo=TZINFO)
            t = ts.from_datetime(local_dt)
            angle = almanac.moon_phase(eph, t).radians
            illum = round((1 - math.cos(angle)) / 2 * 100, 2)

        # Local time of the event in 24h format
        event_time_str = event.dt.strftime("%H:%M")
        return event_time_str, illum

    # Otherwise compute illumination at local midnight
    local_dt = datetime(d.year, d.month, d.day, 0, 0, tzinfo=TZINFO)
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
    t = ts.from_datetime(datetime(d.year, d.month, d.day, 0, 0, tzinfo=TZINFO))
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

# ----------------------------------------
# SVG MOON (geometry from the other project)
# ----------------------------------------

@dataclass
class TerminatorGeometry:
    """Geometric description of the lunar terminator curve.

    Attributes
    ----------
    arc_radius : float
        Radius of curvature of the terminator arc.
    terminator_on_right : bool
        True if the bright side of the moon is on the right.
    light_from_left : bool
        True if the illuminated portion is on the left side.
    """
    arc_radius: float
    terminator_on_right: bool
    light_from_left: bool


def compute_terminator_geometry(phase: float, radius: float) -> TerminatorGeometry:
    """Compute the terminator arc geometry for a given lunar phase.

    Parameters
    ----------
    phase : float
        Lunation fraction in the range [0, 1], where:
        - 0.0 = new moon
        - 0.5 = full moon
        - 1.0 = new moon again
    radius : float
        Radius of the moon disc in SVG coordinate units.

    Returns
    -------
    TerminatorGeometry
        A dataclass describing the curvature and orientation of the terminator.
    """

    QUADRANTS = [
        (0.25, lambda p: p,          True,  False),
        (0.50, lambda p: 0.5 - p,    False, False),
        (0.75, lambda p: p - 0.5,    True,  True),
        (1.00, lambda p: 1 - p,      False, True),
    ]

    for threshold, L_fn, right, lit_left in QUADRANTS:
        if phase <= threshold:
            L = L_fn(phase)
            terminator_on_right = right
            light_from_left = lit_left
            break

    # Compute terminator arc curvature
    x = radius * (1 - math.cos(2 * math.pi * L))
    n = radius - x
    arc_radius = (radius**2 + n**2) / (2 * n)

    return TerminatorGeometry(
        arc_radius=arc_radius,
        terminator_on_right=terminator_on_right,
        light_from_left=light_from_left,
    )


def render_moon_svg(phase: float, size: int = 24) -> str:
    """Render an SVG moon icon for a given lunar phase.

    Parameters
    ----------
    phase : float
        Lunation fraction (0.0 = new, 0.5 = full).
    size : int, optional
        Width and height of the SVG viewport in pixels. Default is 24.

    Returns
    -------
    str
        SVG markup representing the moon at the given phase.
    """

    r = size / 2
    geom = compute_terminator_geometry(phase, r)

    # Determine shading classes
    colours = {
        "left":  "light" if geom.light_from_left else "shadow",
        "right": "shadow" if geom.light_from_left else "light",
    }

    # SVG path components
    move_to_top = f"M{r},0"
    disc_left_arc  = f"A {r} {r} 0 0 1 {r} 0"
    disc_right_arc = f"A {r} {r} 0 0 0 {r} 0"

    terminator_arc = (
        f"A {geom.arc_radius} {geom.arc_radius} "
        f"0 0 {'1' if geom.terminator_on_right else '0'} {r} {size}"
    )

    # Build the two halves of the moon
    paths = [
        f'<path d="{move_to_top} {terminator_arc} {disc_left_arc}" class="{colours["left"]}"/>',
        f'<path d="{move_to_top} {terminator_arc} {disc_right_arc}" class="{colours["right"]}"/>'
    ]

    # Outline circle
    outline = f'<circle cx="{r}" cy="{r}" r="{r - 0.5}" class="moon-outline"/>'

    return (
        f'<svg class="moon-svg" viewBox="0 0 {size} {size}">'
        f'{outline}{"".join(paths)}'
        f'</svg>'
    )

# ----------------------------------------
# HTML GENERATION
# ----------------------------------------
def month_name(m: int) -> str:
    """Return the abbreviated month name for a given month number.

    Parameters
    ----------
    m : int
        Month number in the range 1–12.

    Returns
    -------
    str
        Three‑letter month abbreviation (e.g., "Jan", "Feb").
    """
    return date(2000, m, 1).strftime("%b")


def write_html(year: int) -> None:
    """Generate the full lunar calendar HTML document for a given year.

    This function orchestrates:
    - computing lunar phase events,
    - assigning daily phases,
    - rendering SVG moon icons,
    - and assembling the complete HTML output.

    The resulting HTML file is written to disk as:
        lunar_calendar_<year>.html

    Parameters
    ----------
    year : int
        The calendar year for which the lunar calendar should be generated.

    Returns
    -------
    None
        The function writes an HTML file but does not return a value.
    """
    global EVENTS_GLOBAL
    events, events_by_month = compute_phase_events_for_year(year)
    EVENTS_GLOBAL = events  # retained for illumination lookups


    html = f"""
<html>
<head>
<meta charset="UTF-8">
<title>Lunar Calendar {year} – {CITY}</title>
<style>

body {{
    font-family: Arial;
    font-size: 10px;
    margin: 10px;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    table-layout: fixed;
}}

td, th {{
    border: 1px solid #ccc;
    text-align: center;
    padding: 2px;
}}

.phase {{
    font-weight: bold;
    color: #fff;
    border-radius: 4px;
}}

.phase-new {{
    background: #2E3440;
}}

.phase-waxing {{
    background: #88C0D0;
    color: #000;
}}

.phase-full {{
    background: #EBCB8B;
    color: #000;
}}

.phase-waning {{
    background: #B48EAD;
    color: #000;
}}

.phase-time {{
    font-size: 12px;
    height: 14px;
    line-height: 14px;
    opacity: 0.8;
}}

.phase-time.hidden {{
    display: none;
}}


.moon-svg {{
    width: 24px;
    height: 24px;
}}

.light {{ fill: #fdfdfd; }}
.shadow {{ fill: #111111; }}

.moon-outline {{
    fill: none;
    stroke: #444;
    stroke-width: 0.8;
}}

.brightness {{
    font-size: 12px;
}}

</style>"""

    if COSMETICS_MODE:
        html += f"""
<style>
/* ===== Layout & background ===== */
body {{
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 11px;
    color: #e5e9f0;
    background: radial-gradient(circle at top, #2e3440 0%, #1b1f27 45%, #05060a 100%);
    margin: 16px;
}}

h1 {{
    font-family: "Merriweather", "Georgia", serif;
    font-size: 28px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #eceff4;
    text-align: center;
    margin-bottom: 18px;
}}

/* ===== Month cards ===== */
.month-block {{
    background: rgba(15, 18, 26, 0.96);
    border-radius: 12px;
    box-shadow: 0 14px 30px rgba(0, 0, 0, 0.45);
    padding: 12px 14px 14px 14px;
    margin-bottom: 20px;
    border: 1px solid rgba(136, 192, 208, 0.18);
}}

.month-name {{
    font-family: "Merriweather", "Georgia", serif;
    font-size: 22px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #e5e9f0;
    margin: 0 0 8px 2px;
}}

.month-subtitle {{
    font-size: 10px;
    color: #88c0d0;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    margin-bottom: 8px;
}}

/* ===== Table ===== */
table {{
    border-collapse: separate;
    border-spacing: 2px;
    width: 100%;
    table-layout: fixed;
}}

th {{
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #d8dee9;
    padding: 4px 2px;
    border: none;
    background: transparent;
}}

td {{
    padding: 6px 4px;
    border-radius: 8px;
    background: radial-gradient(circle at top, #2b303b 0%, #191d24 60%, #111318 100%);
    border: 1px solid rgba(67, 76, 94, 0.9);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.45);
    vertical-align: top;
}}

.day-cell {{
    position: relative;
}}

.day-number {{
    font-size: 11px;
    font-weight: 600;
    color: #e5e9f0;
    text-align: left;
    margin-bottom: 2px;
}}

/* ===== Moon icon, halo, depth ===== */
.moon-wrapper {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    gap: 1px;
    margin-top: 2px;
}}

.moon-svg {{
    width: 32px;
    height: 32px;
    filter: drop-shadow(0 0 6px rgba(235, 203, 139, 0.55));
}}

.moon-outline {{
    fill: none;
    stroke: #4c566a;
    stroke-width: 0.9;
}}

.light {{
    fill: #eceff4;
}}

.shadow {{
    fill: #2e3440;
}}

/* ===== Luminance & time ===== */
.brightness {{
    font-size: 11px;
    color: #e5e9f0;
    opacity: 0.9;
}}

.phase-time {{
    font-size: 10px;
    height: 14px;
    line-height: 14px;
    opacity: 0.75;
    color: #88c0d0;
}}

.phase-time.hidden {{
    display: none;
}}

/* ===== Phase gradient bar ===== */
.phase-bar {{
    margin-top: 3px;
    height: 4px;
    border-radius: 999px;
    overflow: hidden;
    background: #3b4252;
}}

/* Waxing: gradient towards full (gold) */
.phase-bar-waxing {{
    background: linear-gradient(to right, #3b4252 0%, #88c0d0 35%, #ebcb8b 100%);
}}

/* Full: bright gold band */
.phase-bar-full {{
    background: linear-gradient(to right, #d08770 0%, #ebcb8b 50%, #d08770 100%);
}}

/* Waning: gradient away from full towards dark */
.phase-bar-waning {{
    background: linear-gradient(to right, #ebcb8b 0%, #88c0d0 65%, #3b4252 100%);
}}

/* New: very dark band with subtle blue hint */
.phase-bar-new {{
    background: linear-gradient(to right, #2e3440 0%, #3b4252 50%, #2e3440 100%);
}}

/* ===== Moonrise / moonset ===== */
.moonrise-set {{
    margin-top: 3px;
    font-size: 9px;
    color: #d8dee9;
    opacity: 0.8;
}}

.moonrise-set span {{
    display: inline-block;
    margin: 0 2px;
}}

.moonrise-icon {{
    color: #a3be8c;
}}

.moonset-icon {{
    color: #bf616a;
}}

/* ===== Mini illumination trend graph (placeholder styling) ===== */
.illum-graph {{
    margin-top: 4px;
    height: 18px;
    width: 100%;
    opacity: 0.85;
}}

/* ===== Legend & seasons ===== */
.legend {{
    margin-top: 18px;
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(15, 18, 26, 0.96);
    border: 1px solid rgba(67, 76, 94, 0.9);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
    font-size: 10px;
    color: #e5e9f0;
}}

.legend-title {{
    font-family: "Merriweather", "Georgia", serif;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #88c0d0;
    margin-bottom: 6px;
}}

.legend-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
}}

.legend-item {{
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 4px;
}}

.legend-swatch {{
    width: 14px;
    height: 6px;
    border-radius: 999px;
}}

.legend-swatch-full {{
    background: linear-gradient(to right, #d08770 0%, #ebcb8b 50%, #d08770 100%);
}}

.legend-swatch-new {{
    background: linear-gradient(to right, #2e3440 0%, #3b4252 50%, #2e3440 100%);
}}

.legend-swatch-waxing {{
    background: linear-gradient(to right, #3b4252 0%, #88c0d0 35%, #ebcb8b 100%);
}}

.legend-swatch-waning {{
    background: linear-gradient(to right, #ebcb8b 0%, #88c0d0 65%, #3b4252 100%);
}}

.season-marker {{
    font-size: 9px;
    color: #a3be8c;
    text-transform: uppercase;
    letter-spacing: 0.14em;
}}
</style>
"""

    html += """
</head>
<body>

<h1>Lunar Calendar {year} – {city}</h1>""".format(year=year, city=CITY)

    # Only open the giant table when NOT in cosmetic mode
    if not COSMETICS_MODE:
        html += "<table><tr><th>Month</th>"
        for d in range(1, 32):
            html += f"<th>{d}</th>"
        html += "</tr>\n"

    for m in range(1, 13):
        days = monthrange(year, m)[1]
        phases = assign_daily_phases(year, m, events, events_by_month)

        if COSMETICS_MODE:
            html += f"""
            <div class="month-block">
                <div class="month-name">{month_name(m)}</div>
                <div class="month-subtitle">Lunar Phases</div>
                <table>
            """
        else:
            html += f"<tr><td rowspan='2'><b>{month_name(m)}</b></td>"

        # Row 1: phase bands
        d = 1
        while d <= days:
            phase = phases[d]
            span = 1
            while d + span <= days and phases[d + span] == phase:
                span += 1

            display = (
                "New" if phase == "New Moon"
                else "Full" if phase == "Full Moon"
                else phase
            )

            css = {
                "New Moon": "phase-new",
                "Waxing": "phase-waxing",
                "Full Moon": "phase-full",
                "Waning": "phase-waning"
            }[phase]

            html += (
                f"<td colspan='{span}' class='phase {css}'>"
                f"<div class='phase-inner'>{display}</div>"
                f"</td>"
            )
            d += span

        for _ in range(days + 1, 32):
            if not COSMETICS_MODE:
                html += "<td></td>"
        html += "</tr>\n"

        # Row 2: moon icons + brightness
        html += "<tr>"
        for d in range(1, 32):
            if d <= days:
                day_date = date(year, m, d)

                frac = moon_phase_fraction(day_date)
                moon_svg = render_moon_svg(frac, size=24)
                event_time_str, illum = moon_illumination_percent(day_date)

                time_class = "phase-time"
                if not SHOW_EVENT_TIME:
                    time_class += " hidden"

                html += "<td class='day-cell'>"

                if COSMETICS_MODE:
                    html += f"<div class='day-number'>{d}</div>"

                html += "<div class='moon-wrapper'>"
                html += moon_svg

                if SHOW_LUMINANCE:
                    html += f"<div class='brightness'>{illum}%</div>"

                html += f"<div class='{time_class}'>{event_time_str}</div>"
                html += "</div>"  # end moon-wrapper

                html += "</td>"
            else:
                if not COSMETICS_MODE:
                    html += "<td></td>"

        html += "</tr>\n"

        # Close cosmetic block
        if COSMETICS_MODE:
            html += "</table></div>"

    if not COSMETICS_MODE:
        html += "</table>"

    html += "</body></html>"

    with open(f"lunar_calendar_{year}.html", "w") as f:
        f.write(html)

    print("Generated lunar_calendar.html")



# ----------------------------------------
# MAIN
# ----------------------------------------

if __name__ == "__main__":
    write_html(YEAR)
