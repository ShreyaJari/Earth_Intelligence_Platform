"""
compute_statistics.py

Compute summary statistics for the Earth Intelligence Engine.
"""

import time


def compute_statistics(intelligence_product):
    """
    Compute Earth Intelligence summary statistics.

    Parameters
    ----------
    intelligence_product : dict

    Returns
    -------
    dict
    """

    start = time.time()

    intelligence = intelligence_product["intelligence"]

    score = intelligence["earth_intelligence_score"]["score"]

    sustainability = intelligence["sustainability"]["score"]

    highest_risk = intelligence["hazard_summary"]["highest_risk"]

    statistics = {
        "earth_intelligence_score": score,
        "sustainability_score": sustainability,
        "highest_risk": highest_risk,
        "number_of_insights": len(intelligence["key_insights"]),
        "number_of_recommendations": len(intelligence["recommendations"]),
    }

    intelligence_product["statistics"] = statistics

    intelligence_product["processing"]["statistics_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return intelligence_product
