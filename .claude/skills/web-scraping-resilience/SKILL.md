---
name: web-scraping-resilience
description: Use when making HTTP requests to government data portals or WAF-protected APIs that return 403, JS challenges, or empty responses. Covers required headers, cookie jar seeding, retry with backoff, and User-Agent management.
---

# Web Scraping Resilience

Patterns for reliable data fetching from WAF-protected government portals (NBS, FRED, Eurostat, etc.).

## When to Use

- HTTP 403 with WAF event IDs (`reason:UrlACL`, `reason:JsChallenge`)
- Response is `text/html` with obfuscated JS instead of expected JSON
- Intermittent empty responses or connection resets
- Need to add resilience to `requests`/`httpx` calls against protected APIs

## Required Headers

Government WAFs (Cloudflare, CWAP, etc.) inspect these headers. Missing any one can trigger a block.

```python
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://data.stats.gov.cn/dg/website/page.html",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}
```

**Key rules:**
- `Referer` must match the SPA origin, not your script URL
- `User-Agent` must look like a real browser — bare `python-requests/2.x` is blocked by most WAFs
- `Accept` should include `application/json` for JSON endpoints

## Retry with Exponential Backoff

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_resilient_session(
    retries: int = 3,
    backoff_factor: float = 1.0,
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
```

## WAF JS Challenge Handling

Some GET endpoints return a JS challenge (obfuscated script that sets a cookie) instead of data. Signs:

- Response `Content-Type` is `text/html` when you expect `application/json`
- Response body contains `<script>` with encoded/obfuscated JS
- Response sets a cookie like `__jsl_clearance_s` or `acw_sc__v2`

**Options (in order of preference):**

1. **Use POST endpoints** — many WAFs only challenge GETs. NBS `getEsDataByCidAndDt` (POST) works without cookies while `queryIndexTreeAsync` (GET) triggers the challenge.
2. **Seed cookie jar via Playwright** — do one headless page load to get the challenge cookie, then reuse it with `requests`:
   ```python
   cookies = {c["name"]: c["value"] for c in await page.context.cookies()}
   session.cookies.update(cookies)
   ```
3. **Hardcode known IDs** — if the GET is only needed for discovery (not runtime), cache results in `codes.json` and skip the GET entirely at runtime.

## Response Validation

```python
def validate_nbs_response(resp: requests.Response) -> dict:
    if resp.headers.get("Content-Type", "").startswith("text/html"):
        raise ValueError("WAF JS challenge received instead of JSON")
    data = resp.json()
    if data.get("state") != 20000:
        raise ValueError(f"NBS API error: state={data.get('state')}, message={data.get('message')}")
    if not data.get("data"):
        raise ValueError("NBS API returned empty data array")
    return data
```

## Proxy Fallback

If direct requests fail, route through the project proxy:

```python
PROXIES = {
    "http": "http://user:pass@cheap-one.space:3128",
    "https": "http://user:pass@cheap-one.space:3128",
}
session.proxies.update(PROXIES)
```

Load credentials from `~/.config/use-proxy/proxy.env`, never hardcode.

## Common Mistakes

- **Retrying on 403 without changing headers** — 403 from WAF won't resolve with retries alone; fix headers first.
- **Using `requests` default User-Agent** — `python-requests/2.32.3` is in every WAF blocklist. Always override.
- **Ignoring Content-Type in response** — a 200 with `text/html` is a JS challenge, not success.
- **Rotating User-Agent on every request** — unnecessary for government portals. One consistent browser UA is fine. Rotation is for anti-bot systems that fingerprint request patterns.
