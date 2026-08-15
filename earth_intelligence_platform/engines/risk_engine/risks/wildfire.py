"""
wildfire.py

Wildfire risk assessment.
"""

from ..risk_helpers import (
    combine_confidence,
    get_landcover_confidence,
    get_satellite_coverage_modifier,
    get_vegetation_percentage,
    get_weather_confidence,
    get_weather_stat,
)


def normalize(value, minimum, maximum, inverse=False):
    """
    Normalize a value to the range 0–100.
    """

    if maximum == minimum:
        return 0.0

    score = ((value - minimum) / (maximum - minimum)) * 100

    score = max(0, min(score, 100))

    if inverse:
        score = 100 - score

    return round(score, 1)


def compute_wildfire_risk(
    landcover_product,
    weather_product,
    satellite_product,
):
    """
    Compute wildfire risk.

    Returns
    -------
    dict
    """

    temperature = get_weather_stat(weather_product, "temperature", "mean")

    humidity = get_weather_stat(weather_product, "humidity", "mean")

    precipitation = get_weather_stat(weather_product, "precipitation", "total")

    vegetation = get_vegetation_percentage(landcover_product)

    temperature_score = normalize(
        temperature,
        0,
        45,
    )

    humidity_score = normalize(
        humidity,
        0,
        100,
        inverse=True,
    )

    rainfall_score = normalize(
        precipitation,
        0,
        200,
        inverse=True,
    )

    vegetation_score = normalize(
        vegetation,
        0,
        100,
    )

    score = round(
        0.35 * temperature_score
        + 0.25 * humidity_score
        + 0.20 * rainfall_score
        + 0.20 * vegetation_score,
        1,
    )

    if score < 25:
        category = "Low"

    elif score < 50:
        category = "Moderate"

    elif score < 75:
        category = "High"

    else:
        category = "Very High"

    drivers = []

    if temperature_score > 70:
        drivers.append("High temperature")

    if humidity_score > 70:
        drivers.append("Low humidity")

    if rainfall_score > 70:
        drivers.append("Low precipitation")

    if vegetation_score > 70:
        drivers.append("Dense vegetation")

    weather_confidence = get_weather_confidence(weather_product)

    landcover_confidence = get_landcover_confidence(landcover_product)

    satellite_modifier = get_satellite_coverage_modifier(satellite_product)

    confidence = combine_confidence(
        [
            (weather_confidence, 0.35 + 0.25 + 0.20),
            (landcover_confidence, 0.20),
        ],
        satellite_modifier,
    )

    return {
        "score": score,
        "category": category,
        "drivers": drivers,
        "confidence": confidence,
    }
