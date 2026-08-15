"""
validation.py

Validation utilities for the Weather Engine.
"""

import pandas as pd


def validate_aoi(aoi):
    """
    Validate the Area of Interest.

    Parameters
    ----------
    aoi : dict
    """

    if aoi is None:
        raise ValueError("AOI cannot be None.")

    if "geometry" not in aoi:
        raise ValueError("AOI must contain a geometry.")


def validate_dataset(dataset):
    """
    Validate the selected weather dataset.

    Parameters
    ----------
    dataset : dict
    """

    if dataset is None:
        raise ValueError("No weather dataset selected.")

    required = [
        "name",
        "category",
        "url",
        "variables",
    ]

    for field in required:

        if field not in dataset:

            raise ValueError(f"Dataset missing required field: {field}")


def validate_weather(weather_df):
    """
    Validate downloaded weather data.

    Parameters
    ----------
    weather_df : pandas.DataFrame
    """

    if weather_df is None:
        raise ValueError("Weather data is None.")

    if weather_df.empty:
        raise ValueError("Weather dataset is empty.")

    required_columns = [
        "time",
        "temperature",
        "precipitation",
        "humidity",
        "pressure",
        "wind_speed",
        "wind_direction",
    ]

    missing = [
        column for column in required_columns if column not in weather_df.columns
    ]

    if missing:

        raise ValueError(f"Missing weather columns: {missing}")


def validate_products(products):
    """
    Validate processed weather products.

    Parameters
    ----------
    products : dict
    """

    required = [
        "temperature",
        "precipitation",
        "wind_speed",
        "wind_direction",
        "humidity",
        "pressure",
        "time",
        "weather_dataframe",
    ]

    for product in required:

        if product not in products:

            raise ValueError(f"Missing product: {product}")

        if products[product] is None:

            raise ValueError(f"Product is None: {product}")
