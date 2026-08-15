import streamlit as st


def success(message):
    """
    Display a success message.
    """

    st.success(message)


def info(message):
    """
    Display an informational message.
    """

    st.info(message)


def warning(message):
    """
    Display a warning message.
    """

    st.warning(message)


def error(message):
    """
    Display an error message.
    """

    st.error(message)


def loading(message="Loading..."):
    """
    Display a loading spinner.
    """

    with st.spinner(message):
        pass
