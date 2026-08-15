"""
Earth Intelligence Platform
Land Cover Refinement Model

Train Land Cover Classifier

Trains a per-pixel land cover classifier directly on Sentinel-2
spectral bands, derived indices, and local texture features,
using ESA WorldCover as weak (pixel-aligned) training labels.

Uses stratified per-class, per-site sampling — rather than
uniform random sampling — so classes that are naturally rare
within a scene (e.g. Shrubland within a mostly-cropland scene)
aren't lost to random subsampling. Classes present only
marginally at a site (likely noisy/ambiguous edge pixels, e.g.
"Bare" sandbars misclassified within a rainforest scene) are
capped at a much smaller quota instead of taking a full share,
so they don't dilute the dataset with unrepresentative examples.

STANDALONE SCRIPT — run this ONCE, locally, with internet
access. Not part of the live pipeline.

Run with:
    python earth_intelligence_platform/models/train_landcover_classifier.py
"""

import sys
from pathlib import Path

import joblib
import numpy as np
import planetary_computer
from odc.stac import load
from pystac_client import Client
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

try:

    from landcover_features import extract_features

except ImportError:

    from earth_intelligence_platform.models.landcover_features import extract_features

try:

    sys.path.append(
        str(Path(__file__).resolve().parents[1] / "engines" / "land_cover_engine")
    )

    from legend import LAND_COVER_LEGEND

except ImportError:

    from earth_intelligence_platform.engines.land_cover_engine.legend import (
        LAND_COVER_LEGEND,
    )


STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"

MODEL_OUTPUT_PATH = Path(__file__).resolve().parent / "landcover_classifier.joblib"

# ---------------------------------------------------------
# Training sites
#
# Original 7 general-purpose sites, plus 7 added specifically
# to target classes that scored poorly in the first training
# run (Shrubland, Snow/Ice, Herbaceous Wetland, Mangroves,
# Moss/Lichen, Built-up).
# ---------------------------------------------------------

TRAINING_SITES = [
    {
        "name": "Mumbai, India (urban)",
        "lon": 72.87,
        "lat": 19.07,
        "datetime": "2025-01-01/2025-03-31",
    },
    {
        "name": "Amazon Rainforest (dense forest)",
        "lon": -60.0,
        "lat": -3.0,
        "datetime": "2025-06-01/2025-08-31",
    },
    {
        "name": "US Midwest (cropland)",
        "lon": -95.0,
        "lat": 41.5,
        "datetime": "2025-07-01/2025-08-31",
    },
    {
        "name": "Sahara Desert (bare)",
        "lon": 10.0,
        "lat": 25.0,
        "datetime": "2025-06-01/2025-06-30",
    },
    {
        "name": "Swiss Alps (snow/mountain)",
        "lon": 8.0,
        "lat": 46.5,
        "datetime": "2025-02-01/2025-02-28",
    },
    {
        "name": "Netherlands (mixed urban/water)",
        "lon": 4.9,
        "lat": 52.3,
        "datetime": "2025-04-01/2025-06-30",
    },
    {
        "name": "Bangladesh Delta (wetland)",
        "lon": 90.0,
        "lat": 23.5,
        "datetime": "2025-01-01/2025-03-31",
    },
    # --- Added for weak classes ---
    {
        "name": "Sundarbans (mangroves)",
        "lon": 89.1,
        "lat": 21.9,
        "datetime": "2025-01-01/2025-03-31",
    },
    {
        "name": "Okavango Delta, Botswana (herbaceous wetland)",
        "lon": 22.9,
        "lat": -19.3,
        "datetime": "2025-06-01/2025-08-31",
    },
    {
        "name": "Alice Springs, Australia (shrubland)",
        "lon": 133.9,
        "lat": -23.7,
        "datetime": "2025-05-01/2025-07-31",
    },
    {
        "name": "Patagonia Steppe, Argentina (shrubland)",
        "lon": -69.2,
        "lat": -49.3,
        "datetime": "2025-01-01/2025-03-31",
    },
    {
        "name": "Svalbard, Norway (snow/ice)",
        "lon": 15.6,
        "lat": 78.2,
        "datetime": "2025-04-01/2025-05-31",
    },
    {
        "name": "Yamal Peninsula, Siberia (moss/lichen tundra)",
        "lon": 70.0,
        "lat": 67.5,
        "datetime": "2025-06-01/2025-08-31",
    },
    {
        "name": "Manhattan, New York (dense built-up)",
        "lon": -73.97,
        "lat": 40.78,
        "datetime": "2025-04-01/2025-09-30",
    },
]

VALID_CLASSES = list(LAND_COVER_LEGEND.keys())

MAX_PIXELS_PER_CLASS_PER_SITE = 2500

MAX_MINOR_CLASS_PIXELS_PER_SITE = 300

MIN_NATURAL_FRACTION = 0.02  # class must be >=2% of a site's pixels to earn full quota

MIN_TOTAL_PIXELS_WARNING = 500


def stratified_sample(
    features_flat,
    labels_flat,
    max_per_class,
    max_minor_class,
    min_natural_fraction,
):
    """
    Sample up to max_per_class pixels for each class present —
    but only if that class makes up at least min_natural_fraction
    of this site's pixels. Classes present only marginally (e.g.
    isolated sandbars misclassified as "Bare" in a rainforest
    scene) are capped at max_minor_class instead, so they still
    contribute a few examples without diluting the dataset with
    likely-noisy edge pixels.
    """

    total = len(labels_flat)

    sampled_features = []

    sampled_labels = []

    for class_id in np.unique(labels_flat):

        class_idx = np.where(labels_flat == class_id)[0]

        natural_fraction = len(class_idx) / total

        cap = (
            max_per_class
            if natural_fraction >= min_natural_fraction
            else max_minor_class
        )

        if len(class_idx) > cap:

            class_idx = np.random.choice(
                class_idx,
                cap,
                replace=False,
            )

        sampled_features.append(features_flat[class_idx])

        sampled_labels.append(labels_flat[class_idx])

    return (
        np.concatenate(sampled_features, axis=0),
        np.concatenate(sampled_labels, axis=0),
    )


def fetch_site_pixels(site, catalog):
    """
    Fetch a Sentinel-2 scene and pixel-aligned WorldCover data
    for one training site, returning stratified feature/label
    pairs. Returns (None, None) if the fetch fails for any
    reason (network issue, corrupted source file, etc.) so a
    single bad scene doesn't abort the whole training run.
    """

    print(f"Fetching: {site['name']}")

    try:

        search = catalog.search(
            collections=["sentinel-2-l2a"],
            intersects={"type": "Point", "coordinates": [site["lon"], site["lat"]]},
            datetime=site["datetime"],
            query={"eo:cloud_cover": {"lte": 20}},
            max_items=1,
        )

        items = list(search.items())

        if not items:

            print("  No Sentinel-2 scene found, skipping.")

            return None, None

        item = planetary_computer.sign(items[0])

        s2_data = load(

            [item],

            bands=["B02", "B03", "B04", "B08", "B11", "B12"],

            resolution=10,

            resampling="bilinear",

            chunks={},

        )

        geobox = s2_data.odc.geobox

        wc_catalog = Client.open(
            STAC_URL,
            modifier=planetary_computer.sign_inplace,
        )

        wc_search = wc_catalog.search(
            collections=["esa-worldcover"],
            intersects={"type": "Point", "coordinates": [site["lon"], site["lat"]]},
        )

        wc_items = list(wc_search.item_collection())

        if not wc_items:

            print("  No WorldCover data found, skipping.")

            return None, None

        wc_data = load(
            wc_items,
            bands=["map"],
            geobox=geobox,  # forces identical pixel grid to Sentinel-2
            chunks={},
        )

        blue = s2_data["B02"].isel(time=0).values

        green = s2_data["B03"].isel(time=0).values

        red = s2_data["B04"].isel(time=0).values

        nir = s2_data["B08"].isel(time=0).values

        swir1 = s2_data["B11"].isel(time=0).values

        swir2 = s2_data["B12"].isel(time=0).values

        worldcover = wc_data["map"].values

        if worldcover.ndim == 3:

            worldcover = worldcover[0]

        features = extract_features(blue, green, red, nir, swir1, swir2)

    except Exception as error:

        print(
            f"  Failed to fetch/read data for {site['name']}: "
            f"{type(error).__name__}: {error}"
        )

        print("  Skipping this site and continuing.")

        return None, None

    # ---------------------------------------------------------
    # extract_features() needs full 2D arrays (not flattened)
    # so texture features have real neighborhood context —
    # flatten AFTER computing features, not before.
    # ---------------------------------------------------------

    features = extract_features(blue, green, red, nir, swir1, swir2)

    features_flat = features.reshape(-1, features.shape[-1])

    labels_flat = worldcover.flatten()

    valid_mask = np.isin(labels_flat, VALID_CLASSES) & np.isfinite(features_flat).all(
        axis=-1
    )

    features_flat = features_flat[valid_mask]

    labels_flat = labels_flat[valid_mask]

    if len(labels_flat) == 0:

        print("  No valid labeled pixels, skipping.")

        return None, None

    features_sampled, labels_sampled = stratified_sample(
        features_flat,
        labels_flat,
        MAX_PIXELS_PER_CLASS_PER_SITE,
        MAX_MINOR_CLASS_PIXELS_PER_SITE,
        MIN_NATURAL_FRACTION,
    )

    class_counts = {
        LAND_COVER_LEGEND.get(int(c), {}).get("name", str(c)): int(
            (labels_sampled == c).sum()
        )
        for c in np.unique(labels_sampled)
    }

    print(f"  {len(labels_sampled)} pixels sampled — {class_counts}")

    return features_sampled, labels_sampled


def main():

    catalog = Client.open(
        STAC_URL,
        modifier=planetary_computer.sign_inplace,
    )

    all_features = []

    all_labels = []

    for site in TRAINING_SITES:

        features, labels = fetch_site_pixels(site, catalog)

        if features is None:

            continue

        all_features.append(features)

        all_labels.append(labels)

    X = np.concatenate(all_features, axis=0)

    y = np.concatenate(all_labels, axis=0)

    print(f"\nTotal training pixels: {len(y)}")

    unique, counts = np.unique(y, return_counts=True)

    for class_id, count in zip(unique, counts):

        name = LAND_COVER_LEGEND.get(int(class_id), {}).get("name", "Unknown")

        flag = (
            "  <-- still low, consider more sites for this class"
            if count < MIN_TOTAL_PIXELS_WARNING
            else ""
        )

        print(f"  {name}: {count}{flag}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
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
            zero_division=0,
        )
    )

    print("=================================\n")

    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_OUTPUT_PATH)

    print(f"Model saved to: {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":

    main()
