"""
process_risk.py

Generate all risk assessments.
"""

import time

from earth_intelligence_platform.engines.land_cover_engine import landcover_product
from earth_intelligence_platform.engines.risk_engine import risk_product

from .ml_wildfire_risk import compute_ml_wildfire_risk  # NEW import
from .risks.flood import compute_flood_risk
from .risks.landslide import compute_landslide_risk
from .risks.urban_heat import compute_urban_heat_risk
from .risks.wildfire import compute_wildfire_risk
from .risks.wind import compute_wind_risk


def process_risk(
    terrain_product,
    landcover_product,
    weather_product,
    satellite_product,
    risk_product,
):
    """
    Generate all risk assessments.

    Returns
    -------
    dict
    """

    start = time.time()

    risk_product["products"]["flood"] = compute_flood_risk(
        terrain_product,
        landcover_product,
        weather_product,
        satellite_product,
    )

    risk_product["products"]["landslide"] = compute_landslide_risk(
        terrain_product,
        landcover_product,
        weather_product,
        satellite_product,
    )

    risk_product["products"]["wildfire"] = compute_wildfire_risk(
        landcover_product,
        weather_product,
        satellite_product,
    )

    risk_product["products"]["wildfire"]["ml_calibrated"] = compute_ml_wildfire_risk(
        landcover_product,
        weather_product,
    )

    risk_product["products"]["urban_heat"] = compute_urban_heat_risk(
        landcover_product,
        weather_product,
        satellite_product,
    )

    risk_product["products"]["wind"] = compute_wind_risk(
        terrain_product,
        weather_product,
        satellite_product,
    )

    risk_product["processing"]["processing_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return risk_product
