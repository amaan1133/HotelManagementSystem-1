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

st.title("💵 Cash Sales")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
sales = load_data('sales.json', selected_hotel)
rooms = load_data('rooms.json', selected_hotel)

# Filter cash sales
cash_sales = [s for s in sales if s['payment_type'] == 'Cash']

# Overview
st.markdown("### Cash Sales Overview")

total_cash_sales = sum(sale['amount'] for sale in cash_sales)
today_cash_sales = sum(sale['amount'] for sale in cash_sales if sale['date'].startswith('2025-06-23'))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Cash Sales", f"₹{total_cash_sales:,.2f}")
with col2:
    st.metric("Today's Cash Sales", f"₹{today_cash_sales:,.2f}")
with col3:
    st.metric("Total Transactions", len(cash_sales))

st.markdown("---")

# Add new cash sale
st.markdown("### Add Cash Sale")

with st.form("add_cash_sale_form"):
    col1, col2 = st.columns(2)

    with col1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        amount = st.number_input("Amount", min_value=0.0, step=100.0)
        sale_type = st.selectbox("Sale Type", ["Room Booking", "Food & Beverage", "Room Service", "Event", "Other"])

    with col2:
        description = st.text_area("Description", placeholder="Sale description")
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
        cash_received = st.number_input("Cash Received", min_value=0.0, step=100.0)

    if st.form_submit_button("Add Cash Sale", type="primary"):
        if customer_name and amount > 0:
            new_sale = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'type': sale_type,
                'amount': amount,
                'payment_type': 'Cash',
                'customer_name': customer_name,
                'description': description,
                'room_number': room_number if room_number != "None" else None,
                'cash_received': cash_received,
                'status': 'Completed',
                'created_by': st.session_state.get('username', 'Unknown')
            }
            sales.append(new_sale)
            save_data('sales.json', sales, selected_hotel)
            st.success("Cash sale added successfully!")
            st.rerun()
        else:
            st.error("Customer name and amount are required")

st.markdown("---")

# Cash sales list
st.markdown("### Cash Sales Records")

if cash_sales:
    # Filter by date
    filter_date = st.selectbox("Filter by Date", ["All", "Today", "This Week", "This Month"])

    filtered_sales = cash_sales
    if filter_date == "Today":
        filtered_sales = [s for s in filtered_sales if s['date'].startswith('2025-06-23')]
    elif filter_date == "This Week":
        # Simplified - just this month for demo
        filtered_sales = [s for s in filtered_sales if s['date'].startswith('2025-06')]
    elif filter_date == "This Month":
        filtered_sales = [s for s in filtered_sales if s['date'].startswith('2025-06')]

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

            with col2:
                cash_received = sale.get('cash_received') or sale.get('amount', 0)
                st.write(f"**Cash Received:** ₹{cash_received:,.2f}")
                st.write(f"**Room:** {sale.get('room_number', 'N/A')}")
                st.write(f"**Created by:** {sale.get('created_by', 'Unknown')}")

            if sale.get('description'):
                st.write(f"**Description:** {sale['description']}")

            # Admin actions
            if user_role == 'Admin':
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Edit", key=f"edit_{sale['id']}"):
                        with st.form(f"edit_sale_{sale['id']}"):
                            new_amount = st.number_input("Amount", value=sale['amount'], min_value=0.0)
                            new_cash_received = st.number_input("Cash Received", value=sale.get('cash_received', sale['amount']), min_value=0.0)
                            if st.form_submit_button("Update Sale"):
                                for s in sales:
                                    if s['id'] == sale['id']:
                                        s['amount'] = new_amount
                                        s['cash_received'] = new_cash_received
                                        break
                                save_data('sales.json', sales, selected_hotel)
                                st.success("Sale updated!")
                                st.rerun()

                with col2:
                    if st.button(f"Delete", key=f"delete_{sale['id']}", type="secondary"):
                        sales = [s for s in sales if s['id'] != sale['id']]
                        save_data('sales.json', sales, selected_hotel)
                        st.success("Sale deleted!")
                        st.rerun()

# Cash handover section
st.markdown("---")
st.markdown("### Cash Handover")

if cash_sales:
    total_cash_to_handover = sum(sale.get('cash_received', sale['amount']) for sale in cash_sales)
    st.info(f"Total cash to handover: ₹{total_cash_to_handover:,.2f}")

    with st.form("cash_handover_form"):
        col1, col2 = st.columns(2)

        with col1:
            handover_amount = st.number_input("Handover Amount", value=float(total_cash_to_handover), min_value=0.0)
            received_by = st.text_input("Received By", placeholder="Name of person receiving cash")

        with col2:
            handover_date = st.date_input("Handover Date")
            notes = st.text_area("Notes", placeholder="Any additional notes")

        if st.form_submit_button("Record Cash Handover"):
            if received_by:
                # Here you could save handover records to a separate file
                st.success(f"Cash handover of ₹{handover_amount:,.2f} recorded for {received_by}")
            else:
                st.error("Please specify who received the cash")
else:
    st.info("No cash sales to handover")
