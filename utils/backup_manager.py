import json
import os
import shutil
from datetime import datetime

def create_backup():
    """Create a backup of all data files"""
    try:
        # Create backup directory if it doesn't exist
        backup_dir = 'data/backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Create timestamp for backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'backup_{timestamp}')
        
        # Copy entire data directory
        shutil.copytree('data', backup_path, ignore=shutil.ignore_patterns('backups'))
        
        return True, f"Backup created successfully at {backup_path}"
    except Exception as e:
        return False, f"Backup failed: {str(e)}"

def list_backups():
    """List all available backups"""
    try:
        backup_dir = 'data/backups'
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for item in os.listdir(backup_dir):
            backup_path = os.path.join(backup_dir, item)
            if os.path.isdir(backup_path) and item.startswith('backup_'):
                # Extract timestamp from folder name
                timestamp_str = item.replace('backup_', '')
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    backups.append({
                        'name': item,
                        'path': backup_path,
                        'timestamp': timestamp,
                        'formatted_date': timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except ValueError:
                    continue
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
    except Exception:
        return []

def restore_from_backup(backup_name):
    """Restore data from a specific backup"""
    try:
        backup_path = os.path.join('data/backups', backup_name)
        
        if not os.path.exists(backup_path):
            return False, "Backup not found"
        
        # Create current backup before restore
        create_backup()
        
        # Get list of files to restore (excluding backups folder)
        for item in os.listdir(backup_path):
            if item == 'backups':
                continue
                
            source_path = os.path.join(backup_path, item)
            dest_path = os.path.join('data', item)
            
            if os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
            elif os.path.isdir(source_path):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
        
        return True, f"Data restored successfully from {backup_name}"
    except Exception as e:
        return False, f"Restore failed: {str(e)}"

def restore_system_defaults():
    """Restore system default users and essential data"""
    try:
        from utils.auth import ensure_system_users
        from utils.data_manager import initialize_data
        
        # Restore system users
        users = ensure_system_users({})
        
        # Reinitialize all data files
        initialize_data()
        
        return True, "System defaults restored successfully"
    except Exception as e:
        return False, f"System restore failed: {str(e)}"