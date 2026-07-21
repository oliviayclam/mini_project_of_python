"""Create BI charts from expense data."""

from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # Save charts to files (works without a GUI window)
import matplotlib.pyplot as plt

from bi.load_data import DATA_DIR, load_rows
from bi.summary import category_totals

CHARTS_DIR = DATA_DIR / "charts"


def create_category_chart(output_path: Optional[Path] = None) -> Path:
    """Build a bar chart of spending by category and save it as PNG."""
    rows = load_rows()
    totals = category_totals(rows)
    if not totals:
        raise ValueError("No data available to chart.")

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path or (CHARTS_DIR / "spending_by_category.png")

    categories = list(totals.keys())
    amounts = list(totals.values())

    plt.figure(figsize=(8, 4.5))
    bars = plt.bar(categories, amounts, color="#2f6fed")
    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount ($)")
    plt.xticks(rotation=30, ha="right")
    for bar, amount in zip(bars, amounts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"${amount:.0f}",
                 ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def show_chart() -> None:
    """Menu action: generate and save a chart."""
    print()
    print("----- Chart -----")
    try:
        path = create_category_chart()
    except (FileNotFoundError, ValueError, ImportError) as exc:
        print(f"Could not create chart: {exc}")
        if isinstance(exc, ImportError):
            print("Install matplotlib with: pip install matplotlib")
        input("\nPress Enter to return...")
        return

    print(f"Chart saved to: {path}")
    print("Open that PNG file to view your BI chart.")
    input("\nPress Enter to return...")
