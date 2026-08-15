"""
validation.py

Validation functions for the Land Cover Engine.
"""


def validate_aoi(aoi):
    """
    Validate the Area of Interest (AOI).

    Parameters
    ----------
    aoi : dict

    Raises
    ------
    ValueError
        If the AOI is invalid.
    """

    if aoi is None:
        raise ValueError("AOI cannot be None.")

    if not isinstance(aoi, dict):
        raise ValueError("AOI must be a dictionary.")

    if "geometry" not in aoi:
        raise ValueError("AOI must contain a 'geometry' field.")


def validate_dataset(dataset):
    """
    Validate the selected land cover dataset.

    Parameters
    ----------
    dataset : dict

    Raises
    ------
    ValueError
        If the dataset is invalid.
    """

    if dataset is None:
        raise ValueError("Dataset selection failed.")

    if not isinstance(dataset, dict):
        raise ValueError("Dataset must be a dictionary.")

    required_fields = ["name", "category", "priority"]

    for field in required_fields:

        if field not in dataset:

            raise ValueError(f"Dataset missing required field: '{field}'.")


def validate_landcover(classification):
    """
    Validate the downloaded land cover raster.

    Parameters
    ----------
    classification : xarray.DataArray

    Raises
    ------
    ValueError
        If the raster is invalid.
    """

    if classification is None:

        raise ValueError("Land cover raster is empty.")

    if getattr(classification, "size", 0) == 0:

        raise ValueError("Land cover raster contains no pixels.")


def validate_products(products):
    """
    Validate generated land cover products.

    Parameters
    ----------
    products : dict

    Raises
    ------
    ValueError
        If products are invalid.
    """

    if not isinstance(products, dict):

        raise ValueError("Products must be a dictionary.")

    if products.get("classification") is None:

        raise ValueError("Classification product was not created.")

    if products.get("legend") is None:

        raise ValueError("Legend was not created.")
