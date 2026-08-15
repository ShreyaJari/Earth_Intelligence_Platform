"""
Earth Intelligence Platform
Satellite Engine

Rank Acquisitions

Ranks candidate acquisitions (groups of same-date tiles)
based on AOI coverage, cloud cover, and recency.
"""

from datetime import datetime, timezone

import pandas as pd


def rank_acquisitions(acquisitions):
    """
    Rank candidate acquisitions.

    Parameters
    ----------
    acquisitions : list[Acquisition]

    Returns
    -------
    list[Acquisition]
        Sorted, highest score first. Each Acquisition gains
        a `.score` attribute (set dynamically).
    """

    if not acquisitions:

        raise ValueError("No acquisitions to rank.")

    now = datetime.now(timezone.utc)

    ages = [
        (now - pd.to_datetime(acquisition.date, utc=True)).days
        for acquisition in acquisitions
    ]

    max_age = max(ages) if max(ages) > 0 else 1

    for acquisition, age_days in zip(acquisitions, ages):

        coverage_score = acquisition.coverage_percent

        cloud_score = 100.0 - acquisition.cloud_cover

        recency_score = 100.0 * (1 - age_days / max_age)

        acquisition.score = round(
            0.50 * coverage_score + 0.30 * cloud_score + 0.20 * recency_score,
            2,
        )

    ranked = sorted(
        acquisitions,
        key=lambda a: a.score,
        reverse=True,
    )

    print("\n========== RANKED ACQUISITIONS ==========")

    for acquisition in ranked[:10]:

        print(
            f"{acquisition.date}  "
            f"score={acquisition.score}  "
            f"coverage={acquisition.coverage_percent}%  "
            f"cloud={acquisition.cloud_cover}%  "
            f"tiles={len(acquisition.items)}"
        )

    print("==========================================\n")

    return ranked
