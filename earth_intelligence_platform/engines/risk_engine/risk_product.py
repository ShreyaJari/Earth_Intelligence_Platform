"""
risk_product.py

Create the standard Risk Engine product.
"""

from datetime import UTC, datetime


def create_risk_product():
    """
    Create an empty Risk Engine product.

    Returns
    -------
    dict
        Standard risk product.
    """

    return {
        "success": False,
        "errors": [],
        "warnings": [],
        "products": {
            "flood": None,
            "landslide": None,
            "wildfire": None,
            "urban_heat": None,
            "wind": None,
        },
        "statistics": {
            "highest_risk": None,
            "average_risk": None,
            "risk_summary": {},
        },
        "processing": {
            "engine": "Risk Engine",
            "created": datetime.now(UTC).isoformat(),
            "processing_time_seconds": None,
            "statistics_time_seconds": None,
        },
    }
