"""Unit tests for utility functions.

# this_file: tests/unit/test_utils.py
"""

from __future__ import annotations

from box import Box

from topl.utils import (
    get_by_path,
    iter_box_strings,
    resolve_external,
    resolve_internal_once,
)


class TestGetByPath:
    """Tests for the get_by_path utility function."""

    def test_simple_path(self):
        """Test retrieving simple path."""
        data = Box({"a": "value"})
        assert get_by_path(data, "a") == "value"

    def test_nested_path(self):
        """Test retrieving nested path."""
        data = Box({"a": {"b": {"c": "value"}}})
        assert get_by_path(data, "a.b.c") == "value"

    def test_missing_path(self):
        """Test retrieving non-existent path."""
        data = Box({"a": "value"})
        assert get_by_path(data, "missing") is None
        assert get_by_path(data, "a.missing") is None

    def test_partial_path(self):
        """Test path that exists partially."""
        data = Box({"a": {"b": "value"}})
        assert get_by_path(data, "a.b.c") is None

    def test_empty_path(self):
        """Test handling of empty or whitespace-only paths."""
        data = Box({"a": "value"})
        assert get_by_path(data, "") is None
        assert get_by_path(data, "   ") is None
        assert get_by_path(data, "\t") is None
        assert get_by_path(data, "\n") is None


class TestResolveInternalOnce:
    """Tests for the resolve_internal_once function."""

    def test_simple_replacement(self):
        """Test simple placeholder replacement."""
        data = Box({"name": "world"})
        result = resolve_internal_once("Hello {{name}}!", data)
        assert result == "Hello world!"

    def test_nested_replacement(self):
        """Test nested placeholder replacement."""
        data = Box({"user": {"name": "Alice"}})
        result = resolve_internal_once("Hello {{user.name}}!", data)
        assert result == "Hello Alice!"

    def test_missing_placeholder(self):
        """Test placeholder that doesn't exist."""
        data = Box({"name": "world"})
        result = resolve_internal_once("Hello {{missing}}!", data)
        assert result == "Hello {{missing}}!"

    def test_multiple_placeholders(self):
        """Test multiple placeholders in one string."""
        data = Box({"first": "John", "last": "Doe"})
        result = resolve_internal_once("{{first}} {{last}}", data)
        assert result == "John Doe"


class TestResolveExternal:
    """Tests for the resolve_external function."""

    def test_simple_external(self):
        """Test simple external parameter replacement."""
        result = resolve_external("Hello {{name}}!", {"name": "world"})
        assert result == "Hello world!"

    def test_missing_external(self):
        """Test missing external parameter."""
        result = resolve_external("Hello {{missing}}!", {})
        assert result == "Hello {{missing}}!"

    def test_empty_params(self):
        """Test with no external parameters."""
        result = resolve_external("Hello {{name}}!", {})
        assert result == "Hello {{name}}!"

    def test_multiple_external(self):
        """Test multiple external parameters."""
        result = resolve_external(
            "{{greeting}} {{name}}!", {"greeting": "Hi", "name": "Alice"}
        )
        assert result == "Hi Alice!"


class TestIterBoxStrings:
    """Tests for the iter_box_strings function."""

    def test_flat_strings(self):
        """Test iteration over flat string values."""
        data = Box({"a": "text1", "b": "text2", "c": 123})
        results = list(iter_box_strings(data))

        # Should only get string values
        assert len(results) == 2
        keys = [key for key, _ in results]
        assert "a" in keys
        assert "b" in keys

    def test_nested_strings(self):
        """Test iteration over nested string values."""
        data = Box(
            {
                "top": "value1",
                "nested": {"inner": "value2", "deep": {"value": "value3"}},
            }
        )
        results = list(iter_box_strings(data))

        # Should find all string values regardless of nesting
        assert len(results) == 3

    def test_mixed_types(self):
        """Test iteration with mixed value types."""
        data = Box(
            {
                "string": "text",
                "number": 42,
                "boolean": True,
                "nested": {"another_string": "more text", "list": [1, 2, 3]},
            }
        )
        results = list(iter_box_strings(data))

        # Should only find string values
        assert len(results) == 2
        string_values = [parent[key] for key, parent in results]
        assert "text" in string_values
        assert "more text" in string_values

    def test_strings_in_lists(self):
        """Test iteration over strings in lists and tuples."""
        data = Box(
            {
                "items": ["string1", "string2", 123],
                "nested": {
                    "list": ["nested1", {"inner": "nested2"}],
                    "tuple_data": ("tuple1", "tuple2")
                }
            }
        )
        results = list(iter_box_strings(data))

        # Should find all string values including those in lists/tuples
        string_values = []
        for key, parent in results:
            string_values.append(parent[key])

        assert "string1" in string_values
        assert "string2" in string_values
        assert "nested1" in string_values
        assert "nested2" in string_values
        assert "tuple1" in string_values
        assert "tuple2" in string_values
        assert len(results) == 6
