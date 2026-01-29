import streamlit as st
import pandas as pd
import requests

BACKEND_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Smart Support Desk", layout="wide")

# Session State
if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.role = None

# Helpers
def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }

# AUTH PAGE
def auth_page():
    st.title("Smart Support Desk")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    #LOGIN
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            res = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": email, "password": password}
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data["token"]
                st.session_state.role = data["role"]
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")

    #SIGNUP
    with tab2:
        st.info("New users will be registered as **Agents**")

        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create Account"):
            res = requests.post(
                f"{BACKEND_URL}/auth/register",
                json={
                    "name": name,
                    "email": email,
                    "password": password
                }
            )

            if res.status_code == 201:
                st.success("Account created. Please login.")
                st.write("STATUS:", res.status_code)
                st.write("RESPONSE:", res.text)
            else:
                try:
                    error_mssg = res.json().get('error', 'Registration failed')
                except:
                    error_mssg = "Please try again"

                st.error(error_mssg)

    st.stop()  #stop app here if not logged in

# AUTH GATE
if st.session_state.token is None:
    auth_page()

st.success("Logged in successfully! Use the sidebar to navigate")

# MAIN APP
st.title("Smart Support Desk")
