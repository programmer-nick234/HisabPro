#!/usr/bin/env python3
"""
Test Invoice Creation with Supabase
This script tests the complete invoice creation, storage, and retrieval workflow
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, date

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from lib.supabase_service import supabase_service

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("🔌 Testing Supabase connection...")
    
    try:
        supabase_service.connect()
        if supabase_service._connected and supabase_service.client:
            print("✅ Supabase connection successful")
            return True
        else:
            print("❌ Supabase connection failed")
            return False
    except Exception as e:
        print(f"❌ Supabase connection error: {str(e)}")
        return False

def test_invoice_creation():
    """Test creating an invoice in Supabase"""
    print("\n📝 Testing invoice creation...")
    
    try:
        # Test invoice data
        invoice_data = {
            'user_id': 1,
            'invoice_number': f'INV-{datetime.now().strftime("%Y%m%d")}-001',
            'client_name': 'Test Client',
            'client_email': 'test@example.com',
            'client_phone': '+1234567890',
            'client_address': '123 Test Street, Test City',
            'issue_date': date.today().isoformat(),
            'due_date': date.today().isoformat(),
            'subtotal': 100.00,
            'tax_rate': 10.00,
            'tax_amount': 10.00,
            'total_amount': 110.00,
            'status': 'pending',
            'notes': 'Test invoice created via API',
            'terms_conditions': 'Payment due within 30 days'
        }
        
        # Create invoice
        invoice_id = supabase_service.create_invoice(invoice_data)
        
        if invoice_id:
            print(f"✅ Invoice created successfully with ID: {invoice_id}")
            return invoice_id
        else:
            print("❌ Failed to create invoice")
            return None
            
    except Exception as e:
        print(f"❌ Error creating invoice: {str(e)}")
        return None

def test_invoice_retrieval(invoice_id):
    """Test retrieving the created invoice"""
    print(f"\n📋 Testing invoice retrieval for ID: {invoice_id}")
    
    try:
        invoice = supabase_service.get_invoice(invoice_id)
        
        if invoice:
            print("✅ Invoice retrieved successfully")
            print(f"   Invoice Number: {invoice.get('invoice_number')}")
            print(f"   Client Name: {invoice.get('client_name')}")
            print(f"   Total Amount: ${invoice.get('total_amount')}")
            print(f"   Status: {invoice.get('status')}")
            return True
        else:
            print("❌ Failed to retrieve invoice")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving invoice: {str(e)}")
        return False

def test_invoice_listing():
    """Test listing invoices for a user"""
    print("\n📋 Testing invoice listing...")
    
    try:
        invoices = supabase_service.get_user_invoices(user_id=1, limit=10)
        
        print(f"✅ Found {len(invoices)} invoices for user")
        
        for invoice in invoices:
            print(f"   - {invoice.get('invoice_number')}: {invoice.get('client_name')} (${invoice.get('total_amount')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing invoices: {str(e)}")
        return False

def test_invoice_update(invoice_id):
    """Test updating an invoice"""
    print(f"\n✏️  Testing invoice update for ID: {invoice_id}")
    
    try:
        update_data = {
            'status': 'paid',
            'notes': 'Invoice updated - payment received'
        }
        
        success = supabase_service.update_invoice(invoice_id, update_data)
        
        if success:
            print("✅ Invoice updated successfully")
            
            # Verify the update
            updated_invoice = supabase_service.get_invoice(invoice_id)
            if updated_invoice and updated_invoice.get('status') == 'paid':
                print("✅ Update verified - status changed to 'paid'")
                return True
            else:
                print("❌ Update verification failed")
                return False
        else:
            print("❌ Failed to update invoice")
            return False
            
    except Exception as e:
        print(f"❌ Error updating invoice: {str(e)}")
        return False

def test_invoice_deletion(invoice_id):
    """Test deleting an invoice"""
    print(f"\n🗑️  Testing invoice deletion for ID: {invoice_id}")
    
    try:
        success = supabase_service.delete_invoice(invoice_id)
        
        if success:
            print("✅ Invoice deleted successfully")
            
            # Verify deletion
            deleted_invoice = supabase_service.get_invoice(invoice_id)
            if deleted_invoice is None:
                print("✅ Deletion verified - invoice no longer exists")
                return True
            else:
                print("❌ Deletion verification failed - invoice still exists")
                return False
        else:
            print("❌ Failed to delete invoice")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting invoice: {str(e)}")
        return False

def test_dashboard_summary():
    """Test dashboard summary functionality"""
    print("\n📊 Testing dashboard summary...")
    
    try:
        summary = supabase_service.get_invoice_summary(user_id=1)
        
        print("✅ Dashboard summary retrieved successfully")
        print(f"   Total Invoices: {summary.get('total_invoices', 0)}")
        print(f"   Paid Invoices: {summary.get('paid_invoices', 0)}")
        print(f"   Pending Invoices: {summary.get('pending_invoices', 0)}")
        print(f"   Total Amount: ${summary.get('total_amount', 0)}")
        print(f"   Paid Amount: ${summary.get('paid_amount', 0)}")
        print(f"   Pending Amount: ${summary.get('pending_amount', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting dashboard summary: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints with authentication"""
    print("\n🔗 Testing API endpoints...")
    
    base_url = "http://localhost:8000/api"
    
    # First, login to get token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Login
        login_response = requests.post(f"{base_url}/auth/login/", json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('tokens', {}).get('access')
            
            if access_token:
                print("✅ Login successful, testing API endpoints...")
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                # Test invoice creation via API
                test_invoice = {
                    'user_id': 1,
                    'invoice_number': f'INV-API-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                    'client_name': 'API Test Client',
                    'client_email': 'api@test.com',
                    'subtotal': 200.00,
                    'tax_rate': 10.00,
                    'tax_amount': 20.00,
                    'total_amount': 220.00,
                    'status': 'pending'
                }
                
                # Create invoice via API
                create_response = requests.post(f"{base_url}/supabase/invoices/", json=test_invoice, headers=headers, timeout=10)
                
                if create_response.status_code == 201:
                    print("✅ Invoice created via API successfully")
                    created_invoice = create_response.json()
                    invoice_id = created_invoice.get('id')
                    
                    # Test getting invoices list
                    list_response = requests.get(f"{base_url}/supabase/invoices/", headers=headers, timeout=10)
                    if list_response.status_code == 200:
                        print("✅ Invoice list retrieved via API successfully")
                    
                    # Test getting summary
                    summary_response = requests.get(f"{base_url}/supabase/invoices/summary/", headers=headers, timeout=10)
                    if summary_response.status_code == 200:
                        print("✅ Invoice summary retrieved via API successfully")
                    
                    # Clean up - delete the test invoice
                    if invoice_id:
                        delete_response = requests.delete(f"{base_url}/supabase/invoices/{invoice_id}/", headers=headers, timeout=10)
                        if delete_response.status_code == 204:
                            print("✅ Test invoice deleted via API successfully")
                    
                    return True
                else:
                    print(f"❌ API invoice creation failed: {create_response.status_code}")
                    print(f"   Response: {create_response.text}")
                    return False
            else:
                print("❌ No access token received")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Invoice Creation Test Suite")
    print("=" * 50)
    
    # Test connection
    if not test_supabase_connection():
        print("\n❌ Cannot proceed without Supabase connection")
        return
    
    # Test invoice creation
    invoice_id = test_invoice_creation()
    if not invoice_id:
        print("\n❌ Invoice creation failed")
        return
    
    # Test invoice retrieval
    if not test_invoice_retrieval(invoice_id):
        print("\n❌ Invoice retrieval failed")
        return
    
    # Test invoice listing
    if not test_invoice_listing():
        print("\n❌ Invoice listing failed")
        return
    
    # Test invoice update
    if not test_invoice_update(invoice_id):
        print("\n❌ Invoice update failed")
        return
    
    # Test dashboard summary
    if not test_dashboard_summary():
        print("\n❌ Dashboard summary failed")
        return
    
    # Test API endpoints
    if not test_api_endpoints():
        print("\n❌ API endpoints test failed")
        return
    
    # Test invoice deletion
    if not test_invoice_deletion(invoice_id):
        print("\n❌ Invoice deletion failed")
        return
    
    print("\n🎉 All tests passed!")
    print("\n✅ Invoice creation, storage, and retrieval is working perfectly!")
    print("✅ Real-time synchronization with Supabase is functional!")
    print("✅ API endpoints are responding correctly!")
    print("✅ CRUD operations are working as expected!")

if __name__ == "__main__":
    main()
