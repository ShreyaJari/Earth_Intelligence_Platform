import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import streamlit as st
from components.maps import display_map
from utils.config import VERSION

from earth_intelligence_platform.engines.data_discovery import run_data_discovery_engine
from earth_intelligence_platform.engines.location_engine.main import run_location_engine

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🌍 Earth Intelligence Platform")

st.caption(
    "An integrated GeoAI platform for Earth Observation and Environmental Intelligence."
)

st.divider()

# ---------------------------------------------------------
# Area of Interest
# ---------------------------------------------------------

st.header("📍 Area of Interest")

col1, col2 = st.columns(2)

with col1:

    city = st.text_input(
        "City",
        value="Mumbai",
    )

with col2:

    country = st.text_input(
        "Country",
        value="India",
    )

run = st.button(
    "Analyze Area",
    use_container_width=True,
)

# ---------------------------------------------------------
# Run Engines
# ---------------------------------------------------------

if run:

    with st.spinner("Generating Area of Interest..."):

        aoi = run_location_engine(
            location={
                "input_type": "city",
                "city": city,
                "country": country,
            }
        )

        st.session_state["aoi"] = aoi

        st.session_state["pipeline_status"]["location"] = True

    with st.spinner("Discovering datasets..."):

        catalog = run_data_discovery_engine(aoi)

        st.session_state["catalog"] = catalog

        st.session_state["pipeline_status"]["discovery"] = True

# ---------------------------------------------------------
# Display AOI
# ---------------------------------------------------------

if st.session_state["aoi"] is not None:

    aoi = st.session_state["aoi"]

    st.success("Location Engine completed successfully.")

    left, right = st.columns([2, 1])

    with left:

        display_map(aoi)

    with right:

        st.subheader("AOI Summary")

        st.write(f"**Location:** {aoi['identity']['name']}")

        st.write(f"**Country:** {aoi['identity']['country']}")

        st.write(f"**Geometry:** {aoi['geometry']['geometry_type']}")

        st.write(f"**CRS:** {aoi['geometry']['crs']}")

        st.write(f"**Area:** {aoi['spatial']['area_sq_km']:.2f} km²")

        st.write(f"**Perimeter:** {aoi['spatial']['perimeter_km']:.2f} km")

# ---------------------------------------------------------
# Dataset Summary
# ---------------------------------------------------------

if st.session_state["catalog"] is not None:

    catalog = st.session_state["catalog"]

    st.divider()

    st.header("🗂 Data Discovery")

    st.success("Data Discovery Engine completed successfully.")

    datasets = catalog["datasets"]

    applicable_count = sum(1 for dataset in datasets if dataset.get("applicable"))

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Datasets Discovered",
            len(datasets),
        )

    with col2:

        st.metric(
            "Applicable to this AOI",
            applicable_count,
        )

    dataset_table = pd.DataFrame(
        [
            {
                "Dataset": dataset["name"],
                "Category": dataset["category"],
                "Provider": dataset.get("provider", "N/A"),
                "Applicable": "✅" if dataset.get("applicable") else "⬜",
                "Priority": dataset.get("priority", "N/A"),
            }
            for dataset in datasets
        ]
    )

    st.dataframe(
        dataset_table,
        use_container_width=True,
    )

    with st.expander("Advanced Information"):

        st.json(catalog)

# ---------------------------------------------------------
# Workflow Status
# ---------------------------------------------------------

st.divider()

st.header("Workflow")

status = st.session_state["pipeline_status"]

workflow_steps = [
    ("location", "Location"),
    ("discovery", "Discovery"),
    ("satellite", "Satellite"),
    ("terrain", "Terrain"),
    ("landcover", "Land Cover"),
    ("weather", "Weather"),
    ("risk", "Risk"),
    ("intelligence", "Intelligence"),
]

row1 = st.columns(4)

row2 = st.columns(4)

columns = row1 + row2

for column, (key, label) in zip(columns, workflow_steps):

    with column:

        st.write(label)

        st.write("✅" if status.get(key) else "⬜")

st.caption(f"Platform Version {VERSION}")
