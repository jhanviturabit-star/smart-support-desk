import streamlit as st
import pandas as pd
import jwt
import requests
from utils import BACKEND_URL, auth_headers

st.set_page_config(page_title="Smart Support Desk", layout="wide")

#can_modify = (st.session_state.role == 'ADMIN' or row.get('created_by') == st.session_state.user_id)

# if 'user_id' not in st.session_state:
#     st.session_state.user_id = None

# Session State
if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.user_id = None

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
                st.write("LOGIN RESPONSE:", data)
                st.session_state.user_id = data["user_id"]
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
                st.success("Customer created successfully")
                st.success("RESPONSE:", res.text)
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