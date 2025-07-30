"""Tests for the main CLI module."""

from typer.testing import CliRunner

from leap_bundle.main import app

runner = CliRunner()


def test_version() -> None:
    """Test version command."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "leap-bundle version" in result.stdout


def test_help() -> None:
    """Test help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "LEAP" in result.stdout


def test_login_command() -> None:
    """Test login command requires token argument."""
    result = runner.invoke(app, ["login"])
    assert result.exit_code != 0
    assert "Missing argument 'API_TOKEN'" in result.output


def test_logout_command() -> None:
    """Test logout command when not logged in."""
    result = runner.invoke(app, ["logout"])
    assert result.exit_code == 0
    assert "not currently logged in" in result.stdout


def test_config_command() -> None:
    """Test config command shows config file location."""
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "Config file location:" in result.stdout
