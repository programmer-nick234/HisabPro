#!/usr/bin/env python3
"""
Check Invoice Table Structure
This script checks the actual structure of the invoices table in Supabase
"""

import os
import sys
from supabase import create_client, Client
from decouple import config

def check_invoice_table():
    """Check the structure of the invoices table"""
    print("🔍 Checking Invoice Table Structure")
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
        
        # Try to get table structure by attempting a simple query
        print("\n📋 Attempting to get table structure...")
        
        try:
            # Try to get one record to see the structure
            result = supabase.table('invoices').select('*').limit(1).execute()
            print("✅ Table exists and is accessible")
            
            if result.data:
                print("\n📊 Sample record structure:")
                for key, value in result.data[0].items():
                    print(f"   {key}: {type(value).__name__} = {value}")
            else:
                print("✅ Table exists but is empty")
                
        except Exception as e:
            print(f"❌ Error accessing table: {str(e)}")
        
        # Try to check user_profiles table
        print("\n👥 Checking user_profiles table...")
        try:
            profiles_result = supabase.table('user_profiles').select('id, user_id').limit(5).execute()
            if profiles_result.data:
                print(f"✅ Found {len(profiles_result.data)} user profiles:")
                for profile in profiles_result.data:
                    print(f"   ID: {profile.get('id')} - User ID: {profile.get('user_id')}")
            else:
                print("✅ user_profiles table exists but is empty")
        except Exception as e:
            print(f"❌ Error accessing user_profiles table: {str(e)}")
        
        # Try to create an invoice without user_id
        print("\n🧪 Testing invoice creation without user_id...")
        try:
            test_invoice = {
                'invoice_number': 'INV-TEST-001',
                'client_name': 'Test Client',
                'client_email': 'test@example.com',
                'total_amount': 100.00,
                'status': 'draft',
                'invoice_date': '2025-08-19',
                'due_date': '2025-09-18'
            }
            
            result = supabase.table('invoices').insert(test_invoice).execute()
            if result.data:
                print("✅ Invoice created successfully without user_id!")
                print(f"   Invoice ID: {result.data[0]['id']}")
                
                # Clean up - delete the test invoice
                supabase.table('invoices').delete().eq('id', result.data[0]['id']).execute()
                print("✅ Test invoice cleaned up")
            else:
                print("❌ Failed to create invoice without user_id")
                
        except Exception as e:
            print(f"❌ Error creating invoice without user_id: {str(e)}")
        
        print("\n✅ Structure check completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_invoice_table()
