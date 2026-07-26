#!/usr/bin/env python3
"""Refresh public/banks.json from Forbrukerrådet bankinnskudd JSON (no API key)."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "banks.json"
META = ROOT / "public" / "data-meta.json"
API = "https://finans-api.forbrukerradet.no/bankprodukt/bankinnskudd"
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def fetch_products() -> list[dict[str, Any]]:
    params = {
        "age": "40",
        "depositAmount": "150000",
        "format": "json",
        "isMonthlySavings": "false",
        "isSalaryRequired": "false",
        "membershipType": "None",
        "query": "",
        "requiredProductTypes": "None",
        "sortBy": "effectiveInterestRate",
        "sortDirection": "desc",
    }
    url = f"{API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.load(resp)
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected bank API payload: {type(data)}")
    return data


def map_bank(item: dict[str, Any]) -> dict[str, Any]:
    product = item.get("product") or {}
    company = product.get("bankCompany") or {}
    intervals = product.get("intervalAccountData") or []

    rates: list[str] = []
    thresholds: list[str] = []
    for interval in intervals[:6]:
        rate = interval.get("nominalInterestRate")
        threshold = interval.get("thresholdInterestRate")
        rates.append("" if rate is None else str(rate))
        thresholds.append("" if threshold is None else str(threshold))

    while len(rates) < 6:
        rates.append("")
    while len(thresholds) < 6:
        thresholds.append("")

    # App currently compounds on rentesats1 — prefer first interval, else effective rate.
    primary = rates[0] if rates[0] not in ("", None) else str(item.get("effectiveInterestRate") or "")

    url = (
        company.get("becomeCustomerURL")
        or company.get("contactURL")
        or company.get("changeBankURL")
        or ""
    )
    if url and not url.startswith("http"):
        url = "https://" + url.lstrip("/")

    today = datetime.now().strftime("%d.%m.%Y")
    return {
        "date": today,
        "product_id": str(item.get("oldProductId") or item.get("id") or ""),
        "version_id": str(item.get("id") or ""),
        "navn": item.get("name") or product.get("name") or "",
        "published": "TRUE",
        "publiserFra": (product.get("publishFrom") or "")[:10],
        "publiserTil": (product.get("publishTo") or "")[:10] if product.get("publishTo") else "",
        "leverandorId": str(item.get("companyId") or company.get("id") or ""),
        "leverandorUrl": url,
        "icon_url": "",
        "leverandorHref": "",
        "leverandorVisningsnavn": item.get("companyName") or company.get("name") or "",
        "markedsomraade": "Landsdekkende",
        "markedsomraadeTekst": "",
        "totaltInnestaende": str(item.get("totalAmount") or ""),
        "effectivRente": str(item.get("effectiveInterestRate") or ""),
        "nominellRente": primary,
        "rentebelop": str(item.get("interestAmount") or ""),
        "totalbelop": str(item.get("totalAmount") or ""),
        "minAlder": str(product.get("ageFrom") or ""),
        "maksAlder": str(product.get("ageTo") or ""),
        "trenger_ikke_pakke": "FALSE" if product.get("isPackageRequired") else "TRUE",
        "produktpakkeNavn": "",
        "produktpakkeHref": "",
        "forutsettermedlemskap": "TRUE" if product.get("isMembershipRequired") else "FALSE",
        "medlemskapNavn": "",
        "medlemskapHref": "",
        "kap_periode": str(product.get("capitalizationPeriod") or ""),
        "trapp_type": "rente pr intervall" if len(intervals) > 1 else "",
        "rentesats1": primary,
        "rentesats2": rates[1],
        "rentesats3": rates[2],
        "rentesats4": rates[3],
        "rentesats5": rates[4],
        "rentesats6": rates[5],
        "grensebelop1": thresholds[0],
        "grensebelop2": thresholds[1],
        "grensebelop3": thresholds[2],
        "grensebelop4": thresholds[3],
        "grensebelop5": thresholds[4],
        "grensebelop6": thresholds[5],
        "frie_uttak": str(product.get("numberOfFreeWithdrawalsPerYear") or ""),
    }


def write_meta(banks_count: int) -> None:
    meta = {}
    if META.exists():
        try:
            meta = json.loads(META.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}
    meta.update(
        {
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "banksCount": banks_count,
            "banksSource": "finans-api.forbrukerradet.no/bankprodukt/bankinnskudd",
        }
    )
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    products = fetch_products()
    print(f"Fetched {len(products)} bank products")
    banks = [map_bank(p) for p in products]
    banks = [b for b in banks if b["navn"] and b["leverandorVisningsnavn"] and b["rentesats1"]]

    if len(banks) < 50:
        raise SystemExit(f"Too few banks mapped ({len(banks)}); aborting write")

    OUT.write_text(json.dumps(banks, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    write_meta(len(banks))
    print(f"Wrote {len(banks)} banks -> {OUT}")
    print("Tip: run scripts/fix_icon_urls.py afterwards to fill icon_url favicons.")


if __name__ == "__main__":
    main()
