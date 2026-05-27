[![Python](https://img.shields.io/badge/python-v3.10+-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# nbsc: Python interface to National Bureau of Statistics of China (NBSC) API

Fetch macroeconomic time series (CPI, GDP, PMI, M2, PPI, unemployment) from China's NBS public data portal.

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

# Quarterly GDP at current prices (100M CNY)
gdp = nbsc.get_gdp_nominal("2020")

# Manufacturing PMI (%)
pmi = nbsc.get_manufacturing_pmi("2020")

# Money supply M2, end-of-period (100M CNY)
m2 = nbsc.get_m2("2020")

# Urban survey unemployment rate (%)
unemp = nbsc.get_unemployment_rate()

# Producer price index, year-on-year (same month last year = 100)
ppi = nbsc.get_ppi_yoy("2020")
```

## Available series

### CPI (Inflation)

| Function | Returns | Frequency |
|---|---|---|
| `get_annual_inflation(first_year)` | YoY CPI as decimal (0.012 = +1.2%) | Monthly |
| `get_recent_inflation(first_year)` | MoM CPI as decimal | Monthly |
| `get_inflation_from_2001()` | MoM CPI 2001-2020 | Monthly |
| `calculate_monthly_from_annual()` | Monthly CPI derived from annual, 1987+ | Monthly |

### GDP (Quarterly)

| Function | Returns | Available from |
|---|---|---|
| `get_gdp_nominal(first_year)` | GDP at current prices, quarterly (100M CNY) | 1992 |
| `get_gdp_nominal_cumulative(first_year)` | GDP at current prices, cumulative (100M CNY) | 1992 |
| `get_gdp_real(first_year)` | GDP at constant prices, quarterly (100M CNY) | 2011 |
| `get_gdp_real_cumulative(first_year)` | GDP at constant prices, cumulative (100M CNY) | 2011 |
| `get_gdp_index(first_year)` | GDP index (same period last year = 100) | 1992 |
| `get_gdp_index_cumulative(first_year)` | GDP index, cumulative | 1992 |
| `get_gdp_qoq_growth(first_year)` | GDP quarter-on-quarter growth (%) | 2011 |

### PMI

| Function | Returns | Available from |
|---|---|---|
| `get_manufacturing_pmi(first_year)` | Manufacturing PMI (%) | 2005 |
| `get_non_manufacturing_pmi(first_year)` | Non-manufacturing business activity index (%) | 2007 |
| `get_composite_pmi(first_year)` | Composite PMI output index (%) | 2017 |

### Money Supply

| Function | Returns | Available from |
|---|---|---|
| `get_m2(first_year)` | M2 end-of-period (100M CNY) | 1999 |
| `get_m2_yoy(first_year)` | M2 year-on-year growth (%) | 1999 |
| `get_m1(first_year)` | M1 end-of-period (100M CNY) | 1999 |
| `get_m1_yoy(first_year)` | M1 year-on-year growth (%) | 1999 |
| `get_m0(first_year)` | M0 end-of-period (100M CNY) | 1999 |
| `get_m0_yoy(first_year)` | M0 year-on-year growth (%) | 1999 |

### Unemployment

| Function | Returns | Available from |
|---|---|---|
| `get_unemployment_rate(first_year)` | National urban survey unemployment rate (%) | 2018 |

### PPI (Producer Price Index)

| Function | Returns | Available from |
|---|---|---|
| `get_ppi_yoy(first_year)` | Ex-factory PPI (same month last year = 100) | 1996 |
| `get_ppi_mom(first_year)` | Ex-factory PPI (preceding month = 100) | 2011 |

## What changed in 1.0.0

NBS retired the `easyquery.htm` API (returns 403 since May 2026). Version 1.0.0 replaces the transport layer with the new UUID-based API under `data.stats.gov.cn/dg/website/publicrelease/web/external/`.

**Architecture:**
- `codes.json` maps series codes to UUID catalog/indicator pairs. Codes may span multiple NBS "period leaves" (e.g., 2021-2025 and 2026- are separate catalogs) — stitched automatically.
- `fetch_series(cid, indicator_id, dts)` — low-level POST to the NBS data endpoint.
- `_dts_from_legacy(periods, freq)` — translates period formats (`'2016-2020'`, `'LATEST10'`) to `YYYYMMTT` range strings.
- Supports monthly (`MM`), quarterly (`SS`), and annual (`A`) frequencies.
- `scripts/discover_uuids.py` — Playwright-based tool for re-discovering UUIDs after NBS reshuffles.

## Porting new series

To add new NBS series:

1. Run `scripts/discover_uuids.py` through a proxy to find catalog/indicator UUIDs
2. Add entries to `nbsc/codes.json`
3. Create or update the module with a `load_nbs_web()` call
4. Write integration tests (`NBSC_INTEGRATION=1`)

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
