"""
Earth Intelligence Platform
Risk Engine

ML Wildfire Risk

Computes a wildfire risk score using a classifier trained on
real NASA FIRMS fire detections vs. background points (see
models/train_wildfire_risk_classifier.py), using the SAME
covariates (temperature, humidity, precipitation, vegetation %)
as the hand-weighted formula in risks/wildfire.py.

Shown SIDE BY SIDE with the hand-weighted score, not as a
replacement — the hand-weighted formula remains the "official"
score used elsewhere in the platform (e.g. Earth Intelligence
Engine's hazard_summary).
"""

from pathlib import Path

import joblib

from .risk_helpers import get_vegetation_percentage, get_weather_stat

MODEL_PATH = (
    Path(__file__).resolve().parents[2] / "models" / "wildfire_risk_classifier.joblib"
)

FEATURE_ORDER = [
    "temperature",
    "humidity",
    "precipitation",
    "vegetation_percentage",
]

_model = None


def _load_model():

    global _model

    if _model is None:

        if not MODEL_PATH.exists():

            return None

        _model = joblib.load(MODEL_PATH)

    return _model


def compute_ml_wildfire_risk(landcover_product, weather_product):
    """
    Compute a learned wildfire risk score.

    Parameters
    ----------
    landcover_product : dict

    weather_product : dict

    Returns
    -------
    dict or None
        None if the trained model file isn't available — the
        page should fall back to showing only the hand-weighted
        score in that case, not raise an error.
    """

    model = _load_model()

    if model is None:

        return None

    temperature = get_weather_stat(weather_product, "temperature", "mean")

    humidity = get_weather_stat(weather_product, "humidity", "mean")

    precipitation = get_weather_stat(weather_product, "precipitation", "total")

    vegetation = get_vegetation_percentage(landcover_product)

    features = [[temperature, humidity, precipitation, vegetation]]

    probabilities = model.predict_proba(features)[0]

    fire_probability = float(probabilities[1])

    score = round(fire_probability * 100, 1)

    if score < 25:

        category = "Low"

    elif score < 50:

        category = "Moderate"

    elif score < 75:

        category = "High"

    else:

        category = "Very High"

    # How far the model's prediction sits from a 50/50 guess —
    # 0 = maximally uncertain, 1 = maximally certain. This is
    # MODEL CERTAINTY, distinct from the data-quality confidence
    # computed elsewhere in the Risk Engine (Phase 1).

    model_certainty = round(abs(fire_probability - 0.5) * 2, 2)

    feature_importance = dict(
        zip(
            FEATURE_ORDER,
            [round(float(v), 3) for v in model.feature_importances_],
        )
    )

    return {
        "score": score,
        "category": category,
        "model_certainty": model_certainty,
        "feature_importance": feature_importance,
        "inputs": {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "precipitation": round(precipitation, 1),
            "vegetation_percentage": round(vegetation, 1),
        },
        "temporal_note": (
            "This model was trained on weather covariates from "
            "a 7-day window ending on each historical fire date. "
            "The inputs above instead reflect whatever date range "
            "was selected when running the Weather Engine, which "
            "may be longer. If that range is much longer than 7 "
            "days, treat this score as less reliable than it "
            "would be with a short, recent window."
        ),
    }
