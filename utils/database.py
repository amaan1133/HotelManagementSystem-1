"""
Database utility module for PostgreSQL operations
"""
import os
import json
from datetime import datetime
from sqlalchemy import create_engine, text
import pandas as pd

class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not found")
        
        # Create engine
        self.engine = create_engine(self.database_url)
        
    def init_tables(self):
        """Initialize all database tables"""
        try:
            with self.engine.connect() as conn:
                # Users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(256) NOT NULL,
                        role VARCHAR(20) NOT NULL DEFAULT 'User',
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Rooms table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS rooms (
                        id VARCHAR(50) PRIMARY KEY,
                        room_number VARCHAR(10) NOT NULL,
                        status VARCHAR(20) DEFAULT 'Available',
                        type VARCHAR(20) DEFAULT 'Standard',
                        price DECIMAL(10,2) DEFAULT 2000,
                        current_guest VARCHAR(100),
                        guest_phone VARCHAR(20),
                        checkin_date DATE,
                        checkout_date DATE,
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Add missing columns to existing tables
                try:
                    # Room Services table alterations
                    room_service_columns = [
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS customer_name VARCHAR(100)",
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS service_category VARCHAR(50)",
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS service_item VARCHAR(100)",
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1",
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS unit_price DECIMAL(10,2) DEFAULT 0",
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS special_instructions TEXT",
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'Normal'",
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20)",
                        "ALTER TABLE room_services ADD COLUMN IF NOT EXISTS completed_date TIMESTAMP",
                        "ALTER TABLE room_services ALTER COLUMN room_number DROP NOT NULL"
                    ]
                    
                    for alter_cmd in room_service_columns:
                        try:
                            conn.execute(text(alter_cmd))
                        except:
                            pass
                    
                    # Outstanding Dues table alterations
                    outstanding_due_columns = [
                        "ALTER TABLE outstanding_dues ADD COLUMN IF NOT EXISTS due_type VARCHAR(50)",
                        "ALTER TABLE outstanding_dues ADD COLUMN IF NOT EXISTS due_date DATE",
                        "ALTER TABLE outstanding_dues ADD COLUMN IF NOT EXISTS phone VARCHAR(20)",
                        "ALTER TABLE outstanding_dues ADD COLUMN IF NOT EXISTS payment_history TEXT",
                        "ALTER TABLE outstanding_dues ADD COLUMN IF NOT EXISTS received_date TIMESTAMP",
                        "ALTER TABLE outstanding_dues ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20)",
                        "ALTER TABLE outstanding_dues ADD COLUMN IF NOT EXISTS payment_date TIMESTAMP"
                    ]
                    
                    for alter_cmd in outstanding_due_columns:
                        try:
                            conn.execute(text(alter_cmd))
                        except:
                            pass
                    
                    # Sales table alterations
                    sales_columns = [
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS transaction_date TIMESTAMP",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20)",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS due_date DATE",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS cash_received DECIMAL(10,2)",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS order_details TEXT",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS special_instructions TEXT",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS restaurant_name VARCHAR(100)",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS order_type VARCHAR(50)",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS advance_id VARCHAR(50)",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS original_advance_date DATE",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS payment_date DATE",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS original_due_id VARCHAR(50)",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS notes TEXT",
                        "ALTER TABLE sales ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'Completed'"
                    ]
                    
                    for alter_cmd in sales_columns:
                        try:
                            conn.execute(text(alter_cmd))
                        except:
                            pass
                    
                    # Discounts table alterations
                    discount_columns = [
                        "ALTER TABLE discounts ADD COLUMN IF NOT EXISTS amount DECIMAL(10,2)",
                        "ALTER TABLE discounts ADD COLUMN IF NOT EXISTS discount_type VARCHAR(50)",
                        "ALTER TABLE discounts ADD COLUMN IF NOT EXISTS reason VARCHAR(200)",
                        "ALTER TABLE discounts ADD COLUMN IF NOT EXISTS reference_id VARCHAR(50)",
                        "ALTER TABLE discounts ADD COLUMN IF NOT EXISTS percentage DECIMAL(5,2) DEFAULT 0",
                        "ALTER TABLE discounts ADD COLUMN IF NOT EXISTS original_advance_date DATE",
                        "ALTER TABLE discounts ADD COLUMN IF NOT EXISTS advance_id VARCHAR(50)",
                        "ALTER TABLE discounts ADD COLUMN IF NOT EXISTS original_due_id VARCHAR(50)"
                    ]
                    
                    for alter_cmd in discount_columns:
                        try:
                            conn.execute(text(alter_cmd))
                        except:
                            pass
                    
                    # Bad Debts table alterations
                    bad_debt_columns = [
                        "ALTER TABLE bad_debts ADD COLUMN IF NOT EXISTS reference_id VARCHAR(50)",
                        "ALTER TABLE bad_debts ADD COLUMN IF NOT EXISTS original_due_id VARCHAR(50)",
                        "ALTER TABLE bad_debts ADD COLUMN IF NOT EXISTS original_advance_date DATE",
                        "ALTER TABLE bad_debts ADD COLUMN IF NOT EXISTS advance_id VARCHAR(50)"
                    ]
                    
                    for alter_cmd in bad_debt_columns:
                        try:
                            conn.execute(text(alter_cmd))
                        except:
                            pass
                    
                    # Cash/Account Handovers table alterations
                    handover_columns = [
                        "ALTER TABLE cash_handovers ADD COLUMN IF NOT EXISTS handover_date DATE",
                        "ALTER TABLE cash_handovers ADD COLUMN IF NOT EXISTS notes TEXT",
                        "ALTER TABLE cash_handovers ADD COLUMN IF NOT EXISTS received_by VARCHAR(100)",
                        "ALTER TABLE cash_handovers ADD COLUMN IF NOT EXISTS handed_by VARCHAR(100)",
                        "ALTER TABLE cash_handovers ADD COLUMN IF NOT EXISTS handover_type VARCHAR(50)",
                        "ALTER TABLE cash_handovers ADD COLUMN IF NOT EXISTS reference_number VARCHAR(100)",
                        "ALTER TABLE account_handovers ADD COLUMN IF NOT EXISTS handover_date DATE",
                        "ALTER TABLE account_handovers ADD COLUMN IF NOT EXISTS notes TEXT",
                        "ALTER TABLE account_handovers ADD COLUMN IF NOT EXISTS received_by VARCHAR(100)",
                        "ALTER TABLE account_handovers ADD COLUMN IF NOT EXISTS handed_by VARCHAR(100)",
                        "ALTER TABLE account_handovers ADD COLUMN IF NOT EXISTS handover_type VARCHAR(50)",
                        "ALTER TABLE account_handovers ADD COLUMN IF NOT EXISTS reference_number VARCHAR(100)"
                    ]
                    
                    for alter_cmd in handover_columns:
                        try:
                            conn.execute(text(alter_cmd))
                        except:
                            pass
                    
                    # Complementary Rooms table alterations
                    comp_room_columns = [
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS guest_contact VARCHAR(20)",
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS checkin_date DATE",
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS checkout_date DATE",
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS nights INTEGER DEFAULT 1",
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS room_rate DECIMAL(10,2) DEFAULT 0",
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS comp_reason VARCHAR(200)",
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS approved_by VARCHAR(50)",
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS special_notes TEXT",
                        "ALTER TABLE complementary_rooms ADD COLUMN IF NOT EXISTS actual_checkout TIMESTAMP"
                    ]
                    
                    for alter_cmd in comp_room_columns:
                        try:
                            conn.execute(text(alter_cmd))
                        except:
                            pass
                    
                    # Add hotel column to tables that might be missing it
                    tables_needing_hotel = [
                        'cash_handovers', 'account_handovers', 'bad_debts', 
                        'discounts', 'uploaded_bills', 'complementary_rooms',
                        'room_services', 'outstanding_dues'
                    ]
                    
                    for table in tables_needing_hotel:
                        try:
                            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS hotel VARCHAR(20) DEFAULT 'hotel1'"))
                        except:
                            pass  # Column might already exist
                except:
                    pass
                
                # Sales table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sales (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        transaction_date TIMESTAMP,
                        type VARCHAR(50) NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        customer_name VARCHAR(100),
                        customer_phone VARCHAR(20),
                        description TEXT,
                        payment_type VARCHAR(20),
                        room_number VARCHAR(10),
                        due_date DATE,
                        cash_received DECIMAL(10,2),
                        order_details TEXT,
                        special_instructions TEXT,
                        restaurant_name VARCHAR(100),
                        order_type VARCHAR(50),
                        advance_id VARCHAR(50),
                        original_advance_date DATE,
                        payment_date DATE,
                        original_due_id VARCHAR(50),
                        notes TEXT,
                        status VARCHAR(20) DEFAULT 'Completed',
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Restaurant table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS restaurant (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        customer_name VARCHAR(100),
                        room_number VARCHAR(10),
                        items TEXT,
                        total_amount DECIMAL(10,2) NOT NULL,
                        payment_method VARCHAR(20),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Expenditures table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS expenditures (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        vendor_name VARCHAR(100),
                        description TEXT,
                        payment_method VARCHAR(20),
                        status VARCHAR(20),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Advance Payments table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS advance_payments (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        customer_name VARCHAR(100) NOT NULL,
                        customer_contact VARCHAR(20),
                        customer_email VARCHAR(100),
                        room_number VARCHAR(10),
                        booking_date DATE,
                        advance_amount DECIMAL(10,2) NOT NULL,
                        remaining_amount DECIMAL(10,2),
                        total_amount DECIMAL(10,2),
                        payment_method VARCHAR(20),
                        cheque_number VARCHAR(50),
                        cheque_date DATE,
                        transaction_id VARCHAR(100),
                        purpose VARCHAR(50),
                        notes TEXT,
                        status VARCHAR(20) DEFAULT 'Pending',
                        received_amount DECIMAL(10,2) DEFAULT 0,
                        full_payment_date DATE,
                        completion_date TIMESTAMP,
                        final_payment_method VARCHAR(20),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Add missing columns for advance_payments
                try:
                    conn.execute(text("ALTER TABLE advance_payments ADD COLUMN IF NOT EXISTS completion_date TIMESTAMP"))
                    conn.execute(text("ALTER TABLE advance_payments ADD COLUMN IF NOT EXISTS final_payment_method VARCHAR(20)"))
                except:
                    pass
                
                # Outstanding Dues table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS outstanding_dues (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        customer_name VARCHAR(100) NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        due_type VARCHAR(50),
                        due_date DATE,
                        description TEXT,
                        phone VARCHAR(20),
                        room_number VARCHAR(10),
                        payment_type VARCHAR(20),
                        payment_history TEXT,
                        received_date TIMESTAMP,
                        payment_method VARCHAR(20),
                        payment_date TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'Pending',
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Cash Handovers table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS cash_handovers (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        handover_date DATE,
                        amount DECIMAL(10,2) NOT NULL,
                        notes TEXT,
                        handed_by VARCHAR(100),
                        received_by VARCHAR(100),
                        handover_type VARCHAR(50),
                        reference_number VARCHAR(100),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Account Handovers table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS account_handovers (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        handover_date DATE,
                        amount DECIMAL(10,2) NOT NULL,
                        notes TEXT,
                        handed_by VARCHAR(100),
                        received_by VARCHAR(100),
                        handover_type VARCHAR(50),
                        reference_number VARCHAR(100),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Bad Debts table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS bad_debts (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        customer_name VARCHAR(100) NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        reason VARCHAR(200),
                        reference_id VARCHAR(50),
                        original_due_id VARCHAR(50),
                        original_advance_date DATE,
                        advance_id VARCHAR(50),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Discounts table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS discounts (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        customer_name VARCHAR(100),
                        amount DECIMAL(10,2) NOT NULL,
                        original_amount DECIMAL(10,2),
                        discount_type VARCHAR(50),
                        reason VARCHAR(200),
                        reference_id VARCHAR(50),
                        percentage DECIMAL(5,2) DEFAULT 0,
                        original_advance_date DATE,
                        advance_id VARCHAR(50),
                        original_due_id VARCHAR(50),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Add missing columns for discounts
                try:
                    conn.execute(text("ALTER TABLE discounts ADD COLUMN IF NOT EXISTS original_amount DECIMAL(10,2)"))
                except:
                    pass
                
                # Uploaded Bills table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS uploaded_bills (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        file_name VARCHAR(200) NOT NULL,
                        file_path VARCHAR(500),
                        amount DECIMAL(10,2),
                        description TEXT,
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        uploaded_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Complementary Rooms table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS complementary_rooms (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        room_number VARCHAR(10) NOT NULL,
                        guest_name VARCHAR(100) NOT NULL,
                        guest_contact VARCHAR(20),
                        checkin_date DATE,
                        checkout_date DATE,
                        nights INTEGER DEFAULT 1,
                        room_rate DECIMAL(10,2) DEFAULT 0,
                        room_value DECIMAL(10,2) NOT NULL,
                        comp_reason VARCHAR(200),
                        approved_by VARCHAR(50),
                        special_notes TEXT,
                        actual_checkout TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'Active',
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Room Services table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS room_services (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        room_number VARCHAR(10),
                        customer_name VARCHAR(100),
                        service_category VARCHAR(50),
                        service_item VARCHAR(100),
                        quantity INTEGER DEFAULT 1,
                        unit_price DECIMAL(10,2) DEFAULT 0,
                        amount DECIMAL(10,2) NOT NULL,
                        special_instructions TEXT,
                        priority VARCHAR(20) DEFAULT 'Normal',
                        status VARCHAR(20) DEFAULT 'Pending',
                        payment_method VARCHAR(20),
                        completed_date TIMESTAMP,
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Complementary Records table (for complementary payments/waivers)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS complementary_records (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        customer_name VARCHAR(100) NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        type VARCHAR(50),
                        reason VARCHAR(200),
                        reference_id VARCHAR(50),
                        original_advance_date DATE,
                        advance_id VARCHAR(50),
                        original_due_id VARCHAR(50),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                conn.commit()
                print("Database tables initialized successfully")
                
        except Exception as e:
            print(f"Error initializing database tables: {e}")
            raise
    
    def load_data_from_db(self, table_name, hotel='hotel1'):
        """Load data from database table with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.engine.connect() as conn:
                    query = text(f"SELECT * FROM {table_name} WHERE hotel = :hotel ORDER BY created_at DESC")
                    result = conn.execute(query, {"hotel": hotel})
                    
                    # Convert to list of dictionaries
                    columns = result.keys()
                    data = []
                    for row in result:
                        row_dict = dict(zip(columns, row))
                        # Convert datetime objects to strings for compatibility
                        for key, value in row_dict.items():
                            if hasattr(value, 'isoformat'):
                                row_dict[key] = value.isoformat()
                            elif hasattr(value, '__float__'):  # Handle Decimal types
                                row_dict[key] = float(value)
                            elif value is None:
                                row_dict[key] = None
                            else:
                                row_dict[key] = str(value) if not isinstance(value, (int, float, bool)) else value
                        data.append(row_dict)
                    
                    return data
                    
            except Exception as e:
                print(f"Error loading data from {table_name} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    # Recreate engine for next attempt
                    try:
                        self.engine = create_engine(self.database_url)
                    except:
                        pass
                else:
                    return []
    
    def save_data_to_db(self, table_name, data, hotel='hotel1'):
        """Save data to database table"""
        try:
            with self.engine.connect() as conn:
                # Clear existing data for this hotel
                conn.execute(text(f"DELETE FROM {table_name} WHERE hotel = :hotel"), {"hotel": hotel})
                
                # Insert new data
                if data:
                    for item in data:
                        # Prepare data for insertion
                        item_copy = item.copy()
                        item_copy['hotel'] = hotel
                        
                        # Build column list and values
                        columns = list(item_copy.keys())
                        placeholders = [f":{col}" for col in columns]
                        
                        query = text(f"""
                            INSERT INTO {table_name} ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                            ON CONFLICT (id) DO UPDATE SET
                            {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])}
                        """)
                        
                        conn.execute(query, item_copy)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving data to {table_name}: {e}")
            return False
    
    def add_record_to_db(self, table_name, record):
        """Add a single record to database with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.engine.connect() as conn:
                    # Build column list and values
                    columns = list(record.keys())
                    placeholders = [f":{col}" for col in columns]
                    
                    query = text(f"""
                        INSERT INTO {table_name} ({', '.join(columns)})
                        VALUES ({', '.join(placeholders)})
                        ON CONFLICT (id) DO UPDATE SET
                        {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])}
                    """)
                    
                    conn.execute(query, record)
                    conn.commit()
                    return True
                    
            except Exception as e:
                print(f"Error adding record to {table_name} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    try:
                        self.engine = create_engine(self.database_url)
                    except:
                        pass
                else:
                    return False
    
    def migrate_json_to_db(self):
        """Migration disabled to prevent data mixing between hotels"""
        print("Migration disabled to prevent data mixing between Saz Valley Bhaderwah and Saz Valley Kishtwar")
        return True
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False