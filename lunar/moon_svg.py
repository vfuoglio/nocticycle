"""SVG rendering of the moon and illumination sparklines."""

from dataclasses import dataclass
import math
from . import config as cfg


@dataclass
class TerminatorGeometry:
    """Geometric description of the lunar terminator curve.

    Attributes
    ----------
    arc_radius : float
        Radius of curvature of the terminator arc.
    terminator_on_right : bool
        True if the bright side of the moon is on the right.
    light_from_left : bool
        True if the illuminated portion is on the left side.
    """
    arc_radius: float
    terminator_on_right: bool
    light_from_left: bool


def compute_terminator_geometry(phase: float, radius: float) -> TerminatorGeometry:
    """Compute the terminator arc geometry for a given lunar phase.

    Parameters
    ----------
    phase : float
        Lunation fraction in the range [0, 1], where:
        - 0.0 = new moon
        - 0.5 = full moon
        - 1.0 = new moon again
    radius : float
        Radius of the moon disc in SVG coordinate units.

    Returns
    -------
    TerminatorGeometry
        A dataclass describing the curvature and orientation of the terminator.
    """

    QUADRANTS = [
        (0.25, lambda p: p,          True,  False),
        (0.50, lambda p: 0.5 - p,    False, False),
        (0.75, lambda p: p - 0.5,    True,  True),
        (1.00, lambda p: 1 - p,      False, True),
    ]

    for threshold, L_fn, right, lit_left in QUADRANTS:
        if phase <= threshold:
            L = L_fn(phase)
            terminator_on_right = right
            light_from_left = lit_left
            break

    # Compute terminator arc curvature
    x = radius * (1 - math.cos(2 * math.pi * L))
    n = radius - x
    arc_radius = (radius**2 + n**2) / (2 * n)

    return TerminatorGeometry(
        arc_radius=arc_radius,
        terminator_on_right=terminator_on_right,
        light_from_left=light_from_left,
    )


def render_moon_svg(phase: float, size: int = 24, mirror: bool = False) -> str:
    """Render an SVG moon icon for a given lunar phase.

    Parameters
    ----------
    phase : float
        Lunation fraction (0.0 = new, 0.5 = full).
    size : int, optional
        Width and height of the SVG viewport in pixels. Default is 24.
    mirror : bool, optional
        Flip the icon horizontally. Seen from the southern hemisphere the
        Moon appears upside down, so the lit side of a waxing moon is on
        the left. Default is False (northern-hemisphere view).

    Returns
    -------
    str
        SVG markup representing the moon at the given phase.
    """

    r = size / 2
    geom = compute_terminator_geometry(phase, r)

    # Determine shading classes
    colours = {
        "left":  "light" if geom.light_from_left else "shadow",
        "right": "shadow" if geom.light_from_left else "light",
    }

    # SVG path components
    move_to_top = f"M{r},0"
    disc_left_arc  = f"A {r} {r} 0 0 1 {r} 0"
    disc_right_arc = f"A {r} {r} 0 0 0 {r} 0"

    terminator_arc = (
        f"A {geom.arc_radius} {geom.arc_radius} "
        f"0 0 {'1' if geom.terminator_on_right else '0'} {r} {size}"
    )

    # Build the two halves of the moon
    paths = [
        f'<path d="{move_to_top} {terminator_arc} {disc_left_arc}" class="{colours["left"]}"/>',
        f'<path d="{move_to_top} {terminator_arc} {disc_right_arc}" class="{colours["right"]}"/>'
    ]

    # Outline circle
    outline = f'<circle cx="{r}" cy="{r}" r="{r - 0.5}" class="moon-outline"/>'

    body = f'{outline}{"".join(paths)}'
    if mirror:
        body = f'<g transform="translate({size},0) scale(-1,1)">{body}</g>'

    return f'<svg class="moon-svg" viewBox="0 0 {size} {size}">{body}</svg>'


def is_southern_hemisphere() -> bool:
    """True when the geocoded location lies south of the equator."""
    return cfg.LAT is not None and cfg.LAT < 0


def render_illumination_sparkline(values: list[float], width: int = 80, height: int = 18) -> str:
    """
    Render a compact SVG Bézier-curve sparkline representing illumination trends.

    The curve is colored based on waxing or waning behavior:
        • Waxing  → teal (#88c0d0)
        • Waning  → amber (#d08770)

    Parameters
    ----------
    values : list of float
        Illumination percentages (0–100) sampled over several days.
    width : int, optional
        Width of the SVG viewport in pixels. Default is 80.
    height : int, optional
        Height of the SVG viewport in pixels. Default is 18.

    Returns
    -------
    str
        SVG markup containing a smoothed Bézier curve sparkline.
    """
    if not values:
        return ""

    n = len(values)
    if n == 1:
        x = width / 2
        y = height - (values[0] / 100.0) * height
        return (
            f'<svg class="illum-graph" viewBox="0 0 {width} {height}">'
            f'<circle cx="{x}" cy="{y}" r="2" fill="#88c0d0" />'
            f'</svg>'
        )

    # Determine waxing vs waning
    waxing = values[-1] > values[0]
    color = "#88c0d0" if waxing else "#d08770"   # teal vs amber

    # Convert values to coordinates
    step_x = width / (n - 1)
    pts = []
    for i, v in enumerate(values):
        x = i * step_x
        y = height - (v / 100.0) * height
        pts.append((x, y))

    # Build a smooth cubic Bézier path
    d = f"M {pts[0][0]:.2f},{pts[0][1]:.2f} "

    for i in range(1, n):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        cx = (x0 + x1) / 2
        d += f"C {cx:.2f},{y0:.2f} {cx:.2f},{y1:.2f} {x1:.2f},{y1:.2f} "

    return (
        f'<svg class="illum-graph" viewBox="0 0 {width} {height}">'
        f'<path d="{d}" stroke="{color}" stroke-width="1.8" fill="none" />'
        f'</svg>'
    )
