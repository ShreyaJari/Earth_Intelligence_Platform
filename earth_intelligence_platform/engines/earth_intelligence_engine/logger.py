"""
logger.py

Logger for the Earth Intelligence Engine.
"""

import logging


def get_logger():

    logger = logging.getLogger("EarthIntelligenceEngine")

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
