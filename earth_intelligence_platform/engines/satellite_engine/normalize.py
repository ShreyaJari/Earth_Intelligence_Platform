"""
Earth Intelligence Platform
Satellite Engine

Normalize

Common normalization utilities for satellite visualization.
"""

import numpy as np

# ============================================================
# Percentile Stretch
# ============================================================


def percentile_stretch(
    image,
    lower=2,
    upper=98,
):
    """
    Normalize an image using percentile stretching.

    Parameters
    ----------
    image : ndarray

    lower : int

    upper : int

    Returns
    -------
    ndarray
    """

    image = image.astype(np.float32)

    valid = np.isfinite(image)

    if valid.sum() == 0:

        return np.zeros_like(
            image,
            dtype=np.uint8,
        )

    p_low = np.nanpercentile(
        image,
        lower,
    )

    p_high = np.nanpercentile(
        image,
        upper,
    )

    if p_high <= p_low:

        return np.zeros_like(
            image,
            dtype=np.uint8,
        )

    image = np.clip(
        image,
        p_low,
        p_high,
    )

    image = (image - p_low) / (p_high - p_low)

    image = np.clip(
        image,
        0,
        1,
    )

    image = (image * 255).astype(np.uint8)

    return image


# ============================================================
# Stack RGB
# ============================================================


def stack_rgb(
    red,
    green,
    blue,
):
    """
    Stack three normalized bands.
    """

    return np.dstack(
        [
            red,
            green,
            blue,
        ]
    )


# ============================================================
# Replace NaNs
# ============================================================


def replace_nan(
    image,
    value=0,
):
    """
    Replace NaN values.
    """

    return np.nan_to_num(
        image,
        nan=value,
    )
