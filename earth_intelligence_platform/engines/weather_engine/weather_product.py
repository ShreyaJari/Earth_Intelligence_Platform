"""
weather_product.py

Create the standard Weather Engine product.
"""

from datetime import UTC, datetime


def create_weather_product():
    """
    Create an empty Weather Engine product.

    Returns
    -------
    dict
        Standard weather product.
    """

    return {
        "success": False,
        "errors": [],
        "warnings": [],
        "dataset": None,
        "metadata": {},
        "products": {
            "temperature": None,
            "precipitation": None,
            "wind_speed": None,
            "wind_direction": None,
            "humidity": None,
            "pressure": None,
            "time": None,
        },
        "statistics": {
            "temperature": {},
            "precipitation": {},
            "wind_speed": {},
            "humidity": {},
            "pressure": {},
        },
        "processing": {
            "engine": "Weather Engine",
            "created": datetime.now(UTC).isoformat(),
            "download_time_seconds": None,
            "processing_time_seconds": None,
            "statistics_time_seconds": None,
        },
    }
