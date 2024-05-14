from typing import Any, Mapping, TypeVar

from openai import BaseModel

__all__ = ["M", "P"]

M = TypeVar("M", bound=BaseModel)
"""OpenAI model generic"""

P = TypeVar("P", bound=Mapping[str, Any])
"""Partial OpenAI model generic"""
