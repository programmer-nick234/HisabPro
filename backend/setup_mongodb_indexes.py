#!/usr/bin/env python
"""
Setup MongoDB indexes for optimal performance
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
import logging

logger = logging.getLogger(__name__)

def setup_mongodb_indexes():
    """Setup MongoDB indexes for optimal performance"""
    try:
        print("Setting up MongoDB indexes...")
        
        # Ensure connection
        mongodb_service.connect()
        
        if not mongodb_service._connected:
            print("❌ Failed to connect to MongoDB")
            return False
        
        # Create indexes for invoices collection
        print("Creating indexes for invoices collection...")
        
        # User ID index for fast user-specific queries
        mongodb_service.db.invoices.create_index("user_id")
        print("✅ Created index on user_id")
        
        # Invoice number index for unique lookups
        mongodb_service.db.invoices.create_index("invoice_number", unique=True)
        print("✅ Created unique index on invoice_number")
        
        # Status index for filtering by status
        mongodb_service.db.invoices.create_index("status")
        print("✅ Created index on status")
        
        # Created at index for sorting by date
        mongodb_service.db.invoices.create_index("created_at")
        print("✅ Created index on created_at")
        
        # Compound index for user + status queries
        mongodb_service.db.invoices.create_index([("user_id", 1), ("status", 1)])
        print("✅ Created compound index on user_id + status")
        
        # Compound index for user + created_at queries
        mongodb_service.db.invoices.create_index([("user_id", 1), ("created_at", -1)])
        print("✅ Created compound index on user_id + created_at")
        
        # Create indexes for invoice_items collection
        print("Creating indexes for invoice_items collection...")
        
        # Invoice ID index for fast item lookups
        mongodb_service.db.invoice_items.create_index("invoice_id")
        print("✅ Created index on invoice_id")
        
        # Create indexes for payments collection (if exists)
        print("Creating indexes for payments collection...")
        
        # Invoice ID index for payment lookups
        mongodb_service.db.payments.create_index("invoice_id")
        print("✅ Created index on invoice_id for payments")
        
        # Transaction ID index for unique payment tracking
        mongodb_service.db.payments.create_index("transaction_id", unique=True)
        print("✅ Created unique index on transaction_id")
        
        print("\n🎉 MongoDB indexes setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up MongoDB indexes: {str(e)}")
        logger.error(f"Error setting up MongoDB indexes: {str(e)}")
        return False

if __name__ == '__main__':
    setup_mongodb_indexes()
