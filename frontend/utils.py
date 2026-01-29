import streamlit as st

BACKEND_URL = "http://127.0.0.1:5000"

def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }
