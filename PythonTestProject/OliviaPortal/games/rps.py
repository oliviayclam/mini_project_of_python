"""Rock-Paper-Scissors game."""

import random

CHOICES = ("rock", "paper", "scissors")
BEATS = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper",
}


def _winner(player: str, computer: str) -> str:
    if player == computer:
        return "tie"
    if BEATS[player] == computer:
        return "player"
    return "computer"


def play() -> None:
    """Play Rock-Paper-Scissors against the computer."""
    print()
    print("----- Rock-Paper-Scissors -----")
    print("Type rock, paper, or scissors.")
    print("Type 'q' to quit this game.")
    print()

    wins = 0
    losses = 0
    ties = 0

    while True:
        player = input("Your move: ").strip().lower()
        if player == "q":
            break

        if player not in CHOICES:
            print("Please type rock, paper, scissors, or q.")
            continue

        computer = random.choice(CHOICES)
        result = _winner(player, computer)
        print(f"Computer chose: {computer}")

        if result == "tie":
            ties += 1
            print("It's a tie!")
        elif result == "player":
            wins += 1
            print("You win!")
        else:
            losses += 1
            print("Computer wins!")

        print(f"Score  You {wins} - {losses} Computer  (ties: {ties})")
        print()

    print(f"Final score  You {wins} - {losses} Computer  (ties: {ties})")
    input("\nPress Enter to return to the Games menu...")
