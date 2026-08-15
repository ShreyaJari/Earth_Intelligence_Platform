"""
process_intelligence.py

Generate Earth Intelligence from previous engine outputs.
"""

import time

from .intelligence_helpers import (
    get_built_up_percentage,
    get_terrain_stat,
    get_vegetation_percentage,
    get_water_percentage,
    get_weather_stat,
)


def process_intelligence(
    location_product,
    discovery_product,
    satellite_product,
    terrain_product,
    landcover_product,
    weather_product,
    risk_product,
    intelligence_product,
):
    """
    Generate Earth Intelligence.

    Returns
    -------
    dict
    """

    start = time.time()

    intelligence = intelligence_product["intelligence"]

    mean_elevation = get_terrain_stat(terrain_product, "elevation", "mean")

    mean_slope = get_terrain_stat(terrain_product, "slope", "mean")

    vegetation = get_vegetation_percentage(landcover_product)

    built_up = get_built_up_percentage(landcover_product)

    water = get_water_percentage(landcover_product)

    mean_temperature = get_weather_stat(weather_product, "temperature", "mean")

    total_precipitation = get_weather_stat(weather_product, "precipitation", "total")

    mean_humidity = get_weather_stat(weather_product, "humidity", "mean")

    mean_wind_speed = get_weather_stat(weather_product, "wind_speed", "mean")

    # --------------------------------------------------
    # Environmental Summary
    # --------------------------------------------------

    intelligence["environmental_summary"] = {
        "terrain": {
            "mean_elevation": mean_elevation,
            "mean_slope": mean_slope,
        },
        "landcover": {
            "vegetation_percentage": vegetation,
            "built_up_percentage": built_up,
        },
        "weather": {
            "mean_temperature": mean_temperature,
            "total_precipitation": total_precipitation,
        },
    }

    # --------------------------------------------------
    # Hazard Summary
    # --------------------------------------------------

    highest = risk_product["statistics"]["highest_risk"]

    average_risk_score = risk_product["statistics"]["average_risk"]

    overall_risk = {
        "score": average_risk_score,
    }

    intelligence["hazard_summary"] = {
        "highest_risk": highest,
        "overall_risk": overall_risk,
        "risk_breakdown": risk_product["statistics"]["risk_summary"],
    }

    # --------------------------------------------------
    # Sustainability
    # --------------------------------------------------

    sustainability_score = round(
        vegetation * 0.6 + (100 - built_up) * 0.4,
        1,
    )

    intelligence["sustainability"] = {
        "score": sustainability_score,
        "summary": None,
    }

    # --------------------------------------------------
    # Earth Intelligence Score
    # --------------------------------------------------

    # Environmental Quality

    environmental_quality = round(
        vegetation * 0.5 + water * 0.2 + (100 - built_up) * 0.3,
        1,
    )

    # Terrain Stability

    terrain_stability = round(
        100 - min(mean_slope * 2, 100),
        1,
    )

    # Climate Conditions

    temperature_score = max(
        0,
        100 - abs(mean_temperature - 22) * 4,
    )

    humidity_score = max(
        0,
        100 - abs(mean_humidity - 60) * 2,
    )

    precipitation_score = min(
        total_precipitation,
        100,
    )

    wind_score = max(
        0,
        100 - mean_wind_speed * 3,
    )

    climate_conditions = round(
        temperature_score * 0.30
        + humidity_score * 0.25
        + precipitation_score * 0.20
        + wind_score * 0.25,
        1,
    )

    # Hazard Resilience

    hazard_resilience = round(
        100 - overall_risk["score"],
        1,
    )

    # Final Earth Intelligence Score

    earth_score = round(
        environmental_quality * 0.25
        + terrain_stability * 0.15
        + climate_conditions * 0.20
        + hazard_resilience * 0.25
        + sustainability_score * 0.15,
        1,
    )

    intelligence["earth_intelligence_score"] = {
        "score": earth_score,
        "components": {
            "environmental_quality": environmental_quality,
            "terrain_stability": terrain_stability,
            "climate_conditions": climate_conditions,
            "hazard_resilience": hazard_resilience,
            "sustainability": sustainability_score,
        },
    }

    # --------------------------------------------------
    # Key Insights
    # --------------------------------------------------

    insights = []

    if vegetation > 60:
        insights.append("The area has extensive vegetation cover.")

    if built_up > 50:
        insights.append("The area is predominantly urban.")

    insights.append(
        f"Highest identified hazard is " f"{highest['hazard'].replace('_', ' ')}."
    )

    intelligence["key_insights"] = insights

    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------

    recommendations = []

    if built_up > 50:
        recommendations.append("Increase urban green infrastructure.")

    if vegetation < 30:
        recommendations.append("Increase vegetation cover where feasible.")

    if highest["category"] in [
        "High",
        "Very High",
    ]:
        recommendations.append(
            f"Prioritize mitigation for " f"{highest['hazard'].replace('_', ' ')} risk."
        )

    intelligence["recommendations"] = recommendations

    # --------------------------------------------------
    # Explainability
    # --------------------------------------------------

    intelligence["explainability"] = {
        "drivers": risk_product["products"][highest["hazard"]]["drivers"],
        "limitations": [
            "Based on currently available datasets.",
            "Version 1 uses rule-based scoring.",
        ],
    }

    intelligence_product["processing"]["processing_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return intelligence_product
