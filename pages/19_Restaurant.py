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

# Check hotel access - only hotel2 (Saz Valley Bhaderwah) users can access restaurant
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
hotel_access = st.session_state.get('hotel_access', 'both')

# Restrict access to hotel2 users only
if selected_hotel != 'hotel2' and hotel_access != 'hotel2':
    if hotel_access == 'hotel1':
        st.error("🚫 Restaurant access is not available for Saz Valley Kistwar users")
        st.info("The restaurant is only available at Saz Valley Bhaderwah location")
        st.stop()
    elif hotel_access == 'both':
        # Admin with both access but currently viewing hotel1
        if selected_hotel == 'hotel1':
            st.warning("⚠️ Restaurant is only available for Saz Valley Bhaderwah")
            st.info("Please switch to Saz Valley Bhaderwah to access restaurant features")
            st.stop()

user_role = st.session_state.get('user_role', 'User')

st.title("🍽️ Saz Valley Bhaderwah Restaurant")

# Load data
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
sales = load_data('sales.json', selected_hotel)
rooms = load_data('rooms.json', selected_hotel)

# Filter restaurant sales
restaurant_sales = [s for s in sales if s.get('type') == 'Restaurant' or s.get('description', '').lower().find('restaurant') != -1]

# Overview
st.markdown("### Restaurant Sales Overview")

total_restaurant_sales = sum(sale['amount'] for sale in restaurant_sales)
cash_restaurant_sales = sum(sale['amount'] for sale in restaurant_sales if sale['payment_type'] == 'Cash')
account_restaurant_sales = sum(sale['amount'] for sale in restaurant_sales if sale['payment_type'] == 'Account')

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Restaurant Sales", f"₹{total_restaurant_sales:,.2f}")
with col2:
    st.metric("Cash Sales", f"₹{cash_restaurant_sales:,.2f}")
with col3:
    st.metric("Account Sales", f"₹{account_restaurant_sales:,.2f}")
with col4:
    st.metric("Total Orders", len(restaurant_sales))

st.markdown("---")

# Menu items for Saz Valley Bhahrwah
st.markdown("### Restaurant Menu")

# Define menu categories and items
menu_categories = {
    "Appetizers": [
        {"name": "Samosa (2 pcs)", "price": 40},
        {"name": "Pakora Platter", "price": 120},
        {"name": "Chicken Wings (6 pcs)", "price": 180},
        {"name": "Fish Fingers", "price": 200},
        {"name": "Vegetable Spring Rolls", "price": 100}
    ],
    "Main Course - Vegetarian": [
        {"name": "Dal Makhani", "price": 160},
        {"name": "Paneer Butter Masala", "price": 220},
        {"name": "Mixed Vegetable Curry", "price": 140},
        {"name": "Aloo Gobi", "price": 130},
        {"name": "Rajma Rice", "price": 180}
    ],
    "Main Course - Non-Vegetarian": [
        {"name": "Butter Chicken", "price": 280},
        {"name": "Chicken Biryani", "price": 250},
        {"name": "Mutton Curry", "price": 320},
        {"name": "Fish Curry", "price": 300},
        {"name": "Chicken Tikka Masala", "price": 290}
    ],
    "Rice & Bread": [
        {"name": "Steamed Rice", "price": 60},
        {"name": "Jeera Rice", "price": 80},
        {"name": "Naan (2 pcs)", "price": 50},
        {"name": "Roti (4 pcs)", "price": 40},
        {"name": "Garlic Naan", "price": 70}
    ],
    "Beverages": [
        {"name": "Tea", "price": 25},
        {"name": "Coffee", "price": 30},
        {"name": "Fresh Lime Water", "price": 40},
        {"name": "Lassi", "price": 60},
        {"name": "Cold Drinks", "price": 35}
    ],
    "Desserts": [
        {"name": "Gulab Jamun (2 pcs)", "price": 80},
        {"name": "Ice Cream", "price": 70},
        {"name": "Kheer", "price": 90},
        {"name": "Jalebi", "price": 100}
    ]
}

# Display menu in expandable sections
for category, items in menu_categories.items():
    with st.expander(f"📋 {category}", expanded=False):
        for item in items:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{item['name']}**")
            with col2:
                st.write(f"₹{item['price']}")

st.markdown("---")

# Add new restaurant order
st.markdown("### New Restaurant Order")

with st.form("add_restaurant_order_form"):
    col1, col2 = st.columns(2)

    with col1:
        # Add custom date selection for historical entries
        order_date = st.date_input("Order Date", value=datetime.now().date(), 
                                 help="Select the date for this restaurant order")
        customer_name = st.text_input("Customer Name", placeholder="Enter customer name")
        customer_phone = st.text_input("Phone Number", placeholder="Customer phone (optional)")

        # Room number (optional) - for room service orders
        if isinstance(rooms, dict):
            all_rooms = [f"Room {k}" for k in sorted(rooms.keys(), key=lambda x: int(x))]
        elif isinstance(rooms, list):
            # If rooms is a list of room objects, extract room numbers
            all_rooms = [f"Room {room.get('room_number', room.get('id', i+101))}" for i, room in enumerate(rooms)]
        else:
            # Default room numbers
            all_rooms = [f"Room {i}" for i in range(101, 109)]
        room_options = ["Walk-in Customer"] + all_rooms
        room_number = st.selectbox("Customer Type", room_options)

        payment_type = st.selectbox("Payment Type", ["Cash", "Account"])

    with col2:
        # Order items
        st.markdown("**Order Items:**")
        selected_items = []
        total_amount = 0

        # Create a simple order interface
        order_text = st.text_area("Order Details", 
                                placeholder="Enter items and quantities\nExample:\nButter Chicken x1 - ₹280\nNaan x2 - ₹100\nTea x2 - ₹50",
                                height=120)

        # Manual amount entry for custom orders
        manual_amount = st.number_input("Total Amount", min_value=0.0, step=10.0, help="Enter total bill amount")

    special_instructions = st.text_area("Special Instructions", placeholder="Any special cooking instructions or notes")

    if st.form_submit_button("Add Restaurant Order", type="primary"):
        if customer_name and manual_amount > 0:
            # Determine order type
            order_type = "Restaurant - Room Service" if room_number != "Walk-in Customer" else "Restaurant - Dine In"

            new_sale = {
                'id': generate_id(),
                'date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'Restaurant',
                'amount': manual_amount,
                'payment_type': payment_type,
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'description': f"Saz Valley Bhahrwah Restaurant - {order_type}",
                'order_details': order_text,
                'room_number': room_number if room_number != "Walk-in Customer" else None,
                'special_instructions': special_instructions,
                'restaurant_name': 'Saz Valley Bhahrwah',
                'order_type': order_type,
                'status': 'Completed',
                'created_by': st.session_state.get('username', 'Unknown')
            }

            sales.append(new_sale)
            save_data('sales.json', sales, selected_hotel)
            st.success(f"Restaurant order added successfully! ₹{manual_amount:,.2f} added to {payment_type} sales.")
            st.rerun()
        else:
            st.error("Customer name and amount are required")

st.markdown("---")

# Restaurant orders list
st.markdown("### Restaurant Orders")

if restaurant_sales:
    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_payment = st.selectbox("Filter by Payment", ["All", "Cash", "Account"])
    with col2:
        filter_date = st.selectbox("Filter by Date", ["All", "Today", "This Week", "This Month"])
    with col3:
        filter_type = st.selectbox("Filter by Type", ["All", "Dine In", "Room Service"])

    # Apply filters
    filtered_orders = restaurant_sales

    if filter_payment != "All":
        filtered_orders = [s for s in filtered_orders if s['payment_type'] == filter_payment]

    if filter_date == "Today":
        today_date = get_current_datetime()[:10]
        filtered_orders = [s for s in filtered_orders if s['date'].startswith(today_date)]
    elif filter_date == "This Week":
        # Simplified - just this month for demo
        current_month = get_current_datetime()[:7]
        filtered_orders = [s for s in filtered_orders if s['date'].startswith(current_month)]
    elif filter_date == "This Month":
        current_month = get_current_datetime()[:7]
        filtered_orders = [s for s in filtered_orders if s['date'].startswith(current_month)]

    if filter_type != "All":
        if filter_type == "Dine In":
            filtered_orders = [s for s in filtered_orders if s.get('order_type', '').find('Dine In') != -1]
        elif filter_type == "Room Service":
            filtered_orders = [s for s in filtered_orders if s.get('order_type', '').find('Room Service') != -1]

    # Display filtered results
    if filtered_orders:
        st.info(f"Showing {len(filtered_orders)} orders totaling ₹{sum(order['amount'] for order in filtered_orders):,.2f}")

        for order in filtered_orders:
            order_date = order['date'][:10] if order['date'] else 'N/A'
            order_type_display = order.get('order_type', 'Restaurant Order')

            with st.expander(f"#{order['id']} - {order['customer_name']} - ₹{order['amount']:,.2f} - {order_date} - {order_type_display}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Date:** {order['date']}")
                    st.write(f"**Customer:** {order['customer_name']}")
                    st.write(f"**Phone:** {order.get('customer_phone', 'N/A')}")
                    st.write(f"**Amount:** ₹{order['amount']:,.2f}")
                    st.write(f"**Payment Type:** {order['payment_type']}")

                with col2:
                    st.write(f"**Order Type:** {order.get('order_type', 'Restaurant Order')}")
                    st.write(f"**Room:** {order.get('room_number', 'Walk-in')}")
                    st.write(f"**Status:** {order.get('status', 'Completed')}")
                    st.write(f"**Created by:** {order.get('created_by', 'Unknown')}")

                if order.get('order_details'):
                    st.write(f"**Order Details:**")
                    st.text(order['order_details'])

                if order.get('special_instructions'):
                    st.write(f"**Special Instructions:** {order['special_instructions']}")

                # Admin actions
                if user_role == 'Admin':
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(f"Edit Order", key=f"edit_{order['id']}"):
                            with st.form(f"edit_order_{order['id']}"):
                                new_amount = st.number_input("Amount", value=order['amount'], min_value=0.0)
                                new_payment = st.selectbox("Payment Type", ["Cash", "Account"], 
                                                         index=["Cash", "Account"].index(order['payment_type']))
                                if st.form_submit_button("Update Order"):
                                    for s in sales:
                                        if s['id'] == order['id']:
                                            s['amount'] = new_amount
                                            s['payment_type'] = new_payment
                                            break
                                    save_data('sales.json', sales, selected_hotel)
                                    st.success("Order updated!")
                                    st.rerun()

                    with col2:
                        if st.button(f"Delete Order", key=f"delete_{order['id']}", type="secondary"):
                            sales = [s for s in sales if s['id'] != order['id']]
                            save_data('sales.json', sales, selected_hotel)
                            st.success("Order deleted!")
                            st.rerun()
    else:
        st.info("No orders found matching the selected filters")
else:
    st.info("No restaurant orders found")

st.markdown("---")

# Restaurant analytics
if restaurant_sales:
    st.markdown("### Restaurant Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Payment type distribution
        payment_data = {}
        for sale in restaurant_sales:
            payment_type = sale['payment_type']
            payment_data[payment_type] = payment_data.get(payment_type, 0) + sale['amount']

        if payment_data:
            import plotly.express as px
            fig_payment = px.pie(
                values=list(payment_data.values()), 
                names=list(payment_data.keys()), 
                title="Restaurant Sales by Payment Type"
            )
            st.plotly_chart(fig_payment, use_container_width=True)

    with col2:
        # Order type distribution
        order_type_data = {"Dine In": 0, "Room Service": 0, "Other": 0}
        for sale in restaurant_sales:
            order_type = sale.get('order_type', '')
            if 'Dine In' in order_type:
                order_type_data["Dine In"] += sale['amount']
            elif 'Room Service' in order_type:
                order_type_data["Room Service"] += sale['amount']
            else:
                order_type_data["Other"] += sale['amount']

        # Remove zero values
        order_type_data = {k: v for k, v in order_type_data.items() if v > 0}

        if order_type_data:
            fig_type = px.bar(
                x=list(order_type_data.keys()), 
                y=list(order_type_data.values()), 
                title="Restaurant Sales by Order Type"
            )
            st.plotly_chart(fig_type, use_container_width=True)

    # Top customers
    st.markdown("#### Top Customers")
    customer_totals = {}
    for sale in restaurant_sales:
        customer = sale['customer_name']
        customer_totals[customer] = customer_totals.get(customer, 0) + sale['amount']

    if customer_totals:
        top_customers = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (customer, total) in enumerate(top_customers, 1):
            st.write(f"{i}. **{customer}**: ₹{total:,.2f}")

# Admin download section
if user_role == 'Admin':
    st.markdown("---")
    st.markdown("### 📥 Download Restaurant Data")

    col1, col2 = st.columns(2)

    with col1:
        if restaurant_sales:
            df = pd.DataFrame(restaurant_sales)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 Download Restaurant Orders CSV",
                data=csv,
                file_name=f"saz_valley_bhaderwah_restaurant_orders_{get_current_datetime()[:10]}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No restaurant orders to download")

    with col2:
        # Download all restaurant data as JSON
        if restaurant_sales:
            import json
            restaurant_data = {
                "restaurant_name": "Saz Valley Bhaderwah",
                "export_date": get_current_datetime(),
                "total_orders": len(restaurant_sales),
                "total_revenue": sum(sale['amount'] for sale in restaurant_sales),
                "orders": restaurant_sales
            }
            json_data = json.dumps(restaurant_data, indent=2)
            st.download_button(
                label="📄 Download Restaurant JSON",
                data=json_data,
                file_name=f"saz_valley_bhaderwah_restaurant_complete_{get_current_datetime()[:10]}.json",
                mime="application/json"
            )

st.markdown("---")
st.caption("Saz Valley Bhahrwah Restaurant • Integrated with hotel sales system")