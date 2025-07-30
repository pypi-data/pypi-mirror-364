"""Command-line interface for topl.

# this_file: src/topl/cli.py
"""

from __future__ import annotations

import logging
import sys
import tomllib
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

from .core import resolve_placeholders
from .exceptions import (
    CircularReferenceError,
    InvalidTOMLError,
    PlaceholderResolutionError,
)
from .exceptions import FileNotFoundError as TOPLFileNotFoundError


def configure_logging(verbose: bool = False) -> None:
    """Configure logging with Rich formatting.

    Args:
        verbose: Enable debug-level logging if True
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, console=Console(stderr=True))],
    )


def load_toml_file(path: Path) -> dict[str, Any]:
    """Load and parse a TOML file.

    Args:
        path: Path to the TOML file

    Returns:
        Parsed TOML data as dictionary

    Raises:
        TOPLFileNotFoundError: If file doesn't exist
        InvalidTOMLError: If TOML parsing fails
    """
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError as e:
        raise TOPLFileNotFoundError(f"TOML file {path} not found") from e
    except tomllib.TOMLDecodeError as e:
        raise InvalidTOMLError(f"Invalid TOML in {path}: {e}") from e


def main_cli(path: str, verbose: bool = False, **params: str) -> None:
    """Main CLI function for processing TOML files with placeholders.

    Args:
        path: Path to the TOML file to process
        verbose: Enable verbose logging
        **params: External parameters for placeholder resolution

    Examples:
        >>> # CLI usage: topl config.toml --verbose --name=world
        >>> main_cli("config.toml", verbose=True, name="world")
    """
    configure_logging(verbose)
    logger = logging.getLogger(__name__)

    # Resolve path
    toml_path = Path(path).expanduser().resolve()
    logger.debug(f"Processing file: {toml_path}")

    try:
        # Load TOML data
        data = load_toml_file(toml_path)
        logger.debug(f"Loaded TOML with {len(data)} top-level keys")

        # Resolve placeholders
        if params:
            logger.debug(f"Using external parameters: {list(params.keys())}")
        config = resolve_placeholders(data, **params)

        # Display results
        console = Console()
        console.print(config.to_dict())

        # Report unresolved placeholders if any
        if config.has_unresolved:
            logger.warning(f"Unresolved placeholders: {config.unresolved_placeholders}")
            sys.exit(1)

    except TOPLFileNotFoundError as e:
        logger.error(f"File error: {e}")
        sys.exit(1)
    except InvalidTOMLError as e:
        logger.error(f"TOML parsing error: {e}")
        sys.exit(1)
    except CircularReferenceError as e:
        logger.error(f"Circular reference detected: {e}")
        sys.exit(1)
    except PlaceholderResolutionError as e:
        logger.error(f"Placeholder resolution failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        sys.exit(1)
