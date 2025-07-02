import streamlit as st
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils'))

from utils.auth import check_authentication
from utils.database_data_manager import load_data, save_data, get_current_date, get_current_datetime, generate_id
from utils.backup_manager import list_backups, restore_from_backup, create_backup
import json

# Check authentication
if not check_authentication():
    st.warning("Please log in to access this page")
    st.stop()

st.title("🔄 Data Recovery System")

# Get user details
user_role = st.session_state.get('user_role', 'User')
username = st.session_state.get('username', 'User')
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
hotel_name = st.session_state.get('hotel_name', 'Hotel')

# Only admin can use data recovery
if user_role != 'Admin':
    st.error("Only administrators can access data recovery features")
    st.stop()

st.markdown(f"### Data Recovery for {hotel_name}")

# Create tabs for different recovery options
tab1, tab2, tab3, tab4 = st.tabs(["📊 Current Data Status", "💾 Backup & Restore", "➕ Quick Data Entry", "🔧 Repair Tools"])

with tab1:
    st.markdown("#### Current Data Status")
    
    # Check data files for selected hotel
    data_files = [
        ('sales.json', 'Sales Records'),
        ('expenditures.json', 'Expenditures'),
        ('advance_payments.json', 'Advance Payments'),
        ('outstanding_dues.json', 'Outstanding Dues'),
        ('room_services.json', 'Room Services'),
        ('complementary_rooms.json', 'Complementary Rooms')
    ]
    
    for filename, display_name in data_files:
        data = load_data(filename, selected_hotel)
        count = len(data) if isinstance(data, list) else len(data.keys()) if isinstance(data, dict) else 0
        st.metric(display_name, count, f"records in {filename}")
    
    # Show recent activity
    st.markdown("#### Recent Activity Logs")
    try:
        with open('data/logs/data_access.log', 'r') as f:
            logs = json.load(f)
        
        # Filter logs for today and selected hotel
        today = get_current_date()
        recent_logs = [log for log in logs[-20:] if selected_hotel in log.get('filename', '')]
        
        if recent_logs:
            for log in reversed(recent_logs):
                st.text(f"{log['timestamp'][:19]} - {log['operation']} - {log['filename']}")
        else:
            st.info("No recent activity for this hotel location")
    except:
        st.info("No activity logs available")

with tab2:
    st.markdown("#### Backup and Restore System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Create Backup")
        if st.button("Create Full Backup", type="primary"):
            success, message = create_backup()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    with col2:
        st.markdown("##### Available Backups")
        backups = list_backups()
        
        if backups:
            for backup in backups[:5]:  # Show last 5 backups
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.text(f"{backup['formatted_date']}")
                with col_b:
                    if st.button("Restore", key=f"restore_{backup['name']}"):
                        success, message = restore_from_backup(backup['name'])
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        else:
            st.info("No backups available")

with tab3:
    st.markdown("#### Quick Data Entry for Lost Records")
    st.info("Use this section to quickly re-add data that was lost")
    
    entry_type = st.selectbox("What type of data do you want to add?", [
        "Sales Record", "Expenditure", "Advance Payment", "Outstanding Due", "Room Service"
    ])
    
    if entry_type == "Sales Record":
        with st.form("add_sales_record"):
            col1, col2 = st.columns(2)
            with col1:
                customer_name = st.text_input("Customer Name")
                amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
                payment_type = st.selectbox("Payment Type", ["Cash", "Account"])
                
            with col2:
                sale_type = st.selectbox("Sale Type", ["Room Booking", "Room Service", "Restaurant", "Other"])
                room_number = st.text_input("Room Number (if applicable)")
                description = st.text_area("Description")
                
            if st.form_submit_button("Add Sales Record"):
                if customer_name and amount > 0:
                    sales = load_data('sales.json', selected_hotel)
                    new_sale = {
                        'id': generate_id(),
                        'date': get_current_datetime(),
                        'customer_name': customer_name,
                        'amount': amount,
                        'type': sale_type,
                        'payment_type': payment_type,
                        'status': 'Completed',
                        'room_number': room_number,
                        'description': description,
                        'created_by': username
                    }
                    sales.append(new_sale)
                    save_data('sales.json', sales, selected_hotel)
                    st.success(f"Sales record added successfully for {customer_name}")
                    st.rerun()
                else:
                    st.error("Please fill in customer name and amount")
    
    elif entry_type == "Expenditure":
        with st.form("add_expenditure"):
            col1, col2 = st.columns(2)
            with col1:
                description = st.text_input("Description")
                amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
                category = st.selectbox("Category", ["Food & Supplies", "Maintenance", "Utilities", "Staff", "Marketing", "Other"])
                
            with col2:
                vendor = st.text_input("Vendor/Supplier")
                payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Credit Card", "Cheque"])
                notes = st.text_area("Additional Notes")
                
            if st.form_submit_button("Add Expenditure"):
                if description and amount > 0:
                    expenditures = load_data('expenditures.json', selected_hotel)
                    new_expenditure = {
                        'id': generate_id(),
                        'date': get_current_datetime(),
                        'description': description,
                        'amount': amount,
                        'category': category,
                        'vendor': vendor,
                        'payment_method': payment_method,
                        'notes': notes,
                        'created_by': username
                    }
                    expenditures.append(new_expenditure)
                    save_data('expenditures.json', expenditures, selected_hotel)
                    st.success(f"Expenditure added successfully: {description}")
                    st.rerun()
                else:
                    st.error("Please fill in description and amount")

with tab4:
    st.markdown("#### Data Repair Tools")
    
    if st.button("Reset All Data Files for This Hotel", type="secondary"):
        st.warning("⚠️ This will clear all data for the current hotel location!")
        if st.button("CONFIRM - Reset All Data"):
            # Reset all data files for selected hotel
            data_files = ['sales.json', 'expenditures.json', 'advance_payments.json', 
                         'outstanding_dues.json', 'room_services.json', 'complementary_rooms.json']
            
            for filename in data_files:
                save_data(filename, [], selected_hotel)
            
            st.success("All data files have been reset for this hotel location")
            st.rerun()
    
    st.markdown("---")
    
    if st.button("Repair Corrupted Files"):
        from utils.data_integrity import check_all_data_integrity, repair_corrupted_files
        
        issues = check_all_data_integrity()
        if issues:
            st.warning("Issues found:")
            for issue in issues:
                st.text(f"• {issue}")
            
            success, repairs = repair_corrupted_files()
            if success:
                st.success("Repair completed:")
                for repair in repairs:
                    st.text(f"✓ {repair}")
            else:
                st.error(f"Repair failed: {repairs}")
        else:
            st.success("No data integrity issues found")

st.markdown("---")
st.info("💡 **Tip**: All operations are logged and can be reviewed in the activity logs above.")