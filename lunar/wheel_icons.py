"""Icon set for the year-wheel events (24x24, drawn with currentColor).

Each icon is a small pictogram: line work in ``currentColor`` with a soft
fill so it reads at 14 px on a calendar cell and at 40 px on the day card.
Icons are shared between wheels (a candle is a candle in every tradition).
"""

_S = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
_F = 'fill="currentColor" fill-opacity=".28" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
_SOLID = 'fill="currentColor"'

_RAYS8 = "".join(
    f'<path d="M12 2.5v2.6" transform="rotate({k * 45} 12 12)"/>' for k in range(8)
)

_BODY = {
    "sun": f'<g {_S}><circle cx="12" cy="12" r="4.2" fill="currentColor" fill-opacity=".35"/>{_RAYS8}</g>',

    "sun_high": (
        f'<g {_S}><circle cx="12" cy="12" r="5" fill="currentColor" fill-opacity=".4"/>'
        + "".join(f'<path d="M12 1.5v3.2" transform="rotate({k * 30} 12 12)"/>' for k in range(12))
        + '</g>'
    ),

    "sun_low": (
        f'<g {_S}><path d="M5.5 17a6.5 6.5 0 0 1 13 0" fill="currentColor" fill-opacity=".35"/>'
        '<path d="M2 17h20M12 6.500V4M5.200 9.200 3.500 7.500M18.800 9.200l1.700-1.700M7 20.500h10"/></g>'
    ),

    "snowflake": (
        f'<g {_S}><path d="M12 2.500v19M3.800 7.250l16.400 9.500M3.800 16.750l16.400-9.500"/>'
        '<path d="M9.500 4.500 12 7l2.500-2.500M9.500 19.500 12 17l2.500 2.500"/>'
        '<path d="M5.300 10.300 8.700 9.700 8 6.300M18.700 13.700l-3.400.6.700 3.400"/>'
        '<path d="M5.300 13.700l3.400-.6L8 16.500M18.700 10.300l-3.400-.6.700-3.400"/></g>'
    ),

    "snow_light": (
        f'<g {_S}><path d="M7 14.500a4 4 0 0 1 .5-7.900 5 5 0 0 1 9.600 1.300A3.300 3.300 0 0 1 17 14.500z" '
        'fill="currentColor" fill-opacity=".28"/></g>'
        f'<g {_SOLID}><circle cx="8" cy="18.500" r="1.200"/><circle cx="12.500" cy="20.500" r="1.200"/>'
        '<circle cx="17" cy="18.500" r="1.200"/></g>'
    ),

    "candle": (
        f'<g {_S}><path d="M12 2.500c2.200 2.800 2.600 4.600 0 6.500-2.600-1.900-2.200-3.700 0-6.500z" '
        'fill="currentColor" fill-opacity=".5"/>'
        '<rect x="8.500" y="10" width="7" height="10.500" rx="1.200" fill="currentColor" fill-opacity=".22"/>'
        '<path d="M12 9v1M6.500 21.500h11"/></g>'
    ),

    "sprout": (
        f'<g {_S}><path d="M12 21.500V11.500"/>'
        '<path d="M12 12.500c0-4.200 3-6.800 7.500-6.800 0 4.300-3 6.800-7.500 6.800z" fill="currentColor" fill-opacity=".3"/>'
        '<path d="M12 15c0-3.200-2.400-5.200-6.200-5.200 0 3.500 2.600 5.200 6.200 5.200z" fill="currentColor" fill-opacity=".3"/>'
        '<path d="M5 21.500h14"/></g>'
    ),

    "egg": (
        f'<g {_S}><path d="M12 2.500c4.200 0 7 6 7 10.500a7 7 0 0 1-14 0c0-4.500 2.800-10.500 7-10.500z" '
        'fill="currentColor" fill-opacity=".22"/>'
        '<path d="M5.300 13.500l2.700-2 2.700 2 2.600-2 2.700 2 2.700-2"/></g>'
    ),

    "hare": (
        f'<g {_S}><path d="M9 11.500C7 7 7.300 3 9.200 2.800c1.900-.2 2.500 4 2.300 8.700" fill="currentColor" fill-opacity=".25"/>'
        '<path d="M15 11.500c2-4.500 1.700-8.500-.2-8.700-1.900-.2-2.500 4-2.300 8.700" fill="currentColor" fill-opacity=".25"/>'
        '<circle cx="12" cy="15.500" r="6" fill="currentColor" fill-opacity=".18"/>'
        '<path d="M10.600 17.600c.8.700 1.800.7 2.800 0"/></g>'
        f'<g {_SOLID}><circle cx="9.800" cy="14.600" r="1"/><circle cx="14.200" cy="14.600" r="1"/></g>'
    ),

    "bonfire": (
        f'<g {_S}><path d="M12 2c1.200 4.200 5.300 6 5.300 10.800a5.300 5.300 0 0 1-10.600 0c0-2.200 1-3.700 2.200-4.800.1 2.200 1 3.200 2.200 3.200-.4-4.200-.8-6.200.9-9.200z" '
        'fill="currentColor" fill-opacity=".4"/>'
        '<path d="M4.500 21.500l15-3.200M4.500 18.300l15 3.200"/></g>'
    ),


    "wheat": (
        f'<g {_S}><path d="M12 22V8"/>'
        '<path d="M12 8.500c-2.800-.5-3.800-2.500-3.800-4.200 3 0 3.800 1.800 3.800 4.200zM12 8.500c2.800-.5 3.800-2.500 3.800-4.200-3 0-3.800 1.800-3.800 4.200z" fill="currentColor" fill-opacity=".35"/>'
        '<path d="M12 13c-2.800-.5-3.800-2.500-3.800-4.200 3 0 3.800 1.800 3.800 4.200zM12 13c2.800-.5 3.800-2.500 3.800-4.200-3 0-3.800 1.800-3.800 4.200z" fill="currentColor" fill-opacity=".35"/>'
        '<path d="M12 17.500c-2.800-.5-3.800-2.500-3.800-4.200 3 0 3.800 1.800 3.800 4.200zM12 17.500c2.800-.5 3.800-2.500 3.800-4.200-3 0-3.800 1.800-3.800 4.200z" fill="currentColor" fill-opacity=".35"/>'
        '<path d="M12 5c-1.300-1.300-1.300-2.700 0-3.800 1.300 1.100 1.300 2.500 0 3.800z" fill="currentColor" fill-opacity=".35"/></g>'
    ),

    "apple": (
        f'<g {_S}><path d="M12 8c-2.200-2-7.200-1.600-7.200 4.200 0 4.500 3 8.800 5.600 8.800 1 0 1.600-.5 1.600-.5s.6.500 1.600.5c2.600 0 5.600-4.300 5.600-8.800C19.200 6.400 14.200 6 12 8z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M12 8c0-2.200 1-3.700 3.200-4.800"/>'
        '<path d="M13.500 5.500c1-1.400 2.500-1.700 4-1.200-.4 1.500-1.800 2.300-4 1.200z" fill="currentColor" fill-opacity=".5"/></g>'
    ),

    "leaf": (
        f'<g {_S}><path d="M4.500 19.500C4.500 10.500 10 4.500 20 3.800c0 10-5.500 15.700-13.500 15.700z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M4.500 19.500 14 10M4 21.500l2.500-2"/></g>'
    ),

    "pumpkin": (
        f'<g {_S}><path d="M9 8c-4 0-7 3-7 6.200S5 21 9 21c1.500 0 2.500-.6 3-.6s1.500.6 3 .6c4 0 7-3.600 7-6.800S19 8 15 8c-1.500 0-2.500.9-3 .9S10.500 8 9 8z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M12 8.500c0-2.500.6-3.800 2.200-4.800"/></g>'
        f'<g {_SOLID}><path d="M7.500 12.200 9.200 15H5.800zM16.500 12.200 18.200 15h-3.400z"/>'
        '<path d="M8 17.600l1.600-1.400 1.200 1.300 1.200-1.300 1.200 1.300 1.200-1.300 1.600 1.400-1.400 1.400H9.400z"/></g>'
    ),

    "lantern": (
        f'<g {_S}><path d="M12 1.800V4M9 4h6"/>'
        '<rect x="6.500" y="5" width="11" height="13" rx="4.500" fill="currentColor" fill-opacity=".25"/>'
        '<path d="M12 5v13M6.600 11.500h10.800M9 18v1.800h6V18M12 19.800v2"/></g>'
    ),

    "lightning": (
        f'<g {_S}><path d="M13.500 2 5 13.200h6l-1 8.800 9-12h-6z" fill="currentColor" fill-opacity=".4"/></g>'
    ),

    "rain": (
        f'<g {_S}><path d="M7 14.500a4 4 0 0 1 .5-7.900 5 5 0 0 1 9.600 1.300A3.300 3.300 0 0 1 17 14.500z" '
        'fill="currentColor" fill-opacity=".25"/>'
        '<path d="M8 17.500 7 21M12.500 17.500 11.500 21M17 17.500 16 21"/></g>'
    ),

    "thunder": (
        f'<g {_S}><path d="M7 13.500a4 4 0 0 1 .5-7.900 5 5 0 0 1 9.600 1.300A3.300 3.300 0 0 1 17 13.500" '
        'fill="currentColor" fill-opacity=".25"/>'
        '<path d="M12.800 10.500 9.500 16h3l-1 5.500 4-6.500h-3z" fill="currentColor" fill-opacity=".5"/></g>'
    ),

    "drop": (
        f'<g {_S}><path d="M12 2.800c4.200 5 6.300 8 6.300 11.200a6.300 6.300 0 0 1-12.600 0c0-3.200 2.100-6.200 6.300-11.200z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M8.700 14.500a3.400 3.400 0 0 0 2.300 3.200"/></g>'
    ),

    "crystal": (
        f'<g {_S}><path d="M12 2.500 17.500 12 12 21.500 6.500 12z" fill="currentColor" fill-opacity=".28"/>'
        '<path d="M6.500 12h11M12 2.500v19"/></g>'
    ),


    "tulip": (
        f'<g {_S}><path d="M12 21.500V12"/>'
        '<path d="M12 13c-4.200 0-6.500-3.200-6.500-8 3.200 0 5.200 1.700 6.500 4.300C13.300 6.700 15.300 5 18.500 5c0 4.800-2.300 8-6.500 8z" '
        'fill="currentColor" fill-opacity=".3"/>'
        '<path d="M12 18c0-2.200 2-3.500 4.500-3.500"/></g>'
    ),

    "wreath": (
        f'<g {_S}><circle cx="12" cy="12" r="7.500" stroke-dasharray="3.200 2.400" stroke-width="2.600"/>'
        '<circle cx="12" cy="4.500" r="2" fill="currentColor" fill-opacity=".5"/>'
        '<circle cx="19.500" cy="12" r="2" fill="currentColor" fill-opacity=".5"/>'
        '<circle cx="12" cy="19.500" r="2" fill="currentColor" fill-opacity=".5"/>'
        '<circle cx="4.500" cy="12" r="2" fill="currentColor" fill-opacity=".5"/></g>'
    ),

    "thermo_hi": (
        f'<g {_S}><path d="M10 14.200V5a2 2 0 0 1 4 0v9.200a4 4 0 1 1-4 0z" fill="currentColor" fill-opacity=".2"/>'
        '<path d="M12 8v8"/></g>'
        f'<g {_SOLID}><circle cx="12" cy="17.500" r="2.300"/></g>'
    ),

    "thermo_lo": (
        f'<g {_S}><path d="M10 14.200V5a2 2 0 0 1 4 0v9.200a4 4 0 1 1-4 0z" fill="currentColor" fill-opacity=".2"/>'
        '<path d="M12 13.500v3"/></g>'
        f'<g {_SOLID}><circle cx="12" cy="17.500" r="2.300"/></g>'
    ),

    "kite": (
        f'<g {_S}><path d="M12 2.500 18 10l-6 8.500L6 10z" fill="currentColor" fill-opacity=".25"/>'
        '<path d="M12 2.500v16M6 10h12M12 18.500c-2.500 1.200-.8 2.800-3 3.200"/></g>'
    ),

    "balance": (
        f'<g {_S}><path d="M12 3v18M7 21h10M4.500 6.500h15"/>'
        '<path d="M4.500 6.500 2 13.500a3 3 0 0 0 5 0zM19.500 6.500 17 13.500a3 3 0 0 0 5 0z" fill="currentColor" fill-opacity=".28"/></g>'
    ),

    "bowl": (
        f'<g {_S}><path d="M3 12.500h18a9 8 0 0 1-18 0z" fill="currentColor" fill-opacity=".25"/>'
        '<path d="M8 21h8"/></g>'
        f'<g {_SOLID} fill-opacity=".75"><circle cx="8.500" cy="9.500" r="2.300"/><circle cx="13.500" cy="9.800" r="2.300"/>'
        '<circle cx="11" cy="6.200" r="2.300"/></g>'
    ),

    "moon": (
        f'<g {_S}><path d="M20 14.500A8.500 8.500 0 1 1 9.500 4a7 7 0 0 0 10.500 10.500z" fill="currentColor" fill-opacity=".28"/></g>'
    ),

    "wave": (
        f'<g {_S}><path d="M2.500 8c2-3 4-3 6 0s4 3 6 0 4-3 7 0M2.500 13c2-3 4-3 6 0s4 3 6 0 4-3 7 0M2.500 18c2-3 4-3 6 0s4 3 6 0 4-3 7 0"/></g>'
    ),

    "sunwheel": (
        f'<g {_S}><circle cx="12" cy="12" r="8.500" fill="currentColor" fill-opacity=".15"/>'
        '<circle cx="12" cy="12" r="2.300" fill="currentColor" fill-opacity=".5"/>'
        + "".join(f'<path d="M12 3.500v6.200" transform="rotate({k * 45} 12 12)"/>' for k in range(8))
        + '</g>'
    ),


    "fir": (
        f'<g {_S}><path d="M12 2.500 17 9h-3l4.200 6H5.800L10 9H7z" fill="currentColor" fill-opacity=".28"/>'
        '<path d="M12 15v6M9.500 21.500h5"/></g>'
        f'<g {_SOLID}><circle cx="10" cy="12.500" r=".9"/><circle cx="13.800" cy="11" r=".9"/><circle cx="12" cy="7" r=".9"/></g>'
    ),
}

from .icons_moon import BODY as _MOON_BODY  # noqa: E402
_BODY.update(_MOON_BODY)


def icon_names() -> list:
    return sorted(_BODY)


def icon_svg(name: str, css_class: str = "wi") -> str:
    """Return the named icon as an inline SVG (24x24 viewBox, currentColor)."""
    return f'<svg class="{css_class}" viewBox="0 0 24 24" aria-hidden="true">{_BODY[name]}</svg>'


def icon_inner(name: str) -> str:
    """The icon's inner markup, for nesting in a larger SVG (e.g. the wheel)."""
    return _BODY[name]
