"""
Earth Intelligence Platform

Satellite Page

Runs the Satellite Engine and displays the results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from datetime import date

import numpy as np
import plotly.express as px
import streamlit as st

from earth_intelligence_platform.engines.satellite_engine.main import (
    run_satellite_engine,
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
        "cover, not cloud cover specifically over your AOI. "
        "A tile can be excluded here even if it's clear "
        "directly over your area of interest."
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

# ============================================================
# Display Results
# ============================================================

if st.session_state.get("satellite") is None:

    st.stop()

product = st.session_state["satellite"]

st.success("Satellite Engine completed successfully.")

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
        "Collection",
        product.scene.collection,
    )

with col3:

    st.metric(
        "Provider",
        product.scene.provider,
    )

with col4:

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

    st.warning("False colour image not available.")

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

    st.metric(
        "AOI Cloud % (ML, measured)",
        f"{product.quality.ml_cloud_percentage:.2f}%",
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

    st.warning("Cloud mask not available.")

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

st.divider()

# ============================================================
# Spatial Grid
# ============================================================

st.subheader("Spatial Grid")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Width",
        product.grid.width,
    )

with col2:

    st.metric(
        "Height",
        product.grid.height,
    )

with col3:

    st.metric(
        "Resolution",
        f"{product.grid.resolution} m",
    )

st.json(product.grid.bounds)

st.divider()

# ============================================================
# Advanced
# ============================================================

with st.expander("Advanced Information"):

    st.write("### Request")

    st.write(product.request)

    st.write("### Scene")

    st.write(product.scene)

    st.write("### Grid")

    st.write(product.grid)

    st.write("### Metadata")

    st.write(product.metadata)

    st.write("### Quality")

    st.write(product.quality)

st.divider()

# ============================================================
# Developer Information
# ============================================================

with st.expander("Developer Debug"):

    st.write("Satellite Product")

    st.write(product)

    st.write()

    st.write("Raw Imagery (summary — full dataset too large to render)")

    st.write(
        {
            "dimensions": dict(product.imagery.raw.sizes),
            "data_variables": list(product.imagery.raw.data_vars),
            "crs": str(product.imagery.raw.rio.crs),
        }
    )

    st.write()

    st.write("Prepared AOI Imagery (summary — full dataset too large to render)")

    st.write(
        {
            "dimensions": dict(product.imagery.aoi.sizes),
            "data_variables": list(product.imagery.aoi.data_vars),
            "crs": str(product.imagery.aoi.rio.crs),
        }
    )