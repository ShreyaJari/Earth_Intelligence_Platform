"""
fetch_baseline.py

Fetches a multi-year historical baseline for comparison
against the currently selected period ("was this hotter/wetter
than normal?").

Baseline is defined as: the same calendar month as the
selected period's start date, across the past N years. This
is a simplification (not exact day-of-year matching across
leap years) but is a defensible, documented approach.
"""

import datetime
import time

import pandas as pd
import requests

from .load_weather import ARCHIVE_URL, HOURLY_VARIABLES

YEARS_BACK = 5


def fetch_weather_baseline(
    latitude,
    longitude,
    reference_start_date,
    years_back=YEARS_BACK,
):
    """
    Fetch a multi-year baseline for the same calendar month as
    reference_start_date.

    Parameters
    ----------
    latitude : float

    longitude : float

    reference_start_date : str (YYYY-MM-DD)
        The selected period's start date — its MONTH is used
        to define the baseline window.

    years_back : int

    Returns
    -------
    dict
        {
            "mean_temperature": float,
            "mean_precipitation_per_hour": float,
            "years_used": list[int],
        }
        or None if the fetch failed.
    """

    start = time.time()

    reference_date = datetime.date.fromisoformat(reference_start_date)

    month = reference_date.month

    current_year = datetime.date.today().year

    years = [current_year - offset for offset in range(1, years_back + 1)]

    all_temperatures = []

    all_precipitation = []

    years_used = []

    for year in years:

        month_start = datetime.date(year, month, 1)

        if month == 12:

            month_end = datetime.date(year, 12, 31)

        else:

            month_end = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": month_start.isoformat(),
            "end_date": month_end.isoformat(),
            "hourly": ["temperature_2m", "precipitation"],
            "timezone": "auto",
        }

        try:

            response = requests.get(
                ARCHIVE_URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()["hourly"]

            all_temperatures.extend(data["temperature_2m"])

            all_precipitation.extend(data["precipitation"])

            years_used.append(year)

        except Exception as error:

            print(
                f"Baseline fetch failed for {year}: " f"{type(error).__name__}: {error}"
            )

    if not years_used:

        return None

    temperature_series = pd.Series(all_temperatures).dropna()

    precipitation_series = pd.Series(all_precipitation).dropna()

    elapsed = round(time.time() - start, 2)

    print(
        f"Baseline fetched from {len(years_used)} year(s) "
        f"in {elapsed}s: {years_used}"
    )

    return {
        "mean_temperature": float(temperature_series.mean()),
        "mean_precipitation_per_hour": float(precipitation_series.mean()),
        "years_used": years_used,
        "fetch_time_seconds": elapsed,
    }
