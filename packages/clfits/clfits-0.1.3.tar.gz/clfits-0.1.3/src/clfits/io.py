"""Functions for handling FITS file I/O operations."""

from pathlib import Path

from astropy.io import fits
from astropy.io.fits.header import Header


def read_header(fits_file: Path) -> Header:
    """Read the primary header from a FITS file.

    Parameters
    ----------
    fits_file : Path
        The path to the FITS file.

    Returns
    -------
    Header
        The primary header object from the FITS file.

    Raises
    ------
    FileNotFoundError
        If the FITS file does not exist.
    OSError
        If the file is not a valid FITS file.

    """
    if not fits_file.exists():
        raise FileNotFoundError(f"Error: FITS file not found at '{fits_file}'")

    try:
        with fits.open(fits_file) as hdul:
            return hdul[0].header
    except OSError as e:
        raise OSError(f"Error: Failed to read FITS file at '{fits_file}'. It may be corrupted.") from e


def write_header(fits_file: Path, header: Header) -> None:
    """Write a header to the primary HDU of a FITS file.

    This function opens the FITS file in update mode and replaces the
    primary header with the new one.

    Parameters
    ----------
    fits_file : Path
        The path to the FITS file.
    header : Header
        The header object to write to the file.

    Raises
    ------
    FileNotFoundError
        If the FITS file does not exist.
    OSError
        If the file is not a valid FITS file or cannot be written to.

    """
    if not fits_file.exists():
        raise FileNotFoundError(f"Error: FITS file not found at '{fits_file}'")

    try:
        with fits.open(fits_file, mode="update") as hdul:
            hdul[0].header = header
            hdul.flush()
    except OSError as e:
        raise OSError(f"Error: Failed to write to FITS file at '{fits_file}'.") from e
