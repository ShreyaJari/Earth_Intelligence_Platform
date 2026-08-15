"""
Earth Intelligence Platform
Satellite Engine

RGB

Builds a natural colour RGB image from Sentinel-2 imagery.
"""

import numpy as np

from earth_intelligence_platform.engines.satellite_engine.normalize import (
    percentile_stretch,
    replace_nan,
    stack_rgb,
)

# ============================================================
# Build RGB
# ============================================================


def build_rgb(
    imagery,
):
    """
    Build a natural colour RGB image.

    Parameters
    ----------
    imagery : xarray.Dataset

    Returns
    -------
    numpy.ndarray
    """

    print("\n========== RGB ==========")

    required = [
        "B04",  # Red
        "B03",  # Green
        "B02",  # Blue
    ]

    for band in required:

        if band not in imagery:

            raise ValueError(f"{band} not found.")

    red = imagery["B04"].isel(time=0).compute().values

    green = imagery["B03"].isel(time=0).compute().values

    blue = imagery["B02"].isel(time=0).compute().values

    import matplotlib.pyplot as plt

    plt.figure(figsize=(6, 6))
    plt.imshow(red)
    plt.title("Raw Red Band")
    plt.colorbar()
    plt.show()

    red = replace_nan(red)

    green = replace_nan(green)

    blue = replace_nan(blue)

    red = percentile_stretch(red)

    green = percentile_stretch(green)

    blue = percentile_stretch(blue)

    rgb = stack_rgb(
        red,
        green,
        blue,
    )

    print("RGB Shape :", rgb.shape)

    print("RGB Type  :", rgb.dtype)

    print("=========================\n")

    return rgb
