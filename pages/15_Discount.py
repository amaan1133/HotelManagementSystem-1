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

st.title("🏷️ Discount Management")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
discounts = load_data('discounts.json', selected_hotel)
sales = load_data('sales.json', selected_hotel)

# Overview
st.markdown("### Discount Overview")

total_discounts = sum(discount['amount'] for discount in discounts)
this_month_discounts = sum(discount['amount'] for discount in discounts if discount['date'].startswith('2025-06'))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Discounts", f"₹{total_discounts:,.2f}")
with col2:
    st.metric("This Month", f"₹{this_month_discounts:,.2f}")
with col3:
    st.metric("Total Records", len(discounts))

st.markdown("---")

# Add new discount
st.markdown("### Add Discount Record")

with st.form("add_discount_form"):
    col1, col2 = st.columns(2)

    with col1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        amount = st.number_input("Discount Amount", min_value=0.0, step=100.0)
        discount_type = st.selectbox("Discount Type", 
                                   ["Senior Citizen", "Staff Discount", "Corporate Rate", 
                                    "Loyalty Discount", "Group Booking", "Promotional", "Other"])

    with col2:
        reason = st.text_area("Reason", placeholder="Reason for discount")
        reference_id = st.text_input("Reference ID", placeholder="Original invoice/booking ID")
        percentage = st.number_input("Discount Percentage", min_value=0.0, max_value=100.0, step=5.0)
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

    if st.form_submit_button("Add Discount Record", type="primary"):
        if customer_name and amount > 0:
            new_discount = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'customer_name': customer_name,
                'amount': amount,
                'original_amount': amount,
                'discount_type': discount_type,
                'reason': reason or f"{discount_type} discount applied",
                'reference_id': reference_id,
                'percentage': percentage,
                'created_by': st.session_state.get('username', 'Unknown')
            }
            discounts.append(new_discount)
            save_data('discounts.json', discounts, selected_hotel)
            st.success("Discount record added successfully!")
            st.rerun()
        else:
            st.error("Customer name and discount amount are required")

st.markdown("---")

# Discount records
st.markdown("### Discount Records")

if discounts:
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox("Filter by Type", ["All"] + 
                                 ["Senior Citizen", "Staff Discount", "Corporate Rate", 
                                  "Loyalty Discount", "Group Booking", "Promotional", "Other"])
    with col2:
        filter_month = st.selectbox("Filter by Month", ["All", "This Month", "Last Month"])

    filtered_discounts = discounts
    if filter_type != "All":
        filtered_discounts = [d for d in filtered_discounts if d['discount_type'] == filter_type]

    if filter_month == "This Month":
        filtered_discounts = [d for d in filtered_discounts if d['date'].startswith('2025-06')]
    elif filter_month == "Last Month":
        filtered_discounts = [d for d in filtered_discounts if d['date'].startswith('2025-05')]

    for discount in filtered_discounts:
        with st.expander(f"#{discount['id']} - {discount['customer_name']} - ₹{discount['amount']:,.2f}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {discount['date']}")
                st.write(f"**Customer:** {discount['customer_name']}")
                st.write(f"**Amount:** ₹{discount['amount']:,.2f}")
                st.write(f"**Type:** {discount['discount_type']}")
                st.write(f"**Created by:** {discount.get('created_by', 'Unknown')}")

            with col2:
                st.write(f"**Percentage:** {discount.get('percentage', 0):.1f}%")
                st.write(f"**Reference ID:** {discount.get('reference_id', 'N/A')}")
                if discount.get('original_due_id'):
                    st.write(f"**Original Due ID:** {discount['original_due_id']}")

            st.write(f"**Reason:** {discount['reason']}")

            # Admin actions
            if user_role == 'Admin':
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Edit", key=f"edit_{discount['id']}"):
                        with st.form(f"edit_discount_{discount['id']}"):
                            new_amount = st.number_input("Amount", value=discount['amount'], min_value=0.0)
                            new_type = st.selectbox("Type", 
                                                  ["Senior Citizen", "Staff Discount", "Corporate Rate", 
                                                   "Loyalty Discount", "Group Booking", "Promotional", "Other"],
                                                  index=["Senior Citizen", "Staff Discount", "Corporate Rate", 
                                                        "Loyalty Discount", "Group Booking", "Promotional", "Other"].index(discount['discount_type']))
                            new_reason = st.text_area("Reason", value=discount['reason'])
                            if st.form_submit_button("Update Record"):
                                for d in discounts:
                                    if d['id'] == discount['id']:
                                        d['amount'] = new_amount
                                        d['discount_type'] = new_type
                                        d['reason'] = new_reason
                                        break
                                save_data('discounts.json', discounts, selected_hotel)
                                st.success("Discount record updated!")
                                st.rerun()

                with col2:
                    if st.button(f"Delete", key=f"delete_{discount['id']}", type="secondary"):
                        discounts = [d for d in discounts if d['id'] != discount['id']]
                        save_data('discounts.json', discounts, selected_hotel)
                        st.success("Discount record deleted!")
                        st.rerun()

# Summary analysis
st.markdown("---")
st.markdown("### Discount Analysis")

if discounts:
    # Type analysis
    type_discounts = {}
    for discount in discounts:
        dtype = discount['discount_type']
        type_discounts[dtype] = type_discounts.get(dtype, 0) + discount['amount']

    if type_discounts:
        st.markdown("**Discounts by Type:**")
        sorted_types = sorted(type_discounts.items(), key=lambda x: x[1], reverse=True)
        for dtype, amount in sorted_types:
            st.write(f"• {dtype}: ₹{amount:,.2f}")

    # Customer analysis
    customer_discounts = {}
    for discount in discounts:
        customer = discount['customer_name']
        customer_discounts[customer] = customer_discounts.get(customer, 0) + discount['amount']

    if customer_discounts:
        st.markdown("**Top Discount Recipients:**")
        sorted_customers = sorted(customer_discounts.items(), key=lambda x: x[1], reverse=True)[:5]
        for customer, amount in sorted_customers:
            st.write(f"• {customer}: ₹{amount:,.2f}")
else:
    st.info("No discount records found")