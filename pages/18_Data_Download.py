
import streamlit as st
import sys
import os
import pandas as pd
import zipfile
import io
from datetime import datetime

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication
from utils.database_data_manager import load_data, get_current_date

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

# Check admin privileges
if st.session_state.get('user_role') != 'Admin':
    st.error("Access denied. Only admin can download data.")
    st.stop()

st.title("📥 Data Download Center")

# Get selected hotel
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
hotel_name = st.session_state.get('hotel_name', 'Hotel 1')

st.markdown(f"### Download Data for {hotel_name}")

# Load all data
rooms_list = load_data('rooms.json', selected_hotel)
# Convert rooms list to dictionary for backward compatibility
if isinstance(rooms_list, list):
    rooms_dict = {}
    for room in rooms_list:
        if isinstance(room, dict) and 'room_number' in room:
            rooms_dict[room['room_number']] = room
else:
    rooms_dict = rooms_list if rooms_list else {}

all_data = {
    'Sales Management': load_data('sales.json', selected_hotel),
    'Expenditure Management': load_data('expenditures.json', selected_hotel),
    'Room Management': rooms_dict,
    'Room Service': load_data('room_services.json', selected_hotel),
    'Complementary Rooms': load_data('complementary_rooms.json', selected_hotel),
    'Advance Payments': load_data('advance_payments.json', selected_hotel),
    'Outstanding Dues': load_data('outstanding_dues.json', selected_hotel),
    'Bill Upload': load_data('uploaded_bills.json', selected_hotel),
    'Cash Handover': load_data('cash_handovers.json', selected_hotel),
    'Account Handover': load_data('account_handovers.json', selected_hotel),
    'Bad Debt': load_data('bad_debts.json', selected_hotel),
    'Discount': load_data('discounts.json', selected_hotel),
    'Complementary Records': load_data('complementary_records.json', selected_hotel)
}

# Individual page downloads
st.markdown("### 📄 Download by Page")

col1, col2, col3 = st.columns(3)

# Sales Management
with col1:
    if st.button("📊 Sales Management Data"):
        if all_data['Sales Management']:
            df = pd.DataFrame(all_data['Sales Management'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Sales CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_sales_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No sales data available")

# Expenditure Management
with col2:
    if st.button("💸 Expenditure Data"):
        if all_data['Expenditure Management']:
            df = pd.DataFrame(all_data['Expenditure Management'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Expenditures CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_expenditures_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No expenditure data available")

# Room Management
with col3:
    if st.button("🏠 Room Management Data"):
        if all_data['Room Management']:
            # Convert rooms dict to list for DataFrame
            rooms_list = [dict(room, room_id=room_id) for room_id, room in all_data['Room Management'].items()]
            df = pd.DataFrame(rooms_list)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Rooms CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_rooms_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No room data available")

# Row 2
col1, col2, col3 = st.columns(3)

# Room Service
with col1:
    if st.button("🛎️ Room Service Data"):
        if all_data['Room Service']:
            df = pd.DataFrame(all_data['Room Service'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Room Service CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_room_service_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No room service data available")

# Complementary Rooms
with col2:
    if st.button("🆓 Complementary Rooms Data"):
        if all_data['Complementary Rooms']:
            df = pd.DataFrame(all_data['Complementary Rooms'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Complementary CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_complementary_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No complementary room data available")

# Advance Payments
with col3:
    if st.button("💰 Advance Payments Data"):
        if all_data['Advance Payments']:
            df = pd.DataFrame(all_data['Advance Payments'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Advance Payments CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_advance_payments_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No advance payment data available")

# Row 3
col1, col2, col3 = st.columns(3)

# Outstanding Dues
with col1:
    if st.button("📋 Outstanding Dues Data"):
        if all_data['Outstanding Dues']:
            df = pd.DataFrame(all_data['Outstanding Dues'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Outstanding Dues CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_outstanding_dues_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No outstanding dues data available")

# Bill Upload
with col2:
    if st.button("📄 Bill Upload Data"):
        if all_data['Bill Upload']:
            df = pd.DataFrame(all_data['Bill Upload'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Bills CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_bills_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No bill data available")

# Cash Handover
with col3:
    if st.button("💵 Cash Handover Data"):
        if all_data['Cash Handover']:
            df = pd.DataFrame(all_data['Cash Handover'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Cash Handover CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_cash_handover_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No cash handover data available")

# Row 4
col1, col2, col3 = st.columns(3)

# Account Handover
with col1:
    if st.button("🏦 Account Handover Data"):
        if all_data['Account Handover']:
            df = pd.DataFrame(all_data['Account Handover'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Account Handover CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_account_handover_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No account handover data available")

# Bad Debt
with col2:
    if st.button("💸 Bad Debt Data"):
        if all_data['Bad Debt']:
            df = pd.DataFrame(all_data['Bad Debt'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Bad Debt CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_bad_debt_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No bad debt data available")

# Discount
with col3:
    if st.button("🏷️ Discount Data"):
        if all_data['Discount']:
            df = pd.DataFrame(all_data['Discount'])
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Discount CSV",
                data=csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_discount_{get_current_date()}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No discount data available")

st.markdown("---")

# Bulk download options
st.markdown("### 📦 Bulk Download Options")

col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Download All Data as ZIP", type="primary"):
        try:
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add each data type to ZIP
                for data_type, data in all_data.items():
                    if data:  # Only add if data exists
                        if data_type == 'Room Management':
                            # Handle rooms dict specially
                            rooms_list = [dict(room, room_id=room_id) for room_id, room in data.items()]
                            df = pd.DataFrame(rooms_list)
                        else:
                            df = pd.DataFrame(data)
                        
                        csv_content = df.to_csv(index=False)
                        filename = f"{data_type.replace(' ', '_').lower()}.csv"
                        zip_file.writestr(filename, csv_content)
                
                # Add a summary file
                summary_data = {
                    'Hotel': hotel_name,
                    'Download Date': get_current_date(),
                    'Admin User': st.session_state.get('username', 'Unknown'),
                    'Data Types Included': len([d for d in all_data.values() if d]),
                    'Total Records': sum(len(d) if isinstance(d, list) else len(d.keys()) for d in all_data.values() if d)
                }
                summary_df = pd.DataFrame([summary_data])
                zip_file.writestr("download_summary.csv", summary_df.to_csv(index=False))
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="📥 Download ZIP File",
                data=zip_buffer.getvalue(),
                file_name=f"{hotel_name.replace(' ', '_').lower()}_complete_data_{get_current_date()}.zip",
                mime="application/zip"
            )
            
            st.success("✅ ZIP file prepared for download!")
            
        except Exception as e:
            st.error(f"Error creating ZIP file: {str(e)}")

with col2:
    if st.button("📊 Download Summary Report"):
        try:
            # Create summary report
            summary_data = []
            for data_type, data in all_data.items():
                if isinstance(data, list):
                    record_count = len(data)
                    total_amount = sum(item.get('amount', 0) for item in data if isinstance(item, dict) and 'amount' in item)
                elif isinstance(data, dict):
                    record_count = len(data)
                    total_amount = 0
                else:
                    record_count = 0
                    total_amount = 0
                
                summary_data.append({
                    'Data Type': data_type,
                    'Record Count': record_count,
                    'Total Amount': f"₹{total_amount:,.2f}" if total_amount > 0 else "N/A",
                    'Last Updated': get_current_date()
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_csv = summary_df.to_csv(index=False)
            
            st.download_button(
                label="📊 Download Summary CSV",
                data=summary_csv,
                file_name=f"{hotel_name.replace(' ', '_').lower()}_summary_report_{get_current_date()}.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Error creating summary report: {str(e)}")

st.markdown("---")

# Data statistics
st.markdown("### 📈 Data Statistics")

total_records = 0
total_amount = 0

for data_type, data in all_data.items():
    if data:
        if isinstance(data, list):
            record_count = len(data)
            amount = sum(item.get('amount', 0) for item in data if isinstance(item, dict) and 'amount' in item)
        elif isinstance(data, dict):
            record_count = len(data)
            amount = 0
        else:
            record_count = 0
            amount = 0
        
        total_records += record_count
        total_amount += amount

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", total_records)

with col2:
    st.metric("Total Amount", f"₹{total_amount:,.2f}")

with col3:
    data_types_with_data = len([d for d in all_data.values() if d])
    st.metric("Active Data Types", data_types_with_data)

with col4:
    st.metric("Hotel", hotel_name)

# Show data breakdown
st.markdown("### 📋 Data Breakdown")

breakdown_data = []
for data_type, data in all_data.items():
    if isinstance(data, list):
        record_count = len(data)
        total_amount = sum(item.get('amount', 0) for item in data if isinstance(item, dict) and 'amount' in item)
    elif isinstance(data, dict):
        record_count = len(data)
        total_amount = 0
    else:
        record_count = 0
        total_amount = 0
    
    breakdown_data.append({
        'Page/Module': data_type,
        'Records': record_count,
        'Amount': f"₹{total_amount:,.2f}" if total_amount > 0 else "N/A",
        'Status': "✅ Has Data" if record_count > 0 else "❌ No Data"
    })

breakdown_df = pd.DataFrame(breakdown_data)
st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption(f"Data Download Center | {hotel_name} | Generated on: {get_current_date()}")
