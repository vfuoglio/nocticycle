"""Extra icons for the named-moon systems (animals, plants, flowers, moons).

Same conventions as ``wheel_icons.py`` (24x24 viewBox, ``currentColor``); the
two sets are merged in ``wheel_icons.py`` so ``icon_svg`` serves both.
"""

_S = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
_SOLID = 'fill="currentColor"'


def _petals(n, cx, cy, rx, ry, dist, rot=0, opacity=".3"):
    """n ellipses arranged around (cx, cy), their centres `dist` from it."""
    out = []
    for k in range(n):
        a = rot + k * 360 / n
        out.append(
            f'<ellipse cx="{cx}" cy="{cy - dist}" rx="{rx}" ry="{ry}" '
            f'fill="currentColor" fill-opacity="{opacity}" transform="rotate({a:g} {cx} {cy})"/>'
        )
    return "".join(out)


def _flower(cx, cy, r, d, rot=0):
    """Five round petals (plum/cherry style) around (cx, cy)."""
    import math
    out = []
    for k in range(5):
        a = math.radians(rot + k * 72 - 90)
        out.append(f'<circle cx="{cx + d * math.cos(a):.2f}" cy="{cy + d * math.sin(a):.2f}" r="{r}" '
                   f'fill="currentColor" fill-opacity=".3"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * .55:.2f}" fill="currentColor"/>')
    return "".join(out)


BODY = {
    "spirit": (
        f'<g {_S}><circle cx="12" cy="12" r="9.500" stroke-dasharray="2.600 2"/>'
        '<path d="M12 5.500c2.800 3.200 4 5 4 7.700a4 4 0 0 1-8 0c0-2.700 1.200-4.500 4-7.700z" '
        'fill="currentColor" fill-opacity=".35"/>'
        '<path d="M12 12.500c1 1.200 1.400 2 1.400 2.900a1.400 1.400 0 0 1-2.800 0c0-.9.400-1.700 1.400-2.900z" '
        'fill="currentColor" fill-opacity=".6"/></g>'
    ),

    "paw": (
        f'<g {_S}><path d="M12 11.500c-3.300 0-6 3-6 5.500 0 2 1.700 3 3.200 3 1.200 0 1.800-.6 2.800-.6s1.600.6 2.800.6c1.500 0 3.200-1 3.200-3 0-2.500-2.700-5.500-6-5.500z" '
        'fill="currentColor" fill-opacity=".3"/>'
        '<ellipse cx="5.200" cy="10.300" rx="1.900" ry="2.400" transform="rotate(-18 5.200 10.300)" fill="currentColor" fill-opacity=".3"/>'
        '<ellipse cx="9.300" cy="6.400" rx="1.900" ry="2.600" transform="rotate(-6 9.300 6.400)" fill="currentColor" fill-opacity=".3"/>'
        '<ellipse cx="14.700" cy="6.400" rx="1.900" ry="2.600" transform="rotate(6 14.700 6.400)" fill="currentColor" fill-opacity=".3"/>'
        '<ellipse cx="18.800" cy="10.300" rx="1.900" ry="2.400" transform="rotate(18 18.800 10.300)" fill="currentColor" fill-opacity=".3"/></g>'
    ),

    "maple": (
        f'<g {_S}><path d="M12 2.200 14 6.200 17.200 5 16.200 10 20.300 9 17.500 13.200 19.800 13.800 13 19.300V22h-2v-2.700L4.200 13.800 6.500 13.200 3.700 9 7.800 10 6.800 5 10 6.200z" '
        'fill="currentColor" fill-opacity=".3"/></g>'
    ),

    "fish": (
        f'<g {_S}><path d="M2.500 12c3-5 9.500-6.200 14-3l5-3.200v12.400l-5-3.200c-4.500 3.200-11 2-14-3z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M10.500 8.500c1.300 2 1.300 5 0 7M14 9.500c.8 1.600.8 3.400 0 5"/></g>'
        f'<g {_SOLID}><circle cx="6.800" cy="11.200" r=".95"/></g>'
    ),

    "blossom": (
        f'<g {_S}>{_petals(5, 12, 12, 3.500, 4.600, 4.800)}'
        '<circle cx="12" cy="12" r="1.900" fill="currentColor" fill-opacity=".7"/></g>'
    ),

    "strawberry": (
        f'<g {_S}><path d="M12 21.500c-5-2.800-7.600-7-6.500-11.500a4.200 4.200 0 0 1 4.200-3c1 0 1.700.5 2.300.5s1.300-.5 2.300-.5a4.200 4.200 0 0 1 4.200 3c1.100 4.500-1.500 8.700-6.500 11.500z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M7.500 6.500c1.700 1.200 3.200.8 4.500-1 1.300 1.800 2.800 2.200 4.500 1M12 5.500V2.500"/></g>'
        f'<g {_SOLID}><circle cx="9.500" cy="12" r=".8"/><circle cx="14.500" cy="12" r=".8"/>'
        '<circle cx="12" cy="14.500" r=".8"/><circle cx="9.800" cy="16.800" r=".8"/><circle cx="14.200" cy="16.800" r=".8"/></g>'
    ),

    "berries": (
        f'<g {_S}>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="2.700" fill="currentColor" fill-opacity=".3"/>'
                  for x, y in ((12, 9.500), (8.700, 13), (15.300, 13), (6.500, 17.500), (12, 17), (17.500, 17.500)))
        + '<path d="M12 6.500C12 4.500 13 3.200 15 2.800M12 6.500c-1.700-1.600-3.200-1.800-4.600-1"/></g>'
    ),

    "grapes": (
        f'<g {_S}>'
        + "".join(f'<circle cx="{x}" cy="{y}" r="2.500" fill="currentColor" fill-opacity=".3"/>'
                  for x, y in ((8, 10), (12, 10), (16, 10), (10, 14), (14, 14), (12, 18)))
        + '<path d="M12 7.500C12 5.200 13.300 3.600 15.500 3.200M12 7C10.500 5 8.500 4.600 6.500 5.500"/></g>'
    ),

    "corn": (
        f'<g {_S}><path d="M12 2.500c3.200 3 4.200 8 3.200 12.500-.6 2.700-1.700 4.500-3.200 4.500s-2.600-1.800-3.200-4.500C7.800 10.500 8.800 5.500 12 2.500z" '
        'fill="currentColor" fill-opacity=".3"/>'
        '<path d="M12 21.800c-4.800-.8-7-4.500-7-8.500 3.300.8 6.300 3.700 7 8.500zM12 21.800c4.800-.8 7-4.500 7-8.500-3.300.8-6.300 3.700-7 8.500z" '
        'fill="currentColor" fill-opacity=".2"/>'
        '<path d="M12 5v13M9.300 9h5.400M9 13h6"/></g>'
    ),

    "falling_leaves": (
        f'<g {_S}><path d="M3.500 13.500C3.500 7.500 7.500 3.800 14 3.200c0 6.500-3.600 10.300-9.500 10.300z" '
        'fill="currentColor" fill-opacity=".3" transform="rotate(8 8 8)"/>'
        '<path d="M3.500 13.500 11 7.500" transform="rotate(8 8 8)"/>'
        '<path d="M13.500 20c0-4 2.600-6.400 7-6.800 0 4.200-2.400 6.800-7 6.800z" fill="currentColor" fill-opacity=".3"/>'
        '<path d="M13.500 20 18.500 15.500M19 4.500l1.500 2M16 9l.8 1.800" opacity=".6"/></g>'
    ),

    "wolf": (
        f'<g {_S}><path d="M3.500 2.500 9 6.800h6l5.500-4.300V11c0 5.500-3.700 10-8.500 10s-8.500-4.500-8.500-10z" fill="currentColor" fill-opacity=".25"/>'
        '<ellipse cx="12" cy="15.800" rx="3.800" ry="3.200" fill="currentColor" fill-opacity=".2"/></g>'
        f'<g {_SOLID}><path d="M7 10.500l2.500.8-.4 1.400-2.600-.7zM17 10.500l-2.500.8.400 1.400 2.600-.7z"/>'
        '<path d="M10.300 14h3.400l-1.700 2z"/></g>'
    ),

    "goblet": (
        f'<g {_S}><path d="M6.500 3h11c0 5.500-1.700 8.700-5.500 9.700C8.200 11.700 6.500 8.500 6.500 3z" fill="currentColor" fill-opacity=".28"/>'
        '<path d="M12 12.700V19M8 21.500h8M6.800 6.500h10.400"/></g>'
    ),

    "herb": (
        f'<g {_S}><path d="M12 22V4"/>'
        '<path d="M12 8c-3 0-5-1.500-5.500-4 3 0 5 1.500 5.500 4zM12 8c3 0 5-1.500 5.500-4-3 0-5 1.500-5.500 4z" fill="currentColor" fill-opacity=".3"/>'
        '<path d="M12 14c-3 0-5-1.500-5.500-4 3 0 5 1.500 5.500 4zM12 14c3 0 5-1.500 5.500-4-3 0-5 1.500-5.500 4z" fill="currentColor" fill-opacity=".3"/>'
        '<path d="M12 20c-3 0-5-1.500-5.500-4 3 0 5 1.500 5.500 4zM12 20c3 0 5-1.500 5.500-4-3 0-5 1.500-5.500 4z" fill="currentColor" fill-opacity=".3"/></g>'
    ),

    "bow": (
        f'<g {_S}><path d="M7 2.800c9 3.200 9 15.200 0 18.400" fill="currentColor" fill-opacity=".12"/>'
        '<path d="M7 2.800v18.400M3 12h17M16.500 8.700 20 12l-3.500 3.300M3 12l-1.200-1.800M3 12l-1.200 1.800"/></g>'
    ),

    "acorn": (
        f'<g {_S}><path d="M5.800 10.500c0-3.300 2.700-5.500 6.200-5.500s6.200 2.200 6.200 5.500z" fill="currentColor" fill-opacity=".35"/>'
        '<path d="M7 10.500c0 6 2 9.800 5 11 3-1.200 5-5 5-11"/>'
        '<path d="M12 5V2.800M9 8l.8 1M12.500 7.200l.6 1.300M15.200 8.200l.8 1" opacity=".7"/></g>'
    ),

    "worm": (
        f'<g {_S}><path d="M3.500 17c0-5 5.500-5.500 5.500-1.500s6 3.500 6-1.500c0-3 3-4.500 5.500-3" stroke-width="3.200" opacity=".4"/>'
        '<path d="M3.500 17c0-5 5.500-5.500 5.500-1.500s6 3.500 6-1.500c0-3 3-4.500 5.500-3"/></g>'
        f'<g {_SOLID}><circle cx="20" cy="10.300" r="1.300"/></g>'
    ),

    "antlers": (
        f'<g {_S}><path d="M12 21v-8M12 13c-3 0-5.200-2.200-5.200-6.200M6.800 11.200C4.800 11.200 3.700 10 3.500 8M9.300 12.300 8.800 8M12 13c3 0 5.200-2.200 5.200-6.200M17.200 11.200c2 0 3.100-1.200 3.300-3.200M14.700 12.300l.5-4.300"/>'
        '<path d="M8.800 21c0-2.800 6.400-2.800 6.400 0z" fill="currentColor" fill-opacity=".3"/></g>'
    ),

    "beaver": (
        f'<g {_S}><circle cx="12" cy="12" r="7.500" fill="currentColor" fill-opacity=".25"/>'
        '<circle cx="6.500" cy="6" r="2.300" fill="currentColor" fill-opacity=".3"/><circle cx="17.500" cy="6" r="2.300" fill="currentColor" fill-opacity=".3"/>'
        '<path d="M10.400 14.500h3.200v4h-3.200z" fill="currentColor" fill-opacity=".1"/><path d="M12 14.500v4"/></g>'
        f'<g {_SOLID}><circle cx="9" cy="10.500" r="1"/><circle cx="15" cy="10.500" r="1"/><path d="M11 12.800h2l-1 1.200z"/></g>'
    ),

    "blue_moon": (
        f'<g {_S}><circle cx="11.500" cy="12.500" r="8" fill="currentColor" fill-opacity=".25"/>'
        '<path d="M7.500 10.500a3.200 3.200 0 0 0 3.600 3.600M13.500 16.800a2 2 0 0 0 2.600-2"/>'
        '<path d="M19 2.200v4M17 4.200h4"/></g>'
    ),

    "black_moon": (
        f'<g {_S}><circle cx="12" cy="12" r="8.500" fill="currentColor" fill-opacity=".8"/>'
        '<circle cx="12" cy="12" r="10.500" stroke-dasharray="1.600 2.400" opacity=".6"/></g>'
    ),

    "birch": (
        f'<g {_S}><path d="M12 22V9"/>'
        '<ellipse cx="12" cy="7" rx="4.600" ry="5.200" fill="currentColor" fill-opacity=".28"/>'
        '<path d="M10.300 14h3.400M10.800 17.500h2.800M10.300 11.500h2.200"/><path d="M8.500 22h7"/></g>'
    ),

    "willow": (
        f'<g {_S}><path d="M12 22V8"/>'
        '<path d="M12 7c-5-1.500-8 1.500-8 7.500M12 7c5-1.500 8 1.500 8 7.500M12 7c-3-1-5.300 1-5.300 5.500M12 7c3-1 5.300 1 5.300 5.500M12 7V13" '
        'fill="none"/>'
        '<path d="M4 14.500c0 2.500.8 4.200.8 4.200M20 14.500c0 2.500-.8 4.200-.8 4.200M6.700 12.500c0 1.800.5 3 .5 3M17.300 12.500c0 1.800-.5 3-.5 3" opacity=".7"/></g>'
    ),

    "holly": (
        f'<g {_S}><path d="M12 2.500 14 5.500 17.200 5 16.500 8.500 20 10 18 13 20.300 16 16.500 16.500 16 20 13 19 12 21.800 11 19 8 20 7.500 16.500 3.700 16 6 13 4 10 7.500 8.500 6.800 5 10 5.500z" '
        'fill="currentColor" fill-opacity=".28"/><path d="M12 5v14M12 10l-3.500-1.500M12 10l3.500-1.500M12 14.500 8.500 13M12 14.500l3.500-1.500" opacity=".7"/></g>'
        f'<g {_SOLID}><circle cx="19.200" cy="19" r="1.800"/><circle cx="16.400" cy="21" r="1.500"/></g>'
    ),

    "ivy": (
        f'<g {_S}><path d="M12 21.500c-6-.5-9-4.500-8-9 2-.5 4 .5 4.800 2 .3-3 .8-5.500 3.200-9.500 2.400 4 2.900 6.500 3.200 9.500.8-1.500 2.800-2.500 4.800-2 1 4.500-2 8.500-8 9z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M12 21.500V6.500M12 17l-4-2.500M12 17l4-2.500"/></g>'
    ),

    "reed": (
        f'<g {_S}><path d="M12 22V9M7.500 22V12M16.500 22V13"/>'
        '<ellipse cx="12" cy="6.500" rx="2" ry="4.200" fill="currentColor" fill-opacity=".4"/>'
        '<path d="M12 2.300V1M7.500 12c-1-1.500-1-3.500 0-5M16.500 13c1-1.500 1-3.500 0-5"/></g>'
    ),

    "elderflower": (
        f'<g {_S}><path d="M12 22V10M12 14c-3 0-4.500-1.500-5-3.500M12 14c3 0 4.500-1.500 5-3.500"/></g>'
        f'<g {_SOLID} fill-opacity=".6">'
        + "".join(f'<circle cx="{x}" cy="{y}" r="1.350"/>'
                  for x, y in ((12, 3.500), (9, 4.800), (15, 4.800), (7, 7.200), (10, 7), (14, 7), (17, 7.200),
                               (8.300, 10), (12, 9.600), (15.700, 10), (12, 6.200)))
        + '</g>'
    ),

    "tree_round": (
        f'<g {_S}><path d="M12 22v-7"/>'
        '<circle cx="8.500" cy="10.500" r="4.500" fill="currentColor" fill-opacity=".28"/>'
        '<circle cx="15.500" cy="10.500" r="4.500" fill="currentColor" fill-opacity=".28"/>'
        '<circle cx="12" cy="6.500" r="4.500" fill="currentColor" fill-opacity=".28"/>'
        '<path d="M9 22h6"/></g>'
    ),

    "plum_blossom": (
        f'<g {_S}><path d="M2.500 21.500C8 17.500 12 16 15.500 12 18 9.300 19.500 6.500 21.500 2.500" stroke-width="1.800"/></g>'
        f'<g fill="none" stroke="currentColor" stroke-width=".9">{_flower(7.500, 15, 1.900, 2.800)}{_flower(15, 9.800, 1.900, 2.800, 20)}'
        f'{_flower(19.300, 4.500, 1.300, 1.900, 40)}</g>'
    ),

    "peach": (
        f'<g {_S}><path d="M12 21.500c-4.800 0-8-3.500-8-8 0-3.800 2.500-6.800 6-7.500 1-.2 1.500.8 2 .8s1-1 2-.8c3.500.7 6 3.700 6 7.500 0 4.500-3.200 8-8 8z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M12 6.800C12 5 12.800 3.600 14.500 2.800M12 6.800c-1.200-2-3-2.500-5-1.800 1 2.200 3 2.700 5 1.800zM12 8.500c-.8 3-.8 6.500 0 10" opacity=".7"/></g>'
    ),

    "peony": (
        f'<g {_S}>{_petals(8, 12, 12, 3.600, 4.400, 5, opacity=".22")}'
        f'{_petals(6, 12, 12, 2.800, 3.400, 2.800, rot=30, opacity=".3")}'
        '<circle cx="12" cy="12" r="1.800" fill="currentColor" fill-opacity=".7"/></g>'
    ),

    "pomegranate": (
        f'<g {_S}><path d="M12 6.500c-5 0-8 3.300-8 7.500 0 4.200 3.500 7.500 8 7.500s8-3.300 8-7.500c0-4.200-3-7.500-8-7.500z" '
        'fill="currentColor" fill-opacity=".28"/>'
        '<path d="M8.500 6.500 9.800 3.200 12 5.200l2.200-2 1.300 3.300"/>'
        '<path d="M12 11v7M8.500 13.500c.6 2 .6 3.500 0 5M15.500 13.500c-.6 2-.6 3.500 0 5" opacity=".6"/></g>'
    ),

    "lotus": (
        f'<g {_S}><path d="M12 3.500c3 3 4 7 0 12.500-4-5.500-3-9.500 0-12.500z" fill="currentColor" fill-opacity=".35"/>'
        '<path d="M3.500 9c4 .3 7 2.700 8.500 7-4.500.8-8.500-1.500-8.500-7zM20.500 9c-4 .3-7 2.700-8.500 7 4.500.8 8.500-1.500 8.500-7z" '
        'fill="currentColor" fill-opacity=".22"/>'
        '<path d="M2.500 19.500c3 1.500 6 1.700 9.500 1.700s6.500-.2 9.500-1.700" /></g>'
    ),

    "orchid": (
        f'<g {_S}><ellipse cx="12" cy="7" rx="3" ry="4.600" fill="currentColor" fill-opacity=".3"/>'
        '<ellipse cx="6.800" cy="11.800" rx="4.800" ry="3" transform="rotate(-18 6.800 11.800)" fill="currentColor" fill-opacity=".3"/>'
        '<ellipse cx="17.200" cy="11.800" rx="4.800" ry="3" transform="rotate(18 17.200 11.800)" fill="currentColor" fill-opacity=".3"/>'
        '<ellipse cx="12" cy="15.500" rx="2.700" ry="3.200" fill="currentColor" fill-opacity=".5"/>'
        '<path d="M12 18.700V22"/></g>'
    ),

    "chrysanthemum": (
        f'<g {_S}>'
        + "".join(f'<path d="M12 3.200v5.300" transform="rotate({k * 22.5} 12 12)"/>' for k in range(16))
        + '<circle cx="12" cy="12" r="3.200" fill="currentColor" fill-opacity=".5"/></g>'
    ),
}
