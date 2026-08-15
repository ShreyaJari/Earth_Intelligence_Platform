"""
load_weather.py

Download weather data and convert it to the standard format.
"""

import datetime
import time

import pandas as pd
import requests

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

HOURLY_VARIABLES = [
    "temperature_2m",
    "precipitation",
    "relative_humidity_2m",
    "surface_pressure",
    "wind_speed_10m",
    "wind_direction_10m",
]


def load_weather(
    aoi,
    dataset,
    weather_product,
    start_date=None,
    end_date=None,
):
    """
    Load weather data for an explicit date range.

    Uses the historical archive API when a date range is
    given (recommended — the forecast API only covers recent
    days and a short forecast window, which is why omitting
    dates previously made the page look like it only showed
    one day of data). Falls back to the forecast API's default
    window if no dates are given, for backward compatibility.

    Parameters
    ----------
    aoi : dict

    dataset : dict

    weather_product : dict

    start_date : str, optional (YYYY-MM-DD)

    end_date : str, optional (YYYY-MM-DD)

    Returns
    -------
    tuple
        (weather_dataframe, weather_product)
    """

    start = time.time()

    centroid = aoi["geometry"]["geometry"].centroid

    latitude = centroid.y
    longitude = centroid.x

    use_archive = start_date is not None and end_date is not None

    url = ARCHIVE_URL if use_archive else dataset["url"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": HOURLY_VARIABLES,
        "timezone": "auto",
    }

    if use_archive:

        params["start_date"] = start_date

        params["end_date"] = end_date

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    hourly = data["hourly"]

    weather_df = pd.DataFrame(
        {
            "time": hourly["time"],
            "temperature": hourly["temperature_2m"],
            "precipitation": hourly["precipitation"],
            "humidity": hourly["relative_humidity_2m"],
            "pressure": hourly["surface_pressure"],
            "wind_speed": hourly["wind_speed_10m"],
            "wind_direction": hourly["wind_direction_10m"],
        }
    )

    weather_product["metadata"] = {
        "provider": dataset["name"],
        "latitude": latitude,
        "longitude": longitude,
        "timezone": data.get("timezone"),
        "elevation": data.get("elevation"),
        "generation_time_ms": data.get("generationtime_ms"),
        "start_date": start_date,
        "end_date": end_date,
        "source": "archive" if use_archive else "forecast (default window)",
    }

    weather_product["processing"]["download_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return (
        weather_df,
        weather_product,
    )
