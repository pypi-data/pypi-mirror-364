"""Tests for the export command and related functions."""

import csv
import json
from pathlib import Path
from typing import Dict, Union

import pytest
import yaml
from typer.testing import CliRunner

from clfits.export import Format, to_csv, to_dict, to_json, to_yaml
from clfits.main import app
from tests.utils import create_test_fits

runner = CliRunner()


@pytest.fixture
def fits_header(tmp_path: Path):
    """Create a FITS file and return its header."""
    fits_file = create_test_fits(tmp_path)
    from astropy.io import fits

    with fits.open(fits_file) as hdul:
        return hdul[0].header


def test_to_dict(fits_header):
    """Test converting a FITS header to a dictionary."""
    header_dict = to_dict(fits_header)
    assert isinstance(header_dict, dict)
    assert header_dict["OBJECT"] == "NGC 101"
    assert header_dict["EXPTIME"] == 300.0


def test_to_json(fits_header):
    """Test converting a FITS header to JSON."""
    json_str = to_json(fits_header)
    data = json.loads(json_str)
    assert data["OBJECT"] == "NGC 101"


def test_to_yaml(fits_header):
    """Test converting a FITS header to YAML."""
    yaml_str = to_yaml(fits_header)
    data = yaml.safe_load(yaml_str)
    assert data["OBJECT"] == "NGC 101"


def test_to_csv(fits_header):
    """Test converting a FITS header to CSV."""
    csv_str = to_csv(fits_header)
    reader = csv.reader(csv_str.splitlines())
    rows = list(reader)
    assert rows[0] == ["keyword", "value", "comment"]
    assert any(row[0] == "OBJECT" and row[1] == "NGC 101" for row in rows)


def test_export_to_stdout(tmp_path: Path):
    """Test exporting to stdout."""
    fits_file = create_test_fits(tmp_path)
    result = runner.invoke(app, ["export", str(fits_file), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["OBJECT"] == "NGC 101"


def test_export_to_file(tmp_path: Path):
    """Test exporting to a file."""
    fits_file = create_test_fits(tmp_path)
    output_file = tmp_path / "header.yaml"
    result = runner.invoke(app, ["export", str(fits_file), "--output", str(output_file)])
    assert result.exit_code == 0
    assert "Success: Header exported" in result.stdout
    with open(output_file) as f:
        data = yaml.safe_load(f)
    assert data["OBJECT"] == "NGC 101"


def test_export_infer_format(tmp_path: Path):
    """Test inferring format from filename."""
    fits_file = create_test_fits(tmp_path)
    output_file = tmp_path / "header.csv"
    result = runner.invoke(app, ["export", str(fits_file), "--output", str(output_file)])
    assert result.exit_code == 0
    with open(output_file) as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows[0] == ["keyword", "value", "comment"]


def test_export_format_required_error():
    """Test that --format is required for stdout."""
    result = runner.invoke(app, ["export", "dummy.fits"], catch_exceptions=False)
    assert result.exit_code == 1
    assert "Error: --format is required" in result.stdout


def test_export_infer_format_error(tmp_path: Path):
    """Test error on unknown file extension."""
    fits_file = create_test_fits(tmp_path)
    output_file = tmp_path / "header.txt"
    result = runner.invoke(app, ["export", str(fits_file), "--output", str(output_file)], catch_exceptions=False)
    assert result.exit_code == 1
    assert "Error: Could not infer format" in result.stdout 