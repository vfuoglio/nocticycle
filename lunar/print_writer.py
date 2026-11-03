"""One-page landscape print layout."""

from datetime import date
from calendar import monthrange
from . import config as cfg
from .assets import load_css
from .astro import assign_daily_phases, moon_illumination_percent, moon_phase_fraction
from .dates import month_name
from .moon_svg import is_southern_hemisphere, render_moon_svg


PRINT_MARGIN_IN = 0.35


PRINT_TITLE_IN = 0.3


PRINT_LABEL_IN = 0.6


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
        if cfg.SHOW_QUARTERS else ""
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
    if cfg.SHOW_QUARTERS:
        moments += [q for q in cfg.QUARTER_EVENTS_GLOBAL if q.dt.year == year]
    return sorted(moments, key=lambda e: e.dt)


def print_geometry(n_events: int) -> dict:
    """Compute physical sizes (inches/points) so the year fits one page.

    Everything printed is sized from the paper dimensions, so the layout
    scales to any supported paper instead of relying on the browser to
    shrink an oversized table.
    """
    width, height = cfg.PAPER_SIZES[cfg.PAPER]
    usable_w = width - 2 * PRINT_MARGIN_IN
    usable_h = height - 2 * PRINT_MARGIN_IN

    per_line = max(1, int(usable_w / PRINT_EVENT_ITEM_IN))
    lines = -(-n_events // per_line) if n_events else 0
    footer = PRINT_LEGEND_IN + lines * PRINT_EVENT_LINE_IN + 0.06

    if cfg.PRINT_LAYOUT == "rows":
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
    if cfg.SHOW_LUMINANCE:
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

    quarter_days = {q.date for q in cfg.QUARTER_EVENTS_GLOBAL} if cfg.SHOW_QUARTERS else set()
    major_days = {e.date for e in events}
    phases = {m: assign_daily_phases(year, m, events, events_by_month) for m in range(1, 13)}

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Lunar Calendar {year} – {cfg.CITY}</title>
<style>
{css}
</style>
</head>
<body class="ps-{cfg.PRINT_STYLE} layout-{cfg.PRINT_LAYOUT}">
{PRINT_HATCH_DEFS if cfg.PRINT_STYLE == "hatched" else ""}
<h1>Lunar Calendar {year} – {cfg.CITY}</h1>
<table class="year">
"""

    if cfg.PRINT_LAYOUT == "rows":
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
