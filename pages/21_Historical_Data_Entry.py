"""
Historical Data Entry - Enter past data with custom dates
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.auth import check_authentication
from utils.data_integration import data_integration

def main():
    # Check authentication
    if not check_authentication():
        return
    
    st.title("📅 Historical Data Entry")
    st.markdown("Enter past data with custom dates for all modules")
    
    # Get user's hotel
    user_hotel = st.session_state.get('user_hotel', 'hotel1')
    
    # Data entry tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Sales", "Restaurant", "Expenditures", "Room Service", 
        "Advance Payments", "Outstanding Dues", "Complementary Rooms"
    ])
    
    with tab1:
        st.subheader("📊 Historical Sales Entry")
        
        with st.form("historical_sales_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sale_date = st.date_input("Sale Date", value=date.today())
                customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
                description = st.text_input("Description")
                amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01)
            
            with col2:
                payment_type = st.selectbox("Payment Type", ["Cash", "Account"])
                sale_type = st.selectbox("Sale Type", ["Room Booking", "Service", "Other"])
                room_number = st.selectbox("Room Number (Optional)", 
                                         [""] + [f"10{i}" for i in range(1, 9)])
            
            if st.form_submit_button("Add Historical Sale"):
                if description and amount > 0 and customer_name:
                    try:
                        sale_data = {
                            'date': sale_date,
                            'customer_name': customer_name,
                            'description': description,
                            'amount': amount,
                            'payment_type': payment_type,
                            'type': sale_type,
                            'room_number': room_number if room_number else None,
                            'hotel': user_hotel,
                            'created_by': st.session_state.username
                        }
                        
                        if data_integration.add_historical_sale(sale_data, user_hotel):
                            st.success(f"✅ Historical sale added for {sale_date} - Will appear in Sales Management and Dashboard")
                        else:
                            st.error("Failed to add historical sale")
                    except Exception as e:
                        st.error(f"Error adding sale: {e}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab2:
        st.subheader("🍽️ Historical Restaurant Entry")
        
        with st.form("historical_restaurant_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                restaurant_date = st.date_input("Restaurant Sale Date", value=date.today())
                description = st.text_input("Description", key="restaurant_desc")
                amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, key="restaurant_amount")
            
            with col2:
                payment_type = st.selectbox("Payment Type", ["Cash", "Account"], key="restaurant_payment")
            
            if st.form_submit_button("Add Historical Restaurant Entry"):
                if description and amount > 0:
                    try:
                        restaurant_data = {
                            'date': restaurant_date,
                            'description': description,
                            'amount': amount,
                            'payment_type': payment_type,
                            'hotel': user_hotel,
                            'created_by': st.session_state.username
                        }
                        
                        if data_integration.add_historical_restaurant(restaurant_data, user_hotel):
                            st.success(f"✅ Historical restaurant entry added for {restaurant_date} - Will appear in Restaurant and Sales sections")
                        else:
                            st.error("Failed to add historical restaurant entry")
                    except Exception as e:
                        st.error(f"Error adding restaurant entry: {e}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab3:
        st.subheader("💰 Historical Expenditure Entry")
        
        with st.form("historical_expenditure_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                expenditure_date = st.date_input("Expenditure Date", value=date.today())
                description = st.text_input("Description", key="exp_desc")
                amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, key="exp_amount")
            
            with col2:
                category = st.selectbox("Category", [
                    "Staff Salaries", "Utilities", "Maintenance", "Supplies", 
                    "Food & Beverage", "Marketing", "Insurance", "Other"
                ])
            
            if st.form_submit_button("Add Historical Expenditure"):
                if description and amount > 0:
                    try:
                        expenditure_data = {
                            'date': expenditure_date,
                            'description': description,
                            'amount': amount,
                            'category': category,
                            'hotel': user_hotel,
                            'created_by': st.session_state.username
                        }
                        
                        if data_integration.add_historical_expenditure(expenditure_data, user_hotel):
                            st.success(f"✅ Historical expenditure added for {expenditure_date} - Will appear in Expenditure Management and Dashboard")
                        else:
                            st.error("Failed to add historical expenditure")
                    except Exception as e:
                        st.error(f"Error adding expenditure: {e}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab4:
        st.subheader("🛎️ Historical Room Service Entry")
        
        with st.form("historical_room_service_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                service_date = st.date_input("Service Date", value=date.today())
                room_number = st.selectbox("Room Number", [f"10{i}" for i in range(1, 9)], key="service_room")
                description = st.text_input("Service Description", key="service_desc")
            
            with col2:
                amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, key="service_amount")
                payment_type = st.selectbox("Payment Type", ["Cash", "Account"], key="service_payment")
                status = st.selectbox("Status", ["Completed", "Pending"])
            
            if st.form_submit_button("Add Historical Room Service"):
                if description and amount > 0:
                    try:
                        service_data = {
                            'date': service_date,
                            'room_number': room_number,
                            'description': description,
                            'amount': amount,
                            'payment_type': payment_type,
                            'status': status,
                            'hotel': user_hotel,
                            'created_by': st.session_state.username
                        }
                        
                        if data_integration.add_historical_room_service(service_data, user_hotel):
                            msg = f"✅ Historical room service added for {service_date} - Will appear in Room Service section"
                            if status == 'Completed':
                                msg += " and Sales"
                            st.success(msg)
                        else:
                            st.error("Failed to add historical room service")
                    except Exception as e:
                        st.error(f"Error adding room service: {e}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab5:
        st.subheader("💳 Historical Advance Payment Entry")
        
        with st.form("historical_advance_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                advance_date = st.date_input("Advance Payment Date", value=date.today())
                guest_name = st.text_input("Guest Name", key="advance_guest")
                guest_phone = st.text_input("Guest Phone", key="advance_phone")
                advance_amount = st.number_input("Advance Amount (₹)", min_value=0.0, step=0.01, key="advance_amt")
            
            with col2:
                total_amount = st.number_input("Total Amount (₹)", min_value=0.0, step=0.01, key="advance_total")
                room_number = st.selectbox("Room Number (Optional)", 
                                         [""] + [f"10{i}" for i in range(1, 9)], key="advance_room")
                status = st.selectbox("Status", ["Pending", "Completed", "Partially Paid"])
                completion_date = st.date_input("Completion Date (if completed)", value=None, key="advance_completion")
            
            notes = st.text_area("Notes", key="advance_notes")
            
            if st.form_submit_button("Add Historical Advance Payment"):
                if guest_name and advance_amount > 0:
                    try:
                        advance_data = {
                            'advance_date': advance_date,
                            'guest_name': guest_name,
                            'guest_phone': guest_phone,
                            'advance_amount': advance_amount,
                            'total_amount': total_amount if total_amount > 0 else None,
                            'room_number': room_number if room_number else None,
                            'status': status,
                            'completion_date': completion_date if status == 'Completed' else None,
                            'notes': notes,
                            'hotel': user_hotel,
                            'created_by': st.session_state.username
                        }
                        
                        if data_integration.add_historical_advance_payment(advance_data, user_hotel):
                            msg = f"✅ Historical advance payment added for {advance_date} - Will appear in Advance Payments section"
                            if status == 'Completed':
                                msg += " and Sales (as it's marked completed)"
                            st.success(msg)
                        else:
                            st.error("Failed to add historical advance payment")
                    except Exception as e:
                        st.error(f"Error adding advance payment: {e}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab6:
        st.subheader("⏰ Historical Outstanding Dues Entry")
        
        with st.form("historical_dues_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                due_date = st.date_input("Due Date", value=date.today())
                guest_name = st.text_input("Guest Name", key="dues_guest")
                guest_phone = st.text_input("Guest Phone", key="dues_phone")
                amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, key="dues_amount")
            
            with col2:
                room_number = st.selectbox("Room Number (Optional)", 
                                         [""] + [f"10{i}" for i in range(1, 9)], key="dues_room")
                status = st.selectbox("Status", ["Pending", "Paid"])
                payment_date = st.date_input("Payment Date (if paid)", value=None, key="dues_payment_date")
            
            description = st.text_area("Description", key="dues_description")
            
            if st.form_submit_button("Add Historical Outstanding Due"):
                if guest_name and amount > 0:
                    try:
                        due_data = {
                            'due_date': due_date,
                            'guest_name': guest_name,
                            'guest_phone': guest_phone,
                            'amount': amount,
                            'room_number': room_number if room_number else None,
                            'description': description,
                            'status': status,
                            'payment_date': payment_date if status == 'Paid' else None,
                            'hotel': user_hotel,
                            'created_by': st.session_state.username
                        }
                        
                        if data_integration.add_historical_outstanding_due(due_data, user_hotel):
                            msg = f"✅ Historical outstanding due added for {due_date} - Will appear in Outstanding Dues section"
                            if status == 'Paid':
                                msg += " and Sales (as it's marked paid)"
                            st.success(msg)
                        else:
                            st.error("Failed to add historical outstanding due")
                    except Exception as e:
                        st.error(f"Error adding outstanding due: {e}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab7:
        st.subheader("🎁 Historical Complementary Room Entry")
        
        with st.form("historical_comp_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                comp_date = st.date_input("Date", value=date.today())
                room_number = st.selectbox("Room Number", [f"10{i}" for i in range(1, 9)], key="comp_room")
                guest_name = st.text_input("Guest Name", key="comp_guest")
            
            with col2:
                guest_phone = st.text_input("Guest Phone", key="comp_phone")
                reason = st.text_area("Reason for Complementary Stay", key="comp_reason")
            
            if st.form_submit_button("Add Historical Complementary Room"):
                if guest_name and reason:
                    try:
                        comp_data = {
                            'date': comp_date,
                            'room_number': room_number,
                            'guest_name': guest_name,
                            'guest_phone': guest_phone,
                            'reason': reason,
                            'hotel': user_hotel,
                            'created_by': st.session_state.username
                        }
                        
                        if data_integration.add_historical_complementary_room(comp_data, user_hotel):
                            st.success(f"✅ Historical complementary room added for {comp_date} - Will appear in Complementary Rooms section")
                        else:
                            st.error("Failed to add historical complementary room")
                    except Exception as e:
                        st.error(f"Error adding complementary room: {e}")
                else:
                    st.error("Please fill in all required fields")
    
    # Show recent entries
    st.markdown("---")
    st.subheader("📋 Recent Historical Entries")
    
    # Display recent entries for verification
    try:
        recent_sales = data_integration.get_data_for_dashboard('sales', user_hotel)
        
        if len(recent_sales) > 0:
            st.write("Recent Sales Entries:")
            # Show only recent entries created by current user
            user_sales = [sale for sale in recent_sales if sale.get('created_by') == st.session_state.username]
            if user_sales:
                df = pd.DataFrame(user_sales[-5:])  # Last 5 entries
                st.dataframe(df[['date', 'description', 'amount', 'payment_type']])
            else:
                st.info("No historical entries found. Add some entries above!")
        else:
            st.info("No historical entries found. Add some entries above!")
        
    except Exception as e:
        st.info("Ready to save historical entries. Add some entries above to get started!")

if __name__ == "__main__":
    main()