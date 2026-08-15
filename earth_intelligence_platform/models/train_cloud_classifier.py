"""
Earth Intelligence Platform
Cloud Detection Model

Train Cloud Classifier

Trains a per-pixel cloud/clear classifier for Sentinel-2
imagery using the Scene Classification Layer (SCL) band as
training labels.

STANDALONE SCRIPT — run this ONCE, locally, with internet
access. It is not part of the live pipeline.

Run with:
    python earth_intelligence_platform/models/train_cloud_classifier.py
"""

from pathlib import Path

import joblib
import numpy as np
import planetary_computer
from cloud_features import extract_features
from odc.stac import load
from pystac_client import Client
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

MODEL_OUTPUT_PATH = Path(__file__).resolve().parent / "cloud_classifier.joblib"

# ---------------------------------------------------------
# Training locations
#
# Deliberately diverse regions/seasons, so the classifier
# sees clear sky, dense cloud, thin cirrus, snow, water, and
# vegetation, rather than overfitting to one climate.
# ---------------------------------------------------------

TRAINING_SITES = [
    {
        "name": "Mumbai, India (monsoon)",
        "lon": 72.87,
        "lat": 19.07,
        "datetime": "2025-07-01/2025-07-31",
    },
    {
        "name": "London, UK (winter, cloudy)",
        "lon": -0.13,
        "lat": 51.51,
        "datetime": "2025-01-01/2025-01-31",
    },
    {
        "name": "Sahara Desert (clear, bright)",
        "lon": 10.0,
        "lat": 25.0,
        "datetime": "2025-06-01/2025-06-30",
    },
    {
        "name": "Amazon Rainforest (vegetation, cloud)",
        "lon": -60.0,
        "lat": -3.0,
        "datetime": "2025-08-01/2025-08-31",
    },
    {
        "name": "Swiss Alps (snow)",
        "lon": 8.0,
        "lat": 46.5,
        "datetime": "2025-02-01/2025-02-28",
    },
    {
        "name": "Pacific Ocean off California (water)",
        "lon": -123.0,
        "lat": 37.0,
        "datetime": "2025-05-01/2025-05-31",
    },
]

PIXELS_PER_SCENE = 5000

# ---------------------------------------------------------
# SCL class codes -> binary label
#
#  8 = cloud medium probability
#  9 = cloud high probability
# 10 = thin cirrus
#
#  4 = vegetation
#  5 = bare soil
#  6 = water
#  7 = unclassified
# 11 = snow/ice
#
# Classes 0 (no data), 1 (saturated), 2 (dark area),
# 3 (cloud shadow) are ambiguous and excluded from training.
# ---------------------------------------------------------

CLOUD_CLASSES = {8, 9, 10}

CLEAR_CLASSES = {4, 5, 6, 7, 11}


def fetch_training_pixels():
    """
    Search and download one scene per training site, extract
    feature/label pairs for a random sample of pixels.
    """

    catalog = Client.open(
        STAC_URL,
        ignore_conformance=True,
    )

    all_features = []

    all_labels = []

    for site in TRAINING_SITES:

        print(f"Fetching: {site['name']}")

        search = catalog.search(
            collections=["sentinel-2-l2a"],
            intersects={
                "type": "Point",
                "coordinates": [site["lon"], site["lat"]],
            },
            datetime=site["datetime"],
            query={"eo:cloud_cover": {"lte": 90}},
            max_items=1,
        )

        items = list(search.items())

        if not items:

            print(f"  No scenes found for {site['name']}, skipping.")

            continue

        item = planetary_computer.sign(items[0])

        data = load(
            [item],
            bands=["B02", "B03", "B04", "B08", "SCL"],
            resolution=20,
            chunks={},
        )

        blue = data["B02"].isel(time=0).values

        green = data["B03"].isel(time=0).values

        red = data["B04"].isel(time=0).values

        nir = data["B08"].isel(time=0).values

        scl = data["SCL"].isel(time=0).values

        features = extract_features(blue, green, red, nir)

        features = features.reshape(-1, features.shape[-1])

        scl_flat = scl.flatten()

        valid_mask = np.isin(scl_flat, list(CLOUD_CLASSES)) | np.isin(
            scl_flat, list(CLEAR_CLASSES)
        )

        features = features[valid_mask]

        labels = np.isin(
            scl_flat[valid_mask],
            list(CLOUD_CLASSES),
        ).astype(int)

        if len(labels) > PIXELS_PER_SCENE:

            sample_idx = np.random.choice(
                len(labels),
                PIXELS_PER_SCENE,
                replace=False,
            )

            features = features[sample_idx]

            labels = labels[sample_idx]

        print(
            f"  {len(labels)} pixels "
            f"({labels.sum()} cloud, {len(labels) - labels.sum()} clear)"
        )

        all_features.append(features)

        all_labels.append(labels)

    X = np.concatenate(all_features, axis=0)

    y = np.concatenate(all_labels, axis=0)

    return X, y


def main():

    print("Fetching training data...\n")

    X, y = fetch_training_pixels()

    print(f"\nTotal training pixels: {len(y)}")

    print(f"Cloud: {y.sum()}  Clear: {len(y) - y.sum()}\n")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    print("Training Random Forest classifier...")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n========== EVALUATION ==========")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["Clear", "Cloud"],
        )
    )

    print("Confusion Matrix:")

    print(confusion_matrix(y_test, y_pred))

    print("=================================\n")

    MODEL_OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(model, MODEL_OUTPUT_PATH)

    print(f"Model saved to: {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":

    main()
