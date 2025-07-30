"""Tic-Tac-Toe game package."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .ai import AIPlayer
from .board import Board

__all__ = ["Board", "AIPlayer"]
