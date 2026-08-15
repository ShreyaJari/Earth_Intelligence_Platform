"""
earth_intelligence_engine.py

Main Earth Intelligence Engine workflow.
"""

from .compute_statistics import compute_statistics
from .intelligence_product import create_intelligence_product
from .process_intelligence import process_intelligence
from .validation import validate_products


def run_earth_intelligence_engine(
    location_product,
    discovery_product,
    satellite_product,
    terrain_product,
    landcover_product,
    weather_product,
    risk_product,
):
    """
    Execute the Earth Intelligence Engine.

    Returns
    -------
    dict
    """

    intelligence_product = create_intelligence_product()

    try:

        validate_products(
            location_product,
            discovery_product,
            satellite_product,
            terrain_product,
            landcover_product,
            weather_product,
            risk_product,
        )

        intelligence_product = process_intelligence(
            location_product,
            discovery_product,
            satellite_product,
            terrain_product,
            landcover_product,
            weather_product,
            risk_product,
            intelligence_product,
        )

        intelligence_product = compute_statistics(intelligence_product)

        intelligence_product["success"] = True

    except Exception as e:

        intelligence_product["errors"].append(str(e))

        intelligence_product["success"] = False

    return intelligence_product
