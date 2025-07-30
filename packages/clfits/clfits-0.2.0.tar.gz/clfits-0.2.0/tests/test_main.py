"""Tests for the main CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from clfits import __version__
from clfits.io import read_header
from clfits.main import app

from .utils import create_test_fits

runner = CliRunner()


def test_version_callback() -> None:
    """Test the version callback."""
    result = runner.invoke(app, ["--version"], catch_exceptions=False)
    assert result.exit_code == 0
    assert f"clfits version: {__version__}" in result.stdout


def test_view_command(tmp_path: Path) -> None:
    """Test the 'view' command."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["view", str(fits_file)])
    assert result.exit_code == 0
    assert "OBJECT  = 'NGC 101'" in result.stdout


def test_get_command(tmp_path: Path) -> None:
    """Test the 'get' command."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["get", str(fits_file), "OBJECT"])
    assert result.exit_code == 0
    assert "NGC 101" in result.stdout

    result_fail = runner.invoke(app, ["get", str(fits_file), "NONEXISTENT"], catch_exceptions=False)
    assert result_fail.exit_code == 1
    assert "Error: Keyword 'NONEXISTENT' not found" in result_fail.stdout


def test_set_command(tmp_path: Path) -> None:
    """Test the 'set' command."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["set", str(fits_file), "OBJECT", "NGC 202"])
    assert result.exit_code == 0
    header = read_header(fits_file)
    assert header["OBJECT"] == "NGC 202"

    result_with_comment = runner.invoke(app, ["set", str(fits_file), "OBSERVER", "Webb", "--comment", "New Telescope"])
    assert result_with_comment.exit_code == 0
    header = read_header(fits_file)
    assert header["OBSERVER"] == "Webb"
    assert header.comments["OBSERVER"] == "New Telescope"


def test_delete_command(tmp_path: Path) -> None:
    """Test the 'delete' command."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["del", str(fits_file), "OBSERVER"])
    assert result.exit_code == 0
    header = read_header(fits_file)
    assert "OBSERVER" not in header

    result_fail = runner.invoke(app, ["del", str(fits_file), "NONEXISTENT"], catch_exceptions=False)
    assert result_fail.exit_code == 0
    assert "Warning: Keyword 'NONEXISTENT' not found" in result_fail.stdout


def test_file_not_found_errors() -> None:
    """Test that commands fail gracefully for non-existent files."""
    for command in ["view", "get", "set", "del"]:
        args = [command, "nonexistent.fits"]
        if command in ["get", "set", "del"]:
            args.append("KEYWORD")
        if command == "set":
            args.append("VALUE")

        result = runner.invoke(app, args, catch_exceptions=False)
        assert result.exit_code == 1
        assert "Error: FITS file not found" in result.stdout


def test_main_entrypoint(tmp_path: Path) -> None:
    """Test the main entrypoint."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["view", str(fits_file)])
    assert result.exit_code == 0
