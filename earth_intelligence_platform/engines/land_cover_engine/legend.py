"""
Earth Intelligence Platform
Land Cover Engine

Legend

Shared ESA WorldCover class legend, used by both the
static (WorldCover) classification path and the ML-refined
classification path, so both always agree on class IDs,
names, and colors.
"""

LAND_COVER_LEGEND = {
    10: {"name": "Tree Cover", "color": "#006400"},
    20: {"name": "Shrubland", "color": "#ffbb22"},
    30: {"name": "Grassland", "color": "#ffff4c"},
    40: {"name": "Cropland", "color": "#f096ff"},
    50: {"name": "Built-up", "color": "#fa0000"},
    60: {"name": "Bare / Sparse Vegetation", "color": "#b4b4b4"},
    70: {"name": "Snow / Ice", "color": "#f0f0f0"},
    80: {"name": "Permanent Water", "color": "#0064c8"},
    90: {"name": "Herbaceous Wetland", "color": "#0096a0"},
    95: {"name": "Mangroves", "color": "#00cf75"},
    100: {"name": "Moss / Lichen", "color": "#fae6a0"},
}
