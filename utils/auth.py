"""Auth guard for Streamlit pages."""

import streamlit as st


def check_auth() -> None:
    """Block page execution if user is not authenticated."""
    if not st.session_state.get("authenticated"):
        st.warning("Faça login pela página principal.")
        st.stop()
