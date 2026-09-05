"""
Earth Intelligence Platform

Custom CSS styling for the app.
"""

import streamlit as st


def load_css():
    """
    Inject custom CSS for the app.
    """

    st.markdown(
        """
        <style>

        /* ============================================================
           Metric Cards — explicit, theme-independent styling.
           Both background and text colors are hardcoded together so
           they can never mismatch, regardless of the user's system
           light/dark mode or Streamlit's theme.
        ============================================================ */

        .metric-card {
            background: #f8f9fa !important;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 8px;
        }

        .metric-label {
            color: #6c757d !important;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 4px;
            white-space: normal;
            overflow-wrap: break-word;
        }

        .metric-value {
            color: #212529 !important;
            font-size: 1.4rem;
            font-weight: 700;
            white-space: normal;
            overflow-wrap: break-word;
            word-break: break-word;
        }

        /* ============================================================
           Streamlit's own st.metric() component.

           The container itself (stMetric) can clip content via
           overflow/fixed flex sizing even when the inner value text
           is told to wrap — flex children default to min-width:auto,
           which forces overflow instead of wrapping. min-width: 0
           plus overflow: visible on the container fixes this.
        ============================================================ */

                [data-testid="stMetric"] {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 12px 16px;
            overflow: visible !important;
            min-width: 0 !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.15rem !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            word-break: break-word !important;
            overflow: visible !important;
            text-overflow: clip !important;
            min-width: 0 !important;
        }

        [data-testid="stMetricValue"] > div {
            white-space: normal !important;
            overflow-wrap: anywhere !important;
            word-break: break-word !important;
            overflow: visible !important;
            text-overflow: clip !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
            white-space: normal !important;
            overflow-wrap: break-word !important;
        }

        /* ============================================================
           Fixed watermark — stays in the bottom-right corner
           regardless of scroll position.
        ============================================================ */

            .watermark-fixed {
            position: fixed;
            bottom: 10px;
            right: 14px;
            color: #6c757d;
            font-size: 0.85rem;
            font-weight: 600;
            z-index: 9999;
            pointer-events: none;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )