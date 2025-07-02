"""
Database-only data manager - replaces JSON file operations with PostgreSQL
"""
import uuid
from datetime import datetime
from utils.database import DatabaseManager

# Create global database manager instance
db_manager = None

def get_db_manager():
    """Get or create database manager instance"""
    global db_manager
    if db_manager is None:
        try:
            db_manager = DatabaseManager()
            db_manager.init_tables()
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return None
    return db_manager

def load_data(filename, hotel='hotel1'):
    """Load data from database table"""
    db = get_db_manager()
    if not db:
        return []

    # Map filename to table name
    table_mapping = {
        'sales.json': 'sales',
        'restaurant.json': 'restaurant',
        'expenditures.json': 'expenditures',
        'advance_payments.json': 'advance_payments',
        'outstanding_dues.json': 'outstanding_dues',
        'rooms.json': 'rooms',
        'users.json': 'users',
        'cash_handovers.json': 'cash_handovers',
        'account_handovers.json': 'account_handovers',
        'bad_debts.json': 'bad_debts',
        'discounts.json': 'discounts',
        'uploaded_bills.json': 'uploaded_bills',
        'complementary_rooms.json': 'complementary_rooms',
        'room_services.json': 'room_services',
        'complementary_records.json': 'complementary_rooms'
    }

    # Remove hotel prefix if present
    clean_filename = filename.replace(f'{hotel}_', '')
    table_name = table_mapping.get(clean_filename, clean_filename.replace('.json', ''))

    try:
        return db.load_data_from_db(table_name, hotel)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

def save_data(filename, data, hotel='hotel1'):
    """Save data to database table"""
    db = get_db_manager()
    if not db:
        return False

    # Map filename to table name
    table_mapping = {
        'sales.json': 'sales',
        'restaurant.json': 'restaurant',
        'expenditures.json': 'expenditures',
        'advance_payments.json': 'advance_payments',
        'outstanding_dues.json': 'outstanding_dues',
        'rooms.json': 'rooms',
        'users.json': 'users',
        'cash_handovers.json': 'cash_handovers',
        'account_handovers.json': 'account_handovers',
        'bad_debts.json': 'bad_debts',
        'discounts.json': 'discounts',
        'uploaded_bills.json': 'uploaded_bills',
        'complementary_rooms.json': 'complementary_rooms',
        'room_services.json': 'room_services',
        'complementary_records.json': 'complementary_rooms'
    }

    # Remove hotel prefix if present
    clean_filename = filename.replace(f'{hotel}_', '')
    table_name = table_mapping.get(clean_filename, clean_filename.replace('.json', ''))

    try:
        return db.save_data_to_db(table_name, data, hotel)
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def add_record(filename, record, hotel='hotel1'):
    """Add a single record to database"""
    db = get_db_manager()
    if not db:
        return False

    # Map filename to table name
    table_mapping = {
        'sales.json': 'sales',
        'restaurant.json': 'restaurant',
        'expenditures.json': 'expenditures',
        'advance_payments.json': 'advance_payments',
        'outstanding_dues.json': 'outstanding_dues',
        'rooms.json': 'rooms',
        'users.json': 'users',
        'cash_handovers.json': 'cash_handovers',
        'account_handovers.json': 'account_handovers',
        'bad_debts.json': 'bad_debts',
        'discounts.json': 'discounts',
        'uploaded_bills.json': 'uploaded_bills',
        'complementary_rooms.json': 'complementary_rooms',
        'room_services.json': 'room_services',
        'complementary_records.json': 'complementary_rooms'
    }

    # Remove hotel prefix if present
    clean_filename = filename.replace(f'{hotel}_', '')
    table_name = table_mapping.get(clean_filename, clean_filename.replace('.json', ''))

    # Add hotel to record
    record['hotel'] = hotel

    try:
        return db.add_record_to_db(table_name, record)
    except Exception as e:
        print(f"Error adding record to {filename}: {e}")
        return False

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())[:8]

def get_current_date():
    """Get current date as string"""
    return datetime.now().strftime('%Y-%m-%d')

def get_current_datetime():
    """Get current datetime as string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def migrate_all_json_to_database():
    """Migrate all existing JSON data to PostgreSQL"""
    db = get_db_manager()
    if db:
        db.migrate_json_to_db()
        print("All JSON data migrated to PostgreSQL")
    else:
        print("Database not available for migration")

def calculate_total_sales(hotel=None):
    """Calculate total sales from database"""
    db = get_db_manager()
    if not db:
        return 0

    hotels = [hotel] if hotel else ['hotel1', 'hotel2']
    total = 0

    for h in hotels:
        sales = load_data('sales.json', h)
        restaurant = load_data('restaurant.json', h)

        for sale in sales:
            total += float(sale.get('amount', 0))

        for order in restaurant:
            total += float(order.get('total_amount', 0))

    return total

def calculate_total_expenditures(hotel=None):
    """Calculate total expenditures from database"""
    db = get_db_manager()
    if not db:
        return 0

    hotels = [hotel] if hotel else ['hotel1', 'hotel2']
    total = 0

    for h in hotels:
        expenditures = load_data('expenditures.json', h)

        for expense in expenditures:
            total += float(expense.get('amount', 0))

    return total

def calculate_pending_dues(hotel=None):
    """Calculate pending dues from database"""
    db = get_db_manager()
    if not db:
        return 0

    hotels = [hotel] if hotel else ['hotel1', 'hotel2']
    total = 0

    for h in hotels:
        dues = load_data('outstanding_dues.json', h)

        for due in dues:
            if due.get('status') == 'Pending':
                total += float(due.get('amount', 0))

    return total

# Initialize database and migrate existing data
def initialize_database_system():
    """Initialize the database system and migrate existing data"""
    print("Initializing database system...")
    db = get_db_manager()
    if db:
        print("Database connected successfully")
        migrate_all_json_to_database()
        print("Database system ready")
    else:
        print("Failed to initialize database system")