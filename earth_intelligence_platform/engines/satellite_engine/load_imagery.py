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

MAX_PIXELS = 25_000_000  # deploy-only safety cap for free-tier memory limits


def load_imagery(
    scene: Scene,
    grid: Grid,
    bands=None,
):
    """
    Load and mosaic calibrated satellite imagery for all
    tiles belonging to the selected acquisition.

    On memory-constrained deployments, large grids are
    automatically downsampled (via a coarser GeoBox) to keep
    peak memory usage within free-tier hosting limits. This
    only affects the resolution of the loaded imagery, not the
    original Grid object used elsewhere in the pipeline.

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

    # ---------------------------------------------------------
    # Memory safety: downsample the load geobox for very large
    # grids, so peak memory doesn't exceed free-tier hosting
    # limits. Uses a coarser GeoBox at load time only — the
    # original grid.geobox and grid.resolution are untouched.
    # ---------------------------------------------------------

    total_pixels = grid.width * grid.height

    load_geobox = grid.geobox

    load_resolution = grid.resolution

    if total_pixels > MAX_PIXELS:

        downsample_factor = int((total_pixels / MAX_PIXELS) ** 0.5) + 1

        print(

            f"Large grid ({total_pixels:,} px) — downsampling "

            f"{downsample_factor}x for memory safety on this "

            "deployment."

        )

        load_geobox = grid.geobox.zoom_out(downsample_factor)

        load_resolution = grid.resolution * downsample_factor

    print("\n========== LOAD IMAGERY ==========")
    print("Acquisition Date :", scene.acquisition_date)
    print("Tiles            :", scene.tile_ids)
    print("Tile Count       :", len(scene.stac_items))
    print("Coverage         :", scene.coverage_percent, "%")
    print("Bands            :", bands)
    print("Resolution       :", load_resolution)
    print("===================================\n")
    start = time.time()
    signed_items = [
        planetary_computer.sign(item)
        for item in scene.stac_items
    ]
    imagery = load(
        signed_items,
        bands=bands,
        geobox=load_geobox,
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