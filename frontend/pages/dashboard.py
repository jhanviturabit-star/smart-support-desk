import streamlit as st
import pandas as pd
import requests
from streamlit_app import BACKEND_URL, auth_headers
import plotly.express as px

st.set_page_config(page_title="Dashboard", layout="wide")

st.session_state.role = st.session_state.role.upper()

# st.write("DEBUG - Role:", st.session_state.role)
# st.write("DEBUG - Token:", st.session_state.token[:10], "...")

# --------- Ensure role exists (FIXED) ---------
if "role" not in st.session_state or "token" not in st.session_state:
    st.warning("Please login first")
    st.stop()

# --------- Only allow dashboard if logged in ---------
if st.session_state.role not in ["TEAM_LEAD", "ADMIN", "AGENT"]:
    st.warning("Unauthorized access")
    st.stop()

# ---------------- DASHBOARD STARTS ----------------
st.header("Dashboard")
st.caption("Overview of your support operations")

# Fetch dashboard data
#st.write("DEBUG HEADERS:", auth_headers())

res = requests.get(
    f"{BACKEND_URL}/dashboard/",
    headers=auth_headers()
)

if res.status_code != 200:
    st.error("Failed to load dashboard")
    st.stop()

data = res.json()["data"]

# ---------------- METRICS ROW (TOP CARDS) ----------------
st.subheader("Overview")

col1, col2, col3, col4, col5, col6 = st.columns(6)

# Prepare status counts safely
status_count = {
    "Open": 0,
    "Closed": 0,
    "In_progress": 0,
    "Resolved": 0
}

for item in data["tickets_by_status"]:
    status_count[item["t_status"]] = item["count"]

#Common metrics (both for Agent & Admin)
col1.metric("Total Tickets", data["total_tickets"])
col2.metric("Open", status_count["Open"])
col3.metric("Closed", status_count["Closed"])
col4.metric("In Progress", status_count["In_progress"])
col5.metric("Resolved", status_count["Resolved"])

#Different metrics according to Admin & Agent
if st.session_state.role == 'AGENT':
    total_customers = len(data["top_customers"])
    col6.metric("My Customer", total_customers)
else:
    total_customers = len(data['top_customers'])
    col6.metric("Top customers"), total_customers

st.markdown("---")

# ---------------- CHARTS SECTION ----------------
col_left, col_right = st.columns(2)

# -------- Tickets by Status (Pie Chart) --------
with col_left:
    st.markdown(" Tickets by Status")

    if len(data["tickets_by_status"]) == 0:
        st.info("No status data available")
    else:
        df_status = pd.DataFrame(data["tickets_by_status"])
        fig1 = px.pie(
            df_status,
            names="t_status",
            values="count",
            hole=0.5
        )
        st.plotly_chart(fig1, use_container_width=True)

# -------- Tickets by Priority (Bar Chart) --------
with col_right:
    st.markdown(" Tickets by Priority")

    if len(data["tickets_by_priority"]) == 0:
        st.info("No priority data available")
    else:
        df_priority = pd.DataFrame(data["tickets_by_priority"])
        fig2 = px.bar(
            df_priority,
            x="priority",
            y="count"
        )
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ---------------- TOP CUSTOMERS SECTION ----------------
st.subheader(" Top Customers")

if len(data["top_customers"]) == 0:
    st.info("No customer data available")
else:
    df_customers = pd.DataFrame(data["top_customers"])
    st.dataframe(df_customers, use_container_width=True)

# ---------------- ROLE BASED MESSAGE (LIKE YOUR SS) ----------------
st.markdown("---")

if st.session_state.role == "AGENT":
    st.success("You are viewing your own tickets only (Agent Dashboard)")
else:
    st.success("You are viewing ALL tickets (Admin / Team Lead Dashboard)")
