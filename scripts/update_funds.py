#!/usr/bin/env python3
"""Refresh public/funds.json by scraping Nordnet fund list SSR pages (no API key)."""
from __future__ import annotations

import json
import math
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "funds.json"
META = ROOT / "public" / "data-meta.json"
BASE_URL = "https://www.nordnet.no/fond/liste"
PAGE_SIZE = 100
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "nb-NO,nb;q=0.9,en;q=0.8",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "ignore")


def extract_fundlist_payload(html: str) -> dict:
    marker = '\\"results\\":[{\\"instrument_info\\"'
    pos = html.find(marker)
    if pos < 0:
        raise RuntimeError("Could not find fund results in Nordnet HTML")

    start = html.rfind('{\\"rows\\":', 0, pos)
    if start < 0:
        raise RuntimeError("Could not find fundlist rows object")

    depth = 0
    in_str = False
    i = start
    while i < len(html):
        if in_str:
            if html.startswith('\\"', i):
                in_str = False
                i += 2
                continue
            if html.startswith("\\\\", i):
                i += 2
                continue
            i += 1
            continue

        if html.startswith('\\"', i):
            in_str = True
            i += 2
            continue
        ch = html[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                raw = html[start : i + 1]
                unescaped = (
                    raw.replace("\\\\", "\u0000")
                    .replace('\\"', '"')
                    .replace("\u0000", "\\")
                )
                return json.loads(unescaped)
        i += 1

    raise RuntimeError("Unbalanced fundlist payload")


def normalize_fund(item: dict) -> dict:
    info = item.get("instrument_info") or {}
    nnx = item.get("nnx_info") or {}
    market = item.get("market_info") or {}
    return {
        "instrument_info": {
            "name": info.get("name") or info.get("display_name") or "",
            "instrument_icon_url": info.get("instrument_icon_url") or "",
            "instrument_id": info.get("instrument_id"),
            "isin": info.get("isin") or "",
            "market_data_order_book_id": nnx.get("market_data_order_book_id") or "",
            "display_slug": nnx.get("display_slug") or "",
            "market_identifier": market.get("identifier") or "",
        },
        "price_info": item.get("price_info") or {},
        "historical_returns_info": item.get("historical_returns_info") or {},
        "fund_info": item.get("fund_info") or {},
        "annual_growth_info": item.get("annual_growth_info") or {},
        "statistical_info": item.get("statistical_info") or {},
    }


def page_url(page: int) -> str:
    if page <= 1:
        return BASE_URL
    return f"{BASE_URL}?page={page}"


def write_meta(funds_count: int) -> None:
    meta = {}
    if META.exists():
        try:
            meta = json.loads(META.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}
    meta.update(
        {
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "fundsCount": funds_count,
            "fundsSource": "nordnet.no/fond/liste (SSR scrape)",
        }
    )
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    first = extract_fundlist_payload(fetch(page_url(1)))
    total_hits = int(first.get("total_hits") or 0)
    pages = max(1, math.ceil(total_hits / PAGE_SIZE))
    print(f"Nordnet reports {total_hits} funds across ~{pages} pages")

    by_name: dict[str, dict] = {}
    for page in range(1, pages + 1):
        html = fetch(page_url(page)) if page > 1 else None
        data = first if page == 1 else extract_fundlist_payload(html)
        results = data.get("results") or []
        for item in results:
            normalized = normalize_fund(item)
            name = normalized["instrument_info"]["name"]
            if name:
                by_name[name] = normalized
        print(f"  page {page}/{pages}: +{len(results)} (unique {len(by_name)})")
        if page < pages:
            time.sleep(0.35)

    funds = list(by_name.values())
    if len(funds) < 100:
        raise SystemExit(f"Too few funds scraped ({len(funds)}); aborting write")

    OUT.write_text(json.dumps(funds, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    write_meta(len(funds))
    print(f"Wrote {len(funds)} funds -> {OUT}")


if __name__ == "__main__":
    main()
