"""Build customer note yes/no counts by region name.

Reads all rows from data/sales.csv, determines whether each row has
customer_note text, groups by region_name, and writes the results to

data/output/consumer_note_by_region.csv.

Run from project root:

    uv run python -m streaming.customer_note_by_region_dawson
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Final

from datafun_streaming.io.io_utils import append_csv_row, read_csv_rows
import matplotlib.pyplot as plt

from streaming.data_engineering.derived_fields import compute_has_customer_note

ROOT_DIR: Final[Path] = Path.cwd()
DATA_DIR: Final[Path] = ROOT_DIR / "data"
OUTPUT_DIR: Final[Path] = DATA_DIR / "output"

SALES_CSV: Final[Path] = DATA_DIR / "sales.csv"
REGIONS_CSV: Final[Path] = DATA_DIR / "regions.csv"
OUTPUT_CSV: Final[Path] = OUTPUT_DIR / "consumer_note_by_region.csv"
OUTPUT_CHART: Final[Path] = OUTPUT_DIR / "consumer_note_by_region.png"

OUTPUT_FIELDNAMES: Final[list[str]] = [
    "region_name",
    "customer_note_yes_count",
    "customer_note_no_count",
]


def build_region_lookup() -> dict[str, str]:
    """Return mapping of region_id to region_name from regions.csv."""
    region_rows = read_csv_rows(REGIONS_CSV)
    return {
        row.get("region_id", ""): row.get("region_name", "Unknown")
        for row in region_rows
        if row.get("region_id", "")
    }


def count_customer_note_by_region(
    sales_rows: list[dict[str, str]],
    region_lookup: dict[str, str],
) -> dict[str, dict[str, int]]:
    """Count customer_note yes/no values grouped by region_name."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"yes": 0, "no": 0})

    for row in sales_rows:
        region_id = row.get("region_id", "")
        region_name = region_lookup.get(region_id, "Unknown")
        has_customer_note = compute_has_customer_note(row.get("customer_note", ""))
        counts[region_name][has_customer_note] += 1

    return dict(counts)


def write_counts(counts_by_region: dict[str, dict[str, int]]) -> None:
    """Write grouped counts to data/output/consumer_note_by_region.csv."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_CSV.exists():
        OUTPUT_CSV.unlink()

    for region_name in sorted(counts_by_region):
        counts = counts_by_region[region_name]
        append_csv_row(
            path=OUTPUT_CSV,
            row={
                "region_name": region_name,
                "customer_note_yes_count": counts.get("yes", 0),
                "customer_note_no_count": counts.get("no", 0),
            },
            fieldnames=OUTPUT_FIELDNAMES,
        )


def write_bar_chart(
    counts_by_region: dict[str, dict[str, int]],
    output_path: Path = OUTPUT_CHART,
) -> None:
    """Write a grouped bar chart of customer note yes/no counts by region."""
    region_names = sorted(counts_by_region)
    yes_counts = [counts_by_region[region].get("yes", 0) for region in region_names]
    no_counts = [counts_by_region[region].get("no", 0) for region in region_names]

    positions = list(range(len(region_names)))
    bar_width = 0.4

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(
        [position - bar_width / 2 for position in positions],
        yes_counts,
        width=bar_width,
        label="Yes",
    )
    ax.bar(
        [position + bar_width / 2 for position in positions],
        no_counts,
        width=bar_width,
        label="No",
    )

    ax.set_title("Customer Note Presence by Region")
    ax.set_xlabel("Region Name")
    ax.set_ylabel("Count")
    ax.set_xticks(positions)
    ax.set_xticklabels(region_names, rotation=30, ha="right")
    ax.legend()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def main() -> None:
    """Run the customer note aggregation pipeline."""
    sales_rows = read_csv_rows(SALES_CSV)
    region_lookup = build_region_lookup()
    counts_by_region = count_customer_note_by_region(sales_rows, region_lookup)
    write_counts(counts_by_region)
    write_bar_chart(counts_by_region)


if __name__ == "__main__":
    main()
