"""
Earth Intelligence Platform

Terrain Engine

Public Entry Point
"""

from .terrain_engine import terrain_engine


def run_terrain_engine(aoi, catalog):
    """
    Run the Terrain Engine.

    Parameters
    ----------
    aoi : dict
        Area of Interest.

    catalog : dict
        Earth Intelligence Catalog.

    Returns
    -------
    dict
        Terrain Product.
    """

    return terrain_engine(aoi, catalog)
