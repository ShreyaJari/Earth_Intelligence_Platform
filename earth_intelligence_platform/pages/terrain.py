"""
Earth Intelligence Platform

Terrain Page

Runs the Terrain Engine and displays the results.
"""

import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import streamlit as st

from earth_intelligence_platform.engines.terrain_engine.main import run_terrain_engine

# ============================================================
# Chart Helpers
# ============================================================


def build_histogram(values, title, x_label):
    """
    Build a histogram of raster pixel values.
    """

    fig = px.histogram(
        x=values,
        nbins=40,
        title=title,
    )

    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title="Pixel Count",
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        showlegend=False,
    )

    return fig


def build_aspect_rose(values):
    """
    Build a polar rose diagram of aspect (slope direction).
    """

    bin_edges = np.arange(0, 361, 22.5)

    counts, _ = np.histogram(values, bins=bin_edges)

    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    fig = px.bar_polar(
        r=counts,
        theta=bin_centers,
        title="Aspect Distribution (Slope Direction)",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=400,
    )

    return fig


UNITS = {
    "elevation": "meters",
    "slope": "degrees",
    "hillshade": "0-255",
}

# ============================================================
# Page
# ============================================================

st.title("🏔️ Terrain")

st.caption(
    "Digital Elevation Model and derived terrain products "
    "for the selected Area of Interest."
)

# ============================================================
# Dependency Check
# ============================================================

if st.session_state.get("aoi") is None:

    st.warning("Please complete the Home page first.")

    st.stop()

if st.session_state.get("catalog") is None:

    st.warning("Please run Data Discovery on the Home page first.")

    st.stop()

st.divider()

# ============================================================
# Run Engine
# ============================================================

if st.button(
    "Run Terrain Engine",
    width="stretch",
):

    with st.spinner("Downloading and processing terrain data..."):

        product = run_terrain_engine(
            aoi=st.session_state["aoi"],
            catalog=st.session_state["catalog"],
        )

        st.session_state["terrain"] = product

        st.session_state["pipeline_status"]["terrain"] = product["success"]

# ============================================================
# Display Results
# ============================================================

if st.session_state.get("terrain") is None:

    st.stop()

product = st.session_state["terrain"]

if not product["success"]:

    st.error("Terrain Engine failed.")

    st.write(product["errors"])

    st.stop()

st.success("Terrain Engine completed successfully.")

st.divider()

# ============================================================
# Dataset Summary
# ============================================================

st.subheader("Dataset")

dataset = product["dataset"]

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Dataset",
        dataset["name"],
    )

with col2:

    st.metric(
        "Provider",
        dataset["provider"],
    )

with col3:

    st.metric(
        "Category",
        dataset["category"],
    )

st.divider()

# ============================================================
# Terrain Products + Statistics
# ============================================================

st.subheader("Terrain Products")

products = product["products"]

statistics = product["statistics"]

aoi_geometry = st.session_state["aoi"]["geometry"]["geometry"]

product_labels = {
    "elevation": "Elevation",
    "slope": "Slope",
    "aspect": "Aspect",
    "hillshade": "Hillshade",
}

available = [name for name in product_labels if name in products]

if available:

    tabs = st.tabs([product_labels[name] for name in available])

    for tab, name in zip(tabs, available):

        with tab:

            layer = products[name]

            fig, ax = plt.subplots()

            layer.plot.imshow(
                ax=ax,
                cmap=(
                    "gray"
                    if name == "hillshade"
                    else "terrain" if name == "elevation" else "viridis"
                ),
            )

            if aoi_geometry.geom_type == "Polygon":

                boundary_polygons = [aoi_geometry]

            elif aoi_geometry.geom_type == "MultiPolygon":

                boundary_polygons = list(aoi_geometry.geoms)

            else:

                boundary_polygons = []

            for polygon in boundary_polygons:

                x, y = polygon.exterior.xy

                ax.plot(
                    x,
                    y,
                    color="red",
                    linewidth=1.5,
                )

                for interior in polygon.interiors:

                    xi, yi = interior.xy

                    ax.plot(
                        xi,
                        yi,
                        color="red",
                        linewidth=1.0,
                        linestyle="--",
                    )

            ax.set_title(product_labels[name])

            st.pyplot(fig)

            plt.close(fig)

            st.divider()

            values = layer.values.flatten()

            values = values[np.isfinite(values)]

            if name == "aspect":

                chart = build_aspect_rose(values)

            else:

                chart = build_histogram(
                    values,
                    f"{product_labels[name]} Distribution",
                    UNITS.get(name, ""),
                )

            st.plotly_chart(
                chart,
                use_container_width=True,
            )

            stats = statistics.get(name)

            if stats:

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Min",
                        (
                            f"{stats['minimum']:.2f}"
                            if stats["minimum"] is not None
                            else "N/A"
                        ),
                    )

                with col2:

                    st.metric(
                        "Max",
                        (
                            f"{stats['maximum']:.2f}"
                            if stats["maximum"] is not None
                            else "N/A"
                        ),
                    )

                with col3:

                    st.metric(
                        "Mean",
                        f"{stats['mean']:.2f}" if stats["mean"] is not None else "N/A",
                    )

                with col4:

                    st.metric(
                        "Std Dev",
                        (
                            f"{stats['standard_deviation']:.2f}"
                            if stats["standard_deviation"] is not None
                            else "N/A"
                        ),
                    )

else:

    st.warning("No terrain products available.")

st.divider()

# ============================================================
# Dataset Metadata
# ============================================================

st.subheader("Dataset Metadata")

metadata = product["metadata"]

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Width",
        metadata.get("width", "N/A"),
    )

with col2:

    st.metric(
        "Height",
        metadata.get("height", "N/A"),
    )

with col3:

    st.metric(
        "CRS",
        metadata.get("crs", "N/A"),
    )

st.json(metadata.get("resolution", {}))

st.divider()

# ============================================================
# Processing
# ============================================================

st.subheader("Processing")

processing = product["processing"]

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Download Time",
        f"{processing.get('download_time_seconds', 0):.2f} s",
    )

with col2:

    st.metric(
        "Processing Time",
        f"{processing.get('processing_time_seconds', 0):.2f} s",
    )

with col3:

    st.metric(
        "Statistics Time",
        f"{processing.get('statistics_time_seconds', 0):.2f} s",
    )

st.divider()

# ============================================================
# Advanced
# ============================================================

with st.expander("Advanced Information"):

    st.write("### Dataset")

    st.write(product["dataset"])

    st.write("### Metadata")

    st.write(product["metadata"])

    st.write("### Statistics")

    st.write(product["statistics"])

    st.write("### Processing")

    st.write(product["processing"])

st.divider()

# ============================================================
# Developer Information
# ============================================================

with st.expander("Developer Debug"):

    st.write("Terrain Product Keys")

    st.write(list(product.keys()))

    st.write()

    st.write("Raw DEM")

    st.write(product["dem"])

    st.write()

    st.write("Terrain Products (raw)")

    st.write(product["products"])
