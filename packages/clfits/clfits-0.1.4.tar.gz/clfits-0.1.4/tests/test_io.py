"""Tests for the FITS file I/O operations."""

from pathlib import Path

import pytest
from astropy.io.fits.header import Header

from clfits.io import read_header, write_header
from tests.utils import create_test_fits


def test_read_header_not_found():
    """Test reading a header from a non-existent file."""
    with pytest.raises(FileNotFoundError):
        read_header(Path("nonexistent.fits"))


def test_read_header_corrupted(tmp_path: Path):
    """Test reading a header from a corrupted FITS file."""
    corrupted_file = tmp_path / "corrupted.fits"
    corrupted_file.write_text("This is not a FITS file.")
    with pytest.raises(OSError):
        read_header(corrupted_file)


def test_write_header_not_found():
    """Test writing a header to a non-existent file."""
    with pytest.raises(FileNotFoundError):
        write_header(Path("nonexistent.fits"), Header())


def test_write_header_corrupted(tmp_path: Path):
    """Test writing a header to a corrupted FITS file."""
    fits_file = create_test_fits(tmp_path)
    # Make the file read-only to simulate a write error
    fits_file.chmod(0o444)
    header = read_header(fits_file)

    with pytest.raises(OSError):
        write_header(fits_file, header)
