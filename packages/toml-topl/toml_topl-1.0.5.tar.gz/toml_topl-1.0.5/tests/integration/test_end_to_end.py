"""End-to-end integration tests.

# this_file: tests/integration/test_end_to_end.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class TestCLIIntegration:
    """Integration tests for the CLI interface."""

    def test_cli_via_python_module(self, temp_toml_file):
        """Test running CLI via python -m topl."""
        result = subprocess.run(
            [sys.executable, "-m", "topl", str(temp_toml_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,  # Project root
        )

        assert result.returncode == 0
        assert "Hello world!" in result.stdout

    def test_cli_with_parameters(self, tmp_path):
        """Test CLI with external parameters."""
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('message = "Hello {{name}}!"')

        result = subprocess.run(
            [sys.executable, "-m", "topl", str(toml_file), "--name=Alice"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 0
        assert "Hello Alice!" in result.stdout

    def test_cli_verbose_mode(self, temp_toml_file):
        """Test CLI verbose mode."""
        result = subprocess.run(
            [sys.executable, "-m", "topl", str(temp_toml_file), "--verbose"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 0
        # Should have some stderr output in verbose mode
        assert result.stderr or result.stdout

    def test_cli_error_handling(self, tmp_path):
        """Test CLI error handling for missing files."""
        missing_file = tmp_path / "missing.toml"

        result = subprocess.run(
            [sys.executable, "-m", "topl", str(missing_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 1
        # Check that error message appears in stderr (may be split across lines)
        assert "File error" in result.stderr or "not found" in result.stderr


class TestComplexResolution:
    """Integration tests for complex placeholder resolution scenarios."""

    def test_multi_level_nesting(self, tmp_path):
        """Test deeply nested placeholder resolution."""
        toml_content = """
[database]
host = "localhost"
port = 5432
name = "myapp"

[connection]
url = "postgresql://{{database.host}}:{{database.port}}/{{database.name}}"

[application]
name = "MyApp"
version = "1.0.0"
full_name = "{{application.name}} v{{application.version}}"

[deployment]
environment = "{{env}}"
database_url = "{{connection.url}}"
app_name = "{{application.full_name}}"
"""
        toml_file = tmp_path / "complex.toml"
        toml_file.write_text(toml_content)

        result = subprocess.run(
            [sys.executable, "-m", "topl", str(toml_file), "--env=production"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 0
        output = result.stdout

        # Check resolved values
        assert "postgresql://localhost:5432/myapp" in output
        assert "MyApp v1.0.0" in output
        assert "production" in output

    def test_recursive_resolution(self, tmp_path):
        """Test multi-pass recursive resolution."""
        toml_content = """
base = "app"
version = "1.0"
name = "{{base}}-{{version}}"
full_path = "/opt/{{name}}/bin"
command = "{{full_path}}/{{name}}"
"""
        toml_file = tmp_path / "recursive.toml"
        toml_file.write_text(toml_content)

        result = subprocess.run(
            [sys.executable, "-m", "topl", str(toml_file)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 0
        output = result.stdout

        # Should resolve recursively
        assert "app-1.0" in output
        assert "/opt/app-1.0/bin" in output
        assert "/opt/app-1.0/bin/app-1.0" in output
