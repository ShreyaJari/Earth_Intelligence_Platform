"""
compute_statistics.py

Compute Weather Engine statistics.
"""

import time

import pandas as pd

from .fetch_baseline import fetch_weather_baseline


def compute_statistics(
    weather_product,
):
    """
    Compute weather statistics, including extremes, daily
    aggregation summary, and a historical baseline comparison.

    Parameters
    ----------
    weather_product : dict

    Returns
    -------
    dict
    """

    start = time.time()

    products = weather_product["products"]

    temperature = products["temperature"]

    precipitation = products["precipitation"]

    wind_speed = products["wind_speed"]

    wind_direction = products["wind_direction"]

    humidity = products["humidity"]

    pressure = products["pressure"]

    time_series = products["time"]

    weather_product["statistics"] = {
        "temperature": {
            "minimum": float(temperature.min()),
            "maximum": float(temperature.max()),
            "mean": float(temperature.mean()),
        },
        "precipitation": {
            "minimum": float(precipitation.min()),
            "maximum": float(precipitation.max()),
            "mean": float(precipitation.mean()),
            "total": float(precipitation.sum()),
        },
        "wind_speed": {
            "minimum": float(wind_speed.min()),
            "maximum": float(wind_speed.max()),
            "mean": float(wind_speed.mean()),
        },
        "wind_direction": {"dominant": int(wind_direction.mode().iloc[0])},
        "humidity": {
            "minimum": float(humidity.min()),
            "maximum": float(humidity.max()),
            "mean": float(humidity.mean()),
        },
        "pressure": {
            "minimum": float(pressure.min()),
            "maximum": float(pressure.max()),
            "mean": float(pressure.mean()),
        },
    }

    # ---------------------------------------------------------
    # Tier 1: Extremes
    # ---------------------------------------------------------

    hottest_index = temperature.idxmax()

    coldest_index = temperature.idxmin()

    heaviest_rain_index = precipitation.idxmax()

    weather_product["statistics"]["extremes"] = {
        "hottest_hour": {
            "time": str(time_series.loc[hottest_index]),
            "value": float(temperature.loc[hottest_index]),
        },
        "coldest_hour": {
            "time": str(time_series.loc[coldest_index]),
            "value": float(temperature.loc[coldest_index]),
        },
        "heaviest_rain_hour": {
            "time": str(time_series.loc[heaviest_rain_index]),
            "value": float(precipitation.loc[heaviest_rain_index]),
        },
    }

    # ---------------------------------------------------------
    # Tier 1: Wet / Dry day counts (daily precipitation totals)
    # ---------------------------------------------------------

    daily_df = pd.DataFrame(
        {
            "time": pd.to_datetime(time_series),
            "precipitation": precipitation,
        }
    )

    daily_precipitation = (
        daily_df.set_index("time")["precipitation"].resample("D").sum()
    )

    weather_product["statistics"]["wet_days"] = int((daily_precipitation > 0.1).sum())

    weather_product["statistics"]["dry_days"] = int((daily_precipitation <= 0.1).sum())

    weather_product["statistics"]["total_days"] = int(len(daily_precipitation))

    # ---------------------------------------------------------
    # Tier 2: Historical Baseline + Anomaly
    # ---------------------------------------------------------

    metadata = weather_product["metadata"]

    start_date = metadata.get("start_date")

    if start_date is not None:

        baseline = fetch_weather_baseline(
            latitude=metadata["latitude"],
            longitude=metadata["longitude"],
            reference_start_date=start_date,
        )

        weather_product["baseline"] = baseline

        if baseline is not None:

            temperature_delta = (
                weather_product["statistics"]["temperature"]["mean"]
                - baseline["mean_temperature"]
            )

            precipitation_delta = (
                weather_product["statistics"]["precipitation"]["mean"]
                - baseline["mean_precipitation_per_hour"]
            )

            weather_product["anomaly"] = {
                "temperature_delta": round(temperature_delta, 2),
                "precipitation_delta_per_hour": round(precipitation_delta, 3),
                "baseline_years": baseline["years_used"],
            }

        else:

            weather_product["anomaly"] = None

    else:

        weather_product["baseline"] = None

        weather_product["anomaly"] = None

    weather_product["processing"]["statistics_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return weather_product
