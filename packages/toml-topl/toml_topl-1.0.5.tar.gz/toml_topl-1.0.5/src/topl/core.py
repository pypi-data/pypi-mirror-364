"""Core functionality for TOML placeholder resolution.

# this_file: src/topl/core.py
"""

from __future__ import annotations

import logging
from types import MappingProxyType
from typing import Any

from box import Box

from .constants import MAX_INTERNAL_PASSES, PLACEHOLDER_PATTERN
from .exceptions import CircularReferenceError
from .types import ConfigMapping
from .utils import iter_box_strings, resolve_external, resolve_internal_once

logger = logging.getLogger(__name__)


class TOPLConfig:
    """Wrapper class for resolved TOML configuration with placeholder support.

    This class provides a convenient interface for working with resolved
    configuration data, maintaining the Box functionality while adding
    metadata about the resolution process.
    """

    def __init__(self, data: Box, unresolved_placeholders: list[str] | None = None):
        """Initialize with resolved data and optional unresolved placeholders.

        Args:
            data: Resolved configuration data as Box
            unresolved_placeholders: List of placeholders that couldn't be resolved
        """
        self._data = data
        self._unresolved = unresolved_placeholders or []

    @property
    def data(self) -> Box:
        """Access the underlying Box data."""
        return self._data

    @property
    def unresolved_placeholders(self) -> list[str]:
        """List of placeholders that couldn't be resolved."""
        return self._unresolved.copy()

    @property
    def has_unresolved(self) -> bool:
        """Check if there are any unresolved placeholders."""
        return len(self._unresolved) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to plain dictionary."""
        return self._data.to_dict()

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying Box."""
        return getattr(self._data, name)

    def __getitem__(self, key: str) -> Any:
        """Delegate item access to the underlying Box."""
        return self._data[key]

    def __repr__(self) -> str:
        """String representation showing unresolved count."""
        unresolved_info = (
            f", {len(self._unresolved)} unresolved" if self._unresolved else ""
        )
        return f"TOPLConfig({self._data}{unresolved_info})"


def resolve_placeholders(data: ConfigMapping, **params: str) -> TOPLConfig:
    """Resolve placeholders inside data and return a TOPLConfig instance.

    This function performs two-phase placeholder resolution:
    1. Internal phase: Resolves placeholders that reference keys within the same data
    2. External phase: Resolves remaining placeholders using provided parameters
    3. Warning phase: Collects any unresolved placeholders for reporting

    Args:
        data: Mapping returned by tomllib.load or similar
        **params: External parameters used during the external phase

    Returns:
        TOPLConfig instance with resolved data and metadata

    Raises:
        CircularReferenceError: If circular references are detected during internal resolution

    Examples:
        >>> import tomllib
        >>> toml_data = tomllib.loads('name = "world"\\ngreeting = "Hello {{name}}!"')
        >>> config = resolve_placeholders(toml_data)
        >>> config.greeting
        'Hello world!'

        >>> config_with_external = resolve_placeholders(
        ...     tomllib.loads('message = "Hello {{external_name}}!"'),
        ...     external_name="Alice"
        ... )
        >>> config_with_external.message
        'Hello Alice!'
    """
    # Create Box with safe attribute access and deep copy to prevent mutations
    import copy
    cfg = Box(copy.deepcopy(data), default_box=True, default_box_attr=None)

    # Phase 1: Internal substitutions (multiple passes)
    logger.debug("Starting internal placeholder resolution")

    for i in range(MAX_INTERNAL_PASSES):
        changed = False
        for key, parent in iter_box_strings(cfg):
            original = parent[key]
            resolved = resolve_internal_once(original, cfg)
            if original != resolved:
                parent[key] = resolved
                changed = True
                logger.debug(f"Resolved internal: {original} -> {resolved}")

        if not changed:
            logger.debug(f"Internal resolution stabilized after {i + 1} passes")
            break
    else:
        # This indicates circular references or very deep nesting
        raise CircularReferenceError(
            f"Reached maximum internal passes ({MAX_INTERNAL_PASSES}). "
            "Circular placeholder references detected or resolution is too complex."
        )

    # Phase 2: External substitutions
    logger.debug(
        f"Starting external placeholder resolution with {len(params)} parameters"
    )
    for key, parent in iter_box_strings(cfg):
        original = parent[key]
        resolved = resolve_external(original, MappingProxyType(params))
        if original != resolved:
            parent[key] = resolved
            logger.debug(f"Resolved external: {original} -> {resolved}")

    # Phase 3: Collect unresolved placeholders
    unresolved_placeholders: list[str] = []
    for key, parent in iter_box_strings(cfg):
        unresolved_placeholders.extend(
            match.group(0)
            for match in PLACEHOLDER_PATTERN.finditer(parent[key])
        )

    if unresolved_placeholders:
        unique_unresolved = sorted(set(unresolved_placeholders))
        logger.warning(
            f"Could not resolve {len(unique_unresolved)} placeholder(s): "
            f"{', '.join(unique_unresolved)}"
        )
    else:
        logger.debug("All placeholders resolved successfully")

    return TOPLConfig(cfg, unique_unresolved if unresolved_placeholders else None)
