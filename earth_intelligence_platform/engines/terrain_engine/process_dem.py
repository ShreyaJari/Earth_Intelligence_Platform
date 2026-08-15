"""
Earth Intelligence Platform
Terrain Engine

Generate Terrain Products
"""

import time

import numpy as np
import xarray as xr
from scipy.ndimage import sobel, gaussian_filter


SMOOTHING_SIGMA = 8  # pixels — see note below on choosing this value


def process_dem(dem, terrain_product):
    """
    Generate terrain products from the Digital Elevation Model (DEM).

    Version 1 generates:

    - Elevation
    - Slope
    - Aspect
    - Hillshade

    Parameters
    ----------
    dem : xarray.Dataset
        Digital Elevation Model.

    terrain_product : dict
        Terrain Product.

    Returns
    -------
    dict
        Updated Terrain Product.
    """

    start_time = time.time()

    # Elevation
    elevation = dem["data"].squeeze()

    print("Elevation min/max:", np.nanmin(elevation.values), np.nanmax(elevation.values))
    print("Values below -50:", np.sum(elevation.values < -50))
    print("Values above 500:", np.sum(elevation.values > 500))

    # ---------------------------------------------------------
    # Light smoothing before gradient calculation.
    #
    # Sobel-based slope amplifies high-frequency noise —
    # building edges, in the case of a DSM-based Copernicus
    # DEM, get read as artificially steep "cliffs" even though
    # they aren't real terrain. Smoothing suppresses this
    # high-frequency signal while preserving genuine
    # larger-scale topography (hills, valleys).
    #
    # This does NOT fully solve the underlying DSM-vs-DTM
    # issue (see README limitations) — it reduces the
    # artifact's severity, combined with using the coarser
    # 90m DEM resolution.
    # ---------------------------------------------------------
    elevation_values = elevation.values

    nan_mask = np.isnan(elevation_values)

    if nan_mask.any():

        filled = np.where(nan_mask, np.nanmean(elevation_values), elevation_values)

        smoothed = gaussian_filter(filled, sigma=SMOOTHING_SIGMA)

        smoothed[nan_mask] = np.nan

    else:

        smoothed = gaussian_filter(elevation_values, sigma=SMOOTHING_SIGMA)

    smoothed_elevation_values = smoothed

    print("Elevation std BEFORE smoothing:", np.nanstd(elevation_values))
    print("Elevation std AFTER smoothing:", np.nanstd(smoothed_elevation_values))
    print(
        "Std reduction:",
        round(100 * (1 - np.nanstd(smoothed_elevation_values) / np.nanstd(elevation_values)), 1),
        "%",
    )

    # Calculate terrain gradients (on the SMOOTHED elevation)
    dz_dx = sobel(
        smoothed_elevation_values,
        axis=1
    ) / 8.0

    dz_dy = sobel(
        smoothed_elevation_values,
        axis=0
    ) / 8.0

    # Slope (degrees)
    slope = np.degrees(

        np.arctan(

            np.sqrt(

                dz_dx ** 2 +

                dz_dy ** 2

            )

        )

    )

    # Aspect (degrees)
    aspect = np.degrees(

        np.arctan2(

            -dz_dx,

            dz_dy

        )

    )

    aspect = np.where(

        aspect < 0,

        aspect + 360,

        aspect

    )

    # Hillshade
    azimuth = np.radians(315)

    altitude = np.radians(45)

    slope_rad = np.radians(slope)

    aspect_rad = np.radians(aspect)

    hillshade = 255 * (

        np.cos(altitude)

        * np.cos(slope_rad)

        +

        np.sin(altitude)

        * np.sin(slope_rad)

        * np.cos(

            azimuth - aspect_rad

        )

    )

    hillshade = np.clip(

        hillshade,

        0,

        255

    )

    terrain_product["products"] = {

        "elevation": elevation,   # kept RAW (unsmoothed) for display/stats — only slope/aspect/hillshade use the smoothed version

        "slope": xr.DataArray(

            slope,

            coords=elevation.coords,

            dims=elevation.dims,

            attrs={

                "units": "degrees"

            }

        ),

        "aspect": xr.DataArray(

            aspect,

            coords=elevation.coords,

            dims=elevation.dims,

            attrs={

                "units": "degrees"

            }

        ),

        "hillshade": xr.DataArray(

            hillshade,

            coords=elevation.coords,

            dims=elevation.dims,

            attrs={

                "units": "0-255"

            }

        )

    }

    terrain_product["processing"][

        "processing_time_seconds"

    ] = round(

        time.time() - start_time,

        2

    )

    return terrain_product