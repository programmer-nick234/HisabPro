#!/usr/bin/env python3
"""
Test Simple Invoice Creation
This script tests creating an invoice with minimal required fields
"""

import os
import sys
from supabase import create_client, Client
from decouple import config
from datetime import datetime, date

def test_simple_invoice():
    """Test creating a simple invoice with minimal fields"""
    print("🧪 Testing Simple Invoice Creation")
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
        
        # Test with minimal required fields
        simple_invoice = {
            'user_id': 1,
            'invoice_number': f'INV-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'client_name': 'Test Client',
            'total_amount': 100.00
        }
        
        print(f"📝 Creating invoice with data: {simple_invoice}")
        
        # Try to create the invoice
        result = supabase.table('invoices').insert(simple_invoice).execute()
        
        if result.data:
            print("✅ Invoice created successfully!")
            print(f"   Invoice ID: {result.data[0]['id']}")
            print(f"   Invoice Number: {result.data[0]['invoice_number']}")
            print(f"   Client Name: {result.data[0]['client_name']}")
            print(f"   Total Amount: ${result.data[0]['total_amount']}")
            
            # Now try to retrieve it
            print("\n📋 Testing retrieval...")
            retrieved = supabase.table('invoices').select('*').eq('id', result.data[0]['id']).execute()
            
            if retrieved.data:
                print("✅ Invoice retrieved successfully!")
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

def test_with_additional_fields():
    """Test creating an invoice with more fields"""
    print("\n🧪 Testing Invoice with Additional Fields")
    print("=" * 40)
    
    try:
        # Get Supabase credentials
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test with more fields
        detailed_invoice = {
            'user_id': 1,
            'invoice_number': f'INV-DETAILED-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'client_name': 'Detailed Test Client',
            'client_email': 'test@example.com',
            'subtotal': 90.00,
            'tax_rate': 10.00,
            'tax_amount': 9.00,
            'total_amount': 99.00,
            'status': 'pending',
            'notes': 'Test invoice with detailed information'
        }
        
        print(f"📝 Creating detailed invoice with data: {detailed_invoice}")
        
        # Try to create the invoice
        result = supabase.table('invoices').insert(detailed_invoice).execute()
        
        if result.data:
            print("✅ Detailed invoice created successfully!")
            print(f"   Invoice ID: {result.data[0]['id']}")
            print(f"   Invoice Number: {result.data[0]['invoice_number']}")
            print(f"   Client Name: {result.data[0]['client_name']}")
            print(f"   Client Email: {result.data[0].get('client_email', 'N/A')}")
            print(f"   Subtotal: ${result.data[0].get('subtotal', 'N/A')}")
            print(f"   Tax Amount: ${result.data[0].get('tax_amount', 'N/A')}")
            print(f"   Total Amount: ${result.data[0]['total_amount']}")
            print(f"   Status: {result.data[0].get('status', 'N/A')}")
            
            return result.data[0]['id']
        else:
            print("❌ Failed to create detailed invoice")
            print(f"   Error: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Test simple invoice first
    simple_id = test_simple_invoice()
    
    if simple_id:
        print(f"\n✅ Simple invoice test passed! ID: {simple_id}")
    else:
        print("\n❌ Simple invoice test failed!")
    
    # Test detailed invoice
    detailed_id = test_with_additional_fields()
    
    if detailed_id:
        print(f"\n✅ Detailed invoice test passed! ID: {detailed_id}")
    else:
        print("\n❌ Detailed invoice test failed!")
    
    print("\n�� Test completed!")
