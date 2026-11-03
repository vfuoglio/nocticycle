"""The phase band above each month: one night-sky bar that follows the real moon cycle.

The bar is a single rounded strip. Its colour at each day is the moon's
illumination (deep indigo at new moon, brightening to a silver glow at full moon),
so the gradient is the lunar cycle itself. Each phase carries a small glyph and an
italic label; narrow segments show the glyph only.
"""

from datetime import date

# (illumination 0..1, rgb): deep night sky -> dusky mauve -> amber -> warm moonlight
_STOPS = [(0.0, (8, 12, 31)), (0.4, (38, 44, 108)), (0.68, (112, 98, 148)),
          (0.88, (212, 176, 150)), (1.0, (252, 238, 212))]

_NAMES = {"New Moon": "New", "Full Moon": "Full", "Waxing": "Waxing", "Waning": "Waning"}
_TITLES = {"New Moon": "New Moon", "Full Moon": "Full Moon", "Waxing": "Waxing", "Waning": "Waning"}

# 16x16 glyphs: the lit part of the moon (waxing = lit on the right in the northern hemisphere)
_GLYPH = {
    "New Moon": '<circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.6"/>',
    "Full Moon": '<circle cx="8" cy="8" r="6.5" fill="currentColor"/>',
    "Waxing": '<path d="M8 1.5a6.5 6.5 0 1 1 0 13 4 6.5 0 0 0 0-13z" fill="currentColor"/>'
              '<circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1"/>',
    "Waning": '<path d="M8 1.5a6.5 6.5 0 1 0 0 13 4 6.5 0 0 1 0-13z" fill="currentColor"/>'
              '<circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1"/>',
}


def _colour(illum_pct: float) -> str:
    t = max(0.0, min(1.0, illum_pct / 100.0))
    for (t0, c0), (t1, c1) in zip(_STOPS, _STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            r, g, b = (round(a + (b_ - a) * f) for a, b_ in zip(c0, c1))
            return f"rgb({r},{g},{b})"
    return "rgb(252,238,212)"


def _glyph(phase: str, mirror: bool) -> str:
    key = phase
    if mirror and phase in ("Waxing", "Waning"):
        key = "Waning" if phase == "Waxing" else "Waxing"
    return f'<svg class="pb-glyph" viewBox="0 0 16 16" aria-hidden="true">{_GLYPH[key]}</svg>'


def phase_band_row(days: int, phases: dict, illum: dict, mirror: bool = False) -> str:
    """HTML of the phase-band table row for a month.

    phases: day -> "New Moon" | "Waxing" | "Full Moon" | "Waning"
    illum:  day -> illumination percent for that day
    """
    segs = []
    d = 1
    while d <= days:
        phase = phases[d]
        span = 1
        while d + span <= days and phases[d + span] == phase:
            span += 1
        stops = ", ".join(
            f"{_colour(illum[d + i])} {(i + 0.5) / span * 100:.1f}%" for i in range(span)
        )
        if span == 1:
            stops = f"{_colour(illum[d])}, {_colour(illum[d])}"
        centre = illum[d + span // 2]
        lit = phase == "Full Moon" or centre >= 78
        label = f"<span class='pb-name'>{_NAMES[phase]}</span>" if span >= 4 else ""
        segs.append(
            f"<div class='pb-seg{' pb-lit' if lit else ''}' data-p='{phase.split()[0].lower()}' "
            f"style='flex:{span} 1 0;background:linear-gradient(90deg,{stops})' title='{_TITLES[phase]}'>"
            f"<span class='pb-inner'>{_glyph(phase, mirror)}{label}</span></div>"
        )
        d += span
    return f"<tr class='phase-row'><td colspan='{days}' class='phase-band'><div class='pb'>{''.join(segs)}</div></td></tr>\n"
