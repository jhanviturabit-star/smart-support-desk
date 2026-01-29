import streamlit as st
import pandas as pd
import requests
from streamlit_app import BACKEND_URL, auth_headers

#CUSTOMERS
st.header("Customers")

res = requests.get(
    f"{BACKEND_URL}/customers",
    headers=auth_headers()
)

if res.status_code == 200:
    df = pd.DataFrame(res.json())
    st.dataframe(df, use_container_width=True)
else:
    st.error("Failed to load customers")

st.stop()