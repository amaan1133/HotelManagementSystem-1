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

st.title("💰 Cash Handover")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
cash_handovers = load_data('cash_handovers.json', selected_hotel)
sales = load_data('sales.json', selected_hotel)

# Filter cash sales
cash_sales = [s for s in sales if s['payment_type'] == 'Cash']

# Calculate cash amounts
total_cash_sales = sum(sale['amount'] for sale in cash_sales)
total_handed_over = sum(handover['amount'] for handover in cash_handovers)
cash_in_hand = total_cash_sales - total_handed_over

# Overview
st.markdown("### Cash Handover Overview")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Cash Sales", f"₹{total_cash_sales:,.2f}")
with col2:
    st.metric("Total Handed Over", f"₹{total_handed_over:,.2f}")
with col3:
    st.metric("Cash in Hand", f"₹{cash_in_hand:,.2f}")

st.markdown("---")

# Record cash handover
st.markdown("### Record Cash Handover")

with st.form("cash_handover_form"):
    col1, col2 = st.columns(2)

    with col1:
        handover_amount = st.number_input("Handover Amount", value=float(cash_in_hand) if cash_in_hand > 0 else 0.0, min_value=0.0, step=100.0)
        received_by = st.text_input("Received By", placeholder="Name of person receiving cash")

    with col2:
        handover_date = st.date_input("Handover Date")
        notes = st.text_area("Notes", placeholder="Any additional notes")

    if st.form_submit_button("Record Handover", type="primary"):
        if received_by and handover_amount > 0:
            new_handover = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'handover_date': str(handover_date),
                'amount': handover_amount,
                'received_by': received_by,
                'notes': notes,
                'handed_by': st.session_state.get('username', 'Unknown')
            }
            cash_handovers.append(new_handover)
            save_data('cash_handovers.json', cash_handovers, selected_hotel)
            st.success(f"Cash handover of ₹{handover_amount:,.2f} recorded successfully!")
            st.rerun()
        else:
            st.error("Please enter valid amount and receiver name")

st.markdown("---")

# Handover history
st.markdown("### Handover History")

if cash_handovers:
    for handover in sorted(cash_handovers, key=lambda x: x['date'], reverse=True):
        handover_date = handover['date'][:10] if handover['date'] else 'N/A'
        with st.expander(f"#{handover['id']} - ₹{handover['amount']:,.2f} to {handover['received_by']} - {handover_date}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {handover['date']}")
                st.write(f"**Handover Date:** {handover['handover_date']}")
                st.write(f"**Amount:** ₹{handover['amount']:,.2f}")

            with col2:
                st.write(f"**Received By:** {handover['received_by']}")
                st.write(f"**Handed By:** {handover['handed_by']}")

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
                            if st.form_submit_button("Update Handover"):
                                for h in cash_handovers:
                                    if h['id'] == handover['id']:
                                        h['amount'] = new_amount
                                        h['received_by'] = new_received_by
                                        break
                                save_data('cash_handovers.json', cash_handovers, selected_hotel)
                                st.success("Handover updated!")
                                st.rerun()

                with col2:
                    if st.button(f"Delete", key=f"delete_{handover['id']}", type="secondary"):
                        cash_handovers = [h for h in cash_handovers if h['id'] != handover['id']]
                        save_data('cash_handovers.json', cash_handovers, selected_hotel)
                        st.success("Handover record deleted!")
                        st.rerun()
else:
    st.info("No handover records found")

# Today's cash summary
st.markdown("---")
st.markdown("### Today's Cash Summary")

today_cash_sales = sum(sale['amount'] for sale in cash_sales if sale['date'].startswith('2025-06-23'))
today_handovers = sum(handover['amount'] for handover in cash_handovers if handover['date'].startswith('2025-06-23'))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Today's Cash Sales", f"₹{today_cash_sales:,.2f}")
with col2:
    st.metric("Today's Handovers", f"₹{today_handovers:,.2f}")
with col3:
    st.metric("Today's Cash in Hand", f"₹{today_cash_sales - today_handovers:,.2f}")