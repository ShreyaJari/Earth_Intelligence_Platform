
import streamlit as st
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from components.sidebar import render_sidebar_footer, render_sidebar_header
from utils.config import APP_ICON, APP_NAME, VERSION
from utils.styles import load_css
import sys
from pathlib import Path

# Ensure the project root is on sys.path so
# "earth_intelligence_platform.engines...." imports resolve
# correctly regardless of how/where this script is invoked
# (local `streamlit run`, Streamlit Cloud, etc.)

# ---------------------------------------------------------
# Streamlit Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------

DEFAULT_SESSION = {
    "aoi": None,
    "catalog": None,
    "satellite": None,
    "terrain": None,
    "landcover": None,
    "weather": None,
    "risk": None,
    "intelligence": None,
    "pipeline_status": {
        "location": False,
        "discovery": False,
        "satellite": False,
        "terrain": False,
        "landcover": False,
        "weather": False,
        "risk": False,
        "intelligence": False,
    },
}

for key, value in DEFAULT_SESSION.items():

    if key not in st.session_state:

        st.session_state[key] = value

# ---------------------------------------------------------
# Page Definitions
# ---------------------------------------------------------

PAGES_DIR = "pages"

pages = {
    "Overview": [
        st.Page(
            f"{PAGES_DIR}/home.py",
            title="Home",
            icon="🏠",
            default=True,
        ),
    ],
    "Data Engines": [
        st.Page(
            f"{PAGES_DIR}/satellite.py",
            title="Satellite",
            icon="🛰️",
        ),
        st.Page(
            f"{PAGES_DIR}/terrain.py",
            title="Terrain",
            icon="🏔️",
        ),
        st.Page(
            f"{PAGES_DIR}/weather.py",
            title="Weather",
            icon="🌦️",
        ),
        st.Page(
            f"{PAGES_DIR}/land_cover.py",
            title="Land Cover",
            icon="🌱",
        ),
    ],
    "Analysis": [
        st.Page(
            f"{PAGES_DIR}/risk.py",
            title="Risk",
            icon="⚠️",
        ),
        st.Page(
            f"{PAGES_DIR}/earth_intelligence.py",
            title="Earth Intelligence",
            icon="🌍",
        ),
    ],
}

# Hide the built-in nav widget so we control layout ourselves.

navigation = st.navigation(
    pages,
    position="hidden",
)

# ---------------------------------------------------------
# Sidebar: Branding, then navigation, then version footer
# ---------------------------------------------------------

with st.sidebar:

    render_sidebar_header()

    for section, section_pages in pages.items():

        st.caption(section)

        for page in section_pages:

            st.page_link(page)

    st.divider()

    render_sidebar_footer()

# ---------------------------------------------------------
# Run Selected Page
# ---------------------------------------------------------

navigation.run()
