"""Summarize expense data by category."""

from collections import defaultdict
from typing import Dict, List, Tuple

from bi.load_data import load_rows


def category_totals(rows: List[Dict[str, str]]) -> Dict[str, float]:
    """Return total amount per category."""
    totals: Dict[str, float] = defaultdict(float)
    for row in rows:
        category = row.get("category", "Unknown")
        try:
            amount = float(row.get("amount", "0"))
        except ValueError:
            amount = 0.0
        totals[category] += amount
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def overall_stats(rows: List[Dict[str, str]]) -> Tuple[int, float, float]:
    """Return count, total, and average amount."""
    amounts = []
    for row in rows:
        try:
            amounts.append(float(row.get("amount", "0")))
        except ValueError:
            continue
    count = len(amounts)
    total = sum(amounts)
    average = total / count if count else 0.0
    return count, total, average


def print_summary(rows: List[Dict[str, str]]) -> None:
    """Print overall stats and category breakdown."""
    count, total, average = overall_stats(rows)
    print(f"Transactions : {count}")
    print(f"Total spent  : ${total:,.2f}")
    print(f"Average      : ${average:,.2f}")
    print()
    print("Spending by category:")
    print("-" * 32)
    for category, amount in category_totals(rows).items():
        print(f"  {category:<16} ${amount:>8.2f}")


def show_summary() -> None:
    """Menu action: print summary stats."""
    print()
    print("----- Summary Report -----")
    try:
        rows = load_rows()
    except FileNotFoundError as exc:
        print(exc)
        input("\nPress Enter to return...")
        return

    print_summary(rows)
    input("\nPress Enter to return...")
