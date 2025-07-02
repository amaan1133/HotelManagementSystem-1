import streamlit as st
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication, create_user, delete_user, load_users
import pandas as pd

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

# Check admin privileges
if st.session_state.get('user_role') != 'Admin':
    st.error("Access denied. Only admin can manage users.")
    st.stop()

st.title("👥 User Management")

# Show current admin's context
current_hotel_access = st.session_state.get('hotel_access', 'both')
current_selected_hotel = st.session_state.get('selected_hotel', 'hotel1')

if current_hotel_access == 'both':
    hotel_context = f"Currently managing: **{st.session_state.get('hotel_name', 'Unknown')}**"
    st.info(f"{hotel_context} - Users created will have access to this hotel only")
else:
    hotel_name = "Saz Valley Kistwar" if current_hotel_access == 'hotel1' else "Saz Valley Bhaderwah"
    st.info(f"You can only create users for: **{hotel_name}**")

# Create user section
st.markdown("### Create New User")
with st.form("create_user_form"):
    col1, col2 = st.columns(2)
    with col1:
        new_username = st.text_input("Username", placeholder="Enter username")
        new_password = st.text_input("Password", type="password", placeholder="Enter password")
    with col2:
        user_role = st.selectbox("Role", ["User", "Manager"])
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
    
    create_button = st.form_submit_button("Create User", type="primary")
    
    if create_button:
        if not new_username or not new_password:
            st.error("Username and password are required")
        elif new_password != confirm_password:
            st.error("Passwords do not match")
        elif len(new_password) < 6:
            st.error("Password must be at least 6 characters long")
        else:
            success, message = create_user(new_username, new_password, user_role)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

st.markdown("---")

# User list section
st.markdown("### User List")
users = load_users()

if users:
    # Convert to DataFrame for better display
    user_data = []
    for username, info in users.items():
        hotel_access = info.get('hotel_access', 'both')
        if hotel_access == 'hotel1':
            hotel_name = 'Saz Valley Kistwar'
        elif hotel_access == 'hotel2':
            hotel_name = 'Saz Valley Bhaderwah'
        else:
            hotel_name = 'Both Hotels'
        
        user_data.append({
            'Username': username,
            'Role': info['role'],
            'Hotel Access': hotel_name,
            'Created Date': info.get('created_date', 'Unknown'),
            'Actions': username
        })
    
    df = pd.DataFrame(user_data)
    
    # Display users in a table format
    for index, row in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 1])
        
        with col1:
            st.write(f"**{row['Username']}**")
        with col2:
            st.write(row['Role'])
        with col3:
            st.write(row['Hotel Access'])
        with col4:
            st.write(row['Created Date'])
        with col5:
            if row['Username'] != 'admin':  # Can't delete admin
                if st.button(f"Delete", key=f"delete_{row['Username']}", type="secondary"):
                    success, message = delete_user(row['Username'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.write("Admin")
        
        st.markdown("---")

else:
    st.info("No users found")

# User statistics
st.markdown("### User Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    total_users = len(users)
    st.metric("Total Users", total_users)

with col2:
    admin_count = len([u for u in users.values() if u['role'] == 'Admin'])
    st.metric("Admin Users", admin_count)

with col3:
    regular_users = len([u for u in users.values() if u['role'] == 'User'])
    st.metric("Regular Users", regular_users)
