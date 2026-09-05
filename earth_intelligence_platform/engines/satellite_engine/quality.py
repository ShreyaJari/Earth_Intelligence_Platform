"""
Earth Intelligence Platform
Satellite Engine

Quality

Computes quality metrics describing the downloaded imagery.
"""

import numpy as np

from earth_intelligence_platform.engines.satellite_engine.satellite_product import (
    Quality,
)

# ============================================================
# Compute Quality
# ============================================================


def compute_quality(
    imagery,
    scene,
    ml_cloud_percentage=0.0,
):
    """
    Compute quality metrics for imagery.

    Parameters
    ----------
    imagery : xarray.Dataset

    scene : Scene

    ml_cloud_percentage : float or None
        AOI-specific cloud percentage from the ML cloud mask.
        None if the ML cloud mask was skipped (e.g. on a
        lightweight deployment).

    Returns
    -------
    Quality
    """

    quality = Quality()

    band_name = list(imagery.data_vars)[0]

    image = imagery[band_name].isel(time=0).compute().values

    total_pixels = image.size

    valid_pixels = np.count_nonzero(np.isfinite(image))

    nodata_pixels = total_pixels - valid_pixels

    quality.valid_pixel_percentage = round(
        100 * valid_pixels / total_pixels,
        2,
    )

    quality.nodata_percentage = round(
        100 * nodata_pixels / total_pixels,
        2,
    )

    quality.cloud_cover = scene.cloud_cover

    quality.ml_cloud_percentage = ml_cloud_percentage

    print()

    print("Coverage")

    print("Valid Pixels :", valid_pixels)

    print("Total Pixels :", total_pixels)

    print("Coverage % :", 100 * valid_pixels / total_pixels)

    print()

    print("========== QUALITY ==========")

    print(
        "Valid Pixels :",
        quality.valid_pixel_percentage,
        "%",
    )

    print(
        "NoData Pixels:",
        quality.nodata_percentage,
        "%",
    )

    print(
        "Cloud Cover (Metadata):",
        quality.cloud_cover,
        "%",
    )

    if quality.ml_cloud_percentage is not None:

        print(
            "Cloud Cover (ML, AOI-measured):",
            quality.ml_cloud_percentage,
            "%",
        )

    else:

        print(
            "Cloud Cover (ML, AOI-measured): N/A "
            "(ML cloud detection disabled on this deployment)"
        )

    print("=============================\n")

    return quality