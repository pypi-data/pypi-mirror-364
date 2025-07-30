# topl

TOML extended with placeholders

---

#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["python-box", "rich", "fire"]
# ///
# this_file: resolve_toml.py
"""
resolve_toml.py
===============

Resolve double‑curly‑brace placeholders in a TOML file **in two phases**:

1. **Internal phase** – placeholders that reference keys *inside* the same
   TOML structure are substituted first (e.g. ``{{dict2.key2}}``).
2. **External phase** – any *remaining* placeholders are substituted with
   user‑supplied parameters (e.g. ``external1="foo"``).
3. **Warning phase** – unresolved placeholders are left intact **and** a
   warning is emitted.

The script purposefully performs *minimal* work: it does **not** try to
re‑order keys, merge files, or perform type conversions beyond ``str``;
it only “does what it says on the tin”.

---------------------------------------------------------------------------
Usage (CLI)
-----------

./resolve_toml.py path/to/file.toml --external external1="bar" external2="baz"

The CLI is provided by fire; every keyword argument after the filename is
treated as an external parameter.

⸻

Why Box?

Box gives intuitive dotted access (cfg.dict2.key2) while still behaving
like a plain dict for serialization.

“””

from future import annotations

import logging
import re
import sys
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

import tomllib  # Python 3.11+
from box import Box
import fire
from rich.console import Console
from rich.logging import RichHandler

—————————————————————————

Constants & regexes

_PLACEHOLDER_RE = re.compile(r”{{([^{}]+)}}”)
_MAX_INTERNAL_PASSES = 10  # avoid infinite loops on circular refs

—————————————————————————

Logging setup – colourised & optionally verbose

def _configure_logging(verbose: bool = False) -> None:
level = logging.DEBUG if verbose else logging.INFO
logging.basicConfig(
level=level,
format=”%(message)s”,
handlers=[RichHandler(rich_tracebacks=True, console=Console(stderr=True))],
)

logger = logging.getLogger(name)

—————————————————————————

Low‑level helpers

def _get_by_path(box: Box, dotted_path: str) -> Any:
“””
Return value at dotted_path or None if the path is invalid.

``dotted_path`` follows Box semantics: ``"foo.bar.baz"``.
"""
current = box
for part in dotted_path.split("."):
    if not isinstance(current, Mapping) or part not in current:
        return None
    current = current[part]
return current

def _resolve_internal_once(s: str, root: Box) -> str:
“””
Replace one pass of internal placeholders in s.

A placeholder is internal if the path exists in *root*.
"""
def repl(match: re.Match[str]) -> str:
    path = match.group(1).strip()
    value = _get_by_path(root, path)
    return str(value) if value is not None else match.group(0)

return _PLACEHOLDER_RE.sub(repl, s)

def _resolve_external(s: str, params: Mapping[str, str]) -> str:
“””
Replace external placeholders using str.format_map.

We temporarily convert ``{{name}}`` → ``{name}`` then format.
Missing keys are left untouched.
"""

class _SafeDict(dict):  # noqa: D401
    """dict that leaves unknown placeholders unchanged."""

    def __missing__(self, key: str) -> str:  # noqa: D401
        return f"{{{{{key}}}}}"

if not params:
    return s

# Convert `{{name}}` → `{name}`
tmp = _PLACEHOLDER_RE.sub(lambda m: "{" + m.group(1).strip() + "}", s)
return tmp.format_map(_SafeDict(params))

def _iter_box_strings(box: Box) -> tuple[tuple[str, Box], …]:
“””
Yield (key, parent_box) pairs for every string leaf in box.

We return both key *and* the parent so we can assign new values in‑place.
"""
results: list[tuple[str, Box]] = []
for key, val in box.items():
    if isinstance(val, str):
        results.append((key, box))
    elif isinstance(val, Mapping):
        results.extend(_iter_box_strings(val))  # type: ignore[arg-type]
return tuple(results)

—————————————————————————

Public API

def resolve_placeholders(data: Mapping[str, Any], **params: str) -> Box:
“””
Resolve placeholders inside data in‑place and return a new Box.

Parameters
----------
data:
    Mapping returned by ``tomllib.load``.
**params:
    External parameters used during the *external* phase.

Returns
-------
Box
    The resolved configuration object.
"""
cfg = Box(data, default_box=True, default_box_attr=None)

# -- Phase 1: internal substitutions (multiple passes) ------------------ #
for i in range(_MAX_INTERNAL_PASSES):
    changed = False
    for key, parent in _iter_box_strings(cfg):
        original = parent[key]
        resolved = _resolve_internal_once(original, cfg)
        if original != resolved:
            parent[key] = resolved
            changed = True
    if not changed:
        logger.debug("Internal resolution stabilised after %s passes", i + 1)
        break
else:  # pragma: no cover
    logger.warning(
        "Reached maximum internal passes (%s). "
        "Possible circular placeholder references?",
        _MAX_INTERNAL_PASSES,
    )

# -- Phase 2: external substitutions ----------------------------------- #
for key, parent in _iter_box_strings(cfg):
    parent[key] = _resolve_external(parent[key], MappingProxyType(params))

# -- Phase 3: warn about leftovers ------------------------------------- #
leftovers: list[str] = []
for key, parent in _iter_box_strings(cfg):
    for match in _PLACEHOLDER_RE.finditer(parent[key]):
        leftovers.append(match.group(0))
if leftovers:
    unique = sorted(set(leftovers))
    logger.warning(
        "Could not resolve %s placeholder(s): %s",
        len(unique),
        ", ".join(unique),
    )

return cfg

—————————————————————————

CLI entry‑point

def main(path: str, verbose: bool = False, **params: str) -> None:  # noqa: D401
“””
Read path (TOML), resolve placeholders, and pretty‑print the result.

Any ``key=value`` arguments after *path* are considered external params.
"""
_configure_logging(verbose)

toml_path = Path(path).expanduser()
try:
    data = toml_path.read_bytes()
except FileNotFoundError:
    logger.error("TOML file %s not found", toml_path)
    sys.exit(1)

config = resolve_placeholders(tomllib.loads(data.decode()), **params)
Console().print(config.to_dict())

if name == “main”:  # pragma: no cover
fire.Fire(main)

---

### How this fulfils the brief 📝

1. **Two‑phase resolution**:  
   *Internal* references are substituted first; only the unresolved placeholders
   are then offered to external parameters via ``str.format_map``.
2. **Warnings**: Any placeholders still unreplaced are logged **once** –
   exactly as requested.
3. **Box integration**: The Toml structure is returned as a `Box`, so callers
   keep dotted access for further processing.
4. **CLI optionality**: Fire provides a one‑liner interface but is *not*
   mandatory for library use.
5. **Safety**: Circular references are detected via a pass‑count limit and will
   not hang the program.

Feel free to drop the CLI bits if you only need a function – everything is
modular.
