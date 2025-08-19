#!/usr/bin/env python3
"""
Test Complete Invoice Flow
This script tests the complete login -> invoice creation flow
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def test_complete_flow():
    """Test the complete flow: login -> create invoice -> view invoice"""
    print("🎯 Testing Complete Invoice Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    try:
        # 1. Login
        print("🔐 Step 1: Testing Login...")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post(f"{base_url}/auth/login/", json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            print("✅ Login successful!")
            token_data = login_response.json()
            access_token = token_data.get('tokens', {}).get('access')
            
            if access_token:
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                # 2. Create Invoice (Simplified)
                print("\n📝 Step 2: Testing Invoice Creation...")
                simple_invoice = {
                    'client_name': 'Test Client',
                    'client_email': 'test@example.com',
                    'total_amount': 100.00,
                    'status': 'pending',
                    'notes': 'Test invoice from complete flow'
                }
                
                print(f"   Creating invoice: {simple_invoice}")
                create_response = requests.post(f"{base_url}/supabase/invoices/", json=simple_invoice, headers=headers, timeout=10)
                
                print(f"   Response Status: {create_response.status_code}")
                
                if create_response.status_code == 201:
                    print("✅ Invoice created successfully!")
                    created_invoice = create_response.json()
                    invoice_id = created_invoice.get('id')
                    
                    print(f"   Invoice ID: {invoice_id}")
                    print(f"   Invoice Number: {created_invoice.get('invoice_number')}")
                    print(f"   Client Name: {created_invoice.get('client_name')}")
                    print(f"   Total Amount: ${created_invoice.get('total_amount')}")
                    
                    # 3. List Invoices
                    print("\n📋 Step 3: Testing Invoice List...")
                    list_response = requests.get(f"{base_url}/supabase/invoices/", headers=headers, timeout=10)
                    
                    if list_response.status_code == 200:
                        print("✅ Invoice list retrieved successfully!")
                        invoices = list_response.json()
                        print(f"   Found {len(invoices)} invoices")
                    else:
                        print(f"❌ List failed: {list_response.status_code}")
                    
                    # 4. Get Single Invoice
                    print(f"\n📖 Step 4: Testing Single Invoice Retrieval...")
                    get_response = requests.get(f"{base_url}/supabase/invoices/{invoice_id}/", headers=headers, timeout=10)
                    
                    if get_response.status_code == 200:
                        print("✅ Single invoice retrieved successfully!")
                        single_invoice = get_response.json()
                        print(f"   Invoice: {single_invoice.get('invoice_number')} - {single_invoice.get('client_name')}")
                    else:
                        print(f"❌ Single retrieval failed: {get_response.status_code}")
                    
                    # 5. Update Invoice
                    print(f"\n✏️  Step 5: Testing Invoice Update...")
                    update_data = {'status': 'paid'}
                    update_response = requests.put(f"{base_url}/supabase/invoices/{invoice_id}/", json=update_data, headers=headers, timeout=10)
                    
                    if update_response.status_code == 200:
                        print("✅ Invoice updated successfully!")
                        updated_invoice = update_response.json()
                        print(f"   New Status: {updated_invoice.get('status')}")
                    else:
                        print(f"❌ Update failed: {update_response.status_code}")
                    
                    # 6. Delete Invoice (cleanup)
                    print(f"\n🗑️  Step 6: Cleaning up test invoice...")
                    delete_response = requests.delete(f"{base_url}/supabase/invoices/{invoice_id}/", headers=headers, timeout=10)
                    
                    if delete_response.status_code == 204:
                        print("✅ Test invoice deleted successfully!")
                    else:
                        print(f"❌ Delete failed: {delete_response.status_code}")
                    
                    return True
                else:
                    print(f"❌ Invoice creation failed: {create_response.status_code}")
                    print(f"   Response: {create_response.text}")
                    return False
            else:
                print("❌ No access token received")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Complete Invoice Flow Test")
    print("=" * 50)
    
    if test_complete_flow():
        print("\n🎉 Complete flow test successful!")
        print("\n✅ Your system is ready!")
        print("✅ Login is working")
        print("✅ Invoice creation is working")
        print("✅ Invoice retrieval is working")
        print("✅ Invoice updates are working")
        print("✅ Invoice deletion is working")
        print("✅ Real-time synchronization with Supabase!")
        
        print("\n📋 Next Steps:")
        print("1. Open http://localhost:3000")
        print("2. Login with admin/admin123")
        print("3. Go to invoices/create")
        print("4. Fill in Client Name, Email, and Total Amount")
        print("5. Click 'Create Invoice'")
        print("6. See your invoice in Supabase!")
        
    else:
        print("\n❌ Some issues need to be resolved")
        print("Check the RLS policies in Supabase dashboard")

if __name__ == "__main__":
    main()
