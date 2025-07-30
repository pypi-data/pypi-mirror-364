"""Pytest configuration and fixtures for topl tests.

# this_file: tests/conftest.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def sample_toml_data() -> dict[str, Any]:
    """Simple TOML data for testing."""
    return {
        "name": "world",
        "greeting": "Hello {{name}}!",
        "nested": {"value": "test", "message": "This is {{nested.value}}"},
    }


@pytest.fixture
def circular_ref_data() -> dict[str, Any]:
    """TOML data with circular references."""
    return {"a": "{{b}}", "b": "{{c}}", "c": "{{a}}"}


@pytest.fixture
def external_placeholder_data() -> dict[str, Any]:
    """TOML data requiring external parameters."""
    return {"message": "Hello {{external_name}}!", "path": "/home/{{user}}/{{project}}"}


@pytest.fixture
def mixed_placeholder_data() -> dict[str, Any]:
    """TOML data with both internal and external placeholders."""
    return {
        "base_name": "myapp",
        "version": "1.0.0",
        "full_name": "{{base_name}}-{{version}}",
        "deployment_path": "/opt/{{environment}}/{{full_name}}",
    }


@pytest.fixture
def temp_toml_file(tmp_path: Path) -> Path:
    """Create a temporary TOML file."""
    toml_file = tmp_path / "test.toml"
    toml_content = """
name = "world"
greeting = "Hello {{name}}!"

[nested]
value = "test"
message = "This is {{nested.value}}"
"""
    toml_file.write_text(toml_content)
    return toml_file


@pytest.fixture
def invalid_toml_file(tmp_path: Path) -> Path:
    """Create a temporary invalid TOML file."""
    toml_file = tmp_path / "invalid.toml"
    toml_content = """
name = "world
greeting = "Hello {{name}}!"  # Missing closing quote
"""
    toml_file.write_text(toml_content)
    return toml_file
