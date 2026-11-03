"""Geocoding, timezone detection and observer setup."""

import sys
from skyfield.api import wgs84
from geopy.geocoders import Nominatim
from . import config as cfg


class LocationError(RuntimeError):
    """Raised when the city cannot be turned into coordinates or a timezone."""


def geocode_candidates(name: str, limit: int = 5) -> list:
    """Return up to `limit` Nominatim matches for a place name.

    Network and service problems are converted into a LocationError with a
    message the user can act on.
    """
    from geopy.exc import GeopyError

    kwargs = {}
    try:  # use certifi's CA bundle when available (needed in bundled builds)
        import ssl
        import certifi
        kwargs["ssl_context"] = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    geolocator = Nominatim(user_agent="nocticycle", timeout=10, **kwargs)
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
    cfg.LAT, cfg.LON = geocode_city(cfg.CITY)
    cfg.OBSERVER = wgs84.latlon(cfg.LAT, cfg.LON)


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
    if cfg.OBSERVER is None:
        resolve_location()
