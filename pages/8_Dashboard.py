import streamlit as st
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication
from utils.database_data_manager import (
    load_data, 
    calculate_total_sales, 
    calculate_total_expenditures, 
    calculate_pending_dues,
    get_current_date
)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

# All users can view dashboard
user_role = st.session_state.get('user_role', 'User')

st.title("📈 Dashboard")

# Get selected hotel
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
hotel_name = st.session_state.get('hotel_name', 'Hotel 1')

st.markdown(f"### {hotel_name} Dashboard")

# Date filtering at the top
st.markdown("### 📅 Filter Data by Date")
from datetime import datetime, timedelta

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

# Function to filter data by date
def filter_data_by_date(data_list, date_filter, start_date=None, end_date=None):
    if date_filter == "All Time":
        return data_list

    today = datetime.now()
    filtered_data = []

    for item in data_list:
        try:
            # Use the item date for filtering
            item_date = item['date'][:10] if item['date'] else None
            if not item_date:
                continue

            item_datetime = datetime.strptime(item_date, '%Y-%m-%d')

            if date_filter == "Today":
                if item_datetime.date() == today.date():
                    filtered_data.append(item)
            elif date_filter == "This Week":
                week_start = today - timedelta(days=today.weekday())
                if item_datetime.date() >= week_start.date():
                    filtered_data.append(item)
            elif date_filter == "This Month":
                if item_datetime.month == today.month and item_datetime.year == today.year:
                    filtered_data.append(item)
            elif date_filter == "This Year":
                if item_datetime.year == today.year:
                    filtered_data.append(item)
            elif date_filter == "Custom Range" and start_date and end_date:
                if start_date <= item_datetime.date() <= end_date:
                    filtered_data.append(item)
        except ValueError:
            # Skip records with invalid dates
            continue

    return filtered_data

st.markdown("---")

# Load all data for selected hotel with error handling
try:
    all_sales = load_data('sales.json', selected_hotel)
    if not isinstance(all_sales, list):
        all_sales = []
except:
    all_sales = []

try:
    all_expenditures = load_data('expenditures.json', selected_hotel)
    if not isinstance(all_expenditures, list):
        all_expenditures = []
except:
    all_expenditures = []

try:
    all_room_services = load_data('room_services.json', selected_hotel)
    if not isinstance(all_room_services, list):
        all_room_services = []
except:
    all_room_services = []

try:
    all_complementary_rooms = load_data('complementary_rooms.json', selected_hotel)
    if not isinstance(all_complementary_rooms, list):
        all_complementary_rooms = []
except:
    all_complementary_rooms = []

try:
    all_advance_payments = load_data('advance_payments.json', selected_hotel)
    if not isinstance(all_advance_payments, list):
        all_advance_payments = []
except:
    all_advance_payments = []

try:
    all_outstanding_dues = load_data('outstanding_dues.json', selected_hotel)
    if not isinstance(all_outstanding_dues, list):
        all_outstanding_dues = []
except:
    all_outstanding_dues = []

try:
    all_uploaded_bills = load_data('uploaded_bills.json', selected_hotel)
    if not isinstance(all_uploaded_bills, list):
        all_uploaded_bills = []
except:
    all_uploaded_bills = []

try:
    all_cash_handovers = load_data('cash_handovers.json', selected_hotel)
    if not isinstance(all_cash_handovers, list):
        all_cash_handovers = []
except:
    all_cash_handovers = []

try:
    rooms = load_data('rooms.json', selected_hotel)
    if not isinstance(rooms, dict):
        rooms = {}
except:
    rooms = {}

# Apply date filtering to all data
sales = filter_data_by_date(all_sales, date_filter, start_date, end_date)
expenditures = filter_data_by_date(all_expenditures, date_filter, start_date, end_date)
room_services = filter_data_by_date(all_room_services, date_filter, start_date, end_date)
complementary_rooms = filter_data_by_date(all_complementary_rooms, date_filter, start_date, end_date)
advance_payments = filter_data_by_date(all_advance_payments, date_filter, start_date, end_date)
outstanding_dues = filter_data_by_date(all_outstanding_dues, date_filter, start_date, end_date)
uploaded_bills = filter_data_by_date(all_uploaded_bills, date_filter, start_date, end_date)
cash_handovers = filter_data_by_date(all_cash_handovers, date_filter, start_date, end_date)

# Show filtered period info
period_text = {
    "All Time": "All Time",
    "Today": "Today",
    "This Week": "This Week", 
    "This Month": "This Month",
    "This Year": "This Year",
    "Custom Range": f"{start_date} to {end_date}" if start_date and end_date else "Custom Range"
}
st.info(f"📊 Showing data for: **{period_text[date_filter]}**")

# Key metrics
st.markdown("### Key Performance Indicators")

# Calculate metrics from filtered data
total_sales = sum(sale['amount'] for sale in sales)
total_expenditures = sum(exp['amount'] for exp in expenditures)
pending_dues = sum(due['amount'] for due in outstanding_dues if due.get('status') == 'Pending')
net_profit = total_sales - total_expenditures

# Current period metrics (based on filtered data)
filtered_sales_amount = total_sales
filtered_expenditures_amount = total_expenditures

# Room occupancy
if isinstance(rooms, dict):
    occupied_rooms = len([r for r in rooms.values() if r['status'] == 'Occupied'])
    total_rooms = len(rooms)
elif isinstance(rooms, list):
    occupied_rooms = len([r for r in rooms if isinstance(r, dict) and r.get('status') == 'Occupied'])
    total_rooms = len(rooms)
else:
    occupied_rooms = 0
    total_rooms = 8  # Default number of rooms
occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0

# Calculate advance payments
advance_amount = sum(ap['amount'] for ap in advance_payments if ap['status'] == 'Pending')

# Display metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Sales", f"₹{total_sales:,.2f}", f"Period: {period_text[date_filter]}")

with col2:
    st.metric("Total Expenditures", f"₹{total_expenditures:,.2f}", f"Period: {period_text[date_filter]}")

with col3:
    st.metric("Net Profit", f"₹{net_profit:,.2f}", f"Margin: {(net_profit/total_sales*100):.1f}%" if total_sales > 0 else "0%")

with col4:
    outstanding_amount = sum(due['amount'] for due in outstanding_dues if due['status'] == 'Pending')
    st.metric("Outstanding Dues", f"₹{outstanding_amount:,.2f}")

with col5:
    st.metric("Advance Payments", f"₹{advance_amount:,.2f}")

with col6:
    st.metric("Room Occupancy", f"{occupancy_rate:.1f}%", f"{occupied_rooms}/{total_rooms}")

st.markdown("---")

# Sales overview
st.markdown("### Sales Overview")

if sales:
    col1, col2 = st.columns(2)

    with col1:
        # Sales by payment type
        payment_data = {}
        for sale in sales:
            payment_type = sale['payment_type']
            payment_data[payment_type] = payment_data.get(payment_type, 0) + sale['amount']

        if payment_data:
            fig_payment = px.pie(
                values=list(payment_data.values()), 
                names=list(payment_data.keys()), 
                title=f"Sales by Payment Type - {period_text[date_filter]}"
            )
            st.plotly_chart(fig_payment, use_container_width=True)

    with col2:
        # Sales by type
        type_data = {}
        for sale in sales:
            sale_type = sale['type']
            type_data[sale_type] = type_data.get(sale_type, 0) + sale['amount']

        if type_data:
            fig_type = px.bar(
                x=list(type_data.keys()), 
                y=list(type_data.values()), 
                title=f"Sales by Type - {period_text[date_filter]}"
            )
            st.plotly_chart(fig_type, use_container_width=True)

# Restaurant analytics section
restaurant_sales = [s for s in sales if s.get('type') == 'Restaurant']
if restaurant_sales:
    st.markdown("---")
    st.markdown("### 🍽️ Restaurant Analytics")

    restaurant_total = sum(sale['amount'] for sale in restaurant_sales)
    restaurant_cash = sum(sale['amount'] for sale in restaurant_sales if sale['payment_type'] == 'Cash')
    restaurant_account = sum(sale['amount'] for sale in restaurant_sales if sale['payment_type'] == 'Account')

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Restaurant Sales", f"₹{restaurant_total:,.2f}")
    with col2:
        st.metric("Restaurant Cash", f"₹{restaurant_cash:,.2f}")
    with col3:
        st.metric("Restaurant Account", f"₹{restaurant_account:,.2f}")
    with col4:
        restaurant_percentage = (restaurant_total / total_sales * 100) if total_sales > 0 else 0
        st.metric("Restaurant Share", f"{restaurant_percentage:.1f}%")

    # Restaurant order types
    col1, col2 = st.columns(2)

    with col1:
        dine_in_sales = sum(sale['amount'] for sale in restaurant_sales if 'Dine In' in sale.get('order_type', ''))
        room_service_sales = sum(sale['amount'] for sale in restaurant_sales if 'Room Service' in sale.get('order_type', ''))

        st.metric("Dine In Sales", f"₹{dine_in_sales:,.2f}")
        st.metric("Room Service Sales", f"₹{room_service_sales:,.2f}")

    with col2:
        if restaurant_sales:
            # Restaurant order type chart
            order_type_data = {"Dine In": dine_in_sales, "Room Service": room_service_sales}
            order_type_data = {k: v for k, v in order_type_data.items() if v > 0}

            if order_type_data:
                fig_restaurant = px.pie(
                    values=list(order_type_data.values()), 
                    names=list(order_type_data.keys()), 
                    title="Restaurant Sales by Type"
                )
                st.plotly_chart(fig_restaurant, use_container_width=True)

# Cash flow analysis
st.markdown("---")
st.markdown("### Cash Flow Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    cash_sales = sum(sale['amount'] for sale in sales if sale['payment_type'] == 'Cash')
    st.metric("Cash Sales", f"₹{cash_sales:,.2f}")

with col2:
    account_sales = sum(sale['amount'] for sale in sales if sale['payment_type'] == 'Account')
    st.metric("Account Sales", f"₹{account_sales:,.2f}")

with col3:
    advance_amount = sum(ap['amount'] for ap in advance_payments if ap['status'] == 'Pending')
    st.metric("Advance Payments", f"₹{advance_amount:,.2f}")

# Room service analytics
st.markdown("---")
st.markdown("### Room Service Analytics")

if room_services:
    col1, col2 = st.columns(2)

    with col1:
        # Room service revenue
        rs_revenue = sum(rs['amount'] for rs in room_services)
        rs_completed = len([rs for rs in room_services if rs['status'] == 'Completed'])
        rs_pending = len([rs for rs in room_services if rs['status'] == 'Pending'])

        st.metric("Room Service Revenue", f"₹{rs_revenue:,.2f}")
        st.metric("Completed Services", rs_completed)
        st.metric("Pending Services", rs_pending)

    with col2:
        # Popular services
        service_counts = {}
        for rs in room_services:
            service = rs['service_item']
            service_counts[service] = service_counts.get(service, 0) + 1

        if service_counts:
            top_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            st.markdown("**Top 5 Services:**")
            for service, count in top_services:
                st.write(f"• {service}: {count} orders")

# Expenditure breakdown
st.markdown("---")
st.markdown("### Expenditure Breakdown")

if expenditures:
    # Expenditure by category
    exp_categories = {}
    for exp in expenditures:
        category = exp['category']
        exp_categories[category] = exp_categories.get(category, 0) + exp['amount']

    if exp_categories:
        fig_exp = px.bar(
            x=list(exp_categories.values()), 
            y=list(exp_categories.keys()), 
            orientation='h',
            title=f"Expenditure by Category - {period_text[date_filter]}"
        )
        st.plotly_chart(fig_exp, use_container_width=True)

# Room utilization
st.markdown("---")
st.markdown("### Room Utilization")

if rooms:
    # Room status distribution
    room_status = {}
    if isinstance(rooms, dict):
        for room in rooms.values():
            status = room['status']
            room_status[status] = room_status.get(status, 0) + 1
    elif isinstance(rooms, list):
        for room in rooms:
            if isinstance(room, dict):
                status = room.get('status', 'Available')
                room_status[status] = room_status.get(status, 0) + 1

    col1, col2 = st.columns(2)

    with col1:
        # Room status pie chart
        if room_status:
            fig_rooms = px.pie(
                values=list(room_status.values()), 
                names=list(room_status.keys()), 
                title="Room Status Distribution"
            )
            st.plotly_chart(fig_rooms, use_container_width=True)

    with col2:
        # Room revenue potential
        available_rooms = room_status.get('Available', 0)
        occupied_rooms = room_status.get('Occupied', 0)

        # Calculate potential revenue
        if isinstance(rooms, dict):
            avg_room_rate = sum(room['price'] for room in rooms.values()) / len(rooms)
            total_rooms_count = len(rooms)
        elif isinstance(rooms, list):
            room_prices = [room.get('price', 2000) for room in rooms if isinstance(room, dict)]
            avg_room_rate = sum(room_prices) / len(room_prices) if room_prices else 2000
            total_rooms_count = len(rooms)
        else:
            avg_room_rate = 2000
            total_rooms_count = 8
        current_revenue = occupied_rooms * avg_room_rate
        potential_revenue = total_rooms_count * avg_room_rate

        st.metric("Current Room Revenue Potential", f"₹{current_revenue:,.2f}")
        st.metric("Maximum Room Revenue Potential", f"₹{potential_revenue:,.2f}")
        st.metric("Revenue Efficiency", f"{(current_revenue/potential_revenue*100):.1f}%" if potential_revenue > 0 else "0%")

# Complementary rooms impact
if complementary_rooms:
    st.markdown("---")
    st.markdown("### Complementary Rooms Impact")

    comp_value = sum(comp['room_value'] for comp in complementary_rooms)
    comp_active = len([comp for comp in complementary_rooms if comp['status'] == 'Active'])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Comp Value", f"₹{comp_value:,.2f}")
    with col2:
        st.metric("Active Comp Rooms", comp_active)
    with col3:
        impact_percentage = (comp_value / total_sales * 100) if total_sales > 0 else 0
        st.metric("Impact on Revenue", f"{impact_percentage:.1f}%")

# Period trends
st.markdown("---")
st.markdown(f"### {period_text[date_filter]} Performance")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(f"{period_text[date_filter]} Sales", f"₹{total_sales:,.2f}")
with col2:
    st.metric(f"{period_text[date_filter]} Expenses", f"₹{total_expenditures:,.2f}")
with col3:
    st.metric(f"{period_text[date_filter]} Profit", f"₹{net_profit:,.2f}")

# Performance summary
st.markdown("---")
st.markdown("### Performance Summary")

performance_data = {
    "Metric": [
        "Total Transactions",
        "Average Sale Value",
        "Room Occupancy Rate",
        "Service Revenue Share",
        "Expense Ratio",
        "Customer Satisfaction"
    ],
    "Value": [
        len(sales),
        f"₹{total_sales/len(sales):,.2f}" if sales else "₹0",
        f"{occupancy_rate:.1f}%",
        f"{(sum(rs['amount'] for rs in room_services)/total_sales*100):.1f}%" if total_sales > 0 else "0%",
        f"{(total_expenditures/total_sales*100):.1f}%" if total_sales > 0 else "0%",
        "85%" # Placeholder - would be calculated from guest feedback
    ],
    "Status": [
        "📊",
        "💰",
        "🏠",
        "🛎️",
        "📉",
        "⭐"
    ]
}

df_performance = pd.DataFrame(performance_data)
st.dataframe(df_performance, use_container_width=True, hide_index=True)

# Action items and alerts
st.markdown("---")
st.markdown("### Action Items & Alerts")

alerts = []

# Check for pending outstanding dues
if outstanding_amount > 0:
    alerts.append(f"Outstanding dues: ₹{outstanding_amount:,.2f} - Follow up required")

# Check for pending advance payments
if advance_amount > 0:
    alerts.append(f"Advance payments: ₹{advance_amount:,.2f} remaining to collect")

# Check for pending bills
pending_bills = len([b for b in uploaded_bills if b['status'] == 'Pending'])
if pending_bills > 0:
    alerts.append(f"{pending_bills} bills pending review")

# Check room occupancy
if occupancy_rate > 80:
    alerts.append(f"High occupancy rate: {occupancy_rate:.1f}% - Consider room availability")

# Calculate cash in hand
cash_sales = sum(sale['amount'] for sale in sales if sale['payment_type'] == 'Cash')
cash_handovers = load_data('cash_handovers.json')
total_handovers = sum(h['amount'] for h in cash_handovers)
cash_in_hand = cash_sales - total_handovers

# Check cash in hand
if cash_in_hand > 50000:
    alerts.append(f"High cash in hand: ₹{cash_in_hand:,.2f} - Consider handover")

# Check for low occupancy
if occupancy_rate < 50:
    alerts.append(f"📉 Low occupancy rate: {occupancy_rate:.1f}% - Marketing needed")

# Check for pending room services
pending_services = len([rs for rs in room_services if rs['status'] == 'Pending'])
if pending_services > 0:
    alerts.append(f"🛎️ {pending_services} pending room service requests")

# Check for maintenance rooms
if isinstance(rooms, dict):
    maintenance_rooms = len([r for r in rooms.values() if r['status'] == 'Maintenance'])
elif isinstance(rooms, list):
    maintenance_rooms = len([r for r in rooms if isinstance(r, dict) and r.get('status') == 'Maintenance'])
else:
    maintenance_rooms = 0
if maintenance_rooms > 0:
    alerts.append(f"🔧 {maintenance_rooms} rooms under maintenance")

# Check expense ratio
if total_sales > 0 and (total_expenditures / total_sales) > 0.7:
    alerts.append(f"💸 High expense ratio: {(total_expenditures/total_sales*100):.1f}%")

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("No immediate action items - Operations running smoothly!")

# Quick actions
st.markdown("---")
st.markdown("### Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Cash Sales"):
        st.switch_page("pages/12_Cash_Sales.py")

with col2:
    if st.button("Account Sales"):
        st.switch_page("pages/11_Account_Sales.py")

with col3:
    if st.button("Outstanding Dues"):
        st.switch_page("pages/9_Outstanding_Dues.py")

with col4:
    if st.button("🍽️ Restaurant"):
        st.switch_page("pages/19_Restaurant.py")

# Add row for more actions
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Cash Handover"):
        st.switch_page("pages/13_Cash_Handover.py")

with col2:
    if st.button("Account Handover"):
        st.switch_page("pages/17_Account_Handover.py")

with col3:
    if st.button("Financial Summary"):
        st.switch_page("pages/16_Financial_Summary.py")

with col4:
    if st.button("Bad Debt"):
        st.switch_page("pages/14_Bad_Debt.py")

# Add third row
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Discount"):
        st.switch_page("pages/15_Discount.py")

with col2:
    pass  # Empty for spacing

with col3:
    pass  # Empty for spacing

with col4:
    pass  # Empty for spacing

# Admin download section
if user_role == 'Admin':
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📥 Data Download Center"):
            st.switch_page("pages/18_Data_Download.py")

    with col2:
        pass  # Empty for spacing

    with col3:
        pass  # Empty for spacing

    with col4:
        pass  # Empty for spacing

# Admin-only section: Delete All Data
if user_role == 'Admin':
    st.markdown("---")
    st.markdown("### 🗑️ Admin Data Management")

    with st.expander("⚠️ Delete All Data (Admin Only)", expanded=False):
        st.warning("**DANGER ZONE** - This action cannot be undone!")
        st.write("This will permanently delete all data from the system:")

        data_types = [
            "• All Sales Records",
            "• All Expenditure Records", 
            "• All Room Service Records",
            "• All Complementary Room Records",
            "• All Advance Payment Records",
            "• All Outstanding Dues Records",
            "• All Uploaded Bills",
            "• All Cash Handover Records",
            "• Room booking information (rooms will be reset to Available)",
            "• All Account Handover Records",
            "• All Financial Summary Records",
            "• All Bad Debt Records",
            "• All Discount Records",
            #"• All User Records",
           # "• All Room Records",
          #  ""
        ]

        for data_type in data_types:
            st.write(data_type)

        st.markdown("**Users and room configuration will NOT be deleted.**")

        # Two-step confirmation
        col1, col2 = st.columns(2)

        with col1:
            confirm_text = st.text_input("Type 'DELETE ALL DATA' to confirm:", placeholder="DELETE ALL DATA")

        with col2:
            if confirm_text == "DELETE ALL DATA":
                if st.button("🗑️ DELETE ALL DATA", type="primary"):
                    # Clear all data files
                    from utils.data_manager import save_data

                    # Reset all data files to empty lists
                    data_files = [
                        'sales.json',
                        'expenditures.json', 
                        'room_services.json',
                        'complementary_rooms.json',
                        'advance_payments.json',
                        'outstanding_dues.json',
                        'uploaded_bills.json',
                        'cash_handovers.json',
                        'account_handovers.json',
                        'bad_debts.json',
                        'discounts.json',
                        'complementary_records.json'
                    ]

                    for file_name in data_files:
                        save_data(file_name, [], selected_hotel)

                    # Reset rooms to default state but keep current prices
                    current_rooms = load_data('rooms.json', selected_hotel)
                    rooms_reset = {}

                    # Different room ranges for different hotels
                    if selected_hotel == 'hotel1':
                        room_numbers = range(101, 109)  # 101-108
                    else:  # hotel2
                        room_numbers = [101, 102, 103, 201, 202, 203, 301, 302, 303, 304, 305, 401, 402, 403, 501, 502, 503]

                    for room_num in room_numbers:
                        room_key = str(room_num)
                        # Keep existing price if room exists, otherwise use default
                        if isinstance(current_rooms, dict):
                            existing_price = current_rooms.get(room_key, {}).get('price', 2000)
                            existing_type = current_rooms.get(room_key, {}).get('type', 'Standard')
                        elif isinstance(current_rooms, list):
                            # Find room in list by room_number
                            existing_room = next((r for r in current_rooms if str(r.get('room_number', r.get('id'))) == room_key), {})
                            existing_price = existing_room.get('price', 2000)
                            existing_type = existing_room.get('type', 'Standard')
                        else:
                            existing_price = 2000
                            existing_type = 'Standard'

                        rooms_reset[room_key] = {
                            'room_number': room_key,
                            'status': 'Available',
                            'type': existing_type,
                            'price': existing_price,
                            'current_guest': None,
                            'checkin_date': None,
                            'checkout_date': None,
                            'guest_phone': None
                        }
                    save_data('rooms.json', rooms_reset, selected_hotel)

                    st.success("✅ All data has been successfully deleted!")
                    st.balloons()
                    st.rerun()
            else:
                st.button("🗑️ DELETE ALL DATA", disabled=True, help="Type 'DELETE ALL DATA' to enable this button")

# Data refresh info
st.markdown("---")
st.caption(f"Dashboard last updated: {get_current_date()} | Showing data for: {period_text[date_filter]} | Data refreshes automatically")
```

```
The dashboard code is updated to load data from the database for various components including sales, restaurant, room services, expenditures, advance payments, outstanding dues, cash handovers, account handovers, bad debts, discounts and complementary data.
```