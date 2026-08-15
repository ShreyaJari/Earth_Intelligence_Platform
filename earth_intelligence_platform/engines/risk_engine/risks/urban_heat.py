"""
urban_heat.py

Urban Heat risk assessment.
"""

from ..risk_helpers import (
    combine_confidence,
    get_built_up_percentage,
    get_landcover_confidence,
    get_satellite_coverage_modifier,
    get_vegetation_percentage,
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


def compute_urban_heat_risk(
    landcover_product,
    weather_product,
    satellite_product,
):
    """
    Compute Urban Heat risk.

    Returns
    -------
    dict
    """

    temperature = get_weather_stat(weather_product, "temperature", "mean")

    built_up = get_built_up_percentage(landcover_product)

    vegetation = get_vegetation_percentage(landcover_product)

    impervious = built_up

    temperature_score = normalize(
        temperature,
        0,
        45,
    )

    builtup_score = normalize(
        built_up,
        0,
        100,
    )

    vegetation_score = normalize(
        vegetation,
        0,
        100,
        inverse=True,
    )

    impervious_score = normalize(
        impervious,
        0,
        100,
    )

    score = round(
        0.35 * temperature_score
        + 0.35 * builtup_score
        + 0.20 * vegetation_score
        + 0.10 * impervious_score,
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
        drivers.append("High air temperature")

    if builtup_score > 70:
        drivers.append("Dense built-up area")

    if vegetation_score > 70:
        drivers.append("Limited vegetation")

    if impervious_score > 70:
        drivers.append("Large impervious surface")

    weather_confidence = get_weather_confidence(weather_product)

    landcover_confidence = get_landcover_confidence(landcover_product)

    satellite_modifier = get_satellite_coverage_modifier(satellite_product)

    confidence = combine_confidence(
        [
            (weather_confidence, 0.35),
            (landcover_confidence, 0.35 + 0.20 + 0.10),
        ],
        satellite_modifier,
    )

    return {
        "score": score,
        "category": category,
        "drivers": drivers,
        "confidence": confidence,
    }
