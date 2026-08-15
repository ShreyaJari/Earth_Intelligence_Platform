"""
intelligence_helpers.py

Shared statistics accessors for the Earth Intelligence Engine.

Mirrors risk_engine/risk_helpers.py's approach: Terrain and
Weather statistics are nested per-variable, and Land Cover
statistics are keyed by legend class NAME rather than flat
fields, so percentages must be derived rather than read
directly.
"""

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

# NOTE: These groupings are an assumption, not defined elsewhere
# in the codebase. Kept consistent with risk_engine/risk_helpers.py's
# VEGETATION_CLASSES / BUILT_UP_CLASS — revisit both together if
# the intended definitions differ.

VEGETATION_CLASSES = [
    "Tree Cover",
    "Shrubland",
    "Grassland",
    "Cropland",
    "Mangroves",
    "Herbaceous Wetland",
]

BUILT_UP_CLASS = "Built-up"

WATER_CLASSES = [
    "Permanent Water",
]


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


def get_water_percentage(landcover_product):
    """
    Sum percentage_per_class across water-related land cover classes.
    """

    percentages = landcover_product["statistics"]["percentage_per_class"]

    return sum(percentages.get(class_name, 0.0) for class_name in WATER_CLASSES)
