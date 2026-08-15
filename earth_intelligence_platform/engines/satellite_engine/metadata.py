"""
Earth Intelligence Platform
Satellite Engine

Metadata

Builds metadata describing the downloaded imagery.
"""

from earth_intelligence_platform.engines.satellite_engine.satellite_product import (
    Metadata,
)

# ============================================================
# Build Metadata
# ============================================================


def build_metadata(
    imagery,
    scene,
    load_time=0.0,
):
    """
    Build metadata for the imagery.

    Parameters
    ----------
    imagery : xarray.Dataset

    scene : Scene

    load_time : float

    Returns
    -------
    Metadata
    """

    metadata = Metadata()

    metadata.bands = list(imagery.data_vars)

    metadata.download_time = load_time

    metadata.processing_time = 0.0

    return metadata
