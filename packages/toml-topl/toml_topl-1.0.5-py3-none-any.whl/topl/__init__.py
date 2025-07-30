"""TOPL: TOML Extended with Placeholders.

A Python library for resolving placeholders in TOML configuration files
using a two-phase approach: internal references first, then external parameters.

# this_file: src/topl/__init__.py

Examples:
    >>> import tomllib
    >>> from topl import resolve_placeholders
    >>>
    >>> # Basic usage with internal references
    >>> toml_data = tomllib.loads('''
    ... name = "world"
    ... greeting = "Hello {{name}}!"
    ... ''')
    >>> config = resolve_placeholders(toml_data)
    >>> print(config.greeting)  # "Hello world!"

    >>> # Usage with external parameters
    >>> config = resolve_placeholders(toml_data, external_param="value")
"""

from __future__ import annotations

try:
    from ._version import __version__
except ImportError:
    # Fallback version when not installed via pip
    __version__ = "0.0.0+unknown"

# Core functionality exports
from .core import TOPLConfig, resolve_placeholders

# Exception exports for error handling
from .exceptions import (
    CircularReferenceError,
    FileNotFoundError,
    InvalidTOMLError,
    PlaceholderResolutionError,
    TOPLError,
)

# Type exports for advanced usage
from .types import ConfigMapping, PlaceholderParams, TOMLData

__all__ = [
    "CircularReferenceError",
    "ConfigMapping",
    "FileNotFoundError",
    "InvalidTOMLError",
    "PlaceholderParams",
    "PlaceholderResolutionError",
    "TOMLData",
    "TOPLConfig",
    "TOPLError",
    "__version__",
    "resolve_placeholders",
]
