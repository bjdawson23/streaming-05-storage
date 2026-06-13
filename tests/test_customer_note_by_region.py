"""Tests for customer note counts by region."""

from pathlib import Path

from streaming.customer_note_by_region_dawson import (
    count_customer_note_by_region,
    write_bar_chart,
)


def test_count_customer_note_by_region_groups_yes_no() -> None:
    sales_rows = [
        {"region_id": "US-MO", "customer_note": "great course"},
        {"region_id": "US-MO", "customer_note": ""},
        {"region_id": "US-MO", "customer_note": "  "},
        {"region_id": "US-CA", "customer_note": "thanks"},
        {"region_id": "US-CA", "customer_note": "helpful"},
    ]
    region_lookup = {"US-MO": "Missouri", "US-CA": "California"}

    result = count_customer_note_by_region(sales_rows, region_lookup)

    assert result["Missouri"]["yes"] == 1
    assert result["Missouri"]["no"] == 2
    assert result["California"]["yes"] == 2
    assert result["California"]["no"] == 0


def test_write_bar_chart_creates_output_file(tmp_path: Path) -> None:
    counts_by_region = {
        "Missouri": {"yes": 3, "no": 2},
        "California": {"yes": 5, "no": 1},
    }
    output_path = tmp_path / "consumer_note_by_region.png"

    write_bar_chart(counts_by_region, output_path)

    assert output_path.exists()
