import streamlit as st
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication
from utils.database_data_manager import load_data, save_data, generate_id, get_current_datetime, add_record
import pandas as pd
import plotly.express as px

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

# All users can add sales data, admin can edit/delete
user_role = st.session_state.get('user_role', 'User')

st.title("💰 Sales Management")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
sales = load_data('sales.json', selected_hotel)
rooms_list = load_data('rooms.json', selected_hotel)
outstanding_dues = load_data('outstanding_dues.json', selected_hotel)
advance_payments = load_data('advance_payments.json', selected_hotel)

# Ensure sales is a list
if not isinstance(sales, list):
    sales = []
    save_data('sales.json', sales, selected_hotel)

# Convert list to dictionary if needed
if isinstance(rooms_list, list):
    rooms = {}
    for room in rooms_list:
        if isinstance(room, dict) and 'room_number' in room:
            rooms[room['room_number']] = room
else:
    rooms = rooms_list if rooms_list else {}

# Date filtering at the top
from datetime import datetime, timedelta

st.markdown("### 📅 Filter by Date")

col1, col2, col3 = st.columns(3)

with col1:
    date_filter = st.selectbox("Filter by Date", ["All Time", "Today", "This Week", "This Month", "This Year", "Custom Range"])

with col2:
    if date_filter == "Custom Range":
        start_date = st.date_input("Start Date", value=datetime(2025, 1, 1))
    else:
        start_date = None

with col3:
    if date_filter == "Custom Range":
        end_date = st.date_input("End Date", value=datetime.now())
    else:
        end_date = None

# Function to filter sales by date
def filter_sales_by_date(sales_data, date_filter, start_date=None, end_date=None):
    if date_filter == "All Time":
        return sales_data

    today = datetime.now()
    filtered_data = []

    for sale in sales_data:
        try:
            # Use the sale date for filtering
            sale_date = sale['date'][:10] if sale['date'] else None
            if not sale_date:
                continue
            
            sale_datetime = datetime.strptime(sale_date, '%Y-%m-%d')
            
            if date_filter == "Today":
                if sale_datetime.date() == today.date():
                    filtered_data.append(sale)
            elif date_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                if sale_datetime.date() >= week_start.date():
                    filtered_data.append(sale)
            elif date_filter == "This Month":
                if sale_datetime.month == today.month and sale_datetime.year == today.year:
                    filtered_data.append(sale)
            elif date_filter == "This Year":
                if sale_datetime.year == today.year:
                    filtered_data.append(sale)
            elif date_filter == "Custom Range" and start_date and end_date:
                if start_date <= sale_datetime.date() <= end_date:
                    filtered_data.append(sale)
        except ValueError:
            # Skip records with invalid dates
            continue

    return filtered_data

# Apply date filter to sales data
filtered_sales_overview = filter_sales_by_date(sales, date_filter, start_date, end_date)

# Sales overview with filtered data
st.markdown("### Sales Overview")

# Show period summary
period_text = {
    "All Time": "All Time",
    "Today": "Today",
    "This Week": "This Week", 
    "This Month": "This Month",
    "This Year": "This Year",
    "Custom Range": f"{start_date} to {end_date}" if start_date and end_date else "Custom Range"
}
st.markdown(f"**Showing data for: {period_text[date_filter]}**")

# Calculate totals from filtered data
total_sales = sum(sale['amount'] for sale in filtered_sales_overview)
cash_sales = sum(sale['amount'] for sale in filtered_sales_overview if sale['payment_type'] == 'Cash')
account_sales = sum(sale['amount'] for sale in filtered_sales_overview if sale['payment_type'] == 'Account')
outstanding_amount = sum(due['amount'] for due in outstanding_dues if due['status'] == 'Pending')
advance_amount = sum(ap['amount'] for ap in advance_payments if ap['status'] == 'Pending')

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Sales", f"₹{total_sales:,.2f}")
with col2:
    st.metric("Cash Sales", f"₹{cash_sales:,.2f}")
with col3:
    st.metric("Account Sales", f"₹{account_sales:,.2f}")
with col4:
    st.metric("Outstanding Dues", f"₹{outstanding_amount:,.2f}")
with col5:
    st.metric("Advance Payments", f"₹{advance_amount:,.2f}")

st.markdown("---")

# Add new sale
st.markdown("### Add New Sale")

with st.form("add_sale_form"):
    col1, col2 = st.columns(2)

    with col1:
        # Add custom date selection for historical entries
        sale_date = st.date_input("Sale Date", value=datetime.now().date(), 
                                help="Select the date for this sale")
        sale_type = st.selectbox("Sale Type", ["Room Booking", "Food & Beverage", "Restaurant", "Laundry", "Other Services"])
        amount = st.number_input("Amount", min_value=0.0, step=100.0, format="%.2f")
        payment_type = st.selectbox("Payment Type", ["Cash", "Account", "Outstanding Due", "Advance Cash"])

    with col2:
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        description = st.text_area("Description", placeholder="Sale description")
        # Get all rooms for selected hotel (regardless of occupancy status)
        if isinstance(rooms, dict):
            all_rooms = [f"Room {k}" for k in sorted(rooms.keys(), key=lambda x: int(x))]
        elif isinstance(rooms, list):
            # If rooms is a list of room objects, extract room numbers
            all_rooms = [f"Room {room.get('room_number', room.get('id', i+101))}" for i, room in enumerate(rooms)]
        else:
            # Default room numbers based on selected hotel
            if selected_hotel == 'hotel1':
                all_rooms = [f"Room {i}" for i in range(101, 109)]  # 101-108
            else:  # hotel2
                all_rooms = [f"Room {i}" for i in ['101', '102', '103', '201', '202', '203', '301', '302', '303', '304', '305', '401', '402', '403', '501', '502', '503']]
        room_number = st.selectbox("Room Number (if applicable)", 
                                 ["None"] + all_rooms)

    submit_sale = st.form_submit_button("Add Sale", type="primary")

    if submit_sale:
        if not customer_name or amount <= 0:
            st.error("Customer name and valid amount are required")
        else:
            # Handle different payment types
            if payment_type == "Outstanding Due":
                # Add to outstanding dues
                new_due = {
                    'id': generate_id(),
                    'date': sale_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'customer_name': customer_name,
                    'amount': amount,
                    'due_type': sale_type,
                    'due_date': get_current_datetime()[:10],
                    'description': description,
                    'phone': '',
                    'status': 'Pending',
                    'created_by': st.session_state.get('username', 'Unknown')
                }
                outstanding_dues.append(new_due)
                save_data('outstanding_dues.json', outstanding_dues, selected_hotel)
                st.success(f"Outstanding due of ₹{amount:,.2f} added successfully!")

            elif payment_type == "Advance Cash":
                # Add to advance payments
                new_advance = {
                    'id': generate_id(),
                    'date': sale_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'customer_name': customer_name,
                    'customer_contact': '',
                    'customer_email': '',
                    'room_number': room_number if room_number != "None" else None,
                    'booking_date': None,
                    'amount': amount,
                    'payment_method': 'Cash',
                    'cheque_number': '',
                    'cheque_date': None,
                    'transaction_id': '',
                    'purpose': sale_type,
                    'notes': description,
                    'status': 'Pending',
                    'created_by': st.session_state.get('username', 'Unknown')
                }
                advance_payments.append(new_advance)
                save_data('advance_payments.json', advance_payments, selected_hotel)
                st.success(f"Advance payment of ₹{amount:,.2f} added successfully!")

            else:
                # Regular sales (Cash/Account)
                new_sale = {
                    'id': generate_id(),
                    'date': sale_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': sale_type,
                    'amount': amount,
                    'payment_type': payment_type,
                    'customer_name': customer_name,
                    'description': description,
                    'room_number': room_number if room_number != "None" else None,
                    'status': 'Pending' if payment_type == 'Account' else 'Completed',
                    'created_by': st.session_state.get('username', 'Unknown')
                }

                # Add to sales data and save
                if add_record('sales.json', new_sale, selected_hotel):
                    st.success(f"Sale of ₹{amount:,.2f} added to {payment_type} sales successfully!")
                else:
                    st.error("Failed to add sale record")
                    
                # Force reload of sales data to ensure it appears immediately
                st.rerun()

            # If room booking, update room status (for all payment types)
            if sale_type == "Room Booking" and room_number != "None":
                room_num = room_number.split()[1]
                if room_num in rooms:
                    rooms[room_num]['status'] = 'Occupied'
                    rooms[room_num]['current_guest'] = customer_name
                    rooms[room_num]['checkin_date'] = get_current_datetime()[:10]
                    save_data('rooms.json', rooms, selected_hotel)

            st.rerun()

st.markdown("---")

# Sales list and management
st.markdown("### Sales Records")

# Initialize filtered_sales
filtered_sales = []

if sales:
    # Apply date filter first
    filtered_sales = filter_sales_by_date(sales, date_filter, start_date, end_date)
    
    # Additional filter options
    st.markdown("#### Additional Filters")
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_type = st.selectbox("Filter by Type", ["All"] + list(set(sale['type'] for sale in filtered_sales)) if filtered_sales else ["All"])
    with col2:
        filter_payment = st.selectbox("Filter by Payment", ["All"] + list(set(sale['payment_type'] for sale in filtered_sales)) if filtered_sales else ["All"])
    with col3:
        filter_status = st.selectbox("Filter by Status", ["All", "Completed", "Pending"])

    # Apply additional filters
    if filter_type != "All":
        filtered_sales = [s for s in filtered_sales if s['type'] == filter_type]
    if filter_payment != "All":
        filtered_sales = [s for s in filtered_sales if s['payment_type'] == filter_payment]
    if filter_status != "All":
        filtered_sales = [s for s in filtered_sales if s['status'] == filter_status]
    
    # Show filtered results summary
    if date_filter != "All Time" or filter_type != "All" or filter_payment != "All" or filter_status != "All":
        filtered_total = sum(sale['amount'] for sale in filtered_sales)
        st.info(f"Showing {len(filtered_sales)} sales records totaling ₹{filtered_total:,.2f}")
    
    st.markdown("---")

    # Display sales
    for sale in filtered_sales:
        # Show original advance date for advance payments, regular date for others
        display_date = sale.get('original_advance_date', sale['date'][:10] if sale['date'] else 'N/A')
        with st.expander(f"#{sale['id']} - {sale['customer_name']} - ₹{sale['amount']:,.2f} - {display_date}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {sale['date']}")
                st.write(f"**Type:** {sale['type']}")
                st.write(f"**Amount:** ₹{sale['amount']:,.2f}")
                st.write(f"**Payment:** {sale['payment_type']}")

            with col2:
                st.write(f"**Customer:** {sale['customer_name']}")
                st.write(f"**Status:** {sale['status']}")
                st.write(f"**Room:** {sale.get('room_number', 'N/A')}")
                st.write(f"**Created by:** {sale.get('created_by', 'Unknown')}")

            if sale.get('description'):
                st.write(f"**Description:** {sale['description']}")

            # Admin actions
            if user_role == 'Admin':
                st.markdown("**Admin Actions:**")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if sale['status'] == 'Pending' and st.button(f"✅ Complete", key=f"complete_{sale['id']}"):
                        updated_sales = load_data('sales.json', selected_hotel)
                        for s in updated_sales:
                            if s['id'] == sale['id']:
                                s['status'] = 'Completed'
                                break
                        save_data('sales.json', updated_sales, selected_hotel)
                        st.success("Sale marked as completed!")
                        st.rerun()

                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_{sale['id']}"):
                        st.session_state[f"edit_mode_{sale['id']}"] = not st.session_state.get(f"edit_mode_{sale['id']}", False)
                        st.rerun()

                with col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{sale['id']}", type="secondary"):
                        st.session_state[f"confirm_delete_{sale['id']}"] = True
                        st.rerun()

                with col4:
                    if sale['status'] == 'Completed' and st.button(f"⏸️ Pending", key=f"pending_{sale['id']}"):
                        updated_sales = load_data('sales.json', selected_hotel)
                        for s in updated_sales:
                            if s['id'] == sale['id']:
                                s['status'] = 'Pending'
                                break
                        save_data('sales.json', updated_sales, selected_hotel)
                        st.success("Sale marked as pending!")
                        st.rerun()

                # Edit form
                if st.session_state.get(f"edit_mode_{sale['id']}", False):
                    with st.form(f"edit_sale_{sale['id']}"):
                        st.markdown("**Edit Sale Details:**")
                        edit_col1, edit_col2 = st.columns(2)
                        
                        with edit_col1:
                            new_amount = st.number_input("Amount", value=sale['amount'], min_value=0.0)
                            new_customer = st.text_input("Customer Name", value=sale['customer_name'])
                            new_payment_type = st.selectbox("Payment Type", ["Cash", "Account"], 
                                                          index=0 if sale['payment_type'] == 'Cash' else 1)
                        
                        with edit_col2:
                            new_type = st.selectbox("Sale Type", 
                                                  ["Room Booking", "Food & Beverage", "Restaurant", "Laundry", "Other Services"],
                                                  index=["Room Booking", "Food & Beverage", "Restaurant", "Laundry", "Other Services"].index(sale['type']) if sale['type'] in ["Room Booking", "Food & Beverage", "Restaurant", "Laundry", "Other Services"] else 0)
                            new_description = st.text_area("Description", value=sale.get('description', ''))
                            new_status = st.selectbox("Status", ["Completed", "Pending"], 
                                                    index=0 if sale['status'] == 'Completed' else 1)
                        
                        col_update, col_cancel = st.columns(2)
                        with col_update:
                            if st.form_submit_button("💾 Update Sale", type="primary"):
                                updated_sales = load_data('sales.json', selected_hotel)
                                for s in updated_sales:
                                    if s['id'] == sale['id']:
                                        s['amount'] = new_amount
                                        s['customer_name'] = new_customer
                                        s['payment_type'] = new_payment_type
                                        s['type'] = new_type
                                        s['description'] = new_description
                                        s['status'] = new_status
                                        break
                                save_data('sales.json', updated_sales, selected_hotel)
                                st.session_state[f"edit_mode_{sale['id']}"] = False
                                st.success("Sale updated successfully!")
                                st.rerun()
                        
                        with col_cancel:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f"edit_mode_{sale['id']}"] = False
                                st.rerun()

                # Delete confirmation
                if st.session_state.get(f"confirm_delete_{sale['id']}", False):
                    st.error(f"⚠️ Are you sure you want to delete this sale of ₹{sale['amount']:,.2f}?")
                    col_confirm, col_cancel = st.columns(2)
                    
                    with col_confirm:
                        if st.button(f"🗑️ Yes, Delete", key=f"confirm_delete_yes_{sale['id']}", type="primary"):
                            updated_sales = load_data('sales.json', selected_hotel)
                            updated_sales = [s for s in updated_sales if s['id'] != sale['id']]
                            save_data('sales.json', updated_sales, selected_hotel)
                            st.session_state[f"confirm_delete_{sale['id']}"] = False
                            st.success("Sale deleted successfully!")
                            st.rerun()
                    
                    with col_cancel:
                        if st.button(f"❌ Cancel", key=f"confirm_delete_no_{sale['id']}"):
                            st.session_state[f"confirm_delete_{sale['id']}"] = False
                            st.rerun()

else:
    st.info("No sales records found")

# Sales analytics
if sales and len(filtered_sales) > 0:
    st.markdown("---")
    st.markdown("### Sales Analytics")
    
    # Show period summary
    period_text = {
        "All Time": "All Time",
        "Today": "Today",
        "This Week": "This Week", 
        "This Month": "This Month",
        "This Year": "This Year",
        "Custom Range": f"{start_date} to {end_date}" if start_date and end_date else "Custom Range"
    }
    st.markdown(f"**Analytics for: {period_text[date_filter]}**")

    col1, col2 = st.columns(2)

    with col1:
        # Sales by type
        df_type = pd.DataFrame(filtered_sales)
        type_summary = df_type.groupby('type')['amount'].sum().reset_index()
        fig_type = px.pie(type_summary, values='amount', names='type', title=f"Sales by Type - {period_text[date_filter]}")
        st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        # Sales by payment method
        payment_summary = df_type.groupby('payment_type')['amount'].sum().reset_index()
        fig_payment = px.bar(payment_summary, x='payment_type', y='amount', title=f"Sales by Payment Method - {period_text[date_filter]}")
        st.plotly_chart(fig_payment, use_container_width=True)

# Admin download section
if user_role == 'Admin':
    st.markdown("---")
    st.markdown("### 📥 Download Sales Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download All Sales"):
            if sales:
                df = pd.DataFrame(sales)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download All Sales CSV",
                    data=csv,
                    file_name=f"sales_all_{get_current_datetime()[:10]}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No sales data to download")
    
    with col2:
        if st.button("📋 Download Filtered Sales"):
            if filtered_sales:
                df = pd.DataFrame(filtered_sales)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Filtered Sales CSV",
                    data=csv,
                    file_name=f"sales_filtered_{period_text[date_filter].lower().replace(' ', '_')}_{get_current_datetime()[:10]}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No filtered sales data to download")
    
    with col3:
        if st.button("🎯 Go to Download Center"):
            st.switch_page("pages/18_Data_Download.py")

# Cash handover section
st.markdown("---")
st.markdown("### Cash Handover")

if cash_sales > 0:
    st.info(f"Total cash sales to handover: ₹{cash_sales:,.2f}")

    with st.form("cash_handover"):
        handover_amount = st.number_input("Handover Amount", value=float(cash_sales), min_value=0.0)
        received_by = st.text_input("Received By", placeholder="Name of person receiving cash")
        notes = st.text_area("Notes", placeholder="Any additional notes")

        if st.form_submit_button("Record Cash Handover"):
            if not received_by:
                st.error("Please specify who received the cash")
            else:
                cash_handovers = load_data('cash_handovers.json', selected_hotel)
                new_handover = {
                    'id': generate_id(),
                    'date': get_current_datetime(),
                    'amount': handover_amount,
                    'received_by': received_by,
                    'notes': notes,
                    'created_by': st.session_state.get('username', 'Unknown')
                }
                cash_handovers.append(new_handover)
                save_data('cash_handovers.json', cash_handovers, selected_hotel)
                st.success(f"Cash handover of ₹{handover_amount:,.2f} recorded for {received_by}")
                st.rerun()
else:
    st.info("No cash sales to handover")