"""
logger.py

Logging configuration for the Weather Engine.
"""

import logging


def get_logger():
    """
    Return the Weather Engine logger.

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger("WeatherEngine")

    if not logger.handlers:

        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
