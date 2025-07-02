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

st.title("📄 Bill Upload")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
uploaded_bills = load_data('uploaded_bills.json', selected_hotel)

# Overview
st.markdown("### Uploaded Bills Overview")

total_bills = len(uploaded_bills)
pending_bills = len([b for b in uploaded_bills if b['status'] == 'Pending'])
reviewed_bills = len([b for b in uploaded_bills if b['status'] == 'Reviewed'])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Bills", total_bills)
with col2:
    st.metric("Pending Review", pending_bills)
with col3:
    st.metric("Reviewed", reviewed_bills)

st.markdown("---")

# Upload new bill
st.markdown("### Upload New Bill")

with st.form("upload_bill_form"):
    col1, col2 = st.columns(2)

    with col1:
        bill_type = st.selectbox("Bill Type", ["Expense Bill", "Purchase Bill", "Service Bill", "Utility Bill", "Other"])
        vendor_name = st.text_input("Vendor/Supplier Name", placeholder="Enter vendor name")
        amount = st.number_input("Bill Amount", min_value=0.0, step=100.0)

    with col2:
        bill_date = st.date_input("Bill Date")
        bill_number = st.text_input("Bill Number", placeholder="Enter bill number")
        description = st.text_area("Description", placeholder="Description of the bill")

    # File upload
    uploaded_file = st.file_uploader("Upload Bill Image/PDF", type=['jpg', 'jpeg', 'png', 'pdf'])

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

    if st.form_submit_button("Upload Bill", type="primary"):
        if vendor_name and amount > 0:
            file_info = None
            if uploaded_file:
                file_info = {
                    'filename': uploaded_file.name,
                    'size': uploaded_file.size,
                    'type': uploaded_file.type
                }

            new_bill = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'bill_type': bill_type,
                'vendor_name': vendor_name,
                'amount': amount,
                'bill_date': str(bill_date),
                'bill_number': bill_number,
                'description': description,
                'file_info': file_info,
                'status': 'Pending',
                'uploaded_by': st.session_state.get('username', 'Unknown')
            }
            uploaded_bills.append(new_bill)
            save_data('uploaded_bills.json', uploaded_bills, selected_hotel)
            st.success("Bill uploaded successfully!")
            st.rerun()
        else:
            st.error("Vendor name and amount are required")

st.markdown("---")

# Bills list
st.markdown("### Uploaded Bills")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
uploaded_bills = load_data('uploaded_bills.json', selected_hotel)

if uploaded_bills:
    # Filter
    filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Reviewed", "Approved"])
    filter_type = st.selectbox("Filter by Type", ["All"] + ["Expense Bill", "Purchase Bill", "Service Bill", "Utility Bill", "Other"])

    filtered_bills = uploaded_bills
    if filter_status != "All":
        filtered_bills = [b for b in filtered_bills if b['status'] == filter_status]
    if filter_type != "All":
        filtered_bills = [b for b in filtered_bills if b['bill_type'] == filter_type]

    for bill in filtered_bills:
        with st.expander(f"#{bill['id']} - {bill['vendor_name']} - ₹{bill['amount']:,.2f}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Upload Date:** {bill['date']}")
                st.write(f"**Bill Type:** {bill['bill_type']}")
                st.write(f"**Vendor:** {bill['vendor_name']}")
                st.write(f"**Amount:** ₹{bill['amount']:,.2f}")
                st.write(f"**Status:** {bill['status']}")

            with col2:
                st.write(f"**Bill Date:** {bill['bill_date']}")
                st.write(f"**Bill Number:** {bill.get('bill_number', 'N/A')}")
                st.write(f"**Uploaded by:** {bill.get('uploaded_by', 'Unknown')}")
                if bill.get('file_info'):
                    st.write(f"**File:** {bill['file_info']['filename']}")

            if bill.get('description'):
                st.write(f"**Description:** {bill['description']}")

            # Admin actions
            if user_role == 'Admin':
                col1, col2, col3 = st.columns(3)

                with col1:
                    if bill['status'] == 'Pending' and st.button(f"Mark Reviewed", key=f"review_{bill['id']}"):
                        for b in uploaded_bills:
                            if b['id'] == bill['id']:
                                b['status'] = 'Reviewed'
                                b['reviewed_date'] = get_current_datetime()
                                break
                        save_data('uploaded_bills.json', uploaded_bills, selected_hotel)
                        st.success("Bill marked as reviewed!")
                        st.rerun()

                with col2:
                    if st.button(f"Edit", key=f"edit_{bill['id']}"):
                        with st.form(f"edit_bill_{bill['id']}"):
                            new_amount = st.number_input("Amount", value=bill['amount'], min_value=0.0)
                            new_status = st.selectbox("Status", ["Pending", "Reviewed", "Approved"], 
                                                    index=["Pending", "Reviewed", "Approved"].index(bill['status']))
                            if st.form_submit_button("Update Bill"):
                                for b in uploaded_bills:
                                    if b['id'] == bill['id']:
                                        b['amount'] = new_amount
                                        b['status'] = new_status
                                        break
                                save_data('uploaded_bills.json', uploaded_bills, selected_hotel)
                                st.success("Bill updated!")
                                st.rerun()

                with col3:
                    if st.button(f"Delete", key=f"delete_{bill['id']}", type="secondary"):
                        uploaded_bills = [b for b in uploaded_bills if b['id'] != bill['id']]
                        save_data('uploaded_bills.json', uploaded_bills, selected_hotel)
                        st.success("Bill deleted!")
                        st.rerun()
else:
    st.info("No bills uploaded yet")

# Admin dashboard section
if user_role == 'Admin':
    st.markdown("---")
    st.markdown("### Admin Bill Dashboard")

    # Load data
    selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
    uploaded_bills = load_data('uploaded_bills.json', selected_hotel)

    if uploaded_bills:
        # Bills by type
        bill_types = {}
        for bill in uploaded_bills:
            bill_type = bill['bill_type']
            bill_types[bill_type] = bill_types.get(bill_type, 0) + bill['amount']

        st.markdown("**Bills by Type:**")
        for bill_type, amount in bill_types.items():
            st.write(f"• {bill_type}: ₹{amount:,.2f}")

        # Recent uploads
        st.markdown("**Recent Uploads:**")
        recent_bills = sorted(uploaded_bills, key=lambda x: x['date'], reverse=True)[:5]
        for bill in recent_bills:
            st.write(f"• {bill['vendor_name']} - ₹{bill['amount']:,.2f} ({bill['status']})")