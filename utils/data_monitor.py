
import streamlit as st
import json
import os
import threading
import time
from datetime import datetime
from utils.database_data_manager import load_data, save_data

class DataMonitor:
    def __init__(self):
        self.monitoring = False
        self.thread = None
        
    def start_monitoring(self):
        """Start monitoring data integrity"""
        if not self.monitoring:
            self.monitoring = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self._check_data_integrity()
                time.sleep(60)  # Check every 1 minute for better protection
            except Exception as e:
                print(f"Data monitor error: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def _check_data_integrity(self):
        """Check and repair data integrity"""
        critical_files = [
            'sales.json', 'rooms.json', 'expenditures.json',
            'advance_payments.json', 'outstanding_dues.json'
        ]
        
        for hotel in ['hotel1', 'hotel2']:
            for filename in critical_files:
                try:
                    data = load_data(filename, hotel)
                    if data is None:
                        print(f"Data integrity issue detected for {hotel}_{filename}")
                        # The load_data function will automatically attempt recovery
                except Exception as e:
                    print(f"Critical data error for {hotel}_{filename}: {e}")

# Global monitor instance
data_monitor = DataMonitor()

def start_data_monitoring():
    """Start the data monitoring service"""
    data_monitor.start_monitoring()

def stop_data_monitoring():
    """Stop the data monitoring service"""
    data_monitor.stop_monitoring()
