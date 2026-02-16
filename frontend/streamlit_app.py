import streamlit as st
import pandas as pd
import jwt
import requests
from utils import BACKEND_URL, auth_headers

st.set_page_config(page_title="Smart Support Desk", layout="wide")

hide_menu_style = """
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

#can_modify = (st.session_state.role == 'ADMIN' or row.get('created_by') == st.session_state.user_id)

# if 'user_id' not in st.session_state:
#     st.session_state.user_id = None

# Session State
if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.user_id = None

def logout():
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.user_id = None
    st.rerun()

# AUTH PAGE
def auth_page():
    st.title("Smart Support Desk")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    #LOGIN
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        role = st.radio("Login as:", options=['AGENT', 'ADMIN'], horizontal=True)


        if st.button("Login"):
            res = requests.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": email, "password": password, "role": role}
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data["token"]
                print("NEW TOKEN:", res.json()["token"])
                st.session_state.role = str(data["role"]).upper()
                st.write("LOGIN RESPONSE:", data)
                st.session_state.user_id = data["user_id"]
                st.success("Logged in successfully")
                print(st.session_state.token)
                st.rerun()
            else:
                st.error("Invalid credentials")

    #SIGNUP
    with tab2:
        st.info("New users will be registered as **Agents**")

        name = st.text_input("Full Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        signup_role = st.radio("Register as:", options=['AGENT', 'ADMIN'], horizontal=True, key="signup_role")


        if st.button("Create Account"):
            res = requests.post(
                f"{BACKEND_URL}/auth/register",
                json={
                    "name": name,
                    "email": email,
                    "password": password,
                    "role": signup_role
                }
            )

            if res.status_code == 201:
                st.success("Account created. Please login.")
                st.write(f"RESPONSE: {res.text}")
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

with st.sidebar:
    st.title("Support Desk")

    st.markdown(f"**Logged in as:** {st.session_state.role}")

    st.markdown("---")

    st.page_link("pages/dashboard.py", label="Dashboard")
    st.page_link("pages/customers.py", label="Customers")
    st.page_link("pages/tickets.py", label="Tickets")

    st.markdown("---")

    if st.button("Logout"):
        logout()

    st.caption("Smart Support Desk v1.0")

# MAIN APP
st.title("Smart Support Desk")