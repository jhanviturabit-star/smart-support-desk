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

# MAIN APP
st.title("Smart Support Desk")

#DASHBOARD
if st.session_state.role in ["TEAM_LEAD", "ADMIN"]:
    st.header("Dashboard")

    res = requests.get(
        f"{BACKEND_URL}/dashboard/summary",
        headers=auth_headers()
    )

    if res.status_code == 200:
        data = res.json()["data"]

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Tickets", data["total_tickets"])

        status_count = {
            "Open": 0,
            "Closed": 0,
            "In_progress": 0,
            "Resolved": 0
        }

        for item in data["tickets_by_status"]:
            status_count[item["t_status"]] = item["count"]

        col2.metric("Open", status_count["Open"])
        col3.metric("Closed", status_count["Closed"])
        col4.metric("In Progress", status_count["In_progress"])
        col5.metric("Resolved", status_count["Resolved"])

#CUSTOMERS
st.header("Customers")

res = requests.get(
    f"{BACKEND_URL}/customers",
    headers=auth_headers()
)

if res.status_code == 200:
    df = pd.DataFrame(res.json())
    st.dataframe(df, use_container_width=True)

#TICKETS
st.header("Tickets")


status_filter = st.selectbox(
    "Status",
    ["All", "Open", "Closed", "In_progress", "Resolved"]
)

priority_filter = st.selectbox(
    "Priority",
    ["All", "Low", "Medium", "High", "Critical"]
)

params = {}
if status_filter != "All":
    params["status"] = status_filter
if priority_filter != "All":
    params["priority"] = priority_filter

res = requests.get(
    f"{BACKEND_URL}/tickets",
    headers=auth_headers(),
    params=params
)

if res.status_code == 200:
    df = pd.DataFrame(res.json())
    st.dataframe(df, use_container_width=True)
