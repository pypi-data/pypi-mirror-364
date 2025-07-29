"""
Semantic EQ Data Models

This module defines the data structures for prompt compression requests and responses.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CompressionResult:
    """Result of prompt compression with compressed system and user prompts"""
    system_prompt: str
    user_prompt: str
    original_system_prompt: str
    original_user_prompt: str
    improvement_score: Optional[float] = None