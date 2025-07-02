import streamlit as st
import sys
import os
from datetime import datetime

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

# All users can add expenditure data, admin can edit/delete
user_role = st.session_state.get('user_role', 'User')

st.title("📊 Expenditure Management")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
expenditures = load_data('expenditures.json', selected_hotel)

# Expenditure overview
st.markdown("### Expenditure Overview")

# Calculate totals
total_expenditure = sum(exp['amount'] for exp in expenditures)
today_expenditure = sum(exp['amount'] for exp in expenditures if exp['date'].startswith('2025-06-23'))
pending_expenditure = sum(exp['amount'] for exp in expenditures if exp.get('status') == 'Pending')

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Expenditure", f"₹{total_expenditure:,.2f}")
with col2:
    st.metric("Today's Expenditure", f"₹{today_expenditure:,.2f}")
with col3:
    st.metric("Pending Payments", f"₹{pending_expenditure:,.2f}")
with col4:
    st.metric("Number of Records", len(expenditures))

st.markdown("---")

# Add new expenditure
st.markdown("### Add New Expenditure")

with st.form("add_expenditure_form"):
    col1, col2 = st.columns(2)

    with col1:
        # Add custom date selection for historical entries
        expense_date = st.date_input("Expenditure Date", value=datetime.now().date(), 
                                   help="Select the date for this expenditure")
        expense_category = st.selectbox("Category", [
            "Staff Salaries", "Utilities", "Maintenance", "Supplies", 
            "Marketing", "Food & Beverage", "Laundry", "Other"
        ])
        amount = st.number_input("Amount", min_value=0.0, step=100.0, format="%.2f")
        payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Card", "Cheque"])

    with col2:
        vendor_name = st.text_input("Vendor/Payee Name", placeholder="Enter vendor name")
        description = st.text_area("Description", placeholder="Expenditure description")
        status = st.selectbox("Status", ["Completed", "Pending", "Approved"])

    submit_expenditure = st.form_submit_button("Add Expenditure", type="primary")

    if submit_expenditure:
        if not vendor_name or amount <= 0:
            st.error("Vendor name and valid amount are required")
        else:
            new_expenditure = {
                'id': generate_id(),
                'date': expense_date.strftime('%Y-%m-%d %H:%M:%S'),
                'category': expense_category,
                'amount': amount,
                'payment_method': payment_method,
                'vendor_name': vendor_name,
                'description': description,
                'status': status,
                'created_by': st.session_state.get('username', 'Unknown')
            }

            # Add to expenditures data and save
            if add_record('expenditures.json', new_expenditure, selected_hotel):
                st.success("Expenditure added successfully!")
            else:
                st.error("Failed to add expenditure record")
            st.rerun()

st.markdown("---")

# Expenditure list and management
st.markdown("### Expenditure Records")

if expenditures:
    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + list(set(exp['category'] for exp in expenditures)))
    with col2:
        filter_payment = st.selectbox("Filter by Payment Method", ["All"] + list(set(exp['payment_method'] for exp in expenditures)))
    with col3:
        filter_status = st.selectbox("Filter by Status", ["All", "Completed", "Pending", "Approved"])

    # Apply filters
    filtered_expenditures = expenditures
    if filter_category != "All":
        filtered_expenditures = [e for e in filtered_expenditures if e['category'] == filter_category]
    if filter_payment != "All":
        filtered_expenditures = [e for e in filtered_expenditures if e['payment_method'] == filter_payment]
    if filter_status != "All":
        filtered_expenditures = [e for e in filtered_expenditures if e['status'] == filter_status]

    # Display expenditures
    for exp in filtered_expenditures:
        with st.expander(f"#{exp['id']} - {exp['vendor_name']} - ₹{exp['amount']:,.2f}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Date:** {exp['date']}")
                st.write(f"**Category:** {exp['category']}")
                st.write(f"**Amount:** ₹{exp['amount']:,.2f}")
                st.write(f"**Payment Method:** {exp['payment_method']}")

            with col2:
                st.write(f"**Vendor:** {exp['vendor_name']}")
                st.write(f"**Status:** {exp['status']}")
                st.write(f"**Created by:** {exp.get('created_by', 'Unknown')}")

            if exp.get('description'):
                st.write(f"**Description:** {exp['description']}")

            # Admin actions - Full control over all expenditures
            if user_role == 'Admin':
                col1, col2, col3 = st.columns(3)

                with col1:
                    if exp['status'] == 'Pending' and st.button(f"Approve", key=f"approve_{exp['id']}"):
                        for e in expenditures:
                            if e['id'] == exp['id']:
                                e['status'] = 'Approved'
                                break
                        save_data('expenditures.json', expenditures, selected_hotel)
                        st.success("Expenditure approved!")
                        st.rerun()

                with col2:
                    if st.button(f"Edit", key=f"edit_{exp['id']}"):
                        # Show edit form
                        with st.form(f"edit_exp_{exp['id']}"):
                            new_amount = st.number_input("New Amount", value=exp['amount'], min_value=0.0)
                            new_status = st.selectbox("Status", ["Pending", "Approved", "Completed"], 
                                                    index=["Pending", "Approved", "Completed"].index(exp['status']))
                            if st.form_submit_button("Update Expenditure"):
                                for e in expenditures:
                                    if e['id'] == exp['id']:
                                        e['amount'] = new_amount
                                        e['status'] = new_status
                                        break
                                save_data('expenditures.json', expenditures, selected_hotel)
                                st.success("Expenditure updated successfully!")
                                st.rerun()

                with col3:
                    if st.button(f"Delete", key=f"delete_{exp['id']}", type="secondary"):
                        expenditures = [e for e in expenditures if e['id'] != exp['id']]
                        save_data('expenditures.json', expenditures, selected_hotel)
                        st.success("Expenditure deleted successfully!")
                        st.rerun()

else:
    st.info("No expenditure records found")

# Expenditure analytics
if expenditures:
    st.markdown("---")
    st.markdown("### Expenditure Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Expenditure by category
        df_exp = pd.DataFrame(expenditures)
        category_summary = df_exp.groupby('category')['amount'].sum().reset_index()
        fig_category = px.pie(category_summary, values='amount', names='category', title="Expenditure by Category")
        st.plotly_chart(fig_category, use_container_width=True)

    with col2:
        # Expenditure by status
        status_summary = df_exp.groupby('status')['amount'].sum().reset_index()
        fig_status = px.bar(status_summary, x='status', y='amount', title="Expenditure by Status")
        st.plotly_chart(fig_status, use_container_width=True)

# Monthly expenditure summary
st.markdown("---")
st.markdown("### Monthly Summary")

if expenditures:
    # Group by month (simplified for demo)
    monthly_exp = sum(exp['amount'] for exp in expenditures if exp['date'].startswith('2025-06'))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("This Month", f"₹{monthly_exp:,.2f}")
    with col2:
        avg_daily = monthly_exp / 23 if monthly_exp > 0 else 0  # Assuming 23 days in month so far
        st.metric("Daily Average", f"₹{avg_daily:,.2f}")
    with col3:
        projected_monthly = avg_daily * 30
        st.metric("Projected Monthly", f"₹{projected_monthly:,.2f}")

# Budget tracking
st.markdown("---")
st.markdown("### Budget Tracking")

with st.form("budget_form"):
    st.markdown("Set monthly budget limits for categories:")

    col1, col2 = st.columns(2)

    with col1:
        staff_budget = st.number_input("Staff Salaries Budget", value=50000, step=5000)
        utilities_budget = st.number_input("Utilities Budget", value=15000, step=1000)
        maintenance_budget = st.number_input("Maintenance Budget", value=10000, step=1000)
        supplies_budget = st.number_input("Supplies Budget", value=8000, step=500)

    with col2:
        marketing_budget = st.number_input("Marketing Budget", value=5000, step=500)
        fnb_budget = st.number_input("Food & Beverage Budget", value=12000, step=1000)
        laundry_budget = st.number_input("Laundry Budget", value=3000, step=500)
        other_budget = st.number_input("Other Budget", value=5000, step=500)

    if st.form_submit_button("Save Budget"):
        st.success("Budget limits saved successfully!")

# Budget vs actual comparison (if expenditures exist)
if expenditures:
    st.markdown("#### Budget vs Actual Comparison")

    # This would compare actual spending against budget
    # For demo purposes, showing a simple comparison
    categories = ["Staff Salaries", "Utilities", "Maintenance", "Supplies", "Marketing", "Food & Beverage", "Laundry", "Other"]
    budgets = [50000, 15000, 10000, 8000, 5000, 12000, 3000, 5000]

    comparison_data = []
    for i, category in enumerate(categories):
        actual = sum(exp['amount'] for exp in expenditures if exp['category'] == category)
        comparison_data.append({
            'Category': category,
            'Budget': budgets[i],
            'Actual': actual,
            'Variance': budgets[i] - actual,
            'Utilization %': (actual / budgets[i] * 100) if budgets[i] > 0 else 0
        })

    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)