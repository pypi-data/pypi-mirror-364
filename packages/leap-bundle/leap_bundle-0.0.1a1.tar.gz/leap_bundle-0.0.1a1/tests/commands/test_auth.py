"""Tests for authentication commands."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from leap_bundle.main import app

runner = CliRunner()


def test_login_success() -> None:
    """Test successful login command with valid API token."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"

        with patch(
            "leap_bundle.utils.config.get_config_file_path", return_value=config_path
        ), patch("leap_bundle.commands.auth.validate_api_token", return_value=True):
            result = runner.invoke(app, ["login", "leap_test_token_123456789"])

        assert result.exit_code == 0
        assert "Successfully logged in" in result.stdout
        assert config_path.exists()


def test_login_invalid_token() -> None:
    """Test login command with invalid API token."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"

        with patch(
            "leap_bundle.utils.config.get_config_file_path", return_value=config_path
        ), patch("leap_bundle.commands.auth.validate_api_token", return_value=False):
            result = runner.invoke(app, ["login", "invalid_token"])

        assert result.exit_code == 1
        assert "Invalid API token" in result.stdout
        assert not config_path.exists()


def test_login_already_logged_in() -> None:
    """Test login command when already logged in."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"
        config_path.write_text("api_token: existing-token\n")

        with patch(
            "leap_bundle.utils.config.get_config_file_path", return_value=config_path
        ):
            result = runner.invoke(app, ["login", "new-token"])

        assert result.exit_code == 0
        assert "already logged in" in result.stdout


def test_login_validation_error() -> None:
    """Test login command when validation service is unavailable."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"

        with patch(
            "leap_bundle.utils.config.get_config_file_path", return_value=config_path
        ), patch("leap_bundle.commands.auth.validate_api_token", return_value=False):
            result = runner.invoke(app, ["login", "test_token"])

        assert result.exit_code == 1
        assert "Invalid API token" in result.stdout
        assert not config_path.exists()


def test_login_missing_token() -> None:
    """Test login command without token argument."""
    result = runner.invoke(app, ["login"])
    assert result.exit_code != 0
    assert "Missing argument 'API_TOKEN'" in result.output


def test_logout_success() -> None:
    """Test successful logout command."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"
        config_path.write_text("api_token: test-token\n")

        with patch(
            "leap_bundle.utils.config.get_config_file_path", return_value=config_path
        ):
            result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert "Successfully logged out" in result.stdout
        assert config_path.exists()

        content = config_path.read_text()
        assert "api_token" not in content


def test_logout_not_logged_in() -> None:
    """Test logout command when not logged in."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"

        with patch(
            "leap_bundle.utils.config.get_config_file_path", return_value=config_path
        ):
            result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert "not currently logged in" in result.stdout


def test_logout_preserves_config_file() -> None:
    """Test logout preserves config file with other settings."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / ".liquid-leap"
        config_path.write_text(
            "api_token: test-token\nserver_url: https://custom.server.com\n"
        )

        with patch(
            "leap_bundle.utils.config.get_config_file_path", return_value=config_path
        ):
            result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert "Successfully logged out" in result.stdout
        assert config_path.exists()

        content = config_path.read_text()
        assert "api_token" not in content
        assert "server_url: https://custom.server.com" in content
