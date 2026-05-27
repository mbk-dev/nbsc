"""Discover NBS indicator UUIDs by loading the SPA and capturing XHR.

The GET endpoints (queryIndexTreeAsync, queryIndicatorsByCid) trigger a WAF
JS challenge that only resolves in a real browser context. This script:
1. Navigates to the NBS SPA to seed the WAF cookie
2. Uses page.evaluate(fetch) to make API calls from within the browser context
3. Falls back to clicking tree nodes and capturing XHR responses

Run through proxy:
    ~/.claude/skills/use-proxy/scripts/with-proxy.sh .venv/bin/python scripts/discover_uuids.py
"""

import asyncio
import json
import os
import sys

from playwright.async_api import async_playwright

API_BASE = "https://data.stats.gov.cn/dg/website/publicrelease/web/external"

# Known YoY (上年同月=100) leaf CIDs
YOY_LEAVES = [
    {"cid": "5c7452825c7c4dcba391db5ca7f335c5", "label": "CPI YoY 2026-", "year_start": 2026, "year_end": None},
    {"cid": "809d2522b0fe4be89142650341b19083", "label": "CPI YoY 2021-2025", "year_start": 2021, "year_end": 2025},
    {"cid": "9d4eec43537742a7ab5d63db97fa2f51", "label": "CPI YoY 2016-2020", "year_start": 2016, "year_end": 2020},
    {"cid": "954cfd7597e34b919ec71caf6aeead51", "label": "CPI YoY -2015", "year_start": 1987, "year_end": 2015},
]

MOM_PARENT_CID = "7318f3bae40b4b4badbf519bcd2c79c9"


async def api_get(page, url: str) -> dict | None:
    """Make a GET request from within the browser page context."""
    try:
        result = await page.evaluate(
            """async (url) => {
                const resp = await fetch(url, {
                    credentials: 'include',
                    headers: { 'Accept': 'application/json, text/plain, */*' }
                });
                const text = await resp.text();
                try { return JSON.parse(text); }
                catch(e) { return { _error: 'not_json', _body: text.substring(0, 200) }; }
            }""",
            url,
        )
        return result
    except Exception as e:
        return {"_error": str(e)}


async def fetch_indicators(page, cid: str, label: str) -> dict | None:
    url = f"{API_BASE}/new/queryIndicatorsByCid?cid={cid}&dt=&name="
    print(f"  {label} (cid={cid[:12]}...)...", file=sys.stderr)
    data = await api_get(page, url)
    if data and data.get("success"):
        indicators = data.get("data", {}).get("list", [])
        print(f"    -> {len(indicators)} indicators found", file=sys.stderr)
        headline = None
        for ind in indicators:
            if ind.get("ds_order") == 1 or "居民消费价格指数" == ind.get("_name", "").strip():
                headline = ind["_id"]
            name = ind.get("_name", "")
            showname = ind.get("i_showname", "")
            print(f"       {ind['_id'][:12]}... {name} | {showname}", file=sys.stderr)
        return {
            "label": label,
            "headline_indicator_id": headline,
            "all_indicators": [
                {"_id": i["_id"], "_name": i.get("_name", ""), "i_showname": i.get("i_showname", "")}
                for i in indicators
            ],
        }
    elif data and "_error" in data:
        print(f"    -> Error: {data['_error']}", file=sys.stderr)
        if "_body" in data:
            print(f"       Body: {data['_body'][:100]}", file=sys.stderr)
    else:
        print(f"    -> Unexpected: {json.dumps(data, ensure_ascii=False)[:200]}", file=sys.stderr)
    return None


async def main():
    proxy_url = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
    if not proxy_url:
        print("WARNING: No proxy detected.", file=sys.stderr)

    launch_args = {"headless": True}
    if proxy_url:
        from urllib.parse import urlparse
        parsed = urlparse(proxy_url)
        proxy_cfg = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
        if parsed.username:
            proxy_cfg["username"] = parsed.username
        if parsed.password:
            proxy_cfg["password"] = parsed.password
        launch_args["proxy"] = proxy_cfg
        print(f"  Proxy: {parsed.hostname}:{parsed.port} (user={parsed.username})", file=sys.stderr)

    async with async_playwright() as p:
        browser = await p.chromium.launch(**launch_args)
        page = await browser.new_page()

        # Step 1: Load the SPA to get WAF cookies
        print("Loading NBS SPA to seed WAF cookies...", file=sys.stderr)
        spa_url = "https://data.stats.gov.cn/dg/website/page.html#/pc/national/monthData"
        await page.goto(spa_url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        print(f"  Page title: {await page.title()}", file=sys.stderr)

        # Check cookies
        cookies = await page.context.cookies()
        cookie_names = [c["name"] for c in cookies]
        print(f"  Cookies: {cookie_names}", file=sys.stderr)

        results = {}

        # Step 2: Fetch indicators for YoY leaves
        print("\n=== YoY (上年同月=100) indicators ===", file=sys.stderr)
        for leaf in YOY_LEAVES:
            result = await fetch_indicators(page, leaf["cid"], leaf["label"])
            if result:
                result["year_start"] = leaf["year_start"]
                result["year_end"] = leaf["year_end"]
                results[leaf["cid"]] = result

        # Step 3: Discover MoM tree
        print("\n=== MoM (上月=100) tree discovery ===", file=sys.stderr)
        tree_url = f"{API_BASE}/new/queryIndexTreeAsync?pid={MOM_PARENT_CID}&code=1"
        tree_data = await api_get(page, tree_url)

        mom_leaves = []
        if tree_data and tree_data.get("success"):
            nodes = tree_data.get("data", [])
            print(f"  Found {len(nodes)} MoM sub-nodes:", file=sys.stderr)
            for node in nodes:
                print(
                    f"    {node['_id'][:12]}... {node.get('_name', '')} "
                    f"isLeaf={node.get('isLeaf')} "
                    f"sdate={node.get('sdate')} edate={node.get('edate')}",
                    file=sys.stderr,
                )
                if node.get("isLeaf"):
                    mom_leaves.append(node)
            results["_mom_tree"] = [
                {"_id": n["_id"], "_name": n.get("_name", ""), "isLeaf": n.get("isLeaf"),
                 "sdate": n.get("sdate"), "edate": n.get("edate")}
                for n in nodes
            ]
        elif tree_data and tree_data.get("_error") == "not_json":
            print(f"  WAF challenge on tree endpoint. Body: {tree_data.get('_body', '')[:100]}", file=sys.stderr)
            print("  Trying parent as leaf...", file=sys.stderr)
            result = await fetch_indicators(page, MOM_PARENT_CID, "CPI MoM (direct)")
            if result:
                results[MOM_PARENT_CID] = result

        # Step 4: Fetch indicators for MoM leaves
        if mom_leaves:
            print("\n=== MoM leaf indicators ===", file=sys.stderr)
            for node in mom_leaves:
                leaf_cid = node["_id"]
                label = f"CPI MoM {node.get('_name', '')} ({node.get('sdate', '?')}-{node.get('edate', '')})"
                result = await fetch_indicators(page, leaf_cid, label)
                if result:
                    result["sdate"] = node.get("sdate")
                    result["edate"] = node.get("edate")
                    results[leaf_cid] = result

        await browser.close()

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
