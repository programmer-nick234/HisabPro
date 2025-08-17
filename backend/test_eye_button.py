#!/usr/bin/env python
"""
Test Eye Button (Invoice Detail View) Functionality
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def test_eye_button_functionality():
    """Test the eye button functionality"""
    print("👁️ Testing Eye Button Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login/", json=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get('tokens', {}).get('access')
        
        if not access_token:
            print("❌ No access token received")
            return False
        
        print("✅ Login successful")
        
        # Step 2: Get list of invoices
        print("\n2. Getting invoices list...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        invoices_response = requests.get(f"{base_url}/mongodb/invoices/", headers=headers, timeout=10)
        if invoices_response.status_code != 200:
            print(f"❌ Failed to get invoices: {invoices_response.status_code}")
            return False
        
        invoices_data = invoices_response.json()
        invoices = invoices_data.get('results', []) if isinstance(invoices_data, dict) else invoices_data
        
        if not invoices:
            print("❌ No invoices found")
            return False
        
        print(f"✅ Found {len(invoices)} invoices")
        
        # Step 3: Test eye button for first invoice
        first_invoice = invoices[0]
        invoice_id = first_invoice.get('id')
        
        if not invoice_id:
            print("❌ No invoice ID found")
            return False
        
        print(f"\n3. Testing eye button for invoice: {first_invoice.get('invoice_number')}")
        
        # Test the detail endpoint (what the eye button calls)
        detail_response = requests.get(f"{base_url}/mongodb/invoices/{invoice_id}/", headers=headers, timeout=10)
        
        if detail_response.status_code == 200:
            detail_data = detail_response.json()
            print("✅ Eye button works! Invoice detail retrieved successfully")
            print(f"   Invoice Number: {detail_data.get('invoice_number')}")
            print(f"   Client: {detail_data.get('client_name')}")
            print(f"   Amount: ${detail_data.get('total_amount')}")
            print(f"   Status: {detail_data.get('status')}")
            
            # Check if items are included
            items = detail_data.get('items', [])
            print(f"   Items: {len(items)}")
            
            return True
            
        elif detail_response.status_code == 404:
            print("❌ Eye button failed: Invoice not found (404)")
            print(f"   Response: {detail_response.text}")
            return False
            
        else:
            print(f"❌ Eye button failed: Status {detail_response.status_code}")
            print(f"   Response: {detail_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_frontend_routes():
    """Test if frontend routes are accessible"""
    print("\n🌐 Testing Frontend Routes")
    print("=" * 50)
    
    frontend_urls = [
        "http://localhost:3000/invoices",
        "http://localhost:3000/invoices/create",
    ]
    
    for url in frontend_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - Accessible")
            else:
                print(f"⚠️ {url} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - Frontend not running")
        except Exception as e:
            print(f"❌ {url} - Error: {str(e)}")

def main():
    """Main test function"""
    print("🔍 Eye Button Functionality Test")
    print("=" * 60)
    
    # Test backend functionality
    backend_works = test_eye_button_functionality()
    
    # Test frontend routes
    test_frontend_routes()
    
    print("\n" + "=" * 60)
    if backend_works:
        print("🎉 Eye button functionality is working!")
        print("\n💡 To test the eye button:")
        print("1. Start the frontend: cd frontend && npm run dev")
        print("2. Go to http://localhost:3000/invoices")
        print("3. Click the eye icon next to any invoice")
        print("4. You should see the invoice detail page")
    else:
        print("❌ Eye button functionality has issues")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Django server is running")
        print("2. Check MongoDB connection")
        print("3. Verify authentication is working")

if __name__ == '__main__':
    main()
