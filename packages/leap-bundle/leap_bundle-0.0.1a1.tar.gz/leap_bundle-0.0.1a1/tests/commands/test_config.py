"""Tests for configuration commands."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from leap_bundle.main import app

runner = CliRunner()


def test_config_set_server() -> None:
    """Test setting server URL."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"

        with patch(
            "leap_bundle.commands.config.get_config_file_path", return_value=config_path
        ):
            result = runner.invoke(
                app, ["config", "--server", "https://custom.server.com"]
            )

        assert result.exit_code == 0
        assert "Server URL set to: https://custom.server.com" in result.stdout


def test_config_show_current_server() -> None:
    """Test showing config file location when no config exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"

        with patch(
            "leap_bundle.commands.config.get_config_file_path", return_value=config_path
        ), patch("leap_bundle.commands.config.load_config", return_value={}):
            result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert f"Config file location: {config_path}" in result.stdout
        assert "No configuration found." in result.stdout


def test_config_show_custom_server() -> None:
    """Test showing config file location and existing configs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"
        config_path.write_text("server_url: https://custom.server.com\n")

        with patch(
            "leap_bundle.commands.config.get_config_file_path", return_value=config_path
        ):
            result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert f"Config file location: {config_path}" in result.stdout
        assert "Current configuration:" in result.stdout
        assert "server_url: https://custom.server.com" in result.stdout
