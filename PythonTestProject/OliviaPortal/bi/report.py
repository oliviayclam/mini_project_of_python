"""Phase 4: auto-export a text BI report."""

from datetime import datetime
from pathlib import Path

from bi.load_data import DATA_DIR, load_rows
from bi.summary import category_totals, overall_stats

REPORTS_DIR = DATA_DIR / "reports"


def export_report() -> Path:
    """Write a timestamped summary report to data/reports/."""
    rows = load_rows()
    count, total, average = overall_stats(rows)
    totals = category_totals(rows)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"expense_report_{stamp}.txt"

    lines = [
        "Olivia Portal — Expense BI Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Transactions : {count}",
        f"Total spent  : ${total:,.2f}",
        f"Average      : ${average:,.2f}",
        "",
        "Spending by category:",
        "-" * 32,
    ]
    for category, amount in totals.items():
        lines.append(f"  {category:<16} ${amount:>8.2f}")
    lines.append("")
    lines.append("End of report.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def auto_export_report() -> None:
    """Menu action: automatically export a report file."""
    print()
    print("----- Auto Report Export -----")
    try:
        path = export_report()
    except FileNotFoundError as exc:
        print(exc)
        input("\nPress Enter to return...")
        return

    print("Report created automatically.")
    print(f"Saved to: {path}")
    print()
    print("This is a simple automation example:")
    print("one click -> read data -> write a finished report file.")
    input("\nPress Enter to return...")
