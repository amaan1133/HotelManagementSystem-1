import streamlit as st
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication
from utils.database_data_manager import load_data, save_data, generate_id, get_current_datetime, add_record
import pandas as pd

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

user_role = st.session_state.get('user_role', 'User')

st.title("📊 Account Sales")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
sales = load_data('sales.json', selected_hotel)
rooms = load_data('rooms.json', selected_hotel)

# Filter account sales
account_sales = [s for s in sales if s['payment_type'] == 'Account']

# Overview
st.markdown("### Account Sales Overview")

total_account_sales = sum(sale['amount'] for sale in account_sales)
pending_account_sales = sum(sale['amount'] for sale in account_sales if sale.get('status') == 'Pending')
completed_account_sales = sum(sale['amount'] for sale in account_sales if sale.get('status') == 'Completed')

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Account Sales", f"₹{total_account_sales:,.2f}")
with col2:
    st.metric("Pending Account Sales", f"₹{pending_account_sales:,.2f}")
with col3:
    st.metric("Completed Account Sales", f"₹{completed_account_sales:,.2f}")

st.markdown("---")

# Add new account sale
st.markdown("### Add Account Sale")

with st.form("add_account_sale_form"):
    col1, col2 = st.columns(2)

    with col1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        amount = st.number_input("Amount", min_value=0.0, step=100.0)
        sale_type = st.selectbox("Sale Type", ["Room Booking", "Food & Beverage", "Event", "Conference", "Other"])

    with col2:
        description = st.text_area("Description", placeholder="Sale description")
        due_date = st.date_input("Payment Due Date")
        # Room number (optional) - dynamic based on selected hotel
        selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
        rooms = load_data('rooms.json', selected_hotel)
        if isinstance(rooms, dict):
            all_rooms = [f"Room {k}" for k in sorted(rooms.keys(), key=lambda x: int(x))]
        elif isinstance(rooms, list):
            all_rooms = [f"Room {room.get('room_number', room.get('id', i+101))}" for i, room in enumerate(rooms)]
        else:
            all_rooms = [f"Room {i}" for i in range(101, 109)]
        room_options = ["None"] + all_rooms
        room_number = st.selectbox("Room Number (if applicable)", room_options)

    if st.form_submit_button("Add Account Sale", type="primary"):
        if customer_name and amount > 0:
            new_sale = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'type': sale_type,
                'amount': amount,
                'payment_type': 'Account',
                'customer_name': customer_name,
                'description': description,
                'room_number': room_number if room_number != "None" else None,
                'due_date': str(due_date),
                'status': 'Pending',
                'created_by': st.session_state.get('username', 'Unknown')
            }
            sales.append(new_sale)
            save_data('sales.json', sales, selected_hotel)
            st.success("Account sale added successfully!")
            st.rerun()
        else:
            st.error("Customer name and amount are required")

st.markdown("---")

# Account sales list
st.markdown("### Account Sales Records")

if account_sales:
    # Filter
    filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])

    filtered_sales = account_sales
    if filter_status != "All":
        filtered_sales = [s for s in filtered_sales if s.get('status') == filter_status]

    for sale in filtered_sales:
        # Show original advance date for advance payments, regular date for others
        display_date = sale.get('original_advance_date', sale['date'][:10] if sale['date'] else 'N/A')
        with st.expander(f"#{sale['id']} - {sale['customer_name']} - ₹{sale['amount']:,.2f} - {display_date}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {sale['date']}")
                st.write(f"**Customer:** {sale['customer_name']}")
                st.write(f"**Amount:** ₹{sale['amount']:,.2f}")
                st.write(f"**Type:** {sale['type']}")
                st.write(f"**Status:** {sale.get('status', 'Pending')}")

            with col2:
                st.write(f"**Due Date:** {sale.get('due_date', 'Not Set')}")
                st.write(f"**Room:** {sale.get('room_number', 'N/A')}")
                st.write(f"**Created by:** {sale.get('created_by', 'Unknown')}")

            if sale.get('description'):
                st.write(f"**Description:** {sale['description']}")

            # Actions
            col1, col2, col3 = st.columns(3)

            with col1:
                if sale.get('status') == 'Pending' and st.button(f"Mark Paid", key=f"paid_{sale['id']}"):
                    for s in sales:
                        if s['id'] == sale['id']:
                            s['status'] = 'Completed'
                            s['payment_date'] = get_current_datetime()
                            break
                    save_data('sales.json', sales, selected_hotel)
                    st.success("Account sale marked as paid!")
                    st.rerun()

            with col2:
                if user_role == 'Admin' and st.button(f"Edit", key=f"edit_{sale['id']}"):
                    with st.form(f"edit_sale_{sale['id']}"):
                        new_amount = st.number_input("Amount", value=sale['amount'], min_value=0.0)
                        new_status = st.selectbox("Status", ["Pending", "Completed"], 
                                                index=["Pending", "Completed"].index(sale.get('status', 'Pending')))
                        if st.form_submit_button("Update Sale"):
                            for s in sales:
                                if s['id'] == sale['id']:
                                    s['amount'] = new_amount
                                    s['status'] = new_status
                                    break
                            save_data('sales.json', sales, selected_hotel)
                            st.success("Sale updated!")
                            st.rerun()

            with col3:
                if user_role == 'Admin' and st.button(f"Delete", key=f"delete_{sale['id']}", type="secondary"):
                    sales = [s for s in sales if s['id'] != sale['id']]
                    save_data('sales.json', sales, selected_hotel)
                    st.success("Sale deleted!")
                    st.rerun()
else:
    st.info("No account sales found")