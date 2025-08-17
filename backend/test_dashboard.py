#!/usr/bin/env python
"""
Test script to verify dashboard endpoints are working quickly
"""

import os
import sys
import django
import time
import requests

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def test_dashboard_endpoints():
    """Test dashboard API endpoints"""
    base_url = "http://localhost:8000/api"
    
    print("Testing Dashboard Endpoints...")
    print("=" * 40)
    
    # Test endpoints that should respond quickly
    endpoints = [
        "/invoices/summary/",
        "/invoices/recent/",
        "/invoices/",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTesting: {url}")
        
        start_time = time.time()
        try:
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            if response.status_code == 401:
                print(f"✅ Response time: {end_time - start_time:.2f}s (Authentication required - expected)")
            elif response.status_code == 200:
                print(f"✅ Response time: {end_time - start_time:.2f}s (Success)")
            else:
                print(f"⚠️  Response time: {end_time - start_time:.2f}s (Status: {response.status_code})")
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout after 10s - Endpoint is hanging!")
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error - Server not running")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    test_dashboard_endpoints()
