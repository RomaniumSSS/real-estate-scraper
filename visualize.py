"""Generate professional charts from cleaned apartment data."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CHARTS_DIR = Path("output/charts")
COLORS = {
    "primary": "#2D6A4F",
    "secondary": "#E76F51",
    "accent": "#1B4332",
    "bg": "#F5F5F0",
    "grid": "#B7E4C7",
}


def generate_charts(df: pd.DataFrame) -> list[Path]:
    """Generate all charts and return list of saved file paths."""
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.facecolor": COLORS["bg"],
            "axes.facecolor": "white",
            "axes.edgecolor": COLORS["grid"],
            "font.size": 11,
        }
    )

    paths = [
        _price_distribution(df),
        _price_per_sqm_by_district(df),
        _rooms_vs_price(df),
    ]
    print(f"  Saved {len(paths)} charts to {CHARTS_DIR}/")
    return paths


def _price_distribution(df: pd.DataFrame) -> Path:
    """Histogram of apartment prices with median line."""
    fig, ax = plt.subplots(figsize=(10, 6))

    prices_m = df["price_czk"] / 1_000_000  # millions
    ax.hist(prices_m, bins=30, color=COLORS["primary"], alpha=0.8, edgecolor="white")

    median = prices_m.median()
    ax.axvline(
        median,
        color=COLORS["secondary"],
        linewidth=2,
        linestyle="--",
        label=f"Median: {median:.1f}M CZK",
    )

    ax.set_xlabel("Price (million CZK)", fontsize=12)
    ax.set_ylabel("Number of Listings", fontsize=12)
    ax.set_title(
        "Price Distribution of Prague Apartments", fontsize=14, fontweight="bold"
    )
    ax.legend(fontsize=11)

    path = CHARTS_DIR / "price_distribution.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _price_per_sqm_by_district(df: pd.DataFrame) -> Path:
    """Horizontal bar chart — avg price/m² for top 10 districts."""
    fig, ax = plt.subplots(figsize=(10, 7))

    top = (
        df.groupby("district")["price_per_sqm"]
        .agg(["mean", "count"])
        .query("count >= 3")
        .nlargest(10, "mean")
        .sort_values("mean")
    )

    bars = ax.barh(top.index, top["mean"], color=COLORS["primary"], edgecolor="white")

    for bar, (_, row) in zip(bars, top.iterrows()):
        ax.text(
            bar.get_width() + 500,
            bar.get_y() + bar.get_height() / 2,
            f"{row['mean']:,.0f} CZK",
            va="center",
            fontsize=9,
        )

    ax.set_xlabel("Average Price per m² (CZK)", fontsize=12)
    ax.set_title("Price per m² by District (Top 10)", fontsize=14, fontweight="bold")

    path = CHARTS_DIR / "price_per_sqm_by_district.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _rooms_vs_price(df: pd.DataFrame) -> Path:
    """Box plot of prices grouped by room count."""
    fig, ax = plt.subplots(figsize=(10, 6))

    room_types = sorted(df[df["rooms"] != ""]["rooms"].unique())
    data = [df[df["rooms"] == r]["price_czk"] / 1_000_000 for r in room_types]

    bp = ax.boxplot(
        data,
        labels=room_types,
        patch_artist=True,
        boxprops=dict(facecolor=COLORS["primary"], alpha=0.7),
        medianprops=dict(color=COLORS["secondary"], linewidth=2),
        whiskerprops=dict(color=COLORS["accent"]),
        capprops=dict(color=COLORS["accent"]),
        flierprops=dict(
            marker="o", markerfacecolor=COLORS["secondary"], markersize=4, alpha=0.5
        ),
    )

    ax.set_xlabel("Room Layout", fontsize=12)
    ax.set_ylabel("Price (million CZK)", fontsize=12)
    ax.set_title("Price by Room Count", fontsize=14, fontweight="bold")

    path = CHARTS_DIR / "rooms_vs_price.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path
