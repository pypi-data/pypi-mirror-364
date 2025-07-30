# Tic-Tac-Toe Game

[![CI](https://github.com/v-s-v-i-s-h-w-a-s/tic-tac-toe/workflows/CI/badge.svg)](https://github.com/v-s-v-i-s-h-w-a-s/tic-tac-toe/actions)
[![Coverage](https://codecov.io/gh/v-s-v-i-s-h-w-a-s/tic-tac-toe/branch/main/graph/badge.svg)](https://codecov.io/gh/v-s-v-i-s-h-w-a-s/tic-tac-toe)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A well-tested Tic-Tac-Toe game implementation in Python with a CLI interface and AI opponent.

---

## Features

* Interactive command-line interface
* AI opponent with multiple difficulty levels
* Human vs Human gameplay
* Smart AI using minimax algorithm
* Comprehensive test suite with >95% coverage
* Modern Python development setup with pre-commit hooks
* Proper package structure and configuration

---

## Installation

### From PyPI

```bash
pip install tictactoe-vish
```

### Development Installation

```bash
git clone https://github.com/v-s-v-i-s-h-w-a-s/tic-tac-toe.git
cd tic-tac-toe
pip install -e .[dev]
```

---

## Usage

### Command Line Interface

```bash
# Run the game
tictactoe

# Or if installed in development mode
python -m src.tictactoe.cli
```

### As a Library

```python
from tictactoe import Board, AIPlayer

# Create a game
board = Board()
ai = AIPlayer(difficulty="hard")

# Make moves
board.make_move(1, 1)  # Human move to center
ai_move = ai.get_best_move(board)  # AI calculates best move
board.make_move(ai_move[0], ai_move[1])  # AI makes move

# Check game state
if board.check_winner():
    print(f"Winner: {board.check_winner()}")
elif board.is_full():
    print("It's a tie!")
```

---

## Game Rules

* Players take turns placing X's and O's on a 3x3 grid
* First player to get 3 in a row (horizontally, vertically, or diagonally) wins
* If the grid fills up with no winner, it's a tie
* Positions are specified as row,col coordinates (0-2 for each)

---

## AI Difficulty Levels

* **Easy**: Random moves
* **Medium**: Blocks opponent wins and takes available wins
* **Hard**: Uses minimax algorithm for optimal play

---

## Development

### Setup Development Environment

```bash
# Clone and install
git clone https://github.com/v-s-v-i-s-h-w-a-s/tic-tac-toe.git
cd tic-tac-toe
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/tictactoe --cov-report=html

# Run specific test file
pytest tests/test_board.py
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests
pylint src

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## Project Structure

```
tic-tac-toe/
├── .github/workflows/        # CI/CD pipelines
├── src/tictactoe/            # Main package
│   ├── __init__.py           # Package initialization
│   ├── board.py              # Game logic
│   ├── cli.py                # Command-line interface
│   └── ai.py                 # AI implementation
├── tests/                    # Test suite
├── pyproject.toml            # Project configuration
├── .pre-commit-config.yaml   # Code quality hooks
└── README.md                 # This file
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b amazing-feature`)
3. Make your changes
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin amazing-feature`)
7. Open a Pull Request

### Development Guidelines

* Write tests for new features
* Maintain code coverage above 95%
* Follow PEP 8 style guidelines (enforced by black and flake8)
* Add type hints to new functions
* Update documentation as needed

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

* Classic Tic-Tac-Toe game rules
* Minimax algorithm for AI implementation
* Python community for excellent tooling
