"""NoctiCycle entry point: ties CLI, location, computation and writers together."""

import os
import sys
from zoneinfo import ZoneInfo

from . import config as cfg
from .astro import compute_phase_events_for_year
from .cli import apply_cli_to_globals, parse_cli_args, validate_output_path
from .html_writer import write_html
from .ics import write_ics
from .location import LocationError, detect_timezone, resolve_location


def main():

    args = parse_cli_args()
    apply_cli_to_globals(args)

    if args.output:
        try:
            output_path = validate_output_path(args.output)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        output_path = os.path.join(cfg.BASE_DIR, f"lunar_calendar_{cfg.CITY}_{cfg.YEAR}.html")

    if cfg.TRADITION and not cfg.COSMETICS_MODE:
        print("Note: --tradition is only available in the interactive layout; "
              "ignoring it for --print-format.")
        cfg.TRADITION = None

    if cfg.WHEEL and not cfg.COSMETICS_MODE:
        print("Note: --wheel is only available in the interactive layout; "
              "ignoring it for --print-format.")
        cfg.WHEEL = None

    # Resolve the location first: it provides the timezone when --tz is
    # omitted and the hemisphere used to orient the moon icons.
    tz_given = cfg.TZ is not None
    try:
        resolve_location()
        if not tz_given:
            cfg.TZ = detect_timezone(cfg.LAT, cfg.LON)
            print(f"Detected timezone: {cfg.TZ}")
    except LocationError as e:
        if tz_given and not cfg.SHOW_RISE_SET_TIMES:
            print(f"\n⚠  {e}")
            print("   Continuing without coordinates (moon icons use the northern-hemisphere orientation).\n")
        else:
            print(f"\nError: {e}")
            sys.exit(1)

    cfg.validate_config()

    cfg.TZINFO = ZoneInfo(cfg.TZ)

    print(f"Generating lunar calendar for {cfg.YEAR} — {cfg.CITY}")
    print(f"Timezone: {cfg.TZ}")

    events, events_by_month = compute_phase_events_for_year(cfg.YEAR)

    write_html(
        cfg.YEAR,
        output_path
    )

    if args.ics:
        if args.ics == "auto":
            ics_path = os.path.splitext(output_path)[0] + ".ics"
        else:
            ics_path = os.path.abspath(os.path.expanduser(args.ics))
            if not ics_path.lower().endswith(".ics"):
                print(f"Error: --ics path must end in .ics (got '{args.ics}')")
                sys.exit(1)
        try:
            write_ics(cfg.YEAR, ics_path)
        except OSError as e:
            print(f"Error: could not write '{ics_path}': {e}")
            sys.exit(1)

    print("Done.")
