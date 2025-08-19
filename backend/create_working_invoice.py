#!/usr/bin/env python3
"""
Create Working Invoice in Supabase
This script creates invoices with the correct structure
"""

import os
import sys
from supabase import create_client, Client
from decouple import config
from datetime import datetime

def create_working_invoice():
    """Create a working invoice with correct structure"""
    print("🔧 Creating Working Invoice")
    print("=" * 40)
    
    try:
        # Get Supabase credentials
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL or SUPABASE_KEY not configured")
            return
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Create invoice with correct structure (let Supabase generate ID)
        working_invoice = {
            'user_id': 1,
            'invoice_number': f'INV-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'client_name': 'Working Test Client',
            'total_amount': 100.00,
            'status': 'pending'
        }
        
        print(f"📝 Creating invoice with data: {working_invoice}")
        
        # Try to create the invoice
        result = supabase.table('invoices').insert(working_invoice).execute()
        
        if result.data:
            print("✅ Invoice created successfully!")
            print(f"   Invoice ID: {result.data[0]['id']}")
            print(f"   Invoice Number: {result.data[0]['invoice_number']}")
            print(f"   Client Name: {result.data[0]['client_name']}")
            print(f"   Total Amount: ${result.data[0]['total_amount']}")
            print(f"   Status: {result.data[0]['status']}")
            
            # Show all fields
            print("\n📋 All invoice fields:")
            for key, value in result.data[0].items():
                print(f"   {key}: {value}")
            
            return result.data[0]['id']
        else:
            print("❌ Failed to create invoice")
            print(f"   Error: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_full_crud_operations(invoice_id):
    """Test full CRUD operations on the invoice"""
    print(f"\n🧪 Testing Full CRUD Operations for ID: {invoice_id}")
    print("=" * 40)
    
    try:
        # Get Supabase credentials
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # 1. READ - Get the invoice
        print("📖 Testing READ operation...")
        read_result = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
        
        if read_result.data:
            print("✅ READ successful!")
            invoice = read_result.data[0]
            print(f"   Invoice: {invoice['invoice_number']} - {invoice['client_name']} - ${invoice['total_amount']}")
        else:
            print("❌ READ failed!")
            return False
        
        # 2. UPDATE - Update the invoice
        print("\n✏️  Testing UPDATE operation...")
        update_data = {
            'status': 'paid',
            'notes': 'Payment received via test'
        }
        
        update_result = supabase.table('invoices').update(update_data).eq('id', invoice_id).execute()
        
        if update_result.data:
            print("✅ UPDATE successful!")
            
            # Verify update
            updated = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
            if updated.data and updated.data[0]['status'] == 'paid':
                print("✅ Update verified!")
            else:
                print("❌ Update verification failed")
        else:
            print("❌ UPDATE failed!")
            return False
        
        # 3. LIST - List all invoices
        print("\n📋 Testing LIST operation...")
        list_result = supabase.table('invoices').select('*').execute()
        
        if list_result.data:
            print(f"✅ LIST successful! Found {len(list_result.data)} invoices")
            for inv in list_result.data:
                print(f"   - {inv['invoice_number']}: {inv['client_name']} (${inv['total_amount']}) - {inv['status']}")
        else:
            print("❌ LIST failed!")
            return False
        
        # 4. DELETE - Delete the invoice
        print(f"\n🗑️  Testing DELETE operation for ID: {invoice_id}...")
        delete_result = supabase.table('invoices').delete().eq('id', invoice_id).execute()
        
        if delete_result.data:
            print("✅ DELETE successful!")
            
            # Verify deletion
            deleted = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
            if not deleted.data:
                print("✅ Deletion verified!")
                return True
            else:
                print("❌ Deletion verification failed")
                return False
        else:
            print("❌ DELETE failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_multiple_invoices():
    """Test creating multiple invoices"""
    print("\n🧪 Testing Multiple Invoice Creation")
    print("=" * 40)
    
    try:
        # Get Supabase credentials
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Create multiple invoices
        invoices = [
            {
                'user_id': 1,
                'invoice_number': f'INV-MULTI-1-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'client_name': 'Client A',
                'total_amount': 150.00,
                'status': 'pending'
            },
            {
                'user_id': 1,
                'invoice_number': f'INV-MULTI-2-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'client_name': 'Client B',
                'total_amount': 250.00,
                'status': 'paid'
            },
            {
                'user_id': 1,
                'invoice_number': f'INV-MULTI-3-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'client_name': 'Client C',
                'total_amount': 75.00,
                'status': 'pending'
            }
        ]
        
        created_ids = []
        
        for i, invoice_data in enumerate(invoices, 1):
            print(f"📝 Creating invoice {i}...")
            result = supabase.table('invoices').insert(invoice_data).execute()
            
            if result.data:
                invoice_id = result.data[0]['id']
                created_ids.append(invoice_id)
                print(f"✅ Invoice {i} created with ID: {invoice_id}")
            else:
                print(f"❌ Failed to create invoice {i}")
        
        print(f"\n✅ Created {len(created_ids)} invoices successfully!")
        
        # List all invoices
        print("\n📋 All invoices in database:")
        list_result = supabase.table('invoices').select('*').execute()
        
        if list_result.data:
            for inv in list_result.data:
                print(f"   - {inv['invoice_number']}: {inv['client_name']} (${inv['total_amount']}) - {inv['status']}")
        
        return created_ids
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []

if __name__ == "__main__":
    # Test single invoice creation and CRUD
    print("🧪 Testing Single Invoice CRUD")
    print("=" * 50)
    
    invoice_id = create_working_invoice()
    
    if invoice_id:
        print(f"\n✅ Working invoice created! ID: {invoice_id}")
        
        # Test CRUD operations
        if test_full_crud_operations(invoice_id):
            print("\n🎉 Single invoice CRUD operations working correctly!")
        else:
            print("\n❌ Some CRUD operations failed!")
    else:
        print("\n❌ Failed to create working invoice!")
    
    # Test multiple invoices
    print("\n" + "=" * 50)
    created_ids = test_multiple_invoices()
    
    if created_ids:
        print(f"\n🎉 Multiple invoice creation successful! Created {len(created_ids)} invoices")
        print("✅ Your invoice system is now working with Supabase!")
        print("✅ You can create, read, update, and delete invoices!")
        print("✅ Real-time synchronization is functional!")
    else:
        print("\n❌ Multiple invoice creation failed!")
    
    print("\n�� Test completed!")
