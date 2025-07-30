"""Type definitions for the topl package.

# this_file: src/topl/types.py
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

# Type aliases for better readability
TOMLData = dict[str, Any]
ConfigMapping = Mapping[str, Any]
PlaceholderParams = dict[str, str] | MappingProxyType[str, str]
NestedValue = str | dict[str, Any] | Any
