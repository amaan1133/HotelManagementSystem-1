"""
Data Integration utility for handling historical data flow between sections
"""
import json
from datetime import datetime, date
from utils.database_data_manager import load_data, save_data, generate_id, add_record

class DataIntegration:
    def __init__(self):
        # Always use database now - no fallback to JSON
        pass
    
    def add_historical_sale(self, sale_data, hotel='hotel1'):
        """Add historical sale and integrate with appropriate sections"""
        try:
            # Add the sale record
            add_record('sales.json', sale_data, hotel)
            
            # If it's an advance payment completion, also update advance payments
            if sale_data.get('payment_type') == 'Cash' and sale_data.get('source') == 'advance_payment':
                advance_payments = load_data('advance_payments.json', hotel)
                for advance in advance_payments:
                    if advance.get('id') == sale_data.get('source_id'):
                        advance['status'] = 'Completed'
                        advance['completion_date'] = sale_data.get('date')
                        break
                save_data('advance_payments.json', advance_payments, hotel)
            
            return True
            
        except Exception as e:
            print(f"Error adding historical sale: {e}")
            return False
    
    def add_historical_advance_payment(self, advance_data, hotel='hotel1'):
        """Add historical advance payment and integrate properly"""
        try:
            # Add to advance payments
            add_record('advance_payments.json', advance_data, hotel)
            return True
            
        except Exception as e:
            print(f"Error adding historical advance payment: {e}")
            return False
    
    def add_historical_outstanding_due(self, due_data, hotel='hotel1'):
        """Add historical outstanding due and integrate properly"""
        try:
            # Add to outstanding dues
            add_record('outstanding_dues.json', due_data, hotel)
            return True
            
        except Exception as e:
            print(f"Error adding historical outstanding due: {e}")
            return False
    
    def add_historical_restaurant(self, restaurant_data, hotel='hotel1'):
        """Add historical restaurant sale"""
        try:
            # Add to restaurant records
            add_record('restaurant.json', restaurant_data, hotel)
            return True
            
        except Exception as e:
            print(f"Error adding historical restaurant sale: {e}")
            return False
    
    def add_historical_expenditure(self, expenditure_data, hotel='hotel1'):
        """Add historical expenditure"""
        try:
            # Add to expenditures
            add_record('expenditures.json', expenditure_data, hotel)
            return True
            
        except Exception as e:
            print(f"Error adding historical expenditure: {e}")
            return False
    
    def add_historical_room_service(self, service_data, hotel='hotel1'):
        """Add historical room service"""
        try:
            # Add to room services
            add_record('room_services.json', service_data, hotel)
            return True
            
        except Exception as e:
            print(f"Error adding historical room service: {e}")
            return False
    
    def add_historical_complementary_room(self, comp_data, hotel='hotel1'):
        """Add historical complementary room"""
        try:
            # Add to complementary rooms
            add_record('complementary_rooms.json', comp_data, hotel)
            return True
            
        except Exception as e:
            print(f"Error adding historical complementary room: {e}")
            return False
    
    def get_data_for_dashboard(self, table_name, hotel='hotel1', start_date=None, end_date=None):
        """Get data for dashboard with date filtering"""
        try:
            data = load_data(table_name, hotel)
            
            if start_date and end_date:
                filtered_data = []
                for record in data:
                    record_date = record.get('date', '')[:10]
                    if start_date <= record_date <= end_date:
                        filtered_data.append(record)
                return filtered_data
            
            return data
            
        except Exception as e:
            print(f"Error getting data for dashboard: {e}")
            return []

# Create global instance
data_integration = DataIntegration()