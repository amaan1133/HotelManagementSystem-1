import json
import os
from datetime import datetime
import uuid

def ensure_data_directory():
    """Ensure data directory exists"""
    if not os.path.exists('data'):
        os.makedirs('data')

def create_default_rooms_for_hotel(hotel):
    """Create default room structure for a specific hotel"""
    rooms = {}
    if hotel == 'hotel1':
        # Saz Valley Kistwar: rooms 101-108
        for i in range(101, 109):
            rooms[str(i)] = {
                'room_number': str(i),
                'status': 'Available',
                'type': 'Standard',
                'price': 2000,
                'current_guest': None,
                'checkin_date': None,
                'checkout_date': None
            }
    elif hotel == 'hotel2':
        # Saz Valley Bhaderwah: rooms 101-103, 201-203, 301-305, 401-403, 501-503
        room_ranges = [
            (101, 104), (201, 204), (301, 306), (401, 404), (501, 504)
        ]
        for start, end in room_ranges:
            for i in range(start, end):
                rooms[str(i)] = {
                    'room_number': str(i),
                    'status': 'Available',
                    'type': 'Standard',
                    'price': 2000,
                    'current_guest': None,
                    'checkin_date': None,
                    'checkout_date': None
                }
    return rooms

def initialize_data():
    """Initialize data files if they don't exist"""
    os.makedirs('data', exist_ok=True)

    # Ensure users.json exists
    users_file = 'data/users.json'
    if not os.path.exists(users_file):
        with open(users_file, 'w') as f:
            json.dump({}, f, indent=2)

    # Initialize hotel selection
    if not os.path.exists('data/hotels.json'):
        hotels = {
            "hotel1": {"name": "Hotel 1", "rooms_range": "101-108"},
            "hotel2": {"name": "Hotel 2", "rooms_range": "201-208"}
        }
        with open('data/hotels.json', 'w') as f:
            json.dump(hotels, f, indent=2)

    # Initialize hotel-specific rooms
    for hotel_id in ['hotel1', 'hotel2']:
        hotel_rooms_file = f'data/{hotel_id}_rooms.json'
        if not os.path.exists(hotel_rooms_file):
            rooms = {}
            # Hotel 1: rooms 101-108, Hotel 2: rooms 201-208
            start_room = 101 if hotel_id == 'hotel1' else 201
            for i in range(start_room, start_room + 8):
                rooms[str(i)] = {
                    'room_number': str(i),
                    'status': 'Available',
                    'type': 'Standard',
                    'price': 2000,
                    'current_guest': None,
                    'checkin_date': None,
                    'checkout_date': None
                }
            with open(hotel_rooms_file, 'w') as f:
                json.dump(rooms, f, indent=2)

    # Initialize main rooms.json for backward compatibility
    if not os.path.exists('data/rooms.json'):
        rooms = {}
        for i in range(101, 109):
            rooms[str(i)] = {
                'room_number': str(i),
                'status': 'Available',
                'type': 'Standard',
                'price': 2000,
                'current_guest': None,
                'checkin_date': None,
                'checkout_date': None
            }
        with open('data/rooms.json', 'w') as f:
            json.dump(rooms, f, indent=2)
    else:
        # Ensure all rooms exist but don't overwrite existing data
        try:
            with open('data/rooms.json', 'r') as f:
                existing_rooms = json.load(f)

            rooms_updated = False
            for i in range(101, 109):
                room_key = str(i)
                if room_key not in existing_rooms:
                    existing_rooms[room_key] = {
                        'room_number': room_key,
                        'status': 'Available',
                        'type': 'Standard',
                        'price': 2000,
                        'current_guest': None,
                        'checkin_date': None,
                        'checkout_date': None
                    }
                    rooms_updated = True

            if rooms_updated:
                with open('data/rooms.json', 'w') as f:
                    json.dump(existing_rooms, f, indent=2)
        except:
            pass

    # Initialize other data files
    data_files = [
        'sales.json',
        'expenditures.json',
        'room_services.json',
        'complementary_rooms.json',
        'advance_payments.json',
        'outstanding_dues.json',
        'uploaded_bills.json',
        'cash_handovers.json',
        'account_handovers.json',
        'bad_debts.json',
        'discounts.json',
        'complementary_records.json'
    ]

    # Initialize both main files and hotel-specific files
    for file_name in data_files:
        # Create main file
        file_path = f'data/{file_name}'
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)
        
        # Create hotel-specific files
        for hotel_id in ['hotel1', 'hotel2']:
            hotel_file_path = f'data/{hotel_id}_{file_name}'
            if not os.path.exists(hotel_file_path):
                with open(hotel_file_path, 'w') as f:
                    json.dump([], f)

def load_data(filename, hotel='hotel1'):
    """Load data from JSON file with hotel-specific support and automatic recovery"""
    # For hotel-specific files, prefix with hotel identifier
    if hotel and filename != 'users.json':
        filename = f"{hotel}_{filename}"

    filepath = os.path.join('data', filename)

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # Try multiple recovery methods if main file fails
    def try_load_from_path(path):
        try:
            with open(path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return None
                return json.loads(content)
        except:
            return None

    # Try main file first
    data = try_load_from_path(filepath)
    
    if data is not None:
        return data
    
    # Try redundant copy
    redundant_path = os.path.join('data/redundant', filename)
    if os.path.exists(redundant_path):
        data = try_load_from_path(redundant_path)
        if data is not None:
            # Restore main file from redundant copy
            try:
                import shutil
                shutil.copy2(redundant_path, filepath)
                print(f"Restored {filepath} from redundant copy")
                return data
            except:
                pass
    
    # Try latest backup
    backup_path = os.path.join('data/auto_backups', f"{filename}.backup")
    if os.path.exists(backup_path):
        data = try_load_from_path(backup_path)
        if data is not None:
            # Restore main file from backup
            try:
                import shutil
                shutil.copy2(backup_path, filepath)
                print(f"Restored {filepath} from backup")
                return data
            except:
                pass
    
    # Try timestamped backups (newest first)
    backup_dir = 'data/auto_backups'
    if os.path.exists(backup_dir):
        import glob
        backup_pattern = os.path.join(backup_dir, f"{filename}_*.backup")
        backups = sorted(glob.glob(backup_pattern), reverse=True)
        
        for backup in backups:
            data = try_load_from_path(backup)
            if data is not None:
                try:
                    import shutil
                    shutil.copy2(backup, filepath)
                    print(f"Restored {filepath} from timestamped backup {backup}")
                    return data
                except:
                    continue
    
    # If all recovery attempts fail, create default structure
    print(f"All recovery attempts failed for {filename}, creating new file")
    
    if 'rooms.json' in filename:
        default_data = create_default_rooms_for_hotel(hotel)
        save_data(filename.replace(f"{hotel}_", ""), default_data, hotel)
        return default_data
    elif filename == 'users.json':
        return {}
    else:
        save_data(filename.replace(f"{hotel}_", ""), [], hotel)
        return []

def save_data(filename, data, hotel='hotel1'):
    """Save data to JSON file with triple redundancy and enhanced persistence"""
    from utils.data_integrity import log_data_access, create_emergency_backup, verify_data_integrity, file_lock
    
    # Thread-safe file operations
    with file_lock:
        # For hotel-specific files, prefix with hotel identifier
        if hotel and filename != 'users.json':
            filename = f"{hotel}_{filename}"

        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        os.makedirs('data/auto_backups', exist_ok=True)
        os.makedirs('data/redundant', exist_ok=True)
        os.makedirs('data/emergency_backups', exist_ok=True)

        filepath = os.path.join('data', filename)
        
        # Log the save operation
        log_data_access('save', filename, hotel)
        
        # Create emergency backup before any operation
        create_emergency_backup(filename, data)
        
        # Create multiple backup layers for all data files
        if os.path.exists(filepath):
            backup_dir = 'data/auto_backups'
            
            # Create timestamped backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            timestamped_backup = os.path.join(backup_dir, f"{filename}_{timestamp}.backup")
            regular_backup = os.path.join(backup_dir, f"{filename}.backup")
            
            try:
                import shutil
                shutil.copy2(filepath, timestamped_backup)
                shutil.copy2(filepath, regular_backup)
                
                # Keep more timestamped backups for permanent storage (100 backups per file)
                import glob
                backup_pattern = os.path.join(backup_dir, f"{filename}_*.backup")
                backups = sorted(glob.glob(backup_pattern))
                while len(backups) > 100:
                    os.remove(backups.pop(0))
                    
            except Exception as e:
                print(f"Warning: Backup creation failed: {e}")
        
        # Multiple save attempts with verification
        save_successful = False
        attempts = 0
        max_attempts = 3
        
        while not save_successful and attempts < max_attempts:
            attempts += 1
            try:
                # Write to temporary file first, then rename (atomic operation)
                temp_path = filepath + f'.tmp_{attempts}'
                with open(temp_path, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Verify temp file before rename
                with open(temp_path, 'r') as f:
                    temp_data = json.load(f)
                    if temp_data != data:
                        raise Exception("Data verification failed for temp file")
                
                # Rename temp file to actual file (atomic on most systems)
                os.rename(temp_path, filepath)
                
                # Double verification that data was written correctly
                if verify_data_integrity(filename, data):
                    save_successful = True
                else:
                    raise Exception("Data integrity verification failed after save")
                
            except Exception as e:
                print(f"Save attempt {attempts} failed: {e}")
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                
                if attempts >= max_attempts:
                    # Try to restore from backup if all save attempts failed
                    backup_path = os.path.join('data/auto_backups', f"{filename}.backup")
                    if os.path.exists(backup_path):
                        try:
                            shutil.copy2(backup_path, filepath)
                            print(f"Restored {filepath} from backup due to save failure")
                        except Exception:
                            pass
                    raise Exception(f"Failed to save data after {max_attempts} attempts: {e}")
                else:
                    time.sleep(0.1)  # Brief pause before retry
        
        # Create redundant copies for ALL files (not just critical ones)
        try:
            redundant_dir = 'data/redundant'
            redundant_path = os.path.join(redundant_dir, filename)
            shutil.copy2(filepath, redundant_path)
            
            # Also create a second redundant copy
            redundant2_path = os.path.join(redundant_dir, f"{filename}.copy2")
            shutil.copy2(filepath, redundant2_path)
            
        except Exception as e:
            print(f"Warning: Redundant copy creation failed: {e}")
        
        # Final verification
        if not verify_data_integrity(filename, data):
            raise Exception("Final data integrity check failed")
            
        print(f"Data successfully saved to {filepath} with full redundancy")

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())[:8]

def get_current_date():
    """Get current date as string"""
    return datetime.now().strftime('%Y-%m-%d')

def get_current_datetime():
    """Get current datetime as string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_total_sales(hotel=None):
    """Calculate total sales from all sources"""
    import streamlit as st
    if not hotel:
        hotel = st.session_state.get('selected_hotel', 'hotel1')
    sales = load_data('sales.json', hotel)
    total = 0
    for sale in sales:
        total += sale.get('amount', 0)
    return total

def calculate_total_expenditures(hotel=None):
    """Calculate total expenditures"""
    import streamlit as st
    if not hotel:
        hotel = st.session_state.get('selected_hotel', 'hotel1')
    expenditures = load_data('expenditures.json', hotel)
    total = 0
    for exp in expenditures:
        total += exp.get('amount', 0)
    return total

def initialize_rooms_for_hotel(hotel):
    """Initialize rooms for specific hotel"""
    rooms = {}
    if hotel == 'hotel1':
        # Hotel 1: rooms 101-108 (8 rooms)
        for i in range(101, 109):
            rooms[str(i)] = {
                'room_number': str(i),
                'status': 'Available',
                'type': 'Standard',
                'price': 2000,
                'current_guest': None,
                'checkin_date': None,
                'checkout_date': None,
                'guest_phone': None
            }
    else:  # hotel2
        # Hotel 2: 17 rooms (101-103, 201-203, 301-305, 401-403, 501-503)
        room_numbers = []
        for floor in [1, 2, 3, 4, 5]:
            start = floor * 100 + 1
            end = start + (2 if floor in [1, 2, 4, 5] else 4)  # Floor 3 has 5 rooms (301-305)
            room_numbers.extend(range(start, end + 1))
        
        for room_num in room_numbers:
            rooms[str(room_num)] = {
                'room_number': str(room_num),
                'status': 'Available',
                'type': 'Standard',
                'price': 2000,
                'current_guest': None,
                'checkin_date': None,
                'checkout_date': None,
                'guest_phone': None
            }
    return rooms

def calculate_pending_dues(hotel=None):
    """Calculate pending dues"""
    import streamlit as st
    if not hotel:
        hotel = st.session_state.get('selected_hotel', 'hotel1')
    # This would be based on unpaid bookings, account sales, etc.
    # For now, we'll calculate from account sales that are unpaid
    sales = load_data('sales.json', hotel)
    outstanding_dues = load_data('outstanding_dues.json', hotel)

    pending = 0
    # Add account sales that are pending
    for sale in sales:
        if sale.get('payment_type') == 'Account' and sale.get('status') == 'Pending':
            pending += sale.get('amount', 0)

    # Add outstanding dues that are pending
    for due in outstanding_dues:
        if due.get('status') == 'Pending':
            pending += due.get('amount', 0)

    return pending

def validate_data_integrity():
    """Validate and repair data file integrity"""
    import streamlit as st
    
    # Check critical files
    critical_files = [
        'sales.json', 'rooms.json', 'expenditures.json', 
        'advance_payments.json', 'outstanding_dues.json'
    ]
    
    current_hotel = st.session_state.get('selected_hotel', 'hotel1')
    
    for filename in critical_files:
        try:
            data = load_data(filename, current_hotel)
            if data is None:
                # File was corrupted, reinitialize
                if filename == 'rooms.json':
                    save_data(filename, initialize_rooms_for_hotel(current_hotel), current_hotel)
                else:
                    save_data(filename, [], current_hotel)
        except Exception as e:
            # Handle any corruption
            if filename == 'rooms.json':
                save_data(filename, initialize_rooms_for_hotel(current_hotel), current_hotel)
            else:
                save_data(filename, [], current_hotel)