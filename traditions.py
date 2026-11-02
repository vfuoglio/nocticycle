"""
Cultural lunar traditions for NoctiCycle.

Each tradition maps a day of the lunar cycle to a named phase that carries a
traditional meaning:

* ``maori``  – the Māori Maramataka, one named night per day of the lunation.
* ``hindu``  – the Hindu Panchang tithi (1 of 30 lunar days, two pakshas).
* ``wiccan`` – the Neopagan / Wiccan esbat phases.

This module only holds data and presentation helpers (names, meanings,
colours, glyphs and decorative SVG). The astronomy that decides *which* night,
tithi or phase applies to a date lives in ``nocticycle.py``.

These traditions are living and vary between regions, lineages and
communities. The texts below are short, general summaries, not authoritative
statements for any one community: edit them freely to match your own
tradition.
"""

import math

# ---------------------------------------------------------------------------
# Glyphs (16x16, drawn with currentColor so CSS can tint them per category)
# ---------------------------------------------------------------------------

_GLYPH_BODY = {
    "dot":  '<circle cx="8" cy="8" r="3.2" fill="currentColor"/>'
            '<circle cx="8" cy="8" r="6.4" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".55"/>',
    "up":   '<path d="M3.5 10.5 8 5.5l4.5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "up2":  '<path d="M3.5 7.5 8 3l4.5 4.5M3.5 12.5 8 8l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
    "down": '<path d="M3.5 5.5 8 10.5l4.5-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "sun":  '<circle cx="8" cy="8" r="2.8" fill="currentColor"/>'
            '<path d="M8 1.2v2.4M8 12.4v2.4M1.2 8h2.4M12.4 8h2.4M3.2 3.2l1.7 1.7M11.1 11.1l1.7 1.7M12.8 3.2l-1.7 1.7M4.9 11.1l-1.7 1.7" '
            'stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
    "zig":  '<path d="M1.5 10 4.5 5l3.5 6 3.5-6 3 5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/>',
    "wave": '<path d="M1 9c1.6-3 3.2-3 4.8 0s3.2 3 4.8 0 3.2-3 4.4 0" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/>',
    "lotus": '<path d="M8 2.2c2 2 2.8 4.2 0 7.6C5.2 6.400 6 4.200 8 2.200z" fill="currentColor"/>'
             '<path d="M2 6.200c2.700.1 4.500 1.500 5 5C4.300 11.200 2.400 9.500 2 6.200zM14 6.200c-2.700.1-4.500 1.500-5 5 2.700 0 4.600-1.700 5-5z" fill="currentColor" opacity=".7"/>'
             '<path d="M3 13.600h10" stroke="currentColor" stroke-width="1.400" stroke-linecap="round"/>',
}


def glyph_svg(name: str, css_class: str = "tg") -> str:
    """Return a small inline SVG for the named glyph."""
    body = _GLYPH_BODY[name]
    return f'<svg class="{css_class}" viewBox="0 0 16 16" aria-hidden="true">{body}</svg>'


# ---------------------------------------------------------------------------
# Māori Maramataka
# ---------------------------------------------------------------------------

MAORI_KINDS = {
    "rest": {"label": "Rest and low energy", "glyph": "dot", "dark": "#8fa0b8", "light": "#52627a"},
    "rise": {"label": "Energy rising / balanced", "glyph": "up", "dark": "#5fd1a5", "light": "#1b8a64"},
    "high": {"label": "High energy and abundance", "glyph": "sun", "dark": "#f2c14e", "light": "#a9760a"},
    "wild": {"label": "Tamatea: unpredictable", "glyph": "zig", "dark": "#f08a4b", "light": "#bd5513"},
    "sea":  {"label": "Tangaroa: sea and fishing", "glyph": "wave", "dark": "#4aa8e0", "light": "#1c6da3"},
}

# (name, kind, meaning). The sequence follows the order commonly published for
# the 29 named nights of the lunation; iwi and regions differ in the middle of
# the cycle, so treat it as one version among several.
_MAORI_NIGHTS = [
    ("Whiro", "rest", "The dark moon and the lowest energy of the cycle. Unfavourable for fishing or planting: a time for rest and strategic planning."),
    ("Tirea", "rise", "Energy begins to rise. Good for planning and light activity."),
    ("Hoata", "rise", "Energy is increasing. Good for learning and communication."),
    ("Ōuenuku", "high", "High energy. Good for fishing and productivity."),
    ("Okoro", "rise", "Balanced energy. Good for social and creative tasks."),
    ("Tamatea-tuhāhā", "wild", "Tamatea nights are unpredictable and highly energetic, matching rougher tides and weather. Often avoided for important decisions."),
    ("Tamatea-aio", "wild", "Tamatea nights are unpredictable and highly energetic, matching rougher tides and weather. Often avoided for important decisions."),
    ("Tamatea-kai-ariki", "wild", "Tamatea nights are unpredictable and highly energetic, matching rougher tides and weather. Often avoided for important decisions."),
    ("Huna", "rest", "The hidden moon. An introspective, spiritual time."),
    ("Ari-matanui", "rise", "A mid-cycle night: energy is building towards the full moon."),
    ("Māwharu", "high", "Favourable for planting and productivity."),
    ("Maurea", "rise", "A mid-cycle night: energy keeps building towards the full moon."),
    ("Atua", "high", "Strong energy. Good for leadership and action."),
    ("Hotu", "high", "High energy. Good for harvesting and gatherings."),
    ("Rākaunui", "high", "The full moon: peak energy, abundance and illumination. The ideal time for harvesting food, gathering and socialising."),
    ("Rākaumatohi", "high", "Slightly waning, still good for reflection and completion."),
    ("Takirau", "rest", "Energy is waning: slow down and avoid big decisions."),
    ("Oike", "rest", "Energy keeps winding down: a quieter night."),
    ("Korekore-te-whiwhia", "rest", "Korekore nights are quiet, low-productivity nights: a time to rest and prepare."),
    ("Korekore-te-rawea", "rest", "Korekore nights are quiet, low-productivity nights: a time to rest and prepare."),
    ("Korekore-piri-ki-ngā-Tangaroa", "rest", "Korekore nights are quiet, low-productivity nights: a time to rest and prepare."),
    ("Tangaroa-ā-mua", "sea", "Attuned to Tangaroa, god of the sea: excellent conditions for ocean fishing, eeling and seafaring."),
    ("Tangaroa-ā-roto", "sea", "Attuned to Tangaroa, god of the sea: excellent conditions for ocean fishing, eeling and seafaring."),
    ("Tangaroa-kiokio", "sea", "Attuned to Tangaroa, god of the sea: excellent conditions for ocean fishing, eeling and seafaring."),
    ("Ōtāne", "rest", "Low energy. Good for rest and recovery."),
    ("Ōrongonui", "rise", "Energy returns. Good for healing and gentle activity."),
    ("Mauri", "rise", "Balanced energy. Good for relationships and wellbeing."),
    ("Ōmutu", "rest", "Energy is ebbing towards the end of the cycle: time to wrap things up."),
    ("Mutuwhenua", "rest", "The end of the cycle: very low energy, a time to rest and reset."),
]


def soft_wrap(name: str, limit: int = 8) -> str:
    """Insert a soft hyphen into long single words so narrow cells wrap tidily.

    Prefers splitting a consonant cluster (Chatur-dashi), otherwise the
    boundary between a vowel and the following consonant (Prati-pada).
    Digraphs such as "ng", "wh" and "th" are never split.
    """
    vowels = "aeiouāēīōūAEIOUĀĒĪŌŪ"
    digraphs = ("ng", "wh", "th", "sh", "ch")
    out = []
    for word in name.split(" "):
        if len(word) > limit and "-" not in word:
            mid = len(word) / 2
            low = word.lower()
            ok = [i for i in range(3, len(word) - 2) if low[i - 1:i + 1] not in digraphs]
            clusters = [i for i in ok if low[i - 1] not in vowels and low[i] not in vowels]
            vc = [i for i in ok if low[i - 1] in vowels and low[i] not in vowels]
            cuts = clusters or vc
            if cuts:
                i = min(cuts, key=lambda c: abs(c - mid))
                word = word[:i] + "\u00ad" + word[i:]
        out.append(word)
    return " ".join(out)


def maori_item(night: int) -> dict:
    """Return the Maramataka entry for night 1..30 (30 repeats the last name)."""
    n = max(1, min(night, len(_MAORI_NIGHTS)))
    name, kind, meaning = _MAORI_NIGHTS[n - 1]
    return {
        "id": f"m{n}",
        "l": name,
        "s": soft_wrap(name.split("-")[0] if name.startswith(("Tamatea", "Korekore", "Tangaroa")) else name),
        "p": f"Night {n} of the lunar cycle",
        "k": kind,
        "m": meaning,
    }


# ---------------------------------------------------------------------------
# Hindu Panchang (tithi)
# ---------------------------------------------------------------------------

HINDU_KINDS = {
    "shukla":  {"label": "Shukla Paksha: waxing, growth", "glyph": "lotus", "dark": "#f2b84b", "light": "#a86a00"},
    "krishna": {"label": "Krishna Paksha: waning, turning inward", "glyph": "down", "dark": "#8b92f0", "light": "#4650c4"},
}

_TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi",
]

_PAKSHA_TEXT = {
    "shukla": "The waxing fortnight is tied to growth: meaningful for starting businesses, marriages or building a home.",
    "krishna": "The waning fortnight means drawing inward: reserved for spiritual cleansing and honouring ancestors.",
}


def hindu_item(tithi: int) -> dict:
    """Return the entry for tithi 1..30 (1-15 Shukla, 16-30 Krishna)."""
    t = max(1, min(tithi, 30))
    paksha = "shukla" if t <= 15 else "krishna"
    num = t if t <= 15 else t - 15

    if num == 15:
        name = "Purnima" if paksha == "shukla" else "Amavasya"
    else:
        name = _TITHI_NAMES[num - 1]

    badge = ""
    text = _PAKSHA_TEXT[paksha]
    if num == 11:
        badge = "Fast"
        text = ("Ekadashi, the 11th tithi of both fortnights: a day of fasting and "
                "spiritual purification for many practising Hindus. ") + text
    elif num == 15 and paksha == "shukla":
        badge = "Full moon"
        text = "Purnima, the full moon: widely observed with prayer, charity and worship. " + text
    elif num == 15:
        badge = "Ancestors"
        text = ("Amavasya, the dark moon: a time to offer prayers to lineage ancestors. ")
    elif num == 4:
        badge = "Ganesha"
        text = "Chaturthi is traditionally dedicated to Ganesha. " + text
    elif num == 13:
        badge = "Pradosha"
        text = "Trayodashi: Pradosha, evening worship of Shiva, often with a fast. " + text
    elif num == 14 and paksha == "krishna":
        badge = "Shivaratri"
        text = "Krishna Chaturdashi is observed as Masik Shivaratri, a monthly night of Shiva. " + text

    return {
        "id": f"h{t}",
        "l": name,
        "s": soft_wrap(name),
        "p": f"{'Shukla' if paksha == 'shukla' else 'Krishna'} Paksha · tithi {num}",
        "k": paksha,
        "m": text,
        "b": badge,
    }


# ---------------------------------------------------------------------------
# Wiccan / Neopagan esbats
# ---------------------------------------------------------------------------

WICCAN_KINDS = {
    "dark":    {"label": "Dark moon: rest and grounding", "glyph": "dot", "dark": "#9a9cc4", "light": "#5a5c8f"},
    "initiate": {"label": "Waxing crescent: initiation", "glyph": "up", "dark": "#b79cff", "light": "#6c46d1"},
    "build":   {"label": "Building towards the full moon", "glyph": "up2", "dark": "#8fb8ff", "light": "#2c68c7"},
    "peak":    {"label": "Full moon: esbat and peak power", "glyph": "sun", "dark": "#ffe27a", "light": "#a67f00"},
    "release": {"label": "Waning: banishing and release", "glyph": "down", "dark": "#ff8fb1", "light": "#c2285c"},
}

_WICCAN_ITEMS = {
    "dark": ("Dark Moon", "Complete rest, grounding and looking inward before rebirth.", ""),
    "initiate": ("Waxing Crescent", "Initiation, attraction and manifestation. Ritual focus is on starting projects, creative expansion and gaining momentum.", ""),
    "build": ("Building Moon", "Growth continues: nurture and strengthen what you began as the moon swells towards fullness.", ""),
    "peak": ("Full Moon", "Peak power, psychic intuition and realization. Used for major ceremonies, celebration and gratitude.", "Esbat"),
    "release": ("Waning Moon", "Banishing, letting go and release. Rituals focus on shedding negative habits, breaking toxic patterns and emotional detox.", ""),
}


def wiccan_item(kind: str, label: str | None = None) -> dict:
    """Return the esbat entry for a category; `label` overrides the display name."""
    name, text, badge = _WICCAN_ITEMS[kind]
    shown = label or name
    return {
        "id": f"w-{kind}-{shown.lower().replace(' ', '-')}",
        "l": shown,
        "p": name if shown != name else "",
        "k": kind,
        "m": text,
        "b": badge,
    }


# ---------------------------------------------------------------------------
# Tradition registry
# ---------------------------------------------------------------------------

TRADITIONS = {
    "maori": {
        "name": "Māori Maramataka",
        "subtitle": "Maramataka · the nights of the moon",
        "blurb": "In the Maramataka every night of the lunar cycle has its own name and character, "
                 "guiding when to fish, plant, gather, rest or reflect.",
        "note": "Night names and their meanings vary between iwi and regions. This calendar follows one "
                "commonly published sequence: please defer to your own iwi's maramataka.",
        "kinds": MAORI_KINDS,
        "accent": ("#4fd1b5", "#12806a"),
    },
    "hindu": {
        "name": "Hindu Panchang · Tithi",
        "subtitle": "Panchang · tithi of the day",
        "blurb": "The Panchang divides the month into the waxing Shukla Paksha and the waning "
                 "Krishna Paksha. Each lunar day, or tithi, carries its own observances.",
        "note": "The tithi shown is the one prevailing at local sunrise. Festival dates in a full "
                "Panchang follow further rules, so please check your local Panchang.",
        "kinds": HINDU_KINDS,
        "accent": ("#ff9f43", "#b85f00"),
    },
    "wiccan": {
        "name": "Wiccan Esbat Calendar",
        "subtitle": "Esbats · the moon's magical phases",
        "blurb": "Esbats are rituals timed to the moon: begin as it waxes, celebrate at the full moon, "
                 "release as it wanes and rest in the dark.",
        "note": "Practices differ between traditions and covens; these are general associations.",
        "kinds": WICCAN_KINDS,
        "accent": ("#b79cff", "#6c46d1"),
    },
}

TRADITION_CHOICES = tuple(TRADITIONS)


# ---------------------------------------------------------------------------
# Decorative banner art
# ---------------------------------------------------------------------------

def _koru_svg() -> str:
    """A koru: an unfurling fern frond, a spiral curling in from a curved stem."""
    cx, cy, theta0, turns = 52, 40, math.pi / 2, 3.1 * math.pi
    pts = []
    for i in range(0, 141):
        u = i / 140
        r = 27 * (1 - u) ** 0.9 + 4
        theta = theta0 + u * turns
        pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    path = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    ex, ey = pts[-1]
    sx, sy = pts[0]
    return (
        '<svg class="trad-art" viewBox="0 0 100 100" aria-hidden="true">'
        '<defs><linearGradient id="kg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="var(--ta)"/><stop offset="1" stop-color="var(--ta2)"/></linearGradient></defs>'
        f'<path d="M{sx:.2f},{sy:.2f} C {sx - 2:.2f},{sy + 14:.2f} {sx + 10:.2f},{sy + 20:.2f} {sx + 4:.2f},96" '
        'fill="none" stroke="url(#kg)" stroke-width="6" stroke-linecap="round"/>'
        f'<path d="{path}" fill="none" stroke="url(#kg)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="4.4" fill="var(--ta2)"/>'
        '</svg>'
    )


def _lotus_svg() -> str:
    """A layered eight-petal lotus mandala."""
    outer = "".join(
        f'<ellipse cx="50" cy="25" rx="8.5" ry="21" fill="var(--ta)" opacity=".85" transform="rotate({k * 45} 50 50)"/>'
        for k in range(8)
    )
    inner = "".join(
        f'<ellipse cx="50" cy="34" rx="6" ry="14" fill="var(--ta2)" opacity=".9" transform="rotate({k * 45 + 22.5} 50 50)"/>'
        for k in range(8)
    )
    return (
        '<svg class="trad-art" viewBox="0 0 100 100" aria-hidden="true">'
        f'{outer}{inner}'
        '<circle cx="50" cy="50" r="7" fill="var(--ta-bg)" stroke="var(--ta)" stroke-width="2"/>'
        '</svg>'
    )


def _triple_moon_svg() -> str:
    """The triple moon: waxing crescent, full moon, waning crescent."""
    r = 17
    wax = (f'<path d="M24,{50 - r} A{r},{r} 0 1 1 24,{50 + r} A{r * 0.62},{r} 0 1 0 24,{50 - r}Z" fill="var(--ta)"/>')
    wane = (f'<g transform="translate(100,0) scale(-1,1)"><path d="M24,{50 - r} A{r},{r} 0 1 1 24,{50 + r} '
            f'A{r * 0.62},{r} 0 1 0 24,{50 - r}Z" fill="var(--ta)"/></g>')
    full = '<circle cx="50" cy="50" r="15" fill="var(--ta2)"/><circle cx="50" cy="50" r="19" fill="none" stroke="var(--ta)" stroke-width="1.6" opacity=".7"/>'
    return f'<svg class="trad-art" viewBox="0 0 100 100" aria-hidden="true">{wax}{full}{wane}</svg>'


_ART = {"maori": _koru_svg, "hindu": _lotus_svg, "wiccan": _triple_moon_svg}


def banner_html(tradition: str) -> str:
    """Header banner: ornament, title, blurb, legend chips and a cultural note."""
    t = TRADITIONS[tradition]
    chips = "".join(
        f'<span class="trad-chip" data-tk="{k}">{glyph_svg(v["glyph"])}{v["label"]}</span>'
        for k, v in t["kinds"].items()
    )
    return (
        f'<section class="trad-banner">'
        f'<div class="trad-art-wrap">{_ART[tradition]()}</div>'
        f'<div class="trad-text">'
        f'<div class="trad-title">{t["name"]}</div>'
        f'<p class="trad-blurb">{t["blurb"]}</p>'
        f'<div class="trad-legend">{chips}</div>'
        f'<p class="trad-note">{t["note"]}</p>'
        f'</div></section>'
    )


def tradition_css(tradition: str) -> str:
    """Per-tradition colour variables: kinds and accent, for dark and light themes."""
    t = TRADITIONS[tradition]
    dark_accent, light_accent = t["accent"]
    dark = [f":root {{ --ta: {dark_accent}; --ta2: {_mix(dark_accent)}; --ta-bg: #12151d; }}"]
    light = [f"  :root {{ --ta: {light_accent}; --ta2: {_mix(light_accent)}; --ta-bg: #ffffff; }}"]
    for k, v in t["kinds"].items():
        dark.append(f'[data-tk="{k}"] {{ --tk: {v["dark"]}; }}')
        light.append(f'  [data-tk="{k}"] {{ --tk: {v["light"]}; }}')
    return "\n".join(dark) + "\n@media (prefers-color-scheme: light) {\n" + "\n".join(light) + "\n}\n"


def _mix(hex_color: str) -> str:
    """A slightly lighter companion of a #rrggbb colour (for gradients)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (min(255, int(c + (255 - c) * 0.35)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"
