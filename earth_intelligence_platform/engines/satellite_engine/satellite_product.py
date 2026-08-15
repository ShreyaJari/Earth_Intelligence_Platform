"""
Earth Intelligence Platform
Satellite Engine

Satellite Product

Defines the data structures used throughout the Satellite Engine.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import xarray as xr

# ============================================================
# Request
# ============================================================


@dataclass
class SatelliteRequest:
    """
    User request sent to the Satellite Engine.
    """

    aoi: Dict[str, Any]

    collection: str = "sentinel-2-l2a"

    start_date: Optional[str] = None

    end_date: Optional[str] = None

    max_cloud_cover: float = 20.0

    resolution: float = 10.0


# ============================================================
# Scene
# ============================================================


@dataclass
class Scene:
    """
    Information about the selected satellite acquisition.
    """

    scene_id: str = ""

    acquisition_date: str = ""

    collection: str = ""

    provider: str = ""

    cloud_cover: float = 0.0

    stac_items: List[Any] = field(default_factory=list)  # was: stac_item

    tile_ids: List[str] = field(default_factory=list)  # NEW

    coverage_percent: float = 0.0  # NEW


# ============================================================
# Grid
# ============================================================


@dataclass
class Grid:
    """
    Spatial grid used to load imagery.
    """

    crs: str = ""

    resolution: float = 10.0

    width: int = 0

    height: int = 0

    bounds: Dict[str, float] = field(default_factory=dict)

    geobox: Any = None


# ============================================================
# Imagery
# ============================================================


@dataclass
class Imagery:
    """
    Loaded imagery.
    """

    raw: Optional[xr.Dataset] = None

    aoi: Optional[xr.Dataset] = None


# ============================================================
# Visualizations
# ============================================================


@dataclass
class Visualizations:
    """
    Images ready for display.
    """

    rgb: Optional[np.ndarray] = None

    false_colour: Optional[np.ndarray] = None


# ============================================================
# Metadata
# ============================================================


@dataclass
class Metadata:
    """
    Metadata describing the imagery.
    """

    bands: List[str] = field(default_factory=list)

    processing_time: float = 0.0

    download_time: float = 0.0


# ============================================================
# Quality
# ============================================================


@dataclass
class Quality:
    """
    Quality assessment of the imagery.
    """

    nodata_percentage: float = 0.0

    valid_pixel_percentage: float = 0.0

    cloud_cover: float = 0.0


# ============================================================
# Satellite Product
# ============================================================


@dataclass
class SatelliteProduct:
    """
    Final output produced by the Satellite Engine.
    """

    request: SatelliteRequest

    scene: Scene = field(default_factory=Scene)

    grid: Grid = field(default_factory=Grid)

    imagery: Imagery = field(default_factory=Imagery)

    visualizations: Visualizations = field(default_factory=Visualizations)

    metadata: Metadata = field(default_factory=Metadata)

    quality: Quality = field(default_factory=Quality)


@dataclass
class Quality:
    """
    Quality assessment of the imagery.
    """

    nodata_percentage: float = 0.0

    valid_pixel_percentage: float = 0.0

    cloud_cover: float = 0.0

    ml_cloud_percentage: float = 0.0  # NEW


@dataclass
class SatelliteProduct:
    """
    Final output produced by the Satellite Engine.
    """

    request: SatelliteRequest

    scene: Scene = field(default_factory=Scene)

    grid: Grid = field(default_factory=Grid)

    imagery: Imagery = field(default_factory=Imagery)

    visualizations: Visualizations = field(default_factory=Visualizations)

    metadata: Metadata = field(default_factory=Metadata)

    quality: Quality = field(default_factory=Quality)

    cloud_mask: Any = None  # NEW — per-pixel cloud probability array
