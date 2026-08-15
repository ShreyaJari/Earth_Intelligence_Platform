"""
landcover_engine.py

Main orchestration for the Land Cover Engine.
"""

from .compute_statistics import compute_statistics
from .landcover_product import create_landcover_product
from .load_landcover import load_landcover
from .logger import get_logger
from .ml_classification import build_ml_classification
from .process_landcover import process_landcover
from .select_dataset import select_dataset

from .validation import (
    validate_aoi,
    validate_dataset,
    validate_landcover,
    validate_products,
)


logger = get_logger()


def landcover_engine(
    aoi,
    catalog,
    satellite_product=None,
):
    """
    Execute the Land Cover Engine.

    Parameters
    ----------
    aoi : dict

    catalog : dict

    satellite_product : SatelliteProduct, optional
        If provided (Satellite Engine already run for this
        AOI), also computes a date-specific ML land cover
        classification alongside the static WorldCover result.
    """

    logger.info("Starting Land Cover Engine.")

    landcover_product = create_landcover_product()

    try:

        validate_aoi(aoi)

        dataset, landcover_product = select_dataset(
            catalog,
            landcover_product,
        )

        validate_dataset(dataset)

        classification, landcover_product = load_landcover(
            aoi,
            dataset,
            landcover_product,
        )

        validate_landcover(classification)

        landcover_product = process_landcover(
            classification,
            landcover_product,
        )

        validate_products(
            landcover_product["products"]
        )

        # ---------------------------------------------------------
        # ML Classification (optional) — must run BEFORE
        # compute_statistics, so ML statistics get computed too.
        # ---------------------------------------------------------

        if satellite_product is not None and satellite_product.imagery.aoi is not None:

            logger.info("Running ML land cover classification.")

            ml_classification, ml_metadata = build_ml_classification(
                satellite_product.imagery.aoi,
            )

            landcover_product["products"]["ml_classification"] = ml_classification

            landcover_product["ml_metadata"] = ml_metadata

        landcover_product = compute_statistics(
            landcover_product
        )

        landcover_product["success"] = True

        logger.info("Land Cover Engine completed successfully.")

    except Exception as e:

        logger.exception("Land Cover Engine failed.")

        landcover_product["errors"].append(str(e))

    return landcover_product