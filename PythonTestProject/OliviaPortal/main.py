"""Olivia Portal — Phase 1: login + main menu."""

from auth import login_screen
from menu import show_main_menu


def main() -> None:
    username = login_screen()
    if username is None:
        return
    show_main_menu(username)


if __name__ == "__main__":
    main()
