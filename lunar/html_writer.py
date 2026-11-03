"""Interactive HTML calendar generation."""

from datetime import date
from calendar import monthrange
from typing import Dict
from html import escape as html_escape
from . import traditions
from . import config as cfg
from .assets import js_json, load_css, load_js
from .astro import assign_daily_phases, compute_phase_events_for_year, illumination_trend_for_date, moon_age_days, moon_illumination_percent, moon_phase_fraction, moon_rise_set_times, phase_name_for_date
from .dates import month_name
from .moon_svg import is_southern_hemisphere, render_illumination_sparkline, render_moon_svg
from .print_writer import write_print_html
from .tradition_days import tradition_item_for_day


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
    events, events_by_month = compute_phase_events_for_year(year)
    cfg.EVENTS_GLOBAL = events  # retained for illumination lookups

    if not cfg.COSMETICS_MODE:
        write_print_html(year, output_path, events, events_by_month)
        return

    css = load_css("default")
    if cfg.TRADITION:
        css += "\n" + load_css("traditions") + "\n" + traditions.tradition_css(cfg.TRADITION)

    html = f"""
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lunar Calendar {year} – {cfg.CITY}</title>
<style>
{css}
</style>
</head>
<body{f' class="trad-{cfg.TRADITION}"' if cfg.TRADITION else ''}>

<h1>Lunar Calendar {year} – {cfg.CITY}</h1>"""

    day_data: Dict[str, dict] = {}
    trad_items: Dict[str, dict] = {}

    if cfg.TRADITION:
        html += traditions.banner_html(cfg.TRADITION)

    if cfg.COSMETICS_MODE:
        html += '<div id="next-events" class="next-events" hidden></div>'

    # Only open the giant table when NOT in cosmetic mode
    if not cfg.COSMETICS_MODE:
        html += "<table><tr><th>Month</th>"
        for d in range(1, 32):
            html += f"<th>{d}</th>"
        html += "</tr>\n"

    for m in range(1, 13):
        days = monthrange(year, m)[1]
        phases = assign_daily_phases(year, m, events, events_by_month)

        if cfg.COSMETICS_MODE:
            html += f"""
            <div class="month-block">
                <div class="month-name">{month_name(m)}</div>
                <div class="month-subtitle">{traditions.TRADITIONS[cfg.TRADITION]["subtitle"] if cfg.TRADITION else "Lunar Phases"}</div>
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
            if not cfg.COSMETICS_MODE:
                html += "<td></td>"
        html += "</tr>\n"

        # Row 2: moon icons + brightness + SPARKLINE
        html += "<tr>"
        for d in range(1, 32):
            if d <= days:
                day_date = date(year, m, d)

                frac = moon_phase_fraction(day_date)
                moon_svg = render_moon_svg(frac, size=24, mirror=is_southern_hemisphere())

                trend_svg = ""
                if cfg.COSMETICS_MODE and cfg.ILLUMINATION_TREND:
                    trend_values = illumination_trend_for_date(day_date, window=3)
                    trend_svg = render_illumination_sparkline(trend_values)

                time_class = "phase-time"
                if not cfg.SHOW_EVENT_TIME:
                    time_class += " hidden"

                # Sunday-first weekday index; only used by the narrow-screen grid
                # layout to offset the first day of the month.
                dow = (day_date.weekday() + 1) % 7
                event_time_str, illum = moon_illumination_percent(day_date)
                phase_name = phase_name_for_date(day_date, frac)

                trad_item = None
                if cfg.TRADITION:
                    trad_item = tradition_item_for_day(cfg.TRADITION, day_date, phase_name, illum)
                    trad_items[trad_item["id"]] = trad_item

                tk_attr = f" data-tk='{trad_item['k']}'" if trad_item else ""
                html += (
                    f"<td class='day-cell' data-date='{day_date.isoformat()}' "
                    f"data-phase='{phases[d].split()[0].lower()}'{tk_attr} style='--dow:{dow}'>"
                )

                if cfg.COSMETICS_MODE:
                    html += f"<div class='day-number'>{d}</div>"

                html += "<div class='moon-wrapper'>"
                html += moon_svg

                if cfg.SHOW_LUMINANCE:
                    html += f"<div class='brightness'>{illum}%</div>"

                rise = set_ = None
                if cfg.SHOW_RISE_SET_TIMES:
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
                if cfg.COSMETICS_MODE and cfg.ILLUMINATION_TREND:
                    html += trend_svg

                html += f"<div class='{time_class}'>{event_time_str}</div>"

                if cfg.SHOW_QUARTERS:
                    quarter = next((q for q in cfg.QUARTER_EVENTS_GLOBAL if q.date == day_date), None)
                    if quarter:
                        label = "1st Qtr" if quarter.kind == "first_quarter" else "Last Qtr"
                        html += (
                            f"<div class='quarter-mark'><span class='qm-label'>{label}</span>"
                            f"<span class='qm-time'>{quarter.dt.strftime('%H:%M')}</span></div>"
                        )

                html += f"""{rise_set_html}"""

                if trad_item:
                    kind = traditions.TRADITIONS[cfg.TRADITION]["kinds"][trad_item["k"]]
                    badge = f"<span class='tb'>{trad_item['b']}</span>" if trad_item.get("b") else ""
                    tip = html_escape(f"{trad_item['l']}: {trad_item['m']}", quote=True)
                    html += (
                        f"<div class='trad' title=\"{tip}\">{traditions.glyph_svg(kind['glyph'])}"
                        f"<span class='tl'>{trad_item.get('s', trad_item['l'])}</span>{badge}</div>"
                    )

                day_data[day_date.isoformat()] = {
                    "t": trad_item["id"] if trad_item else None,
                    "n": phase_name,
                    "i": illum,
                    "a": moon_age_days(day_date),
                    "e": event_time_str,
                    "r": rise or "",
                    "s": set_ or "",
                }

                html += "</div>"  # end moon-wrapper

                html += "</td>"
            else:
                if not cfg.COSMETICS_MODE:
                    html += "<td></td>"

        html += "</tr>\n"

        # Close cosmetic block
        if cfg.COSMETICS_MODE:
            html += "</table></div>"

    if not cfg.COSMETICS_MODE:
        html += "</table>"

    if cfg.COSMETICS_MODE:
        page_data = {
            "year": year,
            "city": cfg.CITY,
            "tz": cfg.TZ,
            "riseSet": bool(cfg.SHOW_RISE_SET_TIMES),
            "events": sorted(
                (
                    {"kind": ev.kind, "iso": ev.dt.isoformat()}
                    for ev in list(events) + list(cfg.QUARTER_EVENTS_GLOBAL)
                ),
                key=lambda e: e["iso"],
            ),
            "days": day_data,
        }
        if cfg.TRADITION:
            spec = traditions.TRADITIONS[cfg.TRADITION]
            page_data["tradition"] = {
                "id": cfg.TRADITION,
                "name": spec["name"],
                "kinds": {
                    k: {"label": v["label"], "svg": traditions.glyph_svg(v["glyph"])}
                    for k, v in spec["kinds"].items()
                },
                "items": trad_items,
            }
        html += (
            f'<script id="nocticycle-data" type="application/json">{js_json(page_data)}</script>'
            f"<script>\n{load_js('calendar')}\n</script>"
        )

    html += "</body></html>"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {output_path}")
