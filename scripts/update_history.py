#!/usr/bin/env python3
"""
Download Nordnet fund return series into public/history/{orderBookId}.json.

Nordnet's market-data API only responds reliably from a real Chrome session,
so this uses Selenium. Values are cumulative return %% (same as Nordnet charts).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

ROOT = Path(__file__).resolve().parents[1]
FUNDS = ROOT / "public" / "funds.json"
OUT_DIR = ROOT / "public" / "history"
META = ROOT / "public" / "data-meta.json"

DEFAULT_NAMES = {
    "dnb global indeks a",
    "klp aksjeusa indeks valutasikret n",
}


def load_targets(mode: str, limit: int | None) -> list[dict]:
    funds = json.loads(FUNDS.read_text(encoding="utf-8"))
    rows = []
    for f in funds:
        info = f.get("instrument_info") or {}
        oid = info.get("market_data_order_book_id")
        slug = info.get("display_slug")
        name = info.get("name") or ""
        if not oid or not slug:
            continue
        if mode == "defaults" and name.lower() not in DEFAULT_NAMES:
            continue
        rows.append({"name": name, "id": oid, "slug": slug})
    if mode == "missing":
        rows = [r for r in rows if not (OUT_DIR / f"{r['id']}.json").exists()]
    if limit:
        rows = rows[:limit]
    return rows


def make_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,900")
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=opts)
    driver.execute_cdp_cmd(
        "Network.enable",
        {"maxTotalBufferSize": 100_000_000, "maxResourceBufferSize": 50_000_000},
    )
    return driver


def drain_series(driver: webdriver.Chrome, wanted: set[str]) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for entry in driver.get_log("performance"):
        msg = json.loads(entry["message"])["message"]
        if msg.get("method") != "Network.responseReceived":
            continue
        resp = msg["params"]["response"]
        url = resp["url"]
        if "price-time-series/period/" not in url or resp["status"] != 200:
            continue
        period = url.split("/period/")[1].split("/")[0]
        if period not in wanted or period in found:
            continue
        req_id = msg["params"]["requestId"]
        try:
            body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_id})[
                "body"
            ]
            found[period] = json.loads(body)
        except Exception:
            continue
    return found


def fetch_fund_history(driver: webdriver.Chrome, slug: str) -> dict | None:
    url = f"https://www.nordnet.no/fond/liste/{slug}"
    driver.get(url)
    time.sleep(3.2)

    # Prefer longest series.
    driver.execute_script(
        "const b=document.querySelector('[role=listbox]'); if(b) b.click();"
    )
    time.sleep(0.35)
    driver.execute_script(
        r"""
        const opts = [...document.querySelectorAll('[role=option]')];
        const prefer = [/maks/i, /max/i, /all/i, /10\s*år/i, /5\s*år/i];
        for (const re of prefer) {
          const opt = opts.find(el => re.test(el.textContent || ''));
          if (opt) { opt.click(); return; }
        }
        """
    )
    time.sleep(3.0)

    series = drain_series(driver, {"ALL", "YEAR_10", "YEAR_5", "YEAR_3", "YEAR_1"})
    for key in ("ALL", "YEAR_10", "YEAR_5", "YEAR_3", "YEAR_1"):
        if key in series and series[key].get("pricePoints"):
            return series[key]
    return None


def write_history(order_book_id: str, name: str, payload: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    points = [
        {"t": p["timeStamp"], "v": p["value"]}
        for p in payload.get("pricePoints") or []
        if "timeStamp" in p and "value" in p
    ]
    out = {
        "id": order_book_id,
        "name": name,
        "period": payload.get("returnedPeriod"),
        "resolution": payload.get("returnedResolution"),
        "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "points": points,
    }
    path = OUT_DIR / f"{order_book_id}.json"
    path.write_text(json.dumps(out, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def touch_meta(count: int) -> None:
    meta = {}
    if META.exists():
        try:
            meta = json.loads(META.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            meta = {}
    meta["historyCount"] = count
    meta["historySource"] = "nordnet market-data v3 (Selenium)"
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("defaults", "missing", "all"),
        default="defaults",
        help="Which funds to download history for",
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    targets = load_targets(args.mode, args.limit)
    if not targets:
        raise SystemExit(
            "No targets. Run npm run update:funds first so funds.json has display_slug / order book ids."
        )

    print(f"Downloading history for {len(targets)} funds ({args.mode})")
    driver = make_driver()
    ok = 0
    try:
        for i, row in enumerate(targets, 1):
            print(f"[{i}/{len(targets)}] {row['name']}")
            try:
                payload = fetch_fund_history(driver, row["slug"])
                if not payload:
                    print("  ! no series")
                    continue
                path = write_history(row["id"], row["name"], payload)
                print(
                    f"  wrote {path.name} "
                    f"({len(payload.get('pricePoints') or [])} pts, "
                    f"{payload.get('returnedPeriod')}/{payload.get('returnedResolution')})"
                )
                ok += 1
            except Exception as e:
                print(f"  ! error: {e}")
    finally:
        driver.quit()

    touch_meta(len(list(OUT_DIR.glob('*.json'))) if OUT_DIR.exists() else ok)
    print(f"Done. Saved {ok}/{len(targets)} histories.")


if __name__ == "__main__":
    main()
