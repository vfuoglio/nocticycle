# nocticycle

NoctiCycle is a Python tool for exploring the rhythm of the Moon. It computes precise lunar phases, illumination and event timings for **your location**, and generates a full year as a single, self-contained HTML calendar with crisp SVG moon icons.

NoctiCycle computes:

- Daily moon phase, illumination and moon age
- Exact times of new, quarter and full moons (localized to your timezone)
- Waxing/waning classification
- Optional moonrise and moonset times
- Optional per-day **illumination trend sparklines**
- Optional cultural overlays: **Māori Maramataka**, **Hindu tithi** and **Wiccan esbat** calendars

It produces either a rich interactive page or a one-page, print-ready layout. The output works offline, in any browser.

**Default theme**
<a href="screenshots/calendar_2017.png">
  <img src="screenshots/calendar_2017.png" width="100%" style="border-radius: 8px; border: 1px solid #ccc;" />
</a>

**Print format**
<a href="screenshots/calendar_2017-print.png">
  <img src="screenshots/calendar_2017-print.png" width="100%" style="border-radius: 8px; border: 1px solid #ccc;" />
</a>

---

## 🌟 Why this exists

Most moon calendars online are:

- inaccurate
- cluttered with ads
- not printable
- not customizable
- or require an internet connection

NoctiCycle fixes that:

- Everything is computed locally using **Skyfield** and NASA ephemeris data
- Output is a single, portable HTML file
- You choose the year, location, and display options
- The cosmetic mode produces a modern, elegant layout
- The print mode fits the whole year on one landscape page

It’s perfect for planners, journals, almanacs, or anyone who loves tracking the Moon.

---

# 🚀 Features

### ✔ Accurate lunar phase calculations

Uses Skyfield + DE421 ephemeris for precise astronomical results.

### ✔ Localized event times

New/full moon timestamps are converted to your chosen timezone.

### ✔ SVG moon rendering

Each day shows a crisp, resolution‑independent moon icon.

### ✔ Illumination percentage

The Moon’s brightness (0–100%) for each day, on by default (`--hide-luminance` to remove it).
On new/full moon days it is evaluated at the exact event moment unless you pass `--midnight-illumination`.

### ✔ Moonrise and moonset times

`--show-rise-set-times` adds the local rise and set time of the Moon to each day.

### ✔ Event times

The exact local moment of each new/full moon (and quarter, with `--show-quarters`) is shown on its day.
Use `--hide-event-time` to turn it off.

### ✔ Optional illumination trend sparkline

A ±3‑day mini‑graph showing illumination change.  
Enabled via:

```
--illumination-trend
```

### ✔ Two display modes

- **Interactive mode** (default): modern, elegant, visually rich, with a detail card per day
- **Print mode** (`--print-format`): the whole year on one landscape sheet, legible in black and white
  (see [Print on one landscape page](#print-on-one-landscape-page))

### ✔ Interactive day details

Click (or press Enter on) any day to open a card with a large moon, the phase name,
illumination, moon age, rise/set times (with `--show-rise-set-times`) and the next
new/full moon. Use the arrow keys to move between days and Esc to close.

### ✔ Today highlight and next-events banner

The current day is highlighted and scrolled into view, and a banner at the top shows
the next new and full moon with a countdown.

### ✔ Responsive layout and light/dark theme

On narrow screens each month becomes a week grid. The default theme follows your
system's light/dark preference.

### ✔ Automatic timezone detection

`--tz` is optional: the timezone is detected from the city's coordinates.

### ✔ Calendar export (.ics)

`--ics` exports new, quarter and full moon events for import into Google/Apple/Outlook calendars.

### ✔ Hemisphere-aware icons and quarter markers

Moon icons are mirrored for locations in the southern hemisphere, and `--show-quarters`
marks first- and last-quarter days.

### ✔ Cultural lunar calendars (`--tradition`)

The Moon has been used as a calendar for thousands of years, and many living cultures give each
day of the lunar month its own name, character and customs. With `--tradition` NoctiCycle lays
one of three such calendars on top of the astronomical one. Each overlay adds a themed banner
and legend, a colour-coded icon and short label on every day, and a full explanation in the
day card (click any day). It works on phones and in light and dark themes.

```
--tradition maori | hindu | wiccan
```

Without the option nothing changes. The overlay is for the interactive page only: with
`--print-format` the option is ignored and a note is printed.

#### `maori`: Māori Maramataka (Aotearoa New Zealand)

The *Maramataka* is the traditional Māori lunar calendar. Every night of the lunar month has a
name (about 29 in total) and a character that guided when to plant, gather, fish or rest. The
cycle starts at the dark moon with **Whiro**, passes through the **Tamatea** nights (changeable,
unpredictable weather and moods), peaks at **Rākaunui** around the full moon, and runs through
the **Korekore** nights (traditionally poor for planting) and the **Tangaroa** nights (good for
fishing) down to **Mutuwhenua**, the nights when the moon "sleeps" before the new one.

NoctiCycle shows the night name for each calendar day (counted at dusk, 18:00 local time, since
the Māori day begins with the night), coloured by character: rest, rising energy, high energy,
Tamatea (unpredictable) and Tangaroa (sea and fishing). The day card gives the meaning.
Southern-hemisphere places such as Auckland also get correctly mirrored moon icons.

<a href="screenshots/tradition_maori.png">
  <img src="screenshots/tradition_maori.png" alt="Māori Maramataka overlay (Auckland, 2025)" width="100%" style="border-radius: 8px; border: 1px solid #ccc;" />
</a>

#### `hindu`: Hindu Panchang, the tithi

The Hindu calendar (*Panchang*) divides the lunar month into 30 **tithis**. A tithi is the time it
takes the Moon to gain 12° of angle on the Sun, so it is purely astronomical. The month has two
halves, or *Pakshas*: **Shukla Paksha** (the waxing, "bright" fortnight, tithis 1–15, ending in
**Purnima**, the full moon) and **Krishna Paksha** (the waning, "dark" fortnight, ending in
**Amavasya**, the new moon). Many observances hang on specific tithis.

NoctiCycle shows the tithi in effect at **local sunrise** for each day, the usual convention for
assigning a tithi to a date. Shukla days are gold and Krishna days indigo. Badges mark
**Ekadashi** (11th tithi, a fasting day), **Purnima**, **Amavasya** (honouring ancestors),
**Chaturthi** (associated with Ganesha), **Pradosha** (13th tithi, associated with Shiva) and
**Maha Shivaratri's** monthly form on Krishna Chaturdashi.

<a href="screenshots/tradition_hindu.png">
  <img src="screenshots/tradition_hindu.png" alt="Hindu tithi overlay (Varanasi, 2025)" width="100%" style="border-radius: 8px; border: 1px solid #ccc;" />
</a>

#### `wiccan`: Wiccan esbats

In Wicca and related modern pagan paths, an **esbat** is a ritual or gathering held at a lunar
phase, most often the full moon (the eight seasonal *sabbats* follow the sun and are not part
of this feature). Practices differ between traditions and covens, but the broad associations are
widely shared: the waxing moon is for beginnings and growth, the full moon for peak power and
celebration, the waning moon for banishing and release, and the dark moon for rest and
reflection.

NoctiCycle labels each day as **dark moon**, **waxing crescent** (initiation), **building**
(first quarter to waxing gibbous), **full moon esbat** (peak) or **waning** (release), each with
its own colour, and adds the esbat badge on full-moon days.

<a href="screenshots/tradition_wiccan.png">
  <img src="screenshots/tradition_wiccan.png" alt="Wiccan esbat overlay (Halifax, 2025)" width="100%" style="border-radius: 8px; border: 1px solid #ccc;" />
</a>

#### Accuracy and your own version

These are living traditions, and they differ between communities. The names and short meanings
are general summaries written for this project, not authoritative statements of any tradition.
In particular, **Maramataka night names and meanings vary between iwi and regions**, and published
lists disagree in the middle of the cycle, so NoctiCycle uses one commonly published sequence.
The Hindu tithi is the one at sunrise only; festival dates in a full Panchang follow further
regional rules (and a tithi can start or end at any hour), so check a local Panchang for religious
observance. All data lives in `lunar/traditions.py` and is easy to edit to match your own
lineage.

### ✔ Fully offline

Once generated, the HTML file requires no internet connection.

---

# 📦 Installation

NoctiCycle requires a few external Python packages:

- **Skyfield** — astronomical calculations
- **tzdata** — timezone definitions for systems without IANA zoneinfo
- **geopy** — obtain latitudes and longitudes via OpenStreetMap (Nominatim)
- **timezonefinder** — detect the timezone from the coordinates (only needed when `--tz` is omitted)

Install them with:

```bash
pip install skyfield tzdata geopy timezonefinder
```

---

## 🔧 Why these packages?

### **skyfield**

Used for:

- Loading NASA’s DE421 ephemeris
- Computing lunar positions
- Determining new/full moon events
- Calculating illumination and phase angles

### **tzdata**

Provides timezone definitions for platforms that **don’t ship with IANA zoneinfo**, such as:

- Windows
- Minimal Linux containers
- Some embedded environments

If your system already has full zoneinfo support, `tzdata` simply ensures portability.

---

# 🐍 Using a Python Virtual Environment (Recommended)

A virtual environment keeps dependencies isolated and avoids polluting your system Python.

### 1. Create a virtual environment

```bash
python3 -m venv .venv
```

### 2. Activate it

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies inside the venv

```bash
pip install skyfield tzdata geopy timezonefinder
```

### 4. Run the script

```bash
python3 nocticycle.py --city "Halifax" --tz "America/Halifax" --year 2025
```

### 5. Deactivate when done

```bash
deactivate
```

---

# 📦 How It Works

## 1. You choose a year **and** location

Only `--city` is required (`--tz` is detected automatically and `--year` defaults to the current year):

```
python3 nocticycle.py --city "Halifax" --tz "America/Halifax" --year 2025
```

## 2. NoctiCycle computes all lunar events

- New moons
- Full moons
- Quarter moons (optional)
- Daily illumination and moon age
- Phase classification and, optionally, rise/set times, trend data and tithi/night/esbat labels

## 3. It renders a complete HTML calendar

- One year, twelve months
- SVG moons and phase bands
- Optional sparklines, quarters and cultural overlays
- Or a one-page print layout

## 4. You open the file in any browser

`lunar_calendar_<city>_2025.html` (or the path given with `-o`)

---

# 🧩 Project layout

`nocticycle.py` is a thin launcher; the code lives in the `lunar/` package:

| Module | Role |
|---|---|
| `config.py` | Defaults and shared runtime state |
| `cli.py` | Command-line parsing, output-path validation |
| `location.py` | Geocoding, timezone detection, observer |
| `sky.py` / `astro.py` | Skyfield setup; phases, illumination, moon age, tithi |
| `moon_svg.py` | SVG moons and sparklines |
| `traditions.py` / `tradition_days.py` | Cultural calendar data and per-day lookup |
| `html_writer.py` / `print_writer.py` | Interactive and print outputs |
| `ics.py` | Calendar export |
| `assets.py` / `dates.py` | CSS/JS loading, date helpers |
| `app.py` | `main()` wiring everything together |

CSS and JS stay in `css/` and `js/`.

---

# ⚙️ Configuration

Defaults live in `lunar/config.py`:

```python
YEAR = 2026                    # CLI default: the current year
SHOW_LUMINANCE = True
SHOW_EVENT_TIME = True
USE_EXACT_EVENT_ILLUMINATION = True
COSMETICS_MODE = True          # False with --print-format
ILLUMINATION_TREND = False
```

Command-line flags override these values.

### Required CLI parameters

```
--city "Your City"
```

### Optional parameters

```
--tz "Your/Timezone"       timezone (default: detected from the city)
--year 2027                year (default: current year)
-o, --output FILE.html     output path (default: lunar_calendar_<city>_<year>.html)

--show-luminance / --hide-luminance        illumination % per day (default: shown)
--show-event-time / --hide-event-time      times of new/full moons (default: shown)
--exact-event-illumination                 illumination at the event moment (default)
--midnight-illumination                    illumination at local midnight instead
--illumination-trend                       ±3-day sparkline per day
--show-rise-set-times                      moonrise and moonset
--show-quarters                            mark first/last quarter days
--ics [PATH]                               export events as an .ics file
--tradition maori|hindu|wiccan             cultural lunar calendar overlay

--print-format                             one-page print layout
--paper letter|a4|legal|tabloid            print paper size (default: letter)
--print-style grey|hatched|solid           print moon style (default: grey)
--print-layout rows|columns                print layout (default: rows)
```

Run `python3 nocticycle.py --help` for the full list.

---

# 🏃 Usage

### Basic run (required flags)

```
python3 nocticycle.py --city "Halifax" --tz "America/Halifax"
```

### Specify year

```
python3 nocticycle.py --city "Halifax" --tz "America/Halifax" --year 2027
```

### Print‑friendly layout

```
python3 nocticycle.py --city "Halifax" --tz "America/Halifax" --print-format
```

### Print on one landscape page

```
python3 nocticycle.py --city "Halifax" --year 2026 --print-format --paper a4
```

The whole year is fitted on a single landscape sheet (`letter`, `a4`, `legal` or `tabloid`).
Print format shows the weekday, day number, moon and illumination for every day, weekends
shaded, new/full moon days highlighted (quarters with `--show-quarters`), and a footer listing
the exact event times. Rise/set times and trend graphs are not part of the print format.

- `--print-style grey|hatched|solid` chooses how the dark side of the moon is drawn
  (`hatched` is best on black-and-white printers).
- `--print-layout columns` puts months across and days down the page, planner style.
  Moon icons are smaller there than in the default `rows` layout.
- In your browser's print dialog, set margins to "Default" or "None", scale to 100% and turn
  on "Background graphics" for the best result.

### Enable illumination trend sparkline

```
python3 nocticycle.py --city "Halifax" --tz "America/Halifax" --illumination-trend
```

### Export the events to a calendar app

```
python3 nocticycle.py --city "Halifax" --year 2026 --ics
```

Writes an `.ics` file next to the HTML (or at `--ics PATH`) with the new, quarter and full moon
events, ready to import into Google, Apple or Outlook calendars.

### Cultural calendars

See [Cultural lunar calendars](#-cultural-lunar-calendars---tradition) for what each one shows.

```
python3 nocticycle.py --city "Auckland" --tradition maori
python3 nocticycle.py --city "Varanasi" --tradition hindu --show-rise-set-times
python3 nocticycle.py --city "Halifax" --tradition wiccan
```

### Mark quarter moons

```
python3 nocticycle.py --city "Halifax" --year 2026 --show-quarters
```

### Combine flags

```
python3 nocticycle.py --city "Halifax" --tz "America/Halifax" --year 2026 --illumination-trend --show-event-time
```

---

# 🌓 Display Options

### Illumination percentage

Shows the Moon’s brightness (0–100%).

### Event times

Shows the exact local time of new/full moon.

### Illumination trend sparkline

A ±3‑day mini‑graph showing illumination change.  
Great for quickly seeing waxing vs waning.

### Cosmetic vs Print mode

- Interactive mode includes colours, day cards, sparklines, rise/set times and cultural overlays.
- Print mode strips it down to what reads well on paper: weekday, day, moon, illumination and an event list.

---

# 🛡 Error Handling

NoctiCycle:

- Looks up the city and lets you pick when the name is ambiguous
- Validates the timezone and output path
- Falls back gracefully when geocoding is unavailable and `--tz` is given
- Fails with clear messages instead of tracebacks

---

# 📄 Output

The script generates:

```
lunar_calendar_<city>_<YEAR>.html
```

in the project folder, unless you choose another path with `-o`.

Open it in any browser.  
Share it. Print it. Use it in journals or planners.

---

# 🧪 Example Workflow

1. You run:
    
    ```
    python3 nocticycle.py --city "Halifax" --tz "America/Halifax" --year 2025 --illumination-trend
    ```
    
2. NoctiCycle computes all lunar data for 2025.
    
3. It generates `lunar_calendar_Halifax_2025.html`.
    
4. You open it and see:
    
    - Moon icons
    - Illumination
    - Phase bands
    - New/full moon times
    - Trend sparklines
5. You print it or embed it in your digital planner.

---

# ❓ FAQ

## Why can I still pass --tz if it is detected automatically?

Because a city name alone is not enough to determine the correct local time.
Geocoding gives us latitude and longitude for astronomical calculations, but it does not provide timezone information. Timezones follow political boundaries, not geography, and cities with the same name can exist in different timezones.

NoctiCycle needs the exact IANA timezone (including DST rules) to convert UTC lunar events into accurate local times.
NoctiCycle looks the timezone up from the geocoded coordinates, so `--tz` is optional. Passing it explicitly overrides the detection (useful offline or for unusual cases) and ensures that rise/set times, phase events, and illumination values are computed correctly for your location.

## Why do some days show “--” for moonrise or moonset?

**Short answer**: 
Because on some calendar days, the Moon simply does not cross the horizon.

**Long answer**: 
The Moon rises about 50 minutes later each day, and its orbit is tilted relative to Earth. Because of this, several natural situations occur:

    The Moon may rise late at night and the next rise happens after midnight the following day, so one calendar day contains no rise.

    The Moon can stay above the horizon for more than 24 hours, producing a day with no rise or set.

    The Moon can stay below the horizon for more than 24 hours, producing the same effect.

This is normal lunar motion, especially at mid‑northern latitudes.
When no rise or set occurs between 00:00 and 23:59 local time, the calendar displays `--` or a mix of times and `--`:

```↑ --   ↓ --```

This does not mean the Moon is hidden by daylight — it means it never crossed the horizon during that date.

---

# 📜 License (MIT)

```
MIT License

Copyright (c) 2026 Valerio Fuoglio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
