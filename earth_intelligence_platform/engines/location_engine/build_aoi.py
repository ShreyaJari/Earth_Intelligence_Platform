"""
build_aoi.py

Constructs a standardized Area of Interest (AOI) object.

Project: Earth Intelligence Platform
Author: Shreya Jariwala
"""

from pyproj import Geod

# ------------------------------------------------------------------
# WGS84 Ellipsoid
# ------------------------------------------------------------------

GEOD = Geod(ellps="WGS84")


# ------------------------------------------------------------------
# Build AOI
# ------------------------------------------------------------------


def build_aoi(city_record):
    """
    Build a standardized AOI dictionary.

    Parameters
    ----------
    city_record : pandas.Series

    Returns
    -------
    dict
        Standardized Area of Interest (AOI)
    """

    geometry = city_record.geometry

    # --------------------------------------------------------------
    # Geometry
    # --------------------------------------------------------------

    centroid = geometry.centroid

    bounds = geometry.bounds

    geometry_type = geometry.geom_type

    # --------------------------------------------------------------
    # Accurate Area & Perimeter
    # --------------------------------------------------------------

    area, perimeter = GEOD.geometry_area_perimeter(geometry)

    area_sq_km = abs(area) / 1_000_000

    perimeter_km = perimeter / 1000

    # --------------------------------------------------------------
    # AOI
    # --------------------------------------------------------------

    aoi = {
        "identity": {
            "name": city_record["GC_UCN_MAI_2025"],
            "country": city_record["GC_CNT_UNN_2025"],
        },
        "geometry": {
            "geometry": geometry,
            "geometry_type": geometry_type,
            "crs": "EPSG:4326",
        },
        "spatial": {
            "centroid": {
                "latitude": centroid.y,
                "longitude": centroid.x,
            },
            "bounds": {
                "west": bounds[0],
                "south": bounds[1],
                "east": bounds[2],
                "north": bounds[3],
            },
            "area_sq_km": area_sq_km,
            "perimeter_km": perimeter_km,
        },
    }

    return aoi
