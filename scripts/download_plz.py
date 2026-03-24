#!/usr/bin/env python3
"""Download all Swiss postal codes and municipality names from OpenPLZ API.

Usage:
    source .venv/bin/activate
    python scripts/download_plz.py
"""

import csv
import json
import ssl
import urllib.request
import time
from pathlib import Path

# macOS Python often lacks SSL certificates — bypass for public open data API
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

API_BASE = "https://openplzapi.org/ch"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "swiss_municipalities.csv"
PAGE_SIZE = 50

# All 26 Swiss cantons with their official keys
# BFS canton keys (no leading zeros — API requires "1" not "01")
CANTON_KEYS = {
    "1": "ZH", "2": "BE", "3": "LU", "4": "UR", "5": "SZ",
    "6": "OW", "7": "NW", "8": "GL", "9": "ZG", "10": "FR",
    "11": "SO", "12": "BS", "13": "BL", "14": "SH", "15": "AR",
    "16": "AI", "17": "SG", "18": "GR", "19": "AG", "20": "TG",
    "21": "TI", "22": "VD", "23": "VS", "24": "NE", "25": "GE",
    "26": "JU",
}


def fetch_localities_for_canton(canton_key: str, page: int) -> list[dict]:
    """Fetch localities for a specific canton."""
    url = f"{API_BASE}/Cantons/{canton_key}/Localities?page={page}&pageSize={PAGE_SIZE}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30, context=SSL_CONTEXT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download_all_localities() -> list[dict]:
    """Download all localities by iterating through cantons."""
    all_localities = []

    for canton_key, canton_abbr in sorted(CANTON_KEYS.items()):
        print(f"\n  Canton {canton_abbr} (key {canton_key}):", end="", flush=True)
        page = 1
        canton_count = 0

        while True:
            try:
                data = fetch_localities_for_canton(canton_key, page)
            except Exception as e:
                print(f" Error on page {page}: {e}")
                break

            if not data:
                break

            all_localities.extend(data)
            canton_count += len(data)
            print(f" {canton_count}", end="", flush=True)
            page += 1
            time.sleep(0.1)

        print(f" — total: {canton_count}")

    return all_localities


def write_csv(localities: list[dict], output_path: Path) -> None:
    """Write localities to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    seen = set()
    rows = []

    for loc in localities:
        plz = loc.get("postalCode", "") or ""
        name = loc.get("name", "") or ""
        canton = ""
        canton_name = ""
        municipality = ""

        if loc.get("canton"):
            canton_key = loc["canton"].get("key", "") or ""
            canton = CANTON_KEYS.get(canton_key, canton_key)  # Convert to abbreviation
            canton_name = loc["canton"].get("name", "") or ""
        if loc.get("municipality"):
            municipality = loc["municipality"].get("name", "") or ""

        key = f"{plz}_{name}"
        if key and key != "_" and key not in seen:
            seen.add(key)
            rows.append({
                "plz": plz,
                "name": name,
                "canton": canton,
                "canton_name": canton_name,
                "municipality": municipality,
            })

    rows.sort(key=lambda r: r["plz"])

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["plz", "name", "canton", "canton_name", "municipality"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Written {len(rows)} unique PLZ/locality entries to {output_path}")


def main() -> None:
    print("🇨🇭 Downloading Swiss postal codes from OpenPLZ API...")
    print(f"   Target: {OUTPUT_FILE}")

    localities = download_all_localities()
    print(f"\n   Total fetched: {len(localities)} entries")

    write_csv(localities, OUTPUT_FILE)


if __name__ == "__main__":
    main()
