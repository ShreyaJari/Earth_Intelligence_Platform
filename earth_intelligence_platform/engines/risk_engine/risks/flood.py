"""
flood.py

Flood risk assessment.
"""

from ..risk_helpers import (
    combine_confidence,
    get_built_up_percentage,
    get_landcover_confidence,
    get_satellite_coverage_modifier,
    get_terrain_layer_confidence,
    get_terrain_stat,
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


def compute_flood_risk(
    terrain_product,
    landcover_product,
    weather_product,
    satellite_product,
):
    """
    Compute flood risk.

    Returns
    -------
    dict
    """

    elevation = get_terrain_stat(terrain_product, "elevation", "mean")

    slope = get_terrain_stat(terrain_product, "slope", "mean")

    precipitation = get_weather_stat(weather_product, "precipitation", "total")

    built_up = get_built_up_percentage(landcover_product)

    elevation_score = normalize(
        elevation,
        0,
        1000,
        inverse=True,
    )

    slope_score = normalize(
        slope,
        0,
        45,
        inverse=True,
    )

    rainfall_score = normalize(
        precipitation,
        0,
        200,
    )

    builtup_score = normalize(
        built_up,
        0,
        100,
    )

    score = (
        0.30 * elevation_score
        + 0.25 * slope_score
        + 0.30 * rainfall_score
        + 0.15 * builtup_score
    )

    score = round(score, 1)

    if score < 25:
        category = "Low"

    elif score < 50:
        category = "Moderate"

    elif score < 75:
        category = "High"

    else:
        category = "Very High"

    drivers = []

    if rainfall_score > 70:
        drivers.append("High precipitation")

    if elevation_score > 70:
        drivers.append("Low elevation")

    if slope_score > 70:
        drivers.append("Flat terrain")

    if builtup_score > 70:
        drivers.append("Large impervious surface")

    elevation_confidence = get_terrain_layer_confidence(terrain_product, "elevation")

    slope_confidence = get_terrain_layer_confidence(terrain_product, "slope")

    weather_confidence = get_weather_confidence(weather_product)

    landcover_confidence = get_landcover_confidence(landcover_product)

    satellite_modifier = get_satellite_coverage_modifier(satellite_product)

    confidence = combine_confidence(
        [
            (elevation_confidence, 0.30),
            (slope_confidence, 0.25),
            (weather_confidence, 0.30),
            (landcover_confidence, 0.15),
        ],
        satellite_modifier,
    )

    print("\n========== FLOOD DIAGNOSTIC ==========")
    print("elevation (mean):", elevation)
    print("elevation_score (inverse):", elevation_score)
    print("slope (mean):", slope)
    print("slope_score (inverse):", slope_score)
    print("precipitation (total):", precipitation)
    print("rainfall_score:", rainfall_score)
    print("built_up (%):", built_up)
    print("builtup_score:", builtup_score)
    print("elevation contribution (0.30x):", round(0.30 * elevation_score, 2))
    print("slope contribution (0.25x):", round(0.25 * slope_score, 2))
    print("rainfall contribution (0.30x):", round(0.30 * rainfall_score, 2))
    print("builtup contribution (0.15x):", round(0.15 * builtup_score, 2))
    print("TOTAL score:", score)
    print("=======================================\n")

    return {
        "score": score,
        "category": category,
        "drivers": drivers,
        "confidence": confidence,
    }
