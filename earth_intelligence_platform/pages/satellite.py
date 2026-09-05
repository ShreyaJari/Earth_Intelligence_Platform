"""
Earth Intelligence Platform

Satellite Page

Runs the Satellite Engine and displays the results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from datetime import date, timedelta

import numpy as np
import plotly.express as px
import streamlit as st

from earth_intelligence_platform.engines.satellite_engine.main import (
    run_satellite_engine,
)

from earth_intelligence_platform.engines.satellite_engine.search_scenes import (
    count_available_scenes,
)

# ============================================================
# Helpers
# ============================================================


def display_zoomable_image(image_array, caption, max_dimension=1200):
    """
    Display a numpy image array with interactive zoom/pan.

    Downsamples large arrays before sending to Plotly — full
    Sentinel-2 resolution (thousands of pixels per side) would
    exceed Streamlit's websocket message size limit. Zoom/pan
    still works normally on the downsampled version.
    """

    height, width = image_array.shape[:2]

    scale = max(1, int(max(height, width) / max_dimension))

    if scale > 1:

        image_array = image_array[::scale, ::scale]

    fig = px.imshow(image_array)

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        title=caption,
        dragmode="pan",
        height=800,
    )

    fig.update_xaxes(visible=False)

    fig.update_yaxes(visible=False)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": True},
    )


# ============================================================
# Page
# ============================================================

st.title("🛰️ Satellite Engine")

st.caption(
    "Search, rank and download the optimal satellite imagery "
    "for the selected Area of Interest."
)

# ============================================================
# Dependency Check
# ============================================================

if st.session_state.get("aoi") is None:

    st.warning("Please complete the Home page first.")

    st.stop()

# ============================================================
# Parameters
# ============================================================

st.subheader("Run Parameters")

col1, col2 = st.columns(2)

with col1:

    start_date = st.date_input(
        "Start Date",
        value=None,
        min_value=date(2015, 6, 23),  # Sentinel-2A launch
        max_value=date.today(),
    )

with col2:

    max_cloud_cover = st.slider(
        "Maximum Cloud Cover (%)",
        min_value=0,
        max_value=100,
        value=40,
    )

    st.caption(
        "Filters candidate tiles by their whole-scene cloud "
        "cover. Lower values are stricter and may find no "
        "matches during persistently cloudy periods (e.g. "
        "monsoon season) — if you get no results, try raising "
        "this threshold."
    )

# ============================================================
# Availability Preview
# ============================================================

with st.spinner("Checking imagery availability..."):

    preview_count = count_available_scenes(
        aoi=st.session_state["aoi"],
        start_date=(str(start_date) if start_date else None),
        max_cloud_cover=max_cloud_cover,
    )

if preview_count == 0:

    st.warning(
        f"⚠️ No scenes currently match a {max_cloud_cover}% "
        "cloud cover threshold for this date range. This is "
        "often caused by persistently cloudy conditions rather "
        "than a lack of imagery — try raising the cloud cover "
        "threshold above, or picking an earlier start date."
    )

else:

    st.caption(f"✅ Matching imagery found for this configuration.")

st.caption(
    "⏱️ Running this engine may take 2-3 minutes while it "
    "searches, ranks, and downloads satellite imagery for "
    "your Area of Interest."
)

st.divider()

# ============================================================
# Run Engine
# ============================================================

if st.button(
    "Run Satellite Engine",
    width="stretch",
):

    with st.spinner("Searching and downloading satellite imagery..."):

        try:

            product = run_satellite_engine(
                aoi=st.session_state["aoi"],
                collection="sentinel-2-l2a",
                start_date=(str(start_date) if start_date else None),
                end_date=None,
                max_cloud_cover=max_cloud_cover,
                resolution=10,
            )

            st.session_state["satellite"] = product

            st.session_state["pipeline_status"]["satellite"] = True

        except RuntimeError as e:

            st.error(
                f"⚠️ {e}\n\n"
                "Try raising the cloud cover threshold or picking "
                "a different date — this happens when the best "
                "available date doesn't have enough tile coverage "
                "for your Area of Interest."
            )

# ============================================================
# Display Results
# ============================================================

if st.session_state.get("satellite") is None:

    st.stop()

product = st.session_state["satellite"]

st.success("Satellite Engine completed successfully.")

st.info("➡️ Next: head to **Terrain** in the sidebar to continue.")

st.divider()

# ============================================================
# Scene Summary
# ============================================================

st.subheader("Scene Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Cloud Cover",
        f"{product.scene.cloud_cover:.2f}%",
    )

with col2:
    st.metric(
        "Provider",
        "Planetary Computer",
    )

with col3:

    st.metric(
        "Acquisition",
        product.scene.acquisition_date[:10],
    )

st.divider()

# ============================================================
# RGB Composite
# ============================================================

st.subheader("Natural Colour (RGB)")

if product.visualizations.rgb is not None:

    display_zoomable_image(
        product.visualizations.rgb,
        "Sentinel-2 RGB Composite",
    )

else:

    st.warning("RGB image not available.")

st.divider()

# ============================================================
# False Colour Composite
# ============================================================

st.subheader("False Colour Composite")

if product.visualizations.false_colour is not None:

    display_zoomable_image(
        product.visualizations.false_colour,
        "NIR / Red / Green",
    )

else:

    st.info(
        "🔒 False Colour Composite is available in the full "
        "local version. This deployment is optimized for "
        "reliability on free-tier hosting — see the README's "
        "'Demo vs. Full Local Version' section, or clone the "
        "repo to run the complete feature set."
    )

st.divider()

# ============================================================
# Quality
# ============================================================

st.subheader("Quality Assessment")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Valid Pixels",
        f"{product.quality.valid_pixel_percentage:.2f}%",
    )

with col2:

    st.metric(
        "NoData",
        f"{product.quality.nodata_percentage:.2f}%",
    )

with col3:

    st.metric(
        "Scene Cloud (Metadata)",
        f"{product.quality.cloud_cover:.2f}%",
    )

with col4:

    if product.quality.ml_cloud_percentage is not None:

        st.metric(
            "AOI Cloud % (ML, measured)",
            f"{product.quality.ml_cloud_percentage:.2f}%",
        )

    else:

        st.metric(
            "AOI Cloud % (ML, measured)",
            "N/A",
        )

st.caption(
    '"Scene Cloud (Metadata)" is Sentinel-2\'s own whole-tile '
    'cloud estimate from STAC metadata. "AOI Cloud % (ML, '
    'measured)" is computed by a trained classifier directly '
    "over your clipped AOI's pixels."
)

st.divider()

# ============================================================
# Cloud Mask
# ============================================================

st.subheader("Cloud Mask (ML-Predicted)")

if product.cloud_mask is not None:

    display_zoomable_image(
        product.cloud_mask.values,
        "Cloud Probability (0 = Clear, 1 = Cloud)",
    )

else:

    st.info(
        "🔒 ML Cloud Detection is available in the full local "
        "version. See the README's 'Demo vs. Full Local "
        "Version' section for details."
    )

st.divider()

# ============================================================
# Metadata
# ============================================================

st.subheader("Metadata")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Bands Loaded",
        len(product.metadata.bands),
    )

with col2:

    st.metric(
        "Download Time",
        f"{product.metadata.download_time:.2f} s",
    )

with st.expander("Loaded Bands"):

    st.write(product.metadata.bands)