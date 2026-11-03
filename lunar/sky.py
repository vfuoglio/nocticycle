"""Skyfield timescale and ephemeris (loaded once).

The DE421 ephemeris (about 17 MB) is looked up, in order, in:
1. the folder bundled with the application (release builds ship it),
2. the per-user data folder (``$XDG_DATA_HOME/nocticycle``, by default
   ``~/.local/share/nocticycle``), where it is downloaded on first use.
"""

import os
import sys
from pathlib import Path

from skyfield.api import Loader

EPHEMERIS = "de421.bsp"


def _data_dir() -> Path:
    candidates = [Path(__file__).resolve().parent / "data"]
    if getattr(sys, "_MEIPASS", None):
        candidates.insert(0, Path(sys._MEIPASS) / "lunar" / "data")
    for c in candidates:
        if (c / EPHEMERIS).exists():
            return c
    base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    path = base / "nocticycle"
    path.mkdir(parents=True, exist_ok=True)
    return path


_loader = Loader(str(_data_dir()))

ts = _loader.timescale()
eph = _loader(EPHEMERIS)
