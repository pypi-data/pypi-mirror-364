"""Tests for CLI module."""

import pytest
from typer.testing import CliRunner

from lcvtoolbox.cli.main import app


class TestCLI:
    """Test CLI functionality."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "version" in result.stdout.lower()

    def test_demo_command(self, runner):
        """Test demo command."""
        result = runner.invoke(app, ["demo"])
        assert result.exit_code == 0
        # Demo should show some output
        assert len(result.stdout) > 0
