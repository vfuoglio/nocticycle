"""Solar computations: the 24 solar terms (Sun's ecliptic longitude in 15° steps).

Solstices and equinoxes are the terms at 270°, 90°, 0° and 180°; the East Asian
calendar uses all 24. Results are cached per (year, timezone).
"""

from functools import lru_cache
from zoneinfo import ZoneInfo

from skyfield import almanac
from skyfield.framelib import ecliptic_frame

from . import config as cfg
from .sky import eph, ts


def _sun_term_index(t):
    """Index (0..23) of the 15° sector the Sun is in; vectorised over t."""
    earth, sun = eph["earth"], eph["sun"]
    _, lon, _ = earth.at(t).observe(sun).apparent().frame_latlon(ecliptic_frame)
    return (lon.degrees // 15).astype(int) % 24


_sun_term_index.step_days = 5


@lru_cache(maxsize=8)
def _terms(year: int, tz_name: str) -> dict:
    t0 = ts.utc(year - 1, 12, 20)
    t1 = ts.utc(year + 1, 1, 10)
    times, idx = almanac.find_discrete(t0, t1, _sun_term_index)
    out = {}
    tz = ZoneInfo(tz_name)
    for t, k in zip(times, idx):
        local = t.utc_datetime().astimezone(tz)
        if local.year == year:
            out[int(k) * 15] = local
    return out


def solar_terms(year: int, tz_name: str | None = None) -> dict:
    """Map Sun longitude (0, 15, ... 345) to the datetime it is reached in `year`.

    Times are in the calendar's timezone, or in `tz_name` when given (the
    Chinese calendar uses Asia/Shanghai).
    """
    return _terms(year, tz_name or str(cfg.TZ))
