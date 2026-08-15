"""
Earth Intelligence Platform
Terrain Engine

Validation Functions
"""


def validate_aoi(aoi):
    """
    Validate the Area of Interest.

    Parameters
    ----------
    aoi : dict
        Area of Interest.

    Raises
    ------
    ValueError
        If the AOI is invalid.
    """

    if aoi is None:
        raise ValueError("AOI is required.")

    if "geometry" not in aoi:
        raise ValueError("AOI geometry is missing.")


def validate_dataset(dataset):
    """
    Validate the selected terrain dataset.

    Parameters
    ----------
    dataset : dict
        Selected terrain dataset.

    Raises
    ------
    ValueError
        If the dataset is invalid.
    """

    if dataset is None:
        raise ValueError("No terrain dataset selected.")

    required_fields = ["id", "name", "provider", "stac_collection"]

    for field in required_fields:

        if field not in dataset:

            raise ValueError(f"Terrain dataset missing '{field}'.")


def validate_dem(dem):
    """
    Validate the downloaded DEM.

    Parameters
    ----------
    dem : xarray.Dataset
        Digital Elevation Model.

    Raises
    ------
    ValueError
        If the DEM is invalid.
    """

    if dem is None:
        raise ValueError("DEM was not loaded.")

    if len(dem.data_vars) == 0:
        raise ValueError("DEM contains no raster bands.")

    if "data" not in dem:
        raise ValueError("DEM is missing the 'data' band.")


def validate_products(products):
    """
    Validate the generated terrain products.

    Parameters
    ----------
    products : dict
        Terrain products.

    Raises
    ------
    ValueError
        If required terrain products are missing.
    """

    if products is None:
        raise ValueError("Terrain products were not generated.")

    required_products = ["elevation", "slope", "aspect", "hillshade"]

    for product in required_products:

        if product not in products:

            raise ValueError(f"Missing terrain product '{product}'.")
