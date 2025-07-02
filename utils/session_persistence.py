
import streamlit as st
import json
import os
from datetime import datetime, timedelta

def save_session_state():
    """Save critical session state to persistent storage"""
    try:
        session_data = {
            'authenticated': st.session_state.get('authenticated', False),
            'username': st.session_state.get('username', ''),
            'user_role': st.session_state.get('user_role', ''),
            'hotel_access': st.session_state.get('hotel_access', ''),
            'selected_hotel': st.session_state.get('selected_hotel', 'hotel1'),
            'hotel_name': st.session_state.get('hotel_name', ''),
            'last_activity': datetime.now().isoformat()
        }
        
        # Save to persistent location
        os.makedirs('data/sessions', exist_ok=True)
        session_file = f"data/sessions/session_{st.session_state.get('username', 'unknown')}.json"
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Create backup of session file
        backup_session_file = f"{session_file}.backup"
        with open(backup_session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
            
    except Exception as e:
        print(f"Failed to save session state: {e}")

def restore_session_state():
    """Restore session state from persistent storage"""
    try:
        # Check if user was recently active
        sessions_dir = 'data/sessions'
        if not os.path.exists(sessions_dir):
            return False
            
        # Look for recent session files
        import glob
        session_files = glob.glob(os.path.join(sessions_dir, 'session_*.json'))
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Keep sessions permanently - no expiration
                last_activity = datetime.fromisoformat(session_data.get('last_activity', ''))
                # Sessions never expire - always restore if file exists
                # Restore session
                for key, value in session_data.items():
                    if key != 'last_activity':
                        st.session_state[key] = value
                
                print(f"Restored session for user: {session_data.get('username', 'unknown')}")
                return True
                    
            except Exception:
                continue
                
        return False
        
    except Exception as e:
        print(f"Failed to restore session state: {e}")
        return False

def cleanup_old_sessions():
    """Sessions are now permanent - no cleanup performed"""
    # Sessions are kept permanently for lifetime storage
    # No automatic deletion of session files
    pass
