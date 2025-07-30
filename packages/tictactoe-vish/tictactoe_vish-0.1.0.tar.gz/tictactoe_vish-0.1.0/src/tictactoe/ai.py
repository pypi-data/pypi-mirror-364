"""Simple AI player for Tic-Tac-Toe using minimax algorithm."""

import random
from typing import Optional, Tuple

from .board import Board


class AIPlayer:
    """AI player that uses minimax algorithm to play Tic-Tac-Toe."""

    def __init__(self, difficulty: str = "hard"):
        """
        Initialize AI player.

        Args:
            difficulty: AI difficulty level ('easy', 'medium', 'hard')
        """
        self.difficulty = difficulty
        self.player_symbol = "O"
        self.opponent_symbol = "X"

    def get_best_move(self, board: Board) -> Tuple[int, int]:
        """
        Get the best move for the AI player.

        Args:
            board: Current game board

        Returns:
            Tuple of (row, col) representing the best move
        """
        if self.difficulty == "easy":
            return self._get_random_move(board)
        if self.difficulty == "medium":
            return self._get_medium_move(board)
        # hard
        return self._get_minimax_move(board)

    def _get_random_move(self, board: Board) -> Tuple[int, int]:
        """Get a random valid move."""
        empty_positions = board.get_empty_positions()
        return random.choice(empty_positions) #NOSONAR

    def _get_medium_move(self, board: Board) -> Tuple[int, int]:
        """
        Medium difficulty: Try to win, then block opponent, otherwise random.
        """
        # Try to win
        winning_move = self._find_winning_move(board, self.player_symbol)
        if winning_move:
            return winning_move

        # Try to block opponent from winning
        blocking_move = self._find_winning_move(board, self.opponent_symbol)
        if blocking_move:
            return blocking_move

        # Otherwise, play randomly
        return self._get_random_move(board)

    def _get_minimax_move(self, board: Board) -> Tuple[int, int]:
        """Get the best move using minimax algorithm."""
        best_score = float("-inf")
        best_move = None

        for row, col in board.get_empty_positions():
            # Make temporary move
            board_copy = board.copy()
            board_copy.make_move(row, col, self.player_symbol)

            # Calculate score using minimax
            score = self._minimax(board_copy, 0, False)

            if score > best_score:
                best_score = score
                best_move = (row, col)

        return best_move if best_move else self._get_random_move(board)

    def _minimax(self, board: Board, depth: int, is_maximizing: bool) -> int:
        """
        Minimax algorithm implementation.

        Args:
            board: Current board state
            depth: Current depth in the game tree
            is_maximizing: True if maximizing player's turn, False otherwise

        Returns:
            Score of the current board state
        """
        winner = board.check_winner()

        # Terminal states
        if winner == self.player_symbol:
            return 10 - depth
        if winner == self.opponent_symbol:
            return depth - 10
        if board.is_full():
            return 0

        if is_maximizing:
            best_score = float("-inf")
            for row, col in board.get_empty_positions():
                board_copy = board.copy()
                board_copy.make_move(row, col, self.player_symbol)
                score = self._minimax(board_copy, depth + 1, False)
                best_score = max(score, best_score)
            return best_score

        best_score = float("inf")
        for row, col in board.get_empty_positions():
            board_copy = board.copy()
            board_copy.make_move(row, col, self.opponent_symbol)
            score = self._minimax(board_copy, depth + 1, True)
            best_score = min(score, best_score)
        return best_score

    def _find_winning_move(
        self, board: Board, player: str
    ) -> Optional[Tuple[int, int]]:
        """
        Find a move that wins the game for the given player.

        Args:
            board: Current board state
            player: Player symbol to find winning move for

        Returns:
            Tuple of (row, col) if winning move exists, None otherwise
        """
        for row, col in board.get_empty_positions():
            board_copy = board.copy()
            board_copy.make_move(row, col, player)
            if board_copy.check_winner() == player:
                return (row, col)
        return None

    def set_difficulty(self, difficulty: str):
        """
        Set AI difficulty level.

        Args:
            difficulty: New difficulty level ('easy', 'medium', 'hard')
        """
        if difficulty in ["easy", "medium", "hard"]:
            self.difficulty = difficulty
        else:
            raise ValueError("Difficulty must be 'easy', 'medium', or 'hard'")

    def set_symbols(self, ai_symbol: str, opponent_symbol: str):
        """
        Set the symbols for AI and opponent.

        Args:
            ai_symbol: Symbol for AI player
            opponent_symbol: Symbol for opponent
        """
        self.player_symbol = ai_symbol
        self.opponent_symbol = opponent_symbol
