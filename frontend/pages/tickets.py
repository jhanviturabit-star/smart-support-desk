import streamlit as st
import pandas as pd
import requests
from utils import BACKEND_URL, auth_headers

#Session state
if "show_add_ticket" not in st.session_state:
    st.session_state.show_add_ticket = False

if "delete_target" not in st.session_state:
    st.session_state.delete_target = None

# if "delete_target" not in st.session_state:
#     st.session_state.delete_target = False

if "edit_ticket" not in st.session_state:
    st.session_state.edit_ticket = None

if "role" not in st.session_state:
    st.session_state.role = None

if "user_id" not in st.session_state or st.session_state.user_id is None:
    st.error("Session expired. Please login again.")
    st.stop()

PRIORITY_OPTIONS = ['Low', 'Medium', 'High', 'Critical']
STATUS_OPTIONS = ['Open', 'In-progress', 'Resolved', 'Closed']

PRIORITY_FILTER_OPTIONS = ['All' ,'Low', 'Medium', 'High', 'Critical']
STATUS_FILTER_OPTIONS = ['All','Open', 'In_progress', 'Resolved', 'Closed']

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

#Fetch customers from Dropdown
cust_res = requests.get(
    f"{BACKEND_URL}/customers",
    headers=auth_headers()
)

if cust_res.status_code == 200:
    customers = pd.DataFrame(cust_res.json())
    customers = customers[customers['created_by'] == int(st.session_state.user_id)]
else:
    customers = pd.DataFrame()

if not customers.empty:
    customer_map = dict(zip(customers["c_name"], customers["c_id"]))
    customer_names = list(customer_map.keys())
else:
    customer_map = {}
    customer_names = []

#st.write("Customers Data:", customers)

#Top actions
col1, col2, col3, col4 = st.columns([3, 1.2, 1.2, 1])

with col1:
    search = st.text_input("Search tickets", placeholder="Search by title or status")

with col2:
    status_filter = st.selectbox(" ", STATUS_FILTER_OPTIONS)

with col3:
    priority_filter = st.selectbox(" ", PRIORITY_FILTER_OPTIONS)

with col4:
    st.write("")
    if st.button("+ New Ticket"):
        st.session_state.show_add_ticket = True
        st.session_state.edit_ticket = None


#Search filter
if search:
    df = df[
        df['t_title'].str.contains(search, case=False, na=False)
        | df['t_status'].str.contains(search, case=False, na=False)
    ]

#Status Filter
if status_filter != "All":
    df = df[df['t_status'] == status_filter]

#Priority filter
if priority_filter != "All":
    df = df[df['priority'] == priority_filter]

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

            if st.button("Delete", key=f"delete_{row['t_id']}"):
                st.session_state.delete_target = row.to_dict()
                st.rerun()

#Delete Ticket
if st.session_state.delete_target:

    ticket = st.session_state.delete_target

    st.markdown("---")
    st.error(f"Delete ticket **{ticket['t_title']}** ?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel"):
            st.session_state.delete_target = None
            st.rerun()
            
    with col2:
        if st.button("Yes, Delete", key=f"confirm_delete_{ticket['t_id']}"):
                res = requests.delete(
                    f"{BACKEND_URL}/tickets/{ticket['t_id']}",
                    headers=auth_headers()
                )

                if res.status_code == 200:
                    st.success("Ticket deleted successfully")
                    st.session_state.delete_target = None
                    st.rerun()
                else:
                    try:
                        data = res.json()
                        if isinstance(data, dict):
                            st.error(data.get("error", "Delete failed"))
                        elif isinstance(data, list) and data:
                            first_item = data[0]
                            if isinstance(first_item, dict):
                                st.error(first_item.get("error", "Delete failed"))
                            else:
                                st.error(str(first_item))
                        else:
                            st.error("Delete failed")
                    except Exception as e:
                        st.error(f"Delete failed: {str(e)}")

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
                try:
                    error = (res.json().get("error", "Failed to update ticket"))
                except Exception:
                    error = f"Failed to update ticket (status {res.status_code})"
                st.error(error)

#Create Ticket
if st.session_state.show_add_ticket:
    st.markdown("---")
    st.subheader("Create New Ticket")

    if customers.empty:
        st.warning("No customers found. Create a customer first")
        st.stop()

    with st.form("create_ticket_form"):
        selected_customer = st.selectbox("Select your customer", options=customer_names, index=0)
        title = st.text_input("Title")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", PRIORITY_OPTIONS)
        status = st.selectbox("Status", STATUS_OPTIONS)
        #customer_id = st.number_input("Customer ID", min_value=1, step=1)

        submit = st.form_submit_button("Create")

        if submit:
            if not title or not description:
                st.error("Title and description are required")
            else:
                selected_c_id = customer_map[selected_customer]
                if not selected_c_id:
                    st.error("Please select a valid customer")
                    st.stop()

                res = requests.post(
                f"{BACKEND_URL}/tickets/create",
                headers=auth_headers(),
                json={
                    "t_title": title,
                    "t_description": description,
                    "priority": priority,
                    "c_id": selected_c_id,
                    't_status': status
                }
                )

                if res.status_code == 201:
                    st.success("Ticket created successfully")
                    st.session_state.show_add_ticket = False
                    st.rerun()
                else:
                    try:
                        data = res.json()
                        if isinstance(data, dict):
                            st.error(data.get("error", "Failed to create ticket"))
                        elif isinstance(data, list) and data:
                            first_item = data[0]
                            if isinstance(first_item, dict):
                                st.error(first_item.get("error", "Failed to create ticket"))
                            else:
                                st.error(str(first_item))
                        else:
                            st.error("Failed to create ticket")
                    except Exception as e:
                        st.error(f"Failed to create ticket: {str(e)}")

