import streamlit as st
import sys
import os
import json
import zipfile
import io

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication
from utils.database_data_manager import load_data, get_current_date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import zipfile
import io
from datetime import datetime, timedelta

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

user_role = st.session_state.get('user_role', 'User')
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
hotel_name = st.session_state.get('hotel_name', 'Hotel 1')

st.title(f"💰 {hotel_name} - Financial Summary")

# Load all financial data with error handling
try:
    sales = load_data('sales.json', selected_hotel)
    if not isinstance(sales, list):
        sales = []
except:
    sales = []

try:
    expenditures = load_data('expenditures.json', selected_hotel)
    if not isinstance(expenditures, list):
        expenditures = []
except:
    expenditures = []

try:
    cash_handovers = load_data('cash_handovers.json', selected_hotel)
    if not isinstance(cash_handovers, list):
        cash_handovers = []
except:
    cash_handovers = []

try:
    account_handovers = load_data('account_handovers.json', selected_hotel)
    if not isinstance(account_handovers, list):
        account_handovers = []
except:
    account_handovers = []

try:
    outstanding_dues = load_data('outstanding_dues.json', selected_hotel)
    if not isinstance(outstanding_dues, list):
        outstanding_dues = []
except:
    outstanding_dues = []

try:
    advance_payments = load_data('advance_payments.json', selected_hotel)
    if not isinstance(advance_payments, list):
        advance_payments = []
except:
    advance_payments = []

try:
    bad_debts = load_data('bad_debts.json', selected_hotel)
    if not isinstance(bad_debts, list):
        bad_debts = []
except:
    bad_debts = []

try:
    discounts = load_data('discounts.json', selected_hotel)
    if not isinstance(discounts, list):
        discounts = []
except:
    discounts = []

try:
    rooms = load_data('rooms.json', selected_hotel)
    if not isinstance(rooms, dict):
        rooms = {}
except:
    rooms = {}

try:
    room_services = load_data('room_services.json', selected_hotel)
    if not isinstance(room_services, list):
        room_services = []
except:
    room_services = []

try:
    complementary_rooms = load_data('complementary_rooms.json', selected_hotel)
    if not isinstance(complementary_rooms, list):
        complementary_rooms = []
except:
    complementary_rooms = []

try:
    uploaded_bills = load_data('uploaded_bills.json', selected_hotel)
    if not isinstance(uploaded_bills, list):
        uploaded_bills = []
except:
    uploaded_bills = []

# Date filter section
st.markdown("### 📅 Date Filter")
col1, col2, col3 = st.columns(3)

with col1:
    date_filter = st.selectbox("Filter Period", ["Today", "This Week", "This Month", "This Year", "All Time", "Custom Range"])

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
def filter_by_date(data, date_filter, start_date=None, end_date=None):
    if date_filter == "All Time":
        return data

    # For rooms data (which is a dict), return as-is since rooms don't have dates
    if isinstance(data, dict) and any(isinstance(v, dict) and 'room_number' in v for v in data.values()):
        return data

    # For list data with date fields
    if not isinstance(data, list):
        return data

    today = datetime.now()

    if date_filter == "Today":
        target_date = today.strftime('%Y-%m-%d')
        return [item for item in data if isinstance(item, dict) and 'date' in item and item['date'].startswith(target_date)]
    elif date_filter == "This Week":
        week_start = (today - timedelta(days=today.weekday())).strftime('%Y-%m-%d')
        return [item for item in data if isinstance(item, dict) and 'date' in item and item['date'] >= week_start]
    elif date_filter == "This Month":
        month_start = today.strftime('%Y-%m')
        return [item for item in data if isinstance(item, dict) and 'date' in item and item['date'].startswith(month_start)]
    elif date_filter == "This Year":
        year_start = today.strftime('%Y')
        return [item for item in data if isinstance(item, dict) and 'date' in item and item['date'].startswith(year_start)]
    elif date_filter == "Custom Range" and start_date and end_date:
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        return [item for item in data if isinstance(item, dict) and 'date' in item and start_str <= item['date'][:10] <= end_str]

    return data

# Enhanced filter function for advance payments
def filter_sales_by_date(sales_data, date_filter, start_date=None, end_date=None):
    """Filter sales using completion date for completed advance payments, otherwise regular date"""
    if date_filter == "All Time":
        return sales_data

    today = datetime.now()
    filtered_data = []

    for sale in sales_data:
        # For advance payments, use completion date if available, otherwise use transaction date
        if 'Advance Payment' in sale.get('type', '') and sale.get('completion_date'):
            # Use completion date for completed advance payments
            display_date = sale['completion_date']
        elif sale.get('transaction_date'):
            # Use transaction date if available
            display_date = sale['transaction_date'][:10]
        else:
            # Fall back to regular date
            display_date = sale['date'][:10]

        try:
            sale_datetime = datetime.strptime(display_date, '%Y-%m-%d')
        except ValueError:
            # If date parsing fails, skip this record
            continue

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

    return filtered_data

# Filter all data
filtered_sales = filter_sales_by_date(sales, date_filter, start_date, end_date)
filtered_expenditures = filter_by_date(expenditures, date_filter, start_date, end_date)
filtered_handovers = filter_by_date(cash_handovers, date_filter, start_date, end_date)
filtered_account_handovers = filter_by_date(account_handovers, date_filter, start_date, end_date)
filtered_rooms = filter_by_date(rooms, date_filter, start_date, end_date)
filtered_room_services = filter_by_date(room_services, date_filter, start_date, end_date)
filtered_complementary_rooms = filter_by_date(complementary_rooms, date_filter, start_date, end_date)
filtered_uploaded_bills = filter_by_date(uploaded_bills, date_filter, start_date, end_date)

st.markdown("---")

# Financial Overview Section
st.markdown("### 💰 Financial Overview")

# Calculate totals
total_sales = sum(sale['amount'] for sale in filtered_sales)
cash_sales = sum(sale['amount'] for sale in filtered_sales if sale['payment_type'] == 'Cash')
account_sales = sum(sale['amount'] for sale in filtered_sales if sale['payment_type'] == 'Account')

total_expenditures = sum(exp['amount'] for exp in filtered_expenditures)
# Fix cash expenditures calculation - check for various cash payment methods
cash_expenditures = sum(exp['amount'] for exp in filtered_expenditures 
                       if exp.get('payment_method', '').lower() in ['cash', 'cash payment'])
# Fix account expenditures calculation
account_expenditures = sum(exp['amount'] for exp in filtered_expenditures 
                          if exp.get('payment_method', '').lower() in ['bank transfer', 'account', 'bank', 'online transfer'])

total_handovers = sum(handover['amount'] for handover in filtered_handovers)
total_account_handovers = sum(handover['amount'] for handover in filtered_account_handovers)

# Outstanding and advance amounts (always show all, not filtered)
outstanding_amount = sum(due['amount'] for due in outstanding_dues if due['status'] == 'Pending')
advance_amount = sum(ap['amount'] for ap in advance_payments if ap['status'] == 'Pending')
bad_debt_amount = sum(bd['amount'] for bd in bad_debts)
discount_amount = sum(disc['amount'] for disc in discounts)

# Calculate balances correctly
cash_balance = cash_sales - cash_expenditures - total_handovers
account_balance = account_sales - account_expenditures - total_account_handovers
net_profit = total_sales - total_expenditures

# Display metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Sales", f"₹{total_sales:,.2f}")
    st.metric("Cash Sales", f"₹{cash_sales:,.2f}", help="Cash received from sales")
    st.metric("Account Sales", f"₹{account_sales:,.2f}", help="Credit/Account sales")

with col2:
    st.metric("Total Expenditures", f"₹{total_expenditures:,.2f}")
    st.metric("Cash Expenditures", f"₹{cash_expenditures:,.2f}", help="Cash payments made")
    st.metric("Account Expenditures", f"₹{account_expenditures:,.2f}", help="Bank/Account payments")

with col3:
    st.metric("Cash Handovers", f"₹{total_handovers:,.2f}", help="Cash handed over to management")
    st.metric("Account Handovers", f"₹{total_account_handovers:,.2f}", help="Account amounts handed over")

    # Show cash balance with color coding
    cash_color = "normal" if cash_balance >= 0 else "inverse"
    st.metric("Cash in Hand", f"₹{cash_balance:,.2f}", 
              help=f"Cash Sales: ₹{cash_sales:,.2f} - Cash Expenses: ₹{cash_expenditures:,.2f} - Cash Handovers: ₹{total_handovers:,.2f}")

    # Show account balance with color coding  
    account_color = "normal" if account_balance >= 0 else "inverse"
    st.metric("Account Balance", f"₹{account_balance:,.2f}", 
              help=f"Account Sales: ₹{account_sales:,.2f} - Account Expenses: ₹{account_expenditures:,.2f} - Account Handovers: ₹{total_account_handovers:,.2f}")

with col4:
    st.metric("Outstanding Dues", f"₹{outstanding_amount:,.2f}", help="Pending receivables")
    st.metric("Advance Payments", f"₹{advance_amount:,.2f}", help="Customer advances held")
    st.metric("Bad Debts", f"₹{bad_debt_amount:,.2f}", help="Irrecoverable amounts")

with col5:
    st.metric("Net Profit", f"₹{net_profit:,.2f}", help="Total sales minus expenditures")
    st.metric("Discounts Given", f"₹{discount_amount:,.2f}", help="Total discounts provided")
    profit_margin = (net_profit / total_sales * 100) if total_sales > 0 else 0
    st.metric("Profit Margin", f"{profit_margin:.1f}%", help="Net profit percentage")

st.markdown("---")

# Add detailed breakdown for debugging
with st.expander("🔍 Detailed Calculation Breakdown", expanded=False):
    st.markdown("#### Cash Flow Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Cash Transactions:**")
        st.write(f"Cash Sales: ₹{cash_sales:,.2f}")
        st.write(f"Cash Expenditures: ₹{cash_expenditures:,.2f}")
        st.write(f"Cash Handovers: ₹{total_handovers:,.2f}")
        st.write(f"**Cash in Hand: ₹{cash_balance:,.2f}**")

        # Show cash expenditure details
        if filtered_expenditures:
            st.markdown("**Cash Expenditure Methods:**")
            cash_methods = {}
            for exp in filtered_expenditures:
                method = exp.get('payment_method', 'Unknown')
                if method.lower() in ['cash', 'cash payment']:
                    cash_methods[method] = cash_methods.get(method, 0) + exp['amount']
            for method, amount in cash_methods.items():
                st.write(f"• {method}: ₹{amount:,.2f}")

    with col2:
        st.markdown("**Account Transactions:**")
        st.write(f"Account Sales: ₹{account_sales:,.2f}")
        st.write(f"Account Expenditures: ₹{account_expenditures:,.2f}")
        st.write(f"Account Handovers: ₹{total_account_handovers:,.2f}")
        st.write(f"**Account Balance: ₹{account_balance:,.2f}**")

        # Show account expenditure details
        if filtered_expenditures:
            st.markdown("**Account Expenditure Methods:**")
            account_methods = {}
            for exp in filtered_expenditures:
                method = exp.get('payment_method', 'Unknown')
                if method.lower() in ['bank transfer', 'account', 'bank', 'online transfer']:
                    account_methods[method] = account_methods.get(method, 0) + exp['amount']
            for method, amount in account_methods.items():
                st.write(f"• {method}: ₹{amount:,.2f}")

# Cash Flow Analysis
st.markdown("### 💵 Cash Flow Analysis")

col1, col2 = st.columns(2)

with col1:
    # Cash flow chart - improved visualization
    cash_inflow = cash_sales
    cash_outflow = cash_expenditures + total_handovers

    fig_cash = go.Figure()

    # Add inflow
    fig_cash.add_trace(go.Bar(
        x=['Cash Inflow'],
        y=[cash_inflow],
        name='Cash Inflow',
        marker_color='green',
        text=f"₹{cash_inflow:,.0f}",
        textposition="outside"
    ))

    # Add outflows
    fig_cash.add_trace(go.Bar(
        x=['Cash Outflow'],
        y=[-cash_outflow],
        name='Cash Outflow',
        marker_color='red',
        text=f"₹{cash_outflow:,.0f}",
        textposition="outside"
    ))

    # Add balance
    balance_color = 'green' if cash_balance >= 0 else 'red'
    fig_cash.add_trace(go.Bar(
        x=['Cash Balance'],
        y=[cash_balance],
        name='Cash Balance',
        marker_color=balance_color,
        text=f"₹{cash_balance:,.0f}",
        textposition="outside"
    ))

    fig_cash.update_layout(
        title="Cash Flow Analysis", 
        showlegend=False, 
        yaxis_title="Amount (₹)",
        xaxis_title="Cash Flow Components"
    )
    st.plotly_chart(fig_cash, use_container_width=True)

with col2:
    # Account flow chart - improved visualization
    account_inflow = account_sales
    account_outflow = account_expenditures + total_account_handovers

    fig_account = go.Figure()

    # Add inflow
    fig_account.add_trace(go.Bar(
        x=['Account Inflow'],
        y=[account_inflow],
        name='Account Inflow',
        marker_color='green',
        text=f"₹{account_inflow:,.0f}",
        textposition="outside"
    ))

    # Add outflows
    fig_account.add_trace(go.Bar(
        x=['Account Outflow'],
        y=[-account_outflow],
        name='Account Outflow',
        marker_color='red',
        text=f"₹{account_outflow:,.0f}",
        textposition="outside"
    ))

    # Add balance
    acc_balance_color = 'green' if account_balance >= 0 else 'red'
    fig_account.add_trace(go.Bar(
        x=['Account Balance'],
        y=[account_balance],
        name='Account Balance',
        marker_color=acc_balance_color,
        text=f"₹{account_balance:,.0f}",
        textposition="outside"
    ))

    fig_account.update_layout(
        title="Account Flow Analysis", 
        showlegend=False, 
        yaxis_title="Amount (₹)",
        xaxis_title="Account Flow Components"
    )
    st.plotly_chart(fig_account, use_container_width=True)

st.markdown("---")

# Detailed Records Section
st.markdown("### 📋 Detailed Records")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Sales Records", "Expenditure Records", "Cash Handovers", "Account Handovers", "Summary Report"])

with tab1:
    st.markdown("#### Sales Records")
    if filtered_sales:
        # Create enhanced sales display
        sales_display = []
        for sale in filtered_sales:
            display_record = {
                'Display Date': sale.get('original_advance_date', sale['date'][:10]),
                'Type': sale['type'],
                'Customer': sale['customer_name'],
                'Amount': f"₹{sale['amount']:,.2f}",
                'Payment Type': sale['payment_type'],
                'Status': sale.get('status', 'Completed')
            }

            # Add advance payment info if applicable
            if sale.get('original_advance_date'):
                display_record['Note'] = f"Advance Payment (Payment Date: {sale.get('transaction_date', sale['date'])[:10]})"
                display_record['Advance Date'] = sale['original_advance_date']
            else:
                display_record['Note'] = 'Regular Sale'
                display_record['Advance Date'] = 'N/A'

            sales_display.append(display_record)

        sales_df = pd.DataFrame(sales_display)
        st.dataframe(sales_df, use_container_width=True)

        # Show advance payment info
        advance_sales = [s for s in filtered_sales if s.get('original_advance_date')]
        if advance_sales:
            st.info(f"ℹ️ {len(advance_sales)} advance payment(s) shown on their original advance dates")

        # Sales summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Total Records:** {len(filtered_sales)}")
        with col2:
            st.write(f"**Cash Sales:** ₹{cash_sales:,.2f}")
        with col3:
            st.write(f"**Account Sales:** ₹{account_sales:,.2f}")
    else:
        st.info("No sales records found for the selected period")

with tab2:
    st.markdown("#### Expenditure Records")
    if filtered_expenditures:
        exp_df = pd.DataFrame(filtered_expenditures)
        exp_df['Amount'] = exp_df['amount'].apply(lambda x: f"₹{x:,.2f}")
        display_columns = ['date', 'category', 'vendor_name', 'Amount', 'payment_method', 'status']
        available_columns = [col for col in display_columns if col in exp_df.columns]
        st.dataframe(exp_df[available_columns], use_container_width=True)

        # Expenditure summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Total Records:** {len(filtered_expenditures)}")
        with col2:
            st.write(f"**Cash Expenditures:** ₹{cash_expenditures:,.2f}")
        with col3:
            st.write(f"**Account Expenditures:** ₹{account_expenditures:,.2f}")
    else:
        st.info("No expenditure records found for the selected period")

with tab3:
    st.markdown("#### Cash Handover Records")
    if filtered_handovers:
        handover_df = pd.DataFrame(filtered_handovers)
        handover_df['Amount'] = handover_df['amount'].apply(lambda x: f"₹{x:,.2f}")
        display_columns = ['date', 'received_by', 'Amount', 'notes']
        available_columns = [col for col in display_columns if col in handover_df.columns]
        st.dataframe(handover_df[available_columns], use_container_width=True)

        st.write(f"**Total Cash Handovers:** ₹{total_handovers:,.2f}")
    else:
        st.info("No cash handover records found for the selected period")

with tab4:
    st.markdown("#### Account Handover Records")
    if filtered_account_handovers:
        acc_handover_df = pd.DataFrame(filtered_account_handovers)
        acc_handover_df['Amount'] = acc_handover_df['amount'].apply(lambda x: f"₹{x:,.2f}")
        display_columns = ['date', 'received_by', 'Amount', 'handover_type', 'reference_number', 'notes']
        available_columns = [col for col in display_columns if col in acc_handover_df.columns]
        st.dataframe(acc_handover_df[available_columns], use_container_width=True)

        st.write(f"**Total Account Handovers:** ₹{total_account_handovers:,.2f}")
    else:
        st.info("No account handover records found for the selected period")

with tab5:
    st.markdown("#### Summary Report")

    # Create summary data
    summary_data = {
        "Category": [
            "Total Sales", "Cash Sales", "Account Sales",
            "Total Expenditures", "Cash Expenditures", "Account Expenditures",
            "Cash Handovers", "Account Handovers", "Cash in Hand", "Account Balance", "Net Profit"
        ],
        "Amount": [
            total_sales, cash_sales, account_sales,
            total_expenditures, cash_expenditures, account_expenditures,
            total_handovers, total_account_handovers, cash_balance, account_balance, net_profit
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df['Amount'] = summary_df['Amount'].apply(lambda x: f"₹{x:,.2f}")

    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # Additional metrics
    st.markdown("#### Additional Information")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Report Period:** {date_filter}")
        if date_filter == "Custom Range" and start_date and end_date:
            st.write(f"**From:** {start_date} **To:** {end_date}")
        st.write(f"**Report Generated:** {get_current_date()}")
        st.write(f"**Generated By:** {st.session_state.get('username', 'Unknown')}")

    with col2:
        st.write(f"**Outstanding Dues:** ₹{outstanding_amount:,.2f}")
        st.write(f"**Advance Payments:** ₹{advance_amount:,.2f}")
        st.write(f"**Bad Debts:** ₹{bad_debt_amount:,.2f}")
        st.write(f"**Discounts Given:** ₹{discount_amount:,.2f}")

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

# Restaurant analytics - only show for Saz Valley Bhaderwah
if selected_hotel == 'hotel2':
    restaurant_sales = [s for s in filtered_sales if s.get('type') == 'Restaurant']
    if restaurant_sales:
        st.markdown("---")
        st.markdown("### 🍽️ Restaurant Analytics - Saz Valley Bhaderwah")

        restaurant_total = sum(sale['amount'] for sale in restaurant_sales)
        restaurant_cash = sum(sale['amount'] for sale in restaurant_sales if sale.get('payment_type') == 'Cash')
        restaurant_account = sum(sale['amount'] for sale in restaurant_sales if sale.get('payment_type') == 'Account')

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Restaurant Revenue", f"₹{restaurant_total:,.2f}")
            st.metric("Restaurant Cash Sales", f"₹{restaurant_cash:,.2f}")
            st.metric("Restaurant Account Sales", f"₹{restaurant_account:,.2f}")

            # Restaurant share of total sales
            restaurant_percentage = (restaurant_total / total_sales * 100) if total_sales > 0 else 0
            st.metric("Restaurant Share", f"{restaurant_percentage:.1f}%")

        with col2:
            # Order type breakdown - safely access order_type
            dine_in_sales = sum(sale['amount'] for sale in restaurant_sales if 'Dine In' in str(sale.get('order_type', '')))
            room_service_rest_sales = sum(sale['amount'] for sale in restaurant_sales if 'Room Service' in str(sale.get('order_type', '')))

            st.metric("Dine In Sales", f"₹{dine_in_sales:,.2f}")
            st.metric("Restaurant Room Service", f"₹{room_service_rest_sales:,.2f}")
            st.metric("Total Restaurant Orders", len(restaurant_sales))

            # Average order value
            avg_order_value = restaurant_total / len(restaurant_sales) if restaurant_sales else 0
            st.metric("Average Order Value", f"₹{avg_order_value:,.0f}")

        # Top restaurant customers
        if restaurant_sales:
            st.markdown("#### Top Restaurant Customers")
            customer_totals = {}
            for sale in restaurant_sales:
                customer = sale.get('customer_name', 'Unknown')
                customer_totals[customer] = customer_totals.get(customer, 0) + sale['amount']

            if customer_totals:
                top_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:5]
                for i, (customer, total) in enumerate(top_customers, 1):
                    st.write(f"{i}. **{customer}**: ₹{total:,.2f}")

        # Restaurant payment type chart
        if restaurant_sales and (restaurant_cash > 0 or restaurant_account > 0):
            col1, col2 = st.columns(2)

            with col1:
                payment_data = {}
                if restaurant_cash > 0:
                    payment_data["Cash"] = restaurant_cash
                if restaurant_account > 0:
                    payment_data["Account"] = restaurant_account

                if payment_data:
                    fig_restaurant_payment = px.pie(
                        values=list(payment_data.values()), 
                        names=list(payment_data.keys()), 
                        title="Restaurant Payment Types"
                    )
                    st.plotly_chart(fig_restaurant_payment, use_container_width=True)

            with col2:
                order_type_data = {}
                if dine_in_sales > 0:
                    order_type_data["Dine In"] = dine_in_sales
                if room_service_rest_sales > 0:
                    order_type_data["Room Service"] = room_service_rest_sales

                if order_type_data:
                    fig_restaurant_type = px.pie(
                        values=list(order_type_data.values()), 
                        names=list(order_type_data.keys()), 
                        title="Restaurant Order Types"
                    )
                    st.plotly_chart(fig_restaurant_type, use_container_width=True)

st.markdown("---")

# Download All Data Section
st.markdown("### 📥 Download All Data")

if st.button("📦 Download All Hotel Data as ZIP"):
    try:
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all data files to ZIP
            data_files = [
                ('sales.json', sales),
                ('expenditures.json', expenditures),
                ('cash_handovers.json', cash_handovers),
                ('account_handovers.json', account_handovers),
                ('outstanding_dues.json', outstanding_dues),
                ('advance_payments.json', advance_payments),
                ('bad_debts.json', bad_debts),
                ('discounts.json', discounts),
                ('rooms.json', rooms),
                ('room_services.json', room_services),
                ('complementary_rooms.json', complementary_rooms),
                ('uploaded_bills.json', uploaded_bills)
            ]

            # Add each data file to ZIP
            for filename, data in data_files:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                zip_file.writestr(filename, json_str)

            # Add summary report
            summary_report = {
                "hotel_name": hotel_name,
                "report_generated": get_current_date(),
                "generated_by": st.session_state.get('username', 'Unknown'),
                "financial_summary": {
                    "total_sales": total_sales,
                    "cash_sales": cash_sales,
                    "account_sales": account_sales,
                    "total_expenditures": total_expenditures,
                    "cash_expenditures": cash_expenditures,
                    "account_expenditures": account_expenditures,
                    "cash_handovers": total_handovers,
                    "account_handovers": total_account_handovers,
                    "cash_balance": cash_balance,
                    "account_balance": account_balance,
                    "net_profit": net_profit,
                    "outstanding_dues": outstanding_amount,
                    "advance_payments": advance_amount,
                    "bad_debts": bad_debt_amount,
                    "discounts": discount_amount
                }
            }

            zip_file.writestr('summary_report.json', json.dumps(summary_report, indent=2, ensure_ascii=False))

        zip_buffer.seek(0)

        st.download_button(
            label="📥 Download All Data",
            data=zip_buffer.getvalue(),
            file_name=f"{hotel_name.lower().replace(' ', '_')}_complete_data_{get_current_date()}.zip",
            mime="application/zip"
        )

        st.success("✅ All data prepared for download!")

    except Exception as e:
        st.error(f"Error creating download file: {str(e)}")

st.markdown("---")

# Export Section
st.markdown("### 📄 Export Options")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export Summary to CSV"):
        # Create comprehensive summary for export
        export_data = []

        # Add summary metrics
        export_data.extend([
            ["FINANCIAL SUMMARY", "", "", ""],
            ["Report Period", date_filter, "", ""],
            ["Generated Date", get_current_date(), "", ""],
            ["Generated By", st.session_state.get('username', 'Unknown'), "", ""],
            ["", "", "", ""],
            ["SALES SUMMARY", "", "", ""],
            ["Total Sales", f"₹{total_sales:,.2f}", "", ""],
            ["Cash Sales", f"₹{cash_sales:,.2f}", "", ""],
            ["Account Sales", f"₹{account_sales:,.2f}", "", ""],
            ["", "", "", ""],
            ["EXPENDITURE SUMMARY", "", "", ""],
            ["Total Expenditures", f"₹{total_expenditures:,.2f}", "", ""],
            ["Cash Expenditures", f"₹{cash_expenditures:,.2f}", "", ""],
            ["Account Expenditures", f"₹{account_expenditures:,.2f}", "", ""],
            ["", "", "", ""],
            ["BALANCE SUMMARY", "", "", ""],
            ["Cash in Hand", f"₹{cash_balance:,.2f}", "", ""],
            ["Account Balance", f"₹{account_balance:,.2f}", "", ""],
            ["Net Profit", f"₹{net_profit:,.2f}", "", ""],
            ["", "", "", ""],
            ["OTHER METRICS", "", "", ""],
            ["Outstanding Dues", f"₹{outstanding_amount:,.2f}", "", ""],
            ["Advance Payments", f"₹{advance_amount:,.2f}", "", ""],
            ["Bad Debts", f"₹{bad_debt_amount:,.2f}", "", ""],
            ["Discounts Given", f"₹{discount_amount:,.2f}", "", ""]
        ])

        export_df = pd.DataFrame(export_data, columns=['Category', 'Value', 'Notes', 'Extra'])

        csv_buffer = io.StringIO()
        export_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{hotel_name.lower().replace(' ', '_')}_financial_summary_{get_current_date()}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📈 Export Charts Data"):
        # Export chart data
        chart_data = {
            "payment_type_data": {
                "cash_sales": cash_sales,
                "account_sales": account_sales
            },
            "balance_data": {
                "cash_balance": cash_balance,
                "account_balance": account_balance
            },
            "flow_data": {
                "cash_inflow": cash_sales,
                "cash_outflow": cash_expenditures + total_handovers,
                "account_inflow": account_sales,
                "account_outflow": account_expenditures + total_account_handovers
            }
        }

        json_str = json.dumps(chart_data, indent=2)

        st.download_button(
            label="📥 Download Chart Data",
            data=json_str,
            file_name=f"{hotel_name.lower().replace(' ', '_')}_charts_data_{get_current_date()}.json",
            mime="application/json"
        )

with col3:
    if st.button("🔍 Export Detailed Records"):
        # Create detailed export with all transactions
        detailed_data = {
            "sales_records": filtered_sales,
            "expenditure_records": filtered_expenditures,
            "cash_handover_records": filtered_handovers,
            "account_handover_records": filtered_account_handovers,
            "metadata": {
                "hotel_name": hotel_name,
                "date_filter": date_filter,
                "generated_date": get_current_date(),
                "generated_by": st.session_state.get('username', 'Unknown')
            }
        }

        json_str = json.dumps(detailed_data, indent=2, ensure_ascii=False)

        st.download_button(
            label="📥 Download Detailed Records",
            data=json_str,
            file_name=f"{hotel_name.lower().replace(' ', '_')}_detailed_records_{get_current_date()}.json",
            mime="application/json"
        )
# The financial summary now loads all relevant financial data from the database for comprehensive reporting.