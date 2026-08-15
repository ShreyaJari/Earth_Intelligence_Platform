"""
Earth Intelligence Platform
Satellite Engine

Main

Orchestrates the complete Satellite Engine workflow.
"""

from .build_grid import build_grid
from .cloud_mask import build_cloud_mask
from .false_colour import build_false_colour
from .group_acquisitions import group_acquisitions
from .load_imagery import load_imagery
from .metadata import build_metadata
from .prepare_imagery import prepare_imagery
from .quality import compute_quality
from .rank_acquisitions import rank_acquisitions
from .rgb import build_rgb
from .satellite_product import SatelliteProduct
from .search_scenes import search_scenes
from .select_acquisition import select_acquisition
from .validation import validate_request

# ============================================================
# Run Satellite Engine
# ============================================================


def run_satellite_engine(
    aoi,
    collection="sentinel-2-l2a",
    start_date=None,
    end_date=None,
    max_cloud_cover=20,
    resolution=10,
    bands=None,
):
    """
    Run the complete Satellite Engine.

    Parameters
    ----------
    aoi : dict
        Area of Interest produced by the Location Engine.

    collection : str

    start_date : str

    end_date : str

    max_cloud_cover : float

    resolution : float

    bands : list[str], optional

    Returns
    -------
    SatelliteProduct
    """

    # ---------------------------------------------------------
    # Validate Request
    # ---------------------------------------------------------

    request = validate_request(
        aoi=aoi,
        collection=collection,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=max_cloud_cover,
        resolution=resolution,
    )

    # ---------------------------------------------------------
    # Create Product
    # ---------------------------------------------------------

    product = SatelliteProduct(
        request=request,
    )

    # ---------------------------------------------------------
    # Search Scenes
    # ---------------------------------------------------------

    inventory = search_scenes(
        request,
    )

    # ---------------------------------------------------------
    # Group + Rank + Select Acquisition
    # ---------------------------------------------------------

    geometry = request.aoi["geometry"]["geometry"]

    acquisitions = group_acquisitions(
        inventory,
        geometry,
    )

    ranked_acquisitions = rank_acquisitions(
        acquisitions,
    )

    scene = select_acquisition(
        ranked_acquisitions,
    )

    product.scene = scene

    # ---------------------------------------------------------
    # Build Grid
    # ---------------------------------------------------------

    grid = build_grid(
        request,
    )

    product.grid = grid

    # ---------------------------------------------------------
    # Load Imagery
    # ---------------------------------------------------------

    imagery = load_imagery(
        scene,
        grid,
        bands=bands,
    )

    product.imagery.raw = imagery

    # ---------------------------------------------------------
    # Prepare Imagery
    # ---------------------------------------------------------

    prepared = prepare_imagery(
        imagery,
        request,
    )

    product.imagery.aoi = prepared

    # ---------------------------------------------------------
    # Cloud Mask  (NEW)
    # ---------------------------------------------------------

    cloud_mask, ml_cloud_percentage = build_cloud_mask(
        prepared,
    )

    product.cloud_mask = cloud_mask

    # ---------------------------------------------------------
    # Build Visualizations
    # ---------------------------------------------------------

    product.visualizations.rgb = build_rgb(
        prepared,
    )

    product.visualizations.false_colour = build_false_colour(
        prepared,
    )

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    product.metadata = build_metadata(
        prepared,
        scene,
    )

    # ---------------------------------------------------------
    # Quality Assessment
    # ---------------------------------------------------------

    product.quality = compute_quality(
        prepared,
        scene,
        ml_cloud_percentage=ml_cloud_percentage,  # NEW argument
    )
    # ---------------------------------------------------------
    # Return Product
    # ---------------------------------------------------------

    return product
