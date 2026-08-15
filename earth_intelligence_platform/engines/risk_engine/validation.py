"""
validation.py

Validation utilities for the Risk Engine.
"""


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


def validate_satellite(satellite_product):
    """
    Validate Satellite Engine output.

    The Satellite Engine returns a SatelliteProduct dataclass,
    not a dict — it has no "success" key/field. Validity is
    checked structurally instead: a scene and quality metrics
    must be present.
    """

    if satellite_product is None:
        raise ValueError("Satellite product is None.")

    if satellite_product.scene is None:

        raise ValueError("Satellite Engine did not select a scene.")

    if satellite_product.quality is None:

        raise ValueError("Satellite Engine did not compute quality metrics.")


def validate_products(
    terrain_product,
    landcover_product,
    weather_product,
    satellite_product,
):
    """
    Validate all engine outputs.
    """

    validate_terrain(terrain_product)

    validate_landcover(landcover_product)

    validate_weather(weather_product)

    validate_satellite(satellite_product)
