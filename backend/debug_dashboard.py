#!/usr/bin/env python
"""
Debug Dashboard Data Issues
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from lib.mongodb import mongodb_service
from invoices.mongodb_models import MongoDBInvoice, MongoDBInvoiceItem
from django.contrib.auth.models import User

def debug_dashboard_data():
    """Debug dashboard data issues"""
    print("🔍 Debugging Dashboard Data")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        mongodb_service.connect()
        if not mongodb_service._connected:
            print("❌ MongoDB connection failed")
            return
        
        print("✅ MongoDB connected")
        
        # Check if admin user exists
        try:
            admin_user = User.objects.get(username='admin')
            print(f"✅ Admin user found: {admin_user.id}")
        except User.DoesNotExist:
            print("❌ Admin user not found")
            return
        
        # Check all invoices in database
        all_invoices = list(mongodb_service.db.invoices.find({}))
        print(f"📊 Total invoices in database: {len(all_invoices)}")
        
        if all_invoices:
            print("📋 Sample invoice data:")
            for i, invoice in enumerate(all_invoices[:3]):
                print(f"   Invoice {i+1}:")
                print(f"     _id: {invoice.get('_id')}")
                print(f"     user_id: {invoice.get('user_id')}")
                print(f"     invoice_number: {invoice.get('invoice_number')}")
                print(f"     client_name: {invoice.get('client_name')}")
                print(f"     status: {invoice.get('status')}")
                print(f"     total_amount: {invoice.get('total_amount')}")
                print()
        
        # Check invoices for admin user
        admin_invoices = list(mongodb_service.db.invoices.find({'user_id': admin_user.id}))
        print(f"👤 Invoices for admin user ({admin_user.id}): {len(admin_invoices)}")
        
        if admin_invoices:
            print("📋 Admin user invoices:")
            for invoice in admin_invoices:
                print(f"   - {invoice.get('invoice_number')}: {invoice.get('client_name')} - {invoice.get('status')}")
        else:
            print("⚠️ No invoices found for admin user")
            
            # Check if there are invoices with different user_id format
            all_user_ids = set()
            for invoice in all_invoices:
                user_id = invoice.get('user_id')
                if user_id is not None:
                    all_user_ids.add(user_id)
            
            print(f"🔍 Found user_ids in database: {all_user_ids}")
            
            if all_user_ids:
                print("📋 Checking invoices with different user_ids:")
                for user_id in all_user_ids:
                    user_invoices = list(mongodb_service.db.invoices.find({'user_id': user_id}))
                    print(f"   User {user_id}: {len(user_invoices)} invoices")
        
        # Test get_summary method
        print("\n🧮 Testing get_summary method:")
        summary = MongoDBInvoice.get_summary(admin_user.id)
        print(f"Summary result: {summary}")
        
        # Test get_by_user method
        print("\n📋 Testing get_by_user method:")
        recent_invoices = MongoDBInvoice.get_by_user(admin_user.id, limit=5)
        print(f"Recent invoices: {len(recent_invoices)}")
        for invoice in recent_invoices:
            print(f"   - {invoice.invoice_number}: {invoice.client_name}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def fix_user_id_issue():
    """Fix user_id issue if needed"""
    print("\n🔧 Fixing User ID Issue")
    print("=" * 50)
    
    try:
        admin_user = User.objects.get(username='admin')
        print(f"Admin user ID: {admin_user.id}")
        
        # Check if there are invoices with wrong user_id
        all_invoices = list(mongodb_service.db.invoices.find({}))
        
        for invoice in all_invoices:
            current_user_id = invoice.get('user_id')
            if current_user_id != admin_user.id:
                print(f"Fixing invoice {invoice.get('invoice_number')}: {current_user_id} -> {admin_user.id}")
                mongodb_service.db.invoices.update_one(
                    {'_id': invoice['_id']},
                    {'$set': {'user_id': admin_user.id}}
                )
        
        print("✅ User ID fix completed")
        
    except Exception as e:
        print(f"❌ Error fixing user_id: {str(e)}")

def main():
    """Main debug function"""
    print("🔍 Dashboard Data Debug")
    print("=" * 60)
    
    debug_dashboard_data()
    
    # Ask if user wants to fix the issue
    print("\n" + "=" * 60)
    print("💡 If you see user_id mismatches, run fix_user_id_issue()")
    print("💡 If no invoices exist, create some test invoices first")

if __name__ == '__main__':
    main()
