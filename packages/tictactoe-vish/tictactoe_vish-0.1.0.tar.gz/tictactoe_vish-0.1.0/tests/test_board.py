"""Unit tests for the Board class."""

from src.tictactoe.board import Board


class TestBoard:
    """Test cases for the Board class."""

    def test_board_initialization(self):
        """Test that board initializes correctly."""
        board = Board()
        assert board.current_player == "X"
        assert board.grid == [[None, None, None] for _ in range(3)]
        assert not board.is_full()
        assert not board.is_game_over()

    def test_board_string_representation(self):
        """Test string representation of the board."""
        board = Board()
        board.make_move(0, 0, "X")
        board.make_move(1, 1, "O")

        board_str = str(board)
        assert "X" in board_str
        assert "O" in board_str
        assert "|" in board_str
        assert "-" in board_str

    def test_make_move_valid(self):
        """Test making valid moves."""
        board = Board()

        # Test successful move
        assert board.make_move(0, 0) is True
        assert board.grid[0][0] == "X"
        assert board.current_player == "O"

        # Test next move
        assert board.make_move(1, 1) is True
        assert board.grid[1][1] == "O"
        assert board.current_player == "X"

    def test_make_move_invalid_position(self):
        """Test making moves to invalid positions."""
        board = Board()

        # Test out of bounds positions
        assert board.make_move(-1, 0) is False
        assert board.make_move(3, 0) is False
        assert board.make_move(0, -1) is False
        assert board.make_move(0, 3) is False

    def test_make_move_occupied_position(self):
        """Test making moves to occupied positions."""
        board = Board()

        # Make initial move
        assert board.make_move(0, 0) is True

        # Try to move to same position
        assert board.make_move(0, 0) is False
        assert board.grid[0][0] == "X"  # Should remain unchanged

    def test_make_move_with_explicit_player(self):
        """Test making moves with explicit player specification."""
        board = Board()

        # Make move with explicit player (should not switch current_player)
        assert board.make_move(0, 0, "O") is True
        assert board.grid[0][0] == "O"
        assert board.current_player == "X"  # Should remain X

    def test_is_valid_position(self):
        """Test position validation."""
        board = Board()

        # Valid positions
        assert board.is_valid_position(0, 0) is True
        assert board.is_valid_position(1, 1) is True
        assert board.is_valid_position(2, 2) is True

        # Invalid positions
        assert board.is_valid_position(-1, 0) is False
        assert board.is_valid_position(3, 0) is False
        assert board.is_valid_position(0, -1) is False
        assert board.is_valid_position(0, 3) is False

    def test_is_position_empty(self):
        """Test checking if position is empty."""
        board = Board()

        # Initially all positions should be empty
        assert board.is_position_empty(0, 0) is True
        assert board.is_position_empty(1, 1) is True

        # After making a move, position should not be empty
        board.make_move(0, 0)
        assert board.is_position_empty(0, 0) is False
        assert board.is_position_empty(1, 1) is True

        # Invalid positions should return False
        assert board.is_position_empty(-1, 0) is False
        assert board.is_position_empty(3, 0) is False

    def test_switch_player(self):
        """Test player switching."""
        board = Board()

        assert board.current_player == "X"
        board.switch_player()
        assert board.current_player == "O"
        board.switch_player()
        assert board.current_player == "X"

    def test_check_winner_rows(self):
        """Test winner detection for rows."""
        board = Board()

        # Test first row win
        board.make_move(0, 0, "X")
        board.make_move(0, 1, "X")
        board.make_move(0, 2, "X")
        assert board.check_winner() == "X"

        # Test second row win
        board = Board()
        board.make_move(1, 0, "O")
        board.make_move(1, 1, "O")
        board.make_move(1, 2, "O")
        assert board.check_winner() == "O"

    def test_check_winner_columns(self):
        """Test winner detection for columns."""
        board = Board()

        # Test first column win
        board.make_move(0, 0, "X")
        board.make_move(1, 0, "X")
        board.make_move(2, 0, "X")
        assert board.check_winner() == "X"

        # Test third column win
        board = Board()
        board.make_move(0, 2, "O")
        board.make_move(1, 2, "O")
        board.make_move(2, 2, "O")
        assert board.check_winner() == "O"

    def test_check_winner_diagonals(self):
        """Test winner detection for diagonals."""
        board = Board()

        # Test main diagonal win
        board.make_move(0, 0, "X")
        board.make_move(1, 1, "X")
        board.make_move(2, 2, "X")
        assert board.check_winner() == "X"

        # Test anti-diagonal win
        board = Board()
        board.make_move(0, 2, "O")
        board.make_move(1, 1, "O")
        board.make_move(2, 0, "O")
        assert board.check_winner() == "O"

    def test_check_winner_no_winner(self):
        """Test that no winner is detected when there isn't one."""
        board = Board()

        # Empty board
        assert board.check_winner() is None

        # Partial game without winner
        board.make_move(0, 0, "X")
        board.make_move(1, 1, "O")
        assert board.check_winner() is None

    def test_is_full(self):
        """Test board full detection."""
        board = Board()

        # Empty board should not be full
        assert board.is_full() is False

        # Fill entire board
        moves = [
            (0, 0, "X"),
            (0, 1, "O"),
            (0, 2, "X"),
            (1, 0, "O"),
            (1, 1, "X"),
            (1, 2, "O"),
            (2, 0, "X"),
            (2, 1, "O"),
            (2, 2, "X"),
        ]

        for row, col, player in moves:
            board.make_move(row, col, player)

        assert board.is_full() is True

    def test_is_game_over(self):
        """Test game over detection."""
        board = Board()

        # Empty board - game not over
        assert board.is_game_over() is False

        # Winning condition - game over
        board.make_move(0, 0, "X")
        board.make_move(0, 1, "X")
        board.make_move(0, 2, "X")
        assert board.is_game_over() is True

        # Full board without winner - game over (tie scenario)
        board = Board()
        moves = [
            (0, 0, "X"),
            (0, 1, "O"),
            (0, 2, "X"),
            (1, 0, "O"),
            (1, 1, "O"),
            (1, 2, "X"),
            (2, 0, "X"),
            (2, 1, "X"),
            (2, 2, "O"),
        ]

        for row, col, player in moves:
            board.make_move(row, col, player)

        assert board.is_game_over() is True
        assert board.check_winner() is None  # No winner, but game is over

    def test_get_empty_positions(self):
        """Test getting empty positions."""
        board = Board()

        # Initially all positions should be empty
        empty_positions = board.get_empty_positions()
        assert len(empty_positions) == 9
        assert (0, 0) in empty_positions
        assert (2, 2) in empty_positions

        # After making moves, empty positions should decrease
        board.make_move(0, 0)
        board.make_move(1, 1)
        empty_positions = board.get_empty_positions()
        assert len(empty_positions) == 7
        assert (0, 0) not in empty_positions
        assert (1, 1) not in empty_positions

    def test_reset(self):
        """Test board reset functionality."""
        board = Board()

        # Make some moves
        board.make_move(0, 0)
        board.make_move(1, 1)
        board.switch_player()

        # Reset board
        board.reset()

        # Check that board is back to initial state
        assert board.current_player == "X"
        assert board.grid == [[None, None, None] for _ in range(3)]
        assert not board.is_full()
        assert not board.is_game_over()

    def test_copy(self):
        """Test board copying functionality."""
        board = Board()

        # Make some moves
        board.make_move(0, 0)
        board.make_move(1, 1)

        # Create copy
        board_copy = board.copy()

        # Check that copy is identical
        assert board_copy.grid == board.grid
        assert board_copy.current_player == board.current_player

        # Check that copy is independent
        board_copy.make_move(2, 2)
        assert board_copy.grid != board.grid

    def test_integration_full_game(self):
        """Test a complete game scenario."""
        board = Board()

        # Play a game where X wins diagonally
        moves = [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)]  # X, O  # X, O  # X wins

        for i, (row, col) in enumerate(moves):
            assert board.is_game_over() is False
            assert board.make_move(row, col) is True

        assert board.check_winner() == "X"
        assert board.is_game_over() is True
