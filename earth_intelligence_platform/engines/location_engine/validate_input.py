"""
Earth Intelligence System (EIS)
Location Engine

Module:
    Input Validation

Purpose:
    Validate normalized user input before communicating with
    external geospatial services.
"""

SUPPORTED_INPUT_TYPES = [
    "city",
]


def validate_input(location: dict) -> dict:
    """
    Validate normalized location input.

    Processing
    ----------
    - Verify supported input type
    - Verify required fields exist
    - Verify required fields are not empty

    Parameters
    ----------
    location : dict
        Normalized location dictionary.

    Returns
    -------
    dict
        Validated location dictionary.

    Raises
    ------
    ValueError
        If the location input is invalid.
    """

    # Validate required keys
    required_fields = [
        "input_type",
        "city",
        "country",
        "search_query",
    ]

    for field in required_fields:
        if field not in location:
            raise ValueError(f"Missing required field: '{field}'")

    # Validate input type
    if location["input_type"] not in SUPPORTED_INPUT_TYPES:
        raise ValueError(f"Unsupported input type: {location['input_type']}")

    # Validate city
    if not location["city"]:
        raise ValueError("City name cannot be empty.")

    # Validate country
    if not location["country"]:
        raise ValueError("Country name cannot be empty.")

    # Validate search query
    if not location["search_query"]:
        raise ValueError("Search query cannot be empty.")

    return location
