import streamlit as st
import pandas as pd
import requests
from utils import BACKEND_URL, auth_headers

#Session state
if "show_add_ticket" not in st.session_state:
    st.session_state.show_add_ticket = False

if "edit_ticket" not in st.session_state:
    st.session_state.edit_ticket = None

if "role" not in st.session_state:
    st.session_state.role = None

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.error("Session expired. Please login again.")
    st.stop()

PRIORITY_OPTIONS = ['Low', 'Medium', 'High', 'Critical']
STATUS_OPTIONS = ['Open', 'In_progress', 'Resolved', 'Closed']

#Header
st.header("Tickets")
st.subheader("Manage support tickets")

#Fetch tickets
res = requests.get(
    f"{BACKEND_URL}/tickets",
    headers=auth_headers()
)

if res.status_code == 200:
    df = pd.DataFrame(res.json())
else:
    st.error("Failed to load tickets")
    st.stop()

#Top actions
left, right = st.columns([4, 1])

with left:
    search = st.text_input("Search tickets", placeholder="Search by title or status")

with right:
    st.write("")
    if st.button("Create Ticket"):
        st.session_state.show_add_ticket = True
        st.session_state.edit_ticket = None

#Search
if search:
    df = df[
        df['t_title'].str.contains(search, case=False, na=False)
        | df['t_status'].str.contains(search, case=False, na=False)
    ]

st.markdown("---")

#Ticket list
for _, row in df.iterrows():
    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

    with col1:
        st.markdown(f"**{row['t_title']}**")
        st.caption(row['t_description'][:80])

    with col2:
        st.text(f"Status: {row['t_status']}")

    with col3:
        st.text(f"Priority: {row['priority']}")

    with col4:
        st.text(f"Customer ID: {row['c_id']}")

    with col5:
        can_modify = (
            st.session_state.role in ['ADMIN', 'TEAM_LEAD']
            or row['created_by'] == st.session_state.user_id
        )

        if can_modify:
            if st.button("Edit", key=f"edit_{row['t_id']}"):
                st.session_state.edit_ticket = row.to_dict()
                st.session_state.show_add_ticket = False
                st.rerun()

#Edit Ticket
if st.session_state.edit_ticket:
    ticket = st.session_state.edit_ticket

    st.markdown("---")
    st.subheader("Edit Ticket")

    with st.form("edit_ticket_form"):
        title = st.text_input("Title", value=ticket['t_title'])
        description = st.text_area("Description", value=ticket['t_description'])

        priority = st.selectbox(
            "Priority",
            PRIORITY_OPTIONS,
            index=PRIORITY_OPTIONS.index(ticket['priority'])
        )

        status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(ticket['t_status'])
        )

        col1, col2 = st.columns(2)

        with col1:
            cancel = st.form_submit_button("Cancel")

        with col2:
            save = st.form_submit_button("Save")

        if cancel:
            st.session_state.edit_ticket = None
            st.rerun()

        if save:
            res = requests.patch(
                f"{BACKEND_URL}/tickets/{ticket['t_id']}",
                headers=auth_headers(),
                json={
                    "t_title": title,
                    "t_description": description,
                    "priority": priority,
                    "t_status": status
                }
            )

            if res.status_code == 200:
                st.success("Ticket updated successfully")
                st.session_state.edit_ticket = None
                st.rerun()
            else:
                st.error(res.json().get("error", "Failed to update ticket"))

#Create Ticket
if st.session_state.show_add_ticket:
    st.markdown("---")
    st.subheader("Create Ticket")

    with st.form("create_ticket_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", PRIORITY_OPTIONS)
        customer_id = st.number_input("Customer ID", min_value=1, step=1)

        submit = st.form_submit_button("Create")

        if submit:
            if not title or not description:
                st.error("Title and description are required")
            else:
                res = requests.post(
                    f"{BACKEND_URL}/tickets/create",
                    headers=auth_headers(),
                    json={
                        "t_title": title,
                        "t_description": description,
                        "priority": priority,
                        "c_id": customer_id
                    }
                )

                if res.status_code == 201:
                    st.success("Ticket created successfully")
                    st.session_state.show_add_ticket = False
                    st.rerun()
                else:
                    st.error(res.json().get("error", "Failed to create ticket"))
