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

# All users can add room service data, admin can edit/delete
user_role = st.session_state.get('user_role', 'User')

st.title("🛎️ Room Service Management")

# Load data
selected_hotel = st.session_state.get('selected_hotel') or 'hotel1'
room_services = load_data('room_services.json', selected_hotel)
rooms_list = load_data('rooms.json', selected_hotel)

# Convert list to dictionary if needed
if isinstance(rooms_list, list):
    rooms = {}
    for room in rooms_list:
        if isinstance(room, dict) and 'room_number' in room:
            rooms[room['room_number']] = room
else:
    rooms = rooms_list if rooms_list else {}

# Room service overview
st.markdown("### Room Service Overview")

# Calculate totals
total_services = len(room_services)
total_revenue = sum(service['amount'] for service in room_services)
pending_services = len([s for s in room_services if s['status'] == 'Pending'])
completed_services = len([s for s in room_services if s['status'] == 'Completed'])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Services", total_services)
with col2:
    st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
with col3:
    st.metric("Pending Services", pending_services)
with col4:
    st.metric("Completed Services", completed_services)

st.markdown("---")

# Service menu/pricing
st.markdown("### Service Menu & Pricing")

# Predefined service menu
service_menu = {
    "Food & Beverage": {
        "Breakfast": 300,
        "Lunch": 450,
        "Dinner": 500,
        "Tea/Coffee": 100,
        "Snacks": 200,
        "Cold Drinks": 80,
        "Water Bottle": 50
    },
    "Laundry": {
        "Shirt/T-shirt": 50,
        "Trousers": 60,
        "Suit": 150,
        "Dress": 80,
        "Undergarments": 30,
        "Bed Sheets": 100,
        "Towels": 40
    },
    "Room Maintenance": {
        "Extra Towels": 50,
        "Extra Bed Sheets": 100,
        "Room Cleaning": 200,
        "Pillow": 150,
        "Blanket": 200
    },
    "Other Services": {
        "Newspaper": 25,
        "Taxi Booking": 100,
        "Wake-up Call": 0,
        "Luggage Assistance": 100,
        "Internet Service": 200
    }
}

# Display service menu
for category, items in service_menu.items():
    with st.expander(f"{category} - Services & Pricing"):
        for service, price in items.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {service}")
            with col2:
                st.write(f"₹{price}")

st.markdown("---")

# Add new room service
st.markdown("### Add New Room Service")

with st.form("add_service_form"):
    col1, col2 = st.columns(2)

    with col1:
        # Get all available rooms for the selected hotel
        selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
        
        # Define room numbers based on hotel (ensuring all rooms are always available for service)
        if selected_hotel == 'hotel1':
            all_rooms = [f"Room {i}" for i in range(101, 109)]  # 101-108
        else:  # hotel2
            all_rooms = [f"Room {i}" for i in ['101', '102', '103', '201', '202', '203', '301', '302', '303', '304', '305', '401', '402', '403', '501', '502', '503']]
        
        selected_room = st.selectbox("Room Number", all_rooms)

        service_category = st.selectbox("Service Category", list(service_menu.keys()))

        # Update service items based on category
        available_services = list(service_menu[service_category].keys())
        selected_service = st.selectbox("Service Item", available_services)

        # Auto-fill price based on selection
        default_price = service_menu[service_category][selected_service]
        amount = st.number_input("Amount", value=float(default_price), min_value=0.0, step=10.0)

    with col2:
        customer_name = st.text_input("Customer Name", placeholder="Guest name")
        quantity = st.number_input("Quantity", value=1, min_value=1, step=1)

        # Calculate total
        total_amount = amount * quantity
        st.write(f"**Total Amount: ₹{total_amount:,.2f}**")

        special_instructions = st.text_area("Special Instructions", placeholder="Any special requests")
        priority = st.selectbox("Priority", ["Normal", "High", "Urgent"])

    submit_service = st.form_submit_button("Add Service Request", type="primary")

    if submit_service:
        if not customer_name:
            st.error("Customer name is required")
        else:
            new_service = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'room_number': selected_room,
                'customer_name': customer_name,
                'service_category': service_category,
                'service_item': selected_service,
                'quantity': quantity,
                'unit_price': amount,
                'amount': total_amount,
                'special_instructions': special_instructions,
                'priority': priority,
                'status': 'Pending',
                'created_by': st.session_state.get('username', 'Unknown'),
                'hotel': selected_hotel
            }

            if add_record('room_services.json', new_service, selected_hotel):
                st.success("Room service request added successfully!")
                st.rerun()
            else:
                st.error("Failed to add room service. Please try again.")

st.markdown("---")

# Room service requests
st.markdown("### Room Service Requests")

if room_services:
    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Completed", "Cancelled"])
    with col2:
        filter_category = st.selectbox("Filter by Category", ["All"] + list(service_menu.keys()))
    with col3:
        filter_priority = st.selectbox("Filter by Priority", ["All", "Normal", "High", "Urgent"])

    # Apply filters
    filtered_services = room_services
    if filter_status != "All":
        filtered_services = [s for s in filtered_services if s['status'] == filter_status]
    if filter_category != "All":
        filtered_services = [s for s in filtered_services if s['service_category'] == filter_category]
    if filter_priority != "All":
        filtered_services = [s for s in filtered_services if s['priority'] == filter_priority]

    # Sort by priority and date
    priority_order = {"Urgent": 0, "High": 1, "Normal": 2}
    filtered_services.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['date']))

    # Display services
    for service in filtered_services:
        # Color coding based on priority
        if service['priority'] == 'Urgent':
            border_color = "#ff4444"
        elif service['priority'] == 'High':
            border_color = "#ff8800"
        else:
            border_color = "#cccccc"

        with st.container():
            st.markdown(f"""
            <div style="border-left: 4px solid {border_color}; padding-left: 10px; margin-bottom: 10px;">
            """, unsafe_allow_html=True)

            with st.expander(f"#{service['id']} - {service['room_number']} - {service['service_item']} - ₹{service['amount']:,.2f}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Date:** {service['date']}")
                    st.write(f"**Room:** {service['room_number']}")
                    st.write(f"**Customer:** {service['customer_name']}")
                    st.write(f"**Service:** {service['service_item']}")
                    st.write(f"**Category:** {service['service_category']}")

                with col2:
                    st.write(f"**Quantity:** {service['quantity']}")
                    st.write(f"**Unit Price:** ₹{service['unit_price']}")
                    st.write(f"**Total Amount:** ₹{service['amount']:,.2f}")
                    st.write(f"**Priority:** {service['priority']}")
                    st.write(f"**Status:** {service['status']}")

                if service.get('special_instructions'):
                    st.write(f"**Special Instructions:** {service['special_instructions']}")

                # Service status management
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if service['status'] == 'Pending' and st.button(f"Start Service", key=f"start_{service['id']}"):
                        for s in room_services:
                            if s['id'] == service['id']:
                                s['status'] = 'In Progress'
                                break
                        save_data('room_services.json', room_services, selected_hotel)
                        st.success("Service started!")
                        st.rerun()

                with col2:
                    if service['status'] == 'In Progress':
                        with st.form(f"complete_service_{service['id']}"):
                            st.write(f"**Amount:** ₹{service['amount']:,.2f}")
                            payment_type = st.selectbox("Payment Type", ["Cash", "Account"], key=f"service_payment_{service['id']}")

                            if st.form_submit_button("Complete & Add to Sales"):
                                # Update service status
                                for s in room_services:
                                    if s['id'] == service['id']:
                                        s['status'] = 'Completed'
                                        s['completed_date'] = get_current_datetime()
                                        s['payment_method'] = payment_type
                                        break
                                save_data('room_services.json', room_services, selected_hotel)

                                # Add to appropriate sales section based on payment type
                                sales = load_data('sales.json', selected_hotel)
                                new_sale = {
                                    'id': generate_id(),
                                    'date': get_current_datetime(),
                                    'type': 'Room Service',
                                    'amount': service['amount'],
                                    'payment_type': payment_type,
                                    'customer_name': service['customer_name'],
                                    'description': f"Room service: {service['service_item']}",
                                    'room_number': service['room_number'],
                                    'status': 'Completed',
                                    'created_by': st.session_state.get('username', 'Unknown')
                                }
                                sales.append(new_sale)
                                selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                                save_data('sales.json', sales, selected_hotel)
                                save_data('room_services.json', room_services, selected_hotel)

                                # Show success message indicating which sales section it went to
                                if payment_type == 'Cash':
                                    st.success(f"Service completed and added to Cash Sales section!")
                                else:
                                    st.success(f"Service completed and added to Account Sales section!")
                                st.rerun()

                with col3:
                    if service['status'] in ['Pending', 'In Progress'] and st.button(f"Cancel", key=f"cancel_{service['id']}"):
                        for s in room_services:
                            if s['id'] == service['id']:
                                s['status'] = 'Cancelled'
                                break
                        save_data('room_services.json', room_services, selected_hotel)
                        st.warning("Service cancelled!")
                        st.rerun()

                with col4:
                    if user_role == 'Admin':
                        if st.button(f"Delete", key=f"delete_{service['id']}", type="secondary"):
                            room_services = [s for s in room_services if s['id'] != service['id']]
                            selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                            save_data('room_services.json', room_services, selected_hotel)
                            st.success("Service deleted!")
                            st.rerun()

                # Admin edit functionality
                if user_role == 'Admin':
                    if st.button(f"Edit Service", key=f"edit_service_{service['id']}"):
                        with st.form(f"edit_service_form_{service['id']}"):
                            new_amount = st.number_input("Amount", value=service['amount'], min_value=0.0)
                            new_status = st.selectbox("Status", ["Pending", "In Progress", "Completed", "Cancelled"], 
                                                    index=["Pending", "In Progress", "Completed", "Cancelled"].index(service['status']))
                            if st.form_submit_button("Update Service"):
                                for s in room_services:
                                    if s['id'] == service['id']:
                                        s['amount'] = new_amount
                                        s['status'] = new_status
                                        break
                                selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
                                save_data('room_services.json', room_services, selected_hotel)
                                st.success("Service updated!")
                                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("No room service requests found")

# Service statistics
if room_services:
    st.markdown("---")
    st.markdown("### Service Statistics")

    col1, col2 = st.columns(2)

    with col1:
        # Most popular services
        service_counts = {}
        for service in room_services:
            item = service['service_item']
            service_counts[item] = service_counts.get(item, 0) + 1

        if service_counts:
            popular_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            st.markdown("**Most Popular Services:**")
            for service, count in popular_services:
                st.write(f"• {service}: {count} orders")

    with col2:
        # Revenue by category
        category_revenue = {}
        for service in room_services:
            category = service['service_category']
            category_revenue[category] = category_revenue.get(category, 0) + service['amount']

        if category_revenue:
            st.markdown("**Revenue by Category:**")
            for category, revenue in category_revenue.items():
                st.write(f"• {category}: ₹{revenue:,.2f}")

# Quick service buttons for common requests
st.markdown("---")
st.markdown("### Quick Service Requests")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🍽️ Breakfast", key="quick_breakfast"):
        st.info("Quick breakfast service - Use form above to complete")

with col2:
    if st.button("☕ Tea/Coffee", key="quick_tea"):
        st.info("Quick tea/coffee service - Use form above to complete")

with col3:
    if st.button("🧺 Laundry", key="quick_laundry"):
        st.info("Quick laundry service - Use form above to complete")

with col4:
    if st.button("🧹 Room Cleaning", key="quick_cleaning"):
        st.info("Quick room cleaning service - Use form above to complete")