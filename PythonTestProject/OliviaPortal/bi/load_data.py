"""Load and display expense CSV data."""

import csv
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_CSV = DATA_DIR / "expenses.csv"


def load_rows(csv_path: Optional[Path] = None) -> List[Dict[str, str]]:
    """Read expense rows from a CSV file."""
    path = csv_path or DEFAULT_CSV
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def print_table(rows: List[Dict[str, str]], limit: int = 20) -> None:
    """Print a simple table of expense rows."""
    if not rows:
        print("No data to show.")
        return

    headers = list(rows[0].keys())
    widths = {h: max(len(h), max(len(str(r.get(h, ""))) for r in rows[:limit])) for h in headers}

    header_line = " | ".join(h.ljust(widths[h]) for h in headers)
    print(header_line)
    print("-+-".join("-" * widths[h] for h in headers))

    for row in rows[:limit]:
        print(" | ".join(str(row.get(h, "")).ljust(widths[h]) for h in headers))

    if len(rows) > limit:
        print(f"... and {len(rows) - limit} more row(s)")


def view_data() -> None:
    """Menu action: show the expense CSV."""
    print()
    print("----- View Data -----")
    try:
        rows = load_rows()
    except FileNotFoundError as exc:
        print(exc)
        input("\nPress Enter to return...")
        return

    print(f"File: {DEFAULT_CSV.name}  ({len(rows)} rows)")
    print()
    print_table(rows)
    input("\nPress Enter to return...")
