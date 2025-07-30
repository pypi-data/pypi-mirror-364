"""Custom exceptions for the topl package.

# this_file: src/topl/exceptions.py
"""

from __future__ import annotations


class TOPLError(Exception):
    """Base exception for all topl-related errors."""


class CircularReferenceError(TOPLError):
    """Raised when circular placeholder references are detected."""


class PlaceholderResolutionError(TOPLError):
    """Raised when placeholder resolution fails."""


class InvalidTOMLError(TOPLError):
    """Raised when TOML parsing fails."""


class FileNotFoundError(TOPLError):
    """Raised when a TOML file cannot be found."""
