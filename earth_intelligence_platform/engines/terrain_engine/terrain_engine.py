"""
Earth Intelligence Platform
Terrain Engine

Terrain Engine Orchestrator
"""

from .compute_statistics import compute_statistics
from .load_dem import load_dem
from .logger import get_logger
from .process_dem import process_dem
from .select_dataset import select_dataset
from .terrain_product import create_terrain_product
from .validation import validate_aoi, validate_dataset, validate_dem, validate_products

logger = get_logger()


def terrain_engine(aoi, catalog):
    """
    Run the Terrain Engine.

    Parameters
    ----------
    aoi : dict
        Area of Interest.

    catalog : dict
        Earth Intelligence Catalog.

    Returns
    -------
    dict
        Terrain Product.
    """

    terrain_product = create_terrain_product()

    try:

        logger.info("Starting Terrain Engine.")

        # ---------------------------------------------------------
        # Validate AOI
        # ---------------------------------------------------------

        logger.info("Validating AOI.")

        validate_aoi(aoi)

        # ---------------------------------------------------------
        # Select Terrain Dataset
        # ---------------------------------------------------------

        logger.info("Selecting terrain dataset.")

        dataset, terrain_product = select_dataset(catalog, terrain_product)

        validate_dataset(dataset)

        # ---------------------------------------------------------
        # Download DEM
        # ---------------------------------------------------------

        logger.info("Downloading DEM.")

        dem, terrain_product = load_dem(aoi, dataset, terrain_product)

        validate_dem(dem)

        # ---------------------------------------------------------
        # Generate Terrain Products
        # ---------------------------------------------------------

        logger.info("Generating terrain products.")

        terrain_product = process_dem(dem, terrain_product)

        validate_products(terrain_product["products"])

        # ---------------------------------------------------------
        # Compute Statistics
        # ---------------------------------------------------------

        logger.info("Computing terrain statistics.")

        terrain_product = compute_statistics(terrain_product)

        terrain_product["success"] = True

        logger.info("Terrain Engine completed successfully.")

    except Exception as e:

        terrain_product["success"] = False

        terrain_product["errors"].append(f"{type(e).__name__}: {e}")

        logger.exception("Terrain Engine failed.")

    return terrain_product
