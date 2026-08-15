"""
risk_engine.py

Main Risk Engine workflow.
"""

from .compute_statistics import compute_statistics
from .process_risk import process_risk
from .risk_product import create_risk_product
from .validation import validate_products


def run_risk_engine(
    terrain_product,
    landcover_product,
    weather_product,
    satellite_product,
):
    """
    Execute the Risk Engine.

    Parameters
    ----------
    terrain_product : dict

    landcover_product : dict

    weather_product : dict

    satellite_product : dict

    Returns
    -------
    dict
    """

    risk_product = create_risk_product()

    try:

        validate_products(
            terrain_product,
            landcover_product,
            weather_product,
            satellite_product,
        )

        risk_product = process_risk(
            terrain_product,
            landcover_product,
            weather_product,
            satellite_product,
            risk_product,
        )

        risk_product = compute_statistics(risk_product)

        risk_product["success"] = True

    except Exception as e:

        risk_product["errors"].append(str(e))

        risk_product["success"] = False

    return risk_product
