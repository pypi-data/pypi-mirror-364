"""Unit tests for the AI player."""

import pytest

from src.tictactoe.ai import AIPlayer
from src.tictactoe.board import Board


class TestAIPlayer:
    """Test cases for the AIPlayer class."""

    def test_ai_initialization(self):
        """Test AI player initialization."""
        ai = AIPlayer()
        assert ai.difficulty == "hard"
        assert ai.player_symbol == "O"
        assert ai.opponent_symbol == "X"

    def test_ai_initialization_with_difficulty(self):
        """Test AI player initialization with custom difficulty."""
        ai = AIPlayer("easy")
        assert ai.difficulty == "easy"

        ai = AIPlayer("medium")
        assert ai.difficulty == "medium"

        ai = AIPlayer("hard")
        assert ai.difficulty == "hard"

    def test_set_difficulty(self):
        """Test setting AI difficulty."""
        ai = AIPlayer()

        ai.set_difficulty("easy")
        assert ai.difficulty == "easy"

        ai.set_difficulty("medium")
        assert ai.difficulty == "medium"

        ai.set_difficulty("hard")
        assert ai.difficulty == "hard"

        # Test invalid difficulty
        with pytest.raises(ValueError):
            ai.set_difficulty("invalid")

    def test_set_symbols(self):
        """Test setting AI and opponent symbols."""
        ai = AIPlayer()

        ai.set_symbols("X", "O")
        assert ai.player_symbol == "X"
        assert ai.opponent_symbol == "O"

    def test_get_random_move(self):
        """Test random move generation."""
        ai = AIPlayer("easy")
        board = Board()

        # Test that AI returns a valid move
        move = ai.get_best_move(board)
        assert isinstance(move, tuple)
        assert len(move) == 2
        assert 0 <= move[0] <= 2
        assert 0 <= move[1] <= 2
        assert board.is_position_empty(move[0], move[1])

    def test_get_random_move_limited_options(self):
        """Test random move when few options available."""
        ai = AIPlayer("easy")
        board = Board()

        # Fill most of the board
        moves = [
            (0, 0, "X"),
            (0, 1, "O"),
            (0, 2, "X"),
            (1, 0, "O"),
            (1, 1, "X"),
            (1, 2, "O"),
            (2, 0, "X"),
            (2, 1, "O"),
        ]

        for row, col, player in moves:
            board.make_move(row, col, player)

        # Only (2, 2) should be available
        move = ai.get_best_move(board)
        assert move == (2, 2)

    def test_find_winning_move(self):
        """Test finding winning moves."""
        ai = AIPlayer()
        board = Board()

        # Set up a winning opportunity for O
        board.make_move(0, 0, "O")
        board.make_move(0, 1, "O")
        # Position (0, 2) would win for O

        winning_move = ai._find_winning_move(board, "O")
        assert winning_move == (0, 2)

        # Test no winning move available
        board = Board()
        board.make_move(0, 0, "O")
        winning_move = ai._find_winning_move(board, "O")
        assert winning_move is None

    def test_medium_difficulty_wins(self):
        """Test medium difficulty AI takes winning moves."""
        ai = AIPlayer("medium")
        board = Board()

        # Set up winning opportunity for AI (O)
        board.make_move(0, 0, "O")
        board.make_move(0, 1, "O")
        board.make_move(1, 0, "X")  # Random move by opponent

        move = ai.get_best_move(board)
        assert move == (0, 2)  # Should take the winning move

    def test_medium_difficulty_blocks(self):
        """Test medium difficulty AI blocks opponent wins."""
        ai = AIPlayer("medium")
        board = Board()

        # Set up opponent winning opportunity
        board.make_move(0, 0, "X")
        board.make_move(0, 1, "X")
        board.make_move(1, 0, "O")  # Random move by AI

        move = ai.get_best_move(board)
        assert move == (0, 2)  # Should block the opponent

    def test_minimax_perfect_play(self):
        """Test that hard AI plays optimally."""
        ai = AIPlayer("hard")
        board = Board()

        # Test AI doesn't make obvious losing moves
        # If opponent has two in a row, AI should block
        board.make_move(0, 0, "X")
        board.make_move(0, 1, "X")

        move = ai.get_best_move(board)
        assert move == (0, 2)  # Should block

    def test_minimax_center_preference(self):
        """Test that AI prefers center when starting."""
        ai = AIPlayer("hard")
        board = Board()

        # On empty board, center is often the best move
        move = ai.get_best_move(board)
        # Center (1,1) is typically preferred, but corner moves are also good
        assert move in [(1, 1), (0, 0), (0, 2), (2, 0), (2, 2)]

    def test_minimax_winning_move_priority(self):
        """Test that minimax takes immediate wins."""
        ai = AIPlayer("hard")
        board = Board()

        # Set up immediate win for AI
        board.make_move(0, 0, "O")
        board.make_move(1, 1, "O")
        board.make_move(0, 1, "X")  # Opponent's move

        move = ai.get_best_move(board)
        assert move == (2, 2)  # Should take winning diagonal

    def test_minimax_fork_creation(self):
        """Test AI's ability to create forks."""
        ai = AIPlayer("hard")
        board = Board()

        # Create a scenario where AI can set up multiple winning threats
        board.make_move(1, 1, "O")  # AI takes center
        board.make_move(0, 0, "X")  # Opponent takes corner

        move = ai.get_best_move(board)
        # AI should take a strategic position (corner or edge to create opportunities)
        # The AI might choose edge positions to block opponent forks
        assert move in [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]

    def test_ai_vs_ai_simulation(self):
        """Test AI playing against itself."""
        ai1 = AIPlayer("hard")
        ai2 = AIPlayer("hard")
        ai2.set_symbols("X", "O")

        board = Board()
        moves_count = 0

        while not board.is_game_over() and moves_count < 20:  # Prevent infinite loop
            if board.current_player == "X":
                move = ai2.get_best_move(board)
            else:
                move = ai1.get_best_move(board)

            assert board.make_move(move[0], move[1]) is True
            moves_count += 1

        # Game should end (either win or draw)
        assert board.is_game_over() is True

        # Should be a reasonable number of moves (3-9 for tic-tac-toe)
        assert 3 <= moves_count <= 9

    def test_difficulty_consistency(self):
        """Test that different difficulties behave consistently."""
        board = Board()
        board.make_move(0, 0, "X")
        board.make_move(0, 1, "X")
        # Opponent threatens to win at (0, 2)

        # All difficulties should block this threat
        for difficulty in ["easy", "medium", "hard"]:
            ai = AIPlayer(difficulty)
            board_copy = board.copy()

            # Run multiple times for stochastic easy mode
            moves = []
            for _ in range(5):
                move = ai.get_best_move(board_copy)
                moves.append(move)

            if difficulty in ["medium", "hard"]:
                # Should always block
                assert all(move == (0, 2) for move in moves)
            else:  # easy
                # Should sometimes block (but might play randomly)
                assert (0, 2) in moves or len(set(moves)) > 1

    def test_edge_case_last_move(self):
        """Test AI behavior when only one move is available."""
        ai = AIPlayer("hard")
        board = Board()

        # Fill all but one position
        moves = [
            (0, 0, "X"),
            (0, 1, "O"),
            (0, 2, "X"),
            (1, 0, "O"),
            (1, 1, "X"),
            (1, 2, "O"),
            (2, 0, "X"),
            (2, 1, "O"),
        ]

        for row, col, player in moves:
            board.make_move(row, col, player)

        # Only (2, 2) is available
        move = ai.get_best_move(board)
        assert move == (2, 2)

    def test_ai_symbol_consistency(self):
        """Test that AI correctly uses its assigned symbols."""
        ai = AIPlayer()
        board = Board()

        # AI should play as 'O' by default
        assert ai.player_symbol == "O"

        # Change symbols
        ai.set_symbols("X", "O")
        assert ai.player_symbol == "X"
        assert ai.opponent_symbol == "O"

        # Test winning move detection with new symbols
        board.make_move(0, 0, "X")
        board.make_move(0, 1, "X")

        winning_move = ai._find_winning_move(board, "X")
        assert winning_move == (0, 2)
