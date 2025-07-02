import streamlit as st
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication
from utils.database_data_manager import load_data, save_data, get_current_date, get_current_datetime, generate_id
import pandas as pd

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

# All users can view rooms and book, admin can edit rooms
user_role = st.session_state.get('user_role', 'User')

st.title("🏠 Room Management")

# Get selected hotel from session state
selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
hotel_name = st.session_state.get('hotel_name', 'Hotel 1')

# Display current hotel
st.info(f"Currently managing: **{hotel_name}**")

# Load data
rooms_list = load_data('rooms.json', selected_hotel)

# Convert list to dictionary if needed
if isinstance(rooms_list, list):
    rooms = {}
    for room in rooms_list:
        if isinstance(room, dict) and 'room_number' in room:
            rooms[room['room_number']] = room
else:
    rooms = rooms_list if rooms_list else {}

# Initialize room data if empty (only create missing rooms)
if not rooms:
    rooms = {}

# Define room numbers based on selected hotel
if selected_hotel == 'hotel1':
    room_numbers = [str(i) for i in range(101, 109)]  # 101-108
else:  # hotel2
    room_numbers = [
        '101', '102', '103',  # 1st floor
        '201', '202', '203',  # 2nd floor  
        '301', '302', '303', '304', '305',  # 3rd floor
        '401', '402', '403',  # 4th floor
        '501', '502', '503'   # 5th floor
    ]

# Ensure all rooms exist but don't overwrite existing prices
for room_key in room_numbers:
    if room_key not in rooms:
        rooms[room_key] = {
            'status': 'Available', 
            'type': 'Standard', 
            'price': 2000, 
            'current_guest': None, 
            'checkin_date': None, 
            'checkout_date': None, 
            'guest_phone': None
        }

# Save only if we added new rooms
save_data('rooms.json', rooms, selected_hotel)

# Room overview
st.markdown("### Room Overview")
col1, col2, col3, col4 = st.columns(4)

available_rooms = len([r for r in rooms.values() if r['status'] == 'Available'])
occupied_rooms = len([r for r in rooms.values() if r['status'] == 'Occupied'])
maintenance_rooms = len([r for r in rooms.values() if r['status'] == 'Maintenance'])

with col1:
    st.metric("Total Rooms", len(rooms))
with col2:
    st.metric("Available", available_rooms, f"{available_rooms}/{len(rooms)}")
with col3:
    st.metric("Occupied", occupied_rooms, f"{occupied_rooms}/{len(rooms)}")
with col4:
    st.metric("Maintenance", maintenance_rooms, f"{maintenance_rooms}/{len(rooms)}")

st.markdown("---")

# Room grid display
st.markdown("### Room Status")

# Display rooms dynamically based on hotel
room_list = sorted(rooms.keys(), key=lambda x: int(x))

# Group rooms by floor for better display
if selected_hotel == 'hotel2':
    floors = {
        '1st Floor': ['101', '102', '103'],
        '2nd Floor': ['201', '202', '203'],
        '3rd Floor': ['301', '302', '303', '304', '305'],
        '4th Floor': ['401', '402', '403'],
        '5th Floor': ['501', '502', '503']
    }

    for floor_name, floor_rooms in floors.items():
        st.markdown(f"**{floor_name}**")

        # Create columns for each floor
        num_cols = len(floor_rooms)
        if num_cols > 0:
            cols = st.columns(num_cols)

            for i, room_key in enumerate(floor_rooms):
                if room_key in rooms:
                    room = rooms[room_key]

                    with cols[i]:
                        # Color coding based on status
                        if room['status'] == 'Available':
                            status_color = "🟢"
                            bg_color = "#d4edda"
                        elif room['status'] == 'Occupied':
                            status_color = "🔴"
                            bg_color = "#f8d7da"
                        else:
                            status_color = "🟡"
                            bg_color = "#fff3cd"

                        st.markdown(f"""
                        <div style="border: 2px solid #ddd; padding: 10px; border-radius: 8px; text-align: center; margin: 5px; background-color: {bg_color};">
                            <h4>{status_color} Room {room_key}</h4>
                            <p><strong>Status:</strong> {room['status']}</p>
                            <p><strong>Type:</strong> {room['type']}</p>
                            <p><strong>Price:</strong> ₹{float(room['price'])}</p>
                            {f"<p><strong>Guest:</strong> {room['current_guest']}</p>" if room['current_guest'] else ""}
                            {f"<p><strong>Check-in:</strong> {room['checkin_date']}</p>" if room.get('checkin_date') else ""}
                            {f"<p><strong>Check-out:</strong> {room['checkout_date']}</p>" if room.get('checkout_date') else ""}
                        </div>
                        """, unsafe_allow_html=True)
        st.markdown("---")
else:
    # Hotel 1: Original 2x4 grid for rooms 101-108
    for row in range(2):
        cols = st.columns(4)
        for col in range(4):
            room_num = 101 + (row * 4) + col
            room_key = str(room_num)

            if room_key in rooms:
                room = rooms[room_key]

                with cols[col]:
                    # Color coding based on status
                    if room['status'] == 'Available':
                        status_color = "🟢"
                        bg_color = "#d4edda"
                    elif room['status'] == 'Occupied':
                        status_color = "🔴"
                        bg_color = "#f8d7da"
                    else:
                        status_color = "🟡"
                        bg_color = "#fff3cd"

                    st.markdown(f"""
                    <div style="border: 2px solid #ddd; padding: 10px; border-radius: 8px; text-align: center; margin: 5px; background-color: {bg_color};">
                        <h4>{status_color} Room {room_num}</h4>
                        <p><strong>Status:</strong> {room['status']}</p>
                        <p><strong>Type:</strong> {room['type']}</p>
                        <p><strong>Price:</strong> ₹{float(room['price'])}</p>
                        {f"<p><strong>Guest:</strong> {room['current_guest']}</p>" if room['current_guest'] else ""}
                        {f"<p><strong>Check-in:</strong> {room['checkin_date']}</p>" if room.get('checkin_date') else ""}
                        {f"<p><strong>Check-out:</strong> {room['checkout_date']}</p>" if room.get('checkout_date') else ""}
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("---")

# Room management section
if user_role == 'Admin':
    st.markdown("### Room Management (Admin)")

    # Room selection - dynamic based on hotel
    room_options = [f"Room {room_key}" for room_key in sorted(rooms.keys(), key=lambda x: int(x))]
    selected_room = st.selectbox("Select Room", room_options)
    room_number = selected_room.split()[1]

    room_data = rooms[room_number]

    # Display current room details
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Current Status:** {room_data['status']}")
        st.markdown(f"**Room Type:** {room_data['type']}")
        st.markdown(f"**Price:** ₹{float(room_data['price'])}")

    with col2:
        if room_data['current_guest']:
            st.markdown(f"**Current Guest:** {room_data['current_guest']}")
            st.markdown(f"**Check-in:** {room_data['checkin_date']}")
            st.markdown(f"**Check-out:** {room_data['checkout_date']}")
            st.markdown(f"**Phone:** {room_data.get('guest_phone', 'N/A')}")

    # Room actions
    st.markdown("#### Update Room")

    with st.form(f"update_room_{room_number}"):
        col1, col2 = st.columns(2)

        with col1:
            new_status = st.selectbox("Status", ["Available", "Occupied", "Maintenance"], 
                                    index=["Available", "Occupied", "Maintenance"].index(room_data['status']))
            new_type = st.selectbox("Room Type", ["Standard", "Deluxe", "Suite"], 
                                  index=["Standard", "Deluxe", "Suite"].index(room_data['type']))
            new_price = st.number_input("Price per night", value=float(room_data['price']), min_value=500, step=100)

        with col2:
            guest_name = st.text_input("Guest Name", value=room_data['current_guest'] or "")
            guest_phone = st.text_input("Guest Phone", value=room_data.get('guest_phone', '') or "")
            checkin_date = st.date_input("Check-in Date")
            checkout_date = st.date_input("Check-out Date")

        update_button = st.form_submit_button("Update Room", type="primary")

        if update_button:
            # Update room data
            rooms[room_number].update({
                'status': new_status,
                'type': new_type,
                'price': new_price,
                'current_guest': guest_name if guest_name else None,
                'guest_phone': guest_phone if guest_phone else None,
                'checkin_date': str(checkin_date) if guest_name else None,
                'checkout_date': str(checkout_date) if guest_name else None
            })

            # Convert to list format for database
            rooms_list_for_db = []
            for rnum, rdata in rooms.items():
                room_record = rdata.copy()
                room_record['room_number'] = str(rnum)
                if 'id' not in room_record:
                    room_record['id'] = generate_id()
                rooms_list_for_db.append(room_record)

            save_data('rooms.json', rooms_list_for_db, selected_hotel)
            st.success(f"Room {room_number} updated successfully!")
            st.rerun()

# Room booking section
st.markdown("---")
st.markdown("### Quick Room Booking")

with st.form("quick_booking"):
    col1, col2, col3 = st.columns(3)

    with col1:
        available_rooms_list = [f"Room {k}" for k, v in sorted(rooms.items(), key=lambda x: int(x[0])) if v['status'] == 'Available']
        if available_rooms_list:
            booking_room = st.selectbox("Select Available Room", available_rooms_list)
        else:
            st.warning("No rooms available for booking")
            booking_room = None

    with col2:
        guest_name = st.text_input("Guest Name", placeholder="Enter guest name")
        guest_phone = st.text_input("Phone Number", placeholder="Guest phone number")

    with col3:
        checkin = st.date_input("Check-in Date", value=None)
        checkout = st.date_input("Check-out Date", value=None)

    book_button = st.form_submit_button("Book Room", type="primary")

    if book_button and booking_room:
        if not guest_name:
            st.error("Guest name is required")
        elif not checkin or not checkout:
            st.error("Check-in and check-out dates are required")
        elif checkin >= checkout:
            st.error("Check-out date must be after check-in date")
        else:
            room_num = booking_room.split()[1]
            rooms[room_num].update({
                'status': 'Occupied',
                'current_guest': guest_name,
                'checkin_date': str(checkin),
                'checkout_date': str(checkout),
                'guest_phone': guest_phone
            })

            # Convert to list format for database
            rooms_list_for_db = []
            for rnum, rdata in rooms.items():
                room_record = rdata.copy()
                room_record['room_number'] = str(rnum)
                if 'id' not in room_record:
                    room_record['id'] = generate_id()
                rooms_list_for_db.append(room_record)

            save_data('rooms.json', rooms_list_for_db, selected_hotel)

            # Automatically create a sale entry for the booking
            sales = load_data('sales.json')
            days = (checkout - checkin).days
            room_price = rooms[room_num]['price']
            total_amount = days * room_price

            new_sale = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'type': 'Room Booking',
                'amount': total_amount,
                'payment_type': 'Account',  # Default to account, can be changed later
                'customer_name': guest_name,
                'description': f"Room booking for {days} days",
                'room_number': booking_room,
                'status': 'Pending',
                'created_by': st.session_state.get('username', 'Unknown')
            }
            sales.append(new_sale)
            save_data('sales.json', sales)

            st.success(f"Room {room_num} booked successfully for {guest_name}! Total amount: ₹{total_amount:,.2f}")
            st.rerun()

# Check-out section
st.markdown("---")
st.markdown("### Quick Check-out")

occupied_rooms_list = [f"Room {k}" for k, v in sorted(rooms.items(), key=lambda x: int(x[0])) if v['status'] == 'Occupied']

if occupied_rooms_list:
    with st.form("checkout_form"):
        checkout_room = st.selectbox("Select Room to Check-out", occupied_rooms_list)

        if st.form_submit_button("Check-out Room", type="secondary"):
            room_num = checkout_room.split()[1]
            guest_name = rooms[room_num]['current_guest']

            # Clear room data
            rooms[room_num].update({
                'status': 'Available',
                'current_guest': None,
                'checkin_date': None,
                'checkout_date': None,
                'guest_phone': None
            })

            # Convert to list format for database
            rooms_list_for_db = []
            for rnum, rdata in rooms.items():
                room_record = rdata.copy()
                room_record['room_number'] = str(rnum)
                if 'id' not in room_record:
                    room_record['id'] = generate_id()
                rooms_list_for_db.append(room_record)

            save_data('rooms.json', rooms_list_for_db, selected_hotel)
            st.success(f"Room {room_num} checked out successfully! Guest: {guest_name}")
            st.rerun()
else:
    st.info("No occupied rooms available for check-out")

# Room maintenance section
if user_role == 'Admin':
    st.markdown("---")
    st.markdown("### Room Maintenance")

    maintenance_rooms_list = [f"Room {k}" for k, v in sorted(rooms.items(), key=lambda x: int(x[0])) if v['status'] == 'Maintenance']
    available_for_maintenance = [f"Room {k}" for k, v in sorted(rooms.items(), key=lambda x: int(x[0])) if v['status'] == 'Available']

    col1, col2 = st.columns(2)

    with col1:
        if available_for_maintenance:
            with st.form("set_maintenance"):
                maintenance_room = st.selectbox("Set Room for Maintenance", available_for_maintenance)
                if st.form_submit_button("Set Maintenance"):
                    room_num = maintenance_room.split()[1]
                    rooms[room_num]['status'] = 'Maintenance'
                    # Convert to list format for database
                    rooms_list_for_db = []
                    for rnum, rdata in rooms.items():
                        room_record = rdata.copy()
                        room_record['room_number'] = str(rnum)
                        if 'id' not in room_record:
                            room_record['id'] = generate_id()
                        rooms_list_for_db.append(room_record)

                    save_data('rooms.json', rooms_list_for_db, selected_hotel)
                    st.success(f"Room {room_num} set for maintenance")
                    st.rerun()

    with col2:
        if maintenance_rooms_list:
            with st.form("complete_maintenance"):
                complete_room = st.selectbox("Complete Maintenance", maintenance_rooms_list)
                if st.form_submit_button("Complete Maintenance"):
                    room_num = complete_room.split()[1]
                    rooms[room_num]['status'] = 'Available'
                    # Convert to list format for database
                    rooms_list_for_db = []
                    for rnum, rdata in rooms.items():
                        room_record = rdata.copy()
                        room_record['room_number'] = str(rnum)
                        if 'id' not in room_record:
                            room_record['id'] = generate_id()
                        rooms_list_for_db.append(room_record)

                    save_data('rooms.json', rooms_list_for_db, selected_hotel)
                    st.success(f"Room {room_num} maintenance completed")
                    st.rerun()

# Room analytics
st.markdown("---")
st.markdown("### Room Analytics")

col1, col2, col3 = st.columns(3)

with col1:
    occupancy_rate = (occupied_rooms / len(rooms)) * 100
    st.metric("Occupancy Rate", f"{occupancy_rate:.1f}%")

with col2:
    total_revenue_potential = sum(room['price'] for room in rooms.values())
    current_revenue = sum(room['price'] for room in rooms.values() if room['status'] == 'Occupied')
    st.metric("Today's Revenue", f"₹{current_revenue:,.2f}")

with col3:
    avg_room_rate = sum(room['price'] for room in rooms.values()) / len(rooms)
    st.metric("Average Room Rate", f"₹{avg_room_rate:,.2f}")

# Room details table
if user_role == 'Admin':
    st.markdown("---")
    st.markdown("### Room Details Table")

    room_details = []
    for room_num, room_data in rooms.items():
        room_details.append({
            'Room': f"Room {room_num}",
            'Status': room_data['status'],
            'Type': room_data['type'],
            'Price': f"₹{room_data['price']:,}",
            'Guest': room_data.get('current_guest', '-'),
            'Check-in': room_data.get('checkin_date', '-'),
            'Check-out': room_data.get('checkout_date', '-'),
            'Phone': room_data.get('guest_phone', '-')
        })

    df_rooms = pd.DataFrame(room_details)
    st.dataframe(df_rooms, use_container_width=True, hide_index=True)