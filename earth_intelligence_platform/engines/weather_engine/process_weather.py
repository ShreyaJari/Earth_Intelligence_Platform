"""
process_weather.py

Generate standardized weather products.
"""

import time

import pandas as pd


def process_weather(
    weather_df,
    weather_product,
):
    """
    Generate weather products.

    Parameters
    ----------
    weather_df : pandas.DataFrame

    weather_product : dict

    Returns
    -------
    dict
    """

    start = time.time()

    weather_df = weather_df.copy()

    weather_df["time"] = pd.to_datetime(weather_df["time"])

    weather_df = weather_df.sort_values(by="time").reset_index(drop=True)

    weather_product["products"] = {
        "temperature": weather_df["temperature"],
        "precipitation": weather_df["precipitation"],
        "wind_speed": weather_df["wind_speed"],
        "wind_direction": weather_df["wind_direction"],
        "humidity": weather_df["humidity"],
        "pressure": weather_df["pressure"],
        "time": weather_df["time"],
        "weather_dataframe": weather_df,
    }

    weather_product["processing"]["processing_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return weather_product
