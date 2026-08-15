import streamlit as st


def load_css():
    st.markdown(
        """
        <style>

        /* ---------------------------------------------
           Layout
        --------------------------------------------- */

        .main {
            padding-top: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        /* ---------------------------------------------
           Headings
        --------------------------------------------- */

        h1 {
            color: #1B4332;
            font-weight: 700;
        }

        h2 {
            color: #2D6A4F;
        }

        h3 {
            color: #40916C;
        }

        /* ---------------------------------------------
           Metric Cards
        --------------------------------------------- */

        .stMetric {
            border-radius: 10px;
            padding: 15px;
            background-color: #F8F9FA;
            border: 1px solid #E9ECEF;
            transition: border-color 0.2s ease;
        }

        .stMetric:hover {
            border-color: #95D5B2;
        }

        /* ---------------------------------------------
           Buttons
        --------------------------------------------- */

        .stButton > button {
            border-radius: 8px;
            border: 1px solid #2D6A4F;
            color: #1B4332;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background-color: #2D6A4F;
            color: #FFFFFF;
            border-color: #2D6A4F;
        }

        .stButton > button:focus:not(:active) {
            border-color: #2D6A4F;
            color: #1B4332;
        }

        /* ---------------------------------------------
           Dividers
        --------------------------------------------- */

        hr {
            border: none;
            border-top: 1px solid #E9ECEF;
            margin: 1.5rem 0;
        }

        /* ---------------------------------------------
           Alerts (success / info / warning / error)
        --------------------------------------------- */

        .stAlert {
            border-radius: 8px;
        }

        /* ---------------------------------------------
           Sidebar
        --------------------------------------------- */

        [data-testid="stSidebar"] {
            background-color: #F1F8F4;
            border-right: 1px solid #E9ECEF;
        }

        [data-testid="stSidebar"] h1 {
            font-size: 1.3rem;
        }

        /* ---------------------------------------------
           Tabs
        --------------------------------------------- */

        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
