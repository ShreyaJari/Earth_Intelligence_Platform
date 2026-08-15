# %% [markdown]
# # Earth Intelligence System
# 
# # Notebook 03: Satellite Engine
# 
# ## Overview
# 
# The Satellite Engine retrieves the most appropriate satellite imagery for a selected Area of Interest (AOI).
# 
# Using the Earth Intelligence Catalog, the engine identifies the preferred satellite dataset, searches for available scenes, ranks candidate imagery, downloads the selected scene, and prepares a standardized Satellite Product for downstream analysis.
# 
# ---
# 
# ## Inputs
# 
# - Area of Interest (AOI)
# - Earth Intelligence Catalog
# 
# ---
# 
# ## Outputs
# 
# - Satellite Product

# %%
# Imports

from pathlib import Path
from datetime import datetime
from pprint import pprint

import json

# %% [markdown]
# # Satellite Engine Objective
# 
# ## Purpose
# 
# Retrieve the highest quality satellite imagery available for the selected Area of Interest.
# 
# The engine is responsible for:
# 
# - Selecting the preferred satellite dataset
# - Discovering available scenes
# - Ranking candidate imagery
# - Downloading imagery
# - Preparing a standardized Satellite Product
# 
# The engine does not perform image analysis.

# %%

# Load Inputs

from pathlib import Path
import json
import geopandas as gpd

DATA_DIR = Path("/Users/ShreyaJariwalaMain/_GeoAI_Notebook/Earth-Intelligence-System/data/outputs")

print("LOADING INPUTS")

# Area of Interest (AOI)

aoi_file = DATA_DIR / "aoi.geojson"

if not aoi_file.exists():
    raise FileNotFoundError(
        "AOI GeoJSON not found. Run Notebook 01 first."
    )

aoi_boundary = gpd.read_file(aoi_file)

print("AOI Loaded")

# Earth Intelligence Catalog

catalog_file = DATA_DIR / "catalog.json"

if not catalog_file.exists():
    raise FileNotFoundError(
        "Catalog not found. Run Notebook 02 first."
    )

with open(catalog_file, "r", encoding="utf-8") as file:
    catalog = json.load(file)

print("Catalog Loaded")

print("\nAll inputs loaded successfully.")

print(f"\nAOI Features : {len(aoi_boundary)}")
print(f"AOI CRS      : {aoi_boundary.crs}")
print(f"Datasets     : {len(catalog['datasets'])}")

# %% [markdown]
# # Satellite Dataset Selection
# 
# ## Purpose
# 
# Select the preferred satellite dataset from the Earth Intelligence Catalog.
# 
# The selection is based on the dataset metadata rather than hardcoded dataset names.
# 
# Selection Criteria
# 
# - Category = Satellite
# - Applicable = True
# - Highest Priority
# 
# The selected dataset becomes the source for satellite scene discovery in the following stages.

# %%
# Satellite Dataset Selection

print("SATELLITE DATASET SELECTION")

# Find all applicable satellite datasets
satellite_datasets = [

    dataset

    for dataset in catalog["datasets"]

    if dataset["category"] == "Satellite"
    and dataset["applicable"]

]

if len(satellite_datasets) == 0:

    raise ValueError(
        "No applicable satellite datasets found."
    )

# Priority ranking
priority_order = {
    "Primary": 1,
    "Secondary": 2
}

satellite_datasets = sorted(

    satellite_datasets,

    key=lambda dataset: priority_order.get(
        dataset["priority"],
        99
    )

)

selected_dataset = satellite_datasets[0]

print("Selected Dataset\n")

for key, value in selected_dataset.items():

    print(f"{key:<22}: {value}")

# %% [markdown]
# # Scene Search Configuration
# 
# ## Purpose
# 
# Define the temporal search window used when discovering satellite imagery.
# 
# The selected date range is used to query the satellite catalog for candidate scenes covering the Area of Interest.

# %%

# Scene Search Configuration

search_parameters = {

    "start_date": "2025-01-01",

    "end_date": "2025-12-31",

    "maximum_cloud_cover": 20

}

print("SCENE SEARCH CONFIGURATION")

for key, value in search_parameters.items():
    print(f"{key:<22}: {value}")

# %% [markdown]
# # Scene Search
# 
# ## Purpose
# 
# Search the selected satellite dataset for imagery covering the Area of Interest (AOI).
# 
# The search is performed using the Microsoft Planetary Computer STAC API.
# 
# The engine returns candidate scenes satisfying:
# 
# - Area of Interest coverage
# - Date range
# - Maximum cloud cover
# 
# The retrieved scenes are ranked and evaluated in subsequent stages.

# %%
# Connect to Microsoft Planetary Computer STAC

from pystac_client import Client
import planetary_computer

print("CONNECTING TO STAC CATALOG")

catalog_client = Client.open(

    "https://planetarycomputer.microsoft.com/api/stac/v1",

    modifier=planetary_computer.sign_inplace

)

print("✓ Connected successfully")

print(f"\nCatalog Title : {catalog_client.title}")

# %% [markdown]
# # Search Parameters
# 
# ## Purpose
# 
# Construct the STAC search request using:
# 
# - Area of Interest
# - Selected satellite dataset
# - Date range
# - Cloud cover threshold

# %%
# Build STAC Search

from shapely.geometry import mapping

print("BUILDING SCENE SEARCH")

search = catalog_client.search(

    collections=[selected_dataset["stac_collection"]],

    intersects=mapping(aoi_boundary.geometry.iloc[0]),

    datetime=(
        f"{search_parameters['start_date']}/"
        f"{search_parameters['end_date']}"
    ),

    query={

        "eo:cloud_cover": {
            "lte": search_parameters["maximum_cloud_cover"]
        }

    }

)

print("Search request created")

# %%
print(catalog["datasets"][0])

# %% [markdown]
# # Candidate Scene Retrieval
# 
# ## Purpose
# 
# Execute the STAC search and retrieve all candidate satellite scenes matching the search criteria.
# 
# Only scene metadata is collected during this stage. Imagery is not downloaded.
# 
# The retrieved metadata will be used during scene ranking and selection.

# %%
# Retrieve Candidate Scenes

print("RETRIEVING CANDIDATE SCENES")

candidate_scenes = list(search.items())

print(f"Candidate Scenes Found : {len(candidate_scenes)}")

if len(candidate_scenes) == 0:
    raise ValueError(
        "No satellite scenes found for the selected search criteria."
    )

# %% [markdown]
# # Scene Metadata Extraction
# 
# ## Purpose
# 
# Extract the metadata of candidate satellite scenes returned by the STAC search.
# 
# The extracted metadata is standardized and organized into a tabular structure for ranking and selection.
# 
# The original STAC Items are retained separately for later download.

# %%
# Scene Metadata Extraction

import pandas as pd

scene_records = []

for item in candidate_scenes:

    properties = item.properties

    scene_records.append({

        "scene_id": item.id,

        "collection": item.collection_id,

        "datetime": properties.get("datetime"),

        "cloud_cover": properties.get("eo:cloud_cover"),

        "platform": properties.get("platform"),

        "instruments": properties.get("instruments"),

        "item": item

    })

scene_table = pd.DataFrame(scene_records)

print("SCENE METADATA EXTRACTED")

print(f"Candidate Scenes : {len(scene_table)}")

scene_table.head()

# %% [markdown]
# # Candidate Scene Summary
# 
# ## Purpose
# 
# Provide a quick overview of the candidate scenes returned by the STAC search.
# 
# The summary helps verify the search results before ranking and selection.

# %%
# Candidate Scene Summary

display_columns = [

    "scene_id",
    "datetime",
    "cloud_cover",
    "platform",
    "collection"

]

scene_table[display_columns].head(10)

# %% [markdown]
# # Scene Inventory
# 
# ## Purpose
# 
# Convert the candidate STAC Items into a standardized Scene Inventory.
# 
# The Scene Inventory provides a tabular representation of all candidate scenes and serves as the primary data structure for scene evaluation, ranking, and selection.
# 
# Each row represents one satellite scene together with its key metadata.

# %%
# Scene Inventory

import pandas as pd

scene_inventory = []

for item in candidate_scenes:

    properties = item.properties

    scene_inventory.append({

        "scene_id": item.id,

        "collection": item.collection_id,

        "acquisition_date": properties.get("datetime"),

        "cloud_cover": properties.get("eo:cloud_cover"),

        "platform": properties.get("platform"),

        "instruments": ", ".join(
            properties.get("instruments", [])
        ),

        "processing_level": properties.get("processing:level"),

        "stac_item": item

    })

scene_inventory = pd.DataFrame(scene_inventory)

print("SCENE INVENTORY")

print(f"Candidate Scenes : {len(scene_inventory)}")
print(f"Columns          : {len(scene_inventory.columns)}")

scene_inventory.head()

# %% [markdown]
# # Scene Inventory Summary
# 
# ## Purpose
# 
# Provide a statistical summary of the Scene Inventory before ranking.
# 
# The summary allows verification of scene availability and quality characteristics.

# %%

# Scene Inventory Summary

print("SCENE INVENTORY SUMMARY")

print(f"Total Scenes : {len(scene_inventory)}")

print(
    f"Earliest Scene : "
    f"{scene_inventory['acquisition_date'].min()}"
)

print(
    f"Latest Scene   : "
    f"{scene_inventory['acquisition_date'].max()}"
)

print(
    f"Minimum Cloud Cover : "
    f"{scene_inventory['cloud_cover'].min()}%"
)

print(
    f"Average Cloud Cover : "
    f"{scene_inventory['cloud_cover'].mean():.2f}%"
)

print(
    f"Maximum Cloud Cover : "
    f"{scene_inventory['cloud_cover'].max()}%"
)

# %% [markdown]
# # Scene Inventory Preview
# 
# ## Purpose
# 
# Preview the candidate scenes before ranking.
# 
# Only the most relevant metadata is displayed for readability.

# %%
# Scene Inventory Preview

preview_columns = [

    "scene_id",

    "acquisition_date",

    "cloud_cover",

    "platform",

    "processing_level"

]

scene_inventory[preview_columns].head(10)

# %% [markdown]
# # Scene Ranking
# 
# ## Purpose
# 
# Evaluate and rank the candidate scenes retrieved from the STAC search.
# 
# Scenes are ranked according to image quality and acquisition characteristics.
# 
# Version 1 Ranking Criteria
# 
# 1. Lowest cloud cover
# 2. Most recent acquisition date
# 
# The highest ranked scene becomes the recommended scene for download.

# %%

# Scene Ranking

scene_inventory["acquisition_date"] = pd.to_datetime(
    scene_inventory["acquisition_date"]
)

scene_inventory = scene_inventory.sort_values(

    by=[
        "cloud_cover",
        "acquisition_date"
    ],

    ascending=[
        True,
        False
    ]

).reset_index(drop=True)

scene_inventory["rank"] = (
    scene_inventory.index + 1
)

print("SCENE RANKING")

print(f"Scenes Ranked : {len(scene_inventory)}")

# %% [markdown]
# # Ranked Scene Inventory
# 
# ## Purpose
# 
# Display the highest ranked candidate scenes.
# 
# The ranked inventory provides a transparent view of how scenes are ordered before selecting the recommended scene.

# %%
# Ranked Scene Inventory

display_columns = [

    "rank",

    "scene_id",

    "acquisition_date",

    "cloud_cover",

    "platform"

]

scene_inventory[display_columns].head(10)

# %% [markdown]
# # Scene Selection
# 
# ## Purpose
# 
# Select the highest ranked scene from the Scene Inventory.
# 
# The selected scene becomes the recommended satellite scene for the Area of Interest and is used in subsequent download and processing steps.

# %%
# Scene Selection

selected_scene = scene_inventory.iloc[0]

print("SELECTED SCENE")


print(f"Scene ID          : {selected_scene['scene_id']}")
print(f"Acquisition Date  : {selected_scene['acquisition_date']}")
print(f"Cloud Cover       : {selected_scene['cloud_cover']} %")
print(f"Platform          : {selected_scene['platform']}")
print(f"Collection        : {selected_scene['collection']}")

# %% [markdown]
# # Satellite Product Model
# 
# ## Purpose
# 
# Create the standardized data model used by the Satellite Engine.
# 
# The Satellite Product represents the final output of the Satellite Engine and serves as the input for downstream Earth Intelligence modules.
# 
# The product combines:
# 
# - Dataset metadata
# - Selected scene metadata
# - Imagery information
# - Band information
# - Quality information
# - Processing metadata

# %%
# Satellite Product Model

from datetime import datetime
from pprint import pprint

satellite_product = {

    # Product Metadata

    "metadata": {

        "engine": "Satellite Engine",

        "version": "1.0",

        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    },

    # Dataset Information

    "dataset": {

        "id": None,

        "name": None,

        "provider": None,

        "category": None,

        "stac_collection": None

    },

    # Selected Scene

    "scene": {

    "acquisition_date": None,

    "tiles_used": None,

    "tile_ids": [],

    "collection": None,

    "cloud_cover": None,

    "platform": None,

    "processing_level": None

},

    # Imagery Information

    "imagery": {

        "crs": None,

        "resolution": None,

        "bounds": None,

        "shape": None,

        "downloaded": False

    },

    # Spectral Bands

    "bands": {

        "available": [],

        "loaded": []

    },

    # Quality Assessment

    "quality": {

        "cloud_cover": None,

        "rank": None

    },

    # Processing Information

    "processing": {

        "provider": "Microsoft Planetary Computer",

        "search_method": "STAC",

        "clipped_to_aoi": True,

        "download_time_seconds": None

    }

}

print("SATELLITE PRODUCT MODEL")

pprint(satellite_product)

# %% [markdown]
# # Populate Satellite Product
# 
# ## Purpose
# 
# Populate the Satellite Product using the selected dataset and the highest-ranked satellite scene.
# 
# The populated product becomes the central object for all remaining processing steps.

# %%
# Populate Satellite Product

# Dataset Information

satellite_product["dataset"] = {

    "id": selected_dataset["id"],

    "name": selected_dataset["name"],

    "provider": selected_dataset["provider"],

    "category": selected_dataset["category"],

    "stac_collection": selected_dataset["stac_collection"]

}

# Scene Information

selected_acquisition = selected_scene["acquisition_date"]

matching_scenes = scene_inventory[
    scene_inventory["acquisition_date"] == selected_acquisition
]

tile_ids = [

    scene.split("_")[5]

    for scene in matching_scenes["scene_id"]

]

satellite_product["scene"] = {

    "acquisition_date": selected_acquisition,

    "tiles_used": len(matching_scenes),

    "tile_ids": tile_ids,

    "collection": selected_scene["collection"],

    "cloud_cover": float(selected_scene["cloud_cover"]),

    "platform": selected_scene["platform"],

    "processing_level": selected_scene["processing_level"]

}

# Quality Information

satellite_product["quality"] = {

    "cloud_cover": selected_scene["cloud_cover"],

    "rank": int(selected_scene["rank"])

}

print("SATELLITE PRODUCT POPULATED")

print(f"Dataset        : {satellite_product['dataset']['name']}")
print(
    f"Acquisition    : "
    f"{satellite_product['scene']['acquisition_date']}"
)

print(
    f"Tiles Used     : "
    f"{satellite_product['scene']['tiles_used']}"
)

print(
    f"Tile IDs       : "
    f"{', '.join(satellite_product['scene']['tile_ids'])}"
)

print(
    f"Cloud Cover    : "
    f"{satellite_product['quality']['cloud_cover']} %"
)

print(
    f"Acquisition Rank : "
    f"{satellite_product['quality']['rank']}"
)

# %% [markdown]
# # Band Configuration
# 
# ## Purpose
# 
# Define the spectral bands required by the Satellite Engine.
# 
# Version 1 loads the four core Sentinel-2 bands used for visualization and vegetation analysis.
# 
# Additional bands can be added in future versions without modifying the loading workflow.

# %%
# Band Configuration

band_configuration = {

    "bands": [

        "B02",  # Blue

        "B03",  # Green

        "B04",  # Red

        "B08"   # Near Infrared

    ]

}

band_configuration

# %% [markdown]
# # Load Satellite Imagery
# 
# ## Purpose
# 
# Load the selected satellite scene using the Microsoft Planetary Computer STAC API.
# 
# The imagery is clipped to the Area of Interest (AOI) and loaded as an xarray Dataset.
# 
# Only the configured spectral bands are retrieved.

# %%
from odc.stac import load
import planetary_computer
import time

start_time = time.time()

selected_acquisition = selected_scene["acquisition_date"]

matching_scenes = scene_inventory[
    scene_inventory["acquisition_date"] == selected_acquisition
]

signed_scenes = [

    planetary_computer.sign(stac_item)

    for stac_item in matching_scenes["stac_item"]

]

imagery = load(

    signed_scenes,

    bands=band_configuration["bands"],

    geopolygon=aoi_boundary.geometry.iloc[0],

    groupby="solar_day",

    chunks={}

)

download_time = round(
    time.time() - start_time,
    2
)

print("Imagery loaded successfully.")
print(f"Tiles loaded : {len(signed_scenes)}")
print(f"Bands loaded : {list(imagery.data_vars)}")
print(f"Processing time : {download_time} seconds")

# %%
import dask
import odc.stac
import xarray
import rasterio

print("Dask:", dask.__version__)
print("xarray:", xarray.__version__)
print("Rasterio:", rasterio.__version__)

# %%
import dask

print(dask.__version__)

# %%
import geopandas
import rasterio
import rioxarray
import xarray
import dask
import odc.stac
import pystac_client
import planetary_computer

print("GeoPandas :", geopandas.__version__)
print("Rasterio  :", rasterio.__version__)
print("Xarray    :", xarray.__version__)
print("Dask      :", dask.__version__)
print("ODC-STAC  :", odc.stac.__version__)
print("PySTAC    :", pystac_client.__version__)
print("Planetary :", planetary_computer.__version__)

# %% [markdown]
# # Load Satellite Imagery
# 
# ## Purpose
# 
# Load the selected Sentinel-2 scene from the Microsoft Planetary Computer.
# 
# Only the configured spectral bands are retrieved.
# 
# The imagery is clipped to the Area of Interest (AOI) and stored as an xarray Dataset for subsequent processing.

# %%
imagery

# %% [markdown]
# # Populate Satellite Product
# 
# ## Purpose
# 
# Populate the Satellite Product with metadata extracted from the loaded satellite imagery.
# 
# The imagery itself remains stored separately as an xarray Dataset, while the Satellite Product stores descriptive metadata required by downstream Earth Intelligence modules.

# %%
from rasterio.transform import array_bounds

# Dataset dimensions
height = imagery.sizes["y"]
width = imagery.sizes["x"]

# Coordinate Reference System
crs = imagery.rio.crs

# Spatial resolution
resolution_x, resolution_y = imagery.rio.resolution()

# Spatial bounds
bounds = imagery.rio.bounds()

# Loaded bands
loaded_bands = list(imagery.data_vars)

# Populate imagery metadata
satellite_product["imagery"] = {

    "crs": str(crs),

    "width": width,

    "height": height,

    "resolution": {

        "x": abs(resolution_x),

        "y": abs(resolution_y)

    },

    "bounds": {

        "left": bounds[0],

        "bottom": bounds[1],

        "right": bounds[2],

        "top": bounds[3]

    },

    "downloaded": True

}

# Populate band information
satellite_product["bands"] = {

    "available": loaded_bands,

    "loaded": loaded_bands

}

# Update processing information
satellite_product["processing"]["download_time_seconds"] = download_time

# %% [markdown]
# # Satellite Product Summary
# 
# ## Purpose
# 
# Review the populated Satellite Product before exporting it.
# 
# This summary verifies that the Satellite Engine successfully retrieved imagery and extracted the required metadata.

# %%
from pprint import pprint

pprint(satellite_product)

# %% [markdown]
# # Export Satellite Product
# 
# ## Purpose
# 
# Export the outputs of the Satellite Engine.
# 
# The Satellite Product metadata is saved as JSON.
# 
# The satellite imagery is saved as a NetCDF dataset for use in downstream Earth Intelligence modules.

# %%
from pathlib import Path
import json

OUTPUT_DIR = Path(
    "/Users/ShreyaJariwalaMain/_GeoAI_Notebook/Earth-Intelligence-System/data/outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# Export Satellite Product Metadata

product_file = OUTPUT_DIR / "satellite_product.json"

with open(product_file, "w", encoding="utf-8") as file:
    json.dump(
        satellite_product,
        file,
        indent=4,
        default=str
    )

# Export Imagery

imagery_file = OUTPUT_DIR / "imagery.nc"

imagery.to_netcdf(imagery_file)

print(f"Satellite Product : {product_file.name}")
print(f"Imagery           : {imagery_file.name}")

# %% [markdown]
# # Notebook Summary
# 
# ## Purpose
# 
# Provide a concise summary of the Satellite Engine outputs.
# 
# This confirms that the notebook successfully retrieved, ranked, loaded, and exported the satellite imagery for the selected Area of Interest.

# %%
summary = {

    "Dataset": satellite_product["dataset"]["name"],

    "Tiles Used": satellite_product["scene"]["tiles_used"],

    "Tile IDs": ", ".join(
    satellite_product["scene"]["tile_ids"]
    ),

    "Acquisition Date": satellite_product["scene"]["acquisition_date"],

    "Cloud Cover (%)": satellite_product["quality"]["cloud_cover"],

    "Bands Loaded": ", ".join(
        satellite_product["bands"]["loaded"]
    ),

    "Raster Size": (
        f"{satellite_product['imagery']['width']} × "
        f"{satellite_product['imagery']['height']}"
    ),

    "Coordinate System": satellite_product["imagery"]["crs"]

}

for key, value in summary.items():
    print(f"{key:<20}: {value}")

# %%
selected_scene

# %%
print(matching_scenes[["scene_id"]])


