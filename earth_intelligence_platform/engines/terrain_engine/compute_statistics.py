"""
Earth Intelligence Platform
Terrain Engine

Compute Terrain Statistics
"""

import time

import numpy as np


# ============================================================
# Circular Statistics (for Aspect)
# ============================================================

def circular_mean_degrees(values_degrees):
    """
    Compute the circular mean of a set of angles in degrees.
    """

    radians = np.radians(values_degrees)

    mean_sin = np.mean(np.sin(radians))

    mean_cos = np.mean(np.cos(radians))

    mean_angle = np.degrees(
        np.arctan2(mean_sin, mean_cos)
    )

    return float(mean_angle % 360)


def circular_std_degrees(values_degrees):
    """
    Compute the circular standard deviation of a set of angles
    in degrees.
    """

    radians = np.radians(values_degrees)

    mean_sin = np.mean(np.sin(radians))

    mean_cos = np.mean(np.cos(radians))

    resultant_length = np.sqrt(mean_sin ** 2 + mean_cos ** 2)

    resultant_length = np.clip(resultant_length, 1e-12, 1.0)

    circular_std_radians = np.sqrt(
        -2 * np.log(resultant_length)
    )

    return float(np.degrees(circular_std_radians))


# ============================================================
# Slope Area Thresholds
#
# Landslide susceptibility literature commonly treats slope
# as a THRESHOLD effect rather than a linear one — shallow
# landslide likelihood increases sharply above roughly 25-30
# degrees (varies by soil/rock type, this is a simplification,
# not a geotechnically validated threshold for this specific
# AOI). An AOI-WIDE MEAN slope is a poor proxy for this: a
# small steep minority within an otherwise flat AOI can pull
# the mean up disproportionately, while the AREA actually at
# risk (the steep minority itself) is what geotechnically
# matters. Computing percentage of AOI area above threshold(s)
# is a more defensible aggregation, consistent with how
# susceptibility mapping is typically approached.
# ============================================================

SLOPE_THRESHOLDS_DEGREES = [15, 25, 35]


def compute_slope_area_percentages(slope_values):
    """
    Compute the percentage of valid slope pixels exceeding
    each threshold in SLOPE_THRESHOLDS_DEGREES.

    Parameters
    ----------
    slope_values : numpy.ndarray
        Valid (non-NaN) slope values, in degrees.

    Returns
    -------
    dict
        {"percentage_above_15_degrees": ..., ...}
    """

    if slope_values.size == 0:

        return {

            f"percentage_above_{threshold}_degrees": 0.0

            for threshold in SLOPE_THRESHOLDS_DEGREES

        }

    print(

        f"Slope > 25°: {int(np.sum(slope_values > 25))} of "

        f"{slope_values.size} pixels "

        f"({100 * np.mean(slope_values > 25):.1f}%)"

    )

    return {

        f"percentage_above_{threshold}_degrees": round(

            100 * float(np.mean(slope_values > threshold)),

            2,

        )

        for threshold in SLOPE_THRESHOLDS_DEGREES

    }

# ============================================================
# Compute Statistics
# ============================================================

def compute_statistics(terrain_product):
    """
    Compute summary statistics for each terrain product.

    Parameters
    ----------
    terrain_product : dict
        Terrain Product.

    Returns
    -------
    dict
        Updated Terrain Product.
    """

    start_time = time.time()

    statistics = {}

    for product_name, layer in terrain_product["products"].items():

        values = layer.values

        valid_values = values[np.isfinite(values)]

        if valid_values.size == 0:

            statistics[product_name] = {

                "minimum": None,

                "maximum": None,

                "mean": None,

                "standard_deviation": None,

                "valid_pixel_count": 0,

            }

            if product_name == "slope":

                statistics[product_name].update(

                    compute_slope_area_percentages(valid_values)

                )

            continue

        if product_name == "aspect":

            statistics[product_name] = {

                "minimum": float(np.min(valid_values)),

                "maximum": float(np.max(valid_values)),

                "mean": circular_mean_degrees(valid_values),

                "standard_deviation": circular_std_degrees(valid_values),

                "valid_pixel_count": int(valid_values.size),

            }

        else:

            statistics[product_name] = {

                "minimum": float(np.min(valid_values)),

                "maximum": float(np.max(valid_values)),

                "mean": float(np.mean(valid_values)),

                "standard_deviation": float(np.std(valid_values)),

                "valid_pixel_count": int(valid_values.size),

            }

        if product_name == "slope":

            statistics[product_name].update(

                compute_slope_area_percentages(valid_values)

            )

    terrain_product["statistics"] = statistics

    terrain_product["processing"][
        "statistics_time_seconds"
    ] = round(

        time.time() - start_time,

        2

    )

    return terrain_product