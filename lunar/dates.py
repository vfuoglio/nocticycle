"""Small date helpers."""

from calendar import monthrange
from datetime import date

from . import config as cfg


def month_name(m: int) -> str:
    """
    Return the month name for a given month number.

    This helper adapts its output based on the active rendering mode:
    - When COSMETICS_MODE is enabled, the full month name is used
      (e.g., "January", "February").
    - When COSMETICS_MODE is disabled (print‑friendly mode), the
      abbreviated three‑letter form is used (e.g., "Jan", "Feb").

    Parameters
    ----------
    m : int
        Month number in the range 1–12.

    Returns
    -------
    str
        The formatted month name, full or abbreviated depending on
        the current cosmetic mode.
    """
    if cfg.COSMETICS_MODE:
        return date(2000, m, 1).strftime("%B")   # Full month name
    else:
        return date(2000, m, 1).strftime("%b")   # Abbreviated name
