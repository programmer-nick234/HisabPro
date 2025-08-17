#!/usr/bin/env python
"""
Debug User Invoices
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from lib.mongodb import mongodb_service
from invoices.mongodb_models import MongoDBInvoice
from django.contrib.auth.models import User

def debug_user_invoices():
    """Debug user invoices"""
    print("🔍 Debug User Invoices")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        mongodb_service.connect()
        if not mongodb_service._connected:
            print("❌ MongoDB connection failed")
            return
        
        print("✅ MongoDB connected")
        
        # Check all invoices in database
        all_invoices = list(mongodb_service.db.invoices.find())
        print(f"📊 Total invoices in database: {len(all_invoices)}")
        
        if all_invoices:
            print("\n📋 Sample invoices:")
            for i, invoice in enumerate(all_invoices[:3]):
                print(f"   Invoice {i+1}:")
                print(f"     ID: {invoice.get('_id')}")
                print(f"     User ID: {invoice.get('user_id')}")
                print(f"     Invoice Number: {invoice.get('invoice_number')}")
                print(f"     Client: {invoice.get('client_name')}")
                print(f"     Status: {invoice.get('status')}")
                print(f"     Amount: {invoice.get('total_amount')}")
                print()
        
        # Check all users
        users = User.objects.all()
        print(f"👥 Total users: {users.count()}")
        
        for user in users:
            print(f"   User: {user.username} (ID: {user.id})")
            
            # Check invoices for this user
            user_invoices = list(mongodb_service.db.invoices.find({'user_id': user.id}))
            print(f"     Invoices: {len(user_invoices)}")
            
            if user_invoices:
                for invoice in user_invoices[:2]:
                    print(f"       - {invoice.get('invoice_number')}: {invoice.get('client_name')}")
        
        # Test admin user specifically
        try:
            admin_user = User.objects.get(username='admin')
            print(f"\n🔍 Testing admin user (ID: {admin_user.id}):")
            
            # Test get_by_user
            admin_invoices = MongoDBInvoice.get_by_user(admin_user.id, limit=5)
            print(f"   get_by_user result: {len(admin_invoices)} invoices")
            
            # Test get_summary
            admin_summary = MongoDBInvoice.get_summary(admin_user.id)
            print(f"   get_summary result: {admin_summary}")
            
        except User.DoesNotExist:
            print("❌ Admin user not found")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    debug_user_invoices()
