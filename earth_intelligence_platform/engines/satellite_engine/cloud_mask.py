"""
Earth Intelligence Platform
Satellite Engine

Cloud Mask

Applies the trained cloud detection classifier to prepared
imagery, producing a per-pixel cloud probability mask and an
AOI-specific cloud percentage.

Unlike scene.cloud_cover (Sentinel-2's own whole-tile cloud
estimate, from STAC metadata), this measures cloud presence
directly over the clipped AOI, using a classifier trained on
raw spectral bands rather than a static QA layer.
"""

from pathlib import Path

import joblib
import numpy as np
import xarray as xr

from earth_intelligence_platform.models.cloud_features import extract_features

MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "cloud_classifier.joblib"

_model = None


def _load_model():
    """
    Load the trained cloud classifier, caching it after the
    first call so it's only read from disk once per process.
    """

    global _model

    if _model is None:

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                f"Cloud classifier not found at {MODEL_PATH}. "
                "Run models/train_cloud_classifier.py first."
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def build_cloud_mask(imagery):
    """
    Predict per-pixel cloud probability over the prepared,
    AOI-clipped imagery.

    Parameters
    ----------
    imagery : xarray.Dataset
        Prepared imagery, containing B02, B03, B04, B08.

    Returns
    -------
    tuple
        (cloud_probability: xarray.DataArray,
         cloud_percentage: float)
    """

    print("\n========== CLOUD MASK ==========")

    required = ["B02", "B03", "B04", "B08"]

    for band in required:

        if band not in imagery:

            raise ValueError(f"{band} not found.")

    model = _load_model()

    blue = imagery["B02"].isel(time=0).compute().values

    green = imagery["B03"].isel(time=0).compute().values

    red = imagery["B04"].isel(time=0).compute().values

    nir = imagery["B08"].isel(time=0).compute().values

    height, width = blue.shape

    features = extract_features(blue, green, red, nir)

    valid_mask = np.isfinite(features).all(axis=-1)

    flat_features = features.reshape(-1, features.shape[-1])

    flat_valid = valid_mask.reshape(-1)

    cloud_probability = np.full(
        flat_valid.shape,
        np.nan,
        dtype=np.float32,
    )

    if flat_valid.any():

        predictions = model.predict_proba(flat_features[flat_valid])[:, 1]

        cloud_probability[flat_valid] = predictions

    cloud_probability = cloud_probability.reshape(height, width)

    reference = imagery["B02"].isel(time=0)

    cloud_mask = xr.DataArray(
        cloud_probability,
        coords=reference.coords,
        dims=reference.dims,
        name="cloud_probability",
    )

    valid_predictions = cloud_probability[np.isfinite(cloud_probability)]

    if valid_predictions.size > 0:

        cloud_percentage = round(
            100 * float(np.mean(valid_predictions > 0.5)),
            2,
        )

    else:

        cloud_percentage = 0.0

    print(
        "Cloud Percentage (AOI, ML-measured):",
        cloud_percentage,
        "%",
    )

    print("=================================\n")

    return cloud_mask, cloud_percentage
