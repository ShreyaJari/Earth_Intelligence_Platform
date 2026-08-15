"""
main.py

Public entry point for the Land Cover Engine.
"""

from .landcover_engine import landcover_engine


def run_landcover_engine(
    aoi,
    catalog,
    satellite_product=None,  # NEW
):
    """
    Execute the Land Cover Engine.

    Parameters
    ----------
    aoi : dict

    catalog : list

    satellite_product : SatelliteProduct, optional
        Enables ML-refined, date-specific classification if
        provided.

    Returns
    -------
    dict
    """

    return landcover_engine(
        aoi,
        catalog,
        satellite_product=satellite_product,
    )
