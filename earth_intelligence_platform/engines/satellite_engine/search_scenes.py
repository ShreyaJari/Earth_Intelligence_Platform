"""
Earth Intelligence Platform
Satellite Engine

Search Scenes

Searches the Microsoft Planetary Computer for satellite
imagery intersecting the requested Area of Interest.
"""

import pandas as pd
from pystac_client import Client

from earth_intelligence_platform.engines.satellite_engine.satellite_product import (
    SatelliteRequest,
)

# ============================================================
# Planetary Computer STAC
# ============================================================

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


# ============================================================
# Search Scenes
# ============================================================


def search_scenes(
    request: SatelliteRequest,
):
    """
    Search Planetary Computer for imagery.

    Parameters
    ----------
    request : SatelliteRequest

    Returns
    -------
    pandas.DataFrame
    """

    geometry = request.aoi["geometry"]["geometry"]

    print("\n==============================")
    print("Satellite Scene Search")
    print("==============================")
    print("Collection :", request.collection)
    print(
        "Date Range :",
        request.start_date,
        "→",
        request.end_date,
    )
    print(
        "Cloud Cover: <=",
        request.max_cloud_cover,
        "%",
    )
    print(
        "AOI Type   :",
        geometry.geom_type,
    )
    print(
        "AOI Bounds :",
        geometry.bounds,
    )
    print("==============================")

    catalog = Client.open(
        STAC_URL,
        ignore_conformance=True,
    )
    # ---------------------------------------------------------
    # Build datetime string
    # ---------------------------------------------------------

    if request.start_date and request.end_date:

        datetime_range = f"{request.start_date}/{request.end_date}"

    elif request.start_date:

        datetime_range = f"{request.start_date}/.."

    elif request.end_date:

        datetime_range = f"../{request.end_date}"

    else:

        datetime_range = None

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    search = catalog.search(
        collections=[request.collection],
        intersects=geometry.__geo_interface__,
        datetime=datetime_range,
        query={
            "eo:cloud_cover": {
                "lte": request.max_cloud_cover,
            }
        },
    )

    items = list(search.items())

    if len(items) == 0:

        raise RuntimeError("No satellite scenes found.")

    print(f"\n✓ Found {len(items)} candidate scene(s).")

    rows = []

    for item in items:

        rows.append(
            {
                "scene_id": item.id,
                "collection": request.collection,
                "acquisition_date": item.datetime,
                "cloud_cover": item.properties.get(
                    "eo:cloud_cover",
                    None,
                ),
                "stac_item": item,
            }
        )

    inventory = pd.DataFrame(rows)

    print("\nCandidate Scenes")
    print("----------------------------")
    print(
        inventory[
            [
                "scene_id",
                "cloud_cover",
                "acquisition_date",
            ]
        ]
    )
    print("----------------------------\n")

    return inventory
