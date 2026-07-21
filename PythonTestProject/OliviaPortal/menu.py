"""Main menu for Olivia Portal."""

from games import guessing, rps
from bi import charts, load_data, report, summary


def show_games_page() -> None:
    """Games submenu: pick a game or go back."""
    while True:
        print()
        print("----- Games -----")
        print("1. Number Guessing")
        print("2. Rock-Paper-Scissors")
        print("3. Back to main menu")
        choice = input("Choose (1-3): ").strip()

        if choice == "1":
            guessing.play()
        elif choice == "2":
            rps.play()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def show_bi_page() -> None:
    """Data & BI submenu."""
    while True:
        print()
        print("----- Data & BI -----")
        print("1. View expense data")
        print("2. Summary report")
        print("3. Create chart")
        print("4. Auto-export report (automation)")
        print("5. Back to main menu")
        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            load_data.view_data()
        elif choice == "2":
            summary.show_summary()
        elif choice == "3":
            charts.show_chart()
        elif choice == "4":
            report.auto_export_report()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter 1-5.")


def show_main_menu(username: str) -> None:
    """Show the main menu until the user logs out."""
    while True:
        print()
        print("===== Olivia Portal =====")
        print(f"Logged in as: {username}")
        print("1. Games")
        print("2. Data & BI")
        print("3. Logout")
        choice = input("Choose (1-3): ").strip()

        if choice == "1":
            show_games_page()
        elif choice == "2":
            show_bi_page()
        elif choice == "3":
            print()
            print("Logged out. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
