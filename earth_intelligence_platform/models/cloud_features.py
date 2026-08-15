"""
Earth Intelligence Platform
Cloud Detection Model

Cloud Features

Shared feature engineering for the cloud detection classifier.

IMPORTANT: This module is used by BOTH the training script
(train_cloud_classifier.py) and the runtime inference module
(engines/satellite_engine/cloud_mask.py). Both must use
IDENTICAL feature extraction, or the trained model's learned
weights will be applied to a different feature space at
inference time, silently producing wrong predictions. Do not
duplicate this logic anywhere else.
"""

import numpy as np

FEATURE_NAMES = [
    "blue",
    "green",
    "red",
    "nir",
    "ndvi",
    "brightness",
    "spectral_std",
    "blue_red_ratio",
    "green_nir_ratio",
]


def extract_features(blue, green, red, nir):
    """
    Build a per-pixel feature array from raw Sentinel-2
    reflectance bands.

    Works for both flattened 1D pixel arrays (training) and
    2D image arrays (inference) — the feature axis is always
    added as the last axis.

    Parameters
    ----------
    blue, green, red, nir : numpy.ndarray
        Raw band values (B02, B03, B04, B08), all the same
        shape. Sentinel-2 L2A digital numbers, typically
        0-10000+.

    Returns
    -------
    numpy.ndarray
        Shape (..., 9), matching FEATURE_NAMES on the last axis.
    """

    blue = blue.astype(np.float32) / 10000.0

    green = green.astype(np.float32) / 10000.0

    red = red.astype(np.float32) / 10000.0

    nir = nir.astype(np.float32) / 10000.0

    blue = np.clip(blue, 0, 1)

    green = np.clip(green, 0, 1)

    red = np.clip(red, 0, 1)

    nir = np.clip(nir, 0, 1)

    eps = 1e-6

    ndvi = (nir - red) / (nir + red + eps)

    brightness = (blue + green + red) / 3.0

    spectral_std = np.std(
        np.stack([blue, green, red], axis=-1),
        axis=-1,
    )

    blue_red_ratio = blue / (red + eps)

    green_nir_ratio = green / (nir + eps)

    features = np.stack(
        [
            blue,
            green,
            red,
            nir,
            ndvi,
            brightness,
            spectral_std,
            blue_red_ratio,
            green_nir_ratio,
        ],
        axis=-1,
    )

    return features
