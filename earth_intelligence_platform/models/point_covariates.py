"""
Earth Intelligence Platform
Wildfire Risk Calibration Model

Point Covariates

Fetches weather and land cover covariates for a single
lat/lon/date point. Used ONLY by the training script — at
runtime, the Risk Engine already has these same values
computed at the AOI level, so no per-point fetching happens
during normal app use.

IMPORTANT — VERIFY: the historical archive endpoint URL and
exact hourly parameter behavior could not be confirmed against
live documentation. The parameter NAMES reused here
(temperature_2m, precipitation, relative_humidity_2m) are the
same ones already confirmed working in engines/weather_engine/
load_weather.py's forecast API call — lower risk than a blind
guess, but still unverified for the historical archive endpoint
specifically.
"""

import sys
import time
from curses import error
from pathlib import Path

import numpy as np
import planetary_computer
import requests
from odc.stac import load
from pystac_client import Client
from shapely.geometry import box

try:

    from earth_intelligence_platform.engines.land_cover_engine.legend import (
        LAND_COVER_LEGEND,
    )

except ImportError:

    sys.path.append(
        str(Path(__file__).resolve().parents[1] / "engines" / "land_cover_engine")
    )

    from legend import LAND_COVER_LEGEND


ARCHIVE_WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"  # VERIFY

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

WEATHER_LOOKBACK_DAYS = 7

LANDCOVER_WINDOW_DEGREES = 0.002  # ~200m box around the point

VEGETATION_CLASSES = [
    "Tree Cover",
    "Shrubland",
    "Grassland",
    "Cropland",
    "Mangroves",
    "Herbaceous Wetland",
]


def fetch_weather_covariates(lat, lon, date_str):
    """
    Fetch mean temperature, mean humidity, and total
    precipitation over the WEATHER_LOOKBACK_DAYS window
    ending on date_str, at a single point.

    Returns
    -------
    dict or None
        {"temperature": ..., "humidity": ..., "precipitation": ...}
        or None if the fetch failed.
    """

    import datetime

    end_date = datetime.date.fromisoformat(date_str)

    start_date = end_date - datetime.timedelta(days=WEATHER_LOOKBACK_DAYS)

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": [
            "temperature_2m",
            "precipitation",
            "relative_humidity_2m",
        ],
        "timezone": "UTC",
    }

    try:

        response = requests.get(
            ARCHIVE_WEATHER_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        hourly = data["hourly"]

        temperature = np.mean(hourly["temperature_2m"])

        humidity = np.mean(hourly["relative_humidity_2m"])

        precipitation = np.sum(hourly["precipitation"])

        return {
            "temperature": float(temperature),
            "humidity": float(humidity),
            "precipitation": float(precipitation),
        }

    except Exception:

        return None


def fetch_vegetation_fraction(lat, lon):
    """
    Sample a small ESA WorldCover window around a point and
    compute the fraction of pixels classified as vegetated.

    Returns
    -------
    float or None
        Vegetation fraction (0.0-1.0), or None if the fetch failed.
    """

    try:

        catalog = Client.open(
            STAC_URL,
            modifier=planetary_computer.sign_inplace,
        )

        search = catalog.search(
            collections=["esa-worldcover"],
            intersects={"type": "Point", "coordinates": [lon, lat]},
        )

        items = list(search.item_collection())

        if not items:

            return None

        window = box(
            lon - LANDCOVER_WINDOW_DEGREES,
            lat - LANDCOVER_WINDOW_DEGREES,
            lon + LANDCOVER_WINDOW_DEGREES,
            lat + LANDCOVER_WINDOW_DEGREES,
        )

        data = load(
            items,
            bands=["map"],
            geopolygon=window,
            resolution=0.0001,  # ~10m in degrees
            chunks={},
        )

        values = data["map"].values

        if values.size == 0:

            return None

        vegetation_ids = [
            class_id
            for class_id, info in LAND_COVER_LEGEND.items()
            if info["name"] in VEGETATION_CLASSES
        ]

        vegetated = np.isin(values, vegetation_ids)

        return float(np.mean(vegetated)) * 100

    except Exception:

        return None


def fetch_point_covariates(lat, lon, date_str):
    """
    Fetch all covariates for a single point. Returns None if
    either weather or land cover fetch failed.
    """

    weather = fetch_weather_covariates(lat, lon, date_str)

    if weather is None:

        return None

    vegetation = fetch_vegetation_fraction(lat, lon)

    if vegetation is None:

        return None

    return {
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "precipitation": weather["precipitation"],
        "vegetation_percentage": vegetation,
    }
