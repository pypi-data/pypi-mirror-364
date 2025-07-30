"""Constants used throughout the topl package.

# this_file: src/topl/constants.py
"""

from __future__ import annotations

import re

# Regex pattern for matching placeholders like {{key.subkey}}
PLACEHOLDER_PATTERN = re.compile(r"{{([^{}]+)}}")

# Maximum number of internal resolution passes to prevent infinite loops
MAX_INTERNAL_PASSES = 10

# Default logging format
DEFAULT_LOG_FORMAT = "%(message)s"
