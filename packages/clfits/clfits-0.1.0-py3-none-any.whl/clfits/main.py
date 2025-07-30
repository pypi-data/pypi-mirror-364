"""Main CLI for clfits."""

import sys
from pathlib import Path
from typing import Optional

import typer

# Use Typer's built-in echo function for output. This ensures that all
# CLI output is routed through Click's testing helpers, allowing
# typer.testing.CliRunner to capture `stdout`/`stderr` reliably during
# tests.
from clfits import __version__
from clfits.io import read_header, write_header

app = typer.Typer(
    add_completion=False,
    rich_markup_mode="markdown",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool) -> None:
    """Print the version of the package and exit."""
    if value:
        typer.echo(f"clfits version: {__version__}")
        raise typer.Exit()


@app.command()
def view(
    fits_file: Path = typer.Argument(..., dir_okay=False),
) -> None:
    """View the header of a FITS file."""
    try:
        header = read_header(fits_file)
        # Pad keywords for alignment
        for card in header.cards:
            keyword = card.keyword.ljust(8)
            value = f"= '{card.value}'" if isinstance(card.value, str) else f"= {card.value}"
            comment = f" / {card.comment}" if card.comment else ""
            typer.echo(f"{keyword}{value}{comment}")
    except (FileNotFoundError, OSError) as e:
        typer.secho(f"{e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)


@app.command()
def get(
    fits_file: Path = typer.Argument(..., dir_okay=False),
    keyword: str = typer.Argument(..., help="The header keyword to retrieve."),
) -> None:
    """Get the value of a specific header keyword."""
    try:
        header = read_header(fits_file)
        value = header.get(keyword)
        if value is None:
            typer.secho(f"Error: Keyword '{keyword}' not found in '{fits_file}'.", fg=typer.colors.RED, bold=True)
            raise typer.Exit(code=1)
        typer.echo(value)
    except (FileNotFoundError, OSError) as e:
        typer.secho(f"{e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)


@app.command()
def set(
    fits_file: Path = typer.Argument(..., dir_okay=False),
    keyword: str = typer.Argument(..., help="The header keyword to set."),
    value: str = typer.Argument(..., help="The value to set for the keyword."),
    comment: Optional[str] = typer.Option(None, "--comment", "-c", help="An optional comment for the keyword."),
) -> None:
    """Set a keyword's value, with an optional comment."""
    try:
        header = read_header(fits_file)
        header[keyword] = (value, comment) if comment else value
        write_header(fits_file, header)
        typer.secho(f"Success: Set '{keyword}' to '{value}' in '{fits_file}'.", fg=typer.colors.GREEN, bold=True)
    except (FileNotFoundError, OSError) as e:
        typer.secho(f"{e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)


# Register this function under the short command name 'del' to match tests.
@app.command(name="del")
def delete(
    fits_file: Path = typer.Argument(..., dir_okay=False),
    keyword: str = typer.Argument(..., help="The header keyword to delete."),
) -> None:
    """Delete a keyword from the header."""
    try:
        header = read_header(fits_file)
        if keyword not in header:
            typer.secho(f"Warning: Keyword '{keyword}' not found in '{fits_file}'.", fg=typer.colors.YELLOW, bold=True)
            raise typer.Exit(code=0)
        del header[keyword]
        write_header(fits_file, header)
        typer.secho(f"Success: Deleted '{keyword}' from '{fits_file}'.", fg=typer.colors.GREEN, bold=True)
    except (FileNotFoundError, OSError) as e:
        typer.secho(f"{e}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(code=1)


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """Manage FITS headers from the command line."""
    pass


if __name__ == "__main__":
    sys.exit(app())
