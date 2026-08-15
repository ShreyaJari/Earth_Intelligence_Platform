"""
Earth Intelligence Platform

Land Cover Page

Runs the Land Cover Engine and displays the results.
"""

import pandas as pd
import streamlit as st
import xarray as xr
import plotly.express as px

from components.cards import metric_card
from components.raster import display_raster, display_metadata

from earth_intelligence_platform.engines.land_cover_engine.main import (
    run_landcover_engine,
)

from earth_intelligence_platform.engines.land_cover_engine.legend import (
    LAND_COVER_LEGEND,
)

# ============================================================
# Page
# ============================================================

st.title("🌱 Land Cover")

st.caption(
    "Land cover classification and statistics for the "
    "selected Area of Interest."
)

# ============================================================
# Dependency Check
# ============================================================

if st.session_state.get("aoi") is None:

    st.warning(
        "Please complete the Home page first."
    )

    st.stop()

if st.session_state.get("catalog") is None:

    st.warning(
        "Please run Data Discovery on the Home page first."
    )

    st.stop()

st.divider()

# ============================================================
# Run Engine
# ============================================================

if st.button(
    "Run Land Cover Engine",
    width="stretch",
):

    with st.spinner(
        "Downloading and classifying land cover..."
    ):

        product = run_landcover_engine(
            aoi=st.session_state["aoi"],
            catalog=st.session_state["catalog"],
            satellite_product=st.session_state.get("satellite"),
        )

        st.session_state["landcover"] = product

        st.session_state["pipeline_status"]["landcover"] = (
            product["success"]
        )

if st.session_state.get("satellite") is None:

    st.info(
        "Run the Satellite Engine first to also generate a "
        "date-specific ML land cover classification alongside "
        "the standard ESA WorldCover result."
    )

# ============================================================
# Display Results
# ============================================================

if st.session_state.get("landcover") is None:

    st.stop()

product = st.session_state["landcover"]

if not product["success"]:

    st.error("Land Cover Engine failed.")

    st.write(product["errors"])

    st.stop()

st.success(
    "Land Cover Engine completed successfully."
)

st.divider()

# ============================================================
# Dataset
# ============================================================

st.subheader("Dataset")

dataset = product["dataset"]

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Dataset",
        dataset["name"],
    )

with col2:

    metric_card(
        "Category",
        dataset["category"],
    )

with col3:

    metric_card(
        "Provider",
        dataset.get("provider", "N/A"),
    )

st.divider()

# ============================================================
# Classification Map
# ============================================================

st.subheader("Classification Map")

classification = product["products"]["classification"]

visualization = product["products"]["visualization"]

raster_dataset = xr.Dataset(
    {
        "classification": classification,
        "visualization": visualization,
    }
)

aoi_geometry = st.session_state["aoi"]["geometry"]["geometry"]

display_raster(
    raster_dataset,
    title="Land Cover",
    aoi_geometry=aoi_geometry,
    categorical_legend=LAND_COVER_LEGEND,
)

st.divider()

# ============================================================
# Legend
# ============================================================

st.subheader("Legend")

legend = product["products"]["legend"]

name_to_color = {
    info["name"]: info["color"]
    for info in legend.values()
}

legend_cols = st.columns(3)

for index, (class_id, info) in enumerate(legend.items()):

    with legend_cols[index % 3]:

        st.markdown(
            f"<div style='display:flex;align-items:center;"
            f"margin-bottom:6px;'>"
            f"<div style='width:16px;height:16px;"
            f"background-color:{info['color']};"
            f"margin-right:8px;border:1px solid #999;'></div>"
            f"{info['name']}"
            f"</div>",
            unsafe_allow_html=True,
        )

st.divider()

# ============================================================
# Statistics
# ============================================================

st.subheader("Statistics")

statistics = product["statistics"]

dominant_class = statistics["dominant_class"]

dominant_percentage = statistics["percentage_per_class"].get(
    dominant_class,
    None,
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    metric_card(
        "Classes Present",
        statistics["number_of_classes"],
    )

with col2:

    metric_card(
        "Dominant Class",
        dominant_class or "N/A",
    )

with col3:

    metric_card(
        "Dominant Coverage",
        f"{dominant_percentage:.1f}%"
        if dominant_percentage is not None
        else "N/A",
    )

with col4:

    metric_card(
        "Total Area",
        f"{statistics['total_area_km2']:.2f} km²",
    )

class_rows = [
    {
        "Class": class_name,
        "Area (km²)": area,
        "Percentage (%)": statistics["percentage_per_class"].get(
            class_name,
            0.0,
        ),
        "Color": name_to_color.get(class_name, "N/A"),
    }
    for class_name, area in statistics["area_per_class"].items()
]

class_table = pd.DataFrame(class_rows).sort_values(
    "Percentage (%)",
    ascending=True,
).reset_index(drop=True)

fig = px.bar(
    class_table,
    x="Percentage (%)",
    y="Class",
    orientation="h",
    color="Class",
    color_discrete_map=name_to_color,
    text="Percentage (%)",
    hover_data={"Area (km²)": ":.2f"},
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
)

fig.update_layout(
    showlegend=False,
    margin=dict(l=0, r=20, t=20, b=0),
    height=max(300, 40 * len(class_table)),
    xaxis_title="Percentage of AOI (%)",
    yaxis_title=None,
)

st.plotly_chart(
    fig,
    width="stretch",
)

with st.expander("Full Statistics Table"):

    st.dataframe(
        class_table.sort_values(
            "Percentage (%)",
            ascending=False,
        ).reset_index(drop=True),
        width="stretch",
    )

st.divider()

# ============================================================
# ML Land Cover (Date-Specific)
# ============================================================

if product["products"].get("ml_classification") is not None:

    st.subheader("ML Land Cover (Date-Specific)")

    ml_metadata = product.get("ml_metadata", {})

    st.caption(
        f"Method: {ml_metadata.get('method', 'N/A')} · "
        f"Labels: {ml_metadata.get('label_source', 'N/A')} · "
        f"{ml_metadata.get('resolution_note', '')}"
    )

    if ml_metadata.get("known_limitations"):

        st.warning(ml_metadata["known_limitations"])

    ml_classification = product["products"]["ml_classification"]

    ml_dataset = xr.Dataset(
        {"ml_classification": ml_classification}
    )

    display_raster(
        ml_dataset,
        title="ML Land Cover",
        aoi_geometry=aoi_geometry,
        categorical_legend=LAND_COVER_LEGEND,
    )

    ml_statistics = product.get("ml_statistics")

    if ml_statistics:

        st.write("**ML Classification Statistics**")

        ml_class_rows = [
            {
                "Class": class_name,
                "Percentage (%)": ml_statistics["percentage_per_class"].get(
                    class_name,
                    0.0,
                ),
                "Color": name_to_color.get(class_name, "#999999"),
            }
            for class_name in ml_statistics["area_per_class"]
        ]

        ml_class_table = pd.DataFrame(ml_class_rows).sort_values(
            "Percentage (%)",
            ascending=True,
        ).reset_index(drop=True)

        ml_fig = px.bar(
            ml_class_table,
            x="Percentage (%)",
            y="Class",
            orientation="h",
            color="Class",
            color_discrete_map=name_to_color,
            text="Percentage (%)",
        )

        ml_fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
        )

        ml_fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=20, t=20, b=0),
            height=max(300, 40 * len(ml_class_table)),
            xaxis_title="Percentage of AOI (%)",
            yaxis_title=None,
        )

        st.plotly_chart(
            ml_fig,
            width="stretch",
        )

    with st.expander("ML Classification Details"):

        st.json(ml_metadata)

    st.divider()

else:

    st.info(
        "ML land cover not available — run the Satellite "
        "Engine first, then re-run Land Cover."
    )

    st.divider()

# ============================================================
# Raster Metadata
# ============================================================

display_metadata(raster_dataset)

st.divider()

# ============================================================
# Dataset Metadata
# ============================================================

st.subheader("Dataset Metadata")

metadata = product["metadata"]

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Collection",
        metadata.get("collection", "N/A"),
    )

with col2:

    metric_card(
        "Items Used",
        metadata.get("number_of_items", "N/A"),
    )

with col3:

    metric_card(
        "CRS",
        metadata.get("crs", "N/A"),
    )

st.json(
    {
        "bounds": metadata.get("bounds"),
        "resolution": metadata.get("resolution"),
    }
)

st.divider()

# ============================================================
# Processing
# ============================================================

st.subheader("Processing")

processing = product["processing"]

col1, col2 = st.columns(2)

with col1:

    metric_card(
        "Engine",
        processing["engine"],
    )

with col2:

    metric_card(
        "Created",
        processing["created"],
    )

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Download Time",
        f"{processing.get('download_time_seconds', 0):.2f} s",
    )

with col2:

    metric_card(
        "Processing Time",
        f"{processing.get('processing_time_seconds', 0):.2f} s",
    )

with col3:

    metric_card(
        "Statistics Time",
        f"{processing.get('statistics_time_seconds', 0):.2f} s",
    )

st.divider()

# ============================================================
# Advanced
# ============================================================

with st.expander(
    "Advanced Information"
):

    st.write("### Dataset")

    st.write(product["dataset"])

    st.write("### Metadata")

    st.write(product["metadata"])

    st.write("### Statistics")

    st.write(product["statistics"])

    if product.get("ml_statistics"):

        st.write("### ML Statistics")

        st.write(product["ml_statistics"])

    st.write("### Processing")

    st.write(product["processing"])

st.divider()

# ============================================================
# Developer Information
# ============================================================

with st.expander(
    "Developer Debug"
):

    st.write("Land Cover Product Keys")

    st.write(list(product.keys()))

    st.write()

    st.write("Masks (raw)")

    st.write(product["products"]["masks"])