import streamlit as st
import json
import hashlib
import os

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    try:
        with open('data/users.json', 'r') as f:
            users = json.load(f)
            # Ensure system users exist
            users = ensure_system_users(users)
            return users
    except FileNotFoundError:
        # Create default users if file doesn't exist
        return ensure_system_users({})

def ensure_system_users(users):
    """Ensure system users exist and are properly configured"""
    system_users_added = False
    
    # Admin user
    if 'admin' not in users:
        users['admin'] = {
            'password': hash_password('admin@12345'),
            'role': 'Admin',
            'created_date': '2025-06-23',
            'hotel_access': 'both'
        }
        system_users_added = True
        
    # Permanent Saz Valley Bhaderwah user
    if 'SazB' not in users:
        users['SazB'] = {
            'password': hash_password('sazbhaderwah'),
            'role': 'User',
            'created_date': '2025-07-01',
            'hotel_access': 'hotel2'
        }
        system_users_added = True
        
    # Permanent Saz Valley Kistwar user
    if 'SazK' not in users:
        users['SazK'] = {
            'password': hash_password('sazkishtwar'),
            'role': 'User',
            'created_date': '2025-07-01',
            'hotel_access': 'hotel1'
        }
        system_users_added = True
        
    # Save if any system users were added
    if system_users_added:
        save_users(users)
        
    return users

def save_users(users):
    """Save users to JSON file"""
    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=2)

def check_authentication():
    """Check if user is authenticated with persistent sessions"""
    # Check if user is authenticated and session is still valid
    authenticated = st.session_state.get('authenticated', False)
    username = st.session_state.get('username', None)

    # If user is authenticated and has username, keep session active
    if authenticated and username:
        return True

    return False

def login_page():
    """Display login page"""
    st.title("🏨 Saz Valley Hotels Management System - Login")

    # Clear any residual session state
    if 'login_error' not in st.session_state:
        st.session_state['login_error'] = False

    with st.form("login_form"):
        st.markdown("### Please login to continue")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login", type="primary")

        if submit_button:
            if username and password:
                if authenticate_user(username, password):
                    st.success("Login successful!")
                    st.session_state['login_error'] = False
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    st.session_state['login_error'] = True
            else:
                st.error("Please enter both username and password")
                st.session_state['login_error'] = True

    # Login help section
    st.markdown("---")
    st.info("**Need help?** Contact your system administrator for login credentials.")

def authenticate_user(username, password):
    """Authenticate user credentials"""
    try:
        users = load_users()  # This now automatically ensures system users exist
        
        # Fix existing admin user if it doesn't have hotel_access or has wrong access
        if 'admin' in users:
            if 'hotel_access' not in users['admin'] or users['admin']['hotel_access'] != 'both':
                users['admin']['hotel_access'] = 'both'
                save_users(users)

        # Check credentials without modifying stored passwords
        if username in users:
            hashed_input_password = hash_password(password)
            if users[username]['password'] == hashed_input_password:
                # Set session state
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['user_role'] = users[username]['role']
                st.session_state['users'] = users
                st.session_state['login_successful'] = True

                # Set hotel access
                user_hotel_access = users[username].get('hotel_access', 'both')
                st.session_state['hotel_access'] = user_hotel_access

                # Initialize hotel selection based on user access
                if user_hotel_access == 'hotel1':
                    st.session_state['selected_hotel'] = 'hotel1'
                    st.session_state['hotel_name'] = 'Saz Valley Kistwar (Rooms 101-108)'
                elif user_hotel_access == 'hotel2':
                    st.session_state['selected_hotel'] = 'hotel2'
                    st.session_state['hotel_name'] = 'Saz Valley Bhaderwah (Rooms 101-103, 201-203, 301-305, 401-403, 501-503)'
                else:  # both
                    st.session_state['selected_hotel'] = 'hotel1'
                    st.session_state['hotel_name'] = 'Saz Valley Kistwar (Rooms 101-108)'

                return True

        return False
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

def create_user(username, password, role='User'):
    """Create a new user (Admin only)"""
    if st.session_state.get('user_role') != 'Admin':
        return False, "Only admin can create users"

    users = load_users()

    if username in users:
        return False, "Username already exists"

    # Determine hotel access based on current admin's selected hotel
    current_admin_hotel_access = st.session_state.get('hotel_access', 'both')
    current_selected_hotel = st.session_state.get('selected_hotel', 'hotel1')

    # If admin has access to both hotels, use currently selected hotel
    # If admin has access to only one hotel, use that hotel
    if current_admin_hotel_access == 'both':
        user_hotel_access = current_selected_hotel
    else:
        user_hotel_access = current_admin_hotel_access

    users[username] = {
        'password': hash_password(password),
        'role': role,
        'created_date': '2025-06-23',
        'hotel_access': user_hotel_access
    }

    save_users(users)
    st.session_state['users'] = users

    hotel_name = "Saz Valley Kistwar" if user_hotel_access == 'hotel1' else "Saz Valley Bhaderwah"
    return True, f"User created successfully with access to {hotel_name}"

def delete_user(username):
    """Delete a user (Admin only)"""
    if st.session_state.get('user_role') != 'Admin':
        return False, "Only admin can delete users"

    # Protect system users from deletion
    system_users = ['admin', 'SazB', 'SazK']
    if username in system_users:
        return False, f"Cannot delete system user '{username}'"

    users = load_users()

    if username not in users:
        return False, "User not found"

    del users[username]
    save_users(users)
    st.session_state['users'] = users
    return True, "User deleted successfully"