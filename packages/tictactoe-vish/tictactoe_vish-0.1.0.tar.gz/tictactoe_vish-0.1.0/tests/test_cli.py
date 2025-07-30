"""Unit tests for the CLI interface."""

import io
from unittest.mock import MagicMock, patch

import pytest

from src.tictactoe.board import Board
from src.tictactoe.cli import CLI


class TestCLI:
    """Test cases for the CLI class."""

    def test_cli_initialization(self):
        """Test CLI initialization."""
        cli = CLI()
        assert isinstance(cli.board, Board)
        assert cli.board.current_player == "X"

    @patch("builtins.input", return_value="1,1")
    def test_get_user_move_valid(self, mock_input):
        """Test getting valid user move."""
        cli = CLI()
        move = cli.get_user_move()
        assert move == (1, 1)

    @patch("builtins.input", side_effect=["invalid", "1,1"])
    def test_get_user_move_invalid_then_valid(self, mock_input):
        """Test handling invalid input then valid input."""
        cli = CLI()
        with patch("sys.stdout", new_callable=io.StringIO):
            move = cli.get_user_move()
        assert move == (1, 1)

    @patch("builtins.input", side_effect=["1", "1,1"])
    def test_get_user_move_missing_comma(self, mock_input):
        """Test handling input without comma."""
        cli = CLI()
        with patch("sys.stdout", new_callable=io.StringIO):
            move = cli.get_user_move()
        assert move == (1, 1)

    @patch("builtins.input", side_effect=["-1,0", "1,1"])
    def test_get_user_move_out_of_bounds(self, mock_input):
        """Test handling out of bounds input."""
        cli = CLI()
        with patch("sys.stdout", new_callable=io.StringIO):
            move = cli.get_user_move()
        assert move == (1, 1)

    @patch("builtins.input", side_effect=["0,0", "0,0", "1,1"])
    def test_get_user_move_occupied_position(self, mock_input):
        """Test handling move to occupied position."""
        cli = CLI()
        cli.board.make_move(0, 0, "X")  # Occupy position first

        with patch("sys.stdout", new_callable=io.StringIO):
            move = cli.get_user_move()
        assert move == (1, 1)

    def test_display_board(self):
        """Test board display functionality."""
        cli = CLI()
        cli.board.make_move(0, 0, "X")
        cli.board.make_move(1, 1, "O")

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cli.display_board()
            output = mock_stdout.getvalue()

        assert "Current board:" in output
        assert "X" in output
        assert "O" in output

    @patch("builtins.input", side_effect=["0,0", "0,1", "1,0", "1,1", "2,0"])
    def test_play_human_vs_human_x_wins(self, mock_input):
        """Test human vs human game where X wins."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cli.play_human_vs_human()
            output = mock_stdout.getvalue()

        assert "Player X wins!" in output

    @patch("builtins.input", side_effect=["0,0", "0,1", "1,1", "2,2"])
    def test_play_human_vs_ai(self, mock_input):
        """Test human vs AI game."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cli.play_human_vs_ai()
            output = mock_stdout.getvalue()

        # Game should complete
        assert "Human vs AI" in output
        assert "wins!" in output or "tie!" in output

    def test_show_game_result_winner(self):
        """Test showing game result when there's a winner."""
        cli = CLI()
        cli.board.make_move(0, 0, "X")
        cli.board.make_move(0, 1, "X")
        cli.board.make_move(0, 2, "X")

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cli.show_game_result()
            output = mock_stdout.getvalue()

        assert "Player X wins!" in output

    def test_show_game_result_tie(self):
        """Test showing game result when it's a tie."""
        cli = CLI()
        # Create a tie game (no winner, board full)
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
            cli.board.make_move(row, col, player)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cli.show_game_result()
            output = mock_stdout.getvalue()

        assert "It's a tie!" in output

    @patch("builtins.input", return_value="1")
    def test_show_menu_choice_1(self, mock_input):
        """Test menu choice 1."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO):
            choice = cli.show_menu()

        assert choice == 1

    @patch("builtins.input", return_value="2")
    def test_show_menu_choice_2(self, mock_input):
        """Test menu choice 2."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO):
            choice = cli.show_menu()

        assert choice == 2

    @patch("builtins.input", return_value="3")
    def test_show_menu_choice_3(self, mock_input):
        """Test menu choice 3."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO):
            choice = cli.show_menu()

        assert choice == 3

    @patch("builtins.input", side_effect=["invalid", "1"])
    def test_show_menu_invalid_then_valid(self, mock_input):
        """Test menu with invalid input then valid input."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO):
            choice = cli.show_menu()

        assert choice == 1

    @patch("builtins.input", side_effect=["1", "0,0", "0,1", "1,0", "1,1", "2,0", "n"])
    def test_run_human_vs_human_one_game(self, mock_input):
        """Test running one human vs human game."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO):
            cli.run()

    @patch("builtins.input", side_effect=["2", "0,0", "0,1", "1,1", "2,2", "n"])
    def test_run_human_vs_ai_one_game(self, mock_input):
        """Test running one human vs AI game."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO):
            cli.run()

    @patch("builtins.input", return_value="3")
    def test_run_quit_immediately(self, mock_input):
        """Test quitting immediately from menu."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cli.run()
            output = mock_stdout.getvalue()

        assert "Thanks for playing! Goodbye!" in output

    @patch(
        "builtins.input", side_effect=["1", "0,0", "0,1", "1,0", "1,1", "2,0", "y", "3"]
    )
    def test_run_play_again(self, mock_input):
        """Test playing again after a game."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO):
            cli.run()

    def test_keyboard_interrupt_get_user_move(self):
        """Test keyboard interrupt during user move input."""
        cli = CLI()

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with pytest.raises(SystemExit):
                cli.get_user_move()

    def test_keyboard_interrupt_show_menu(self):
        """Test keyboard interrupt during menu selection."""
        cli = CLI()

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with patch("sys.stdout", new_callable=io.StringIO):
                with pytest.raises(SystemExit):
                    cli.show_menu()

    def test_main_function(self):
        """Test main function."""
        from src.tictactoe.cli import main

        with patch("src.tictactoe.cli.CLI") as mock_cli_class, \
             patch("sys.argv", ["tictactoe"]):
            mock_cli_instance = MagicMock()
            mock_cli_class.return_value = mock_cli_instance

            main()

            mock_cli_class.assert_called_once()
            mock_cli_instance.run.assert_called_once()

    def test_main_function_keyboard_interrupt(self):
        """Test main function with keyboard interrupt."""
        from src.tictactoe.cli import main

        with patch("src.tictactoe.cli.CLI") as mock_cli_class:
            mock_cli_instance = MagicMock()
            mock_cli_instance.run.side_effect = KeyboardInterrupt
            mock_cli_class.return_value = mock_cli_instance

            with pytest.raises(SystemExit):
                main()

    def test_ai_move_display(self):
        """Test that AI moves are properly displayed."""
        cli = CLI()
        cli.board.current_player = "O"  # AI's turn

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            with patch("builtins.input", side_effect=["0,0"]):  # Human move
                # Simulate one turn of human vs AI
                if cli.board.current_player == "X":
                    row, col = cli.get_user_move()
                    cli.board.make_move(row, col)
                else:
                    print("AI is thinking...")
                    row, col = cli.ai_player.get_best_move(cli.board)
                    print(f"AI plays: {row},{col}")
                    cli.board.make_move(row, col)

            output = mock_stdout.getvalue()

        assert "AI is thinking..." in output
        assert "AI plays:" in output

    def test_board_reset_between_games(self):
        """Test that board is reset between games."""
        cli = CLI()

        # Make some moves
        cli.board.make_move(0, 0, "X")
        cli.board.make_move(1, 1, "O")

        # Simulate starting a new game
        cli.board.reset()

        # Board should be empty
        assert cli.board.grid == [[None, None, None] for _ in range(3)]
        assert cli.board.current_player == "X"

    @patch("builtins.input", side_effect=["0,0", "0,1", "1,0", "1,1", "2,0"])
    def test_complete_game_flow(self, mock_input):
        """Test a complete game from start to finish."""
        cli = CLI()

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cli.play_human_vs_human()
            output = mock_stdout.getvalue()

        # Game should be complete
        assert cli.board.is_game_over()
        assert "wins!" in output or "tie!" in output

        # Check that board shows final state
        assert "Current board:" in output
