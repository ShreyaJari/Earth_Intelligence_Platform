"""
compute_statistics.py

Compute summary statistics for the Risk Engine.
"""

import time


def compute_statistics(risk_product):
    """
    Compute summary statistics for all risks.

    Parameters
    ----------
    risk_product : dict

    Returns
    -------
    dict
    """

    start = time.time()

    risks = risk_product["products"]

    scores = {name: risk["score"] for name, risk in risks.items()}

    categories = {name: risk["category"] for name, risk in risks.items()}

    average_risk = round(
        sum(scores.values()) / len(scores),
        1,
    )

    highest_risk = max(
        scores,
        key=scores.get,
    )

    category_counts = {
        "Low": 0,
        "Moderate": 0,
        "High": 0,
        "Very High": 0,
    }

    for category in categories.values():

        category_counts[category] += 1

    risk_product["statistics"] = {
        "highest_risk": {
            "hazard": highest_risk,
            "score": scores[highest_risk],
            "category": categories[highest_risk],
        },
        "average_risk": average_risk,
        "category_counts": category_counts,
        "risk_summary": {
            hazard: {
                "score": scores[hazard],
                "category": categories[hazard],
            }
            for hazard in risks
        },
    }

    risk_product["processing"]["statistics_time_seconds"] = round(
        time.time() - start,
        2,
    )

    return risk_product
