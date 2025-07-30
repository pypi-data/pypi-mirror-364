"""Tests for the main CLI commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from clfits import __version__
from clfits.io import read_header, write_header
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

        result = runner.invoke(app, args)
        assert result.exit_code == 1
        assert "Error: FITS file not found" in result.stderr


def test_main_entrypoint(tmp_path: Path) -> None:
    """Test the main entrypoint."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["view", str(fits_file)])
    assert result.exit_code == 0


def test_set_keyword_in_table_hdu_by_index(tmp_path: Path):
    """Test setting a keyword in a table HDU by index."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    result = runner.invoke(app, ["set", str(fits_file), "NEW_KW", "new_value", "--hdu", "1"])
    assert result.exit_code == 0
    assert "Success: Set 'NEW_KW' to 'new_value'" in result.stdout

    # Verify the change
    header = read_header(fits_file, hdu=1)
    assert header["NEW_KW"] == "new_value"


def test_set_keyword_in_table_hdu_by_name(tmp_path: Path):
    """Test setting a keyword in a table HDU by name."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    result = runner.invoke(app, ["set", str(fits_file), "NEW_KW", "new_value", "--hdu", "OBSERVATIONS"])
    assert result.exit_code == 0
    assert "Success: Set 'NEW_KW' to 'new_value'" in result.stdout

    # Verify the change
    header = read_header(fits_file, hdu="OBSERVATIONS")
    assert header["NEW_KW"] == "new_value"


def test_delete_keyword_in_table_hdu(tmp_path: Path):
    """Test deleting a keyword from a table HDU."""
    fits_file = create_test_fits(tmp_path, with_table=True)

    # Get the header, add a keyword to it, and write it back
    header = read_header(fits_file, hdu=1)
    header["DEL_KW"] = "to be deleted"
    write_header(fits_file, header, hdu=1)

    # Now, run the 'del' command
    result = runner.invoke(app, ["del", str(fits_file), "DEL_KW", "--hdu", "1"])
    assert result.exit_code == 0
    assert "Success: Deleted 'DEL_KW'" in result.stdout

    # Verify the keyword is gone
    final_header = read_header(fits_file, hdu=1)
    assert "DEL_KW" not in final_header


def test_command_fails_with_invalid_hdu(tmp_path: Path):
    """Test that commands fail gracefully with an invalid HDU."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    result = runner.invoke(app, ["view", str(fits_file), "--hdu", "99"])
    assert result.exit_code == 1
    assert "Error: HDU '99' not found" in result.stderr
