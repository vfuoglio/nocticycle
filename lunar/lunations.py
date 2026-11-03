"""Lunations (new moon to new moon), blue/black moons and the Chinese lunar calendar.

A *lunation* runs from one new moon to the next and contains exactly one full
moon. The named-moon systems (``moon_names.py``) give each lunation a name.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

from skyfield import almanac

from . import config as cfg
from .sky import eph, ts
from .solar import solar_terms

CHINA_TZ = "Asia/Shanghai"


@dataclass
class Lunation:
    start: datetime          # new moon (local time)
    end: datetime            # next new moon (local time)
    full: datetime           # the full moon inside it (local time)
    blue: bool = False       # its full moon is the 2nd of its calendar month
    black_new: bool = False  # its new moon is the 2nd new moon of its calendar month

    @property
    def start_date(self) -> date:
        return self.start.date()

    @property
    def end_date(self) -> date:
        """First day of the next lunation (exclusive end)."""
        return self.end.date()


def _phase_moments(t0, t1, tz) -> tuple:
    """(new moons, full moons) between t0 and t1 as datetimes in tz."""
    f = almanac.moon_phases(eph)
    times, phases = almanac.find_discrete(t0, t1, f)
    new, full = [], []
    for t, p in zip(times, phases):
        dt = t.utc_datetime().astimezone(tz)
        if int(p) == 0:
            new.append(dt)
        elif int(p) == 2:
            full.append(dt)
    return new, full


@lru_cache(maxsize=8)
def _lunations(year: int, tz_name: str) -> tuple:
    tz = ZoneInfo(tz_name)
    new, full = _phase_moments(ts.utc(year - 1, 11, 1), ts.utc(year + 1, 3, 31), tz)
    out = []
    for a, b in zip(new, new[1:]):
        inside = [f for f in full if a <= f < b]
        if len(inside) != 1:           # cannot happen; guards against an edge-of-range gap
            continue
        out.append(Lunation(a, b, inside[0]))
    for i, lun in enumerate(out):
        if i and out[i - 1].full.year == lun.full.year and out[i - 1].full.month == lun.full.month:
            lun.blue = True
        if i and out[i - 1].start.year == lun.start.year and out[i - 1].start.month == lun.start.month:
            lun.black_new = True
    return tuple(out)


def lunations(year: int) -> list:
    """All lunations that overlap `year` (calendar timezone)."""
    return [l for l in _lunations(year, str(cfg.TZ))
            if l.end_date > date(year, 1, 1) and l.start_date <= date(year, 12, 31)]


# ---------------------------------------------------------------------------
# Chinese lunar calendar
# ---------------------------------------------------------------------------

@dataclass
class ChineseMonth:
    start: date              # first day (Beijing date)
    end: date                # first day of the next month (exclusive)
    number: int              # 1..12
    leap: bool               # leap month (the number repeats that of the month before)


@lru_cache(maxsize=8)
def _chinese_months(year: int) -> tuple:
    tz = ZoneInfo(CHINA_TZ)
    new, _ = _phase_moments(ts.utc(year - 2, 11, 1), ts.utc(year + 2, 2, 28), tz)
    starts = [d.date() for d in new]
    # Major solar terms (Sun longitude a multiple of 30 degrees), in Beijing dates.
    zhongqi = []
    for y in (year - 2, year - 1, year, year + 1):
        for lon, moment in solar_terms(y, CHINA_TZ).items():
            if lon % 30 == 0:
                zhongqi.append(moment.date())
    zhongqi.sort()
    solstices = [solar_terms(y, CHINA_TZ)[270].date() for y in (year - 2, year - 1, year, year + 1)]

    def contains(i, day):
        return starts[i] <= day < starts[i + 1]

    def has_zhongqi(i):
        return any(contains(i, z) for z in zhongqi)

    months = [None] * (len(starts) - 1)
    # The month containing the winter solstice is month 11. Number the months between two
    # successive solstice months; with 13 of them, the first without a major term is a leap month.
    sol_idx = []
    for sd in solstices:
        for i in range(len(starts) - 1):
            if contains(i, sd):
                sol_idx.append(i)
                break
    for a, b in zip(sol_idx, sol_idx[1:]):
        n = 11
        leap_done = (b - a) == 12
        months[a] = (11, False)
        for i in range(a + 1, b):
            if not leap_done and not has_zhongqi(i):
                months[i] = (n, True)
                leap_done = True
                continue
            n = n % 12 + 1
            months[i] = (n, False)
    out = []
    for i, m in enumerate(months):
        if m:
            out.append(ChineseMonth(starts[i], starts[i + 1], m[0], m[1]))
    return tuple(out)


def chinese_months(year: int) -> list:
    """Chinese lunar months overlapping `year`."""
    return [m for m in _chinese_months(year)
            if m.end > date(year, 1, 1) and m.start <= date(year, 12, 31)]


def chinese_lunar_date(d: date, year: int):
    """(month, day, leap) of the Chinese lunar date for the calendar day, or None."""
    for m in _chinese_months(year):
        if m.start <= d < m.end:
            return m.number, (d - m.start).days + 1, m.leap
    return None
