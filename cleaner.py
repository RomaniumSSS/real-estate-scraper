"""Clean and transform raw sreality.cz listings into a structured DataFrame."""

import re

import pandas as pd


def clean_listings(raw_estates: list[dict]) -> pd.DataFrame:
    """Transform raw API data into a clean DataFrame with derived fields."""
    records = []
    for estate in raw_estates:
        name = estate.get("name", "")
        locality = estate.get("locality", "")
        gps = estate.get("gps", {})
        hash_id = estate.get("hash_id", 0)
        seo = estate.get("seo", {})

        records.append(
            {
                "hash_id": hash_id,
                "title": name,
                "price_czk": estate.get("price", 0),
                "area_sqm": _parse_area(name),
                "rooms": _parse_rooms(name),
                "district": _extract_district(locality),
                "locality": locality,
                "lat": gps.get("lat"),
                "lon": gps.get("lon"),
                "labels": ", ".join(estate.get("labels", [])),
                "url": _build_url(hash_id, seo),
            }
        )

    df = pd.DataFrame(records)
    initial_count = len(df)

    # Drop rows missing price or area
    df = df[df["price_czk"] > 0]
    df = df[df["area_sqm"] > 0]

    # Remove duplicates
    df = df.drop_duplicates(subset="hash_id")

    # Calculate price per sqm
    df["price_per_sqm"] = (df["price_czk"] / df["area_sqm"]).round(0).astype(int)

    # Remove outliers using IQR on price_per_sqm
    df = _remove_outliers(df, "price_per_sqm")

    df = df.reset_index(drop=True)
    print(f"  Cleaned: {initial_count} → {len(df)} listings")
    return df


def _parse_area(name: str) -> float:
    """Extract area in sqm from listing name, e.g. '55 m²' → 55.0."""
    match = re.search(r"(\d+)\s*m[²2]", name)
    return float(match.group(1)) if match else 0.0


def _parse_rooms(name: str) -> str:
    """Extract room layout from listing name, e.g. '2+kk', '3+1'."""
    match = re.search(r"(\d\+(?:kk|\d))", name)
    return match.group(1) if match else ""


def _extract_district(locality: str) -> str:
    """Extract district from locality — first part before dash or comma."""
    # "Praha 5 - Smíchov" → "Praha 5"
    # "Brno - Žabovřesky" → "Brno"
    for sep in [" - ", ", "]:
        if sep in locality:
            return locality.split(sep)[0].strip()
    return locality.strip()


def _build_url(hash_id: int, seo: dict) -> str:
    """Construct sreality.cz detail URL from hash_id and seo data."""
    locality_seo = seo.get("locality", "")
    if hash_id and locality_seo:
        return f"https://www.sreality.cz/detail/prodej/byt/{locality_seo}/{hash_id}"
    return ""


def _remove_outliers(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Remove rows where column value falls outside 1.5x IQR."""
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    before = len(df)
    df = df[(df[column] >= lower) & (df[column] <= upper)]
    removed = before - len(df)
    if removed:
        print(
            f"  Removed {removed} outliers (price_per_sqm outside {lower:.0f}–{upper:.0f})"
        )
    return df
