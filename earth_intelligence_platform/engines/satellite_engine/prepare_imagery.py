"""
Earth Intelligence Platform
Satellite Engine

Prepare Imagery

Prepares imagery for downstream processing by:

1. Validating CRS
2. Reprojecting the AOI
3. Clipping imagery
4. Removing nodata borders
5. Returning a clean AOI dataset
"""

import rioxarray
import geopandas as gpd

from shapely.geometry import mapping


# ============================================================
# Prepare Imagery
# ============================================================

def prepare_imagery(
    imagery,
    request,
):
    """
    Prepare imagery for downstream processing.

    Parameters
    ----------
    imagery : xarray.Dataset

    request : SatelliteRequest

    Returns
    -------
    xarray.Dataset
    """

    geometry = request.aoi["geometry"]["geometry"]

    print("\n========== PREPARE IMAGERY ==========")

    # ---------------------------------------------------------
    # Validate CRS
    # ---------------------------------------------------------

    if imagery.rio.crs is None:

        raise RuntimeError(
            "Imagery has no CRS."
        )

    print("Raster CRS :", imagery.rio.crs)

    # ---------------------------------------------------------
    # AOI
    # ---------------------------------------------------------

    aoi = gpd.GeoDataFrame(

        geometry=[geometry],

        crs="EPSG:4326",

    )

    aoi = aoi.to_crs(

        imagery.rio.crs

    )

    print("AOI CRS    :", aoi.crs)

    # ---------------------------------------------------------
    # Clip
    # ---------------------------------------------------------

    imagery = imagery.rio.clip(

        aoi.geometry.apply(mapping),

        aoi.crs,

        drop=True,

    )

    print("AOI clipped.")

    # ---------------------------------------------------------
    # Remove nodata borders
    # ---------------------------------------------------------

    imagery = imagery.rio.clip_box(

        *imagery.rio.bounds()

    )

    print("Borders cleaned.")

    # ---------------------------------------------------------
    # Validate dimensions
    # ---------------------------------------------------------

    if imagery.sizes["x"] == 0:

        raise RuntimeError(
            "Prepared imagery has zero width."
        )

    if imagery.sizes["y"] == 0:

        raise RuntimeError(
            "Prepared imagery has zero height."
        )

    print()

    print("Dataset Size")

    print(imagery.sizes)

    print()

    print("Bounds")

    print(imagery.rio.bounds())

    print()

    print("===============================\n")

    return imagery