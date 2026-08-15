"""
Earth Intelligence Platform
Terrain Engine

Load Digital Elevation Model (DEM)
"""

import time

import geopandas as gpd
import planetary_computer
import rioxarray
from odc.stac import load
from pystac_client import Client
from shapely.geometry import mapping


def load_dem(aoi, dataset, terrain_product):
    """
    Download and clip the Digital Elevation Model (DEM) for the Area of
    Interest (AOI).

    Parameters
    ----------
    aoi : dict
        Area of Interest.

    dataset : dict
        Selected terrain dataset.

    terrain_product : dict
        Terrain Product.

    Returns
    -------
    tuple
        DEM and updated Terrain Product.
    """

    start_time = time.time()

    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    geometry = aoi["geometry"]["geometry"]

    search = catalog.search(
        collections=[dataset["stac_collection"]], intersects=geometry
    )

    dem_scenes = list(search.items())

    if len(dem_scenes) == 0:

        raise RuntimeError("No DEM found for the selected Area of Interest.")

    dem = load(dem_scenes, bands=["data"], geopolygon=geometry, chunks={})

    print("\n========== DEM LOAD ==========")

    print("Time steps loaded:", dem.sizes.get("time", "no time dim"))

    print("Before clip:", dict(dem.sizes))

    # ---------------------------------------------------------
    # Safety net — collapse to one time step if the DEM
    # collection ever returns more than one (Copernicus DEM is
    # normally static/single-version, but confirm rather than
    # assume, given the same class of bug already found in
    # Land Cover's WorldCover data).
    # ---------------------------------------------------------

    if "time" in dem.dims and dem.sizes["time"] > 1:

        print(
            f"WARNING: {dem.sizes['time']} time steps present "
            "— selecting the most recent."
        )

        dem = dem.isel(time=-1)

    # ---------------------------------------------------------
    # geopolygon= above only sets the RECTANGULAR bounding
    # extent — it does not mask pixels outside the actual AOI
    # polygon. For irregular/multi-part AOIs, this silently
    # includes real elevation data from OUTSIDE the AOI
    # (neighboring terrain), inflating mean_elevation,
    # mean_slope, and valid_pixel_count. Clip explicitly.
    # ---------------------------------------------------------

    aoi_gdf = gpd.GeoDataFrame(
        geometry=[geometry],
        crs="EPSG:4326",
    )

    dem = dem.rio.clip(
        aoi_gdf.geometry.apply(mapping),
        aoi_gdf.crs,
        drop=True,
    )

    print("After clip:", dict(dem.sizes))

    print("================================\n")

    elevation = dem["data"].squeeze()

    terrain_product["dem"] = dem

    terrain_product["metadata"] = {
        "crs": str(elevation.rio.crs),
        "width": elevation.sizes["longitude"],
        "height": elevation.sizes["latitude"],
        "resolution": {
            "x": float(abs(elevation.longitude[1] - elevation.longitude[0])),
            "y": float(abs(elevation.latitude[1] - elevation.latitude[0])),
        },
    }

    terrain_product["processing"]["download_time_seconds"] = round(
        time.time() - start_time, 2
    )

    return dem, terrain_product
