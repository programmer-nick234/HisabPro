#!/usr/bin/env python
"""
Comprehensive MongoDB Invoice System Setup
"""

import os
import sys
import django
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from lib.mongodb import mongodb_service
from invoices.mongodb_models import MongoDBInvoice, MongoDBInvoiceItem
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")
    
    try:
        mongodb_service.connect()
        
        if mongodb_service._connected:
            print("✅ MongoDB connection successful!")
            return True
        else:
            print("❌ MongoDB connection failed")
            return False
            
    except Exception as e:
        print(f"❌ MongoDB connection error: {str(e)}")
        return False

def setup_mongodb_indexes():
    """Setup MongoDB indexes"""
    print("\nSetting up MongoDB indexes...")
    
    try:
        # Create indexes for invoices collection
        mongodb_service.db.invoices.create_index("user_id")
        mongodb_service.db.invoices.create_index("invoice_number", unique=True)
        mongodb_service.db.invoices.create_index("status")
        mongodb_service.db.invoices.create_index("created_at")
        mongodb_service.db.invoices.create_index([("user_id", 1), ("status", 1)])
        mongodb_service.db.invoices.create_index([("user_id", 1), ("created_at", -1)])
        
        # Create indexes for invoice_items collection
        mongodb_service.db.invoice_items.create_index("invoice_id")
        
        print("✅ MongoDB indexes created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating indexes: {str(e)}")
        return False

def create_sample_data():
    """Create sample invoice data"""
    print("\nCreating sample invoice data...")
    
    try:
        # Get admin user
        admin_user = User.objects.get(username='admin')
        
        # Create sample invoices
        sample_invoices = [
            {
                'client_name': 'Acme Corporation',
                'client_email': 'billing@acme.com',
                'client_phone': '+1-555-0123',
                'client_address': '123 Business St, New York, NY 10001',
                'issue_date': date.today(),
                'due_date': date.today() + timedelta(days=30),
                'status': 'pending',
                'tax_rate': 18.0,
                'notes': 'Web development services',
                'terms_conditions': 'Payment due within 30 days',
                'items': [
                    {'description': 'Frontend Development', 'quantity': 40, 'unit_price': 75.0},
                    {'description': 'Backend API Development', 'quantity': 60, 'unit_price': 85.0},
                    {'description': 'Database Design', 'quantity': 20, 'unit_price': 100.0}
                ]
            },
            {
                'client_name': 'TechStart Inc',
                'client_email': 'accounts@techstart.com',
                'client_phone': '+1-555-0456',
                'client_address': '456 Innovation Ave, San Francisco, CA 94102',
                'issue_date': date.today() - timedelta(days=15),
                'due_date': date.today() + timedelta(days=15),
                'status': 'paid',
                'tax_rate': 18.0,
                'notes': 'Mobile app development',
                'terms_conditions': 'Payment due within 30 days',
                'items': [
                    {'description': 'iOS App Development', 'quantity': 80, 'unit_price': 90.0},
                    {'description': 'Android App Development', 'quantity': 80, 'unit_price': 85.0},
                    {'description': 'UI/UX Design', 'quantity': 30, 'unit_price': 70.0}
                ]
            },
            {
                'client_name': 'Global Solutions Ltd',
                'client_email': 'finance@globalsolutions.com',
                'client_phone': '+1-555-0789',
                'client_address': '789 Enterprise Blvd, Chicago, IL 60601',
                'issue_date': date.today() - timedelta(days=5),
                'due_date': date.today() + timedelta(days=25),
                'status': 'pending',
                'tax_rate': 18.0,
                'notes': 'E-commerce platform development',
                'terms_conditions': 'Payment due within 30 days',
                'items': [
                    {'description': 'E-commerce Platform', 'quantity': 120, 'unit_price': 95.0},
                    {'description': 'Payment Integration', 'quantity': 40, 'unit_price': 110.0},
                    {'description': 'Security Implementation', 'quantity': 30, 'unit_price': 120.0}
                ]
            }
        ]
        
        created_invoices = []
        
        for i, invoice_data in enumerate(sample_invoices):
            # Generate invoice number
            invoice_number = f"INV-{admin_user.id:04d}-{i+1:04d}"
            
            # Create invoice
            invoice = MongoDBInvoice()
            invoice.user_id = admin_user.id
            invoice.invoice_number = invoice_number
            invoice.client_name = invoice_data['client_name']
            invoice.client_email = invoice_data['client_email']
            invoice.client_phone = invoice_data['client_phone']
            invoice.client_address = invoice_data['client_address']
            invoice.issue_date = invoice_data['issue_date']
            invoice.due_date = invoice_data['due_date']
            invoice.status = invoice_data['status']
            invoice.tax_rate = invoice_data['tax_rate']
            invoice.notes = invoice_data['notes']
            invoice.terms_conditions = invoice_data['terms_conditions']
            
            # Save invoice
            invoice.save()
            
            # Add items
            for item_data in invoice_data['items']:
                item = MongoDBInvoiceItem()
                item.invoice_id = str(invoice._id)
                item.description = item_data['description']
                item.quantity = item_data['quantity']
                item.unit_price = item_data['unit_price']
                item.total = item.quantity * item.unit_price
                item.save()
            
            # Calculate totals
            invoice.calculate_totals()
            invoice.save()
            
            created_invoices.append(invoice)
            print(f"✅ Created invoice: {invoice.invoice_number} - {invoice.client_name}")
        
        print(f"\n🎉 Created {len(created_invoices)} sample invoices!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000/api"
        
        # Test endpoints
        endpoints = [
            "/mongodb/invoices/summary/",
            "/mongodb/invoices/recent/",
            "/mongodb/invoices/",
        ]
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            print(f"Testing: {url}")
            
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 401:
                    print(f"✅ {endpoint} - Authentication required (expected)")
                else:
                    print(f"⚠️  {endpoint} - Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"❌ {endpoint} - Server not running")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 MongoDB Invoice System Setup")
    print("=" * 50)
    
    # Test MongoDB connection
    if not test_mongodb_connection():
        print("\n❌ Cannot proceed without MongoDB connection")
        print("Please ensure MongoDB is running and accessible")
        return False
    
    # Setup indexes
    if not setup_mongodb_indexes():
        print("\n❌ Failed to setup indexes")
        return False
    
    # Create sample data
    if not create_sample_data():
        print("\n❌ Failed to create sample data")
        return False
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n🎉 MongoDB Invoice System setup completed!")
    print("\n📋 Next steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Start the frontend: cd ../frontend && npm run dev")
    print("3. Login with admin/admin123")
    print("4. Test invoice creation and deletion")
    
    return True

if __name__ == '__main__':
    main()
