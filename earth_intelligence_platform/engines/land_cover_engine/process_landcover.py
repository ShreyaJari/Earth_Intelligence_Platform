"""
process_landcover.py

Generate derived land cover products.
"""

import time

import numpy as np


def process_landcover(
    classification,
    landcover_product,
):
    """
    Generate land cover products.

    Parameters
    ----------
    classification : xarray.DataArray

    landcover_product : dict

    Returns
    -------
    dict
    """

    start = time.time()

    legend = {
        10: {
            "name": "Tree Cover",
            "color": "#006400",
        },
        20: {
            "name": "Shrubland",
            "color": "#ffbb22",
        },
        30: {
            "name": "Grassland",
            "color": "#ffff4c",
        },
        40: {
            "name": "Cropland",
            "color": "#f096ff",
        },
        50: {
            "name": "Built-up",
            "color": "#fa0000",
        },
        60: {
            "name": "Bare / Sparse Vegetation",
            "color": "#b4b4b4",
        },
        70: {
            "name": "Snow / Ice",
            "color": "#f0f0f0",
        },
        80: {
            "name": "Permanent Water",
            "color": "#0064c8",
        },
        90: {
            "name": "Herbaceous Wetland",
            "color": "#0096a0",
        },
        95: {
            "name": "Mangroves",
            "color": "#00cf75",
        },
        100: {
            "name": "Moss / Lichen",
            "color": "#fae6a0",
        },
    }

    masks = {}

    for class_id in legend:

        masks[class_id] = classification == class_id

    landcover_product["products"] = {
        "classification": classification,
        "visualization": classification,
        "legend": legend,
        "masks": masks,
        "confidence": None,
    }

    landcover_product["processing"]["processing_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return landcover_product
