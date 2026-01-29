import streamlit as st
#import pandas as pd
import requests
from streamlit_app import BACKEND_URL, auth_headers

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