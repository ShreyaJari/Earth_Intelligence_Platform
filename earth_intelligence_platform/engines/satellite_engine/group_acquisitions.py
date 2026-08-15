"""
Earth Intelligence Platform
Satellite Engine

Group Acquisitions

Groups candidate STAC Items into Acquisitions — sets of
tiles sharing an acquisition date whose combined footprint
is evaluated against the AOI as a whole.
"""

from dataclasses import dataclass, field
from typing import Any, List

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

from earth_intelligence_platform.engines.satellite_engine.geo_utils import (
    estimate_utm_crs,
)

# ============================================================
# Acquisition
# ============================================================


@dataclass
class Acquisition:
    """
    A group of STAC Items sharing an acquisition date.
    """

    date: str = ""

    items: List[Any] = field(default_factory=list)

    tile_ids: List[str] = field(default_factory=list)

    footprint: Any = None

    coverage_percent: float = 0.0

    cloud_cover: float = 0.0


# ============================================================
# Group Acquisitions
# ============================================================


def group_acquisitions(
    inventory: pd.DataFrame,
    aoi_geometry,
):
    """
    Group candidate scenes into acquisitions and compute
    AOI coverage for each.

    Parameters
    ----------
    inventory : pandas.DataFrame
        Output of search_scenes(). Must contain
        'scene_id', 'acquisition_date', 'cloud_cover',
        'stac_item'.

    aoi_geometry : shapely.geometry.base.BaseGeometry
        AOI geometry in EPSG:4326.

    Returns
    -------
    list[Acquisition]
    """

    if inventory.empty:

        raise ValueError("Scene inventory is empty.")

    # ---------------------------------------------------------
    # Project AOI + item footprints into a common metric CRS
    # ---------------------------------------------------------

    utm_crs = estimate_utm_crs(aoi_geometry)

    aoi_gdf = gpd.GeoDataFrame(
        geometry=[aoi_geometry],
        crs="EPSG:4326",
    ).to_crs(utm_crs)

    aoi_projected = aoi_gdf.geometry.iloc[0]
    aoi_area = aoi_projected.area

    working = inventory.copy()

    working["date_key"] = pd.to_datetime(
        working["acquisition_date"],
        utc=True,
    ).dt.date

    working["tile_id"] = working["scene_id"].apply(
        lambda scene_id: (
            scene_id.split("_")[5] if len(scene_id.split("_")) > 5 else scene_id
        )
    )

    acquisitions = []

    for date_key, group in working.groupby("date_key"):

        # Build item footprints from stac_item geometry
        footprints_4326 = [_shapely_from_stac_item(item) for item in group["stac_item"]]

        footprints_gdf = gpd.GeoDataFrame(
            geometry=footprints_4326,
            crs="EPSG:4326",
        ).to_crs(utm_crs)

        union_footprint = unary_union(footprints_gdf.geometry.tolist())

        intersection = union_footprint.intersection(aoi_projected)

        coverage_percent = (
            round(
                100 * intersection.area / aoi_area,
                2,
            )
            if aoi_area > 0
            else 0.0
        )

        # ---------------------------------------------------------
        # Coverage-weighted cloud score
        # ---------------------------------------------------------

        weighted_cloud = 0.0
        weight_total = 0.0

        for _, row in group.iterrows():

            tile_geom_4326 = _shapely_from_stac_item(row["stac_item"])

            tile_geom = (
                gpd.GeoDataFrame(
                    geometry=[tile_geom_4326],
                    crs="EPSG:4326",
                )
                .to_crs(utm_crs)
                .geometry.iloc[0]
            )

            tile_overlap_area = tile_geom.intersection(aoi_projected).area

            cloud = row["cloud_cover"]

            if cloud is None:
                cloud = 100.0

            weighted_cloud += cloud * tile_overlap_area
            weight_total += tile_overlap_area

        cloud_cover = weighted_cloud / weight_total if weight_total > 0 else 100.0

        acquisitions.append(
            Acquisition(
                date=str(date_key),
                items=group["stac_item"].tolist(),
                tile_ids=group["tile_id"].tolist(),
                footprint=union_footprint,
                coverage_percent=coverage_percent,
                cloud_cover=round(cloud_cover, 2),
            )
        )

    print("\n========== ACQUISITIONS ==========")

    for acquisition in acquisitions:

        print(
            f"{acquisition.date}  "
            f"tiles={len(acquisition.items)}  "
            f"coverage={acquisition.coverage_percent}%  "
            f"cloud={acquisition.cloud_cover}%  "
            f"tile_ids={acquisition.tile_ids}"
        )

    print("===================================\n")

    return acquisitions


def _shapely_from_stac_item(item):
    """
    Extract a shapely geometry from a pystac Item.
    """

    from shapely.geometry import shape

    return shape(item.geometry)
