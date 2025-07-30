"""Main entry point for the topl CLI.

This module provides the Fire-based command-line interface that matches
the functionality of the original resolve_toml.py script.

# this_file: src/topl/__main__.py

Usage:
    python -m topl path/to/file.toml --verbose --param1=value1 --param2=value2
    topl path/to/file.toml --param1=value1 --param2=value2
"""

from __future__ import annotations

import fire

from .cli import main_cli


def main() -> None:
    """Entry point for the CLI using Fire.

    This function is called when running:
    - python -m topl
    - topl (via console script)

    Fire automatically converts function arguments to CLI arguments.
    """
    fire.Fire(main_cli)


if __name__ == "__main__":  # pragma: no cover
    main()
