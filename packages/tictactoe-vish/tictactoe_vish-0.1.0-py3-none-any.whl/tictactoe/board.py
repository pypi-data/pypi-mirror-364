"""Tic-Tac-Toe game board implementation."""

from typing import List, Optional, Tuple


class Board:
    """Represents a Tic-Tac-Toe game board."""

    def __init__(self):
        """Initialize an empty 3x3 board."""
        self.grid: List[List[Optional[str]]] = [
            [None for _ in range(3)] for _ in range(3)
        ]
        self.current_player = "X"

    def __str__(self) -> str:
        """Return string representation of the board."""
        lines = []
        for i, row in enumerate(self.grid):
            row_str = " | ".join(cell if cell is not None else " " for cell in row)
            lines.append(f" {row_str} ")
            if i < 2:
                lines.append("-----------")
        return "\n".join(lines)

    def make_move(self, row: int, col: int, player: Optional[str] = None) -> bool:
        """
        Make a move on the board.

        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            player: Player symbol ('X' or 'O'). If None, uses current_player

        Returns:
            True if move was successful, False if position is occupied
        """
        if not self.is_valid_position(row, col):
            return False

        if self.grid[row][col] is not None:
            return False

        player_symbol = player if player is not None else self.current_player
        self.grid[row][col] = player_symbol

        if player is None:
            self.switch_player()

        return True

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if the given position is valid."""
        return 0 <= row < 3 and 0 <= col < 3

    def is_position_empty(self, row: int, col: int) -> bool:
        """Check if the given position is empty."""
        if not self.is_valid_position(row, col):
            return False
        return self.grid[row][col] is None

    def switch_player(self):
        """Switch to the next player."""
        self.current_player = "O" if self.current_player == "X" else "X"

    def check_winner(self) -> Optional[str]:
        """
        Check if there's a winner.

        Returns:
            'X' or 'O' if there's a winner, None otherwise
        """
        # Check rows
        for row in self.grid:
            if row[0] == row[1] == row[2] and row[0] is not None:
                return row[0]

        # Check columns
        for col in range(3):
            if (
                self.grid[0][col] == self.grid[1][col] == self.grid[2][col]
                and self.grid[0][col] is not None
            ):
                return self.grid[0][col]

        # Check diagonals
        if (
            self.grid[0][0] == self.grid[1][1] == self.grid[2][2]
            and self.grid[0][0] is not None
        ):
            return self.grid[0][0]

        if (
            self.grid[0][2] == self.grid[1][1] == self.grid[2][0]
            and self.grid[0][2] is not None
        ):
            return self.grid[0][2]

        return None

    def is_full(self) -> bool:
        """Check if the board is full."""
        return all(cell is not None for row in self.grid for cell in row)

    def is_game_over(self) -> bool:
        """Check if the game is over (either someone won or board is full)."""
        return self.check_winner() is not None or self.is_full()

    def get_empty_positions(self) -> List[Tuple[int, int]]:
        """Get all empty positions on the board."""
        empty_positions = []
        for row in range(3):
            for col in range(3):
                if self.grid[row][col] is None:
                    empty_positions.append((row, col))
        return empty_positions

    def reset(self):
        """Reset the board to initial state."""
        self.grid = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = "X"

    def copy(self) -> "Board":
        """Create a copy of the current board."""
        new_board = Board()
        new_board.grid = [row[:] for row in self.grid]
        new_board.current_player = self.current_player
        return new_board
