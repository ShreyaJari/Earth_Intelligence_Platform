"""
Earth Intelligence Platform
Satellite Engine

Load Imagery

Downloads calibrated imagery from the Microsoft Planetary
Computer using a predefined GeoBox.
"""

import time

import planetary_computer
from odc.stac import load

from earth_intelligence_platform.engines.satellite_engine.satellite_product import (
    Scene,
    Grid,
)


# ============================================================
# Load Imagery
# ============================================================

def load_imagery(
    scene: Scene,
    grid: Grid,
    bands=None,
):
    """
    Load and mosaic calibrated satellite imagery for all
    tiles belonging to the selected acquisition.

    Parameters
    ----------
    scene : Scene

    grid : Grid

    bands : list[str], optional

    Returns
    -------
    xarray.Dataset
    """

    if bands is None:

        bands = [

            "B02",   # Blue

            "B03",   # Green

            "B04",   # Red

            "B08",   # Near Infrared

            "B11",   # Short-Wave Infrared 1 (20m native, resampled to grid)

            "B12",   # Short-Wave Infrared 2 (20m native, resampled to grid)

        ]

    if not scene.stac_items:

        raise RuntimeError(

            "Scene has no STAC items to load. "

            "select_acquisition() may not have populated "

            "scene.stac_items correctly."

        )

    print("\n========== LOAD IMAGERY ==========")

    print("Acquisition Date :", scene.acquisition_date)

    print("Tiles            :", scene.tile_ids)

    print("Tile Count       :", len(scene.stac_items))

    print("Coverage         :", scene.coverage_percent, "%")

    print("Bands            :", bands)

    print("Resolution       :", grid.resolution)

    print("===================================\n")

    start = time.time()

    signed_items = [

        planetary_computer.sign(item)

        for item in scene.stac_items

    ]

    imagery = load(

        signed_items,

        bands=bands,

        geobox=grid.geobox,

        groupby="solar_day",

        resampling="bilinear",  # smoother resampling for 20m SWIR bands onto the 10m grid

        chunks={

            "x": 1024,

            "y": 1024,

        },

    )

    if imagery is None:

        raise RuntimeError(

            "Unable to load imagery."

        )

    if "time" not in imagery.dims or imagery.sizes.get("time", 0) == 0:

        raise RuntimeError(

            "Loaded imagery has no time steps. "

            "Check that the selected items share a solar day."

        )

    elapsed = round(

        time.time() - start,

        2,

    )

    print("Imagery loaded successfully.")

    print("Load time   :", elapsed, "seconds")

    print("Time steps  :", imagery.sizes.get("time"))

    print()

    print(imagery)

    return imagery