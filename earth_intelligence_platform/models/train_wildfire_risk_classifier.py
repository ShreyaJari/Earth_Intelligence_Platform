"""
Earth Intelligence Platform
Wildfire Risk Calibration Model

Train Wildfire Risk Classifier

Trains a classifier predicting wildfire likelihood from the
same covariates the hand-weighted formula uses (temperature,
humidity, precipitation, vegetation %), using real NASA FIRMS
fire detections as positive samples and randomly sampled
background points as negatives.

STANDALONE SCRIPT — run this ONCE, locally, with internet
access. Place downloaded FIRMS archive CSVs
(modis_<year>_<country>.csv) in:
    earth_intelligence_platform/models/firms_data/

Run with:
    python earth_intelligence_platform/models/train_wildfire_risk_classifier.py
"""

import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from point_covariates import fetch_point_covariates
from scipy.spatial import cKDTree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

FIRMS_DATA_DIR = Path(__file__).resolve().parent / "firms_data"

MODEL_OUTPUT_PATH = Path(__file__).resolve().parent / "wildfire_risk_classifier.joblib"

CONFIDENCE_THRESHOLD = 50

EXCLUSION_DEGREES = 0.05  # ~5km — background points must be this far from any real fire

POINTS_PER_CLASS_PER_FILE = 150  # pilot size — scale up once this run succeeds

MAX_WORKERS = 8

FEATURE_NAMES = [
    "temperature",
    "humidity",
    "precipitation",
    "vegetation_percentage",
]


def load_firms_file(path):
    """
    Load one FIRMS archive CSV, filtering to genuine
    presumed-vegetation-fire detections (type == 0) above the
    confidence threshold.
    """

    df = pd.read_csv(path)

    df = df[(df["type"] == 0) & (df["confidence"] >= CONFIDENCE_THRESHOLD)]

    return df


def sample_positive_points(fire_df, n):
    """
    Randomly sample n rows from the filtered fire detections.
    """

    if len(fire_df) > n:

        fire_df = fire_df.sample(n, random_state=42)

    return [
        (row["latitude"], row["longitude"], row["acq_date"])
        for _, row in fire_df.iterrows()
    ]


def sample_background_points(fire_df, n):
    """
    Randomly sample n background (non-fire) points within the
    fire dataset's bounding box, excluding points too close to
    any real fire detection.
    """

    min_lat = fire_df["latitude"].min()

    max_lat = fire_df["latitude"].max()

    min_lon = fire_df["longitude"].min()

    max_lon = fire_df["longitude"].max()

    fire_coords = fire_df[["latitude", "longitude"]].values

    tree = cKDTree(fire_coords)

    dates = fire_df["acq_date"].tolist()

    background_points = []

    attempts = 0

    max_attempts = n * 20

    while len(background_points) < n and attempts < max_attempts:

        attempts += 1

        lat = np.random.uniform(min_lat, max_lat)

        lon = np.random.uniform(min_lon, max_lon)

        distance, _ = tree.query([lat, lon])

        if distance < EXCLUSION_DEGREES:

            continue

        date_str = np.random.choice(dates)

        background_points.append((lat, lon, date_str))

    return background_points


def fetch_covariates_for_points(points, label):
    """
    Fetch covariates for a list of (lat, lon, date) points in
    parallel, returning feature rows and labels for whichever
    points succeeded.
    """

    features = []

    labels = []

    def fetch_one(point):

        lat, lon, date_str = point

        return fetch_point_covariates(lat, lon, date_str)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = {executor.submit(fetch_one, point): point for point in points}

        for future in as_completed(futures):

            result = future.result()

            if result is not None:

                features.append([result[name] for name in FEATURE_NAMES])

                labels.append(label)

    return features, labels


def main():

    firms_files = sorted(glob.glob(str(FIRMS_DATA_DIR / "modis_*.csv")))

    if not firms_files:

        raise RuntimeError(
            f"No FIRMS archive files found in {FIRMS_DATA_DIR}. "
            "Download modis_<year>_<country>.csv files there first."
        )

    all_features = []

    all_labels = []

    for file_path in firms_files:

        print(f"\nProcessing: {Path(file_path).name}")

        fire_df = load_firms_file(file_path)

        print(f"  {len(fire_df)} genuine fire detections after filtering.")

        if len(fire_df) == 0:

            print("  No valid fire detections, skipping file.")

            continue

        positive_points = sample_positive_points(
            fire_df,
            POINTS_PER_CLASS_PER_FILE,
        )

        background_points = sample_background_points(
            fire_df,
            POINTS_PER_CLASS_PER_FILE,
        )

        print(f"  Fetching covariates for {len(positive_points)} fire points...")

        pos_features, pos_labels = fetch_covariates_for_points(
            positive_points,
            label=1,
        )

        print(f"    {len(pos_features)} succeeded.")

        print(
            f"  Fetching covariates for {len(background_points)} background points..."
        )

        neg_features, neg_labels = fetch_covariates_for_points(
            background_points,
            label=0,
        )

        print(f"    {len(neg_features)} succeeded.")

        all_features.extend(pos_features)

        all_labels.extend(pos_labels)

        all_features.extend(neg_features)

        all_labels.extend(neg_labels)

    print(f"\nTotal training points: {len(all_labels)}")

    if len(all_labels) < 20:

        raise RuntimeError(
            "Not enough training points succeeded to train a "
            "meaningful model. Check network connectivity and "
            "the VERIFY notes in point_covariates.py."
        )

    X = np.array(all_features)

    y = np.array(all_labels)

    print(f"  Fire: {int(y.sum())}  Background: {int((1 - y).sum())}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )

    print("\nTraining classifier...")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n========== EVALUATION ==========")

    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["Background", "Fire"],
        )
    )

    print("Feature importances:")

    for name, importance in zip(FEATURE_NAMES, model.feature_importances_):

        print(f"  {name}: {importance:.3f}")

    print("=================================\n")

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_OUTPUT_PATH)

    print(f"Model saved to: {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":

    main()
