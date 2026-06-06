"""National Bureau of Statistics of China — new UUID-based API (v0.2.0).

Replaces the dead easyquery.htm endpoint with the 3-step public-data API
under /dg/website/publicrelease/web/external/.

2026-06: NBS renamed the data endpoint from getEsDataByCidAndDt to
stream/esData (catalog UUIDs were unaffected). The tree/indicator GET
endpoints live under external/new/ (see scripts/discover_uuids.py).
"""

import json
import re
import warnings
from importlib import resources
from typing import Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_API_BASE = "https://data.stats.gov.cn/dg/website/publicrelease/web/external"
_POST_URL = f"{_API_BASE}/stream/esData"  # until 2026-06: getEsDataByCidAndDt

_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://data.stats.gov.cn/dg/website/page.html",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

_DEFAULT_TIMEOUT = 15
_ROOT_MONTHLY = "fc982599aa684be7969d7b90b1bd0e84"
_ROOT_QUARTERLY = "a94b8b7365a94874968cabbe392cf679"

_codes: Optional[dict] = None


def _load_codes() -> dict:
    global _codes
    if _codes is not None:
        return _codes
    codes_file = resources.files("nbsc").joinpath("codes.json")
    raw = json.loads(codes_file.read_text(encoding="utf-8"))
    raw.pop("_meta", None)
    _codes = raw
    return _codes


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(_HEADERS)
    retry = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _dts_from_legacy(periods: str, freq: str) -> str:
    """Translate legacy period format to the new ``YYYYMMTT-YYYYMMTT`` range string.

    Supported legacy formats:
      - ``'2026'``       → ``'202601MM-202612MM'``  (monthly) or ``'2026A-2026A'``  (annual)
      - ``'2016-2020'``  → ``'201601MM-202012MM'``
      - ``'LATEST10'`` / ``'LAST5'`` → computed range ending at current month
      - ``'2003,2012'``  → widest range ``200301MM-201212MM`` + warning
    """
    match freq:
        case "month":
            suffix = "MM"
        case "quarter":
            suffix = "SS"
        case _:
            suffix = "A"
    periods = periods.strip()

    # LATEST<N> / LAST<N>
    m = re.match(r"(?:LATEST|LAST)(\d+)", periods, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        now = pd.Timestamp.now()
        if freq == "month":
            end = now
            start = end - pd.DateOffset(months=n - 1)
            return f"{start.strftime('%Y%m')}{suffix}-{end.strftime('%Y%m')}{suffix}"
        elif freq == "quarter":
            end_year = now.year
            start_year = end_year - (n - 1) // 4
            return f"{start_year}01{suffix}-{end_year}04{suffix}"
        else:
            end_year = now.year
            start_year = end_year - n + 1
            return f"{start_year}{suffix}-{end_year}{suffix}"

    # Comma-separated list: '2003,2012' → widest range
    if "," in periods:
        years = [int(y.strip()) for y in periods.split(",")]
        warnings.warn(
            f"Comma-separated periods '{periods}' converted to range "
            f"{min(years)}-{max(years)}. Some intermediate periods may be included.",
            stacklevel=3,
        )
        start_year, end_year = min(years), max(years)
        if freq == "month":
            return f"{start_year}01{suffix}-{end_year}12{suffix}"
        elif freq == "quarter":
            return f"{start_year}01{suffix}-{end_year}04{suffix}"
        return f"{start_year}{suffix}-{end_year}{suffix}"

    # Range: '2016-2020'
    m = re.match(r"(\d{4})\s*-\s*(\d{4})", periods)
    if m:
        start_year, end_year = m.group(1), m.group(2)
        if freq == "month":
            return f"{start_year}01{suffix}-{end_year}12{suffix}"
        elif freq == "quarter":
            return f"{start_year}01{suffix}-{end_year}04{suffix}"
        return f"{start_year}{suffix}-{end_year}{suffix}"

    # Single year: '2026'
    m = re.match(r"(\d{4})$", periods)
    if m:
        year = m.group(1)
        if freq == "month":
            return f"{year}01{suffix}-{year}12{suffix}"
        elif freq == "quarter":
            return f"{year}01{suffix}-{year}04{suffix}"
        return f"{year}{suffix}-{year}{suffix}"

    raise ValueError(f"Unsupported period format: '{periods}'")


def _parse_year_range(periods: str) -> tuple[int, int]:
    """Extract the year range from a legacy period string."""
    periods = periods.strip()

    m = re.match(r"(?:LATEST|LAST)(\d+)", periods, re.IGNORECASE)
    if m:
        now = pd.Timestamp.now()
        n = int(m.group(1))
        return now.year - n + 1, now.year

    if "," in periods:
        years = [int(y.strip()) for y in periods.split(",")]
        return min(years), max(years)

    m = re.match(r"(\d{4})\s*-\s*(\d{4})", periods)
    if m:
        return int(m.group(1)), int(m.group(2))

    m = re.match(r"(\d{4})$", periods)
    if m:
        y = int(m.group(1))
        return y, y

    raise ValueError(f"Cannot parse year range from: '{periods}'")


def _root_for_freq(freq: str) -> str:
    if freq == "quarter":
        return _ROOT_QUARTERLY
    return _ROOT_MONTHLY


def fetch_series(
    cid: str,
    indicator_id: str,
    dts: str,
    *,
    root_id: str | None = None,
    freq: str = "month",
) -> pd.Series:
    """Fetch a single series from the NBS public-data API.

    Parameters
    ----------
    cid : str
        Leaf catalog UUID.
    indicator_id : str
        Indicator UUID within the catalog.
    dts : str
        Period range in new format, e.g. ``'202101MM-202612MM'``.
    root_id : str | None
        Root catalog UUID. Auto-selected from *freq* when ``None``.
    freq : str
        ``'month'``, ``'quarter'``, or ``'year'``.
    """
    if root_id is None:
        root_id = _root_for_freq(freq)

    body = {
        "cid": cid,
        "indicatorIds": [indicator_id],
        "daCatalogId": "",
        "das": [{"text": "全国", "value": "000000000000"}],
        "showType": "1",
        "dts": [dts],
        "rootId": root_id,
    }

    session = _make_session()
    resp = session.post(_POST_URL, json=body, timeout=_DEFAULT_TIMEOUT)
    resp.raise_for_status()

    if resp.headers.get("Content-Type", "").startswith("text/html"):
        raise RuntimeError("WAF JS challenge received instead of JSON — check headers")

    payload = resp.json()
    state = payload.get("state")
    if state != 20000:
        raise RuntimeError(
            f"NBS API error: state={state}, message={payload.get('message')}"
        )

    data = payload.get("data", [])
    if not data:
        return pd.Series(dtype="float64")

    records: dict[pd.Timestamp, float] = {}
    for period_block in data:
        code = period_block.get("code", "")
        date_str = re.sub(r"[A-Za-z]+$", "", code)
        if not date_str:
            continue
        dt = _parse_period_code(date_str, freq)
        if dt is None:
            continue
        for val_entry in period_block.get("values", []):
            raw = val_entry.get("value")
            if raw is not None and raw != "":
                records[dt] = float(raw)

    s = pd.Series(records, dtype="float64")
    s = s.sort_index()
    return s


def _parse_period_code(date_str: str, freq: str) -> pd.Timestamp | None:
    if freq == "quarter":
        # '202601' → Q1 2026: quarter number 01-04
        if len(date_str) >= 6:
            year = int(date_str[:4])
            q = int(date_str[4:6])
            if 1 <= q <= 4:
                month = q * 3
                return pd.Timestamp(year=year, month=month, day=1)
        return None
    date_fmt = "%Y%m" if freq == "month" else "%Y"
    return pd.to_datetime(date_str, format=date_fmt)


def load_nbs_web(series: str, periods: str, freq: str) -> pd.Series:
    """Fetch & parse from the China NBS web data API.

    Signature-compatible with v0.1.x. Looks up ``series`` in ``codes.json``
    to find the new UUID-based catalog/indicator mapping, translates the legacy
    ``periods`` format, and calls :func:`fetch_series`.

    Parameters
    ----------
    series : str
        Legacy series code, e.g. ``'A01010G01'``.
    periods : str
        Period specification: ``'2020-2022'``, ``'LATEST10'``, ``'2026'``, etc.
    freq : str
        ``'month'``, ``'quarter'``, or ``'year'``.
    """
    codes = _load_codes()
    if series not in codes:
        raise KeyError(
            f"Series '{series}' not found in codes.json. "
            f"Available: {sorted(codes.keys())}"
        )

    entry = codes[series]
    leaves = entry["leaves"]
    req_start, req_end = _parse_year_range(periods)

    parts: list[pd.Series] = []
    for leaf in leaves:
        leaf_start = leaf.get("year_start") or 1900
        leaf_end = leaf.get("year_end") or 9999

        if req_start > leaf_end or req_end < leaf_start:
            continue

        cid = leaf.get("cid")
        indicator_id = leaf.get("indicator_id")
        if not cid or not indicator_id:
            raise RuntimeError(
                f"UUID not yet discovered for series '{series}' "
                f"leaf {leaf_start}-{leaf_end}. Run Stage 2 (Playwright discovery)."
            )

        eff_start = max(req_start, leaf_start)
        eff_end = min(req_end, leaf_end) if leaf_end != 9999 else req_end
        leaf_periods = f"{eff_start}-{eff_end}"
        dts = _dts_from_legacy(leaf_periods, freq)

        s = fetch_series(
            cid=cid,
            indicator_id=indicator_id,
            dts=dts,
            freq=freq,
        )
        parts.append(s)

    if not parts:
        return pd.Series(dtype="float64")

    result = pd.concat(parts)
    result = result[~result.index.duplicated(keep="first")]
    return result.sort_index()
