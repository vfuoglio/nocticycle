"""Shared configuration and runtime state for NoctiCycle.

Other modules import this as ``from . import config as cfg`` and read/write
``cfg.NAME`` so that every module sees the same values.
"""

import os
from zoneinfo import ZoneInfo

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
TRADITION: str | None = None
WHEEL: str | None = None
MOON_NAMES: str | None = None

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

# Runtime state, filled in while the calendar is generated.
EVENTS_GLOBAL = None
QUARTER_EVENTS_GLOBAL: list = []
TZINFO = None

LAT: float | None = None
LON: float | None = None
OBSERVER = None



def validate_config():
    """Validate timezone and location settings with user-friendly messages."""

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
