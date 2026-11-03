"""Per-day entries of the cultural lunar calendars (see traditions.py)."""

from datetime import date, datetime
from . import traditions
from . import config as cfg
from .astro import moon_age_at, tithi_for_date


def tradition_item_for_day(tradition: str, d: date, phase_name: str, illum: float) -> dict:
    """Return the cultural-calendar entry (see traditions.py) for one day."""
    if tradition == "maori":
        # Nights begin at dusk, so the night is counted at 18:00 local time.
        age = moon_age_at(datetime(d.year, d.month, d.day, 18, 0, tzinfo=cfg.TZINFO))
        return traditions.maori_item(int(age) + 1 if age is not None else 1)

    if tradition == "hindu":
        return traditions.hindu_item(tithi_for_date(d))

    # wiccan
    if phase_name == "New Moon" or illum <= 2:
        return traditions.wiccan_item("dark")
    if phase_name == "Full Moon":
        return traditions.wiccan_item("peak")
    if phase_name == "Waxing Crescent":
        return traditions.wiccan_item("initiate")
    if phase_name in ("First Quarter", "Waxing Gibbous"):
        return traditions.wiccan_item("build", phase_name)
    return traditions.wiccan_item("release", phase_name)
