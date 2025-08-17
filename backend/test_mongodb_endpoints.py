#!/usr/bin/env python
"""
Test MongoDB endpoints
"""

import os
import sys
import django
import requests

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def test_mongodb_endpoints():
    """Test MongoDB endpoints"""
    base_url = "http://localhost:8000/api"
    
    print("Testing MongoDB Endpoints...")
    print("=" * 40)
    
    # Test endpoints
    endpoints = [
        "/mongodb/invoices/summary/",
        "/mongodb/invoices/recent/",
        "/mongodb/invoices/",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 401:
                print(f"✅ {endpoint} - Authentication required (expected)")
            elif response.status_code == 200:
                print(f"✅ {endpoint} - Success")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Server not running")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")
    
    print("\n" + "=" * 40)
    print("MongoDB endpoints test completed!")

if __name__ == '__main__':
    test_mongodb_endpoints()
