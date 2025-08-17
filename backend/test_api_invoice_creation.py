#!/usr/bin/env python
"""
Test API Invoice Creation
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def test_api_invoice_creation():
    """Test invoice creation through API"""
    base_url = "http://localhost:8000/api"
    
    print("Testing API Invoice Creation...")
    print("=" * 50)
    
    # Login to get token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Login
        login_response = requests.post(f"{base_url}/auth/login/", json=login_data)
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get('tokens', {}).get('access')
        
        if not access_token:
            print("❌ No access token received")
            print(f"Token data: {token_data}")
            return False
        
        print("✅ Login successful")
        
        # Headers with token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test invoice data
        invoice_data = {
            "client_name": "API Test Client",
            "client_email": "test@api.com",
            "client_phone": "1234567890",
            "client_address": "Test Address",
            "issue_date": "2025-08-17",
            "due_date": "2025-09-17",
            "tax_rate": 18.0,
            "notes": "Test invoice from API",
            "terms_conditions": "Test terms",
            "items": [
                {
                    "description": "API Service 1",
                    "quantity": 1,
                    "unit_price": 100.0
                },
                {
                    "description": "API Service 2",
                    "quantity": 2,
                    "unit_price": 50.0
                }
            ]
        }
        
        # Create invoice
        print("📝 Creating invoice...")
        create_response = requests.post(
            f"{base_url}/mongodb/invoices/", 
            json=invoice_data,
            headers=headers
        )
        
        if create_response.status_code == 201:
            invoice = create_response.json()
            print(f"✅ Invoice created successfully!")
            print(f"   Invoice Number: {invoice.get('invoice_number')}")
            print(f"   Client: {invoice.get('client_name')}")
            print(f"   Total Amount: ${invoice.get('total_amount')}")
            
            # Test getting the invoice
            invoice_id = invoice.get('id')
            if invoice_id:
                get_response = requests.get(
                    f"{base_url}/mongodb/invoices/{invoice_id}/",
                    headers=headers
                )
                
                if get_response.status_code == 200:
                    print("✅ Invoice retrieved successfully")
                else:
                    print(f"⚠️ Failed to retrieve invoice: {get_response.status_code}")
                
                # Clean up - delete the test invoice
                delete_response = requests.delete(
                    f"{base_url}/mongodb/invoices/{invoice_id}/",
                    headers=headers
                )
                
                if delete_response.status_code == 204:
                    print("🧹 Test invoice cleaned up")
                else:
                    print(f"⚠️ Failed to delete test invoice: {delete_response.status_code}")
            
            return True
        else:
            print(f"❌ Invoice creation failed: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_api_invoice_creation()
