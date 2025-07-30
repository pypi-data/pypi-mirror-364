"""Functions for searching and filtering FITS headers."""

from fnmatch import fnmatch

from astropy.io.fits.header import Header


def search_header(
    header: Header, key_pattern: str = None, value_pattern: str = None, case_sensitive: bool = False
) -> Header:
    """Search and filter a FITS header by keyword and/or value patterns.

    Parameters
    ----------
    header : Header
        The FITS header to search.
    key_pattern : str, optional
        A glob-style pattern to match against keywords, by default None.
    value_pattern : str, optional
        A glob-style pattern to match against values, by default None.
    case_sensitive : bool, optional
        Whether the pattern matching should be case-sensitive, by default False.

    Returns
    -------
    Header
        A new Header object containing only the cards that match the criteria.

    """
    matches = Header()
    for card in header.cards:
        key_matches = True
        if key_pattern:
            if case_sensitive:
                key_matches = fnmatch(card.keyword, key_pattern)
            else:
                key_matches = fnmatch(card.keyword.lower(), key_pattern.lower())

        value_matches = True
        if value_pattern:
            value_str = str(card.value)
            if case_sensitive:
                value_matches = fnmatch(value_str, value_pattern)
            else:
                value_matches = fnmatch(value_str.lower(), value_pattern.lower())

        if key_matches and value_matches:
            matches.append(card)

    return matches
