"""Skyfield timescale and ephemeris (loaded once)."""

from skyfield.api import load

ts = load.timescale()
eph = load("de421.bsp")
