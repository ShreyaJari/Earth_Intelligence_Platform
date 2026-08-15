"""
landslide.py

Landslide risk assessment.
"""

from ..risk_helpers import (
    get_terrain_stat,
    get_weather_stat,
    get_vegetation_percentage,
    get_steep_area_percentage,
    get_terrain_layer_confidence,
    get_weather_confidence,
    get_landcover_confidence,
    get_satellite_coverage_modifier,
    combine_confidence,
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


def compute_landslide_risk(
    terrain_product,
    landcover_product,
    weather_product,
    satellite_product,
):
    """
    Compute landslide risk.

    Uses PERCENTAGE OF AOI AREA exceeding a critical slope
    threshold (25 degrees), rather than AOI-wide mean slope.
    Mean slope is disproportionately influenced by a small
    steep minority within an otherwise flat AOI — a threshold
    area-percentage approach is more consistent with how real
    landslide susceptibility mapping treats slope as a
    threshold effect rather than a linear one.

    Returns
    -------
    dict
    """

    steep_area_percentage = get_steep_area_percentage(

        terrain_product,

        threshold_degrees=25,

    )

    elevation = get_terrain_stat(
        terrain_product, "elevation", "mean"
    )

    precipitation = get_weather_stat(
        weather_product, "precipitation", "total"
    )

    vegetation = get_vegetation_percentage(
        landcover_product
    )

    # ---------------------------------------------------------
    # Slope Score — direct use of steep-area percentage,
    # saturating at 50% (i.e. half the AOI being steep is
    # already an extreme condition; this saturation point is
    # an assumption, not a validated geotechnical threshold).
    # ---------------------------------------------------------

    slope_score = normalize(

        steep_area_percentage,

        0,

        50,

    )

    elevation_score = normalize(
        elevation,
        0,
        3000,
    )

    rainfall_score = normalize(
        precipitation,
        0,
        200,
    )

    vegetation_score = normalize(
        vegetation,
        0,
        100,
        inverse=True,
    )

    score = round(

        0.40 * slope_score +

        0.20 * elevation_score +

        0.30 * rainfall_score +

        0.10 * vegetation_score,

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

    if steep_area_percentage > 15:

        drivers.append(

            f"{steep_area_percentage:.0f}% of AOI exceeds "

            "25° slope"

        )

    if rainfall_score > 70:
        drivers.append("Heavy precipitation")

    if vegetation_score > 70:
        drivers.append("Sparse vegetation")

    if elevation_score > 70:
        drivers.append("High elevation")

    slope_confidence = get_terrain_layer_confidence(
        terrain_product, "slope"
    )

    elevation_confidence = get_terrain_layer_confidence(
        terrain_product, "elevation"
    )

    weather_confidence = get_weather_confidence(
        weather_product
    )

    landcover_confidence = get_landcover_confidence(
        landcover_product
    )

    satellite_modifier = get_satellite_coverage_modifier(
        satellite_product
    )

    confidence = combine_confidence(

        [

            (slope_confidence, 0.40),

            (elevation_confidence, 0.20),

            (weather_confidence, 0.30),

            (landcover_confidence, 0.10),

        ],

        satellite_modifier,

    )

    print("\n========== LANDSLIDE DIAGNOSTIC ==========")
    print("steep_area_percentage:", steep_area_percentage)
    print("slope_score:", slope_score)
    print("elevation (mean):", elevation)
    print("elevation_score:", elevation_score)
    print("precipitation (total):", precipitation)
    print("rainfall_score:", rainfall_score)
    print("vegetation (%):", vegetation)
    print("vegetation_score:", vegetation_score)
    print("slope contribution (0.40x):", round(0.40 * slope_score, 2))
    print("elevation contribution (0.20x):", round(0.20 * elevation_score, 2))
    print("rainfall contribution (0.30x):", round(0.30 * rainfall_score, 2))
    print("vegetation contribution (0.10x):", round(0.10 * vegetation_score, 2))
    print("TOTAL score:", score)
    print("===========================================\n")

    return{

        "score": score,

        "category": category,

        "drivers": drivers,

        "confidence": confidence,

        "steep_area_percentage": steep_area_percentage,

    }