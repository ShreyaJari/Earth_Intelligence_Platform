"""
main.py

Public entry point for the Weather Engine.
"""

from .weather_engine import weather_engine


def run_weather_engine(
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
        Standardized weather product.
    """

    return weather_engine(
        aoi,
        catalog,
        start_date=start_date,
        end_date=end_date,
    )
