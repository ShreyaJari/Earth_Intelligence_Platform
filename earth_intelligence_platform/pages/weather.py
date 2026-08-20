"""
Earth Intelligence Platform

Weather Page

Runs the Weather Engine and displays the results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.cards import metric_card

from earth_intelligence_platform.engines.weather_engine.main import run_weather_engine

# ============================================================
# Page
# ============================================================

st.title("🌦️ Weather Engine")

st.caption(
    "Historical hourly weather observations for the selected " "Area of Interest."
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

from datetime import date, timedelta

st.subheader("Date Range")

col1, col2 = st.columns(2)

with col1:

    weather_start_date = st.date_input(
        "Start Date",
        value=date.today() - timedelta(days=30),
        min_value=date(2015, 1, 1),
        max_value=date.today()
        - timedelta(days=2),  # archive API has a short reporting delay
    )

with col2:

    weather_end_date = st.date_input(
        "End Date",
        value=date.today() - timedelta(days=2),
        min_value=date(2015, 1, 1),
        max_value=date.today() - timedelta(days=2),
    )

st.caption(
    "Historical archive data — recent days (within ~48 hours) " "are not yet available."
)

# ============================================================
# Run Engine
# ============================================================

if st.button(
    "Run Weather Engine",
    width="stretch",
):

    with st.spinner("Downloading and processing weather data..."):

        product = run_weather_engine(
            aoi=st.session_state["aoi"],
            catalog=st.session_state["catalog"],
            start_date=str(weather_start_date),
            end_date=str(weather_end_date),
        )

        st.session_state["weather"] = product

        st.session_state["pipeline_status"]["weather"] = product["success"]

# ============================================================
# Display Results
# ============================================================

if st.session_state.get("weather") is None:

    st.stop()

product = st.session_state["weather"]

if not product["success"]:

    st.error("Weather Engine failed.")

    st.write(product["errors"])

    st.stop()

st.success("Weather Engine completed successfully.")

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
        "URL",
        dataset["url"],
    )

with st.expander("Available Variables"):

    st.write(dataset["variables"])

st.divider()

# ============================================================
# Location
# ============================================================

st.subheader("Location")

metadata = product["metadata"]

col1, col2, col3, col4 = st.columns(4)

with col1:

    metric_card(
        "Latitude",
        round(metadata["latitude"], 5),
    )

with col2:

    metric_card(
        "Longitude",
        round(metadata["longitude"], 5),
    )

with col3:

    metric_card(
        "Elevation",
        (
            f"{metadata['elevation']} m"
            if metadata.get("elevation") is not None
            else "N/A"
        ),
    )

with col4:

    metric_card(
        "Timezone",
        metadata.get("timezone", "N/A"),
    )

st.divider()

# ============================================================
# Weather Data
# ============================================================

st.subheader("Weather Data")

weather_dataframe = product["products"]["weather_dataframe"]

st.dataframe(
    weather_dataframe,
    use_container_width=True,
)

st.divider()

# ============================================================
# Trends
# ============================================================

st.subheader("Trends")

chart_data = weather_dataframe.set_index("time")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Temperature",
        "Precipitation",
        "Humidity",
        "Wind Speed",
    ]
)

with tab1:

    st.line_chart(
        chart_data["temperature"],
    )

with tab2:

    st.line_chart(
        chart_data["precipitation"],
    )

with tab3:

    st.line_chart(
        chart_data["humidity"],
    )

with tab4:

    st.line_chart(
        chart_data["wind_speed"],
    )

st.divider()

import numpy as np

st.subheader("Wind Rose")

st.caption("Frequency and strength of wind by direction over the " "selected period.")

wind_df = weather_dataframe[["wind_direction", "wind_speed"]].dropna()

direction_bins = np.arange(0, 361, 22.5)

direction_labels = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]

wind_df["direction_bin"] = pd.cut(
    wind_df["wind_direction"] % 360,
    bins=direction_bins,
    labels=direction_labels[:16],
    include_lowest=True,
)

speed_bins = [0, 5, 10, 20, 30, 100]

speed_labels = ["0-5", "5-10", "10-20", "20-30", "30+"]

wind_df["speed_bin"] = pd.cut(
    wind_df["wind_speed"],
    bins=speed_bins,
    labels=speed_labels,
)

wind_rose_data = (
    wind_df.groupby(["direction_bin", "speed_bin"], observed=True)
    .size()
    .reset_index(name="count")
)

wind_rose_fig = px.bar_polar(
    wind_rose_data,
    r="count",
    theta="direction_bin",
    color="speed_bin",
    color_discrete_sequence=px.colors.sequential.Viridis_r,
    labels={"speed_bin": "Wind Speed (km/h)"},
)

wind_rose_fig.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    height=450,
)

st.plotly_chart(
    wind_rose_fig,
    width="stretch",
)

st.divider()

st.subheader("Climograph")

st.caption("Daily mean temperature and total precipitation together.")

climo_df = weather_dataframe.copy()

climo_df["date"] = pd.to_datetime(climo_df["time"]).dt.date

daily_climo = (
    climo_df.groupby("date")
    .agg(
        mean_temperature=("temperature", "mean"),
        total_precipitation=("precipitation", "sum"),
    )
    .reset_index()
)

climo_fig = go.Figure()

climo_fig.add_trace(
    go.Bar(
        x=daily_climo["date"],
        y=daily_climo["total_precipitation"],
        name="Precipitation (mm)",
        marker_color="#4A90D9",
        yaxis="y2",
        opacity=0.6,
    )
)

climo_fig.add_trace(
    go.Scatter(
        x=daily_climo["date"],
        y=daily_climo["mean_temperature"],
        name="Temperature (°C)",
        line=dict(color="#D9534F", width=2),
        yaxis="y1",
    )
)

climo_fig.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    yaxis=dict(
        title="Temperature (°C)",
        side="left",
    ),
    yaxis2=dict(
        title="Precipitation (mm)",
        overlaying="y",
        side="right",
        showgrid=False,
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)

st.plotly_chart(
    climo_fig,
    width="stretch",
)

st.divider()

st.subheader("Diurnal Temperature Pattern")

st.caption(
    "Temperature by hour of day across the selected period — "
    "reveals daily heating/cooling cycles and how they shift "
    "over time."
)

heatmap_df = weather_dataframe.copy()

heatmap_df["time"] = pd.to_datetime(heatmap_df["time"])

heatmap_df["date"] = heatmap_df["time"].dt.date

heatmap_df["hour"] = heatmap_df["time"].dt.hour

pivot = heatmap_df.pivot_table(
    index="hour",
    columns="date",
    values="temperature",
)

heatmap_fig = go.Figure(
    go.Heatmap(
        z=pivot.values,
        x=[str(d) for d in pivot.columns],
        y=pivot.index,
        colorscale="RdYlBu_r",
        colorbar=dict(title="°C"),
    )
)

heatmap_fig.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    xaxis_title="Date",
    yaxis_title="Hour of Day",
)

st.plotly_chart(
    heatmap_fig,
    width="stretch",
)

st.divider()

# ============================================================
# Statistics
# ============================================================

st.subheader("Statistics")

statistics = product["statistics"]

st.write("**Temperature**")

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Minimum",
        f"{statistics['temperature']['minimum']:.1f} °C",
    )

with col2:

    metric_card(
        "Maximum",
        f"{statistics['temperature']['maximum']:.1f} °C",
    )

with col3:

    metric_card(
        "Mean",
        f"{statistics['temperature']['mean']:.1f} °C",
    )

st.write("**Precipitation**")

col1, col2, col3, col4 = st.columns(4)

with col1:

    metric_card(
        "Minimum",
        f"{statistics['precipitation']['minimum']:.2f} mm",
    )

with col2:

    metric_card(
        "Maximum",
        f"{statistics['precipitation']['maximum']:.2f} mm",
    )

with col3:

    metric_card(
        "Mean",
        f"{statistics['precipitation']['mean']:.2f} mm",
    )

with col4:

    metric_card(
        "Total",
        f"{statistics['precipitation']['total']:.2f} mm",
    )

st.write("**Wind Speed**")

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Minimum",
        f"{statistics['wind_speed']['minimum']:.1f} km/h",
    )

with col2:

    metric_card(
        "Maximum",
        f"{statistics['wind_speed']['maximum']:.1f} km/h",
    )

with col3:

    metric_card(
        "Mean",
        f"{statistics['wind_speed']['mean']:.1f} km/h",
    )

st.write("**Wind Direction**")

metric_card(
    "Dominant Direction",
    f"{statistics['wind_direction']['dominant']}°",
)

st.write("**Humidity**")

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Minimum",
        f"{statistics['humidity']['minimum']:.1f}%",
    )

with col2:

    metric_card(
        "Maximum",
        f"{statistics['humidity']['maximum']:.1f}%",
    )

with col3:

    metric_card(
        "Mean",
        f"{statistics['humidity']['mean']:.1f}%",
    )

st.write("**Pressure**")

col1, col2, col3 = st.columns(3)

with col1:

    metric_card(
        "Minimum",
        f"{statistics['pressure']['minimum']:.1f} hPa",
    )

with col2:

    metric_card(
        "Maximum",
        f"{statistics['pressure']['maximum']:.1f} hPa",
    )

with col3:

    metric_card(
        "Mean",
        f"{statistics['pressure']['mean']:.1f} hPa",
    )

st.divider()

st.divider()

# ============================================================
# Extremes
# ============================================================

st.subheader("Extremes")

extremes = statistics.get("extremes", {})

col1, col2, col3 = st.columns(3)

with col1:

    hottest = extremes.get("hottest_hour", {})

    metric_card(
        "Hottest Hour",
        f"{hottest.get('value', 0):.1f}°C",
    )

    st.caption(hottest.get("time", ""))

with col2:

    coldest = extremes.get("coldest_hour", {})

    metric_card(
        "Coldest Hour",
        f"{coldest.get('value', 0):.1f}°C",
    )

    st.caption(coldest.get("time", ""))

with col3:

    heaviest = extremes.get("heaviest_rain_hour", {})

    metric_card(
        "Heaviest Rain Hour",
        f"{heaviest.get('value', 0):.2f} mm",
    )

    st.caption(heaviest.get("time", ""))

col1, col2, col3 = st.columns(3)

with col1:

    metric_card("Wet Days", statistics.get("wet_days", "N/A"))

with col2:

    metric_card("Dry Days", statistics.get("dry_days", "N/A"))

with col3:

    metric_card("Total Days", statistics.get("total_days", "N/A"))

st.divider()

# ============================================================
# Daily Aggregation
# ============================================================

st.subheader("Daily Temperature Range")

daily_df = chart_data.reset_index()

daily_df["date"] = daily_df["time"].dt.date

daily_summary = (
    daily_df.groupby("date")["temperature"].agg(["min", "mean", "max"]).reset_index()
)

daily_fig = go.Figure()

daily_fig.add_trace(
    go.Scatter(
        x=daily_summary["date"],
        y=daily_summary["max"],
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
    )
)

daily_fig.add_trace(
    go.Scatter(
        x=daily_summary["date"],
        y=daily_summary["min"],
        fill="tonexty",
        fillcolor="rgba(45, 106, 79, 0.2)",
        line=dict(width=0),
        name="Daily Range",
    )
)

daily_fig.add_trace(
    go.Scatter(
        x=daily_summary["date"],
        y=daily_summary["mean"],
        line=dict(color="#2D6A4F"),
        name="Daily Mean",
    )
)

daily_fig.update_layout(
    margin=dict(l=0, r=0, t=20, b=0),
    height=350,
    yaxis_title="Temperature (°C)",
)

st.plotly_chart(
    daily_fig,
    width="stretch",
)

st.divider()

# ============================================================
# Historical Baseline / Anomaly
# ============================================================

st.subheader("Compared to Historical Baseline")

anomaly = product.get("anomaly")

baseline = product.get("baseline")

if anomaly is not None and baseline is not None:

    st.caption(
        f"Baseline: same calendar month, averaged across "
        f"{len(baseline['years_used'])} year(s) "
        f"({', '.join(str(y) for y in baseline['years_used'])})"
    )

    col1, col2 = st.columns(2)

    with col1:

        delta = anomaly["temperature_delta"]

        metric_card(
            "Temperature vs. Normal",
            f"{delta:+.1f}°C",
        )

    with col2:

        precip_delta = anomaly["precipitation_delta_per_hour"]

        metric_card(
            "Avg. Hourly Precipitation vs. Normal",
            f"{precip_delta:+.3f} mm/hr",
        )

else:

    st.info(
        "Baseline comparison unavailable — this can happen if "
        "the historical archive fetch failed for every "
        "baseline year."
    )

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

    st.write("Weather Product Keys")

    st.write(list(product.keys()))

    st.write()

    st.write("Products (raw)")

    st.write(product["products"])
