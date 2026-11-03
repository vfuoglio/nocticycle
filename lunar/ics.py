"""iCalendar (.ics) export of the lunar events (and year-wheel festivals)."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from . import config as cfg


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
        ev for ev in list(cfg.EVENTS_GLOBAL or []) + list(cfg.QUARTER_EVENTS_GLOBAL)
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
        f"X-WR-CALNAME:{esc(f'NoctiCycle {year} - {cfg.CITY}')}",
    ]
    full_names = {}
    if cfg.MOON_NAMES:
        from .moon_names import MoonLayer
        full_names = MoonLayer(cfg.MOON_NAMES, year).full_moon_names()

    for ev in moments:
        summary = ICS_EVENT_LABELS[ev.kind]
        if ev.kind == "full" and ev.dt.date().isoformat() in full_names:
            summary += " \u00b7 " + full_names[ev.dt.date().isoformat()]
        start = ev.dt.astimezone(utc)
        end = start + timedelta(minutes=30)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{ev.kind}-{start.strftime('%Y%m%dT%H%M%SZ')}@nocticycle",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{esc(summary)}",
            f"DESCRIPTION:{esc(f'Local time in {cfg.CITY}: ' + ev.dt.strftime('%Y-%m-%d %H:%M %Z'))}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]
    if cfg.WHEEL:
        from . import wheels
        for iso, ev in sorted(wheels.wheel_events(cfg.WHEEL, year).items()):
            day = datetime.fromisoformat(iso)
            nxt = day + timedelta(days=1)
            text = f"{ev['theme']}. {ev['celebrates']}"
            lines += [
                "BEGIN:VEVENT",
                f"UID:wheel-{cfg.WHEEL}-{ev['id']}-{iso}@nocticycle",
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{day.strftime('%Y%m%d')}",
                f"DTEND;VALUE=DATE:{nxt.strftime('%Y%m%d')}",
                f"SUMMARY:{esc(ev['n'] + ' (' + ev['sub'] + ')')}",
                f"DESCRIPTION:{esc(text)}",
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
