import streamlit as st

BACKEND_URL = "http://192.168.1.33:5000"

def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }
