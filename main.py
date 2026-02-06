"""Pipeline: scrape → clean → export → visualize Prague apartment listings."""

import argparse

from scraper import load_cached, save_raw, scrape_listings
from cleaner import clean_listings
from exporter import export_excel
from visualize import generate_charts


def main() -> None:
    parser = argparse.ArgumentParser(description="Prague apartment scraping pipeline")
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Use previously saved data instead of scraping",
    )
    args = parser.parse_args()

    # Step 1: Scrape
    print("[1/4] Scraping listings...")
    if args.use_cache:
        raw = load_cached()
    else:
        raw = scrape_listings()
        save_raw(raw)

    # Step 2: Clean
    print("[2/4] Cleaning data...")
    df = clean_listings(raw)

    # Step 3: Export
    print("[3/4] Exporting to Excel...")
    export_excel(df)

    # Step 4: Visualize
    print("[4/4] Generating charts...")
    generate_charts(df)

    print(f"\nDone! {len(df)} listings processed.")


if __name__ == "__main__":
    main()
