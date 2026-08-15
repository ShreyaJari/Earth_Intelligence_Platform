"""
Earth Intelligence Platform
Satellite Engine

Build Grid

Creates a projected spatial grid for loading satellite imagery.
"""

from odc.geo import Geometry
from odc.geo.geobox import GeoBox
from pyproj import CRS

from earth_intelligence_platform.engines.satellite_engine.satellite_product import Grid

# ============================================================
# Build Grid
# ============================================================


def build_grid(
    request,
):
    """
    Build a projected GeoBox for the AOI.

    Parameters
    ----------
    request : SatelliteRequest

    Returns
    -------
    Grid
    """

    geometry = request.aoi["geometry"]["geometry"]

    # ---------------------------------------------------------
    # Estimate UTM CRS
    # ---------------------------------------------------------

    centroid = geometry.centroid

    lon = centroid.x
    lat = centroid.y

    zone = int((lon + 180) / 6) + 1

    if lat >= 0:

        epsg = 32600 + zone

    else:

        epsg = 32700 + zone

    crs = CRS.from_epsg(epsg)

    print("\n========== GRID ==========")
    print("Estimated CRS :", crs.to_string())
    print("==========================")

    # ---------------------------------------------------------
    # Convert AOI to ODC Geometry
    # ---------------------------------------------------------

    odc_geom = Geometry(
        geometry.__geo_interface__,
        CRS.from_epsg(4326),
    )

    projected = odc_geom.to_crs(crs)

    # ---------------------------------------------------------
    # Create GeoBox
    # ---------------------------------------------------------

    geobox = GeoBox.from_geopolygon(
        projected,
        resolution=request.resolution,
    )

    # ---------------------------------------------------------
    # Build Grid Object
    # ---------------------------------------------------------

    grid = Grid(
        crs=str(crs),
        resolution=request.resolution,
        width=geobox.width,
        height=geobox.height,
        bounds={
            "left": geobox.extent.boundingbox.left,
            "bottom": geobox.extent.boundingbox.bottom,
            "right": geobox.extent.boundingbox.right,
            "top": geobox.extent.boundingbox.top,
        },
        geobox=geobox,
    )

    print("\n========== GRID ==========")
    print("Width      :", grid.width)
    print("Height     :", grid.height)
    print("Resolution :", grid.resolution)
    print("Bounds     :", grid.bounds)
    print("==========================\n")

    return grid
