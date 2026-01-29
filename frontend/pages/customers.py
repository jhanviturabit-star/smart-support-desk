import streamlit as st
import pandas as pd
import requests
from utils import BACKEND_URL, auth_headers

if "show_add_customer" not in st.session_state:
    st.session_state.show_add_customer = False

if "delete_customer_id" not in st.session_state:
    st.session_state.delete_customer_id = None

if "edit_customer" not in st.session_state:
    st.session_state.edit_customer = None

if 'user_id' not in st.session_state or st.session_state.user_id is None:
    st.error("Session expired. Please login again.")
    st.stop()

#CUSTOMERS
st.header("Customers")
st.subheader("Manage your customer database")

res = requests.get(
    f"{BACKEND_URL}/customers",
    headers=auth_headers()
)

if res.status_code == 200:
    df = pd.DataFrame(res.json())
    #st.dataframe(df, use_container_width=True)
else:
    st.error("Failed to load customers")


#st.markdown("### Customers")

top_left, top_right = st.columns([4,1])
#top_left will have 4 parts of space

with top_left:
    search = st.text_input("Search.... ", placeholder = "Search by email or phone")

with top_right:
    st.write(" ") #adding a space
    if st.button("Add"):
        st.session_state.show_add_customer = True

# col1, col2 = st.columns([3,1])
# #col1 will have 3 parts of space

# with col1:
#     search = st.text_input("Search customers")

# with col2:
#     st.write(" ") #adding a space
#     if st.write("Add"):
#         st.session_state.show_add_customer = True

#search bar
if search:
    df = df[
        df['c_name'].str.contains(search, case=False, na=False) | df['c_email'].str.contains(search, case=False, na=False)
    ]

#customer row
st.markdown("---")

for _, row in df.iterrows():
    col1, col2, col3, col4 = st.columns([3, 3, 2, 2])

    with col1:
        st.markdown(f"**{row['c_name']}**")

    with col2:
        st.text(row['c_email'])
    
    with col3:
        st.text(row['phone'])

    with col4:
        can_modify = (st.session_state.role == 'ADMIN' or row['created_by'] == st.session_state.user_id)

        if can_modify:
            if st.button("Edit", key=f"edit_{row['c_id']}"):
                st.session_state.edit_customer = row.to_dict()
                st.session_state.delete_customer_id = None

            if st.button("Delete", key=f"del_{row['c_id']}"):
                st.session_state.delete_customer_id = row['c_id']
                st.session_state.delete_customer_name = row['c_name']
                st.session_state.edit_customer = None
                st.rerun()

#delete confirmation
if st.session_state.delete_customer_id:

    st.markdown("---")
    st.warning("Do you really want to delete this customer?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Cancel', key='cancel_delete'):
            st.session_state.delete_customer_id = None
            st.rerun()

    with col2:
        if st.button("Yes", key='confirm_delete'):
            res = requests.delete(
            f"{BACKEND_URL}/customers/{st.session_state.delete_customer_id}",
            headers=auth_headers()
        )
        try:
            data = res.json()
        except ValueError:
            st.error(f"Request failed (status {res.status_code})")
        else:
            if res.status_code == 200:
                st.success("Customer deleted successfully")
                st.session_state.delete_customer_id = None
                st.rerun()
            else:
                try:
                    error_msg = res.json().get("error", "Failed to delete customer")
                except ValueError:
                    error_msg = f"Failed to delete customer (status {res.status_code})"

                st.error(error_msg)

st.markdown("---")

#edit 
if st.session_state.edit_customer:

    customer = st.session_state.edit_customer

    st.markdown("---")

    st.subheader("Edit Customer")

    with st.form("edit_customer_form"):
        name = st.text_input("Name", value=customer['c_name'])
        email = st.text_input("Email", value=customer['c_email'])
        phone = st.text_input("Phone", value=customer['phone'])

        col1, col2 = st.columns(2)

        with col1:
            cancel = st.form_submit_button("Cancel")
        
        with col2:
            save = st.form_submit_button("Save")

        #actions
        if cancel:
            st.session_state.edit_customer = None
            st.rerun()

        if save:
            if not name or not email or not phone:
                st.error("Fields are required!")
            elif '@' not in email:
                st.error("Invalid email")
            elif len(phone) > 10 or not phone.isdigit():
                st.error("Invalid phone no.")
            else:
                res = requests.put(
                    f"{BACKEND_URL}/customers/{customer['c_id']}",
                    headers=auth_headers(),
                    json={
                        'c_name' : name,
                        'c_email' : email,
                        'phone' : phone
                    }
                )

                if res.status_code == 200:
                    st.success("Customer updated successfully")
                    st.session_state.edit_customer = None
                    st.rerun()
                else :
                    try:
                        error_msg = res.json().get("error", "Failed to update customer")
                    except ValueError:
                        error_msg = f"Failed to update customer (status {res.status_code})"

                    st.error(error_msg)

#add customer
if st.session_state.get('show_add_customer'):

    st.markdown("---")
    st.subheader("Add Customer")

    with st.form('add_customer_form'):
        
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        
        submit = st.form_submit_button('Create')

        if submit:
            #validatiins
            if not name or not email or not phone:
                st.error("Fields are required!")
            elif '@' not in email:
                st.error("Invalid email")
            elif len(phone) > 10 or not phone.isdigit():
                st.error("Invalid phone no.")
            else:
                res = requests.post(
                    f"{BACKEND_URL}/customers/create",
                    headers=auth_headers(),
                    json={
                        'c_name' : name,
                        'c_email' : email,
                        'phone' : phone
                    }
                )

                if res.status_code == 201:
                    st.success("Customer addedd successfully")
                    st.session_state.show_add_customer = False
                    st.rerun()
                else :
                    try:
                        error_msg = res.json().get("error", "Failed to add customer")
                    except ValueError:
                        error_msg = f"Failed to add customer (status {res.status_code})"

                    st.error(error_msg)

