"""Resilient Result - Result pattern with @resilient decorators for clean error handling."""

from .result import Result, Ok, Err
from .decorators import resilient

__version__ = "0.1.0"
__all__ = ["Result", "Ok", "Err", "resilient"]