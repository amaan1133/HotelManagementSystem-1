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

st.title("💸 Bad Debt Management")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
bad_debts = load_data('bad_debts.json', selected_hotel)
sales = load_data('sales.json', selected_hotel)

# Overview
st.markdown("### Bad Debt Overview")

total_bad_debt = sum(debt['amount'] for debt in bad_debts)
this_month_bad_debt = sum(debt['amount'] for debt in bad_debts if debt['date'].startswith('2025-06'))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Bad Debt", f"₹{total_bad_debt:,.2f}")
with col2:
    st.metric("This Month", f"₹{this_month_bad_debt:,.2f}")
with col3:
    st.metric("Total Records", len(bad_debts))

st.markdown("---")

# Add new bad debt (Admin only)
if user_role == 'Admin':
    st.markdown("### Add Bad Debt Record")

    with st.form("add_bad_debt_form"):
        col1, col2 = st.columns(2)

        with col1:
            customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
            amount = st.number_input("Amount", min_value=0.0, step=100.0)

        with col2:
            reason = st.text_area("Reason", placeholder="Reason for bad debt write-off")
            reference_id = st.text_input("Reference ID", placeholder="Original invoice/due ID")

        if st.form_submit_button("Add Bad Debt Record", type="primary"):
            if customer_name and amount > 0 and reason:
                new_bad_debt = {
                    'id': generate_id(),
                    'date': get_current_datetime(),
                    'customer_name': customer_name,
                    'amount': amount,
                    'reason': reason,
                    'reference_id': reference_id,
                    'created_by': st.session_state.get('username', 'Unknown')
                }
                bad_debts.append(new_bad_debt)
                save_data('bad_debts.json', bad_debts, selected_hotel)
                st.success("Bad debt record added successfully!")
                st.rerun()
            else:
                st.error("Customer name, amount, and reason are required")

st.markdown("---")

# Bad debt records
st.markdown("### Bad Debt Records")

if bad_debts:
    # Filter
    filter_month = st.selectbox("Filter by Month", ["All", "This Month", "Last Month"])

    filtered_debts = bad_debts
    if filter_month == "This Month":
        filtered_debts = [d for d in filtered_debts if d['date'].startswith('2025-06')]
    elif filter_month == "Last Month":
        filtered_debts = [d for d in filtered_debts if d['date'].startswith('2025-05')]

    for debt in filtered_debts:
        with st.expander(f"#{debt['id']} - {debt['customer_name']} - ₹{debt['amount']:,.2f}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {debt['date']}")
                st.write(f"**Customer:** {debt['customer_name']}")
                st.write(f"**Amount:** ₹{debt['amount']:,.2f}")
                st.write(f"**Created by:** {debt.get('created_by', 'Unknown')}")

            with col2:
                st.write(f"**Reference ID:** {debt.get('reference_id', 'N/A')}")
                if debt.get('original_due_id'):
                    st.write(f"**Original Due ID:** {debt['original_due_id']}")

            st.write(f"**Reason:** {debt['reason']}")

            # Admin actions
            if user_role == 'Admin':
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Edit", key=f"edit_{debt['id']}"):
                        with st.form(f"edit_debt_{debt['id']}"):
                            new_amount = st.number_input("Amount", value=debt['amount'], min_value=0.0)
                            new_reason = st.text_area("Reason", value=debt['reason'])
                            if st.form_submit_button("Update Record"):
                                for d in bad_debts:
                                    if d['id'] == debt['id']:
                                        d['amount'] = new_amount
                                        d['reason'] = new_reason
                                        break
                                save_data('bad_debts.json', bad_debts, selected_hotel)
                                st.success("Bad debt record updated!")
                                st.rerun()

                with col2:
                    if st.button(f"Delete", key=f"delete_{debt['id']}", type="secondary"):
                        bad_debts = [b for b in bad_debts if b['id'] != debt['id']]
                        save_data('bad_debts.json', bad_debts, selected_hotel)
                        st.success("Bad debt record deleted!")
                        st.rerun()

# Summary analysis
st.markdown("---")
st.markdown("### Bad Debt Analysis")

if bad_debts:
    # Customer analysis
    customer_debts = {}
    for debt in bad_debts:
        customer = debt['customer_name']
        customer_debts[customer] = customer_debts.get(customer, 0) + debt['amount']

    if customer_debts:
        st.markdown("**Top Bad Debt Customers:**")
        sorted_customers = sorted(customer_debts.items(), key=lambda x: x[1], reverse=True)[:5]
        for customer, amount in sorted_customers:
            st.write(f"• {customer}: ₹{amount:,.2f}")

    # Monthly trend
    monthly_debts = {}
    for debt in bad_debts:
        month = debt['date'][:7]  # YYYY-MM
        monthly_debts[month] = monthly_debts.get(month, 0) + debt['amount']

    if len(monthly_debts) > 1:
        st.markdown("**Monthly Bad Debt Trend:**")
        for month, amount in sorted(monthly_debts.items()):
            st.write(f"• {month}: ₹{amount:,.2f}")
else:
    st.info("No bad debt records found")

# Room number (optional) - dynamic based on selected hotel
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
rooms_list = load_data('rooms.json', selected_hotel)

# Convert list to dictionary if needed
if isinstance(rooms_list, list):
    rooms = {}
    for room in rooms_list:
        if isinstance(room, dict) and 'room_number' in room:
            rooms[room['room_number']] = room
else:
    rooms = rooms_list if rooms_list else {}

all_rooms = [f"Room {k}" for k in sorted(rooms.keys(), key=lambda x: int(x))] if rooms else []
room_options = ["None"] + all_rooms
room_number = st.selectbox("Room Number (if applicable)", room_options)