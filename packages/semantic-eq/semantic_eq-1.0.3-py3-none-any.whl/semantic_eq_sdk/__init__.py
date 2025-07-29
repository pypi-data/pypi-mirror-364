"""
Semantic EQ SDK

Python SDK for the Semantic Equivalence API - optimize prompts for semantic equivalence.
"""

__version__ = "1.0.1"

from .client import SemanticEQ, SemanticEQError, OptimizationError
from .models import OptimizationResult

__all__ = [
    "SemanticEQ",
    "SemanticEQError",
    "OptimizationError",
    "OptimizationResult"
]