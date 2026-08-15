"""
Earth Intelligence System (EIS)
Location Engine

Module:
    Input Normalization

Purpose:
    Standardize user-provided location information into a
    consistent format before validation and location search.
"""

from copy import deepcopy


def normalize_input(location: dict) -> dict:
    """
    Normalize user location input.

    Processing
    ----------
    - Remove leading/trailing whitespace
    - Standardize capitalization
    - Create a standardized search query

    Parameters
    ----------
    location : dict
        User location configuration.

    Returns
    -------
    dict
        Normalized location dictionary.

    Example
    -------
    >>> location = {
    ...     "input_type": "city",
    ...     "city": "  mumbai ",
    ...     "country": " india "
    ... }

    >>> normalize_input(location)

    {
        "input_type": "city",
        "city": "Mumbai",
        "country": "India",
        "search_query": "Mumbai, India"
    }
    """

    normalized = deepcopy(location)

    normalized["city"] = normalized["city"].strip().title()

    normalized["country"] = normalized["country"].strip().title()

    normalized["search_query"] = f"{normalized['city']}, " f"{normalized['country']}"

    return normalized
