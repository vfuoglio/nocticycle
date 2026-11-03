"""Command-line parsing and output-path validation."""

from datetime import date
import argparse
import os
from . import traditions
from . import wheels
from . import moon_names
from . import config as cfg


def parse_cli_args():
    """
    Parse command-line arguments for NoctiCycle.

    This function defines the command-line interface for the lunar calendar
    generator. Only --city is required: --tz is detected from the city's
    coordinates when omitted, and --year defaults to the current year.
    Optional flags that override the default global configuration
    values defined in the script.

    Required arguments
    ------------------
    --city : str
        The display name of the city (e.g., "Halifax").

    Optional location/time arguments
    --------------------------------
    --tz : str
        The IANA timezone identifier (e.g., "America/Halifax"). Detected
        automatically from the geocoded coordinates when omitted.
    --year : int
        The calendar year to generate (default: the current year).

    Optional flags
    --------------
    --show-luminance / --hide-luminance : bool
        Enable or disable moon illumination percentage display.

    --show-event-time / --hide-event-time : bool
        Enable or disable event time display for lunar phases.

    --exact-event-illumination / --midnight-illumination : bool
        Choose whether illumination is computed at the exact event moment
        or at local midnight.

    --show-rise-set-time : bool
        Enable or disable showing moonrise and moon set times

    --tradition : str
        Annotate each day with a cultural lunar tradition: maori, hindu or
        wiccan (interactive layout only).

    --wheel : str
        Add the yearly festivals of a tradition (a "year wheel"): wicca,
        druid, slavic, eastasian or heathen (interactive layout only).

    --moon-names : str
        Name each lunation: anishinaabe, wiccan, almanac, celtic or chinese
        (interactive layout only).

    --show-quarters : bool
        Mark first-quarter and last-quarter days in the calendar.

    --ics [PATH] : str
        Also write the new, quarter and full moon events as an iCalendar
        (.ics) file that can be imported or subscribed to in calendar apps.

    --print-format : bool
        Use a simplified, print‑friendly layout. When this flag is present,
        cosmetic styling and enhanced visual elements are disabled. The
        default behavior (without this flag) is to use the full cosmetic
        layout.

    --paper : str
        Paper size used by --print-format (letter, a4, legal, tabloid).

    --print-style : str
        Dark-side rendering for --print-format (grey, hatched, solid).

    --print-layout : str
        Print orientation: rows (one month per row) or columns (one month
        per column).

    --output / -o : str
        Optional full path to the output HTML file.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with attributes corresponding to each CLI option.
    """
    parser = argparse.ArgumentParser(
        description="Generate a full-year lunar calendar with NoctiCycle."
    )

    # Required
    parser.add_argument(
        "--city",
        required=True,
        help="City name for display (e.g., 'Halifax')."
    )
    parser.add_argument(
        "--tz",
        default=None,
        help="IANA timezone (e.g., 'America/Halifax'). Optional: when omitted "
             "it is detected from the city's coordinates."
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Year to generate the lunar calendar for (default: current year)."
    )

    # Optional overrides
    parser.add_argument("--show-luminance", action="store_true",
                        help="Force-enable moon illumination display.")
    parser.add_argument("--hide-luminance", action="store_true",
                        help="Disable moon illumination display.")

    parser.add_argument("--show-event-time", action="store_true",
                        help="Force-enable event time display.")
    parser.add_argument("--hide-event-time", action="store_true",
                        help="Disable event time display.")

    parser.add_argument("--exact-event-illumination", action="store_true",
                        help="Compute illumination at exact event time.")
    parser.add_argument("--midnight-illumination", action="store_true",
                        help="Compute illumination at local midnight.")

    parser.add_argument("--illumination-trend", action="store_true",
                        help="Enable per-day illumination trend sparkline (default: off)")

    parser.add_argument("--show-rise-set-times", action="store_true",
                        help="Display moonrise and moonset times for each day.")

    parser.add_argument("--tradition", choices=traditions.TRADITION_CHOICES, default=None,
                        help="Annotate every day with a cultural lunar calendar: 'maori' "
                             "(Maramataka nights), 'hindu' (Panchang tithi) or 'wiccan' "
                             "(esbat phases). Not available with --print-format.")

    parser.add_argument("--wheel", choices=wheels.WHEEL_CHOICES, default=None,
                        help="Add the yearly festivals of a tradition on top of the calendar: "
                             "'wicca' (Wheel of the Year), 'druid' (Eightfold Wheel), 'slavic' "
                             "(Kolo Goda), 'eastasian' (24 solar terms) or 'heathen' (Seasonal "
                             "Tides). Combines with --tradition. Not available with --print-format.")

    parser.add_argument("--moon-names", choices=moon_names.MOON_NAME_CHOICES, default=None,
                        help="Name each lunation: 'anishinaabe' (Ojibwe 13 moons), 'wiccan' (esbat "
                             "names), 'almanac' (Algonquin / Almanac names), 'celtic' (Celtic tree "
                             "calendar) or 'chinese' (lunar months). Combines with --tradition and "
                             "--wheel. Not available with --print-format.")

    parser.add_argument("--show-quarters", action="store_true",
                        help="Mark first-quarter and last-quarter days (with their times).")

    parser.add_argument("--ics", nargs="?", const="auto", default=None, metavar="PATH",
                        help="Also export new/quarter/full moon events as an .ics calendar "
                             "file (default path: next to the HTML file).")

    parser.add_argument("-o", "--output",type=str,
                        help="Optional full path to the output HTML file."
    )



    # Print‑friendly mode (disables cosmetics)
    parser.add_argument(
        "--print-format",
        action="store_true",
        help="Use a simplified layout suitable for printing."
    )
    parser.add_argument(
        "--print-style",
        choices=("grey", "hatched", "solid"),
        default="grey",
        help="How the dark side of the moon is drawn with --print-format: "
             "light grey (default), diagonal hatching (best on black-and-white "
             "printers) or solid black."
    )
    parser.add_argument(
        "--print-layout",
        choices=("rows", "columns"),
        default="rows",
        help="Print orientation: 'rows' puts one month per row (largest moons, "
             "default); 'columns' puts one month per column and days down the page "
             "(planner style)."
    )
    parser.add_argument(
        "--paper",
        choices=sorted(cfg.PAPER_SIZES),
        default="letter",
        help="Paper size for --print-format; the year is fitted on one "
             "landscape page of this size (default: letter)."
    )

    return parser.parse_args()


def apply_cli_to_globals(args):
    """
    Apply command-line argument values to the module's global configuration
    variables.

    This function updates the global configuration based on CLI input.
    Required parameters always overwrite the defaults. Optional flags only
    override their corresponding global values if explicitly provided.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed CLI arguments from `parse_cli_args()`.

    Effects
    -------
    Updates the following global variables:
        CITY : str
            Display name of the selected location.
        TZ : str
            IANA timezone identifier for the chosen location.
        YEAR : int
            Calendar year to generate.
        SHOW_LUMINANCE : bool
            Whether to display moon illumination percentages.
        SHOW_EVENT_TIME : bool
            Whether to display exact event times for lunar phases.
        SHOW_RISE_SET_TIMES : bool
            Whether to display moonrise and moonset times.
        USE_EXACT_EVENT_ILLUMINATION : bool
            Whether illumination on event days is computed at the exact
            event moment instead of local midnight.
        COSMETICS_MODE : bool
            Controls whether the enhanced visual layout is used. Cosmetics
            are enabled by default; they are disabled only when the
            --print-format flag is provided.
    """


    # Required
    cfg.CITY = args.city
    cfg.TZ = args.tz            # may be None: resolved later from the coordinates
    cfg.YEAR = args.year if args.year is not None else date.today().year

    # Optional overrides
    if args.show_luminance:
        cfg.SHOW_LUMINANCE = True
    if args.hide_luminance:
        cfg.SHOW_LUMINANCE = False

    if args.show_event_time:
        cfg.SHOW_EVENT_TIME = True
    if args.hide_event_time:
        cfg.SHOW_EVENT_TIME = False

    if args.exact_event_illumination:
        cfg.USE_EXACT_EVENT_ILLUMINATION = True
    if args.midnight_illumination:
        cfg.USE_EXACT_EVENT_ILLUMINATION = False

    cfg.SHOW_RISE_SET_TIMES = args.show_rise_set_times
    cfg.SHOW_QUARTERS = args.show_quarters
    cfg.TRADITION = args.tradition
    cfg.WHEEL = args.wheel
    cfg.MOON_NAMES = args.moon_names
    cfg.PAPER = args.paper
    cfg.PRINT_STYLE = args.print_style
    cfg.PRINT_LAYOUT = args.print_layout

    # Default is already True at the top of the script.
    # If print-format is requested, disable cosmetics.
    if args.print_format:
        cfg.COSMETICS_MODE = False

    cfg.ILLUMINATION_TREND = args.illumination_trend



def validate_output_path(path: str) -> str:
    """
    Validate that the user‑provided output path is a writable HTML file.

    This function is used to support the optional `-o/--output` CLI
    argument, allowing the user to specify a custom output location for
    the generated HTML file. The function ensures that the path is
    syntactically valid, points to an existing directory, and that the
    file can be created or overwritten.

    Parameters
    ----------
    path : str
        Full filesystem path to the desired output HTML file. The path
        must end with `.html` or `.htm`. Relative paths are resolved to
        absolute paths.

    Returns
    -------
    str
        The normalized absolute path to the output file, guaranteed to
        be writable.

    Raises
    ------
    ValueError
        If the path does not end with `.html`/`.htm`, if the directory
        does not exist, or if the file cannot be created due to
        permission or I/O issues.

    Notes
    -----
    • This function does not create the file; it only verifies that it
      *can* be created.

    • Directory existence is required; directories are not created
      automatically.

    • Write permission is checked using `os.access()` and by attempting
      to open the file in append mode.

    • The returned path is always absolute, even if the user supplied a
      relative path.
    """
    import os

    # Must end with .html or .htm
    if not path.lower().endswith((".html", ".htm")):
        raise ValueError("Output file must end with .html or .htm")

    abs_path = os.path.abspath(path)
    directory = os.path.dirname(abs_path)

    # Directory must exist
    if not os.path.isdir(directory):
        raise ValueError(f"Directory does not exist: {directory}")

    # Directory must be writable
    if not os.access(directory, os.W_OK):
        raise ValueError(f"No write permission in directory: {directory}")

    # Attempt to open the file (append mode does not destroy contents)
    try:
        with open(abs_path, "a", encoding="utf-8"):
            pass
    except Exception as e:
        raise ValueError(f"Cannot create output file: {e}")

    return abs_path
