#!/usr/bin/env python
"""
Test Dashboard API Endpoints
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

def test_dashboard_api():
    """Test dashboard API endpoints"""
    print("📊 Testing Dashboard API Endpoints")
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
        
        # Step 2: Test Summary Endpoint
        print("\n2. Testing Summary Endpoint...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        summary_response = requests.get(f"{base_url}/mongodb/invoices/summary/", headers=headers, timeout=10)
        print(f"Summary Status: {summary_response.status_code}")
        
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            print("✅ Summary endpoint working!")
            print(f"   Total Invoices: {summary_data.get('total_invoices', 0)}")
            print(f"   Pending Amount: {summary_data.get('total_pending_amount', 0)}")
            print(f"   Paid Amount: {summary_data.get('total_paid_amount', 0)}")
            print(f"   Overdue Amount: {summary_data.get('total_overdue_amount', 0)}")
            print(f"   Summary Data Type: {type(summary_data)}")
            print(f"   Summary Data: {json.dumps(summary_data, indent=2)}")
        else:
            print(f"❌ Summary endpoint failed: {summary_response.text}")
            return False
        
        # Step 3: Test Recent Invoices Endpoint
        print("\n3. Testing Recent Invoices Endpoint...")
        recent_response = requests.get(f"{base_url}/mongodb/invoices/recent/", headers=headers, timeout=10)
        print(f"Recent Status: {recent_response.status_code}")
        
        if recent_response.status_code == 200:
            recent_data = recent_response.json()
            print("✅ Recent invoices endpoint working!")
            print(f"   Recent Data Type: {type(recent_data)}")
            print(f"   Recent Data Length: {len(recent_data) if isinstance(recent_data, list) else 'Not a list'}")
            print(f"   Recent Data: {json.dumps(recent_data[:2] if isinstance(recent_data, list) else recent_data, indent=2)}")
            
            if isinstance(recent_data, list):
                print(f"   Recent Invoices: {len(recent_data)}")
                for i, invoice in enumerate(recent_data[:3]):
                    print(f"   - {invoice.get('invoice_number')}: {invoice.get('client_name')} - {invoice.get('total_amount')}")
            else:
                print(f"   Recent Data Structure: {type(recent_data)}")
        else:
            print(f"❌ Recent invoices endpoint failed: {recent_response.text}")
            return False
        
        # Step 4: Test Main Invoices Endpoint
        print("\n4. Testing Main Invoices Endpoint...")
        invoices_response = requests.get(f"{base_url}/mongodb/invoices/", headers=headers, timeout=10)
        print(f"Invoices Status: {invoices_response.status_code}")
        
        if invoices_response.status_code == 200:
            invoices_data = invoices_response.json()
            print("✅ Main invoices endpoint working!")
            print(f"   Invoices Data Type: {type(invoices_data)}")
            if isinstance(invoices_data, list):
                print(f"   Total Invoices: {len(invoices_data)}")
            elif isinstance(invoices_data, dict):
                print(f"   Invoices Data Keys: {list(invoices_data.keys())}")
                if 'results' in invoices_data:
                    print(f"   Results Length: {len(invoices_data['results'])}")
        else:
            print(f"❌ Main invoices endpoint failed: {invoices_response.text}")
            return False
        
        print("\n🎉 All dashboard API endpoints are working!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_frontend_dashboard():
    """Test if frontend dashboard is accessible"""
    print("\n🌐 Testing Frontend Dashboard")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000/dashboard", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend dashboard is accessible")
        else:
            print(f"⚠️ Frontend dashboard status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main test function"""
    print("🔍 Dashboard API Test")
    print("=" * 60)
    
    # Test backend API
    api_works = test_dashboard_api()
    
    # Test frontend
    test_frontend_dashboard()
    
    print("\n" + "=" * 60)
    if api_works:
        print("🎉 Dashboard API is working perfectly!")
        print("\n💡 If dashboard still doesn't work:")
        print("1. Check browser console for errors")
        print("2. Make sure frontend is running: cd frontend && npm run dev")
        print("3. Clear browser cache and reload")
    else:
        print("❌ Dashboard API has issues")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Django server is running")
        print("2. Check MongoDB connection")
        print("3. Verify authentication is working")

if __name__ == '__main__':
    main()
