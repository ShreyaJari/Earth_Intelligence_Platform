"""
Earth Intelligence Platform
Land Cover Engine

ML Classification

Applies the trained spectral land cover classifier to the
Satellite Engine's prepared AOI imagery, producing a
date-specific, per-pixel land cover classification.

For large AOIs, imagery is adaptively downsampled (block-mean
coarsening) before classification, keeping pixel count near a
known-workable budget (TARGET_PIXELS, based on Mumbai's
~17.7M-pixel AOI completing in a few minutes). This keeps
runtime practical for any city size instead of hanging
indefinitely or refusing to run at all — the effective
resolution used is disclosed in the returned metadata.
"""

from pathlib import Path

import joblib
import numpy as np
import xarray as xr

from earth_intelligence_platform.models.landcover_features import (
    extract_features,
)

from .legend import LAND_COVER_LEGEND


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "landcover_classifier.joblib"
)

TARGET_PIXELS = 17_000_000  # Mumbai-scale — known to complete in a few minutes

_model = None


def _load_model():

    global _model

    if _model is None:

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                f"Land cover classifier not found at {MODEL_PATH}. "
                "Run models/train_landcover_classifier.py first."
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def _maybe_downsample(satellite_imagery):
    """
    Adaptively coarsen resolution for large AOIs so ML
    classification's pixel count stays near TARGET_PIXELS,
    regardless of how large the AOI is. Uses block-mean
    downsampling (xarray.coarsen), a standard, defensible way
    to reduce raster resolution while preserving spectral
    values reasonably well.

    Parameters
    ----------
    satellite_imagery : xarray.Dataset

    Returns
    -------
    tuple
        (imagery, downsample_factor)
    """

    y_dim = "y" if "y" in satellite_imagery.dims else "latitude"

    x_dim = "x" if "x" in satellite_imagery.dims else "longitude"

    height = satellite_imagery.sizes[y_dim]

    width = satellite_imagery.sizes[x_dim]

    pixel_count = height * width

    if pixel_count <= TARGET_PIXELS:

        return satellite_imagery, 1

    factor = int(np.ceil((pixel_count / TARGET_PIXELS) ** 0.5))

    original_crs = satellite_imagery.rio.crs

    coarsened = satellite_imagery.coarsen(
        {y_dim: factor, x_dim: factor},
        boundary="trim",
    ).mean()

    coarsened = coarsened.rio.write_crs(original_crs)

    return coarsened, factor


def build_ml_classification(satellite_imagery):
    """
    Predict per-pixel land cover classification from
    Satellite Engine's prepared AOI imagery.

    Parameters
    ----------
    satellite_imagery : xarray.Dataset
        product.imagery.aoi from the Satellite Engine —
        prepared, AOI-clipped bands (B02, B03, B04, B08).

    Returns
    -------
    tuple
        (ml_classification: xarray.DataArray, metadata: dict)
    """

    print("\n========== ML LAND COVER ==========")

    required = ["B02", "B03", "B04", "B08", "B11", "B12"]

    for band in required:

        if band not in satellite_imagery:

            raise ValueError(f"{band} not found.")

    satellite_imagery, downsample_factor = _maybe_downsample(satellite_imagery)

    if downsample_factor > 1:

        print(

            f"Large AOI detected — downsampling by {downsample_factor}x "

            f"(effective resolution: {10 * downsample_factor}m) to keep "

            "ML classification runtime practical."

        )

    model = _load_model()

    blue = satellite_imagery["B02"].isel(time=0).compute().values

    green = satellite_imagery["B03"].isel(time=0).compute().values

    red = satellite_imagery["B04"].isel(time=0).compute().values

    nir = satellite_imagery["B08"].isel(time=0).compute().values

    swir1 = satellite_imagery["B11"].isel(time=0).compute().values

    swir2 = satellite_imagery["B12"].isel(time=0).compute().values

    height, width = blue.shape

    features = extract_features(blue, green, red, nir, swir1, swir2)

    valid_mask = np.isfinite(features).all(axis=-1)

    flat_features = features.reshape(-1, features.shape[-1])

    flat_valid = valid_mask.reshape(-1)

    predictions = np.full(
        flat_valid.shape,
        np.nan,
        dtype=np.float32,
    )

    if flat_valid.any():

        predicted_classes = model.predict(
            flat_features[flat_valid]
        )

        predictions[flat_valid] = predicted_classes

    classification = predictions.reshape(height, width)

    reference = satellite_imagery["B02"].isel(time=0)

    ml_classification = xr.DataArray(
        classification,
        coords=reference.coords,
        dims=reference.dims,
        name="ml_classification",
    )

    valid_predictions = classification[
        np.isfinite(classification)
    ]

    unique_classes = sorted(
        set(int(c) for c in valid_predictions)
    )

    metadata = {
        "method": "Random Forest on Sentinel-2 spectral features (per-pixel)",
        "label_source": "ESA WorldCover (pixel-aligned weak labels)",
        "resolution_note": (
            f"Effective resolution: {10 * downsample_factor}m "
            + (
                "(downsampled from 10m native due to AOI size, to keep "
                "processing time practical)"
                if downsample_factor > 1
                else "(full 10m native resolution, matching the source "
                "Satellite imagery)"
            )
        ),
        "downsample_factor": downsample_factor,
        "known_limitations": (

            "This model was TRAINED using WorldCover as its "

            "labels — so disagreement with the WorldCover map "

            "above should be read as model error by default, "

            "not as a more accurate result. Now includes SWIR "

            "bands (B11/B12) and NDSI, added specifically to fix "

            "a diagnosed snow/Built-up confusion in winter "

            "imagery. See training evaluation report for current "

            "per-class F1 scores."

        ),
        "classes_predicted": [
            LAND_COVER_LEGEND[c]["name"]
            for c in unique_classes
            if c in LAND_COVER_LEGEND
        ],
    }

    print("Classes predicted:", metadata["classes_predicted"])

    print("====================================\n")

    return ml_classification, metadata