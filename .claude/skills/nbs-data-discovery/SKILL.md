---
name: nbs-data-discovery
description: Use when NBS (data.stats.gov.cn) reshuffles its API and existing UUIDs in codes.json stop working — re-discovers catalog UUIDs via Playwright through proxy, captures XHR from the SPA, and updates the UUID map.
---

# NBS Data Discovery

Re-discover UUIDs for the NBS public-data API after a reshuffle. The NBS periodically reorganizes its Vue SPA at `data.stats.gov.cn/dg/website/page.html`, invalidating cached UUIDs in `codes.json`.

## When to Use

- `POST getEsDataByCidAndDt` returns empty `data`, `state != 20000`, or HTTP error
- NBS announces a site redesign or data reorganization
- Adding a new series (GDP, PPI, retail, etc.) that isn't in `codes.json` yet

## Prerequisites

- Playwright installed (`pip install playwright && playwright install chromium`)
- Proxy credentials at `~/.config/use-proxy/proxy.env`
- `~/.claude/skills/use-proxy/scripts/with-proxy.sh` available

## Discovery Procedure

### 1. Launch Playwright through proxy

```python
import asyncio
from playwright.async_api import async_playwright

async def discover():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": "http://cheap-one.space:3128",
                   "username": "<from proxy.env>",
                   "password": "<from proxy.env>"}
        )
        page = await browser.new_page()
        # Collect XHR responses
        captured = []
        page.on("response", lambda r: captured.append(r)
                if "publicrelease/web/external" in r.url else None)
        await page.goto(
            "https://data.stats.gov.cn/dg/website/page.html#/pc/national/monthData",
            wait_until="networkidle"
        )
```

### 2. Navigate the catalog tree

Target routes by data type:

| Data | SPA route fragment |
|------|--------------------|
| China monthly | `#/pc/national/monthData` |
| China annual | `#/pc/national/yearData` |
| Foreign monthly | `#/pc/national/countryMonthData` |
| HK/Macau/TW annual | `#/pc/national/gatYearData` |

Expand the Element-UI tree on the left. Click the target indicator (e.g. 居民消费价格指数). Wait for XHR to settle.

### 3. Extract UUIDs from captured XHR

Look for three request types in `captured`:

1. **`queryIndexTreeAsync`** — returns tree nodes with `_id` (catalog UUID), `isLeaf`, `_name`
2. **`queryIndicatorsByCid`** — returns indicator list with `_id` (indicator UUID), `_name`, `du_name`
3. **`getEsDataByCidAndDt`** — POST body contains `cid`, `indicatorIds`, `rootId`, `dts`

Parse the POST body of `getEsDataByCidAndDt` to get the exact `cid` and `indicatorIds` the SPA used.

### 4. Verify with bare curl

```bash
curl -s -X POST \
  'https://data.stats.gov.cn/dg/website/publicrelease/web/external/getEsDataByCidAndDt' \
  -H 'Content-Type: application/json' \
  -H 'Referer: https://data.stats.gov.cn/dg/website/page.html' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36' \
  -d '{"cid":"<cid>","indicatorIds":["<indicator_id>"],"daCatalogId":"","das":[{"text":"全国","value":"000000000000"}],"showType":"1","dts":["202501MM-202612MM"],"rootId":"<root_id>"}'
```

Confirm `state: 20000` and `data[].values[].value` is non-empty.

### 5. Update codes.json

Add or update entry:
```json
{
  "LEGACY_CODE": {
    "cid": "<leaf catalog UUID>",
    "indicator_id": "<indicator UUID>",
    "sdate": "2026",
    "edate": null
  }
}
```

## Common Mistakes

- **Wrong SPA route:** `countryMonthData` is foreign countries, not China domestic. Use `monthData` for CPI.
- **Bare curl on GET endpoints:** `queryIndexTreeAsync` triggers a WAF JS challenge from curl. Only `getEsDataByCidAndDt` (POST) works without browser cookies.
- **Assuming same indicator UUID across period leaves:** NBS splits historical data into period-based catalog leaves (e.g. 2026-, 2021-2025, 2016-2020, -2015). Each leaf may have different indicator UUIDs — always verify via `queryIndicatorsByCid` per leaf.
- **Missing headers on POST:** `Content-Type: application/json` and `Referer: https://data.stats.gov.cn/dg/website/page.html` are required. Without `Referer` the WAF may block.

## Known catalog roots (as of 2026-05-17)

| `code` param | Meaning |
|---|---|
| `1` | 全国 (national) — monthData / yearData views |
| `10` | 港澳台年度 (HK/Macau/TW annual) |
| `12` | 三大经济体月度 (G3 monthly) |
| `13` | 国际市场月度商品价格 |
| `14` | 主要国家年度 |

Monthly root UUID: `fc982599aa684be7969d7b90b1bd0e84` (月度数据).
