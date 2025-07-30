"""Command-line interface for Tic-Tac-Toe game."""

import argparse
import sys
from typing import Tuple

from .ai import AIPlayer
from .board import Board


class CLI:
    """Command-line interface for the Tic-Tac-Toe game."""

    def __init__(self):
        """Initialize the CLI."""
        self.board = Board()
        self.ai_player = AIPlayer()

    def display_board(self):
        """Display the current board state."""
        print("\nCurrent board:")
        print(self.board)
        print()

    def get_user_move(self) -> Tuple[int, int]:
        """
        Get move input from user.

        Returns:
            Tuple of (row, col) representing the user's move
        """
        while True:
            try:
                move_input = input(
                    f"Player {self.board.current_player}, "
                    f"enter your move (row,col) [0-2,0-2]: "
                ).strip()

                if "," not in move_input:
                    print("Please enter your move in the format: row,col (e.g., 1,2)")
                    continue

                row_str, col_str = move_input.split(",", 1)
                row, col = int(row_str.strip()), int(col_str.strip())

                if not self.board.is_valid_position(row, col):
                    print("Invalid position! Please enter numbers between 0 and 2.")
                    continue

                if not self.board.is_position_empty(row, col):
                    print(
                        "That position is already taken! "
                        "Please choose an empty position."
                    )
                    continue

                return row, col

            except ValueError:
                print(
                    "Invalid input! Please enter numbers in the format: "
                    "row,col (e.g., 1,2)"
                )
            except KeyboardInterrupt:
                print("\nGame interrupted by user.")
                sys.exit(0)

    def play_human_vs_human(self):
        """Play a human vs human game."""
        print("=== Tic-Tac-Toe: Human vs Human ===")
        print("Enter moves as 'row,col' where both row and col are between 0-2")
        print("For example: '1,1' for the center position")

        while not self.board.is_game_over():
            self.display_board()
            row, col = self.get_user_move()
            self.board.make_move(row, col)

        self.display_board()
        self.show_game_result()

    def play_human_vs_ai(self):
        """Play a human vs AI game."""
        print("=== Tic-Tac-Toe: Human vs AI ===")
        print("You are X, AI is O")
        print("Enter moves as 'row,col' where both row and col are between 0-2")

        while not self.board.is_game_over():
            self.display_board()

            if self.board.current_player == "X":
                # Human turn
                row, col = self.get_user_move()
                self.board.make_move(row, col)
            else:
                # AI turn
                print("AI is thinking...")
                row, col = self.ai_player.get_best_move(self.board)
                print(f"AI plays: {row},{col}")
                self.board.make_move(row, col)

        self.display_board()
        self.show_game_result()

    def show_game_result(self):
        """Display the final game result."""
        winner = self.board.check_winner()
        if winner:
            print(f"🎉 Player {winner} wins!")
        else:
            print("🤝 It's a tie!")

    def show_menu(self):
        """Display the main menu and get user choice."""
        print("\n=== Tic-Tac-Toe Game ===")
        print("1. Human vs Human")
        print("2. Human vs AI")
        print("3. Quit")

        while True:
            try:
                choice = input("Enter your choice (1-3): ").strip()
                if choice in ["1", "2", "3"]:
                    return int(choice)
                print("Please enter 1, 2, or 3")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)

    def run(self):
        """Run the main game loop."""
        while True:
            choice = self.show_menu()

            if choice == 1:
                self.board.reset()
                self.play_human_vs_human()
            elif choice == 2:
                self.board.reset()
                self.play_human_vs_ai()
            elif choice == 3:
                print("Thanks for playing! Goodbye!")
                break

            # Ask if they want to play again
            print("\n" + "=" * 50)
            play_again = (
                input("Would you like to play another game? (y/n): ").strip().lower()
            )
            if play_again not in ["y", "yes"]:
                print("Thanks for playing! Goodbye!")
                break


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="A modern Tic-Tac-Toe game with AI opponent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tictactoe            # Start interactive game
  tictactoe --help     # Show this help message

Game Modes:
  1. Human vs Human - Two players take turns
  2. Human vs AI    - Play against computer opponent

AI Difficulty Levels:
  • Easy   - Random moves
  • Medium - Blocks wins and takes available wins
  • Hard   - Uses minimax algorithm for optimal play
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="tic-tac-toe 0.1.0"
    )

    parser.parse_args()

    try:
        cli = CLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
