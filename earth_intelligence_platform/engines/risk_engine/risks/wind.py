"""
wind.py

Wind exposure assessment.
"""

from ..risk_helpers import (
    combine_confidence,
    get_satellite_coverage_modifier,
    get_terrain_layer_confidence,
    get_terrain_stat,
    get_weather_confidence,
    get_weather_stat,
)


def normalize(value, minimum, maximum, inverse=False):
    """
    Normalize a value to the range 0-100.
    """

    if maximum == minimum:
        return 0.0

    score = ((value - minimum) / (maximum - minimum)) * 100

    score = max(0, min(score, 100))

    if inverse:
        score = 100 - score

    return round(score, 1)


def compute_wind_risk(
    terrain_product,
    weather_product,
    satellite_product,
):
    """
    Compute wind exposure.

    Returns
    -------
    dict
    """

    wind_speed = get_weather_stat(weather_product, "wind_speed", "mean")

    elevation = get_terrain_stat(terrain_product, "elevation", "mean")

    slope = get_terrain_stat(terrain_product, "slope", "mean")

    wind_score = normalize(
        wind_speed,
        0,
        30,
    )

    elevation_score = normalize(
        elevation,
        0,
        3000,
    )

    slope_score = normalize(
        slope,
        0,
        45,
    )

    score = round(
        0.60 * wind_score + 0.25 * elevation_score + 0.15 * slope_score,
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

    if wind_score > 70:
        drivers.append("High wind speed")

    if elevation_score > 70:
        drivers.append("High elevation")

    if slope_score > 70:
        drivers.append("Steep terrain")

    weather_confidence = get_weather_confidence(weather_product)

    elevation_confidence = get_terrain_layer_confidence(terrain_product, "elevation")

    slope_confidence = get_terrain_layer_confidence(terrain_product, "slope")

    satellite_modifier = get_satellite_coverage_modifier(satellite_product)

    confidence = combine_confidence(
        [
            (weather_confidence, 0.60),
            (elevation_confidence, 0.25),
            (slope_confidence, 0.15),
        ],
        satellite_modifier,
    )

    return {
        "score": score,
        "category": category,
        "drivers": drivers,
        "confidence": confidence,
    }
