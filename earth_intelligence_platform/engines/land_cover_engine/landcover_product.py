"""
landcover_product.py

Creates the standardized Land Cover Product object.
"""

from datetime import datetime


def create_landcover_product():
    """
    Create an empty land cover product.

    Returns
    -------
    dict
        Standardized land cover product.
    """

    return {
        # --------------------------------------------------
        # Status
        # --------------------------------------------------
        "success": False,
        "errors": [],
        "warnings": [],
        # --------------------------------------------------
        # Dataset Information
        # --------------------------------------------------
        "dataset": {},
        "metadata": {},
        # --------------------------------------------------
        # Primary Data
        # --------------------------------------------------
        "classification": None,
        # --------------------------------------------------
        # Derived Products
        # --------------------------------------------------
        "products": {
            "classification": None,
            "visualization": None,
            "legend": None,
            "masks": None,
            "confidence": None,
        },
        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------
        "statistics": {
            "area_per_class": {},
            "percentage_per_class": {},
            "dominant_class": None,
            "number_of_classes": 0,
            "total_area_km2": None,
        },
        # --------------------------------------------------
        # Processing Information
        # --------------------------------------------------
        "processing": {
            "engine": "Land Cover Engine",
            "created": datetime.utcnow().isoformat(),
            "download_time_seconds": None,
            "processing_time_seconds": None,
            "statistics_time_seconds": None,
        },
        "products": {
            "classification": None,
            "visualization": None,
            "legend": None,
            "masks": None,
            "confidence": None,
            "ml_classification": None,  # NEW
        },
        "ml_metadata": None,  # NEW — top-level, alongside "processing"
    }
