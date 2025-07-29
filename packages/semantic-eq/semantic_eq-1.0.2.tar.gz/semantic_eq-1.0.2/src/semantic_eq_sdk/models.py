"""
Semantic EQ Data Models

This module defines the data structures for prompt optimization requests and responses.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OptimizationResult:
    """Result of a prompt optimization"""
    original_prompt: str
    optimized_prompt: str
    improvement_score: Optional[float] = None