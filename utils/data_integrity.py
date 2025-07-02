import json
import os
from datetime import datetime
import uuid
import shutil
import threading
import time

# Global lock for file operations
file_lock = threading.Lock()

def ensure_data_directory():
    """Ensure data directory exists with all backup directories"""
    directories = [
        'data',
        'data/auto_backups',
        'data/redundant',
        'data/emergency_backups',
        'data/sessions'
    ]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def log_data_access(operation, filename, hotel=None):
    """Log all data access operations for audit trail"""
    ensure_data_directory()
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'filename': filename,
        'hotel': hotel,
        'thread_id': threading.current_thread().ident
    }

    log_file = 'data/access_log.json'
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        # Keep more log entries for permanent storage
        if len(logs) > 5000:
            logs = logs[-5000:]

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Failed to log data access: {e}")

def create_emergency_backup(filename, data):
    """Create emergency backup with timestamp"""
    ensure_data_directory()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    backup_filename = f"emergency_{filename}_{timestamp}.json"
    backup_path = os.path.join('data/emergency_backups', backup_filename)

    try:
        with open(backup_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Keep more emergency backups for permanent storage (keep last 200 per file)
        import glob
        pattern = os.path.join('data/emergency_backups', f"emergency_{filename}_*.json")
        backups = sorted(glob.glob(pattern))
        while len(backups) > 200:
            os.remove(backups.pop(0))

    except Exception as e:
        print(f"Failed to create emergency backup: {e}")

def verify_data_integrity(filename, expected_data):
    """Verify that saved data matches expected data"""
    try:
        filepath = os.path.join('data', filename)
        if not os.path.exists(filepath):
            return False

        with open(filepath, 'r') as f:
            saved_data = json.load(f)

        return saved_data == expected_data
    except Exception:
        return False

def check_all_data_integrity():
    """Check integrity of all critical data files"""
    issues = []
    critical_files = [
        'sales.json', 'rooms.json', 'expenditures.json',
        'advance_payments.json', 'outstanding_dues.json'
    ]

    for hotel in ['hotel1', 'hotel2']:
        for filename in critical_files:
            hotel_filename = f"{hotel}_{filename}"
            filepath = os.path.join('data', hotel_filename)

            if not os.path.exists(filepath):
                issues.append(f"Missing file: {hotel_filename}")
                continue

            try:
                with open(filepath, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        issues.append(f"Empty file: {hotel_filename}")
                        continue
                    json.loads(content)
            except Exception as e:
                issues.append(f"Corrupted file: {hotel_filename} - {str(e)}")

    return issues

def repair_corrupted_files():
    """Attempt to repair corrupted files from backups"""
    repairs = []
    success = True

    issues = check_all_data_integrity()

    for issue in issues:
        if "Missing file:" in issue or "Empty file:" in issue or "Corrupted file:" in issue:
            filename = issue.split(": ")[1].split(" - ")[0]

            # Try to restore from various backup sources
            restored = False

            # Try redundant copy first
            redundant_path = os.path.join('data/redundant', filename)
            if os.path.exists(redundant_path):
                try:
                    shutil.copy2(redundant_path, os.path.join('data', filename))
                    repairs.append(f"Restored {filename} from redundant copy")
                    restored = True
                except Exception:
                    pass

            # Try regular backup
            if not restored:
                backup_path = os.path.join('data/auto_backups', f"{filename}.backup")
                if os.path.exists(backup_path):
                    try:
                        shutil.copy2(backup_path, os.path.join('data', filename))
                        repairs.append(f"Restored {filename} from backup")
                        restored = True
                    except Exception:
                        pass

            # Try emergency backups
            if not restored:
                import glob
                emergency_pattern = os.path.join('data/emergency_backups', f"emergency_{filename}_*.json")
                emergency_backups = sorted(glob.glob(emergency_pattern), reverse=True)

                for emergency_backup in emergency_backups:
                    try:
                        shutil.copy2(emergency_backup, os.path.join('data', filename))
                        repairs.append(f"Restored {filename} from emergency backup")
                        restored = True
                        break
                    except Exception:
                        continue

            if not restored:
                success = False
                repairs.append(f"Failed to restore {filename}")

    return success, repairs