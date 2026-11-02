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
from typing import List, Dict, Optional

import math
import argparse
import json
import os
import sys

from skyfield.api import load, wgs84
from skyfield import almanac

from geopy.geocoders import Nominatim

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

SHOW_LUMINANCE : bool
    If True, each calendar day displays the Moon’s illumination percentage.

SHOW_EVENT_TIME : bool
    If True, the exact local time of new/full moon events is shown on the
    corresponding day.

USE_EXACT_EVENT_ILLUMINATION : bool
    If True, illumination on true new/full moon days is computed at the
    exact event moment. If False, illumination is always computed at local
    midnight.

ILLUMINATION_TREND : bool
    If True, each calendar day displays a small illumination trend graph
    (sparkline) showing illumination change over ±3 days. Disabled by
    default.

COSMETICS_MODE : bool
    Controls whether the enhanced visual layout is used. Cosmetics are
    enabled by default. They are disabled only when the --print-format
    command-line flag is provided, producing a simplified, print‑friendly
    layout.

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

SHOW_LUMINANCE: bool = True
SHOW_EVENT_TIME: bool = True
ILLUMINATION_TREND: bool = False
SHOW_RISE_SET_TIMES: bool = False
SHOW_QUARTERS: bool = False

USE_EXACT_EVENT_ILLUMINATION: bool = True

COSMETICS_MODE: bool = True

# Print-format settings (only used with --print-format)
PAPER: str = "letter"
PRINT_STYLE: str = "grey"
PRINT_LAYOUT: str = "rows"
# Landscape paper sizes in inches (width, height).
PAPER_SIZES = {
    "letter": (11.0, 8.5),
    "a4": (11.69, 8.27),
    "legal": (14.0, 8.5),
    "tabloid": (17.0, 11.0),
}

ts = load.timescale()
eph = load("de421.bsp")

EVENTS_GLOBAL = None
QUARTER_EVENTS_GLOBAL: list = []
TZINFO = None

LAT: float | None = None
LON: float | None = None
OBSERVER = None

BASE_DIR = None

# ----------------------------------------
# UTILITIES
# ----------------------------------------

def validate_config():
    """Validate timezone and location settings with user-friendly messages."""

    global BASE_DIR

    # --- Check if tzdata is installed BEFORE touching ZoneInfo -------------
    try:
        import tzdata  # noqa: F401
    except ImportError:
        print("\n⚠  Missing timezone data on this system")
        print("   Python could not find any IANA timezone database.")
        print("   This usually means the 'tzdata' package is not installed.")
        print("\n   To fix this, run:")
        print("       pip install tzdata")
        print("\n   Or install your OS timezone package (e.g., 'tzdata' on Linux).")
        print("   After installing, re-run NoctiCycle.\n")
        raise RuntimeError("Timezone data not found (tzdata missing).")

    # --- Validate the user-provided timezone (safe now) --------------------
    try:
        ZoneInfo(TZ)
    except Exception:
        print("\n⚠  Invalid timezone in configuration")
        print(f"   You provided: '{TZ}'")
        print("   This is not a recognized IANA timezone identifier.")
        print("\n   Examples of valid timezones include:")
        print("     - America/Halifax")
        print("     - America/New_York")
        print("     - Europe/London")
        print("     - Asia/Tokyo")
        print("\n   Please update the TZ variable and try again.\n")
        raise ValueError(f"Invalid timezone: '{TZ}'")

    # --- Validate CITY -----------------------------------------------------
    if not CITY or not CITY.strip():
        print("\n⚠  CITY cannot be empty.")
        print("   Please set CITY to a real location name, e.g. 'Halifax'.\n")
        raise ValueError("CITY cannot be empty.")

    if any(char.isdigit() for char in CITY):
        print("\n⚠  CITY contains digits")
        print(f"   You provided: '{CITY}'")
        print("   City names should not contain numbers.")
        print("   Example: 'Halifax', 'Toronto', 'Vancouver'\n")
        raise ValueError(f"Invalid CITY value: '{CITY}'")

    # Optional: warn about capitalization
    if CITY != CITY.title():
        print(f"\nℹ  Note: CITY '{CITY}' is not capitalized normally.")
        print(f"   Consider using '{CITY.title()}' for nicer output.\n")

    return True


def parse_cli_args():
    """
    Parse command-line arguments for NoctiCycle.

    This function defines the command-line interface for the lunar calendar
    generator. Only --city is required: --tz is detected from the city's
    coordinates when omitted, and --year defaults to the current year.
    Optional flags that override the default global configuration
    values defined in the script.

    Required arguments
    ------------------
    --city : str
        The display name of the city (e.g., "Halifax").

    Optional location/time arguments
    --------------------------------
    --tz : str
        The IANA timezone identifier (e.g., "America/Halifax"). Detected
        automatically from the geocoded coordinates when omitted.
    --year : int
        The calendar year to generate (default: the current year).

    Optional flags
    --------------
    --show-luminance / --hide-luminance : bool
        Enable or disable moon illumination percentage display.

    --show-event-time / --hide-event-time : bool
        Enable or disable event time display for lunar phases.

    --exact-event-illumination / --midnight-illumination : bool
        Choose whether illumination is computed at the exact event moment
        or at local midnight.

    --show-rise-set-time : bool
        Enable or disable showing moonrise and moon set times

    --show-quarters : bool
        Mark first-quarter and last-quarter days in the calendar.

    --ics [PATH] : str
        Also write the new, quarter and full moon events as an iCalendar
        (.ics) file that can be imported or subscribed to in calendar apps.

    --print-format : bool
        Use a simplified, print‑friendly layout. When this flag is present,
        cosmetic styling and enhanced visual elements are disabled. The
        default behavior (without this flag) is to use the full cosmetic
        layout.

    --paper : str
        Paper size used by --print-format (letter, a4, legal, tabloid).

    --print-style : str
        Dark-side rendering for --print-format (grey, hatched, solid).

    --print-layout : str
        Print orientation: rows (one month per row) or columns (one month
        per column).

    --output / -o : str
        Optional full path to the output HTML file.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with attributes corresponding to each CLI option.
    """
    parser = argparse.ArgumentParser(
        description="Generate a full-year lunar calendar with NoctiCycle."
    )

    # Required
    parser.add_argument(
        "--city",
        required=True,
        help="City name for display (e.g., 'Halifax')."
    )
    parser.add_argument(
        "--tz",
        default=None,
        help="IANA timezone (e.g., 'America/Halifax'). Optional: when omitted "
             "it is detected from the city's coordinates."
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Year to generate the lunar calendar for (default: current year)."
    )

    # Optional overrides
    parser.add_argument("--show-luminance", action="store_true",
                        help="Force-enable moon illumination display.")
    parser.add_argument("--hide-luminance", action="store_true",
                        help="Disable moon illumination display.")

    parser.add_argument("--show-event-time", action="store_true",
                        help="Force-enable event time display.")
    parser.add_argument("--hide-event-time", action="store_true",
                        help="Disable event time display.")

    parser.add_argument("--exact-event-illumination", action="store_true",
                        help="Compute illumination at exact event time.")
    parser.add_argument("--midnight-illumination", action="store_true",
                        help="Compute illumination at local midnight.")

    parser.add_argument("--illumination-trend", action="store_true",
                        help="Enable per-day illumination trend sparkline (default: off)")

    parser.add_argument("--show-rise-set-times", action="store_true",
                        help="Display moonrise and moonset times for each day.")

    parser.add_argument("--show-quarters", action="store_true",
                        help="Mark first-quarter and last-quarter days (with their times).")

    parser.add_argument("--ics", nargs="?", const="auto", default=None, metavar="PATH",
                        help="Also export new/quarter/full moon events as an .ics calendar "
                             "file (default path: next to the HTML file).")

    parser.add_argument("-o", "--output",type=str,
                        help="Optional full path to the output HTML file."
    )



    # Print‑friendly mode (disables cosmetics)
    parser.add_argument(
        "--print-format",
        action="store_true",
        help="Use a simplified layout suitable for printing."
    )
    parser.add_argument(
        "--print-style",
        choices=("grey", "hatched", "solid"),
        default="grey",
        help="How the dark side of the moon is drawn with --print-format: "
             "light grey (default), diagonal hatching (best on black-and-white "
             "printers) or solid black."
    )
    parser.add_argument(
        "--print-layout",
        choices=("rows", "columns"),
        default="rows",
        help="Print orientation: 'rows' puts one month per row (largest moons, "
             "default); 'columns' puts one month per column and days down the page "
             "(planner style)."
    )
    parser.add_argument(
        "--paper",
        choices=sorted(PAPER_SIZES),
        default="letter",
        help="Paper size for --print-format; the year is fitted on one "
             "landscape page of this size (default: letter)."
    )

    return parser.parse_args()


def apply_cli_to_globals(args):
    """
    Apply command-line argument values to the module's global configuration
    variables.

    This function updates the global configuration based on CLI input.
    Required parameters always overwrite the defaults. Optional flags only
    override their corresponding global values if explicitly provided.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments from `parse_cli_args()`.

    Effects
    -------
    Updates the following global variables:
        CITY : str
            Display name of the selected location.
        TZ : str
            IANA timezone identifier for the chosen location.
        YEAR : int
            Calendar year to generate.
        SHOW_LUMINANCE : bool
            Whether to display moon illumination percentages.
        SHOW_EVENT_TIME : bool
            Whether to display exact event times for lunar phases.
        SHOW_RISE_SET_TIMES : bool
            Whether to display moonrise and moonset times.
        USE_EXACT_EVENT_ILLUMINATION : bool
            Whether illumination on event days is computed at the exact
            event moment instead of local midnight.
        COSMETICS_MODE : bool
            Controls whether the enhanced visual layout is used. Cosmetics
            are enabled by default; they are disabled only when the
            --print-format flag is provided.
    """

    global CITY, TZ, YEAR, BASE_DIR
    global SHOW_LUMINANCE, SHOW_EVENT_TIME
    global USE_EXACT_EVENT_ILLUMINATION, ILLUMINATION_TREND, SHOW_RISE_SET_TIMES, COSMETICS_MODE
    global SHOW_QUARTERS, PAPER, PRINT_STYLE, PRINT_LAYOUT

    # Required
    CITY = args.city
    TZ = args.tz            # may be None: resolved later from the coordinates
    YEAR = args.year if args.year is not None else date.today().year

    # Optional overrides
    if args.show_luminance:
        SHOW_LUMINANCE = True
    if args.hide_luminance:
        SHOW_LUMINANCE = False

    if args.show_event_time:
        SHOW_EVENT_TIME = True
    if args.hide_event_time:
        SHOW_EVENT_TIME = False

    if args.exact_event_illumination:
        USE_EXACT_EVENT_ILLUMINATION = True
    if args.midnight_illumination:
        USE_EXACT_EVENT_ILLUMINATION = False

    SHOW_RISE_SET_TIMES = args.show_rise_set_times
    SHOW_QUARTERS = args.show_quarters
    PAPER = args.paper
    PRINT_STYLE = args.print_style
    PRINT_LAYOUT = args.print_layout

    # Default is already True at the top of the script.
    # If print-format is requested, disable cosmetics.
    if args.print_format:
        COSMETICS_MODE = False

    ILLUMINATION_TREND = args.illumination_trend

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class LocationError(RuntimeError):
    """Raised when the city cannot be turned into coordinates or a timezone."""


def geocode_candidates(name: str, limit: int = 5) -> list:
    """Return up to `limit` Nominatim matches for a place name.

    Network and service problems are converted into a LocationError with a
    message the user can act on.
    """
    from geopy.exc import GeopyError

    geolocator = Nominatim(user_agent="nocticycle", timeout=10)
    try:
        matches = geolocator.geocode(name, exactly_one=False, limit=limit)
    except GeopyError as exc:
        raise LocationError(
            f"Could not reach the geocoding service while looking up '{name}' "
            f"({exc.__class__.__name__}). Check your internet connection and try again."
        ) from exc

    if not matches:
        raise LocationError(
            f"No place found for '{name}'. Try adding the country or region, "
            f"e.g. --city \"{name}, Canada\"."
        )
    return list(matches)


def choose_candidate(name: str, matches: list):
    """Pick one geocoding match, asking the user when the name is ambiguous.

    Without an interactive terminal the best match is used and the other
    candidates are listed so the user can refine the query.
    """
    if len(matches) == 1:
        return matches[0]

    print(f"\nSeveral places match '{name}':")
    for i, m in enumerate(matches, 1):
        print(f"  {i}) {m.address}")

    if sys.stdin.isatty() and sys.stdout.isatty():
        while True:
            answer = input(f"Choose 1-{len(matches)} [1]: ").strip() or "1"
            if answer.isdigit() and 1 <= int(answer) <= len(matches):
                print()
                return matches[int(answer) - 1]
            print("  Please enter one of the listed numbers.")

    print("  Using the first match. Add a country/region to --city to pick another.\n")
    return matches[0]


def geocode_city(name: str) -> tuple[float, float]:
    """
    Resolve a human-readable city name into geographic coordinates.

    Uses OpenStreetMap Nominatim (via `geopy`). When several places match,
    the user is asked to choose in an interactive terminal; otherwise the
    best match is used.

    Parameters
    ----------
    name : str
        The city name provided by the user (e.g., "Halifax", "New York").

    Returns
    -------
    tuple[float, float]
        A pair `(lat, lon)` in decimal degrees.

    Raises
    ------
    LocationError
        If the service is unreachable or no place matches the name.
    """
    loc = choose_candidate(name, geocode_candidates(name))
    return loc.latitude, loc.longitude


def detect_timezone(lat: float, lon: float) -> str:
    """Return the IANA timezone identifier for a coordinate pair.

    Requires the optional `timezonefinder` package.
    """
    try:
        from timezonefinder import TimezoneFinder
    except ImportError as exc:
        raise LocationError(
            "Automatic timezone detection needs the 'timezonefinder' package.\n"
            "   Install it with:  pip install timezonefinder\n"
            "   or pass the timezone yourself with --tz (e.g. --tz America/Halifax)."
        ) from exc

    tz_name = TimezoneFinder().timezone_at(lat=lat, lng=lon)
    if not tz_name:
        raise LocationError(
            f"Could not determine the timezone at ({lat:.3f}, {lon:.3f}). "
            "Please pass it with --tz."
        )
    return tz_name


def resolve_location() -> None:
    """Geocode CITY once and fill LAT, LON and OBSERVER."""
    global LAT, LON, OBSERVER
    LAT, LON = geocode_city(CITY)
    OBSERVER = wgs84.latlon(LAT, LON)


def initialize_observer():
    """
    Make sure the Skyfield observer used for rise/set calculations exists.

    The CITY is geocoded on demand (see `resolve_location`); when the
    location was already resolved earlier in the run nothing is repeated.

    Raises
    ------
    LocationError
        If the CITY cannot be resolved into coordinates.
    """
    if OBSERVER is None:
        resolve_location()

def load_css(style: str) -> str:
    """
    Load and validate a CSS stylesheet from the project's `css/` directory.

    This function supports the theme system by reading external `.css`
    files such as `css/print.css`, `css/default.css`, or any future
    theme file. The selected stylesheet is returned as a raw string and
    later injected directly into the generated HTML inside a <style>
    block, keeping the final document fully self‑contained and printable.

    The function performs lightweight validation to catch common
    mistakes early (such as empty files, accidental HTML markup, or
    corrupted binary content) without attempting full CSS parsing.

    Parameters
    ----------
    style : str
        The name of the CSS theme to load (e.g., "default", "print").
        The function will automatically construct the full path:
        `<script_dir>/css/<style>.css`.

    Returns
    -------
    str
        The validated CSS content exactly as stored on disk.

    Raises
    ------
    FileNotFoundError
        If the CSS file does not exist.

    ValueError
        If the file is empty, contains HTML markup, appears corrupted,
        or does not contain any valid CSS blocks.

    OSError
        If the file cannot be read due to permissions or I/O errors.

    Notes
    -----
    • Validation is intentionally minimal: it checks for structural
      sanity but does not attempt to enforce CSS correctness.

    • This function ensures that theme files are safe to embed inline
      in the final HTML output.

    • Additional themes can be added simply by placing new `.css`
      files in the `css/` directory.
    """
    import os

    global BASE_DIR

    css_path = os.path.join(BASE_DIR, "css", f"{style}.css")

    # --- Read file ---
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # --- Validation rules ---

    # 1. Must not be empty or whitespace-only
    if not css.strip():
        raise ValueError(f"CSS file '{css_path}' is empty or whitespace-only.")

    # 2. Must not contain HTML tags (common mistake when editing)
    lowered = css.lower()
    forbidden_html = ("<html", "<body", "<head", "<style", "<script")
    if any(tag in lowered for tag in forbidden_html):
        raise ValueError(
            f"CSS file '{css_path}' appears to contain HTML or script markup. "
            "CSS files must contain only raw CSS rules."
        )

    # 3. Must contain at least one CSS block
    if "{" not in css or "}" not in css:
        raise ValueError(
            f"CSS file '{css_path}' does not appear to contain any CSS blocks."
        )

    # 4. Detect null bytes or binary garbage
    if "\x00" in css:
        raise ValueError(
            f"CSS file '{css_path}' contains null bytes and may be corrupted."
        )

    # 5. Warn about extremely large CSS files
    if len(css) > 500_000:  # 500 KB threshold
        raise ValueError(
            f"CSS file '{css_path}' is unexpectedly large and may be invalid."
        )

    return css

def validate_output_path(path: str) -> str:
    """
    Validate that the user‑provided output path is a writable HTML file.

    This function is used to support the optional `-o/--output` CLI
    argument, allowing the user to specify a custom output location for
    the generated HTML file. The function ensures that the path is
    syntactically valid, points to an existing directory, and that the
    file can be created or overwritten.

    Parameters
    ----------
    path : str
        Full filesystem path to the desired output HTML file. The path
        must end with `.html` or `.htm`. Relative paths are resolved to
        absolute paths.

    Returns
    -------
    str
        The normalized absolute path to the output file, guaranteed to
        be writable.

    Raises
    ------
    ValueError
        If the path does not end with `.html`/`.htm`, if the directory
        does not exist, or if the file cannot be created due to
        permission or I/O issues.

    Notes
    -----
    • This function does not create the file; it only verifies that it
      *can* be created.

    • Directory existence is required; directories are not created
      automatically.

    • Write permission is checked using `os.access()` and by attempting
      to open the file in append mode.

    • The returned path is always absolute, even if the user supplied a
      relative path.
    """
    import os

    # Must end with .html or .htm
    if not path.lower().endswith((".html", ".htm")):
        raise ValueError("Output file must end with .html or .htm")

    abs_path = os.path.abspath(path)
    directory = os.path.dirname(abs_path)

    # Directory must exist
    if not os.path.isdir(directory):
        raise ValueError(f"Directory does not exist: {directory}")

    # Directory must be writable
    if not os.access(directory, os.W_OK):
        raise ValueError(f"No write permission in directory: {directory}")

    # Attempt to open the file (append mode does not destroy contents)
    try:
        with open(abs_path, "a", encoding="utf-8"):
            pass
    except Exception as e:
        raise ValueError(f"Cannot create output file: {e}")

    return abs_path


# ----------------------------------------
# PHASE EVENTS (for bands + names)
# ----------------------------------------


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

    global QUARTER_EVENTS_GLOBAL

    events: List[PhaseEvent] = []
    quarters: List[PhaseEvent] = []
    for t, phase in zip(times, phases):
        utc_dt = t.utc_datetime().replace(tzinfo=ZoneInfo("UTC"))
        local_dt = utc_dt.astimezone(TZINFO)

        if phase in (1, 3):  # 1=first quarter, 3=last quarter
            kind = "first_quarter" if phase == 1 else "last_quarter"
            quarters.append(PhaseEvent(kind, local_dt.date(), local_dt))
            continue

        kind = "new" if phase == 0 else "full"
        events.append(PhaseEvent(kind, local_dt.date(), local_dt))

    events.sort(key=lambda e: e.date)
    quarters.sort(key=lambda e: e.dt)
    QUARTER_EVENTS_GLOBAL = quarters

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
    t0 = ts.from_datetime(datetime(d.year, d.month, d.day, 0, 0, tzinfo=TZINFO))
    t1 = ts.from_datetime(datetime(d.year, d.month, d.day, 23, 59, tzinfo=TZINFO))

    f = almanac.risings_and_settings(eph, eph['moon'], OBSERVER)
    times, events = almanac.find_discrete(t0, t1, f)

    rise = None
    set_ = None

    for t, e in zip(times, events):
        local = t.utc_datetime().replace(tzinfo=ZoneInfo("UTC")).astimezone(TZINFO)
        if e == 1:   # rising
            rise = local.strftime("%H:%M")
        else:        # setting
            set_ = local.strftime("%H:%M")

    return rise, set_

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


def render_moon_svg(phase: float, size: int = 24, mirror: bool = False) -> str:
    """Render an SVG moon icon for a given lunar phase.

    Parameters
    ----------
    phase : float
        Lunation fraction (0.0 = new, 0.5 = full).
    size : int, optional
        Width and height of the SVG viewport in pixels. Default is 24.
    mirror : bool, optional
        Flip the icon horizontally. Seen from the southern hemisphere the
        Moon appears upside down, so the lit side of a waxing moon is on
        the left. Default is False (northern-hemisphere view).

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

    body = f'{outline}{"".join(paths)}'
    if mirror:
        body = f'<g transform="translate({size},0) scale(-1,1)">{body}</g>'

    return f'<svg class="moon-svg" viewBox="0 0 {size} {size}">{body}</svg>'


def is_southern_hemisphere() -> bool:
    """True when the geocoded location lies south of the equator."""
    return LAT is not None and LAT < 0

def render_illumination_sparkline(values: list[float], width: int = 80, height: int = 18) -> str:
    """
    Render a compact SVG Bézier-curve sparkline representing illumination trends.

    The curve is colored based on waxing or waning behavior:
        • Waxing  → teal (#88c0d0)
        • Waning  → amber (#d08770)

    Parameters
    ----------
    values : list of float
        Illumination percentages (0–100) sampled over several days.
    width : int, optional
        Width of the SVG viewport in pixels. Default is 80.
    height : int, optional
        Height of the SVG viewport in pixels. Default is 18.

    Returns
    -------
    str
        SVG markup containing a smoothed Bézier curve sparkline.
    """
    if not values:
        return ""

    n = len(values)
    if n == 1:
        x = width / 2
        y = height - (values[0] / 100.0) * height
        return (
            f'<svg class="illum-graph" viewBox="0 0 {width} {height}">'
            f'<circle cx="{x}" cy="{y}" r="2" fill="#88c0d0" />'
            f'</svg>'
        )

    # Determine waxing vs waning
    waxing = values[-1] > values[0]
    color = "#88c0d0" if waxing else "#d08770"   # teal vs amber

    # Convert values to coordinates
    step_x = width / (n - 1)
    pts = []
    for i, v in enumerate(values):
        x = i * step_x
        y = height - (v / 100.0) * height
        pts.append((x, y))

    # Build a smooth cubic Bézier path
    d = f"M {pts[0][0]:.2f},{pts[0][1]:.2f} "

    for i in range(1, n):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        cx = (x0 + x1) / 2
        d += f"C {cx:.2f},{y0:.2f} {cx:.2f},{y1:.2f} {x1:.2f},{y1:.2f} "

    return (
        f'<svg class="illum-graph" viewBox="0 0 {width} {height}">'
        f'<path d="{d}" stroke="{color}" stroke-width="1.8" fill="none" />'
        f'</svg>'
    )



# ----------------------------------------
# DAY DETAILS (embedded in the page for the interactive layer)
# ----------------------------------------

SYNODIC_MONTH = 29.530588

def phase_name_for_date(d: date, frac: float) -> str:
    """Return the descriptive phase name (e.g. "Waxing Crescent") for a day.

    Exact event days (new, first quarter, full, last quarter) win over the
    fraction-based name, so the label always agrees with the event markers.
    """
    for ev in EVENTS_GLOBAL or []:
        if ev.date == d:
            return "New Moon" if ev.kind == "new" else "Full Moon"
    for ev in QUARTER_EVENTS_GLOBAL:
        if ev.date == d:
            return "First Quarter" if ev.kind == "first_quarter" else "Last Quarter"

    if frac < 0.25:
        return "Waxing Crescent"
    if frac < 0.5:
        return "Waxing Gibbous"
    if frac < 0.75:
        return "Waning Gibbous"
    return "Waning Crescent"


def moon_age_days(d: date) -> float | None:
    """Days elapsed since the last new moon, measured at local noon of `d`."""
    noon = datetime(d.year, d.month, d.day, 12, 0, tzinfo=TZINFO)
    previous = [ev for ev in EVENTS_GLOBAL or [] if ev.kind == "new" and ev.dt <= noon]
    if not previous:
        return None
    return round((noon - previous[-1].dt).total_seconds() / 86400, 1)


def js_json(obj) -> str:
    """Serialise `obj` as JSON that is safe to embed inside a <script> tag."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def load_js(name: str) -> str:
    """Read an inline script from the project's `js/` directory."""
    with open(os.path.join(BASE_DIR, "js", f"{name}.js"), "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------------------
# ICS EXPORT
# ----------------------------------------

ICS_EVENT_LABELS = {
    "new": "\U0001F311 New Moon",
    "first_quarter": "\U0001F313 First Quarter",
    "full": "\U0001F315 Full Moon",
    "last_quarter": "\U0001F317 Last Quarter",
}


def build_ics(year: int) -> str:
    """Build an iCalendar document with the year's new/quarter/full moons.

    Event times are written in UTC, so calendar apps show them in the
    viewer's own timezone. The description mentions the local time at the
    calendar's city.
    """
    utc = ZoneInfo("UTC")
    stamp = datetime.now(utc).strftime("%Y%m%dT%H%M%SZ")

    moments = [
        ev for ev in list(EVENTS_GLOBAL or []) + list(QUARTER_EVENTS_GLOBAL)
        if ev.dt.year == year
    ]
    moments.sort(key=lambda e: e.dt)

    def esc(text: str) -> str:
        return (text.replace("\\", "\\\\").replace(";", "\\;")
                    .replace(",", "\\,").replace("\n", "\\n"))

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//NoctiCycle//Lunar Calendar//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{esc(f'NoctiCycle {year} - {CITY}')}",
    ]
    for ev in moments:
        start = ev.dt.astimezone(utc)
        end = start + timedelta(minutes=30)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{ev.kind}-{start.strftime('%Y%m%dT%H%M%SZ')}@nocticycle",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{esc(ICS_EVENT_LABELS[ev.kind])}",
            f"DESCRIPTION:{esc(f'Local time in {CITY}: ' + ev.dt.strftime('%Y-%m-%d %H:%M %Z'))}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def write_ics(year: int, output_path: str) -> None:
    """Write the year's moon events to `output_path` as an .ics file."""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(build_ics(year))
    print(f"Generated {output_path}")

# ----------------------------------------
# HTML GENERATION
# ----------------------------------------

def month_name(m: int) -> str:
    """
    Return the month name for a given month number.

    This helper adapts its output based on the active rendering mode:
    - When COSMETICS_MODE is enabled, the full month name is used
      (e.g., "January", "February").
    - When COSMETICS_MODE is disabled (print‑friendly mode), the
      abbreviated three‑letter form is used (e.g., "Jan", "Feb").

    Parameters
    ----------
    m : int
        Month number in the range 1–12.

    Returns
    -------
    str
        The formatted month name, full or abbreviated depending on
        the current cosmetic mode.
    """
    if COSMETICS_MODE:
        return date(2000, m, 1).strftime("%B")   # Full month name
    else:
        return date(2000, m, 1).strftime("%b")   # Abbreviated name

def write_html(year: int, output_path: str) -> None:
    """Generate the full lunar calendar HTML document for a given year.

    This function orchestrates:
    - computing lunar phase events,
    - assigning daily phases,
    - rendering SVG moon icons,
    - and assembling the complete HTML output.

    The resulting HTML file is written to disk at the path specified in output_path

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

    if not COSMETICS_MODE:
        write_print_html(year, output_path, events, events_by_month)
        return

    css = load_css("default")

    html = f"""
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lunar Calendar {year} – {CITY}</title>
<style>
{css}
</style>
</head>
<body>

<h1>Lunar Calendar {year} – {CITY}</h1>"""

    day_data: Dict[str, dict] = {}

    if COSMETICS_MODE:
        html += '<div id="next-events" class="next-events" hidden></div>'

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
                <div class="weekdays" aria-hidden="true">
                    <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span>
                </div>
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

        # Row 2: moon icons + brightness + SPARKLINE
        html += "<tr>"
        for d in range(1, 32):
            if d <= days:
                day_date = date(year, m, d)

                frac = moon_phase_fraction(day_date)
                moon_svg = render_moon_svg(frac, size=24, mirror=is_southern_hemisphere())
                event_time_str, illum = moon_illumination_percent(day_date)

                trend_svg = ""
                if COSMETICS_MODE and ILLUMINATION_TREND:
                    trend_values = illumination_trend_for_date(day_date, window=3)
                    trend_svg = render_illumination_sparkline(trend_values)

                time_class = "phase-time"
                if not SHOW_EVENT_TIME:
                    time_class += " hidden"

                # Sunday-first weekday index; only used by the narrow-screen grid
                # layout to offset the first day of the month.
                dow = (day_date.weekday() + 1) % 7
                html += (
                    f"<td class='day-cell' data-date='{day_date.isoformat()}' "
                    f"data-phase='{phases[d].split()[0].lower()}' style='--dow:{dow}'>"
                )

                if COSMETICS_MODE:
                    html += f"<div class='day-number'>{d}</div>"

                html += "<div class='moon-wrapper'>"
                html += moon_svg

                if SHOW_LUMINANCE:
                    html += f"<div class='brightness'>{illum}%</div>"

                rise = set_ = None
                if SHOW_RISE_SET_TIMES:
                    rise, set_ = moon_rise_set_times(day_date)
                    rise_set_html = (
                        f'<div class="rise-set">'
                        f'↑ {rise if rise else "--"}<br />'
                        f'↓ {set_ if set_ else "--"}'
                        f'</div>'
                    )
                else:
                    rise_set_html = ""

                # NEW: insert sparkline here
                if COSMETICS_MODE and ILLUMINATION_TREND:
                    html += trend_svg

                html += f"<div class='{time_class}'>{event_time_str}</div>"

                if SHOW_QUARTERS:
                    quarter = next((q for q in QUARTER_EVENTS_GLOBAL if q.date == day_date), None)
                    if quarter:
                        label = "1st Qtr" if quarter.kind == "first_quarter" else "Last Qtr"
                        html += (
                            f"<div class='quarter-mark'><span class='qm-label'>{label}</span>"
                            f"<span class='qm-time'>{quarter.dt.strftime('%H:%M')}</span></div>"
                        )

                html += f"""{rise_set_html}"""

                day_data[day_date.isoformat()] = {
                    "n": phase_name_for_date(day_date, frac),
                    "i": illum,
                    "a": moon_age_days(day_date),
                    "e": event_time_str,
                    "r": rise or "",
                    "s": set_ or "",
                }

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

    if COSMETICS_MODE:
        page_data = {
            "year": year,
            "city": CITY,
            "tz": TZ,
            "riseSet": bool(SHOW_RISE_SET_TIMES),
            "events": sorted(
                (
                    {"kind": ev.kind, "iso": ev.dt.isoformat()}
                    for ev in list(events) + list(QUARTER_EVENTS_GLOBAL)
                ),
                key=lambda e: e["iso"],
            ),
            "days": day_data,
        }
        html += (
            f'<script id="nocticycle-data" type="application/json">{js_json(page_data)}</script>'
            f"<script>\n{load_js('calendar')}\n</script>"
        )

    html += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {output_path}")




# ----------------------------------------
# PRINT LAYOUT (one landscape page per year)
# ----------------------------------------

PRINT_MARGIN_IN = 0.35
PRINT_TITLE_IN = 0.3
PRINT_LABEL_IN = 0.6


# Diagonal hatching used for the dark side of the moon in --print-style hatched.
# The icons use a 24-unit viewBox, so the pattern is expressed in those units.
PRINT_HATCH_DEFS = (
    '<svg width="0" height="0" style="position:absolute"><defs>'
    '<pattern id="nc-hatch" width="2.4" height="2.4" patternUnits="userSpaceOnUse" '
    'patternTransform="rotate(45)">'
    '<rect width="2.4" height="2.4" fill="#fff"/>'
    '<line x1="0" y1="0" x2="0" y2="2.4" stroke="#000" stroke-width="1.1"/>'
    '</pattern></defs></svg>'
)

def print_legend_html() -> str:
    """Legend for the markers used in the print calendar."""
    quarter = (
        '<span class="lg"><i class="lg-pill quarter">1</i>Quarter</span>'
        if SHOW_QUARTERS else ""
    )
    return (
        '<div class="legend">'
        '<span class="lg"><i class="lg-bar wax"></i>Waxing</span>'
        '<span class="lg"><i class="lg-bar wan"></i>Waning</span>'
        '<span class="lg"><i class="lg-pill major">1</i>New / full moon</span>'
        f'{quarter}'
        '</div>\n'
    )


PRINT_EVENT_ITEM_IN = 0.78      # width reserved for one "Jan 3 05:02" item
PRINT_EVENT_LINE_IN = 0.115
PRINT_LEGEND_IN = 0.2
PRINT_HEAD_IN = 0.2             # month-name header row in the columns layout
WEEKDAY_INITIALS = "MTWTFSS"


def print_events(year: int, events) -> list:
    """Events listed in the print footer: new/full, plus quarters if enabled."""
    moments = [e for e in events if e.dt.year == year]
    if SHOW_QUARTERS:
        moments += [q for q in QUARTER_EVENTS_GLOBAL if q.dt.year == year]
    return sorted(moments, key=lambda e: e.dt)


def print_geometry(n_events: int) -> dict:
    """Compute physical sizes (inches/points) so the year fits one page.

    Everything printed is sized from the paper dimensions, so the layout
    scales to any supported paper instead of relying on the browser to
    shrink an oversized table.
    """
    width, height = PAPER_SIZES[PAPER]
    usable_w = width - 2 * PRINT_MARGIN_IN
    usable_h = height - 2 * PRINT_MARGIN_IN

    per_line = max(1, int(usable_w / PRINT_EVENT_ITEM_IN))
    lines = -(-n_events // per_line) if n_events else 0
    footer = PRINT_LEGEND_IN + lines * PRINT_EVENT_LINE_IN + 0.06

    if PRINT_LAYOUT == "rows":
        col = (usable_w - PRINT_LABEL_IN) / 31
        row = (usable_h - PRINT_TITLE_IN - footer) / 12
        moon = min(col * 0.9, row * 0.46)
        # Stacked cell: weekday (0.85) + number (1) + illumination (1) lines + moon.
        font_pt = min(9.0, col * 72 * 0.27, (row * 72 * 0.94 - moon * 72) / 2.85)
    else:
        col = usable_w / 12
        row = (usable_h - PRINT_TITLE_IN - footer - PRINT_HEAD_IN) / 31
        moon = row * 0.88
        font_pt = min(8.0, row * 72 * 0.5)

    return {
        "width": width, "height": height, "margin": PRINT_MARGIN_IN,
        "label": PRINT_LABEL_IN, "col": col, "row": row,
        "moon": moon, "font_pt": font_pt, "title": PRINT_TITLE_IN,
        "footer": footer, "head": PRINT_HEAD_IN,
    }


def print_page_css(g: dict) -> str:
    """Page setup and size variables for the print layout."""
    return (
        f"@page {{ size: {g['width']}in {g['height']}in; margin: {g['margin']}in; }}\n"
        ":root {\n"
        f"  --label-w: {g['label']:.3f}in;\n"
        f"  --col-w: {g['col']:.4f}in;\n"
        f"  --row-h: {g['row']:.4f}in;\n"
        f"  --moon: {g['moon']:.4f}in;\n"
        f"  --fs: {g['font_pt']:.2f}pt;\n"
        f"  --title-h: {g['title']}in;\n"
        f"  --head-h: {g['head']}in;\n"
        "}\n"
    )


def print_cell(year: int, m: int, d: int, phases: dict, major_days: set,
               quarter_days: set, mirror: bool) -> str:
    """Return the <td> for one day of the print calendar (blank past month end)."""
    if d > monthrange(year, m)[1]:
        return "<td class='blank'></td>"

    day_date = date(year, m, d)
    frac = moon_phase_fraction(day_date)
    _, illum = moon_illumination_percent(day_date)

    classes = ["day"]
    if day_date.weekday() >= 5:
        classes.append("we")
    if day_date in major_days:
        classes.append("key-major")
    elif day_date in quarter_days:
        classes.append("key-quarter")
    elif phases[d] == "Waxing":
        classes.append("wax")
    elif phases[d] == "Waning":
        classes.append("wan")

    html = f"<td class='{' '.join(classes)}'>"
    html += f"<span class='wd'>{WEEKDAY_INITIALS[day_date.weekday()]}</span>"
    html += f"<span class='dn'>{d}</span>"
    html += render_moon_svg(frac, size=24, mirror=mirror)
    if SHOW_LUMINANCE:
        html += f"<span class='il'>{round(illum)}</span>"
    html += "</td>"
    return html


def print_events_html(moments: list, mirror: bool) -> str:
    """Footer list of exact event times, each with a small phase icon."""
    icon_phase = {"new": 0.0, "first_quarter": 0.2501, "full": 0.5, "last_quarter": 0.7501}
    items = []
    for ev in moments:
        icon = render_moon_svg(icon_phase[ev.kind], size=24, mirror=mirror)
        items.append(
            f"<span class='ev'>{icon}{ev.dt.strftime('%b')} {ev.dt.day} "
            f"<b>{ev.dt.strftime('%H:%M')}</b></span>"
        )
    return f"<div class='events'>{''.join(items)}</div>\n"


def write_print_html(year: int, output_path: str, events, events_by_month) -> None:
    """Write the print-format calendar: the whole year on one landscape page."""
    moments = print_events(year, events)
    g = print_geometry(len(moments))
    css = load_css("print") + "\n" + print_page_css(g)
    mirror = is_southern_hemisphere()

    quarter_days = {q.date for q in QUARTER_EVENTS_GLOBAL} if SHOW_QUARTERS else set()
    major_days = {e.date for e in events}
    phases = {m: assign_daily_phases(year, m, events, events_by_month) for m in range(1, 13)}

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Lunar Calendar {year} – {CITY}</title>
<style>
{css}
</style>
</head>
<body class="ps-{PRINT_STYLE} layout-{PRINT_LAYOUT}">
{PRINT_HATCH_DEFS if PRINT_STYLE == "hatched" else ""}
<h1>Lunar Calendar {year} – {CITY}</h1>
<table class="year">
"""

    if PRINT_LAYOUT == "rows":
        html += '<colgroup><col class="c-label"><col span="31" class="c-day"></colgroup>\n'
        for m in range(1, 13):
            html += f"<tr><th class='month'>{month_name(m)}</th>"
            for d in range(1, 32):
                html += print_cell(year, m, d, phases[m], major_days, quarter_days, mirror)
            html += "</tr>\n"
    else:
        html += '<colgroup><col span="12" class="c-month"></colgroup>\n<tr class="head">'
        for m in range(1, 13):
            html += f"<th class='month'>{month_name(m)}</th>"
        html += "</tr>\n"
        for d in range(1, 32):
            html += "<tr>"
            for m in range(1, 13):
                html += print_cell(year, m, d, phases[m], major_days, quarter_days, mirror)
            html += "</tr>\n"

    html += "</table>\n"
    html += print_legend_html()
    html += print_events_html(moments, mirror)
    html += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {output_path}")


# ----------------------------------------
# MAIN
# ----------------------------------------

#def main():
if __name__ == "__main__":

    args = parse_cli_args()
    apply_cli_to_globals(args)

    if args.output:
        try:
            output_path = validate_output_path(args.output)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        output_path = os.path.join(BASE_DIR, f"lunar_calendar_{CITY}_{YEAR}.html")

    # Resolve the location first: it provides the timezone when --tz is
    # omitted and the hemisphere used to orient the moon icons.
    tz_given = TZ is not None
    try:
        resolve_location()
        if not tz_given:
            TZ = detect_timezone(LAT, LON)
            print(f"Detected timezone: {TZ}")
    except LocationError as e:
        if tz_given and not SHOW_RISE_SET_TIMES:
            print(f"\n⚠  {e}")
            print("   Continuing without coordinates (moon icons use the northern-hemisphere orientation).\n")
        else:
            print(f"\nError: {e}")
            sys.exit(1)

    validate_config()

    TZINFO = ZoneInfo(TZ)

    print(f"Generating lunar calendar for {YEAR} — {CITY}")
    print(f"Timezone: {TZ}")

    events, events_by_month = compute_phase_events_for_year(YEAR)

    write_html(
        YEAR,
        output_path
    )

    if args.ics:
        if args.ics == "auto":
            ics_path = os.path.splitext(output_path)[0] + ".ics"
        else:
            ics_path = os.path.abspath(os.path.expanduser(args.ics))
            if not ics_path.lower().endswith(".ics"):
                print(f"Error: --ics path must end in .ics (got '{args.ics}')")
                sys.exit(1)
        try:
            write_ics(YEAR, ics_path)
        except OSError as e:
            print(f"Error: could not write '{ics_path}': {e}")
            sys.exit(1)

    print("Done.")




