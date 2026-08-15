"""
main.py

Main interface for the Earth Intelligence Platform Location Engine.

Project: Earth Intelligence Platform
Author: Shreya Jariwala
"""

from pathlib import Path

from .build_aoi import build_aoi
from .resolve_city import resolve_city
from .search_city import GHSCityDatabase

# ------------------------------------------------------------------
# Dataset
# ------------------------------------------------------------------

DATABASE = Path(__file__).parent / "data" / "GHS_UCDB_GLOBE_R2024A.gpkg"


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


def run_location_engine(location: dict):
    """
    Runs the complete Location Engine.

    Parameters
    ----------
    location : dict

        Example
        -------
        {
            "input_type": "city",
            "city": "Mumbai",
            "country": "India"
        }

    Returns
    -------
    AOI
    """

    # --------------------------------------------------------------
    # Validate input
    # --------------------------------------------------------------

    if not isinstance(location, dict):
        raise TypeError("location must be a dictionary.")

    input_type = location.get("input_type")

    if input_type != "city":
        raise NotImplementedError(f"Input type '{input_type}' is not yet supported.")

    city = location.get("city")
    country = location.get("country")

    if not city:
        raise ValueError("City name is required.")

    # --------------------------------------------------------------
    # Load database
    # --------------------------------------------------------------

    db = GHSCityDatabase(DATABASE)

    # --------------------------------------------------------------
    # Search
    # --------------------------------------------------------------

    matches = db.search(
        city=city,
        country=country,
    )

    if len(matches) == 0:
        raise ValueError(f"No matching city found for '{city}'.")

    # --------------------------------------------------------------
    # Resolve ambiguity
    # --------------------------------------------------------------

    city_record = resolve_city(matches)

    # --------------------------------------------------------------
    # Build AOI
    # --------------------------------------------------------------

    aoi = build_aoi(city_record)

    print("\n========== AOI ==========")
    print(aoi)
    print("Top-level keys:", aoi.keys())
    print("Spatial:", aoi["spatial"])
    print("=========================\n")

    return aoi

    # ------------------------------------------------------------------
    # Local testing
    # ------------------------------------------------------------------


if __name__ == "__main__":

    test_location = {"input_type": "city", "city": "Mumbai", "country": "India"}

    aoi = run_location_engine(test_location)

    print(aoi)
