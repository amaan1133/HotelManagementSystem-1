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
                        type VARCHAR(50) NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        customer_name VARCHAR(100),
                        description TEXT,
                        payment_type VARCHAR(20),
                        room_number VARCHAR(10),
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
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Outstanding Dues table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS outstanding_dues (
                        id VARCHAR(50) PRIMARY KEY,
                        date TIMESTAMP NOT NULL,
                        customer_name VARCHAR(100) NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        description TEXT,
                        room_number VARCHAR(10),
                        payment_type VARCHAR(20),
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
                        amount DECIMAL(10,2) NOT NULL,
                        description TEXT,
                        handed_by VARCHAR(100),
                        received_by VARCHAR(100),
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
                        amount DECIMAL(10,2) NOT NULL,
                        description TEXT,
                        handed_by VARCHAR(100),
                        received_by VARCHAR(100),
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
                        description TEXT,
                        reason VARCHAR(200),
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
                        original_amount DECIMAL(10,2) NOT NULL,
                        discount_amount DECIMAL(10,2) NOT NULL,
                        final_amount DECIMAL(10,2) NOT NULL,
                        discount_reason VARCHAR(200),
                        hotel VARCHAR(20) DEFAULT 'hotel1',
                        created_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
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
                        reason VARCHAR(200),
                        room_value DECIMAL(10,2) NOT NULL,
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
                        room_number VARCHAR(10) NOT NULL,
                        service_type VARCHAR(50) NOT NULL,
                        description TEXT,
                        amount DECIMAL(10,2) NOT NULL,
                        status VARCHAR(20) DEFAULT 'Pending',
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
        """Load data from database table"""
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
                        elif value is None:
                            row_dict[key] = None
                    data.append(row_dict)
                
                return data
                
        except Exception as e:
            print(f"Error loading data from {table_name}: {e}")
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
        """Add a single record to database"""
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
            print(f"Error adding record to {table_name}: {e}")
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