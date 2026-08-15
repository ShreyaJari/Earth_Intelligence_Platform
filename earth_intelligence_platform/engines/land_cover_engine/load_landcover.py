"""
load_landcover.py

Downloads and clips land cover data.
"""

import time

import geopandas as gpd
import odc.stac
import planetary_computer
import rioxarray
from pystac_client import Client
from shapely.geometry import mapping

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


def load_landcover(
    aoi,
    dataset,
    landcover_product,
):
    """
    Download and clip the selected land cover dataset.

    Parameters
    ----------
    aoi : dict

    dataset : dict

    landcover_product : dict

    Returns
    -------
    tuple
        (classification, landcover_product)
    """

    start = time.time()

    catalog = Client.open(
        STAC_URL,
        modifier=planetary_computer.sign_inplace,
    )

    geometry = aoi["geometry"]["geometry"]

    # ---------------------------------------------------------
    # ESA WorldCover has been published as multiple global
    # releases (2020 and 2021 vintages). Without a datetime
    # filter, the search returns items from BOTH releases for
    # any AOI, which odc.stac.load() then loads as two separate
    # time steps — silently doubling every pixel/area count
    # downstream. Explicitly requesting the most recent release
    # avoids downloading and discarding the redundant one.
    # ---------------------------------------------------------

    search = catalog.search(
        collections=[dataset["stac_collection"]],
        intersects=geometry,
        datetime="2021-01-01/2021-12-31",
    )

    items = search.item_collection()

    classification = odc.stac.load(
        items,
        bands=["map"],
        geopolygon=geometry,
        chunks={},
    )

    classification = classification["map"]

    print("\n========== LAND COVER LOAD ==========")

    print("Time steps loaded:", classification.sizes.get("time", "no time dim"))

    print("Before clip:", dict(classification.sizes))

    # ---------------------------------------------------------
    # Safety net — collapse to one time step even if the
    # datetime filter above still returns more than one for
    # some reason (e.g. a future WorldCover release added with
    # overlapping date ranges).
    # ---------------------------------------------------------

    if "time" in classification.dims and classification.sizes["time"] > 1:

        print(
            f"WARNING: {classification.sizes['time']} time steps "
            "still present after datetime filter — selecting "
            "the most recent."
        )

        classification = classification.isel(time=-1)

    # ---------------------------------------------------------
    # geopolygon= above only sets the RECTANGULAR bounding
    # extent — it does not mask pixels outside the actual AOI
    # polygon. For irregular/multi-part AOIs (e.g. coastal
    # MultiPolygons with large gaps), this leaves in a lot of
    # area that was never part of the real AOI. Clip explicitly.
    # ---------------------------------------------------------

    aoi_gdf = gpd.GeoDataFrame(
        geometry=[geometry],
        crs="EPSG:4326",
    )

    classification = classification.rio.clip(
        aoi_gdf.geometry.apply(mapping),
        aoi_gdf.crs,
        drop=True,
    )

    print("After clip:", dict(classification.sizes))

    print("======================================\n")

    landcover_product["classification"] = classification

    landcover_product["metadata"] = {
        "collection": dataset["stac_collection"],
        "number_of_items": len(items),
        "crs": str(classification.rio.crs),
        "bounds": classification.rio.bounds(),
        "resolution": classification.rio.resolution(),
    }

    landcover_product["processing"]["download_time_seconds"] = round(
        time.time() - start, 2
    )

    return classification, landcover_product
