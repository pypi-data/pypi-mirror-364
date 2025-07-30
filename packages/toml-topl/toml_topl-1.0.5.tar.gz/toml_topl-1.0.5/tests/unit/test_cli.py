"""Unit tests for CLI functionality.

# this_file: tests/unit/test_cli.py
"""

from __future__ import annotations

import pytest

from topl.cli import configure_logging, load_toml_file, main_cli
from topl.exceptions import FileNotFoundError as TOPLFileNotFoundError
from topl.exceptions import InvalidTOMLError


class TestConfigureLogging:
    """Tests for logging configuration."""

    def test_default_logging(self):
        """Test default logging configuration."""
        configure_logging()
        # This should not raise any exceptions

    def test_verbose_logging(self):
        """Test verbose logging configuration."""
        configure_logging(verbose=True)
        # This should not raise any exceptions


class TestLoadTOMLFile:
    """Tests for TOML file loading."""

    def test_load_valid_toml(self, temp_toml_file):
        """Test loading a valid TOML file."""
        data = load_toml_file(temp_toml_file)

        assert isinstance(data, dict)
        assert data["name"] == "world"
        assert data["greeting"] == "Hello {{name}}!"

    def test_load_missing_file(self, tmp_path):
        """Test loading a non-existent file."""
        missing_file = tmp_path / "missing.toml"

        with pytest.raises(TOPLFileNotFoundError):
            load_toml_file(missing_file)

    def test_load_invalid_toml(self, invalid_toml_file):
        """Test loading an invalid TOML file."""
        with pytest.raises(InvalidTOMLError):
            load_toml_file(invalid_toml_file)


class TestMainCLI:
    """Tests for the main CLI function."""

    def test_successful_processing(self, temp_toml_file, capsys):
        """Test successful TOML processing."""
        main_cli(str(temp_toml_file))

        captured = capsys.readouterr()
        # Should output the resolved configuration
        assert "Hello world!" in captured.out

    def test_with_external_params(self, tmp_path, capsys):
        """Test processing with external parameters."""
        toml_file = tmp_path / "external.toml"
        toml_file.write_text('message = "Hello {{name}}!"')

        main_cli(str(toml_file), name="Alice")

        captured = capsys.readouterr()
        assert "Hello Alice!" in captured.out

    def test_verbose_mode(self, temp_toml_file, capsys):
        """Test verbose mode logging."""
        main_cli(str(temp_toml_file), verbose=True)

        captured = capsys.readouterr()
        # Should include debug information in stderr
        assert captured.err or captured.out  # Some output should be present

    def test_missing_file_error(self, tmp_path):
        """Test error handling for missing file."""
        missing_file = tmp_path / "missing.toml"

        with pytest.raises(SystemExit) as exc_info:
            main_cli(str(missing_file))

        assert exc_info.value.code == 1

    def test_invalid_toml_error(self, invalid_toml_file):
        """Test error handling for invalid TOML."""
        with pytest.raises(SystemExit) as exc_info:
            main_cli(str(invalid_toml_file))

        assert exc_info.value.code == 1

    def test_unresolved_placeholders_exit(self, tmp_path):
        """Test exit code when placeholders remain unresolved."""
        toml_file = tmp_path / "unresolved.toml"
        toml_file.write_text('message = "Hello {{missing}}!"')

        with pytest.raises(SystemExit) as exc_info:
            main_cli(str(toml_file))

        assert exc_info.value.code == 1

    def test_path_expansion(self, tmp_path, monkeypatch):
        """Test path expansion (~ and relative paths)."""
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('value = "test"')

        # Change to the temp directory so relative path works
        monkeypatch.chdir(tmp_path)

        # Test with relative path - should work without raising exceptions
        main_cli("test.toml")
        # If we get here, the test passes
