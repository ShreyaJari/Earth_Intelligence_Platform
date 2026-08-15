"""
compute_statistics.py

Compute land cover statistics.
"""

import time

import numpy as np


def compute_pixel_area_km2(classification):
    """
    Compute the real-world area of one pixel, in km^2.
    """

    x_res, y_res = classification.rio.resolution()

    x_res = abs(x_res)

    y_res = abs(y_res)

    crs = classification.rio.crs

    if crs is not None and crs.is_geographic:

        y_name = "y" if "y" in classification.dims else "latitude"

        mean_latitude = float(classification[y_name].values.mean())

        meters_per_degree_lat = 111_320.0

        meters_per_degree_lon = 111_320.0 * np.cos(np.radians(mean_latitude))

        pixel_width_m = x_res * meters_per_degree_lon

        pixel_height_m = y_res * meters_per_degree_lat

    else:

        pixel_width_m = x_res

        pixel_height_m = y_res

    return (pixel_width_m * pixel_height_m) / 1_000_000


def compute_classification_statistics(classification, legend):
    """
    Compute area/percentage/dominant-class statistics for a
    single classification raster.

    IMPORTANT: nodata pixels (from clipping to an irregular
    AOI, e.g. gaps in a coastal MultiPolygon) are excluded by
    checking membership in the legend's known class IDs — NOT
    by checking for NaN. Integer-typed rasters fill nodata
    with a real integer (commonly 0), which np.isnan() cannot
    detect, silently inflating pixel/area counts otherwise.
    """

    values = classification.values

    valid_class_ids = np.array(list(legend.keys()))

    valid_mask = np.isin(values, valid_class_ids)

    valid_pixels = values[valid_mask]

    unique_classes, counts = np.unique(
        valid_pixels,
        return_counts=True,
    )

    total_pixels = counts.sum()

    pixel_area_km2 = compute_pixel_area_km2(classification)

    area_per_class = {}

    percentage_per_class = {}

    dominant_class = None

    dominant_pixels = 0

    for class_id, count in zip(unique_classes, counts):

        class_info = legend.get(int(class_id))

        if class_info is None:

            continue

        class_name = class_info["name"]

        area = count * pixel_area_km2

        percentage = (count / total_pixels) * 100

        area_per_class[class_name] = round(area, 3)

        percentage_per_class[class_name] = round(
            percentage,
            2,
        )

        if count > dominant_pixels:

            dominant_pixels = count

            dominant_class = class_name

    return {
        "area_per_class": area_per_class,
        "percentage_per_class": percentage_per_class,
        "dominant_class": dominant_class,
        "number_of_classes": len(unique_classes),
        "total_area_km2": round(
            total_pixels * pixel_area_km2,
            3,
        ),
        "total_valid_pixels": int(total_pixels),
    }


def compute_statistics(
    landcover_product,
):
    """
    Compute statistics for the land cover products, including
    the ML classification's own statistics if it's present.
    """

    start = time.time()

    classification = landcover_product["products"]["classification"]

    legend = landcover_product["products"]["legend"]

    landcover_product["statistics"] = compute_classification_statistics(
        classification,
        legend,
    )

    ml_classification = landcover_product["products"].get("ml_classification")

    if ml_classification is not None:

        landcover_product["ml_statistics"] = compute_classification_statistics(
            ml_classification,
            legend,
        )

    landcover_product["processing"]["statistics_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return landcover_product
