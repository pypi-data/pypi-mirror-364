"""Tests for the search command and related functions."""

from pathlib import Path

from typer.testing import CliRunner

from clfits.main import app
from tests.utils import create_test_fits

runner = CliRunner()


def test_search_by_key(tmp_path: Path):
    """Test searching by keyword pattern."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["search", str(fits_file), "--key", "OBJ*"])
    assert result.exit_code == 0
    assert "OBJECT" in result.stdout
    assert "OBSERVER" not in result.stdout


def test_search_by_value(tmp_path: Path):
    """Test searching by value pattern."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["search", str(fits_file), "--value", "NGC*"])
    assert result.exit_code == 0
    assert "OBJECT" in result.stdout
    assert "OBSERVER" not in result.stdout


def test_search_by_key_and_value(tmp_path: Path):
    """Test searching by both keyword and value."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["search", str(fits_file), "--key", "OBJ*", "--value", "NGC*"])
    assert result.exit_code == 0
    assert "OBJECT" in result.stdout
    assert "NGC 101" in result.stdout


def test_search_case_sensitive(tmp_path: Path):
    """Test case-sensitive search."""
    fits_file = create_test_fits(tmp_path)
    # This should fail because the case is wrong
    result = runner.invoke(app, ["search", str(fits_file), "--key", "object*", "--case-sensitive"])
    assert result.exit_code == 0
    assert "No matching keywords found" in result.stdout
    # This should succeed
    result_correct_case = runner.invoke(app, ["search", str(fits_file), "--key", "OBJECT*", "--case-sensitive"])
    assert result_correct_case.exit_code == 0
    assert "OBJECT" in result_correct_case.stdout


def test_search_no_matches(tmp_path: Path):
    """Test search with no matches."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["search", str(fits_file), "--key", "NONEXISTENT"])
    assert result.exit_code == 0
    assert "No matching keywords found" in result.stdout


def test_search_no_filter_error(tmp_path: Path):
    """Test that at least one filter is required."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["search", str(fits_file)], catch_exceptions=False)
    assert result.exit_code == 1
    assert "Error: At least one of --key or --value must be provided" in result.stdout


def test_search_with_none_value(tmp_path: Path):
    """Test searching a keyword that has a None value."""
    fits_file = create_test_fits(tmp_path)

    # Add a keyword with a None value
    from astropy.io import fits

    with fits.open(fits_file, mode="update") as hdul:
        hdul[0].header["NONE_KW"] = None

    # Search for a value; this should not find the None keyword and not crash
    result = runner.invoke(app, ["search", str(fits_file), "--value", "some_value"])
    assert result.exit_code == 0
    assert "NONE_KW" not in result.stdout
