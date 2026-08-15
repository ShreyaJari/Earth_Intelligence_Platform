"""
validation.py

Validation utilities for the Earth Intelligence Engine.
"""


def validate_location(location_product):
    """
    Validate Location Engine output.

    location_product is the AOI dict — it has no "success"
    key. Validity is checked structurally instead.
    """

    if location_product is None:
        raise ValueError("Location product is None.")

    required = ["identity", "geometry", "spatial"]

    for key in required:

        if key not in location_product:

            raise ValueError(f"Location product missing '{key}'.")


def validate_discovery(discovery_product):
    """
    Validate Data Discovery Engine output.

    discovery_product is the catalog dict — it has no
    "success" key. Validity is checked structurally instead.
    """

    if discovery_product is None:
        raise ValueError("Discovery product is None.")

    if "datasets" not in discovery_product:

        raise ValueError("Discovery product missing 'datasets'.")

    if len(discovery_product["datasets"]) == 0:

        raise ValueError("Discovery product contains no datasets.")


def validate_satellite(satellite_product):
    """
    Validate Satellite Engine output.

    The Satellite Engine returns a SatelliteProduct dataclass,
    not a dict — it has no "success" key/field. Validity is
    checked structurally instead.
    """

    if satellite_product is None:
        raise ValueError("Satellite product is None.")

    if satellite_product.scene is None:

        raise ValueError("Satellite Engine did not select a scene.")

    if satellite_product.quality is None:

        raise ValueError("Satellite Engine did not compute quality metrics.")


def validate_terrain(terrain_product):
    """
    Validate Terrain Engine output.
    """

    if terrain_product is None:
        raise ValueError("Terrain product is None.")

    if not terrain_product["success"]:
        raise ValueError("Terrain Engine was unsuccessful.")


def validate_landcover(landcover_product):
    """
    Validate Land Cover Engine output.
    """

    if landcover_product is None:
        raise ValueError("Land Cover product is None.")

    if not landcover_product["success"]:
        raise ValueError("Land Cover Engine was unsuccessful.")


def validate_weather(weather_product):
    """
    Validate Weather Engine output.
    """

    if weather_product is None:
        raise ValueError("Weather product is None.")

    if not weather_product["success"]:
        raise ValueError("Weather Engine was unsuccessful.")


def validate_risk(risk_product):
    """
    Validate Risk Engine output.
    """

    if risk_product is None:
        raise ValueError("Risk product is None.")

    if not risk_product["success"]:
        raise ValueError("Risk Engine was unsuccessful.")


def validate_products(
    location_product,
    discovery_product,
    satellite_product,
    terrain_product,
    landcover_product,
    weather_product,
    risk_product,
):
    """
    Validate all engine outputs.
    """

    validate_location(location_product)

    validate_discovery(discovery_product)

    validate_satellite(satellite_product)

    validate_terrain(terrain_product)

    validate_landcover(landcover_product)

    validate_weather(weather_product)

    validate_risk(risk_product)
