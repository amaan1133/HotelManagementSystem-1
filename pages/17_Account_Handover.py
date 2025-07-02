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

st.title("🏦 Account Handover")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
account_handovers = load_data('account_handovers.json', selected_hotel)
sales = load_data('sales.json', selected_hotel)

# Filter account sales
account_sales = [s for s in sales if s['payment_type'] == 'Account']

# Calculate account amounts
total_account_sales = sum(sale['amount'] for sale in account_sales)
total_handed_over = sum(handover['amount'] for handover in account_handovers)
account_balance = total_account_sales - total_handed_over

# Overview
st.markdown("### Account Handover Overview")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Account Sales", f"₹{total_account_sales:,.2f}")
with col2:
    st.metric("Total Handed Over", f"₹{total_handed_over:,.2f}")
with col3:
    st.metric("Account Balance", f"₹{account_balance:,.2f}")

st.markdown("---")

# Record account handover
st.markdown("### Record Account Handover")

with st.form("account_handover_form"):
    col1, col2 = st.columns(2)

    with col1:
        handover_amount = st.number_input("Handover Amount", value=float(account_balance) if account_balance > 0 else 0.0, min_value=0.0, step=100.0)
        received_by = st.text_input("Received By", placeholder="Name of person/department receiving account")
        handover_type = st.selectbox("Handover Type", ["Bank Transfer", "Account Settlement", "Management Transfer", "Other"])

    with col2:
        handover_date = st.date_input("Handover Date")
        reference_number = st.text_input("Reference Number", placeholder="Transaction/Reference number")
        notes = st.text_area("Notes", placeholder="Any additional notes")

    if st.form_submit_button("Record Account Handover", type="primary"):
        if received_by and handover_amount > 0:
            new_handover = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'handover_date': str(handover_date),
                'amount': handover_amount,
                'received_by': received_by,
                'handover_type': handover_type,
                'reference_number': reference_number,
                'notes': notes,
                'handed_by': st.session_state.get('username', 'Unknown')
            }
            account_handovers.append(new_handover)
            save_data('account_handovers.json', account_handovers, selected_hotel)
            st.success(f"Account handover of ₹{handover_amount:,.2f} recorded successfully!")
            st.rerun()
        else:
            st.error("Please enter valid amount and receiver name")

st.markdown("---")

# Handover history
st.markdown("### Account Handover History")

if account_handovers:
    for handover in sorted(account_handovers, key=lambda x: x['date'], reverse=True):
        with st.expander(f"#{handover['id']} - ₹{handover['amount']:,.2f} to {handover['received_by']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {handover['date']}")
                st.write(f"**Handover Date:** {handover['handover_date']}")
                st.write(f"**Amount:** ₹{handover['amount']:,.2f}")
                st.write(f"**Type:** {handover.get('handover_type', 'N/A')}")

            with col2:
                st.write(f"**Received By:** {handover['received_by']}")
                st.write(f"**Handed By:** {handover['handed_by']}")
                st.write(f"**Reference:** {handover.get('reference_number', 'N/A')}")

            if handover.get('notes'):
                st.write(f"**Notes:** {handover['notes']}")

            # Admin actions
            if user_role == 'Admin':
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Edit", key=f"edit_{handover['id']}"):
                        with st.form(f"edit_handover_{handover['id']}"):
                            new_amount = st.number_input("Amount", value=handover['amount'], min_value=0.0)
                            new_received_by = st.text_input("Received By", value=handover['received_by'])
                            new_reference = st.text_input("Reference Number", value=handover.get('reference_number', ''))
                            if st.form_submit_button("Update Handover"):
                                for h in account_handovers:
                                    if h['id'] == handover['id']:
                                        h['amount'] = new_amount
                                        h['received_by'] = new_received_by
                                        h['reference_number'] = new_reference
                                        break
                                save_data('account_handovers.json', account_handovers, selected_hotel)
                                st.success("Account handover updated!")
                                st.rerun()

                with col2:
                    if st.button(f"Delete", key=f"delete_{handover['id']}", type="secondary"):
                        account_handovers = [h for h in account_handovers if h['id'] != handover['id']]
                        save_data('account_handovers.json', account_handovers, selected_hotel)
                        st.success("Account handover record deleted!")
                        st.rerun()
else:
    st.info("No account handover records found")

# Today's account summary
st.markdown("---")
st.markdown("### Today's Account Summary")

today_account_sales = sum(sale['amount'] for sale in account_sales if sale['date'].startswith('2025-06-24'))
today_handovers = sum(handover['amount'] for handover in account_handovers if handover['date'].startswith('2025-06-24'))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Today's Account Sales", f"₹{today_account_sales:,.2f}")
with col2:
    st.metric("Today's Account Handovers", f"₹{today_handovers:,.2f}")
with col3:
    st.metric("Today's Account Balance", f"₹{today_account_sales - today_handovers:,.2f}")

# Account handover analytics
if account_handovers:
    st.markdown("---")
    st.markdown("### Account Handover Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Handover by type
        type_data = {}
        for handover in account_handovers:
            handover_type = handover.get('handover_type', 'Unknown')
            type_data[handover_type] = type_data.get(handover_type, 0) + handover['amount']

        if type_data:
            import plotly.express as px
            fig_type = px.pie(
                values=list(type_data.values()), 
                names=list(type_data.keys()), 
                title="Account Handovers by Type"
            )
            st.plotly_chart(fig_type, use_container_width=True)

    with col2:
        # Monthly handover trends
        monthly_handovers = {}
        for handover in account_handovers:
            month = handover['date'][:7]  # YYYY-MM
            monthly_handovers[month] = monthly_handovers.get(month, 0) + handover['amount']

        if monthly_handovers:
            fig_monthly = px.bar(
                x=list(monthly_handovers.keys()), 
                y=list(monthly_handovers.values()), 
                title="Monthly Account Handovers"
            )
            st.plotly_chart(fig_monthly, use_container_width=True)