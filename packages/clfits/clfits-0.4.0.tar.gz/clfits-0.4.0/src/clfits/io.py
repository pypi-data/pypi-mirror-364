"""Functions for reading and writing FITS headers."""

from pathlib import Path
from typing import Union

from astropy.io import fits
from astropy.io.fits.header import Header

HDU = Union[int, str]


def read_header(fits_file: Path, hdu: HDU = 0) -> Header:
    """Read a header from a specific HDU in a FITS file.

    Parameters
    ----------
    fits_file : Path
        The path to the FITS file.
    hdu : int or str, optional
        The HDU to read from, specified by its 0-based index or name,
        by default 0 (the primary HDU).

    Returns
    -------
    Header
        The header object from the specified HDU.

    Raises
    ------
    FileNotFoundError
        If the FITS file does not exist.
    IndexError
        If the HDU index is out of range.
    KeyError
        If the HDU name is not found.
    OSError
        If the file is not a valid FITS file.

    """
    if not fits_file.exists():
        raise FileNotFoundError(f"Error: FITS file not found at '{fits_file}'")

    try:
        with fits.open(fits_file) as hdul:
            return hdul[hdu].header
    except (IndexError, KeyError) as e:
        # Re-raise with a more informative message
        raise e.__class__(f"Error: HDU '{hdu}' not found in '{fits_file}'.") from e
    except OSError as e:
        # Catch errors like truncated files
        raise OSError(f"Error: Not a valid FITS file: '{fits_file}'") from e


def write_header(fits_file: Path, header: Header, hdu: HDU = 0) -> None:
    """Write a header to a specific HDU of a FITS file.

    This function opens the FITS file in update mode and replaces the
    header of the specified HDU with the new one.

    Parameters
    ----------
    fits_file : Path
        The path to the FITS file.
    header : Header
        The header object to write to the file.
    hdu : int or str, optional
        The HDU to write to, specified by its 0-based index or name,
        by default 0 (the primary HDU).

    Raises
    ------
    FileNotFoundError
        If the FITS file does not exist.
    IndexError
        If the HDU index is out of range.
    KeyError
        If the HDU name is not found.
    OSError
        If the file is not a valid FITS file or cannot be written to.

    """
    if not fits_file.exists():
        raise FileNotFoundError(f"Error: FITS file not found at '{fits_file}'")

    try:
        with fits.open(fits_file, mode="update") as hdul:
            hdul[hdu].header = header
            hdul.flush()  # Ensure changes are written to disk
    except (IndexError, KeyError) as e:
        raise e.__class__(f"Error: HDU '{hdu}' not found in '{fits_file}'.") from e
    except OSError as e:
        raise OSError(f"Error: Could not write to FITS file: '{fits_file}'") from e
