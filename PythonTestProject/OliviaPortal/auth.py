"""Login and password helpers for Olivia Portal."""

import hashlib
import json
from pathlib import Path
from typing import Optional

USERS_FILE = Path(__file__).parent / "users.json"
MAX_ATTEMPTS = 3


def hash_password(password: str) -> str:
    """Return a SHA-256 hex digest of the password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users():
    """Load the user list from users.json."""
    with USERS_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    return data.get("users", [])


def check_login(username: str, password: str) -> bool:
    """Return True if username and password match a stored user."""
    password_hash = hash_password(password)
    for user in load_users():
        if user["username"] == username and user["password"] == password_hash:
            return True
    return False


def login_screen() -> Optional[str]:
    """
    Ask for username and password until success or too many failures.

    Returns the logged-in username, or None if login failed.
    """
    print("===== Olivia Portal Login =====")
    print("(Demo account: olivia / 1234)")
    print()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if check_login(username, password):
            print()
            print(f"Login successful! Welcome, {username}.")
            return username

        remaining = MAX_ATTEMPTS - attempt
        if remaining > 0:
            print(f"Wrong username or password. {remaining} attempt(s) left.")
            print()
        else:
            print("Too many failed attempts. Exiting.")

    return None
