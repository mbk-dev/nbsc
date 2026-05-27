# nbsc — NBS China public data client

Python client for the National Bureau of Statistics of China (data.stats.gov.cn).

## Build & test

```bash
# Install
pip install -e .
# or with poetry
poetry install

# Unit tests (no network)
pytest tests/test_period_translator.py

# Integration tests (requires network access to NBS)
NBSC_INTEGRATION=1 pytest tests/ -v
```

NBS blocks TLS from some IPs. If tests fail with SSL timeout, route through proxy:
```bash
source ~/.config/use-proxy/proxy.env && export HTTPS_PROXY="$PROXY_URL"
NBSC_INTEGRATION=1 pytest tests/ -v
```

## Architecture

- `nbsc/codes.json` — UUID map: series code -> catalog/indicator UUIDs. Supports monthly (`MM`), quarterly (`SS`), and annual (`A`) frequencies.
- `nbsc/request_data.py` — transport layer: `fetch_series()` POSTs to the NBS data endpoint, `load_nbs_web()` is the high-level entry point.
- `scripts/discover_uuids.py` — Playwright-based UUID discovery tool (requires proxy + browser).

## Adding new series

1. Discover leaf CID and indicator UUID via Playwright (`scripts/discover_uuids.py` or manual SPA inspection)
2. Add entry to `nbsc/codes.json` with `freq`, `cid`, `indicator_id`, `year_start`/`year_end`
3. Create or update the module (e.g., `nbsc/gdp.py`)
4. Write integration test gated by `NBSC_INTEGRATION=1`
5. Export from `nbsc/__init__.py`

## Quarterly data

Quarterly series use `freq="quarter"`, `SS` date suffix (e.g., `202401SS`), and the quarterly root UUID (`a94b8b7365a94874968cabbe392cf679`). The transport layer auto-selects the root from `freq`.

## Conventions

- Commit messages in English, `feat:` / `fix:` / `docs:` prefixes.
- Tests are integration tests hitting the live NBS API — mark with `NBSC_INTEGRATION=1`.
