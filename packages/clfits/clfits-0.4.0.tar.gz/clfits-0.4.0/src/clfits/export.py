"""Functions for exporting FITS headers to different formats."""

import csv
import json
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Dict, Union

import yaml
from astropy.io.fits.header import Header


class Format(str, Enum):
    """Supported export formats."""

    JSON = "json"
    YAML = "yaml"
    CSV = "csv"


def to_dict(header: Header) -> Dict[str, Union[str, int, float, bool]]:
    """Convert a FITS header to a dictionary.

    Parameters
    ----------
    header : Header
        The FITS header to convert.

    Returns
    -------
    Dict[str, Union[str, int, float, bool]]
        A dictionary representation of the header.

    """
    return {keyword: value for keyword, value in header.items()}


def to_json(header: Header) -> str:
    """Convert a FITS header to a JSON string.

    Parameters
    ----------
    header : Header
        The FITS header to convert.

    Returns
    -------
    str
        A JSON string representation of the header.

    """
    return json.dumps(to_dict(header), indent=2)


def to_yaml(header: Header) -> str:
    """Convert a FITS header to a YAML string.

    Parameters
    ----------
    header : Header
        The FITS header to convert.

    Returns
    -------
    str
        A YAML string representation of the header.

    """
    return yaml.dump(to_dict(header), indent=2)


def to_csv(header: Header) -> str:
    """Convert a FITS header to a CSV string.

    Parameters
    ----------
    header : Header
        The FITS header to convert.

    Returns
    -------
    str
        A CSV string representation of the header.

    """
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["keyword", "value", "comment"])
    for card in header.cards:
        writer.writerow([card.keyword, card.value, card.comment])
    return output.getvalue()


def export_header(header: Header, format: Format, output_file: Path = None) -> None:
    """Export a FITS header to a specified format and destination.

    Parameters
    ----------
    header : Header
        The FITS header to export.
    format : Format
        The format to export the header to.
    output_file : Path, optional
        The file to save the output to. If None, the output is printed
        to the console, by default None.

    """
    exporters = {
        Format.JSON: to_json,
        Format.YAML: to_yaml,
        Format.CSV: to_csv,
    }
    content = exporters[format](header)

    if output_file:
        output_file.write_text(content)
    else:
        print(content)
