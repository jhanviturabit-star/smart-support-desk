import streamlit as st
import pandas as pd
import requests

BACKEND_URL = 'http://127.0.0.1:5000/'

st.set_page_config(page_title='Smart Support Desk', layout='wide')

st.title('Smart Support Desk')

#1. Dashboard

st.header('Dashboard')

dashboard_res = requests.get(f'{BACKEND_URL}/dashboard')

if dashboard_res.status_code == 200:
    data = dashboard_res.json()['data']

    col1, col2, col3, col4, col5= st.columns(5)

    col1.metric('Total Tickets', data['total_tickets']) #total tickets

    #define all status
    statuses = ['Open', 'Closed', 'In_progress', 'Resolved']

    #initializ counts
    status_count = {
        'Open' : 0,
        'Closed' : 0,
        'In_progress' : 0,
        'Resolved' : 0
    }

    #loop
    for item in data['by_status']:
        status = item['t_status']
        count = count['count']

        if status in status_count:
            status_count[status] = count

    col2.metric('Open Tickets', status_count['Open'])
    col3.metric('Closed Tickets', ['Closed'])
    col4.metric('In Progress Tickets', ['In_progress'])
    col5.metric('Resolved Tickets', ['Resolved'])

#2. Customers

st.header('Customers')

customers_res = requests.get(f'{BACKEND_URL}/customers')

if customers_res.status_code == 200:
    customers = customers_res.json()
    df_customers = pd.DataFrame(customers)
    st.dataframe(df_customers, use_container_width=True)

#3. Tickets

st.header('Tickets')

status_filter = st.selectbox('Filter by status', options=['All', 'Open', 'Closed', 'In_progress', 'Resolved'])

priority_filter = st.selectbox('Filter by priority', options=['All', 'High', 'Low', 'Critical', 'Medium'])

params = {}

if status_filter != 'All':
    params['status'] = status_filter

if priority_filter != 'All':
    params['priority'] = priority_filter
    
tickets_res = requests.get(f'{BACKEND_URL}/tickets', params=params)

if tickets_res.status_code == 200:
    tickets = tickets_res.json()
    df_tickets = pd.DataFrame(tickets)
    st.dataframe(df_tickets, use_container_width=True)

