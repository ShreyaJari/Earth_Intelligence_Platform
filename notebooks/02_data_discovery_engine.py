# %% [markdown]
# # Earth Intelligence System
# 
# # Notebook 02: Data Discovery Engine
# 
# ## Overview
# 
# The Data Discovery Engine identifies Earth observation datasets that are relevant to a selected Area of Interest (AOI).
# 
# Rather than downloading datasets, the engine builds a standardized Earth Intelligence Catalog describing the available data sources for the selected study area.
# 
# This catalog serves as the central inventory for all downstream engines including:
# 
# - Satellite Imagery Engine
# - Terrain Engine
# - Weather Engine
# - Land Cover Engine
# - Population Engine
# - Hydrology Engine
# - Urban Analytics Engine
# 
# ---
# 
# ## Input
# 
# Area of Interest (AOI)
# 
# ## Output
# 
# Earth Intelligence Catalog

# %%
# Imports

from datetime import datetime

from pprint import pprint

# %% [markdown]
# # Earth Intelligence Catalog
# 
# ## Purpose
# 
# The Earth Intelligence Catalog is a structured inventory of all datasets that are available for the selected Area of Interest.
# 
# Each dataset is represented using a common data model regardless of:
# 
# - Provider
# - Spatial resolution
# - Temporal resolution
# - File format
# 
# This standardized representation enables downstream engines to interact with datasets consistently.

# %%
# Dataset Model

dataset_model = {

    # Dataset Identity
    "id": None,
    "name": None,
    "category": None,
    "provider": None,
    "description": None,

    # Spatial Characteristics
    "coverage": None,
    "spatial_resolution": None,
    "temporal_resolution": None,
    "data_type": None,

    # Discovery Information
    "applicable": None,
    "priority": None,

    # Additional Information
    "notes": None
}

print("DATASET MODEL")

pprint(dataset_model)

# %% [markdown]
# # Earth Intelligence Catalog Model
# 
# ## Purpose
# 
# The Earth Intelligence Catalog stores metadata describing all datasets that are relevant to the selected Area of Interest.
# 
# Each dataset follows the standardized Dataset Model.
# 
# The catalog acts as the interface between the Data Discovery Engine and downstream analytical engines.

# %%
# Earth Intelligence Catalog

catalog = {

    "metadata": {

        "engine": "Data Discovery Engine",

        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "version": "1.0"

    },

    "datasets": []

}

print("EARTH INTELLIGENCE CATALOG")

pprint(catalog)

# %% [markdown]
# # Catalog Design Philosophy
# 
# The Earth Intelligence Catalog is intentionally dataset-centric rather than category-centric.
# 
# Each dataset is treated as an independent object with a standardized structure.
# 
# This design allows new datasets to be added without modifying the overall catalog structure.
# 
# Downstream engines query the catalog based on dataset metadata such as category, provider, spatial resolution, or availability.

# %% [markdown]
# # Dataset Registration
# 
# ## Purpose
# 
# Register all Earth observation datasets supported by the Earth Intelligence System.
# 
# Each dataset is represented using the standardized Dataset Model.
# 
# The Data Discovery Engine does not determine availability by querying external services. Instead, it maintains a registry of supported datasets and records their characteristics.
# 
# This registry becomes the foundation for downstream engines responsible for data retrieval and analysis.

# %%
# Dataset Registry

dataset_registry = [

    # Satellite Datasets

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
        "notes": "Preferred optical imagery dataset."
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
        "notes": "Useful for long-term temporal analysis."
    },

    # Terrain Datasets

   {
    "id": "copernicus_dem",
    "name": "Copernicus DEM",
    "category": "Terrain",
    "provider": "Copernicus",
    "access_method": "STAC",
    "stac_collection": "cop-dem-glo-30",
    "description": "Global Digital Elevation Model (DEM).",
    "coverage": "Global",
    "spatial_resolution": "30 m",
    "temporal_resolution": "Static",
    "data_type": "Raster",
    "applicable": True,
    "priority": "Primary",
    "notes": "Preferred elevation dataset."
    },

    # Weather & Climate

    {
    "id": "open_meteo",
    "name": "Open-Meteo Weather API",
    "category": "Weather",
    "provider": "Open-Meteo",
    "access_method": "API",
    "description": "Global weather API providing historical, current, and forecast weather data.",
    "coverage": "Global",
    "spatial_resolution": "Point",
    "temporal_resolution": "Hourly / Daily",
    "data_type": "Time Series",
    "applicable": True,
    "priority": "Primary",
    "notes": "Preferred weather dataset for Version 1."
    },

    # Land Cover

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
    "notes": "Preferred land cover dataset."
    },

    # Population

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
        "notes": "Population density and distribution."
    },

    # Vector Data

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
        "notes": "Primary source for vector features."
    }

]

print("DATASET REGISTRY")

print(f"Registered Datasets : {len(dataset_registry)}")

print("\nDataset Categories:")

categories = sorted({dataset["category"] for dataset in dataset_registry})

for category in categories:
    count = sum(
        dataset["category"] == category
        for dataset in dataset_registry
    )
    print(f"• {category:<12} : {count}")

# %% [markdown]
# # Catalog Population
# 
# ## Purpose
# 
# Populate the Earth Intelligence Catalog using the registered dataset inventory.
# 
# Each supported dataset is added to the catalog using the standardized Dataset Model.
# 
# This creates a unified catalog that downstream engines can query based on dataset metadata.

# %%
# Catalog Population

catalog["datasets"].extend(dataset_registry)

print("CATALOG POPULATION")

print(f"Datasets in Catalog : {len(catalog['datasets'])}")

# %% [markdown]
# # Discovery Assessment
# 
# ## Purpose
# 
# Evaluate the Dataset Registry for the selected Area of Interest (AOI).
# 
# The Discovery Assessment determines which registered datasets are applicable to the current study area and should be included in the Earth Intelligence Catalog.
# 
# For Version 1, all globally available datasets are considered applicable.
# 
# Future versions may evaluate additional factors such as:
# 
# - Geographic coverage
# - Dataset availability
# - AOI size
# - Analysis type
# - Temporal requirements

# %%

# Discovery Assessment

print("DISCOVERY ASSESSMENT")

for dataset in catalog["datasets"]:

    if dataset["coverage"] == "Global":
        dataset["applicable"] = True
    else:
        dataset["applicable"] = False

print("Discovery assessment completed.")

applicable = sum(
    dataset["applicable"]
    for dataset in catalog["datasets"]
)

print(f"\nApplicable Datasets : {applicable}")

# %% [markdown]
# # Catalog Summary
# 
# ## Purpose
# 
# Provide a summary of all datasets registered for the selected Area of Interest.
# 
# The summary groups datasets by category and highlights their priority within the Earth Intelligence System.

# %%
# Catalog Summary

print("EARTH INTELLIGENCE CATALOG")

print(f"\nTotal Registered Datasets : {len(catalog['datasets'])}")

categories = sorted(
    {dataset["category"] for dataset in catalog["datasets"]}
)

print("\nDataset Categories\n")

for category in categories:

    print(f"{category}")

    for dataset in catalog["datasets"]:

        if dataset["category"] == category:

            print(
                f"   • {dataset['name']} "
                f"({dataset['priority']})"
            )

print("\nDiscovery assessment complete.")

# %% [markdown]
# # Export Earth Intelligence Catalog
# 
# ## Purpose
# 
# Export the completed Earth Intelligence Catalog to a JSON file.
# 
# The catalog serves as the standardized input for downstream Earth Intelligence System modules.
# 
# Output:
# 
# - `data/outputs/catalog.json`
# 
# The exported catalog contains metadata describing all datasets that are applicable to the selected Area of Interest.

# %%
# Export Earth Intelligence Catalog

from pathlib import Path
import json

# Create output directory
output_dir = Path("/Users/ShreyaJariwalaMain/_GeoAI_Notebook/Earth-Intelligence-System/data/outputs")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "catalog.json"

# Export catalog
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(
        catalog,
        file,
        indent=4,
        ensure_ascii=False
    )

print("EARTH INTELLIGENCE CATALOG EXPORTED")

print(f"Output File : {output_file.resolve()}")
print("\nExport completed successfully.")

# %% [markdown]
# # ✅ Data Discovery Engine Complete
# 
# ## Outcome
# 
# The Data Discovery Engine successfully evaluated the supported Earth observation datasets and produced a standardized Earth Intelligence Catalog.
# 
# The catalog includes:
# 
# - Dataset registry
# - Dataset metadata
# - Dataset categories
# - Applicability assessment
# - Dataset priorities
# 
# The exported catalog serves as the input for downstream Earth Intelligence System modules, including:
# 
# - Satellite Engine
# - Terrain Engine
# - Weather Engine
# - Land Cover Engine
# - Population Engine
# - Hydrology Engine


