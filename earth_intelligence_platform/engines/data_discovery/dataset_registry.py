"""
Earth Intelligence Platform
Data Discovery Engine

Dataset Registry

This module contains the master registry of all datasets
supported by the Earth Intelligence Platform.

Each dataset follows a standardized metadata model that
allows downstream engines to discover and access datasets
consistently.
"""

dataset_registry = [
    # ==========================================================
    # Satellite Datasets
    # ==========================================================
    {
        "id": "sentinel_2",
        "name": "Sentinel-2 Level-2A",
        "stac_collection": "sentinel-2-l2a",
        "category": "Satellite",
        "provider": "Copernicus",
        "description": "Multispectral optical satellite imagery for land monitoring.",
        "coverage": "Global",
        "spatial_resolution": "10 m",
        "temporal_resolution": "5 days",
        "data_type": "Raster",
        "applicable": True,
        "priority": "Primary",
        "notes": "Preferred optical imagery dataset.",
    },
    {
        "id": "landsat_collection_2",
        "name": "Landsat Collection 2",
        "stac_collection": "landsat-c2-l2",
        "category": "Satellite",
        "provider": "USGS / NASA",
        "description": "Multispectral optical satellite imagery with a long historical archive.",
        "coverage": "Global",
        "spatial_resolution": "30 m",
        "temporal_resolution": "16 days",
        "data_type": "Raster",
        "applicable": True,
        "priority": "Secondary",
        "notes": "Useful for long-term temporal analysis.",
    },
    # ==========================================================
    # Terrain Datasets
    # ==========================================================
    {
    "id": "copernicus_dem",
    "name": "Copernicus DEM",
    "category": "Terrain",
    "provider": "Copernicus",
    "access_method": "STAC",
    "stac_collection": "cop-dem-glo-90",   # was: cop-dem-glo-30
    "description": "Global Digital Elevation Model (DEM), 90m resolution.",
    "coverage": "Global",
    "spatial_resolution": "90 m",   # was: "30 m"
    "temporal_resolution": "Static",
    "data_type": "Raster",
    "applicable": True,
    "priority": "Primary",
    "notes": "Preferred elevation dataset. 90m resolution reduces building-edge slope artifacts in dense urban areas (see README limitations)."
},
    # ==========================================================
    # Weather
    # ==========================================================
    {
        "id": "open_meteo",
        "name": "Open-Meteo Weather API",
        "category": "Weather",
        "provider": "Open-Meteo",
        "access_method": "API",
        "url": "https://api.open-meteo.com/v1/forecast",
        "variables": [
            "temperature_2m",
            "precipitation",
            "relative_humidity_2m",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "description": "Global weather API providing historical, current, and forecast weather data.",
        "coverage": "Global",
        "spatial_resolution": "Point",
        "temporal_resolution": "Hourly / Daily",
        "data_type": "Time Series",
        "applicable": True,
        "priority": "Primary",
        "notes": "Preferred weather dataset for Version 1.",
    },
    # ==========================================================
    # Land Cover
    # ==========================================================
    {
        "id": "esa_worldcover",
        "name": "ESA WorldCover",
        "category": "Land Cover",
        "provider": "European Space Agency",
        "access_method": "STAC",
        "stac_collection": "esa-worldcover",
        "description": "Global land cover classification map.",
        "coverage": "Global",
        "spatial_resolution": "10 m",
        "temporal_resolution": "Annual",
        "data_type": "Raster",
        "applicable": True,
        "priority": "Primary",
        "notes": "Preferred land cover dataset.",
    },
    # ==========================================================
    # Population
    # ==========================================================
    {
        "id": "worldpop",
        "name": "WorldPop",
        "category": "Population",
        "provider": "WorldPop",
        "description": "High-resolution global population distribution dataset.",
        "coverage": "Global",
        "spatial_resolution": "100 m",
        "temporal_resolution": "Annual",
        "data_type": "Raster",
        "applicable": True,
        "priority": "Primary",
        "notes": "Population density and distribution.",
    },
    # ==========================================================
    # Vector Data
    # ==========================================================
    {
        "id": "openstreetmap",
        "name": "OpenStreetMap",
        "category": "Vector",
        "provider": "OpenStreetMap",
        "description": "Crowdsourced vector data including roads, buildings, waterways and points of interest.",
        "coverage": "Global",
        "spatial_resolution": "Variable",
        "temporal_resolution": "Continuously Updated",
        "data_type": "Vector",
        "applicable": True,
        "priority": "Primary",
        "notes": "Primary source for vector features.",
    },
]
