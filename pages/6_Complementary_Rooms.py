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

# All users can add complementary room data, admin can edit/delete
user_role = st.session_state.get('user_role', 'User')

st.title("🎁 Complementary Rooms Management")

# Load data
selected_hotel = st.session_state.get('selected_hotel') or 'hotel1'
complementary_rooms = load_data('complementary_rooms.json', selected_hotel)
rooms_list = load_data('rooms.json', selected_hotel)

# Convert list to dictionary if needed
if isinstance(rooms_list, list):
    rooms = {}
    for room in rooms_list:
        if isinstance(room, dict) and 'room_number' in room:
            rooms[room['room_number']] = room
else:
    rooms = rooms_list if rooms_list else {}

# Complementary rooms overview
st.markdown("### Complementary Rooms Overview")

# Calculate totals
total_comp_rooms = len(complementary_rooms)
active_comp_rooms = len([c for c in complementary_rooms if c['status'] == 'Active'])
completed_comp_rooms = len([c for c in complementary_rooms if c['status'] == 'Completed'])
total_value = sum(c['room_value'] for c in complementary_rooms)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Comp Rooms", total_comp_rooms)
with col2:
    st.metric("Active", active_comp_rooms)
with col3:
    st.metric("Completed", completed_comp_rooms)
with col4:
    st.metric("Total Value", f"₹{total_value:,.2f}")

st.markdown("---")

# Add new complementary room
st.markdown("### Add Complementary Room")

with st.form("add_comp_room_form"):
    col1, col2 = st.columns(2)

    with col1:
        # Get available rooms
        available_rooms = [f"Room {k}" for k, v in sorted(rooms.items(), key=lambda x: int(x[0])) if v['status'] == 'Available']
        if available_rooms:
            selected_room = st.selectbox("Room Number", available_rooms)
        else:
            st.warning("No rooms available")
            # Show all rooms for selected hotel when none are available
            all_rooms = [f"Room {k}" for k in sorted(rooms.keys(), key=lambda x: int(x))]
            selected_room = st.selectbox("Room Number", all_rooms)

        guest_name = st.text_input("Guest Name", placeholder="Enter guest name")
        guest_contact = st.text_input("Guest Contact", placeholder="Phone number")
        checkin_date = st.date_input("Check-in Date")
        checkout_date = st.date_input("Check-out Date")

    with col2:
        comp_reason = st.selectbox("Complementary Reason", [
            "VIP Guest",
            "Loyalty Program",
            "Booking Issue Compensation",
            "Corporate Partnership",
            "Marketing Campaign",
            "Staff Family",
            "Influencer/Media",
            "Other"
        ])

        if comp_reason == "Other":
            custom_reason = st.text_input("Specify Reason", placeholder="Enter custom reason")
        else:
            custom_reason = ""

        # Get room price for value calculation
        room_num = selected_room.split()[1] if selected_room else "101"
        room_price = rooms.get(room_num, {}).get('price', 2000)

        # Calculate nights and value
        if checkin_date and checkout_date and checkout_date > checkin_date:
            nights = (checkout_date - checkin_date).days
            total_value_calc = room_price * nights
        else:
            nights = 1
            total_value_calc = room_price

        st.write(f"**Nights:** {nights}")
        st.write(f"**Room Rate:** ₹{room_price}/night")
        st.write(f"**Total Value:** ₹{total_value_calc:,.2f}")

        approved_by = st.selectbox("Approved By", ["Manager", "Owner", "Admin"])
        special_notes = st.text_area("Special Notes", placeholder="Any special instructions")

    submit_comp_room = st.form_submit_button("Add Complementary Room", type="primary")

    if submit_comp_room:
        if not guest_name or not checkin_date or not checkout_date:
            st.error("Guest name, check-in and check-out dates are required")
        elif checkout_date <= checkin_date:
            st.error("Check-out date must be after check-in date")
        else:
            new_comp_room = {
                'id': generate_id(),
                'date': get_current_datetime(),
                'room_number': selected_room,
                'guest_name': guest_name,
                'guest_contact': guest_contact,
                'checkin_date': str(checkin_date),
                'checkout_date': str(checkout_date),
                'nights': nights,
                'room_rate': room_price,
                'room_value': total_value_calc,
                'comp_reason': comp_reason if comp_reason != "Other" else custom_reason,
                'approved_by': approved_by,
                'special_notes': special_notes,
                'status': 'Active',
                'created_by': st.session_state.get('username', 'Unknown')
            }

            complementary_rooms.append(new_comp_room)
            selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
            save_data('complementary_rooms.json', complementary_rooms, selected_hotel)
            st.success("Complementary room added successfully!")
            st.rerun()

st.markdown("---")

# Complementary rooms list
st.markdown("### Complementary Rooms Records")

if complementary_rooms:
    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "Active", "Completed", "Cancelled"])
    with col2:
        filter_reason = st.selectbox("Filter by Reason", ["All"] + list(set(c['comp_reason'] for c in complementary_rooms)))
    with col3:
        filter_approved_by = st.selectbox("Filter by Approved By", ["All"] + list(set(c['approved_by'] for c in complementary_rooms)))

    # Apply filters
    filtered_comp_rooms = complementary_rooms
    if filter_status != "All":
        filtered_comp_rooms = [c for c in filtered_comp_rooms if c['status'] == filter_status]
    if filter_reason != "All":
        filtered_comp_rooms = [c for c in filtered_comp_rooms if c['comp_reason'] == filter_reason]
    if filter_approved_by != "All":
        filtered_comp_rooms = [c for c in filtered_comp_rooms if c['approved_by'] == filter_approved_by]

    # Display complementary rooms
    for comp in filtered_comp_rooms:
        with st.expander(f"#{comp['id']} - {comp['guest_name']} - {comp['room_number']} - ₹{comp['room_value']:,.2f}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Created:** {comp['date']}")
                st.write(f"**Room:** {comp['room_number']}")
                st.write(f"**Guest:** {comp['guest_name']}")
                st.write(f"**Contact:** {comp.get('guest_contact', 'N/A')}")
                st.write(f"**Check-in:** {comp['checkin_date']}")
                st.write(f"**Check-out:** {comp['checkout_date']}")

            with col2:
                st.write(f"**Nights:** {comp['nights']}")
                st.write(f"**Room Rate:** ₹{comp['room_rate']}/night")
                st.write(f"**Total Value:** ₹{comp['room_value']:,.2f}")
                st.write(f"**Reason:** {comp['comp_reason']}")
                st.write(f"**Approved By:** {comp['approved_by']}")
                st.write(f"**Status:** {comp['status']}")

            if comp.get('special_notes'):
                st.write(f"**Special Notes:** {comp['special_notes']}")

            # Management actions
            col1, col2, col3 = st.columns(3)

            with col1:
                if comp['status'] == 'Active' and st.button(f"Check Out", key=f"checkout_{comp['id']}"):
                    # Update complementary room status
                    for c in complementary_rooms:
                        if c['id'] == comp['id']:
                            c['status'] = 'Completed'
                            c['actual_checkout'] = get_current_datetime()
                            break

                    # Update room status
                    room_num = comp['room_number'].split()[1]
                    if room_num in rooms:
                        rooms[room_num].update({
                            'status': 'Available',
                            'current_guest': None,
                            'checkin_date': None,
                            'checkout_date': None,
                            'booking_type': None
                        })
                        save_data('rooms.json', rooms, selected_hotel)

                    save_data('complementary_rooms.json', complementary_rooms, selected_hotel)
                    st.success("Guest checked out successfully!")
                    st.rerun()

            with col2:
                if comp['status'] == 'Active' and st.button(f"Cancel", key=f"cancel_{comp['id']}"):
                    for c in complementary_rooms:
                        if c['id'] == comp['id']:
                            c['status'] = 'Cancelled'
                            break

                    # Update room status
                    room_num = comp['room_number'].split()[1]
                    if room_num in rooms:
                        rooms[room_num].update({
                            'status': 'Available',
                            'current_guest': None,
                            'checkin_date': None,
                            'checkout_date': None,
                            'booking_type': None
                        })
                        save_data('rooms.json', rooms, selected_hotel)

                    save_data('complementary_rooms.json', complementary_rooms, selected_hotel)
                    st.warning("Complementary room cancelled!")
                    st.rerun()

            with col3:
                if user_role == 'Admin':
                    if st.button(f"Delete", key=f"delete_{comp['id']}", type="secondary"):
                        complementary_rooms = [c for c in complementary_rooms if c['id'] != comp['id']]
                        save_data('complementary_rooms.json', complementary_rooms, selected_hotel)
                        st.success("Record deleted!")
                        st.rerun()

            # Admin edit functionality
            if user_role == 'Admin':
                if st.button(f"Edit Comp Room", key=f"edit_comp_{comp['id']}"):
                    with st.form(f"edit_comp_form_{comp['id']}"):
                        new_guest_name = st.text_input("Guest Name", value=comp['guest_name'])
                        new_room_value = st.number_input("Room Value", value=comp['room_value'], min_value=0.0)
                        new_status = st.selectbox("Status", ["Active", "Completed", "Cancelled"], 
                                                index=["Active", "Completed", "Cancelled"].index(comp['status']))
                        if st.form_submit_button("Update Comp Room"):
                            for c in complementary_rooms:
                                if c['id'] == comp['id']:
                                    c['guest_name'] = new_guest_name
                                    c['room_value'] = new_room_value
                                    c['status'] = new_status
                                    break
                            save_data('complementary_rooms.json', complementary_rooms, selected_hotel)
                            st.success("Complementary room updated!")
                            st.rerun()

else:
    st.info("No complementary room records found")

# Statistics and analytics
if complementary_rooms:
    st.markdown("---")
    st.markdown("### Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Complementary Reasons:**")
        reason_counts = {}
        for comp in complementary_rooms:
            reason = comp['comp_reason']
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

        for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
            st.write(f"• {reason}: {count}")

    with col2:
        st.markdown("**Monthly Value Impact:**")
        monthly_value = sum(c['room_value'] for c in complementary_rooms if c['date'].startswith('2025-06'))
        st.write(f"• This Month: ₹{monthly_value:,.2f}")

        avg_value = monthly_value / len(complementary_rooms) if complementary_rooms else 0
        st.write(f"• Average per Room: ₹{avg_value:,.2f}")

# Approval workflow
st.markdown("---")
st.markdown("### Approval Guidelines")

st.info("""
**Complementary Room Approval Guidelines:**
- VIP Guest: Approved by Manager or above
- Loyalty Program: Automatic approval for qualifying members
- Booking Issue Compensation: Manager approval required
- Corporate Partnership: Pre-approved based on contract
- Marketing Campaign: Marketing team approval
- Staff Family: HR and Manager approval
- Influencer/Media: Marketing team approval
- Other: Case-by-case approval by Manager
""")

# Export functionality
if user_role == 'Admin' and complementary_rooms:
    st.markdown("---")
    if st.button("📊 Export Complementary Rooms Data"):
        df = pd.DataFrame(complementary_rooms)
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name=f"complementary_rooms_{get_current_datetime()[:10]}.csv",
            mime="text/csv"
        )