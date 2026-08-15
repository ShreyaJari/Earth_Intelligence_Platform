import streamlit as st


def metric_card(title, value, delta=None, help_text=None):
    """
    Display a reusable metric card.
    """

    st.metric(
        label=title,
        value=value,
        delta=delta,
        help=help_text,
    )
