#!/usr/bin/env python
"""
Test MongoDB invoice creation
"""

import os
import sys
import django
from datetime import date, timedelta, datetime
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from invoices.mongodb_models import MongoDBInvoice, MongoDBInvoiceItem
from django.contrib.auth.models import User
from lib.mongodb import mongodb_service

def test_mongodb_invoice_creation():
    """Test creating an invoice with MongoDB"""
    try:
        print("Testing MongoDB Invoice Creation...")
        print("=" * 50)
        
        # Ensure MongoDB connection
        mongodb_service.connect()
        if not mongodb_service._connected:
            print("❌ MongoDB connection failed")
            return False
        
        # Get admin user
        admin_user = User.objects.get(username='admin')
        print(f"✅ Found admin user: {admin_user.username}")
        
        # Create a test invoice
        invoice = MongoDBInvoice()
        invoice.user_id = admin_user.id
        invoice.invoice_number = f'TEST-MONGO-{int(datetime.now().timestamp())}'
        invoice.client_name = 'MongoDB Test Client'
        invoice.client_email = 'test@mongodb.com'
        invoice.issue_date = date.today()
        invoice.due_date = date.today() + timedelta(days=30)
        invoice.status = 'pending'
        invoice.tax_rate = 18.0
        
        # Save invoice first to get ID
        invoice.save()
        print(f"✅ Created invoice: {invoice.invoice_number}")
        
        # Create invoice items
        item1 = MongoDBInvoiceItem()
        item1.invoice_id = str(invoice._id)
        item1.description = 'MongoDB Service 1'
        item1.quantity = 1
        item1.unit_price = 50.0
        item1.total = 50.0
        item1.save()
        print(f"✅ Created item 1: {item1.description}")
        
        item2 = MongoDBInvoiceItem()
        item2.invoice_id = str(invoice._id)
        item2.description = 'MongoDB Service 2'
        item2.quantity = 1
        item2.unit_price = 50.0
        item2.total = 50.0
        item2.save()
        print(f"✅ Created item 2: {item2.description}")
        
        # Calculate totals
        invoice.calculate_totals()
        invoice.save()
        
        # Verify invoice
        print(f"\n📋 Invoice Details:")
        print(f"   Invoice Number: {invoice.invoice_number}")
        print(f"   Client: {invoice.client_name}")
        print(f"   Total Amount: ${invoice.total_amount}")
        print(f"   Status: {invoice.status}")
        print(f"   Items: {len(invoice.get_items())}")
        
        # Test retrieval
        retrieved_invoice = MongoDBInvoice.get_by_id(str(invoice._id))
        if retrieved_invoice:
            print(f"✅ Invoice retrieved successfully: {retrieved_invoice.invoice_number}")
        
        # Clean up - delete test invoice
        success = MongoDBInvoice.delete_by_id(str(invoice._id))
        if success:
            print(f"\n🧹 Cleaned up test invoice")
        
        print("\n🎉 MongoDB invoice creation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_mongodb_invoice_creation()
