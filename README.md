[![Python](https://img.shields.io/badge/python-v3-brightgreen.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# nbsc: Python interface to National Bureau of Statistics of China (NBSC) API

## What changed in 0.2.0

The NBS retired the `easyquery.htm` API endpoint (returns 403 since May 2026). Version 0.2.0 replaces the transport layer with the new UUID-based API under `data.stats.gov.cn/dg/website/publicrelease/web/external/`.

**Breaking changes:**
- The internal transport (`request_data.py`) is fully rewritten. `load_nbs_web()` signature is preserved but now uses a UUID-based lookup via `codes.json`.
- Only **CPI inflation series** are ported. All other modules (`gdp`, `household`, `auto_retail`, `investment`, `land`) raise `NotImplementedError` until their UUIDs are discovered and mapped.
- Requires Python >= 3.10 (was >= 3.8).

**New internals:**
- `codes.json` — maps legacy `A0xxxxx` codes to new UUID-based catalog/indicator identifiers. Each code may span multiple NBS "period leaves" (e.g., 2021-2025 and 2026- are separate catalogs).
- `fetch_series(cid, indicator_id, dts)` — low-level POST to the NBS data endpoint.
- `_dts_from_legacy(periods, freq)` — translates old period formats (`'2016-2020'`, `'LATEST10'`) to the new `YYYYMMTT` range format.

## Ported series (CPI inflation)

### Monthly CPI — same month last year = 100 (YoY)
| Legacy code | Period | UUID leaves |
|---|---|---|
| A01010G01 | 2021+ | 2026- + 2021-2025 |
| A01010101 | 2016-2020 | 2016-2020 |
| A01010201 | 1987-2015 | -2015 |

### Monthly CPI — preceding month = 100 (MoM)
| Legacy code | Period | UUID leaves |
|---|---|---|
| A01030G01 | 2021+ | 2026- + 2021-2025 |
| A01030101 | 2016-2020 | 2016-2020 |
| A01030201 | 2001-2015 | -2015 |

## Awaiting port (raise NotImplementedError)

All other series from 0.1.x are stubbed. To port a new series:
1. Run `scripts/discover_uuids.py` through the proxy to find the catalog/indicator UUIDs
2. Add entries to `nbsc/codes.json`
3. Update the module function to use the new transport

## Legacy 0.1.x codes

<details>
<summary>Click to expand full code list from 0.1.x</summary>

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
See the 0.1.x README for the full list of real estate investment, household, auto retail, and land series codes.

</details>
