"""Tests for FITS file I/O operations."""

from pathlib import Path

import pytest
from astropy.io.fits.header import Header

from clfits.io import read_header, write_header
from tests.utils import create_test_fits


def test_read_header_primary(tmp_path: Path):
    """Test reading the primary header."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    header = read_header(fits_file)  # Default is primary HDU
    assert isinstance(header, Header)
    assert "OBJECT" in header
    assert header["OBJECT"] == "NGC 101"


def test_read_header_by_index(tmp_path: Path):
    """Test reading a header from an HDU specified by index."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    header = read_header(fits_file, hdu=1)
    assert isinstance(header, Header)
    assert header["XTENSION"] == "BINTABLE"


def test_read_header_by_name(tmp_path: Path):
    """Test reading a header from an HDU specified by name."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    header = read_header(fits_file, hdu="OBSERVATIONS")
    assert isinstance(header, Header)
    assert header["EXTNAME"] == "OBSERVATIONS"


def test_read_header_file_not_found():
    """Test that reading a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="FITS file not found"):
        read_header(Path("non_existent_file.fits"))


def test_read_header_invalid_hdu_index(tmp_path: Path):
    """Test that an invalid HDU index raises IndexError."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    with pytest.raises(IndexError, match="HDU '99' not found"):
        read_header(fits_file, hdu=99)


def test_read_header_invalid_hdu_name(tmp_path: Path):
    """Test that an invalid HDU name raises KeyError."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    with pytest.raises(KeyError, match="HDU 'NO_SUCH_HDU' not found"):
        read_header(fits_file, hdu="NO_SUCH_HDU")


def test_read_corrupted_fits_file(tmp_path: Path):
    """Test that reading a corrupted FITS file raises OSError."""
    fits_file = tmp_path / "corrupted.fits"
    fits_file.write_text("This is not a FITS file.")
    with pytest.raises(OSError, match="Not a valid FITS file"):
        read_header(fits_file)


def test_write_header_primary(tmp_path: Path):
    """Test writing a header to the primary HDU."""
    fits_file = create_test_fits(tmp_path)
    header = read_header(fits_file)
    header["NEW_KW"] = "new_value"
    write_header(fits_file, header)

    # Re-read and verify
    new_header = read_header(fits_file)
    assert "NEW_KW" in new_header
    assert new_header["NEW_KW"] == "new_value"


def test_write_header_by_index(tmp_path: Path):
    """Test writing a header to an HDU specified by index."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    header = read_header(fits_file, hdu=1)
    header["NEW_KW"] = "table_value"
    write_header(fits_file, header, hdu=1)

    new_header = read_header(fits_file, hdu=1)
    assert "NEW_KW" in new_header
    assert new_header["NEW_KW"] == "table_value"


def test_write_header_by_name(tmp_path: Path):
    """Test writing a header to an HDU specified by name."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    header = read_header(fits_file, hdu="OBSERVATIONS")
    header["NEW_KW"] = "obs_value"
    write_header(fits_file, header, hdu="OBSERVATIONS")

    new_header = read_header(fits_file, hdu="OBSERVATIONS")
    assert "NEW_KW" in new_header
    assert new_header["NEW_KW"] == "obs_value"


def test_write_header_invalid_hdu_index(tmp_path: Path):
    """Test that writing to an invalid HDU index raises IndexError."""
    fits_file = create_test_fits(tmp_path, with_table=True)
    header = read_header(fits_file)
    with pytest.raises(IndexError, match="HDU '99' not found"):
        write_header(fits_file, header, hdu=99)


def test_write_header_os_error(tmp_path: Path, monkeypatch):
    """Test that an OSError is raised if the file cannot be written to."""
    fits_file = create_test_fits(tmp_path)
    header = read_header(fits_file)

    # Simulate a write error by making the flush method fail
    def mock_flush(*args, **kwargs):
        raise OSError("Disk full")

    monkeypatch.setattr("astropy.io.fits.HDUList.flush", mock_flush)

    with pytest.raises(OSError, match="Could not write to FITS file"):
        write_header(fits_file, header)
