"""
Earth Intelligence Platform
Land Cover Refinement Model

Land Cover Features

Shared feature engineering for the land cover classifier.

IMPORTANT: Used by BOTH train_landcover_classifier.py and
engines/land_cover_engine/ml_classification.py. Both must use
IDENTICAL feature extraction — do not duplicate this logic.

IMPORTANT: This function requires FULL, UN-FLATTENED 2D band
arrays as input (not pre-sampled/flattened pixel lists), since
the texture features need neighborhood context. Flatten the
output AFTER calling this, not before.

Includes SWIR bands (B11, B12) and NDSI (Normalized Difference
Snow Index), added specifically to fix a diagnosed failure
mode: without SWIR, snow-covered ground and bright built
surfaces were spectrally similar enough to be confused,
observed directly in winter imagery of Aomori, Japan, where
snow cover was almost entirely misclassified as Built-up.
"""

import numpy as np
from scipy.ndimage import uniform_filter


TEXTURE_WINDOW = 5  # pixels per side; 50m at 10m resolution


FEATURE_NAMES = [

    "blue",

    "green",

    "red",

    "nir",

    "swir1",

    "swir2",

    "ndvi",

    "ndwi",

    "ndsi",

    "brightness",

    "spectral_std",

    "blue_red_ratio",

    "green_nir_ratio",

    "red_texture_std",

    "nir_texture_std",

    "ndvi_texture_std",

]


def _local_std(band, window=TEXTURE_WINDOW):
    """
    NaN-aware local standard deviation within a sliding window.

    A plain box filter treats any NaN in a window as poisoning
    the entire window average, which cascades outward. This
    version averages only over valid pixels within each
    window, so a NaN only affects windows where ALL neighbors
    are invalid.
    """

    valid_mask = np.isfinite(band).astype(np.float32)

    band_filled = np.where(np.isfinite(band), band, 0.0).astype(np.float32)

    window_area = window * window

    valid_count = uniform_filter(valid_mask, size=window) * window_area

    valid_count = np.clip(valid_count, 1e-6, None)

    local_sum = uniform_filter(band_filled, size=window) * window_area

    local_sum_sq = uniform_filter(band_filled ** 2, size=window) * window_area

    local_mean = local_sum / valid_count

    local_mean_sq = local_sum_sq / valid_count

    local_var = local_mean_sq - local_mean ** 2

    local_var = np.clip(local_var, 0, None)

    local_std = np.sqrt(local_var)

    fully_invalid = valid_count < 1.0

    local_std = np.where(fully_invalid, np.nan, local_std)

    return local_std


def extract_features(blue, green, red, nir, swir1, swir2):
    """
    Build a per-pixel feature array from raw Sentinel-2
    reflectance bands, including spectral indices, an SWIR-based
    snow index, and local texture measures.

    Parameters
    ----------
    blue, green, red, nir, swir1, swir2 : numpy.ndarray
        Raw band values (B02, B03, B04, B08, B11, B12), all
        the same 2D shape (H, W). B11/B12 are native 20m
        resolution but are expected here already resampled to
        match the other bands (handled upstream by
        odc.stac.load with a shared geobox and bilinear
        resampling).

    Returns
    -------
    numpy.ndarray
        Shape (H, W, 16), matching FEATURE_NAMES on the last axis.
    """

    blue = blue.astype(np.float32) / 10000.0

    green = green.astype(np.float32) / 10000.0

    red = red.astype(np.float32) / 10000.0

    nir = nir.astype(np.float32) / 10000.0

    swir1 = swir1.astype(np.float32) / 10000.0

    swir2 = swir2.astype(np.float32) / 10000.0

    blue = np.clip(blue, 0, 1)

    green = np.clip(green, 0, 1)

    red = np.clip(red, 0, 1)

    nir = np.clip(nir, 0, 1)

    swir1 = np.clip(swir1, 0, 1)

    swir2 = np.clip(swir2, 0, 1)

    eps = 1e-6

    ndvi = (nir - red) / (nir + red + eps)

    ndwi = (green - nir) / (green + nir + eps)

    # Normalized Difference Snow Index — standard formula.
    # Snow/ice: strongly positive (commonly > 0.4).
    # Vegetation, built-up, bare soil: near zero or negative.
    # Added specifically to separate snow from spectrally
    # similar bright surfaces (see module docstring).

    ndsi = (green - swir1) / (green + swir1 + eps)

    brightness = (blue + green + red + nir) / 4.0

    spectral_std = np.std(

        np.stack([blue, green, red], axis=-1),

        axis=-1,

    )

    blue_red_ratio = blue / (red + eps)

    green_nir_ratio = green / (nir + eps)

    red_texture_std = _local_std(red)

    nir_texture_std = _local_std(nir)

    ndvi_texture_std = _local_std(ndvi)

    features = np.stack(

        [

            blue,

            green,

            red,

            nir,

            swir1,

            swir2,

            ndvi,

            ndwi,

            ndsi,

            brightness,

            spectral_std,

            blue_red_ratio,

            green_nir_ratio,

            red_texture_std,

            nir_texture_std,

            ndvi_texture_std,

        ],

        axis=-1,

    )

    return features