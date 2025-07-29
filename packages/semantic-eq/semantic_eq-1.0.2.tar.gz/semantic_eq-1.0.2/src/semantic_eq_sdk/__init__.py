"""
Semantic EQ SDK

Python SDK for the Semantic Equivalence API - optimize prompts for semantic equivalence.
"""

__version__ = "1.0.0"

from .client import SemanticEQClient, SemanticEQError, OptimizationError
from .models import OptimizationResult

__all__ = [
    "SemanticEQClient",
    "SemanticEQError", 
    "OptimizationError",
    "OptimizationResult"
]