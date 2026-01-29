import streamlit as st
#import pandas as pd
import requests
from streamlit_app import BACKEND_URL, auth_headers

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
