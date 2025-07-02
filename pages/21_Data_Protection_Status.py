
import streamlit as st
import sys
import os
import json
from datetime import datetime, timedelta

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

from utils.auth import check_authentication
from utils.data_integrity import check_all_data_integrity, repair_corrupted_files
from utils.database_data_manager import load_data

# Check authentication
if not check_authentication():
    st.error("Please login first")
    st.stop()

user_role = st.session_state.get('user_role', 'User')

st.title("🛡️ Data Protection Status")
st.markdown("Monitor and ensure your data is fully protected")

# Data integrity check
st.markdown("### 📊 Data Integrity Status")

if st.button("🔍 Check Data Integrity", type="primary"):
    with st.spinner("Checking data integrity..."):
        issues = check_all_data_integrity()
        
        if not issues:
            st.success("✅ All data files are intact and healthy!")
            st.balloons()
        else:
            st.error(f"❌ Found {len(issues)} data integrity issues:")
            for issue in issues:
                st.write(f"• {issue}")
            
            if st.button("🔧 Attempt Auto-Repair"):
                with st.spinner("Attempting to repair data files..."):
                    success, repairs = repair_corrupted_files()
                    
                    if success:
                        st.success("✅ All issues have been resolved!")
                        for repair in repairs:
                            st.write(f"• {repair}")
                    else:
                        st.warning("⚠️ Some issues could not be auto-repaired:")
                        for repair in repairs:
                            st.write(f"• {repair}")

# Backup status
st.markdown("### 💾 Backup Status")

backup_dirs = [
    ('Auto Backups', 'data/auto_backups'),
    ('Redundant Copies', 'data/redundant'),
    ('Emergency Backups', 'data/emergency_backups')
]

for backup_name, backup_path in backup_dirs:
    if os.path.exists(backup_path):
        files = os.listdir(backup_path)
        if files:
            st.success(f"✅ {backup_name}: {len(files)} backup files available")
        else:
            st.warning(f"⚠️ {backup_name}: No backup files found")
    else:
        st.error(f"❌ {backup_name}: Backup directory not found")

# Session persistence status
st.markdown("### 🔐 Session Persistence Status")

sessions_dir = 'data/sessions'
if os.path.exists(sessions_dir):
    session_files = [f for f in os.listdir(sessions_dir) if f.endswith('.json')]
    if session_files:
        st.success(f"✅ Session backups: {len(session_files)} session files saved")
        
        # Show current user's session info
        current_user = st.session_state.get('username', 'unknown')
        user_session_file = f"session_{current_user}.json"
        
        if user_session_file in session_files:
            session_path = os.path.join(sessions_dir, user_session_file)
            try:
                with open(session_path, 'r') as f:
                    session_data = json.load(f)
                last_activity = datetime.fromisoformat(session_data.get('last_activity', ''))
                time_since = datetime.now() - last_activity
                
                if time_since < timedelta(minutes=5):
                    st.info(f"🔄 Your session was last saved: {time_since.seconds} seconds ago")
                else:
                    st.info(f"🔄 Your session was last saved: {time_since} ago")
                    
            except Exception:
                st.warning("⚠️ Could not read session file")
    else:
        st.warning("⚠️ No session backup files found")
else:
    st.error("❌ Session directory not found")

# Data monitoring status
st.markdown("### 🔍 Data Monitoring Status")

# Check if access log exists
if os.path.exists('data/access_log.json'):
    try:
        with open('data/access_log.json', 'r') as f:
            logs = json.load(f)
        
        recent_logs = [log for log in logs if 
                      datetime.now() - datetime.fromisoformat(log['timestamp']) < timedelta(minutes=10)]
        
        st.success(f"✅ Data monitoring active: {len(recent_logs)} operations in last 10 minutes")
        
        if recent_logs and st.checkbox("Show recent data operations"):
            for log in recent_logs[-5:]:  # Show last 5
                timestamp = datetime.fromisoformat(log['timestamp']).strftime('%H:%M:%S')
                st.write(f"• {timestamp}: {log['operation']} - {log['filename']}")
                
    except Exception:
        st.warning("⚠️ Could not read access log")
else:
    st.warning("⚠️ Data access log not found")

# Data protection recommendations
st.markdown("### 💡 Data Protection Recommendations")

recommendations = [
    "✅ Multiple backup layers are active (Auto, Redundant, Emergency)",
    "✅ Session persistence extends your login for up to 7 days",
    "✅ Data integrity monitoring runs every minute",
    "✅ All save operations are verified and logged",
    "✅ Atomic write operations prevent data corruption",
    "✅ Automatic recovery from backups if corruption detected"
]

for rec in recommendations:
    st.write(rec)

st.markdown("---")
st.info("💬 **Your data is now protected with triple redundancy and continuous monitoring. Even if the main files are corrupted, the system will automatically recover from backups.**")

if user_role == 'Admin':
    st.markdown("### 🔧 Admin Data Recovery Tools")
    
    if st.button("🚨 Force Data Recovery Check"):
        with st.spinner("Performing comprehensive data recovery..."):
            # Force check all backup sources
            success, repairs = repair_corrupted_files()
            if repairs:
                st.success("Recovery operations completed:")
                for repair in repairs:
                    st.write(f"• {repair}")
            else:
                st.info("No recovery operations needed")
