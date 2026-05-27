[![Python](https://img.shields.io/badge/python-v3.10+-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# nbsc: Python interface to National Bureau of Statistics of China (NBSC) API

Fetch macroeconomic time series (CPI, GDP, etc.) from China's NBS public data portal.

## Installation

```bash
pip install git+https://github.com/mbk-dev/nbsc.git
```

## Quick start

```python
import nbsc

# Monthly CPI year-on-year (same month last year = 100)
cpi_yoy = nbsc.get_annual_inflation("2021")

# Monthly CPI month-on-month (preceding month = 100)
cpi_mom = nbsc.get_recent_inflation("2025")

# Long-term monthly CPI from 2001
cpi_long = nbsc.get_inflation_from_2001()
```

## What changed in 1.0.0

NBS retired the `easyquery.htm` API (returns 403 since May 2026). Version 1.0.0 replaces the transport layer with the new UUID-based API under `data.stats.gov.cn/dg/website/publicrelease/web/external/`.

**Breaking changes:**
- Transport fully rewritten. `load_nbs_web()` signature preserved but uses UUID-based lookup via `codes.json`.
- Only **CPI inflation** series ported. Other modules (`gdp`, `household`, `auto_retail`, `investment`, `land`) raise `NotImplementedError`.
- Requires Python >= 3.10.

**Architecture:**
- `codes.json` maps legacy `A0xxx` codes to UUID catalog/indicator pairs. Codes may span multiple NBS "period leaves" (e.g., 2021-2025 and 2026- are separate catalogs) — stitched automatically.
- `fetch_series(cid, indicator_id, dts)` — low-level POST to the NBS data endpoint.
- `_dts_from_legacy(periods, freq)` — translates old period formats (`'2016-2020'`, `'LATEST10'`) to `YYYYMMTT` range strings.
- `scripts/discover_uuids.py` — Playwright-based tool for re-discovering UUIDs after NBS reshuffles.

**Verified against official NBS press releases** (May 2026): all values match exactly.

## Available series

### CPI — same month last year = 100 (YoY)

| Code | Period | Description |
|---|---|---|
| A01010G01 | 2021+ | Headline CPI YoY |
| A01010101 | 2016-2020 | CPI YoY |
| A01010201 | 1987-2015 | CPI YoY |

### CPI — preceding month = 100 (MoM)

| Code | Period | Description |
|---|---|---|
| A01030G01 | 2021+ | Headline CPI MoM |
| A01030101 | 2016-2020 | CPI MoM |
| A01030201 | 2001-2015 | CPI MoM |

### Inflation functions

| Function | Returns |
|---|---|
| `get_annual_inflation(first_year)` | Monthly YoY CPI as decimal (e.g., 0.012 = +1.2%) |
| `get_recent_inflation(first_year)` | Monthly MoM CPI as decimal |
| `get_inflation_from_2001()` | MoM CPI 2001-2020 |
| `calculate_monthly_from_annual()` | Monthly CPI derived from annual, 1987+ |

## Porting new series

To add GDP, real estate, or other series:

1. Run `scripts/discover_uuids.py` through a proxy to find catalog/indicator UUIDs
2. Add entries to `nbsc/codes.json`
3. Replace `NotImplementedError` in the module with a `load_nbs_web()` call

## Legacy 0.1.x

<details>
<summary>Full code list from 0.1.x (all codes below are dead)</summary>

### Consumer Price Index (CPI)
**Annual CPI** (dbcode="hgnd")
- A090201 - Consumer Price Index (1978=100)
- A090302 - Consumer Price Index (1978=100)

**Monthly CPI** (dbcode="hgyd")
Last Year = 100:
- A01010G01 - Consumer Price Index (The same month last year=100) 2021-
- A01010101 - Consumer Price Index (The same month last year=100) 2016-2020
- A01010201 - Consumer Price Index (The same month last year=100) 1987-2015

The same period last year=100:
- A01020101 - Consumer Price Index (The same period last year=100) 2016-
- A01020201 - Consumer Price Index (The same period last year=100) 1995-2015

Preceding month=100:
- A01030G01 - Consumer Price Index (preceding month=100) 2021-
- A01030101 - Consumer Price Index (preceding month=100) 2016-2020
- A01030201 - Consumer Price Index (preceding month=100) 2001-2015

### GDP (annual)
- A020102 - Gross Domestic Product (GDP)
- A020106 - Per Capita GDP
- A020101 - Gross National Income

### Other series
See the [0.1.x release](https://github.com/mbk-dev/nbsc/tree/ec0c40d) for the full list of real estate investment, household, auto retail, and land series codes.

</details>
