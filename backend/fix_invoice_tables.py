#!/usr/bin/env python3
"""
Fix Invoice Tables in Supabase
This script creates the correct table structure for invoices
"""

import os
import sys
from supabase import create_client, Client
from decouple import config
import uuid

def create_proper_invoice():
    """Create an invoice with the correct structure"""
    print("🔧 Creating Proper Invoice Structure")
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
        
        # Create invoice with correct structure
        proper_invoice = {
            'id': str(uuid.uuid4()),  # Generate UUID
            'user_id': 1,  # Keep as integer for now
            'invoice_number': f'INV-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'client_name': 'Proper Test Client',
            'total_amount': 100.00,
            'status': 'pending'
        }
        
        print(f"📝 Creating invoice with data: {proper_invoice}")
        
        # Try to create the invoice
        result = supabase.table('invoices').insert(proper_invoice).execute()
        
        if result.data:
            print("✅ Invoice created successfully!")
            print(f"   Invoice ID: {result.data[0]['id']}")
            print(f"   Invoice Number: {result.data[0]['invoice_number']}")
            print(f"   Client Name: {result.data[0]['client_name']}")
            print(f"   Total Amount: ${result.data[0]['total_amount']}")
            print(f"   Status: {result.data[0]['status']}")
            
            # Test retrieval
            print("\n📋 Testing retrieval...")
            retrieved = supabase.table('invoices').select('*').eq('id', result.data[0]['id']).execute()
            
            if retrieved.data:
                print("✅ Invoice retrieved successfully!")
                print("   All fields present:")
                for key, value in retrieved.data[0].items():
                    print(f"     {key}: {value}")
                
                return result.data[0]['id']
            else:
                print("❌ Failed to retrieve invoice")
                return None
        else:
            print("❌ Failed to create invoice")
            print(f"   Error: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_invoice_operations(invoice_id):
    """Test various invoice operations"""
    print(f"\n🧪 Testing Invoice Operations for ID: {invoice_id}")
    print("=" * 40)
    
    try:
        # Get Supabase credentials
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test update
        print("📝 Testing invoice update...")
        update_result = supabase.table('invoices').update({'status': 'paid'}).eq('id', invoice_id).execute()
        
        if update_result.data:
            print("✅ Invoice updated successfully!")
            
            # Verify update
            updated = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
            if updated.data and updated.data[0]['status'] == 'paid':
                print("✅ Update verified!")
            else:
                print("❌ Update verification failed")
        else:
            print("❌ Failed to update invoice")
        
        # Test listing
        print("\n📋 Testing invoice listing...")
        list_result = supabase.table('invoices').select('*').execute()
        
        if list_result.data:
            print(f"✅ Found {len(list_result.data)} invoices")
            for inv in list_result.data:
                print(f"   - {inv['invoice_number']}: {inv['client_name']} (${inv['total_amount']}) - {inv['status']}")
        else:
            print("❌ Failed to list invoices")
        
        # Test deletion
        print(f"\n🗑️  Testing invoice deletion for ID: {invoice_id}...")
        delete_result = supabase.table('invoices').delete().eq('id', invoice_id).execute()
        
        if delete_result.data:
            print("✅ Invoice deleted successfully!")
            
            # Verify deletion
            deleted = supabase.table('invoices').select('*').eq('id', invoice_id).execute()
            if not deleted.data:
                print("✅ Deletion verified!")
                return True
            else:
                print("❌ Deletion verification failed")
                return False
        else:
            print("❌ Failed to delete invoice")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    
    # Create proper invoice
    invoice_id = create_proper_invoice()
    
    if invoice_id:
        print(f"\n✅ Proper invoice created! ID: {invoice_id}")
        
        # Test operations
        if test_invoice_operations(invoice_id):
            print("\n🎉 All invoice operations working correctly!")
        else:
            print("\n❌ Some operations failed!")
    else:
        print("\n❌ Failed to create proper invoice!")
    
    print("\n�� Test completed!")
