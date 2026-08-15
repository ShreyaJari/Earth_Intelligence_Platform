import streamlit as st
from utils.config import APP_NAME, VERSION


def render_sidebar_header():
    """
    Render the sidebar branding header.
    """

    st.title(APP_NAME)

    st.markdown("---")

    st.markdown("""
        **Earth Intelligence Platform**

        Analyze geospatial data and visualize
        environmental intelligence products.
        """)

    st.markdown("---")


def render_sidebar_footer():
    """
    Render the sidebar footer (version).
    """

    st.caption(f"Version {VERSION}")
