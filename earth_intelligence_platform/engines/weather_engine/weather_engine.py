"""
weather_engine.py

Main orchestration for the Weather Engine.
"""

from .compute_statistics import compute_statistics
from .load_weather import load_weather
from .logger import get_logger
from .process_weather import process_weather
from .select_dataset import select_dataset
from .validation import (
    validate_aoi,
    validate_dataset,
    validate_products,
    validate_weather,
)
from .weather_product import create_weather_product

logger = get_logger()


def weather_engine(
    aoi,
    catalog,
    start_date=None,
    end_date=None,
):
    """
    Execute the Weather Engine.

    Parameters
    ----------
    aoi : dict

    catalog : list

    start_date : str, optional (YYYY-MM-DD)

    end_date : str, optional (YYYY-MM-DD)

    Returns
    -------
    dict
    """

    logger.info("Starting Weather Engine.")

    weather_product = create_weather_product()

    try:

        validate_aoi(aoi)

        dataset, weather_product = select_dataset(
            catalog,
            weather_product,
        )

        validate_dataset(dataset)

        weather_data, weather_product = load_weather(
            aoi,
            dataset,
            weather_product,
            start_date=start_date,
            end_date=end_date,
        )

        validate_weather(weather_data)

        weather_product = process_weather(
            weather_data,
            weather_product,
        )

        validate_products(weather_product["products"])

        weather_product = compute_statistics(
            weather_product,
        )

        weather_product["success"] = True

        logger.info("Weather Engine completed successfully.")

    except Exception as e:

        logger.exception("Weather Engine failed.")

        weather_product["errors"].append(str(e))

    return weather_product
