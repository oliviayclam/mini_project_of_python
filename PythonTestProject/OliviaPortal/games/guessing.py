"""Number guessing game."""

import random


def play() -> None:
    """Play: guess a number from 1 to 20."""
    secret = random.randint(1, 20)
    attempts = 0

    print()
    print("----- Number Guessing -----")
    print("I picked a number between 1 and 20.")
    print("Type 'q' to quit this game.")
    print()

    while True:
        guess_text = input("Your guess: ").strip().lower()
        if guess_text == "q":
            print(f"You quit. The number was {secret}.")
            break

        if not guess_text.isdigit():
            print("Please enter a whole number (or 'q' to quit).")
            continue

        guess = int(guess_text)
        if guess < 1 or guess > 20:
            print("Stay between 1 and 20.")
            continue

        attempts += 1
        if guess < secret:
            print("Too low!")
        elif guess > secret:
            print("Too high!")
        else:
            print(f"Correct! You got it in {attempts} attempt(s).")
            break

    input("\nPress Enter to return to the Games menu...")
