"""
Semantic EQ Client

Python client for the Semantic Equivalence API - compress prompts for semantic equivalence.
"""

__version__ = "1.0.5"

from .client import SemanticEQ, SemanticEQError, CompressionError
from .models import CompressionResult

__all__ = [
    "SemanticEQ",
    "SemanticEQError",
    "CompressionError",
    "CompressionResult"
]