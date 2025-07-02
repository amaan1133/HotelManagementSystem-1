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

st.title("💰 Outstanding Dues")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
outstanding_dues = load_data('outstanding_dues.json', selected_hotel)
sales = load_data('sales.json', selected_hotel)

# Overview
st.markdown("### Outstanding Dues Overview")

total_outstanding = sum(due['amount'] for due in outstanding_dues if due['status'] == 'Pending')
received_today = sum(due['amount'] for due in outstanding_dues if due['status'] == 'Received' and due.get('received_date', '').startswith('2025-06-23'))
total_received = sum(due['amount'] for due in outstanding_dues if due['status'] == 'Received')

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Outstanding", f"₹{total_outstanding:,.2f}")
with col2:
    st.metric("Received Today", f"₹{received_today:,.2f}")
with col3:
    st.metric("Total Received", f"₹{total_received:,.2f}")

st.markdown("---")

# Add new outstanding due
st.markdown("### Add Outstanding Due")

with st.form("add_due_form"):
    col1, col2 = st.columns(2)

    with col1:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        amount = st.number_input("Amount", min_value=0.0, step=100.0)
        due_type = st.selectbox("Due Type", ["Room Bill", "Service Bill", "Event Bill", "Other"])

    with col2:
        due_date = st.date_input("Due Date")
        description = st.text_area("Description", placeholder="Description of the due")
        phone = st.text_input("Phone Number", placeholder="Customer phone")

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

    if st.form_submit_button("Add Outstanding Due", type="primary"):
        if customer_name and amount > 0:
            new_due = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'customer_name': customer_name,
                'amount': amount,
                'due_type': due_type,
                'due_date': str(due_date),
                'description': description,
                'phone': phone,
                'status': 'Pending',
                'created_by': st.session_state.get('username', 'Unknown')
            }
            outstanding_dues.append(new_due)
            save_data('outstanding_dues.json', outstanding_dues, selected_hotel)
            st.success("Outstanding due added successfully!")
            st.rerun()
        else:
            st.error("Customer name and amount are required")

st.markdown("---")

# Outstanding dues list
st.markdown("### Outstanding Dues Records")

if outstanding_dues:
    # Filter
    filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Received"])

    filtered_dues = outstanding_dues
    if filter_status != "All":
        filtered_dues = [d for d in filtered_dues if d['status'] == filter_status]

    for due in filtered_dues:
        due_date = due['date'][:10] if due['date'] else 'N/A'
        with st.expander(f"#{due['id']} - {due['customer_name']} - ₹{due['amount']:,.2f} - {due_date}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {due['date']}")
                st.write(f"**Customer:** {due['customer_name']}")
                st.write(f"**Amount:** ₹{due['amount']:,.2f}")
                st.write(f"**Type:** {due['due_type']}")
                st.write(f"**Status:** {due['status']}")

            with col2:
                st.write(f"**Due Date:** {due['due_date']}")
                st.write(f"**Phone:** {due.get('phone', 'N/A')}")
                st.write(f"**Created by:** {due.get('created_by', 'Unknown')}")
                if due.get('received_date'):
                    st.write(f"**Received Date:** {due['received_date']}")

            if due.get('description'):
                st.write(f"**Description:** {due['description']}")

            # Show payment history if exists
            if due.get('payment_history'):
                st.markdown("**Payment History:**")
                for payment in due['payment_history']:
                    st.write(f"• {payment['date']}: ₹{payment['amount']:,.2f} via {payment['payment_type']} by {payment.get('processed_by', 'Unknown')}")
                    if payment.get('notes'):
                        st.write(f"  Notes: {payment['notes']}")

            # Actions
            col1, col2, col3 = st.columns(3)

            with col1:
                if due['status'] == 'Pending':
                    with st.form(f"pay_due_{due['id']}"):
                        st.write(f"**Outstanding Amount:** ₹{due['amount']:,.2f}")

                        payment_amount = st.number_input("Payment Amount", 
                                                       min_value=0.0, 
                                                       max_value=float(due['amount']), 
                                                       value=float(due['amount']),
                                                       step=100.0,
                                                       key=f"payment_amount_{due['id']}")

                        payment_type = st.selectbox("Payment Type", 
                                                  ["Cash", "Account", "Bad Debt", "Discount", "Complementary"], 
                                                  key=f"payment_type_{due['id']}")

                        notes = st.text_area("Notes", placeholder="Any notes for this payment", key=f"notes_{due['id']}")

                        if st.form_submit_button("Process Payment"):
                            if payment_amount <= 0:
                                st.error("Payment amount must be greater than 0")
                            else:
                                # Calculate remaining amount
                                remaining_amount = due['amount'] - payment_amount

                                # Add payment to sales (except for bad debt, discount, complementary)
                                selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                                if payment_type in ["Cash", "Account"]:
                                    sales = load_data('sales.json',selected_hotel)
                                    new_sale = {
                                        'id': generate_id(),
                                        'date': get_current_datetime(),
                                        'type': 'Outstanding Due Collection',
                                        'amount': payment_amount,
                                        'payment_type': payment_type,
                                        'customer_name': due['customer_name'],
                                        'description': f"Partial payment of outstanding due #{due['id']}",
                                        'status': 'Completed',
                                        'created_by': st.session_state.get('username', 'Unknown'),
                                        'notes': notes
                                    }
                                    sales.append(new_sale)
                                    save_data('sales.json', sales, selected_hotel)

                                # Handle different payment types
                                if payment_type == "Bad Debt":
                                    # Add to bad debt records
                                    bad_debts = load_data('bad_debts.json', selected_hotel)
                                    new_bad_debt = {
                                        'id': generate_id(),
                                        'date': get_current_datetime(),
                                        'customer_name': due['customer_name'],
                                        'amount': payment_amount,
                                        'original_due_id': due['id'],
                                        'reason': notes or 'Outstanding due written off as bad debt',
                                        'created_by': st.session_state.get('username', 'Unknown')
                                    }
                                    bad_debts.append(new_bad_debt)
                                    save_data('bad_debts.json', bad_debts, selected_hotel)

                                elif payment_type == "Discount":
                                    # Add to discount records
                                    discounts = load_data('discounts.json', selected_hotel)
                                    new_discount = {
                                        'id': generate_id(),
                                        'date': get_current_datetime(),
                                        'customer_name': due['customer_name'],
                                        'amount': payment_amount,
                                        'original_due_id': due['id'],
                                        'reason': notes or 'Discount applied to outstanding due',
                                        'created_by': st.session_state.get('username', 'Unknown')
                                    }
                                    discounts.append(new_discount)
                                    save_data('discounts.json', discounts, selected_hotel)

                                elif payment_type == "Complementary":
                                    # Add to complementary records
                                    complementary_records = load_data('complementary_records.json', selected_hotel)
                                    new_comp = {
                                        'id': generate_id(),
                                        'date': get_current_datetime(),
                                        'customer_name': due['customer_name'],
                                        'amount': payment_amount,
                                        'original_due_id': due['id'],
                                        'reason': notes or 'Outstanding due made complementary',
                                        'created_by': st.session_state.get('username', 'Unknown')
                                    }
                                    complementary_records.append(new_comp)
                                    save_data('complementary_records.json', complementary_records, selected_hotel)

                                # Update the outstanding due
                                for d in outstanding_dues:
                                    if d['id'] == due['id']:
                                        if remaining_amount <= 0:
                                            # Fully paid
                                            d['status'] = 'Received'
                                            d['received_date'] = get_current_datetime()
                                            d['payment_method'] = payment_type
                                            d['final_amount_paid'] = payment_amount
                                        else:
                                            # Partial payment - reduce the amount
                                            d['amount'] = remaining_amount
                                            # Add payment history
                                            if 'payment_history' not in d:
                                                d['payment_history'] = []
                                            d['payment_history'].append({
                                                'date': get_current_datetime(),
                                                'amount': payment_amount,
                                                'payment_type': payment_type,
                                                'notes': notes,
                                                'processed_by': st.session_state.get('username', 'Unknown')
                                            })
                                        break

                                save_data('outstanding_dues.json', outstanding_dues, selected_hotel)

                                if remaining_amount <= 0:
                                    st.success(f"Outstanding due fully settled with {payment_type}!")
                                else:
                                    st.success(f"Partial payment of ₹{payment_amount:,.2f} processed. Remaining: ₹{remaining_amount:,.2f}")

                                st.rerun()

            with col2:
                if user_role == 'Admin' and st.button(f"Edit", key=f"edit_{due['id']}"):
                    with st.form(f"edit_due_{due['id']}"):
                        new_amount = st.number_input("Amount", value=due['amount'], min_value=0.0)
                        new_status = st.selectbox("Status", ["Pending", "Received"], 
                                                index=["Pending", "Received"].index(due['status']))
                        if st.form_submit_button("Update Due"):
                            for d in outstanding_dues:
                                if d['id'] == due['id']:
                                    d['amount'] = new_amount
                                    d['status'] = new_status
                                    break
                            selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                            save_data('outstanding_dues.json', outstanding_dues, selected_hotel)
                            st.success("Due updated!")
                            st.rerun()

            with col3:
                if user_role == 'Admin' and st.button(f"Delete", key=f"delete_{due['id']}", type="secondary"):
                    selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                    outstanding_dues = [d for d in outstanding_dues if d['id'] != due['id']]
                    save_data('outstanding_dues.json', outstanding_dues, selected_hotel)
                    st.success("Due deleted!")
                    st.rerun()
else:
    st.info("No outstanding dues found")

# Export functionality
if user_role == 'Admin':
    st.markdown("---")
    st.markdown("### 📥 Download Options")

    col1, col2 = st.columns(2)

    with col1:
        if outstanding_dues:
            if st.button("📊 Export Outstanding Dues Data"):
                df = pd.DataFrame(outstanding_dues)
                st.download_button(
                    label="Download Outstanding Dues CSV",
                    data=df.to_csv(index=False),
                    file_name=f"outstanding_dues_{get_current_datetime()[:10]}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No outstanding dues data to export")

    with col2:
        if st.button("🎯 Go to Download Center"):
            st.switch_page("pages/18_Data_Download.py")