"""
Earth Intelligence Platform
Satellite Engine

Geo Utils

Shared geometry helpers used across pipeline stages.
"""

from pyproj import CRS


def estimate_utm_crs(geometry):
    """
    Estimate a suitable UTM CRS for a WGS84 geometry
    based on its centroid.

    Parameters
    ----------
    geometry : shapely.geometry.base.BaseGeometry
        Geometry in EPSG:4326.

    Returns
    -------
    pyproj.CRS
    """

    centroid = geometry.centroid

    lon = centroid.x
    lat = centroid.y

    zone = int((lon + 180) / 6) + 1

    if lat >= 0:

        epsg = 32600 + zone

    else:

        epsg = 32700 + zone

    return CRS.from_epsg(epsg)
