"""
Earth Intelligence Platform
Satellite Engine

Validation

Validates all inputs to the Satellite Engine.
"""

from datetime import datetime

from earth_intelligence_platform.engines.satellite_engine.satellite_product import (
    SatelliteRequest,
)

SUPPORTED_COLLECTIONS = {
    "sentinel-2-l2a",
    "landsat-c2-l2",
}


# ============================================================
# Validate AOI
# ============================================================


def validate_aoi(aoi):
    """
    Validate the AOI object.
    """

    if aoi is None:

        raise ValueError("AOI cannot be None.")

    if not isinstance(aoi, dict):

        raise TypeError("AOI must be a dictionary.")

    required = [
        "identity",
        "geometry",
        "spatial",
    ]

    for key in required:

        if key not in aoi:

            raise KeyError(f"AOI missing '{key}'.")

    if "geometry" not in aoi["geometry"]:

        raise KeyError("AOI geometry missing shapely geometry.")


# ============================================================
# Validate Collection
# ============================================================


def validate_collection(collection):
    """
    Validate satellite collection.
    """

    if collection not in SUPPORTED_COLLECTIONS:

        raise ValueError(f"Unsupported collection: {collection}")


# ============================================================
# Validate Dates
# ============================================================


def validate_dates(
    start_date,
    end_date,
):
    """
    Validate ISO date strings.
    """

    if start_date is not None:

        datetime.fromisoformat(start_date)

    if end_date is not None:

        datetime.fromisoformat(end_date)

    if start_date is not None and end_date is not None:

        if start_date > end_date:

            raise ValueError("Start date must be before end date.")


# ============================================================
# Validate Cloud Cover
# ============================================================


def validate_cloud_cover(
    cloud_cover,
):
    """
    Validate cloud cover threshold.
    """

    if cloud_cover < 0:

        raise ValueError("Cloud cover cannot be negative.")

    if cloud_cover > 100:

        raise ValueError("Cloud cover cannot exceed 100.")


# ============================================================
# Validate Resolution
# ============================================================


def validate_resolution(
    resolution,
):
    """
    Validate requested resolution.
    """

    if resolution <= 0:

        raise ValueError("Resolution must be positive.")


# ============================================================
# Build Validated Request
# ============================================================


def validate_request(
    aoi,
    collection="sentinel-2-l2a",
    start_date=None,
    end_date=None,
    max_cloud_cover=20,
    resolution=10,
):
    """
    Validate all Satellite Engine inputs.

    Returns
    -------
    SatelliteRequest
    """

    validate_aoi(aoi)

    validate_collection(collection)

    validate_dates(
        start_date,
        end_date,
    )

    validate_cloud_cover(
        max_cloud_cover,
    )

    validate_resolution(
        resolution,
    )

    return SatelliteRequest(
        aoi=aoi,
        collection=collection,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=max_cloud_cover,
        resolution=resolution,
    )
