"""
Earth Intelligence Platform

Earth Intelligence Page

Runs the Earth Intelligence Engine — the final synthesis
layer combining Location, Data Discovery, Satellite, Terrain,
Land Cover, Weather, and Risk outputs — and displays the
results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import plotly.graph_objects as go
import streamlit as st
from components.cards import metric_card
from components.maps import display_map

from earth_intelligence_platform.engines.earth_intelligence_engine import (
    run_earth_intelligence_engine,
)

# ============================================================
# Chart Helpers
# ============================================================

CATEGORY_COLORS = {
    "Low": "#2ECC71",
    "Moderate": "#F1C40F",
    "High": "#E67E22",
    "Very High": "#E74C3C",
}


def build_score_gauge(score, title, bar_color="#2D6A4F"):
    """
    Generic 0-100 gauge indicator.
    """

    fig = go.Figure(

        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title},
            number={"suffix": " / 100"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": bar_color},
                "steps": [
                    {"range": [0, 25], "color": "#fdedec"},
                    {"range": [25, 50], "color": "#fdf2e9"},
                    {"range": [50, 75], "color": "#fef9e7"},
                    {"range": [75, 100], "color": "#eafaf1"},
                ],
            },
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=0),
        height=280,
    )

    return fig


def build_component_radar(components, labels):
    """
    Radar chart of the five weighted components making up
    the Earth Intelligence Score.
    """

    categories = [labels[key] for key in components]

    values = list(components.values())

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            line=dict(color="#2D6A4F"),
            fillcolor="rgba(45, 106, 79, 0.25)",
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
            )
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=420,
    )

    return fig


def build_landcover_donut(vegetation, built_up):
    """
    Donut chart of vegetation vs built-up vs other land cover.
    """

    other = max(0.0, 100.0 - vegetation - built_up)

    fig = go.Figure(
        go.Pie(
            labels=["Vegetation", "Built-up", "Other"],
            values=[vegetation, built_up, other],
            hole=0.5,
            marker=dict(
                colors=["#40916C", "#E67E22", "#BDC3C7"],
            ),
            textinfo="label+percent",
        )
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=320,
        showlegend=False,
    )

    return fig


def build_hazard_bar_chart(risk_breakdown, hazard_labels):
    """
    Horizontal bar chart of hazard scores from the risk
    breakdown, colored by category.
    """

    rows = [
        {
            "Hazard": hazard_labels.get(hazard, hazard),
            "Score": info["score"],
            "Category": info["category"],
        }
        for hazard, info in risk_breakdown.items()
    ]

    import pandas as pd
    import plotly.express as px

    chart_data = pd.DataFrame(rows).sort_values(
        "Score",
        ascending=True,
    )

    fig = px.bar(
        chart_data,
        x="Score",
        y="Hazard",
        orientation="h",
        color="Category",
        color_discrete_map=CATEGORY_COLORS,
        text="Score",
        range_x=[0, 100],
    )

    fig.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
    )

    fig.update_layout(
        margin=dict(l=0, r=20, t=20, b=0),
        height=280,
        xaxis_title="Risk Score",
        yaxis_title=None,
        legend_title_text="Category",
    )

    return fig


HAZARD_LABELS = {
    "flood": "Flood",
    "landslide": "Landslide",
    "wildfire": "Wildfire",
    "urban_heat": "Urban Heat",
    "wind": "Wind Exposure",
}

COMPONENT_LABELS = {
    "environmental_quality": "Environmental Quality",
    "terrain_stability": "Terrain Stability",
    "climate_conditions": "Climate Conditions",
    "hazard_resilience": "Hazard Resilience",
    "sustainability": "Sustainability",
}

# ============================================================
# Page
# ============================================================

st.title("🌍 Earth Intelligence")

st.caption(
    "Integrated environmental intelligence for the selected "
    "Area of Interest, synthesized from every engine in the "
    "platform."
)

# ============================================================
# Dependency Check
# ============================================================

required_keys = {
    "aoi": "Location Engine",
    "catalog": "Data Discovery Engine",
    "satellite": "Satellite Engine",
    "terrain": "Terrain Engine",
    "landcover": "Land Cover Engine",
    "weather": "Weather Engine",
    "risk": "Risk Engine",
}

missing = [
    label for key, label in required_keys.items() if st.session_state.get(key) is None
]

if missing:

    st.warning("Please run the following engine(s) first: " + ", ".join(missing))

    st.stop()

location_product = st.session_state["aoi"]

discovery_product = st.session_state["catalog"]

satellite_product = st.session_state["satellite"]

terrain_product = st.session_state["terrain"]

landcover_product = st.session_state["landcover"]

weather_product = st.session_state["weather"]

risk_product = st.session_state["risk"]

failed = []

if not all(key in location_product for key in ["identity", "geometry", "spatial"]):

    failed.append("Location Engine")

if "datasets" not in discovery_product or len(discovery_product["datasets"]) == 0:

    failed.append("Data Discovery Engine")

if satellite_product.scene is None:

    failed.append("Satellite Engine")

if not terrain_product["success"]:

    failed.append("Terrain Engine")

if not landcover_product["success"]:

    failed.append("Land Cover Engine")

if not weather_product["success"]:

    failed.append("Weather Engine")

if not risk_product["success"]:

    failed.append("Risk Engine")

if failed:

    st.warning(
        "The following engine(s) did not complete "
        "successfully, please re-run them: " + ", ".join(failed)
    )

    st.stop()

st.divider()

# ============================================================
# Run Engine
# ============================================================

if st.button(
    "Run Earth Intelligence Engine",
    width="stretch",
):

    with st.spinner("Synthesizing Earth Intelligence..."):

        product = run_earth_intelligence_engine(
            location_product=location_product,
            discovery_product=discovery_product,
            satellite_product=satellite_product,
            terrain_product=terrain_product,
            landcover_product=landcover_product,
            weather_product=weather_product,
            risk_product=risk_product,
        )

        st.session_state["intelligence"] = product

        st.session_state["pipeline_status"]["intelligence"] = product["success"]

# ============================================================
# Display Results
# ============================================================

if st.session_state.get("intelligence") is None:

    st.stop()

product = st.session_state["intelligence"]

if not product["success"]:

    st.error("Earth Intelligence Engine failed.")

    st.write(product["errors"])

    st.stop()

st.success("Earth Intelligence Engine completed successfully.")

st.divider()

intelligence = product["intelligence"]

# ============================================================
# Location
# ============================================================

st.subheader("Location")

left, right = st.columns([2, 1])

with left:

    display_map(location_product)

with right:

    st.write(f"**Location:** {location_product['identity']['name']}")

    st.write(f"**Country:** {location_product['identity']['country']}")

    st.write(f"**Area:** {location_product['spatial']['area_sq_km']:.2f} km²")

st.divider()

# ============================================================
# Earth Intelligence Score
# ============================================================

st.subheader("Earth Intelligence Score")

score_data = intelligence["earth_intelligence_score"]

components = score_data["components"]

col1, col2 = st.columns([1, 1])

with col1:

    st.plotly_chart(
        build_score_gauge(
            score_data["score"],
            "Overall Score",
        ),
        use_container_width=True,
    )

with col2:

    st.plotly_chart(
        build_component_radar(
            components,
            COMPONENT_LABELS,
        ),
        use_container_width=True,
    )

component_cols = st.columns(len(components))

for column, (key, value) in zip(
    component_cols,
    components.items(),
):

    with column:

        metric_card(
            COMPONENT_LABELS.get(key, key),
            f"{value:.1f}",
        )

st.divider()

# ============================================================
# Environmental Summary
# ============================================================

st.subheader("Environmental Summary")

environmental = intelligence["environmental_summary"]

col1, col2 = st.columns([1, 1])

with col1:

    st.write("**Land Cover Composition**")

    st.plotly_chart(
        build_landcover_donut(
            environmental["landcover"]["vegetation_percentage"],
            environmental["landcover"]["built_up_percentage"],
        ),
        use_container_width=True,
    )

with col2:

    st.write("**Terrain**")

    metric_card(
        "Mean Elevation",
        f"{environmental['terrain']['mean_elevation']:.1f} m",
    )

    metric_card(
        "Mean Slope",
        f"{environmental['terrain']['mean_slope']:.1f}°",
    )

    st.write("**Weather**")

    metric_card(
        "Mean Temperature",
        f"{environmental['weather']['mean_temperature']:.1f} °C",
    )

    metric_card(
        "Total Precipitation",
        f"{environmental['weather']['total_precipitation']:.1f} mm",
    )

st.divider()

# ============================================================
# Hazard Summary
# ============================================================

st.subheader("Hazard Summary")

hazard = intelligence["hazard_summary"]

highest = hazard["highest_risk"]

col1, col2 = st.columns([1, 1])

with col1:

    st.plotly_chart(
        build_score_gauge(
            hazard["overall_risk"]["score"],
            "Overall Risk Score",
            bar_color=CATEGORY_COLORS.get(
                highest["category"],
                "#E67E22",
            ),
        ),
        use_container_width=True,
    )

with col2:

    st.plotly_chart(
        build_hazard_bar_chart(
            hazard["risk_breakdown"],
            HAZARD_LABELS,
        ),
        use_container_width=True,
    )

col1, col2 = st.columns(2)

with col1:

    metric_card(
        "Highest Risk",
        HAZARD_LABELS.get(highest["hazard"], highest["hazard"]),
    )

with col2:

    metric_card(
        "Highest Risk Score",
        f"{highest['score']:.1f}",
    )

st.divider()

# ============================================================
# Sustainability
# ============================================================

st.subheader("Sustainability")

sustainability = intelligence["sustainability"]

st.plotly_chart(
    build_score_gauge(
        sustainability["score"],
        "Sustainability Score",
        bar_color="#40916C",
    ),
    use_container_width=True,
)

if sustainability["summary"]:

    st.write(sustainability["summary"])

st.divider()

# ============================================================
# Key Insights
# ============================================================

st.subheader("Key Insights")

insights = intelligence["key_insights"]

if insights:

    for insight in insights:

        st.info(insight)

else:

    st.write("No key insights identified.")

st.divider()

# ============================================================
# Recommendations
# ============================================================

st.subheader("Recommendations")

recommendations = intelligence["recommendations"]

if recommendations:

    for recommendation in recommendations:

        st.success(recommendation)

else:

    st.write("No recommendations at this time.")

st.divider()

# ============================================================
# Explainability
# ============================================================

st.subheader("Explainability")

explainability = intelligence["explainability"]

st.write(
    f"**Drivers behind the highest risk " f"({highest['hazard'].replace('_', ' ')}):**"
)

if explainability["drivers"]:

    for driver in explainability["drivers"]:

        st.write(f"- {driver}")

else:

    st.write("No dominant drivers identified.")

st.write("**Limitations**")

for limitation in explainability["limitations"]:

    st.caption(f"• {limitation}")

st.divider()

# ============================================================
# Statistics
# ============================================================

st.subheader("Statistics")

statistics = product["statistics"]

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Earth Intelligence Score",
        f"{statistics['earth_intelligence_score']:.1f}",
    )

with col2:

    metric_card(
        "Sustainability Score",
        f"{statistics['sustainability_score']:.1f}",
    )

with col3:

    metric_card(
        "Insights / Recommendations",
        f"{statistics['number_of_insights']} / "
        f"{statistics['number_of_recommendations']}",
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

col1, col2 = st.columns(2)

with col1:

    metric_card(
        "Processing Time",
        f"{processing.get('processing_time_seconds', 0):.2f} s",
    )

with col2:

    metric_card(
        "Statistics Time",
        f"{processing.get('statistics_time_seconds', 0):.2f} s",
    )

st.divider()

# ============================================================
# Advanced
# ============================================================

with st.expander("Advanced Information"):

    st.write("### Intelligence")

    st.write(product["intelligence"])

    st.write("### Statistics")

    st.write(product["statistics"])

    st.write("### Processing")

    st.write(product["processing"])

st.divider()

# ============================================================
# Developer Information
# ============================================================

with st.expander("Developer Debug"):

    st.write("Earth Intelligence Product Keys")

    st.write(list(product.keys()))

    st.write()

    st.write("Full Earth Intelligence Product")

    st.write(product)
