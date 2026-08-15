"""
Earth Intelligence Platform
Terrain Engine

Logger Configuration
"""

import logging


def get_logger(name="terrain_engine"):
    """
    Create and configure a logger for the Terrain Engine.

    Parameters
    ----------
    name : str, optional
        Logger name.

    Returns
    -------
    logging.Logger
        Configured logger.
    """

    logger = logging.getLogger(name)

    if logger.hasHandlers():

        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    handler = logging.StreamHandler()

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
