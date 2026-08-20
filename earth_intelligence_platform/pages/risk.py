"""
Earth Intelligence Platform

Risk Page

Runs the Risk Engine (using Terrain, Land Cover, Weather, and
Satellite outputs) and displays the results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.cards import metric_card

from earth_intelligence_platform.engines.risk_engine import run_risk_engine

# ============================================================
# Shared Chart Config
# ============================================================

CATEGORY_COLORS = {
    "Low": "#2ECC71",
    "Moderate": "#F1C40F",
    "High": "#E67E22",
    "Very High": "#E74C3C",
}

HAZARD_LABELS = {
    "flood": "Flood",
    "landslide": "Landslide",
    "wildfire": "Wildfire",
    "urban_heat": "Urban Heat",
    "wind": "Wind Exposure",
}


def build_overview_bar_chart(products):
    """
    Horizontal bar chart comparing all hazard scores,
    colored by risk category.
    """

    rows = [
        {
            "Hazard": HAZARD_LABELS.get(hazard, hazard),
            "Score": risk["score"],
            "Category": risk["category"],
        }
        for hazard, risk in products.items()
    ]

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
        height=300,
        xaxis_title="Risk Score",
        yaxis_title=None,
        legend_title_text="Category",
    )

    return fig


def build_gauge_chart(score, category):
    """
    Gauge indicator for a single hazard's risk score, with
    colored bands matching the Low/Moderate/High/Very High
    thresholds used by the backend.
    """

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " / 100"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": CATEGORY_COLORS.get(category, "#888888")},
                "steps": [
                    {"range": [0, 25], "color": "#eafaf1"},
                    {"range": [25, 50], "color": "#fef9e7"},
                    {"range": [50, 75], "color": "#fdf2e9"},
                    {"range": [75, 100], "color": "#fdedec"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.8,
                    "value": score,
                },
            },
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=0),
        height=280,
    )

    return fig


def build_category_pie_chart(category_counts):
    """
    Donut chart of how many hazards fall into each risk
    category.
    """

    names = list(category_counts.keys())

    values = list(category_counts.values())

    fig = px.pie(
        names=names,
        values=values,
        color=names,
        color_discrete_map=CATEGORY_COLORS,
        hole=0.45,
    )

    fig.update_traces(
        textinfo="label+value",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=350,
        showlegend=True,
    )

    return fig


# ============================================================
# Page
# ============================================================

st.title("⚠️ Risk")

st.caption(
    "Composite environmental risk assessment for the "
    "selected Area of Interest, derived from Terrain, "
    "Land Cover, Weather, and Satellite data."
)

# ============================================================
# Dependency Check
# ============================================================

required_engines = {
    "terrain": "Terrain Engine",
    "landcover": "Land Cover Engine",
    "weather": "Weather Engine",
    "satellite": "Satellite Engine",
}

missing = [
    label
    for key, label in required_engines.items()
    if st.session_state.get(key) is None
]

if missing:

    st.warning("Please run the following engine(s) first: " + ", ".join(missing))

    st.stop()

terrain_product = st.session_state["terrain"]

landcover_product = st.session_state["landcover"]

weather_product = st.session_state["weather"]

satellite_product = st.session_state["satellite"]

failed = []

if not terrain_product["success"]:

    failed.append("Terrain Engine")

if not landcover_product["success"]:

    failed.append("Land Cover Engine")

if not weather_product["success"]:

    failed.append("Weather Engine")

if satellite_product.scene is None:

    failed.append("Satellite Engine")

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
    "Run Risk Engine",
    width="stretch",
):

    with st.spinner("Assessing environmental risk..."):

        product = run_risk_engine(
            terrain_product=terrain_product,
            landcover_product=landcover_product,
            weather_product=weather_product,
            satellite_product=satellite_product,
        )

        st.session_state["risk"] = product

        st.session_state["pipeline_status"]["risk"] = product["success"]

# ============================================================
# Display Results
# ============================================================

if st.session_state.get("risk") is None:

    st.stop()

product = st.session_state["risk"]

if not product["success"]:

    st.error("Risk Engine failed.")

    st.write(product["errors"])

    st.stop()

st.success("Risk Engine completed successfully.")

st.divider()

# ============================================================
# Overview
# ============================================================

st.subheader("Overview")

statistics = product["statistics"]

products = product["products"]

highest_risk = statistics["highest_risk"]

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Highest Risk",
        HAZARD_LABELS.get(
            highest_risk["hazard"],
            highest_risk["hazard"],
        ),
    )

with col2:

    metric_card(
        "Highest Risk Score",
        f"{highest_risk['score']:.1f}",
    )

with col3:

    metric_card(
        "Average Risk Score",
        f"{statistics['average_risk']:.1f}",
    )

st.plotly_chart(
    build_overview_bar_chart(products),
    width="stretch",
)

st.divider()

# ============================================================
# Individual Risk Assessments
# ============================================================

st.subheader("Risk Assessments")

tabs = st.tabs([HAZARD_LABELS[hazard] for hazard in products])

for tab, hazard in zip(tabs, products):

    with tab:

        risk = products[hazard]

        col1, col2 = st.columns([1, 1])

        with col1:

            st.plotly_chart(
                build_gauge_chart(
                    risk["score"],
                    risk["category"],
                ),
                width="stretch",
            )

        with col2:

            metric_card(
                "Category",
                risk["category"],
            )

            metric_card(
                "Confidence",
                f"{risk['confidence'] * 100:.0f}%",
            )

        st.write("**Drivers**")

        if risk["drivers"]:

            for driver in risk["drivers"]:

                st.success(driver)

        else:

            st.info("No dominant drivers identified.")

        # -------------------------------------------------
        # ML-Calibrated Comparison (Wildfire only, for now)
        # -------------------------------------------------

        ml_calibrated = risk.get("ml_calibrated")

        if ml_calibrated is not None:

            st.divider()

            st.write("**ML-Calibrated Score (experimental)**")

            st.caption(
                "Trained on real NASA FIRMS fire detections vs. "
                "background points, using the same weather and "
                "vegetation inputs as the formula above. Shown "
                "for comparison, not as the official score."
            )

            st.caption(f"⚠️ {ml_calibrated.get('temporal_note', '')}")

            col1, col2, col3 = st.columns(3)

            with col1:

                metric_card(
                    "ML Score",
                    f"{ml_calibrated['score']:.1f}",
                )

            with col2:

                metric_card(
                    "ML Category",
                    ml_calibrated["category"],
                )

            with col3:

                metric_card(
                    "Model Certainty",
                    f"{ml_calibrated['model_certainty'] * 100:.0f}%",
                )

            with st.expander("Feature Importance (learned)"):

                for feature, importance in ml_calibrated["feature_importance"].items():

                    st.write(f"- **{feature}**: {importance:.3f}")

        elif hazard == "wildfire":

            st.caption(
                "ML-calibrated wildfire score unavailable — "
                "train the model first "
                "(models/train_wildfire_risk_classifier.py)."
            )

st.divider()

# ============================================================
# Risk Summary
# ============================================================

st.subheader("Risk Summary")

category_counts = statistics["category_counts"]

col1, col2 = st.columns([1, 1])

with col1:

    st.plotly_chart(
        build_category_pie_chart(category_counts),
        width="stretch",
    )

with col2:

    st.write("**Category Breakdown**")

    for category in ["Low", "Moderate", "High", "Very High"]:

        count = category_counts.get(category, 0)

        st.write(f"🔹 **{category}**: {count} hazard" f"{'s' if count != 1 else ''}")

summary_rows = [
    {
        "Hazard": HAZARD_LABELS[hazard],
        "Score": risk["score"],
        "Category": risk["category"],
        "Confidence": f"{risk['confidence'] * 100:.0f}%",
    }
    for hazard, risk in products.items()
]

summary_table = (
    pd.DataFrame(summary_rows)
    .sort_values(
        "Score",
        ascending=False,
    )
    .reset_index(drop=True)
)

with st.expander("Full Risk Summary Table"):

    st.dataframe(
        summary_table,
        width="stretch",
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

    st.write("### Products")

    st.write(product["products"])

    st.write("### Statistics")

    st.write(product["statistics"])

    st.write("### Processing")

    st.write(product["processing"])

st.divider()

# ============================================================
# Developer Information
# ============================================================

with st.expander("Developer Debug"):

    st.write("Risk Product Keys")

    st.write(list(product.keys()))

    st.write()

    st.write("Full Risk Product")

    st.write(product)
