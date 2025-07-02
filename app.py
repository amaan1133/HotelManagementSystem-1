import streamlit as st
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.auth import check_authentication, login_page

# Initialize database system instead of JSON files
print("=== INITIALIZING DATABASE SYSTEM ===")
try:
    from utils.database_data_manager import initialize_database_system, ensure_database_only_operation
    initialize_database_system()
    
    # Ensure database-only operation
    if ensure_database_only_operation():
        print("Database system initialized successfully - JSON files disabled")
    else:
        print("WARNING: Database system validation failed")
except Exception as e:
    print(f"Database system initialization failed: {e}")
    # Database initialization is required for the system to work
    print("Database system is mandatory - please check database connection")

# Enhanced data integrity check and repair on startup
try:
    from utils.data_integrity import check_all_data_integrity, repair_corrupted_files, ensure_data_directory
    
    # Ensure all directories exist
    ensure_data_directory()
    
    # Check data integrity
    issues = check_all_data_integrity()
    if issues:
        print(f"Data integrity issues detected: {issues}")
        # Attempt to repair issues
        success, repairs = repair_corrupted_files()
        if success:
            print(f"Successfully repaired data files: {repairs}")
        else:
            print(f"Some data files could not be repaired: {repairs}")
            # Continue running but log the issues
    else:
        print("All data files passed integrity check")
        
except Exception as e:
    print(f"Data integrity check failed: {e}")
    # Continue running even if integrity check fails

# Configure page
st.set_page_config(
    page_title="Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS styling
st.markdown("""
<style>
    .main-header {
        background: #2E86AB;
        padding: 1rem;
        border-radius: 5px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 5px;
    }
    .stSelectbox > div > div {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Check authentication and show login if needed
    if not check_authentication():
        login_page()
        return
    
    # Welcome message for authenticated users
    st.sidebar.success(f"Welcome, {st.session_state.username}!")

    # Hotel selection based on user's access
    # Use hardcoded hotel data instead of database/JSON for better reliability
    hotels = [
        {'id': 'hotel1', 'name': 'Saz Valley Kishtwar'},
        {'id': 'hotel2', 'name': 'Saz Valley Bhaderwah'}
    ]
    
    if hotels:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🏨 Hotel Location")
        hotel_options = {
            'hotel1': 'Saz Valley Kistwar',
            'hotel2': 'Saz Valley Bhaderwah'
        }

        # Get user's hotel access - ensure it exists
        user_hotel_access = st.session_state.get('hotel_access', 'both')

        # Filter available hotels based on user's access
        if user_hotel_access == 'hotel1':
            available_hotels = ['hotel1']
        elif user_hotel_access == 'hotel2':
            available_hotels = ['hotel2']
        else:  # both or any other value defaults to both
            available_hotels = ['hotel1', 'hotel2']

        # Get current selected hotel from session state
        current_hotel = st.session_state.get('selected_hotel', available_hotels[0])

        # Ensure current hotel is in available hotels
        if current_hotel not in available_hotels:
            current_hotel = available_hotels[0]

        current_index = available_hotels.index(current_hotel) if current_hotel in available_hotels else 0

        # Always show the selectbox for hotel selection
        selected_hotel = st.sidebar.selectbox(
            "Switch Location",
            options=available_hotels,
            format_func=lambda x: hotel_options[x],
            index=current_index,
            key="hotel_selector"
        )
        
        # Show access info
        if len(available_hotels) == 1:
            st.sidebar.info(f"✓ Access: {hotel_options[available_hotels[0]]}")
        else:
            st.sidebar.success(f"✓ Current: {hotel_options[selected_hotel]}")

        # Store selected hotel in session state
        st.session_state['selected_hotel'] = selected_hotel
        st.session_state['hotel_name'] = hotel_options[selected_hotel]

    # Main dashboard
    current_hotel = st.session_state.get('hotel_name', 'Hotel Management System')
    st.markdown(f'<div class="main-header"><h2>{current_hotel}</h2></div>', unsafe_allow_html=True)
    
    # Hotel switcher at top of main content (for multi-hotel access users)
    user_hotel_access = st.session_state.get('hotel_access', 'both')
    if user_hotel_access == 'both':
        st.markdown("### 🏨 Switch Hotel Location")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            current_hotel_key = st.session_state.get('selected_hotel', 'hotel1')
            hotel_options_main = {
                'hotel1': 'Saz Valley Kistwar',
                'hotel2': 'Saz Valley Bhaderwah'
            }
            
            selected_hotel_main = st.selectbox(
                "Choose Location:",
                options=['hotel1', 'hotel2'],
                format_func=lambda x: hotel_options_main[x],
                index=0 if current_hotel_key == 'hotel1' else 1,
                key="main_hotel_selector"
            )
            
            # Update session state if changed
            if selected_hotel_main != st.session_state.get('selected_hotel'):
                st.session_state['selected_hotel'] = selected_hotel_main
                st.session_state['hotel_name'] = hotel_options_main[selected_hotel_main]
                st.rerun()
        
        st.markdown("---")

    # Welcome message with role privileges
    user_role = st.session_state.get('user_role', 'User')
    username = st.session_state.get('username', 'User')

    if user_role == 'Admin':
        st.success(f"Welcome, {username}! You are logged in as **{user_role}** - Full access to upload, view, edit and delete all data")
    else:
        st.success(f"Welcome, {username}! You are logged in as **{user_role}** - You can upload data and view all sections")

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Get current hotel and show appropriate room count
        current_hotel = st.session_state.get('selected_hotel', 'hotel1')
        if current_hotel == 'hotel1':
            st.metric("Total Rooms", "8", "101-108")
        else:
            st.metric("Total Rooms", "17", "101-103, 201-203, 301-305, 401-403, 501-503")

    with col2:
        st.metric("Active Users", len(st.session_state.get('users', {})), "Registered")

    with col3:
        st.metric("Today's Sales", "₹0", "Current day")

    with col4:
        st.metric("Pending Dues", "₹0", "Outstanding")

    # Navigation instructions
    st.markdown("---")
    st.markdown("### 📱 Navigation")
    st.info("Use the sidebar to navigate between different sections of the hotel management system.")

    # Quick actions
    st.markdown("### Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Add Sale", type="primary"):
            st.switch_page("pages/3_Sales_Management.py")

    with col2:
        if st.button("Cash Sales", type="primary"):
            st.switch_page("pages/12_Cash_Sales.py")

    with col3:
        if st.button("Account Sales", type="primary"):
            st.switch_page("pages/11_Account_Sales.py")

    with col4:
        if st.button("Cash Handover", type="primary"):
            st.switch_page("pages/13_Cash_Handover.py")

    # Features overview
    st.markdown("### Available Features")

    features = [
        "User Management (Admin only)",
        "Room Management (Hotel specific rooms)", 
        "Cash Sales (Immediate payment)",
        "Account Sales (Credit sales)",
        "Outstanding Dues (Auto-move to sales when paid)",
        "Advance Payments (Auto-move to sales when utilized)",
        "Bill Upload System",
        "Room Service Management",
        "Analytics Dashboard"
    ]

    for feature in features:
        st.write(f"• {feature}")

    if user_role == 'Admin':
        st.success("As admin, you can edit and delete all records")

    # Logout button
    st.markdown("---")
    if st.button("🚪 Logout", type="secondary"):
        # Clear persistent session files
        import glob
        username = st.session_state.get('username', 'unknown')
        session_files = glob.glob(f"data/sessions/session_{username}.*")
        for session_file in session_files:
            try:
                os.remove(session_file)
            except:
                pass
        
        # Clear all session state for proper logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state['authenticated'] = False
        st.rerun()

    # Sidebar navigation for authenticated users
    st.sidebar.title("Navigation")

    if user_role == 'Admin':
        if st.sidebar.button("User Management"):
            st.switch_page("pages/1_User_Management.py")

    # All authenticated users can access these
    if st.sidebar.button("Room Management"):
        st.switch_page("pages/2_Room_Management.py")

    if st.sidebar.button("Sales Management"):
        st.switch_page("pages/3_Sales_Management.py")

    if st.sidebar.button("Expenditure Management"):
        st.switch_page("pages/4_Expenditure_Management.py")

    if st.sidebar.button("Room Service"):
        st.switch_page("pages/5_Room_Service.py")

    if st.sidebar.button("Complementary Rooms"):
        st.switch_page("pages/6_Complementary_Rooms.py")

    if st.sidebar.button("Advance Payments"):
        st.switch_page("pages/7_Advance_Payments.py")

    if st.sidebar.button("Outstanding Dues"):
        st.switch_page("pages/9_Outstanding_Dues.py")

    if st.sidebar.button("Bad Debt"):
        st.switch_page("pages/14_Bad_Debt.py")

    if st.sidebar.button("Discount"):
        st.switch_page("pages/15_Discount.py")

    if st.sidebar.button("Bill Upload"):
        st.switch_page("pages/10_Bill_Upload.py")

    if st.sidebar.button("Dashboard"):
        st.switch_page("pages/8_Dashboard.py")

    if st.sidebar.button("Financial Summary"):
        st.switch_page("pages/16_Financial_Summary.py")

    if st.sidebar.button("Account Handover"):
        st.switch_page("pages/17_Account_Handover.py")
    
    if st.sidebar.button("Data Recovery"):
        st.switch_page("pages/20_Data_Recovery.py")
    
    if st.sidebar.button("🛡️ Data Protection"):
        st.switch_page("pages/21_Data_Protection_Status.py")

    # Restaurant button - only show for Hotel 2 users
    user_hotel_access = st.session_state.get('hotel_access', 'both')
    current_selected_hotel = st.session_state.get('selected_hotel', 'hotel1')
    
    if user_hotel_access == 'hotel2' or (user_hotel_access == 'both' and current_selected_hotel == 'hotel2'):
        if st.sidebar.button("🍽️ Restaurant"):
            st.switch_page("pages/19_Restaurant.py")

    # Custom CSS for page hiding based on user access
    hide_pages_css = ""

    # Hide pages based on user role
    if user_role != 'Admin':
        hide_pages_css += """
        a[href*="User_Management"] { display: none !important; }
        a[href*="Bill_Upload"] { display: none !important; }
        a[href*="Data_Download"] { display: none !important; }
        """

    # Hide restaurant page from hotel1 users
    user_hotel_access = st.session_state.get('hotel_access', 'both')
    current_selected_hotel = st.session_state.get('selected_hotel', 'hotel1')

    if user_hotel_access == 'hotel1' or (user_hotel_access == 'both' and current_selected_hotel == 'hotel1'):
        hide_pages_css += """
        a[href*="Restaurant"] { display: none !important; }
        """

    # Apply CSS for hiding pages
    st.markdown(f'<style>{hide_pages_css}</style>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()