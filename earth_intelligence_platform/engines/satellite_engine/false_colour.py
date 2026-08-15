"""
Earth Intelligence Platform
Satellite Engine

False Colour

Builds a false colour composite from Sentinel-2 imagery.

Band Combination

    Red   = B08 (Near Infrared)
    Green = B04 (Red)
    Blue  = B03 (Green)
"""

from earth_intelligence_platform.engines.satellite_engine.normalize import (
    percentile_stretch,
    replace_nan,
    stack_rgb,
)

# ============================================================
# Build False Colour
# ============================================================


def build_false_colour(
    imagery,
):
    """
    Build a false colour composite.

    Parameters
    ----------
    imagery : xarray.Dataset

    Returns
    -------
    numpy.ndarray
    """

    print("\n========== FALSE COLOUR ==========")

    required = [
        "B08",  # NIR
        "B04",  # Red
        "B03",  # Green
    ]

    for band in required:

        if band not in imagery:

            raise ValueError(f"{band} not found.")

    nir = imagery["B08"].isel(time=0).compute().values

    red = imagery["B04"].isel(time=0).compute().values

    green = imagery["B03"].isel(time=0).compute().values

    nir = replace_nan(nir)

    red = replace_nan(red)

    green = replace_nan(green)

    nir = percentile_stretch(nir)

    red = percentile_stretch(red)

    green = percentile_stretch(green)

    false_colour = stack_rgb(
        nir,
        red,
        green,
    )

    print("Image Shape :", false_colour.shape)

    print("Image Type  :", false_colour.dtype)

    print("===============================\n")

    return false_colour
