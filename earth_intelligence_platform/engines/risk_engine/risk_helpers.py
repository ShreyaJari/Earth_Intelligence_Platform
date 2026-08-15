"""
risk_helpers.py

Shared statistics and confidence accessors for risk modules.

Terrain and Weather statistics are nested per-variable
(e.g. statistics["elevation"]["mean"]), not flat keys like
"mean_elevation". Land Cover statistics are keyed by legend
class NAME under "percentage_per_class", not flat fields
like "built_up_percentage" — these helpers derive that.

This module also provides real, data-driven confidence
calculations, replacing hardcoded confidence values. Each
hazard's confidence is a weighted combination of:

1. Sample-size confidence — standard error of a mean shrinks
   proportionally to 1/sqrt(n), so confidence rises with the
   number of valid pixels/records behind each statistic.
2. Land Cover classification completeness — how much of the
   AOI was actually classified vs. nodata/gaps.
3. Satellite AOI coverage — how completely the selected
   Satellite Engine acquisition covers the AOI, applied as a
   multiplicative modifier across every hazard.
"""

import math

# ============================================================
# Terrain / Weather — nested statistic lookup
# ============================================================


def get_terrain_stat(terrain_product, layer, stat):
    """
    Read a Terrain Engine statistic.

    Example: get_terrain_stat(terrain_product, "elevation", "mean")
    """

    return terrain_product["statistics"][layer][stat]


def get_weather_stat(weather_product, variable, stat):
    """
    Read a Weather Engine statistic.

    Example: get_weather_stat(weather_product, "precipitation", "total")
    """

    return weather_product["statistics"][variable][stat]


# ============================================================
# Land Cover — class-name based aggregation
# ============================================================

# NOTE: This vegetation grouping is an assumption, not something
# defined elsewhere in the codebase. Currently includes classes
# with live vegetation cover. Revisit if the intended definition
# differs (e.g. whether Mangroves / Herbaceous Wetland should count).

VEGETATION_CLASSES = [
    "Tree Cover",
    "Shrubland",
    "Grassland",
    "Cropland",
    "Mangroves",
    "Herbaceous Wetland",
]

BUILT_UP_CLASS = "Built-up"


def get_vegetation_percentage(landcover_product):
    """
    Sum percentage_per_class across vegetated land cover classes.
    """

    percentages = landcover_product["statistics"]["percentage_per_class"]

    return sum(percentages.get(class_name, 0.0) for class_name in VEGETATION_CLASSES)


def get_built_up_percentage(landcover_product):
    """
    Read the Built-up class percentage.
    """

    percentages = landcover_product["statistics"]["percentage_per_class"]

    return percentages.get(BUILT_UP_CLASS, 0.0)


# ============================================================
# Confidence Calculations
# ============================================================


def sample_size_confidence(n):
    """
    Statistical confidence based on sample size.

    Standard error of a mean shrinks proportionally to
    1/sqrt(n), so this saturates towards 1.0 as sample size
    grows, and is 0 with no data at all.
    """

    if n is None or n <= 0:

        return 0.0

    return 1 - 1 / math.sqrt(n + 1)


def get_terrain_layer_confidence(terrain_product, layer):
    """
    Confidence in a Terrain Engine statistic, based on the
    number of valid pixels contributing to it.
    """

    stats = terrain_product["statistics"].get(layer, {})

    n = stats.get("valid_pixel_count", 0)

    return sample_size_confidence(n)


def get_weather_confidence(weather_product):
    """
    Confidence in Weather Engine statistics, based on the
    number of hourly records retrieved.
    """

    records = weather_product["products"].get("time")

    n = len(records) if records is not None else 0

    return sample_size_confidence(n)


def get_landcover_confidence(landcover_product):
    """
    Confidence in Land Cover Engine statistics, combining:
    - how much of the AOI was actually classified
      (vs. nodata/gaps)
    - the number of valid classified pixels
    """

    stats = landcover_product["statistics"]

    percentages = stats.get("percentage_per_class", {})

    classified_fraction = (
        min(1.0, sum(percentages.values()) / 100.0) if percentages else 0.0
    )

    n = stats.get("total_valid_pixels", 0)

    sample_conf = sample_size_confidence(n)

    return round(
        (classified_fraction + sample_conf) / 2,
        4,
    )


def get_satellite_coverage_modifier(satellite_product):
    """
    Overall AOI data-availability modifier, derived from how
    completely the Satellite Engine's selected acquisition
    covers the AOI. Applied as a multiplicative modifier
    across every hazard's confidence.
    """

    coverage_percent = getattr(
        satellite_product.scene,
        "coverage_percent",
        100.0,
    )

    return max(0.0, min(1.0, coverage_percent / 100.0))


def combine_confidence(weighted_components, satellite_modifier):
    """
    Combine (confidence, weight) pairs into a single weighted
    confidence score, then apply the satellite AOI coverage
    modifier.

    Parameters
    ----------
    weighted_components : list[tuple[float, float]]
        List of (confidence, weight) pairs, using the SAME
        weights as the hazard's own score formula.

    satellite_modifier : float
        From get_satellite_coverage_modifier().

    Returns
    -------
    float
        Combined confidence, rounded to 2 decimal places,
        in the range [0, 1].
    """

    total_weight = sum(weight for _, weight in weighted_components)

    if total_weight == 0:

        base = 0.0

    else:

        base = (
            sum(confidence * weight for confidence, weight in weighted_components)
            / total_weight
        )

    combined = base * satellite_modifier

    return round(
        max(0.0, min(1.0, combined)),
        2,
    )

def get_steep_area_percentage(terrain_product, threshold_degrees=25):
    """
    Read the percentage of AOI area exceeding a critical slope
    threshold — a more defensible landslide susceptibility
    proxy than AOI-wide mean slope, which is disproportionately
    influenced by a small steep minority within an otherwise
    flat AOI. See compute_slope_area_percentages() in the
    Terrain Engine for the full rationale.

    Parameters
    ----------
    terrain_product : dict

    threshold_degrees : int
        Must match one of SLOPE_THRESHOLDS_DEGREES computed by
        the Terrain Engine (15, 25, or 35).

    Returns
    -------
    float
        Percentage (0-100) of AOI area exceeding the threshold.
    """

    stats = terrain_product["statistics"].get("slope", {})

    key = f"percentage_above_{threshold_degrees}_degrees"

    return stats.get(key, 0.0)