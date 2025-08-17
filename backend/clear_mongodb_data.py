#!/usr/bin/env python
"""
Clear MongoDB data for fresh start
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from lib.mongodb import mongodb_service

def clear_mongodb_data():
    """Clear all MongoDB collections"""
    try:
        print("Clearing MongoDB data...")
        
        # Ensure connection
        mongodb_service.connect()
        
        if not mongodb_service._connected:
            print("❌ Failed to connect to MongoDB")
            return False
        
        # Clear collections
        mongodb_service.db.invoices.delete_many({})
        mongodb_service.db.invoice_items.delete_many({})
        mongodb_service.db.payments.delete_many({})
        
        print("✅ MongoDB data cleared successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error clearing data: {str(e)}")
        return False

if __name__ == '__main__':
    clear_mongodb_data()
