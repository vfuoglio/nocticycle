# nocticycle

NoctiCycle is a Python library for exploring the rhythm of the Moon. It computes precise lunar phases, illumination, and event timings, renders elegant SVG moon icons, and generates a full year of location‑specific lunar calendars with accurate astronomical data.

NoctiCycle computes:

- Daily moon phase and illumination
- Exact times of new and full moons (localized to your timezone)
- Waxing/waning classification
- Optional per‑day **illumination trend sparklines**
- Optional rising and setting time
- SVG moon icons rendered directly from astronomical data
- A print‑friendly layout or a rich, cosmetic layout

It’s a zero‑dependency, astronomy‑accurate moon calendar you can generate and view anywhere.

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
- The print mode produces a clean, ink‑friendly version

It’s perfect for planners, journals, almanacs, or anyone who loves tracking the Moon.

---

# 🚀 Features

### ✔ Accurate lunar phase calculations

Uses Skyfield + DE421 ephemeris for precise astronomical results.

### ✔ Localized event times

New/full moon timestamps are converted to your chosen timezone.

### ✔ SVG moon rendering

Each day shows a crisp, resolution‑independent moon icon.

### ✔ Optional illumination percentage

Display the Moon’s brightness for each day.

### ✔ Showing rising and setting times 

Show rise and set times.

### ✔ Optional event times

Show the exact moment of new/full moon on the corresponding day.

### ✔ Optional illumination trend sparkline

A ±3‑day mini‑graph showing illumination change.  
Enabled via:

```
--illumination-trend
```

### ✔ Two display modes

- **Cosmetic mode** (default): modern, elegant, visually rich
- **Print mode** (`--print-format`): minimal, grayscale‑friendly

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
- Daily illumination
- Phase classification
- Optional trend data

## 3. It renders a complete HTML calendar

- One year
- Twelve months
- Clean layout
- SVG graphics
- Optional sparklines

## 4. You open the file in any browser

`lunar_calendar_2025.html`

---

# ⚙️ Configuration

At the top of the script, you’ll find:

```python
YEAR = 2025
CITY = None          # must be provided via CLI
TZ = None            # must be provided via CLI

SHOW_LUMINANCE = True
SHOW_EVENT_TIME = True
USE_EXACT_EVENT_ILLUMINATION = True

COSMETICS_MODE = True
ILLUMINATION_TREND = False
```

### Required CLI parameters

```
--city "Your City"
```

### Optional parameters

```
--tz "Your/Timezone"       (default: detected from the city)
--year 2027                (default: current year)
-o, --output
--illumination-trend
--show-event-time
--show-luminance
--show-rise-set-times
--show-quarters
--ics [PATH]
--print-format
--paper letter|a4|legal|tabloid   (print format, default: letter)
--print-style grey|hatched|solid (print format, default: grey)
--print-layout rows|columns      (print format, default: rows)
```

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

- Cosmetic mode includes colors, SVGs, sparklines, and layout enhancements.
- Print mode strips everything down for clean physical printing.

---

# 🛡 Error Handling

NoctiCycle:

- Validates timezone names
- Ensures `--city` and `--tz` are provided
- Handles missing ephemeris files
- Warns about invalid years
- Fails gracefully with clear messages

---

# 📄 Output

The script generates:

```
lunar_calendar_<YEAR>.html
```

Open it in any browser.  
Share it. Print it. Use it in journals or planners.

---

# 🧪 Example Workflow

1. You run:
    
    ```
    python3 nocticycle.py --city "Halifax" --tz "America/Halifax" --year 2025 --illumination-trend
    ```
    
2. NoctiCycle computes all lunar data for 2025.
    
3. It generates `lunar_calendar_2025.html`.
    
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
