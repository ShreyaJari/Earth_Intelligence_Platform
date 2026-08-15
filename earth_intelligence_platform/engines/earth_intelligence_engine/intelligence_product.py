"""
intelligence_product.py

Create the standard Earth Intelligence Engine product.
"""

from datetime import UTC, datetime


def create_intelligence_product():
    """
    Create an empty Earth Intelligence product.

    Returns
    -------
    dict
        Standard Earth Intelligence product.
    """

    return {
        "success": False,
        "errors": [],
        "warnings": [],
        "intelligence": {
            "earth_intelligence_score": None,
            "environmental_summary": {
                "terrain": {},
                "landcover": {},
                "weather": {},
            },
            "hazard_summary": {
                "highest_risk": None,
                "overall_risk": None,
                "risk_breakdown": {},
            },
            "sustainability": {
                "score": None,
                "summary": None,
            },
            "key_insights": [],
            "recommendations": [],
            "explainability": {
                "drivers": [],
                "limitations": [],
            },
        },
        "statistics": {},
        "processing": {
            "engine": "Earth Intelligence Engine",
            "created": datetime.now(UTC).isoformat(),
            "processing_time_seconds": None,
            "statistics_time_seconds": None,
        },
    }
