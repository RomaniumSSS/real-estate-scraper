"""Scrape apartment listings from sreality.cz API."""

import json
import time
from pathlib import Path

import requests

API_URL = "https://www.sreality.cz/api/cs/v2/estates"
PARAMS = {
    "category_main_cb": 1,  # apartments
    "category_type_cb": 1,  # sale
    "per_page": 60,
}
PAGES = 4
DELAY = 1.5
RAW_PATH = Path("data/raw_listings.json")


def scrape_listings() -> list[dict]:
    """Fetch apartment listings from sreality.cz API with pagination."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (compatible; student-project/1.0)",
            "Accept": "application/json",
        }
    )

    all_estates = []
    for page in range(1, PAGES + 1):
        params = {**PARAMS, "page": page}
        print(f"  Fetching page {page}/{PAGES}...")
        resp = session.get(API_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        estates = data.get("_embedded", {}).get("estates", [])
        if not estates:
            print(f"  No results on page {page}, stopping.")
            break
        all_estates.extend(estates)
        print(f"  Got {len(estates)} listings (total: {len(all_estates)})")
        if page < PAGES:
            time.sleep(DELAY)

    return all_estates


def save_raw(estates: list[dict]) -> Path:
    """Save raw API response to JSON file."""
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_text(
        json.dumps(estates, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Saved {len(estates)} listings to {RAW_PATH}")
    return RAW_PATH


def load_cached() -> list[dict]:
    """Load previously saved raw listings."""
    if not RAW_PATH.exists():
        raise FileNotFoundError(
            f"No cached data at {RAW_PATH}. Run without --use-cache first."
        )
    estates = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    print(f"  Loaded {len(estates)} cached listings from {RAW_PATH}")
    return estates
